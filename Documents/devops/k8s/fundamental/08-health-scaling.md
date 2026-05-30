<!-- tags: kubernetes, k8s, scaling, health-check -->
# 🏥 Health Checks & Auto-scaling

> Probes tell K8s whether the app is "alive" or "ready" — HPA auto-scales pods to match load.

| Aspect           | Detail                                                                     |
| ---------------- | -------------------------------------------------------------------------- |
| **K8s Object**   | Probes (in Pod spec), `autoscaling/v2/HPA`, `autoscaling.k8s.io/v1/VPA`   |
| **Use case**     | Self-healing, auto-scaling, zero-downtime                                  |
| **Go relevance** | Health endpoints, custom metrics exporter                                  |
| **Kubectl**      | `kubectl describe pod`, `kubectl get hpa`                                  |

📅 Created: 2026-03-20 · 🔄 Updated: 2026-04-20 · ⏱️ 15 min read

---

## 1. DEFINE

Picture a workload that not only needs to run, but must prove when it is alive, when it is ready, and when it should scale. Health probes and scaling only become clear when you place them under real operational pressure.

### 3 Types of Probes

| Probe         | Question                           | On failure                           | When checked          |
| ------------- | ---------------------------------- | ------------------------------------ | --------------------- |
| **Liveness**  | Is the app alive?                  | K8s kills + restarts Pod             | Continuously after startup |
| **Readiness** | Is the app ready to serve traffic? | Removed from Service endpoints       | Continuously after startup |
| **Startup**   | Has the app finished initializing? | K8s kills + restarts (startup timeout) | Only during startup   |

### Probe Methods

| Method         | Description                                | Use case                |
| -------------- | ------------------------------------------ | ----------------------- |
| **HTTP GET**   | Check HTTP status code (200-399 = healthy) | Web servers, APIs       |
| **TCP Socket** | Check port open                            | Databases, TCP services |
| **gRPC**       | gRPC health check protocol                 | gRPC services           |
| **Exec**       | Run command, exit code 0 = healthy         | Custom checks           |

### Auto-scaling Types

| Type                   | Scale by                        | Direction             | Object                    |
| ---------------------- | ------------------------------- | --------------------- | ------------------------- |
| **HPA**                | CPU, Memory, Custom metrics     | Horizontal (replicas) | `HorizontalPodAutoscaler` |
| **VPA**                | Actual usage patterns           | Vertical (resources)  | `VerticalPodAutoscaler`   |
| **KEDA**               | External metrics (queue length) | Horizontal            | `ScaledObject`            |
| **Cluster Autoscaler** | Node capacity                   | Add/remove Nodes      | Cloud provider            |

### Failure Modes

| Mistake                                  | Cause                               | Fix                                 |
| ---------------------------------------- | ----------------------------------- | ----------------------------------- |
| Liveness continuously fails → restart loop | Endpoint too heavy or timeout short | Increase timeout, reduce check complexity |
| Readiness fails → no traffic              | DB connection lost                  | Separate DB health from readiness   |
| HPA thrashing (scale up/down repeatedly)  | Metric unstable                     | Increase `stabilizationWindowSeconds` |
| VPA conflicts with HPA                    | Both scale CPU                      | Use VPA for memory, HPA for CPU     |

---

Those failure modes sound familiar. But there is a trap: a liveness probe that is too heavy causes a pod restart loop, and HPA scaling by CPU for an IO-bound workload uses the wrong metric. That trap appears in PITFALLS.

## 2. VISUAL

![Kubernetes Architecture](./images/k8s-architecture.png)

### Probe Decision Tree

```text
Pod Starting
     │
     ▼
┌─────────────┐     fail (< failureThreshold)
│  Startup    │────────────────────────────┐
│  Probe      │                            │
└──────┬──────┘                            ▼
       │ success                      Kill + Restart
       ▼
┌──────────────────────────────────────────────┐
│  Running — Both probes active                 │
│                                               │
│  ┌──────────┐ fail    ┌────────────────────┐ │
│  │ Liveness │────────►│ Kill + Restart Pod │ │
│  │ Probe    │         └────────────────────┘ │
│  └──────────┘                                │
│                                               │
│  ┌──────────┐ fail    ┌────────────────────┐ │
│  │Readiness │────────►│ Remove from Service│ │
│  │ Probe    │         │ Endpoints (no traffic)│
│  └──────────┘ success └────────────────────┘ │
│       │──────────────►│ Add back to Endpoints│ │
│                       └────────────────────┘ │
└──────────────────────────────────────────────┘
```

### HPA Scaling Flow

```text
                    ┌─────────────────┐
                    │  Metrics Server  │
                    │  (CPU/Memory)    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │       HPA       │
                    │ target: 70% CPU │
                    │ min: 2, max: 10 │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │ CPU < 70%          │ CPU = 70%           │ CPU > 70%
        │ Scale Down         │ No Change           │ Scale Up
        ▼                    ▼                     ▼
   Replicas: 2          Replicas: 5          Replicas: 8
   (min)                (current)            (→ max: 10)
```

*Figure: The startup probe gates liveness/readiness. Liveness failure triggers a restart; readiness failure removes the pod from endpoints. HPA watches resource utilization and adjusts replica count between min and max.*

---

## 3. CODE

The diagrams showed the probe decision tree and scaling flow. Code below shows how to build production-grade health endpoints, configure HPA, and integrate KEDA for event-driven scaling.

### Example 1: Basic — Production-grade Health Endpoints

> **Goal**: Go server with proper health/readiness endpoints for K8s
> **Requires**: HTTP server, database connection
> **Outcome**: K8s-aware health checking

```go
// health/handler.go — Production health check system
package health

import (
	"context"
	"database/sql"
	"encoding/json"
	"net/http"
	"sync"
	"sync/atomic"
	"time"
)

// ✅ Health status
type Status struct {
	Status    string            `json:"status"`
	Checks   map[string]Check  `json:"checks,omitempty"`
	Uptime   string            `json:"uptime"`
}

type Check struct {
	Status  string `json:"status"`
	Latency string `json:"latency,omitempty"`
	Error   string `json:"error,omitempty"`
}

type Handler struct {
	db        *sql.DB
	startTime time.Time
	ready     atomic.Bool
	mu        sync.RWMutex
}

func NewHandler(db *sql.DB) *Handler {
	h := &Handler{
		db:        db,
		startTime: time.Now(),
	}
	return h
}

// ✅ SetReady — call when app has finished warming up
func (h *Handler) SetReady(ready bool) {
	h.ready.Store(ready)
}

// ✅ Liveness: is the app process alive? (simple, fast)
// Do NOT check dependencies (DB, Redis) → avoids cascade restart
func (h *Handler) Liveness(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(Status{
		Status: "alive",
		Uptime: time.Since(h.startTime).Round(time.Second).String(),
	})
}

// ✅ Readiness: is the app ready to serve traffic?
// Check dependencies because if DB is down → should not receive requests
func (h *Handler) Readiness(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	if !h.ready.Load() {
		w.WriteHeader(http.StatusServiceUnavailable)
		json.NewEncoder(w).Encode(Status{Status: "not_ready"})
		return
	}

	checks := make(map[string]Check)
	allHealthy := true

	// ✅ Check database
	dbCheck := h.checkDB()
	checks["database"] = dbCheck
	if dbCheck.Status != "healthy" {
		allHealthy = false
	}

	status := "ready"
	httpCode := http.StatusOK
	if !allHealthy {
		status = "degraded"
		httpCode = http.StatusServiceUnavailable
	}

	w.WriteHeader(httpCode)
	json.NewEncoder(w).Encode(Status{
		Status: status,
		Checks: checks,
		Uptime: time.Since(h.startTime).Round(time.Second).String(),
	})
}

func (h *Handler) checkDB() Check {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	start := time.Now()
	if err := h.db.PingContext(ctx); err != nil {
		return Check{
			Status:  "unhealthy",
			Latency: time.Since(start).String(),
			Error:   err.Error(),
		}
	}
	return Check{
		Status:  "healthy",
		Latency: time.Since(start).String(),
	}
}
```

```yaml
# k8s/deployment-health.yaml
spec:
    template:
        spec:
            containers:
                - name: api
                  # ✅ Startup probe — allows 60s for initialization (30 × 2s)
                  startupProbe:
                      httpGet:
                          path: /healthz
                          port: 8080
                      failureThreshold: 30
                      periodSeconds: 2

                  # ✅ Liveness — simple, does NOT check DB
                  livenessProbe:
                      httpGet:
                          path: /healthz
                          port: 8080
                      periodSeconds: 10
                      timeoutSeconds: 3
                      failureThreshold: 3

                  # ✅ Readiness — checks DB, dependencies
                  readinessProbe:
                      httpGet:
                          path: /readyz
                          port: 8080
                      periodSeconds: 5
                      timeoutSeconds: 3
                      failureThreshold: 2
                      successThreshold: 1
```

> **✅ Outcome**: Proper separation: liveness (process alive) vs readiness (can serve).
> **⚠️ Note**: Do NOT check DB in liveness → if DB is down, restarting the app solves nothing.

---

Health probes are covered. But autoscaling needs HPA — time to scale.

### Example 2: Intermediate — HPA with Metrics Server

> **Goal**: Auto-scale Go API pods based on CPU/Memory
> **Requires**: Metrics Server installed
> **Outcome**: Pay-per-use scaling

```bash
# ✅ Install Metrics Server (minikube)
minikube addons enable metrics-server

# Or production:
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
    name: go-api-hpa
spec:
    scaleTargetRef:
        apiVersion: apps/v1
        kind: Deployment
        name: go-api
    minReplicas: 2
    maxReplicas: 20
    metrics:
        # ✅ Scale based on CPU utilization
        - type: Resource
          resource:
              name: cpu
              target:
                  type: Utilization
                  averageUtilization: 70 # Scale when CPU > 70%
        # ✅ Scale based on Memory
        - type: Resource
          resource:
              name: memory
              target:
                  type: Utilization
                  averageUtilization: 80
    behavior:
        scaleUp:
            # ✅ Scale fast when load increases
            stabilizationWindowSeconds: 30
            policies:
                - type: Percent
                  value: 100 # Double the replicas
                  periodSeconds: 30
                - type: Pods
                  value: 4 # Or add 4 pods
                  periodSeconds: 30
            selectPolicy: Max
        scaleDown:
            # ✅ Scale slowly when load decreases (avoid thrashing)
            stabilizationWindowSeconds: 300 # Wait 5 minutes
            policies:
                - type: Percent
                  value: 25 # Reduce by 25%
                  periodSeconds: 60
```

```bash
# Deploy HPA
kubectl apply -f k8s/hpa.yaml

# ✅ Watch HPA
kubectl get hpa go-api-hpa -w
# NAME          REFERENCE        TARGETS         MINPODS   MAXPODS   REPLICAS
# go-api-hpa    Deployment/go-api  45%/70%        2         20        3

# ✅ Load test → trigger scale up
kubectl run loadtest --rm -it --image=busybox -- \
  sh -c "while true; do wget -q -O- http://go-api/; done"
```

> **✅ Outcome**: Auto-scale 2→20 pods based on resource usage.
> **⚠️ Note**: Pod must set `resources.requests` — HPA needs a baseline to calculate utilization %.

---

HPA is covered. But custom metrics need an adapter — time to extend.

### Example 3: Advanced — Custom Metrics + KEDA

> **Goal**: Scale Go workers based on queue length (RabbitMQ/Redis)
> **Requires**: KEDA + Prometheus/RabbitMQ
> **Outcome**: Event-driven auto-scaling

```go
// metrics/prometheus.go — Expose custom metrics for HPA
package metrics

import (
	"net/http"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
	// ✅ Custom metrics for auto-scaling
	requestsTotal = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "http_requests_total",
			Help: "Total HTTP requests",
		},
		[]string{"method", "path", "status"},
	)

	requestDuration = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "http_request_duration_seconds",
			Help:    "HTTP request duration",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"method", "path"},
	)

	// ✅ Queue depth — used for KEDA scaling
	queueDepth = prometheus.NewGauge(
		prometheus.GaugeOpts{
			Name: "job_queue_depth",
			Help: "Number of jobs waiting in queue",
		},
	)

	activeWorkers = prometheus.NewGauge(
		prometheus.GaugeOpts{
			Name: "active_workers",
			Help: "Number of currently active workers",
		},
	)
)

func init() {
	prometheus.MustRegister(requestsTotal, requestDuration, queueDepth, activeWorkers)
}

// ✅ Expose /metrics endpoint for Prometheus scrape
func MetricsHandler() http.Handler {
	return promhttp.Handler()
}

// ✅ Update queue depth — call when polling queue
func SetQueueDepth(depth float64) {
	queueDepth.Set(depth)
}
```

```yaml
# k8s/keda-scaler.yaml — KEDA ScaledObject
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
    name: go-worker-scaler
spec:
    scaleTargetRef:
        name: go-worker # ✅ Target Deployment
    pollingInterval: 15 # Check every 15s
    cooldownPeriod: 300 # Wait 5 minutes before scale down
    minReplicaCount: 1
    maxReplicaCount: 50
    triggers:
        # ✅ Scale based on RabbitMQ queue length
        - type: rabbitmq
          metadata:
              host: amqp://user:pass@rabbitmq.default.svc.cluster.local
              queueName: job-queue
              queueLength: '10' # 1 worker per 10 messages
        # ✅ Or scale based on Prometheus custom metric
        - type: prometheus
          metadata:
              serverAddress: http://prometheus.monitoring.svc.cluster.local:9090
              metricName: job_queue_depth
              query: sum(job_queue_depth)
              threshold: '50'
```

> **✅ Outcome**: Scale workers 1→50 based on queue depth, event-driven.
> **⚠️ Note**: KEDA can scale to 0 (zero idle cost). Set min 1 if always-on is needed.

---

You have walked through probes, HPA, and custom metrics. Now comes the dangerous part: probe restart loops and wrong scaling metrics — the trap set up from the beginning.

## 4. PITFALLS

| #   | Mistake                                                | Consequence              | Fix                                      |
| --- | ------------------------------------------------------ | ------------------------ | ---------------------------------------- |
| 1   | Liveness checks DB → DB down → all pods restart        | Cascade failure          | Only check DB in readiness               |
| 2   | HPA + manual `kubectl scale` → conflict                | Scale reverted           | Only use HPA, never manual scale         |
| 3   | `resources.requests` not set → HPA does not work       | No scaling               | Always set requests for CPU/memory       |
| 4   | Scale up too fast → resource exhaustion                | Node pressure            | Set `scaleUp.stabilizationWindowSeconds` |
| 5   | Startup probe too strict → slow apps restart repeatedly | App never starts         | Increase `failureThreshold × periodSeconds` |

---

## 5. REF

| Resource             | Link                                                                                                                                                                                                  |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Probes               | [kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) |
| HPA                  | [kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)                                                       |
| KEDA                 | [keda.sh](https://keda.sh/)                                                                                                                                                                           |
| Prometheus Go Client | [github.com/prometheus/client_golang](https://github.com/prometheus/client_golang)                                                                                                                    |
| Metrics Server       | [github.com/kubernetes-sigs/metrics-server](https://github.com/kubernetes-sigs/metrics-server)                                                                                                        |

---

## 6. RECOMMEND

| Extension               | When                       | Reason                                     |
| ----------------------- | -------------------------- | ------------------------------------------ |
| **KEDA**                | Event-driven workloads     | Scale based on 50+ event sources           |
| **VPA**                 | Optimize resource requests | Auto-tune memory/CPU based on actual usage |
| **Goldilocks**          | Right-sizing resources     | Dashboard recommends resource limits       |
| **PodDisruptionBudget** | HA during scaling          | Ensure min available pods                  |
| **Kube-state-metrics**  | Advanced HPA metrics       | Expose K8s object states                   |

---

## 🔍 Debug Checklist

| # | Symptom | Cause | Debug Command |
|---|---------|-------|---------------|
| 1 | Liveness probe continuously fails → pod restart loop | Endpoint too heavy, timeout too short, or DB check in liveness | `kubectl describe pod <pod>` → check `Liveness probe failed` events |
| 2 | Readiness probe fails → pod receives no traffic | DB connection lost or app has not finished warming up | `kubectl describe pod <pod>` and `kubectl exec <pod> -- curl localhost:8080/readyz` |
| 3 | HPA does not scale | Metrics Server not installed, or pod missing `resources.requests` | `kubectl get hpa` and `kubectl top pods` |
| 4 | HPA thrashing (scale up/down repeatedly) | Metric unstable, `stabilizationWindowSeconds` too low | `kubectl describe hpa <name>` check Events |
| 5 | Startup probe timeout → slow app cannot start | `failureThreshold × periodSeconds` too low | Increase `failureThreshold: 30` × `periodSeconds: 2` = 60s buffer |
| 6 | `kubectl top pods` does not work | Metrics Server not installed or crashed | `kubectl get pods -n kube-system \| grep metrics-server` |
| 7 | VPA conflicts with HPA | Both adjust CPU resource → thrashing | Use VPA for memory, HPA for CPU; or use KEDA |

---

## 🃏 Quick Reference

| # | Pattern | Command / Rule |
|---|---------|----------------|
| 1 | View HPA status | `kubectl get hpa` |
| 2 | View pod resource usage | `kubectl top pods -n <ns>` |
| 3 | View node resource usage | `kubectl top nodes` |
| 4 | Liveness probe HTTP | `httpGet: {path: /healthz, port: 8080}`, `failureThreshold: 3` |
| 5 | Readiness probe HTTP | `httpGet: {path: /readyz, port: 8080}`, `failureThreshold: 2` |
| 6 | Startup probe (slow apps) | `failureThreshold: 30`, `periodSeconds: 2` = 60s total |
| 7 | Basic HPA YAML | `minReplicas: 2`, `maxReplicas: 10`, `averageUtilization: 70` |
| 8 | Slow scale down | `scaleDown.stabilizationWindowSeconds: 300` (5 minutes) |

---

## 🎯 Interview Angle

**Relevant system design / technical questions:**
- *"How do liveness, readiness, and startup probes differ? When do you need all three?"*
- *"How does HPA calculate the number of replicas from CPU utilization?"*
- *"Why should you never check the database in a liveness probe?"*

**Points the interviewer wants to hear:**

| Topic | Talking Point |
|-------|---------------|
| Liveness vs Readiness | Liveness: is the app process alive? → fail = restart pod; Readiness: ready to serve traffic? → fail = remove from endpoints |
| Startup probe | Allows the app to initialize slowly without being killed by liveness; once startup succeeds, liveness begins checking |
| DB in liveness | If DB is down and liveness checks DB → all pods restart → doesn't help at all; makes it worse |
| HPA formula | `desiredReplicas = ceil(currentReplicas × currentUtilization / targetUtilization)` |
| Scale down delay | `stabilizationWindowSeconds: 300` = wait 5 minutes before scaling down → avoids thrashing |
| KEDA | Scales based on external events (queue length, Kafka lag); can scale to 0 when no events exist |

**Common follow-up questions:**
- *"What must a Pod have for HPA to work?"* → Must have `resources.requests` for CPU/Memory; HPA calculates `utilization = actual / request × 100%`.
- *"How does VPA work?"* → VPA analyzes historical usage → recommends resources; `updateMode: Auto` restarts pods with new resources.
- *"Why should `successThreshold: 1` be set in readiness probe?"* → Default is 1; increase if you need the probe to succeed multiple consecutive times before accepting traffic (reduces false positives).

---

**Links**: [← Helm Charts](./07-helm.md) · [→ CI/CD Pipeline](./09-cicd-pipeline.md)
