<!-- tags: kubernetes, k8s, ci-cd, devops -->
# 🔄 CI/CD Pipeline

> Automate the entire workflow: Code → Build → Test → Deploy → Monitor.

| Aspect           | Detail                                             |
| ---------------- | -------------------------------------------------- |
| **Tools**        | GitLab CI, GitHub Actions, ArgoCD, Tekton          |
| **Use case**     | Continuous Integration, Continuous Deployment      |
| **Go relevance** | Go build → Docker image → K8s deploy               |
| **Pattern**      | Push-based (CI tool deploy) vs Pull-based (GitOps) |

📅 Created: 2026-03-20 · 🔄 Updated: 2026-04-20 · ⏱️ 15 min read

---

## 1. DEFINE

Picture the path from git to cluster as a journey with more breakpoints than the team usually thinks. This pipeline article exists to keep changes entering the cluster through a mechanism that is controlled, rollback-capable, and observable.

### CI vs CD vs CD

| Abbreviation | Full Name              | Description                                    |
| ------------ | ---------------------- | ---------------------------------------------- |
| **CI**       | Continuous Integration | Auto build + test on every commit              |
| **CD**       | Continuous Delivery    | Auto deploy to staging, manual approve for prod |
| **CD**       | Continuous Deployment  | Auto deploy to production (every commit)       |

### Push-based vs Pull-based (GitOps)

| Feature             | Push-based             | Pull-based (GitOps)           |
| ------------------- | ---------------------- | ----------------------------- |
| **Deploy trigger**  | CI pipeline push       | Cluster agent pull            |
| **Credentials**     | CI needs K8s access    | Cluster agent already has access |
| **Security**        | Cluster creds in CI    | No creds exposed externally   |
| **Drift detection** | ❌                     | ✅ Auto-reconcile             |
| **Tools**           | GitLab CI, Jenkins     | ArgoCD, Flux                  |
| **Recommended**     | ✅ Simpler             | ✅ More secure                |

### Actors

| Actor                  | Role                                 |
| ---------------------- | ------------------------------------ |
| **CI Server**          | Build, test, scan, push image        |
| **Container Registry** | Store Docker images                  |
| **GitOps Agent**       | Sync K8s state with Git (ArgoCD/Flux) |
| **Helm/Kustomize**     | Template K8s manifests               |

### Failure Modes

| Mistake             | Cause                           | Fix                               |
| ------------------- | ------------------------------- | --------------------------------- |
| Image build fail    | Dependency missing, test fail   | Fix code, update Dockerfile       |
| Deploy timeout      | Pods not ready, resource limits | Check readiness probes, resources |
| ArgoCD out of sync  | Manual change on cluster        | `argocd app sync --prune`         |
| Rollback fail       | No previous revision            | Keep revision history             |

---

Those failure modes sound clear. But there is a trap: a pipeline deploying without RBAC means kubectl fails, and pushing an image before tests means low-quality artifacts. That trap appears in PITFALLS.

## 2. VISUAL

The definition locked the vocabulary. The visual below shows how CI builds, container registries, and GitOps controllers orchestrate deployments across environments.

![K8s CI/CD — Developer → CI → Docker build → Registry → ArgoCD/Flux GitOps → K8s cluster with env promotion](./images/k8s-cicd-pipeline.png)

### Full CI/CD Pipeline

```text
┌──────┐    ┌────────┐    ┌────────┐    ┌─────────┐    ┌──────────┐
│ Code │───►│  CI    │───►│ Build  │───►│  Push   │───►│  Deploy  │
│ Push │    │ Test   │    │ Image  │    │ Registry│    │  K8s     │
└──────┘    └────────┘    └────────┘    └─────────┘    └──────────┘
   │           │              │              │              │
   │     ┌─────▼─────┐  ┌────▼────┐    ┌────▼────┐   ┌────▼─────┐
   │     │ Unit Test  │  │ Docker  │    │ ECR/GCR │   │ ArgoCD   │
   │     │ Lint       │  │ Build   │    │ Harbor  │   │ or       │
   │     │ Vuln Scan  │  │ Multi-  │    │ DockerHub│  │ kubectl  │
   │     └────────────┘  │ stage   │    └─────────┘   └──────────┘
   │                     └─────────┘
   │
   │    GitOps Flow (Pull-based):
   │    ┌─────────┐    ┌──────────┐    ┌──────────┐
   └───►│  Git    │───►│ ArgoCD   │───►│ K8s      │
        │  Repo   │    │ (watch)  │    │ Cluster  │
        │ k8s/    │    │ auto-sync│    │ apply    │
        └─────────┘    └──────────┘    └──────────┘
```

*Figure: Push-based flow runs CI stages sequentially. GitOps flow separates concerns — CI only builds and pushes images; ArgoCD watches the Git repo and syncs cluster state automatically.*

---

## 3. CODE

The diagram showed the pipeline flow. Code below shows how to build a GitLab CI pipeline, use `ko` for fast Go image builds, and set up ArgoCD for GitOps deployment.

### Example 1: Basic — GitLab CI Pipeline for Go

> **Goal**: CI pipeline: lint → test → build Docker image → push registry
> **Requires**: GitLab CI, Docker-in-Docker
> **Outcome**: Automated CI for every commit

```yaml
# .gitlab-ci.yml
stages:
    - test
    - build
    - deploy

variables:
    DOCKER_IMAGE: ${CI_REGISTRY_IMAGE}
    GO_VERSION: '1.21'

# ✅ Cache Go modules
.go-cache:
    cache:
        key: go-modules-${CI_COMMIT_REF_SLUG}
        paths:
            - .go/pkg/mod/
        policy: pull-push
    variables:
        GOPATH: ${CI_PROJECT_DIR}/.go

# ════════════════════════════════════════
# Stage: TEST
# ════════════════════════════════════════

lint:
    stage: test
    image: golangci/golangci-lint:v1.55
    extends: .go-cache
    script:
        - golangci-lint run ./... --timeout 5m
    rules:
        - if: $CI_MERGE_REQUEST_IID # ✅ Only run in MRs

test:
    stage: test
    image: golang:${GO_VERSION}-alpine
    extends: .go-cache
    services:
        - name: postgres:16-alpine
          alias: postgres
    variables:
        POSTGRES_DB: testdb
        POSTGRES_USER: testuser
        POSTGRES_PASSWORD: testpass
        DATABASE_URL: 'postgres://testuser:testpass@postgres:5432/testdb?sslmode=disable'
    script:
        - go test -race -coverprofile=coverage.out ./...
        - go tool cover -func=coverage.out
    coverage: '/total:\s+\(statements\)\s+(\d+\.\d+)%/'
    artifacts:
        reports:
            coverage_report:
                coverage_format: cobertura
                path: coverage.out

security-scan:
    stage: test
    image: golang:${GO_VERSION}-alpine
    script:
        # ✅ Vulnerability scan
        - go install golang.org/x/vuln/cmd/govulncheck@latest
        - govulncheck ./...
    allow_failure: true

# ════════════════════════════════════════
# Stage: BUILD
# ════════════════════════════════════════

build-image:
    stage: build
    image: docker:24
    services:
        - docker:24-dind
    variables:
        DOCKER_TLS_CERTDIR: '/certs'
    script:
        # ✅ Login to registry
        - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY

        # ✅ Build with cache
        - docker build
          --cache-from $DOCKER_IMAGE:latest
          --tag $DOCKER_IMAGE:$CI_COMMIT_SHA
          --tag $DOCKER_IMAGE:$CI_COMMIT_REF_SLUG
          --tag $DOCKER_IMAGE:latest
          --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
          --build-arg VERSION=$CI_COMMIT_SHA
          .

        # ✅ Push all tags
        - docker push $DOCKER_IMAGE:$CI_COMMIT_SHA
        - docker push $DOCKER_IMAGE:$CI_COMMIT_REF_SLUG
        - docker push $DOCKER_IMAGE:latest
    only:
        - main
        - tags

# ════════════════════════════════════════
# Stage: DEPLOY
# ════════════════════════════════════════

deploy-staging:
    stage: deploy
    image: bitnami/kubectl:1.28
    script:
        - kubectl config use-context staging
        - kubectl set image deployment/go-api api=$DOCKER_IMAGE:$CI_COMMIT_SHA -n staging
        - kubectl rollout status deployment/go-api -n staging --timeout=300s
    environment:
        name: staging
        url: https://api-staging.example.com
    only:
        - main

deploy-production:
    stage: deploy
    image: bitnami/kubectl:1.28
    script:
        - kubectl config use-context production
        - kubectl set image deployment/go-api api=$DOCKER_IMAGE:$CI_COMMIT_SHA -n production
        - kubectl rollout status deployment/go-api -n production --timeout=600s
    environment:
        name: production
        url: https://api.example.com
    only:
        - tags
    when: manual # ✅ Manual approve for production
```

> **✅ Outcome**: Automated CI/CD: lint → test → build → deploy staging → manual deploy prod.
> **⚠️ Note**: Use `$CI_COMMIT_SHA` as image tag — immutable, traceable.

---

Basic CI is covered. But CD needs deploy automation — time to integrate.

### Example 2: Intermediate — GitHub Actions + Ko (fast Go image builds)

> **Goal**: Build Go images without Dockerfile using `ko`, deploy with kustomize
> **Requires**: GitHub Actions, `ko`
> **Outcome**: Fastest Go → K8s pipeline

```yaml
# .github/workflows/deploy.yaml
name: Build & Deploy

on:
    push:
        branches: [main]
    pull_request:
        branches: [main]

env:
    KO_DOCKER_REPO: ghcr.io/${{ github.repository }}

jobs:
    test:
        runs-on: ubuntu-latest
        steps:
            - uses: actions/checkout@v4

            - uses: actions/setup-go@v5
              with:
                  go-version: '1.21'
                  cache: true

            - name: Lint
              uses: golangci/golangci-lint-action@v3
              with:
                  version: latest

            - name: Test
              run: |
                  go test -race -coverprofile=coverage.out ./...
                  go tool cover -func=coverage.out

            - name: Vulnerability Check
              run: |
                  go install golang.org/x/vuln/cmd/govulncheck@latest
                  govulncheck ./...

    build-deploy:
        needs: test
        if: github.ref == 'refs/heads/main'
        runs-on: ubuntu-latest
        permissions:
            packages: write
            contents: read

        steps:
            - uses: actions/checkout@v4

            - uses: actions/setup-go@v5
              with:
                  go-version: '1.21'

            # ✅ ko — build Go image WITHOUT Dockerfile
            - uses: ko-build/setup-ko@v0.6

            - name: Login to GHCR
              run: ko login ghcr.io -u ${{ github.actor }} -p ${{ secrets.GITHUB_TOKEN }}

            # ✅ Build + Push in one step
            - name: Build & Push
              run: |
                  KO_IMAGE=$(ko build ./cmd/server \
                    --base-import-paths \
                    --tags ${{ github.sha }},latest)
                  echo "IMAGE=$KO_IMAGE" >> $GITHUB_ENV

            # ✅ Deploy to K8s
            - name: Deploy
              uses: azure/k8s-deploy@v4
              with:
                  namespace: production
                  manifests: k8s/
                  images: ${{ env.IMAGE }}
```

> **✅ Outcome**: `ko` builds a Go image in ~5 seconds (vs Docker ~30-60s), no Dockerfile needed.
> **⚠️ Note**: `ko` is only for Go apps. Use Dockerfile for apps with native dependencies.

---

CD is covered. But multi-env needs promotion — time to pipeline.

### Example 3: Advanced — GitOps with ArgoCD

> **Goal**: ArgoCD auto-syncs K8s state from Git — pull-based deployment
> **Requires**: ArgoCD installed, Git repo with K8s manifests
> **Outcome**: Self-healing cluster, drift detection, audit trail

```bash
# ✅ Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f \
  https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# ✅ Access ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# ✅ Login
argocd admin initial-password -n argocd
argocd login localhost:8080
```

```yaml
# argocd/application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
    name: go-api
    namespace: argocd
spec:
    project: default
    source:
        # ✅ Git repo containing K8s manifests or Helm chart
        repoURL: https://gitlab.com/myteam/go-api-k8s.git
        targetRevision: main
        path: k8s/overlays/production # Kustomize path
    destination:
        server: https://kubernetes.default.svc
        namespace: production
    syncPolicy:
        # ✅ Auto-sync — apply when Git changes
        automated:
            prune: true # Delete resources no longer in Git
            selfHeal: true # Revert manual changes on cluster
        syncOptions:
            - CreateNamespace=true
            - PruneLast=true
        retry:
            limit: 3
            backoff:
                duration: 5s
                maxDuration: 3m
                factor: 2
---
# argocd/application-staging.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
    name: go-api-staging
    namespace: argocd
spec:
    project: default
    source:
        repoURL: https://gitlab.com/myteam/go-api-k8s.git
        targetRevision: develop # ✅ Staging = develop branch
        path: k8s/overlays/staging
    destination:
        server: https://kubernetes.default.svc
        namespace: staging
    syncPolicy:
        automated:
            prune: true
            selfHeal: true
```

```text
# ✅ CI only needs to: build image + update Git repo
# GitLab CI deploy stage (GitOps style):
update-k8s-manifest:
  stage: deploy
  script:
    # Clone K8s repo
    - git clone https://gitlab.com/myteam/go-api-k8s.git
    - cd go-api-k8s

    # ✅ Update image tag in kustomization
    - cd k8s/overlays/production
    - kustomize edit set image go-api=${DOCKER_IMAGE}:${CI_COMMIT_SHA}

    # ✅ Commit + push → ArgoCD auto-sync
    - git add .
    - git commit -m "deploy: update go-api to ${CI_COMMIT_SHA}"
    - git push
```

> **✅ Outcome**: GitOps — Git is the single source of truth. ArgoCD auto-syncs, self-heals, provides audit trail.
> **⚠️ Note**: CI does not need K8s credentials. Only ArgoCD inside the cluster has access.

---

You have walked through CI, CD, and multi-env promotion. Now comes the dangerous part: missing RBAC and premature push — the trap set up from the beginning.

## 4. PITFALLS

| #   | Mistake                                     | Consequence              | Fix                                           |
| --- | ------------------------------------------- | ------------------------ | --------------------------------------------- |
| 1   | CI uses `latest` tag → deploys wrong version | Untraceable deployments  | Always use `$COMMIT_SHA` or semver            |
| 2   | K8s creds in CI get leaked                   | Cluster compromised      | Use GitOps (ArgoCD) — no external creds       |
| 3   | Rollout timeout in CI → pipeline fails       | False deploy failure     | Set appropriately, check readiness probes     |
| 4   | ArgoCD sync loop (continuously syncing)      | Resource churn           | Check YAML drift, remove server-side defaults |
| 5   | Go tests run slowly in CI                    | Slow feedback loop       | Parallel tests: `go test -parallel 4` + cache |

---

## 5. REF

| Resource               | Link                                                                                                        |
| ---------------------- | ----------------------------------------------------------------------------------------------------------- |
| ArgoCD                 | [argo-cd.readthedocs.io](https://argo-cd.readthedocs.io/)                                                   |
| ko                     | [ko.build](https://ko.build/)                                                                               |
| GitLab K8s Integration | [docs.gitlab.com/ee/user/infrastructure/clusters](https://docs.gitlab.com/ee/user/infrastructure/clusters/) |
| GitHub Actions Docs    | [docs.github.com/en/actions](https://docs.github.com/en/actions)                                            |
| Kustomize              | [kustomize.io](https://kustomize.io/)                                                                       |

---

## 6. RECOMMEND

| Extension                | When                    | Reason                        |
| ------------------------ | ----------------------- | ----------------------------- |
| **Flux CD**              | Alternative GitOps      | Lightweight, CNCF graduated   |
| **Tekton**               | Cloud-native CI/CD      | K8s-native pipeline engine    |
| **Trivy**                | Container security scan | Scan vulnerabilities in CI    |
| **Cosign**               | Image signing           | Verify image provenance       |
| **ArgoCD Image Updater** | Auto-update image tags  | Watch registry, update Git    |

---

## 🔍 Debug Checklist

| # | Symptom | Cause | Debug Command |
|---|---------|-------|---------------|
| 1 | Pipeline fails at deploy step | `kubectl` lacks permissions or kubeconfig is wrong | Check CI env vars `KUBECONFIG` and `kubectl auth can-i` |
| 2 | Image pull fails in K8s after CI push | `imagePullSecrets` not configured for private registry | `kubectl describe pod <pod>` → `ImagePullBackOff` events |
| 3 | `rollout status` times out in CI | Readiness probe fails or pod crashes after deploy | `kubectl get pods -n <ns>` and `kubectl logs <new-pod>` |
| 4 | ArgoCD out of sync continuously | Server-side defaults add fields to object → drift | `argocd app diff <app>` to see diff; use `ignoreDifferences` |
| 5 | CI uses `latest` tag → deploys old version | `imagePullPolicy: IfNotPresent` uses cached image | Use `$COMMIT_SHA` tag and `imagePullPolicy: Always` |
| 6 | RBAC denied in CI pipeline | ServiceAccount for CI lacks permissions | `kubectl describe rolebinding -n <ns>` and `kubectl auth can-i deploy --as=system:serviceaccount:<ns>:<sa>` |
| 7 | GitOps: CI has no K8s creds but ArgoCD syncs fine | ArgoCD reads Git repo instead of CI pushing directly | This is the correct design — CI only pushes image + updates Git manifest |

---

## 🃏 Quick Reference

| # | Pattern | Command / Rule |
|---|---------|----------------|
| 1 | Update image in CI | `kubectl set image deployment/<name> <container>=<image>:<sha>` |
| 2 | Wait for rollout in CI | `kubectl rollout status deployment/<name> --timeout=300s` |
| 3 | Image tag strategy | Use `$COMMIT_SHA` (immutable) or semver; avoid `latest` |
| 4 | Create kubeconfig in CI | Use Service Account token + cluster CA cert |
| 5 | ArgoCD manual sync | `argocd app sync <app> --prune` |
| 6 | Install ArgoCD | `kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml` |
| 7 | Kustomize update image tag | `kustomize edit set image <image>=<image>:<sha>` |
| 8 | Check CI K8s permissions | `kubectl auth can-i create deployments --as=system:serviceaccount:<ns>:<sa>` |

---

## 🎯 Interview Angle

**Relevant system design / technical questions:**
- *"How do push-based CI/CD and GitOps pull-based differ? What are the pros and cons?"*
- *"Why is GitOps considered more secure? How are credentials managed?"*
- *"How is blue-green deployment implemented in CI/CD?"*

**Points the interviewer wants to hear:**

| Topic | Talking Point |
|-------|---------------|
| Push vs Pull | Push: CI tool has K8s credentials, deploys directly → creds are exposed if CI is compromised; Pull: ArgoCD inside cluster self-syncs Git → no creds exposed externally |
| GitOps principles | Git = single source of truth; declarative; automated reconciliation; audit trail via Git history |
| Drift detection | ArgoCD `selfHeal: true` → reverts manual changes; detects if someone runs `kubectl edit` directly |
| Image tag strategy | SHA: immutable, traceable; semver: human-readable; avoid `latest` — you don't know which version is running |
| CI vs CD | CI: build + test every commit; CD (Delivery): auto deploy to staging; CD (Deployment): auto deploy to prod |
| Rollback strategy | Push-based: `kubectl rollout undo`; GitOps: `git revert` commit → ArgoCD auto-syncs |

**Common follow-up questions:**
- *"What is `ko`? Why is it faster than Docker build?"* → `ko` builds a Go binary directly into a container image without Dockerfile; no layer overhead; ~5s vs ~30-60s.
- *"How do you secure K8s credentials in CI?"* → Use OIDC/Workload Identity (GKE, EKS); or short-lived SA tokens; GitOps eliminates the need for credentials in CI.
- *"Why should production deploy require manual approval?"* → Prevents accidental production pushes; compliance requirement; allows final validation before go-live.

---

**Links**: [← Health Checks & Auto-scaling](./08-health-scaling.md) · [→ Production Hardening](./10-production.md)
