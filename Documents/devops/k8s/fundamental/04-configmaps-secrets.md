<!-- tags: kubernetes, k8s, configuration, secrets -->
# 🔐 ConfigMaps & Secrets

> Separate configuration from code — 12-Factor App principle, manage secrets safely in K8s

| Aspect           | Detail                                              |
| ---------------- | --------------------------------------------------- |
| **K8s Object**   | `v1/ConfigMap`, `v1/Secret`                         |
| **Use case**     | Environment config, DB credentials, TLS certs       |
| **Go relevance** | `os.Getenv()`, config files, cert loading           |
| **Kubectl**      | `kubectl create configmap`, `kubectl create secret` |

---

## 1. DEFINE

Picture the moment config and secrets start changing per environment — the question is no longer "where to put env vars" but keeping the boundary between config, secret, and image clean enough to deploy safely.

### ConfigMap vs Secret

| Attribute           | ConfigMap                           | Secret                              |
| ------------------- | ----------------------------------- | ----------------------------------- |
| **Data**            | Non-sensitive (port, feature flags) | Sensitive (passwords, API keys)     |
| **Encoding**        | Plain text                          | Base64 encoded                      |
| **Encryption at rest** | ❌ No                            | ✅ Yes (when EncryptionConfig enabled) |
| **Size limit**      | 1MB                                 | 1MB                                 |
| **Mount**           | Env vars, Volume files              | Env vars, Volume files              |
| **RBAC**            | Usually less restricted             | Should restrict access              |

### How to inject into a Pod

| Method                   | Use case                       | Auto-update?            |
| ------------------------ | ------------------------------ | ----------------------- |
| **Environment Variable** | Single values (port, URL)      | ❌ Requires Pod restart |
| **Volume Mount**         | Config files (JSON, YAML, .env)| ✅ Auto-update (~60s)   |
| **envFrom**              | Load all keys as env vars      | ❌ Requires Pod restart |

### Failure Modes

| Error                                 | Cause                            | Consequence                      |
| ------------------------------------- | -------------------------------- | -------------------------------- |
| Secret not found                      | Typo in name or not yet created  | Pod `CreateContainerConfigError` |
| ConfigMap updated but Pod unaware     | Using env var (no auto-reload)   | Requires Pod restart             |
| Secret committed to Git               | Base64 ≠ encryption              | Credentials leaked               |
| Optional key missing                  | `optional: false` by default     | Pod fails to start               |

---

Those failure modes sound basic. But there is a trap: Secret base64 is not encryption = data exposed, and ConfigMap change does not trigger pod restart = config stale. That trap appears in PITFALLS.

## 2. VISUAL

The concepts have names. Moving to diagrams, the more important part reveals itself: how requests, workloads, or signals flow through these layers.

![ConfigMap & Secret Injection](./images/k8s-configmaps-secrets.png)

*Figure: ConfigMaps hold non-sensitive data, Secrets hold credentials — both inject into Pods via environment variables or volume mounts. Base64 encoding is NOT encryption; enable EncryptionConfiguration for at-rest protection.*

### ConfigMap/Secret → Pod Flow

```
┌─────────────────┐     ┌─────────────────┐
│   ConfigMap      │     │     Secret       │
│ "app-config"     │     │ "db-credentials" │
│                  │     │                  │
│ PORT=8080        │     │ DB_PASS=***      │
│ LOG_LEVEL=info   │     │ API_KEY=***      │
│ config.yaml=...  │     │ tls.crt=...      │
└────────┬─────────┘     └────────┬─────────┘
         │                        │
         ├── env var ─────────────┤
         ├── volume mount ────────┤
         │                        │
    ┌────▼────────────────────────▼────────┐
    │              POD                      │
    │  env:                                 │
    │    PORT=8080          (from ConfigMap) │
    │    DB_PASS=s3cret     (from Secret)   │
    │  volumes:                             │
    │    /etc/config/config.yaml            │
    │    /etc/secrets/tls.crt               │
    └───────────────────────────────────────┘
```

---

## 3. CODE

The diagrams have shown the main path. The code/manifests/commands below pull it down to the artifact level that on-call or reviewers actually use.

### Example 1: Basic — ConfigMap + Secret for a Go app

> **Goal**: Create ConfigMap/Secret, inject into Go app via env vars and volume.
> **Requires**: Go app reading config from environment.
> **Result**: Externalized configuration, config separated from image.

```go
// config/config.go — Go config loader
package config

import (
	"encoding/json"
	"fmt"
	"os"
	"strconv"
)

// ✅ Config struct — reads from env vars (injected by K8s)
type Config struct {
	Port        int    `json:"port"`
	LogLevel    string `json:"log_level"`
	DatabaseURL string `json:"database_url"` // ⚠️ From Secret
	APIKey      string `json:"api_key"`      // ⚠️ From Secret
	Debug       bool   `json:"debug"`
}

// ✅ Load config from environment variables
func Load() (*Config, error) {
	port, _ := strconv.Atoi(getEnv("PORT", "8080"))

	cfg := &Config{
		Port:        port,
		LogLevel:    getEnv("LOG_LEVEL", "info"),
		DatabaseURL: os.Getenv("DATABASE_URL"), // ⚠️ Required — from Secret
		APIKey:      os.Getenv("API_KEY"),       // ⚠️ Required — from Secret
		Debug:       getEnv("DEBUG", "false") == "true",
	}

	// ✅ Validate required fields
	if cfg.DatabaseURL == "" {
		return nil, fmt.Errorf("DATABASE_URL is required (set via K8s Secret)")
	}

	return cfg, nil
}

func getEnv(key, defaultVal string) string {
	if val := os.Getenv(key); val != "" {
		return val
	}
	return defaultVal
}

// ✅ Load config from file (volume mount)
func LoadFromFile(path string) (*Config, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read config file: %w", err)
	}
	var cfg Config
	if err := json.Unmarshal(data, &cfg); err != nil {
		return nil, fmt.Errorf("parse config: %w", err)
	}
	return &cfg, nil
}
```

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
    name: app-config
data:
    PORT: '8080'
    LOG_LEVEL: 'info'
    DEBUG: 'false'
    # ✅ File-based config
    config.json: |
        {
          "port": 8080,
          "log_level": "info",
          "features": {
            "new_dashboard": true,
            "beta_api": false
          }
        }
---
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
    name: db-credentials
type: Opaque
stringData: # ✅ stringData — K8s auto-encodes to base64
    DATABASE_URL: 'postgres://user:p@ssw0rd@postgres:5432/mydb?sslmode=disable'
    API_KEY: 'sk-live-abc123def456'
```

```yaml
# k8s/deployment-with-config.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
    name: go-api
spec:
    replicas: 3
    selector:
        matchLabels:
            app: go-api
    template:
        metadata:
            labels:
                app: go-api
        spec:
            containers:
                - name: api
                  image: go-api:v1
                  ports:
                      - containerPort: 8080
                  # ✅ Env vars from ConfigMap
                  envFrom:
                      - configMapRef:
                            name: app-config
                  # ✅ Env vars from Secret (select individual keys)
                  env:
                      - name: DATABASE_URL
                        valueFrom:
                            secretKeyRef:
                                name: db-credentials
                                key: DATABASE_URL
                      - name: API_KEY
                        valueFrom:
                            secretKeyRef:
                                name: db-credentials
                                key: API_KEY
                  # ✅ Volume mount for config files
                  volumeMounts:
                      - name: config-volume
                        mountPath: /etc/config
                        readOnly: true
                      - name: secret-volume
                        mountPath: /etc/secrets
                        readOnly: true
                  resources:
                      requests: { memory: '64Mi', cpu: '100m' }
                      limits: { memory: '256Mi', cpu: '500m' }
            volumes:
                - name: config-volume
                  configMap:
                      name: app-config
                - name: secret-volume
                  secret:
                      secretName: db-credentials
                      defaultMode: 0400 # ✅ Read-only for owner
```

```bash
# ✅ Create secret from command line (safer than YAML file)
kubectl create secret generic db-credentials \
  --from-literal=DATABASE_URL="postgres://user:pass@host:5432/db" \
  --from-literal=API_KEY="sk-live-xxx"

# Deploy
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment-with-config.yaml

# Verify env vars in pod
kubectl exec -it deploy/go-api -- env | grep -E "PORT|LOG|DATABASE|API_KEY"

# Verify mounted files
kubectl exec -it deploy/go-api -- cat /etc/config/config.json
kubectl exec -it deploy/go-api -- ls -la /etc/secrets/
```

> **Result**: Config externalized, secrets separated, same image runs every environment.
> **Note**: `stringData` in Secret is only a convenience — K8s still stores base64. NEVER commit Secret YAML to Git.

📅 Created: 2026-03-20 · 🔄 Updated: 2026-04-20 · ⏱️ 15 min read

---

ConfigMap is covered. But Secrets need encryption — time to protect.

### Example 2: Intermediate — Hot-reload config with file watcher

> **Goal**: Go app auto-reloads config when ConfigMap changes, no Pod restart needed.
> **Requires**: Volume mount ConfigMap + fsnotify.
> **Result**: Zero-downtime config update.

```go
// configwatcher/watcher.go — Watch config file changes
package configwatcher

import (
	"encoding/json"
	"log"
	"os"
	"sync"
	"time"

	"github.com/fsnotify/fsnotify"
)

// ✅ Thread-safe config holder
type ConfigHolder struct {
	mu     sync.RWMutex
	config AppConfig
	path   string
}

type AppConfig struct {
	LogLevel  string          `json:"log_level"`
	Features  map[string]bool `json:"features"`
	RateLimit int             `json:"rate_limit"`
}

func NewConfigHolder(configPath string) (*ConfigHolder, error) {
	h := &ConfigHolder{path: configPath}
	if err := h.reload(); err != nil {
		return nil, err
	}
	go h.watch()
	return h, nil
}

func (h *ConfigHolder) Get() AppConfig {
	h.mu.RLock()
	defer h.mu.RUnlock()
	return h.config
}

func (h *ConfigHolder) reload() error {
	data, err := os.ReadFile(h.path)
	if err != nil {
		return err
	}
	var cfg AppConfig
	if err := json.Unmarshal(data, &cfg); err != nil {
		return err
	}
	h.mu.Lock()
	h.config = cfg
	h.mu.Unlock()
	log.Printf("✅ Config reloaded: log_level=%s, features=%v", cfg.LogLevel, cfg.Features)
	return nil
}

func (h *ConfigHolder) watch() {
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		log.Printf("⚠️ Failed to create watcher: %v", err)
		return
	}
	defer watcher.Close()

	// ⚠️ K8s ConfigMap mount uses symlinks
	// Watch parent directory instead of file directly
	configDir := "/etc/config"
	if err := watcher.Add(configDir); err != nil {
		log.Printf("⚠️ Failed to watch %s: %v", configDir, err)
		return
	}
	log.Printf("👀 Watching config changes at %s", configDir)

	// ✅ Debounce — K8s may trigger multiple events
	var debounceTimer *time.Timer
	for {
		select {
		case event, ok := <-watcher.Events:
			if !ok {
				return
			}
			if event.Op&(fsnotify.Create|fsnotify.Write|fsnotify.Remove) != 0 {
				if debounceTimer != nil {
					debounceTimer.Stop()
				}
				debounceTimer = time.AfterFunc(500*time.Millisecond, func() {
					if err := h.reload(); err != nil {
						log.Printf("⚠️ Config reload error: %v", err)
					}
				})
			}
		case err, ok := <-watcher.Errors:
			if !ok {
				return
			}
			log.Printf("⚠️ Watcher error: %v", err)
		}
	}
}
```

```go
// main.go — Using the config watcher
package main

import (
	"encoding/json"
	"log"
	"net/http"
	"myapp/configwatcher"
)

func main() {
	cfgHolder, err := configwatcher.NewConfigHolder("/etc/config/config.json")
	if err != nil {
		log.Fatalf("❌ Config load error: %v", err)
	}

	http.HandleFunc("/config", func(w http.ResponseWriter, r *http.Request) {
		// ✅ Always returns latest config — no restart needed
		cfg := cfgHolder.Get()
		json.NewEncoder(w).Encode(cfg)
	})

	log.Fatal(http.ListenAndServe(":8080", nil))
}
```

```bash
# ✅ Update ConfigMap → Pod auto-reloads (no restart needed)
kubectl edit configmap app-config
# Change log_level: "debug"
# Wait ~60s → kubelet sync → fsnotify trigger → reload
```

> **Result**: Config hot-reload, feature flags toggling with no downtime.
> **Note**: K8s syncs ConfigMap volume every ~60s (configurable). Env vars do NOT auto-update.

---

Secrets are covered. But rotation needs a strategy — time to manage.

### Example 3: Advanced — Sealed Secrets + External Secrets Operator

> **Goal**: Manage secrets safely in Git (GitOps), sync from AWS/GCP/Vault.
> **Requires**: Sealed Secrets controller or External Secrets Operator.
> **Result**: Production-grade secret management.

```yaml
# ✅ Sealed Secret — encrypt secret, safe to commit to Git
# Install: helm install sealed-secrets sealed-secrets/sealed-secrets -n kube-system
# Encrypt: kubeseal < secret.yaml > sealed-secret.yaml

apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
    name: db-credentials
    namespace: default
spec:
    encryptedData:
        # ✅ Encrypted with cluster's public key → only the cluster can decrypt
        DATABASE_URL: AgBy3i4OJSWK+PiTySYZZA9rO43cGD...
        API_KEY: AgCtr8BSDI2+PtZwFR9wSQw3r3VaP0...
    template:
        metadata:
            name: db-credentials
        type: Opaque
---
# ✅ External Secret — sync from AWS Secrets Manager / HashiCorp Vault
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
    name: db-credentials
spec:
    refreshInterval: 1h # ✅ Auto-sync every hour
    secretStoreRef:
        name: aws-secret-store
        kind: ClusterSecretStore
    target:
        name: db-credentials
        creationPolicy: Owner
    data:
        - secretKey: DATABASE_URL
          remoteRef:
              key: production/database
              property: url
        - secretKey: API_KEY
          remoteRef:
              key: production/api
              property: key
```

> **Result**: Secrets encrypted in Git (SealedSecrets) or synced from cloud vault.
> **Note**: Always rotate secrets periodically. Use RBAC to restrict who can read secrets.

---

You have covered ConfigMap, Secrets, and rotation. Now comes the dangerous part: base64 illusion and stale config — the trap set up from the beginning.

## 4. PITFALLS

| #   | Mistake                                       | Consequence | Fix                                               |
| --- | --------------------------------------------- | ----------- | ------------------------------------------------- |
| 1   | Commit Secret YAML (base64) to Git → leaked  | —           | Use SealedSecrets or External Secrets             |
| 2   | ConfigMap updated but env var unchanged       | —           | Use volume mount instead of env, or restart pods  |
| 3   | Secret too large (>1MB) → error              | —           | Split or use external secret store                |
| 4   | Immutable ConfigMap/Secret but need update    | —           | Create new with different name, update Deployment |
| 5   | `base64` decode error (line breaks)           | —           | `echo -n "value" | base64` (flag `-n` strips newline) |

---

## 5. REF

| Resource         | Link                                                                                                                |
| ---------------- | ------------------------------------------------------------------------------------------------------------------- |
| ConfigMaps       | [kubernetes.io/docs/concepts/configuration/configmap](https://kubernetes.io/docs/concepts/configuration/configmap/) |
| Secrets          | [kubernetes.io/docs/concepts/configuration/secret](https://kubernetes.io/docs/concepts/configuration/secret/)       |
| Sealed Secrets   | [github.com/bitnami-labs/sealed-secrets](https://github.com/bitnami-labs/sealed-secrets)                            |
| External Secrets | [external-secrets.io](https://external-secrets.io/)                                                                 |
| fsnotify         | [github.com/fsnotify/fsnotify](https://github.com/fsnotify/fsnotify)                                                |

---

## 6. RECOMMEND

| Extension                      | When                           | Reason                                         |
| ------------------------------ | ------------------------------ | ---------------------------------------------- |
| **HashiCorp Vault**            | Enterprise secret management   | Dynamic secrets, rotation, audit logging       |
| **SOPS**                       | Encrypt files in Git           | Mozilla SOPS — encrypt YAML/JSON fields        |
| **Reloader**                   | Auto restart on ConfigMap change | `stakater/Reloader` — watch + rolling restart |
| **Kustomize secretGenerator**  | Multi-env configs              | Generate unique ConfigMap/Secret names per env |
| **Viper** (Go library)         | Complex config loading         | Watch files, env vars, remote config           |

---

## 🔍 Debug Checklist

| # | Symptom | Root cause | Diagnostic command |
|---|---------|------------|-------------------|
| 1 | Pod in `CreateContainerConfigError` | ConfigMap or Secret does not exist | `kubectl describe pod <pod>` → check Events |
| 2 | Env var not injected | Key name wrong in `secretKeyRef`/`configMapKeyRef` | `kubectl exec <pod> -- env \| grep <KEY>` |
| 3 | ConfigMap updated but Pod unaware | Using env var (no auto-reload); only volume mount auto-updates | Check env vs volume in pod spec |
| 4 | Secret value wrong after decode | Base64 decode has trailing newline | `kubectl get secret <name> -o jsonpath='{.data.<key>}' \| base64 -d` |
| 5 | Config hot-reload not working | App watches file directly instead of directory; K8s uses symlink | Watch parent directory (see fsnotify pattern) |

---

## 🃏 Quick Reference

| # | Pattern | Command / Rule |
|---|---------|----------------|
| 1 | Create ConfigMap from literal | `kubectl create configmap <name> --from-literal=KEY=value` |
| 2 | Create ConfigMap from file | `kubectl create configmap <name> --from-file=config.yaml` |
| 3 | Create Secret from literal | `kubectl create secret generic <name> --from-literal=KEY=value` |
| 4 | View Secret value (decoded) | `kubectl get secret <name> -o jsonpath='{.data.KEY}' \| base64 -d` |
| 5 | Load all ConfigMap keys as env | `envFrom: [{configMapRef: {name: <name>}}]` |
| 6 | Volume mount for auto-update | `volumes: [{configMap: {name: <name>}}]` + `volumeMounts` |
| 7 | Base64 encode without newline | `echo -n "myvalue" \| base64` |

---

## 🎯 Interview Angle

**Related system design / technical questions:**
- *"How do ConfigMap and Secret differ? When to use which?"*
- *"Why not commit Secret YAML to Git? What are the alternatives?"*
- *"Can config update without Pod restart? What are the limitations?"*

**Key talking points interviewers expect:**

| Topic | Talking point |
|-------|---------------|
| ConfigMap vs Secret | ConfigMap: non-sensitive; Secret: sensitive, base64-encoded, can encrypt at rest with EncryptionConfig |
| Secret is not encryption | Base64 is just encoding; need EncryptionConfig or Vault/SealedSecrets |
| Env var vs Volume mount | Env: no auto-update (needs restart); Volume: auto-updates after ~60s |
| Secret rotation | External Secrets with `refreshInterval`; volume mount auto-updates, env needs rolling restart |
| Immutable ConfigMap | `immutable: true` → cannot update but improves performance (kubelet stops watching) |
| 12-Factor App | Separate config from code; same image deploys everywhere with different ConfigMap/Secret |

**Common follow-up questions:**
- *"How to rotate secrets with no downtime?"* → External Secrets auto-syncs; Volume mount auto-updates; app reloads from file
- *"What is `stringData`?"* → Convenience field, K8s auto-encodes base64; only used when writing, not reading
- *"How does Sealed Secrets work?"* → Encrypts with cluster public key → only controller can decrypt; safe to commit to Git

---

**Links**: [← Services & Networking](./03-services-networking.md) · [→ Volumes & Storage](./05-volumes-storage.md)
