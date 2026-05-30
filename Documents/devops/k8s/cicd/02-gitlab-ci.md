<!-- tags: kubernetes, k8s, gitlab, ci-cd -->
# 🦊 GitLab CI/CD — Pipeline for Kubernetes

> Build a complete CI/CD pipeline with GitLab CI: build, test, scan, deploy Go services to K8s.

📅 Created: 2026-03-23 · 🔄 Updated: 2026-04-20 · ⏱️ 22 min read

| Aspect         | Detail                                              |
| -------------- | --------------------------------------------------- |
| **Pattern**    | Push-based CI + GitOps CD                           |
| **Use case**   | Automated testing, building, deploying Go services  |
| **Components** | GitLab Runner, Container Registry, K8s Agent        |
| **Supports**   | Docker, Kaniko, Helm, Kustomize, ArgoCD integration |

---

## 1. DEFINE

Picture a good CI/CD pipeline that does not stop at build and test passing. It must deliver the right artifact to the right environment with enough guardrails so that deployment does not become gambling.


### What is GitLab CI/CD?

GitLab CI/CD is a continuous integration (CI) and continuous deployment (CD) system built into GitLab. Pipelines are defined in the `.gitlab-ci.yml` file at the root of the repository.

| Concept         | Description                                           |
| --------------- | ----------------------------------------------------- |
| **Pipeline**    | Collection of stages running sequentially             |
| **Stage**       | Group of jobs running in parallel within the same phase |
| **Job**         | Smallest execution unit, runs in a Docker container   |
| **Runner**      | Agent that executes jobs (shared or self-hosted)      |
| **Artifact**    | Output file from a job, shareable between stages      |
| **Cache**       | Dependencies cached between pipeline runs             |
| **Environment** | Deploy target (staging, production) with URL tracking |
| **Variable**    | Environment variable (CI predefined or custom)        |

### GitLab CI vs Other CI Tools

| Feature               | GitLab CI          | GitHub Actions      | Jenkins       | CircleCI           |
| --------------------- | ------------------ | ------------------- | ------------- | ------------------ |
| **Config file**       | `.gitlab-ci.yml`   | `.github/workflows` | `Jenkinsfile` | `.circleci/config` |
| **Built-in registry** | ✅ Yes             | ✅ GHCR             | ❌ Plugin     | ❌ External        |
| **K8s integration**   | ✅ Agent           | ❌ Manual           | ❌ Plugin     | ❌ Orbs            |
| **Auto DevOps**       | ✅ Yes             | ❌                  | ❌            | ❌                 |
| **Security scanning** | ✅ Built-in        | 🔶 Marketplace      | ❌ Plugin     | ❌ Orbs            |
| **Self-hosted**       | ✅ Yes             | ✅ Yes              | ✅ Yes        | ❌ Cloud only      |
| **Pricing**           | Free tier generous | Free tier generous  | Free (OSS)    | Limited free       |

### GitLab CI Architecture

| Component              | Role                                                |
| ---------------------- | --------------------------------------------------- |
| **GitLab Server**      | Manages repos, pipelines, UI, API                   |
| **GitLab Runner**      | Executes jobs in containers (Docker/K8s executor)   |
| **Container Registry** | Stores Docker images (built-in)                     |
| **K8s Agent**          | Secure connection between GitLab ↔ K8s cluster      |
| **Package Registry**   | Stores Go modules, npm packages, Helm charts        |

### Pipeline Stages (Best Practice)

| Stage          | Jobs                         | Purpose                  |
| -------------- | ---------------------------- | ------------------------ |
| **test**       | lint, unit-test, integration | Validate code quality    |
| **security**   | sast, dependency-scan, trivy | Security vulnerabilities |
| **build**      | docker-build, ko-build       | Build container images   |
| **deploy-stg** | deploy-staging               | Deploy to staging        |
| **verify**     | smoke-test, e2e-test         | Verify deployment        |
| **deploy-prd** | deploy-production (manual)   | Deploy to production     |

### Failure Modes

| Mistake                       | Cause                         | Fix                                   |
| ----------------------------- | ----------------------------- | ------------------------------------- |
| Runner timeout                | Job runs too long             | Increase timeout, optimize tests      |
| Docker-in-Docker (DinD) slow  | Each job creates Docker daemon | Use Kaniko or shared `docker:dind`    |
| Cache miss                    | Key mismatch                  | Use `$CI_COMMIT_REF_SLUG` as key      |
| Registry push denied          | Token expired or wrong scope  | Check `$CI_REGISTRY_*` variables      |
| K8s deploy failed             | Kubeconfig wrong or RBAC issue | Use GitLab K8s Agent                 |

---

Those failure modes are clear. But there is a trap: a runner without resource limits means CI affects the cluster, and a wrong cache key means slow builds from cache misses. That trap appears in PITFALLS.

## 2. VISUAL

Concepts have names now. The diagrams below reveal the more important part: how requests, workloads, or signals flow through these layers.


![GitLab CI/CD Pipeline](./images/gitlab-ci-pipeline.png)

### GitLab CI Pipeline Architecture

```
 Developer          GitLab Server           GitLab Runner          Container Registry       K8s Cluster
    │                     │                       │                        │                      │
    │  git push           │                       │                        │                      │
    │────────────────────►│                       │                        │                      │
    │                     │                       │                        │                      │
    │                     │  trigger pipeline     │                        │                      │
    │                     │──────────────────────►│                        │                      │
    │                     │                       │                        │                      │
    │                     │                       │  Stage: TEST           │                      │
    │                     │                       │  ├── lint (parallel)   │                      │
    │                     │                       │  ├── unit-test         │                      │
    │                     │                       │  └── security-scan    │                      │
    │                     │                       │                        │                      │
    │                     │                       │  Stage: BUILD          │                      │
    │                     │                       │  └── docker build     │                      │
    │                     │                       │      + push ──────────────────────►│          │
    │                     │                       │                        │                      │
    │                     │                       │  Stage: DEPLOY         │                      │
    │                     │                       │  └── kubectl apply  ──────────────────────────►│
    │                     │                       │                        │                      │
    │  pipeline passed ✅ │                       │                        │                      │
    │◄────────────────────│                       │                        │                      │
```

### Pipeline Stages Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GitLab CI Pipeline                         │
│                                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐ │
│  │  TEST     │    │ SECURITY │    │  BUILD    │    │   DEPLOY     │ │
│  │          │    │          │    │          │    │              │ │
│  │ ┌──────┐ │    │ ┌──────┐ │    │ ┌──────┐ │    │ ┌──────────┐│ │
│  │ │ lint │ │    │ │ SAST │ │    │ │docker│ │    │ │ staging  ││ │
│  │ └──────┘ │    │ └──────┘ │    │ │build │ │    │ │ (auto)   ││ │
│  │ ┌──────┐ │    │ ┌──────┐ │    │ │+push │ │    │ └──────────┘│ │
│  │ │ test │ │───►│ │trivy │ │───►│ └──────┘ │───►│ ┌──────────┐│ │
│  │ └──────┘ │    │ └──────┘ │    │          │    │ │production││ │
│  │ ┌──────┐ │    │ ┌──────┐ │    │          │    │ │ (manual) ││ │
│  │ │ race │ │    │ │dep   │ │    │          │    │ └──────────┘│ │
│  │ │detect│ │    │ │scan  │ │    │          │    │              │ │
│  │ └──────┘ │    │ └──────┘ │    │          │    │              │ │
│  └──────────┘    └──────────┘    └──────────┘    └──────────────┘ │
│                                                                     │
│  ───────────   ───────────   ───────────   ─────────────           │
│   Parallel      Parallel      Sequential    Auto + Manual          │
└─────────────────────────────────────────────────────────────────────┘
```

### GitOps Integration: GitLab CI + ArgoCD

```
┌─────────────────────┐     ┌──────────────────────┐     ┌────────────────────┐
│   App Source Repo    │     │  K8s Config Repo      │     │   K8s Cluster      │
│                     │     │                      │     │                    │
│ • Go source code    │     │ • Kustomize overlays │     │ ┌────────────────┐ │
│ • Dockerfile        │     │ • Helm values        │     │ │    ArgoCD      │ │
│ • .gitlab-ci.yml    │     │ • ArgoCD Application │     │ │                │ │
│                     │     │                      │     │ │ Watch + Sync   │ │
│ CI Pipeline:        │     │                      │     │ │ Self-heal      │ │
│ 1. Test             │     │                      │     │ │ Drift detect   │ │
│ 2. Build image      │     │ ◄──── CI updates ────│     │ └───────┬────────┘ │
│ 3. Push registry    │────►│      image tag       │────►│         │          │
│ 4. Update config ───│     │                      │     │    kubectl apply   │
│    repo image tag   │     │                      │     │         │          │
│                     │     │                      │     │    ┌────▼───────┐  │
│                     │     │                      │     │    │ Pods/Svc   │  │
│                     │     │                      │     │    │ Running    │  │
│                     │     │                      │     │    └────────────┘  │
└─────────────────────┘     └──────────────────────┘     └────────────────────┘
```

---

## 3. CODE

The diagrams showed the main flow. Code/manifests/commands below pull it down to the artifact level that on-call or reviewers must actually use.


### Example 1: Basic — Complete GitLab CI for Go Service

> **Goal**: Complete CI pipeline: lint → test → build → push image
> **Requires**: GitLab project, Docker Runner, Container Registry enabled
> **Outcome**: Automated CI for every commit/MR

```yaml
# .gitlab-ci.yml
# ════════════════════════════════════════════════
# GitLab CI Pipeline cho Go API Service
# ════════════════════════════════════════════════

# ✅ Define stages — run sequentially
stages:
    - test
    - build
    - deploy

# ✅ Global variables
variables:
    DOCKER_IMAGE: ${CI_REGISTRY_IMAGE}
    GO_VERSION: '1.22'
    CGO_ENABLED: '0'
    GOOS: 'linux'
    GOARCH: 'amd64'

# ✅ Cache Go modules — shared across all jobs
.go-cache: &go-cache
    cache:
        key:
            files:
                - go.sum # ⚠️ Cache key based on go.sum
        paths:
            - .go/pkg/mod/
        policy: pull-push
    variables:
        GOPATH: ${CI_PROJECT_DIR}/.go
        GOMODCACHE: ${CI_PROJECT_DIR}/.go/pkg/mod

# ════════════════════════════════════════════════
# Stage: TEST — Run in parallel
# ════════════════════════════════════════════════

lint:
    stage: test
    image: golangci/golangci-lint:v1.60-alpine
    <<: *go-cache
    script:
        # ✅ Lint entire project
        - golangci-lint run ./... --timeout 5m
        # ✅ Check formatting
        - test -z "$(gofmt -l .)" || (echo "❌ Code not formatted" && gofmt -l . && exit 1)
    rules:
        - if: $CI_MERGE_REQUEST_IID # ✅ Only run in Merge Request
        - if: $CI_COMMIT_BRANCH == "main" # ✅ Or push to main

unit-test:
    stage: test
    image: golang:${GO_VERSION}-alpine
    <<: *go-cache
    # ✅ Services — database for integration test
    services:
        - name: postgres:16-alpine
          alias: postgres
        - name: redis:7-alpine
          alias: redis
    variables:
        # ⚠️ Postgres config
        POSTGRES_DB: testdb
        POSTGRES_USER: testuser
        POSTGRES_PASSWORD: testpass
        DATABASE_URL: 'postgres://testuser:testpass@postgres:5432/testdb?sslmode=disable'
        # ⚠️ Redis config
        REDIS_URL: 'redis://redis:6379/0'
    before_script:
        # ✅ Wait for Postgres to be ready
        - apk add --no-cache postgresql-client
        - until pg_isready -h postgres -U testuser; do sleep 1; done
    script:
        # ✅ Run tests with race detector + coverage
        - go test -race -count=1 -coverprofile=coverage.out -covermode=atomic ./...
        - go tool cover -func=coverage.out
        # ✅ Generate coverage report
        - go tool cover -html=coverage.out -o coverage.html
    # ✅ Coverage regex — displayed on MR
    coverage: '/total:\s+\(statements\)\s+(\d+\.\d+)%/'
    artifacts:
        paths:
            - coverage.html
        reports:
            coverage_report:
                coverage_format: cobertura
                path: coverage.out
        expire_in: 7 days

# ════════════════════════════════════════════════
# Stage: BUILD
# ════════════════════════════════════════════════

build-image:
    stage: build
    image: docker:24
    services:
        - docker:24-dind
    variables:
        DOCKER_TLS_CERTDIR: '/certs'
        DOCKER_BUILDKIT: '1' # ✅ Enable BuildKit
    before_script:
        - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    script:
        # ✅ Build multi-stage Docker image
        - |
            docker build \
              --cache-from $DOCKER_IMAGE:latest \
              --build-arg BUILDKIT_INLINE_CACHE=1 \
              --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
              --build-arg VERSION=$CI_COMMIT_SHA \
              --build-arg GIT_COMMIT=$CI_COMMIT_SHORT_SHA \
              --tag $DOCKER_IMAGE:$CI_COMMIT_SHA \
              --tag $DOCKER_IMAGE:$CI_COMMIT_SHORT_SHA \
              --tag $DOCKER_IMAGE:$CI_COMMIT_REF_SLUG \
              --tag $DOCKER_IMAGE:latest \
              .
        # ✅ Push all tags
        - docker push $DOCKER_IMAGE:$CI_COMMIT_SHA
        - docker push $DOCKER_IMAGE:$CI_COMMIT_SHORT_SHA
        - docker push $DOCKER_IMAGE:$CI_COMMIT_REF_SLUG
        - docker push $DOCKER_IMAGE:latest
    rules:
        - if: $CI_COMMIT_BRANCH == "main"
        - if: $CI_COMMIT_TAG # ✅ Build for tags
```

> **✅ Outcome**: Complete CI pipeline: lint + test in parallel → Docker build + push.
> **⚠️ Note**: Use `go.sum` as cache key — only rebuild cache when dependencies change.

---

Basic pipeline is covered. But matrix testing needs parallel — time to split.

### Example 2: Intermediate — Kaniko Build + Helm Deploy + Review Apps

> **Goal**: Build image without Docker daemon (Kaniko), deploy with Helm, create Review Apps for MR
> **Requires**: GitLab K8s Agent, Helm chart, Kaniko
> **Outcome**: Secure image build + Helm-based deployment + ephemeral review environments

```yaml
# .gitlab-ci.yml — Intermediate Pipeline
stages:
    - test
    - security
    - build
    - deploy
    - verify
    - cleanup

variables:
    DOCKER_IMAGE: ${CI_REGISTRY_IMAGE}
    HELM_CHART_PATH: ./deploy/helm/go-api
    K8S_AGENT: 'my-project:k8s-agent' # ✅ GitLab K8s Agent

# ════════════════════════════════════════════════
# Stage: SECURITY — Parallel scanning
# ════════════════════════════════════════════════

govulncheck:
    stage: security
    image: golang:1.22-alpine
    script:
        - go install golang.org/x/vuln/cmd/govulncheck@latest
        - govulncheck ./...
    allow_failure: true # ⚠️ Do not block pipeline

trivy-scan:
    stage: security
    image:
        name: aquasec/trivy:latest
        entrypoint: ['']
    script:
        # ✅ Scan filesystem cho vulnerabilities
        - trivy fs --exit-code 1 --severity HIGH,CRITICAL --no-progress .
    allow_failure: true

# ════════════════════════════════════════════════
# Stage: BUILD — Kaniko (no Docker daemon needed)
# ════════════════════════════════════════════════

build-kaniko:
    stage: build
    image:
        name: gcr.io/kaniko-project/executor:v1.23.0-debug
        entrypoint: ['']
    script:
        # ✅ Create Docker config for registry auth
        - mkdir -p /kaniko/.docker
        - |
            echo "{\"auths\":{\"${CI_REGISTRY}\":{\"auth\":\"$(echo -n ${CI_REGISTRY_USER}:${CI_REGISTRY_PASSWORD} | base64)\"}}}" \
              > /kaniko/.docker/config.json
        # ✅ Build with Kaniko — unprivileged, no DinD needed
        - |
            /kaniko/executor \
              --context "${CI_PROJECT_DIR}" \
              --dockerfile "${CI_PROJECT_DIR}/Dockerfile" \
              --destination "${DOCKER_IMAGE}:${CI_COMMIT_SHA}" \
              --destination "${DOCKER_IMAGE}:${CI_COMMIT_SHORT_SHA}" \
              --destination "${DOCKER_IMAGE}:${CI_COMMIT_REF_SLUG}" \
              --cache=true \
              --cache-repo="${CI_REGISTRY_IMAGE}/cache" \
              --build-arg "VERSION=${CI_COMMIT_SHA}" \
              --build-arg "BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
              --snapshot-mode=redo \
              --use-new-run
    rules:
        - if: $CI_COMMIT_BRANCH == "main"
        - if: $CI_COMMIT_TAG
        - if: $CI_MERGE_REQUEST_IID

# ════════════════════════════════════════════════
# Stage: DEPLOY — Helm + GitLab K8s Agent
# ════════════════════════════════════════════════

# ✅ Base deploy template
.helm-deploy:
    image:
        name: alpine/helm:3.14
        entrypoint: ['']
    before_script:
        # ✅ Install kubectl
        - apk add --no-cache curl
        - curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        - chmod +x kubectl && mv kubectl /usr/local/bin/
        # ✅ Use GitLab K8s Agent context
        - kubectl config use-context ${K8S_AGENT}

deploy-staging:
    extends: .helm-deploy
    stage: deploy
    script:
        - |
            helm upgrade --install go-api-staging ${HELM_CHART_PATH} \
              --namespace staging \
              --create-namespace \
              --set image.repository=${DOCKER_IMAGE} \
              --set image.tag=${CI_COMMIT_SHA} \
              --set replicaCount=1 \
              --set resources.requests.cpu=100m \
              --set resources.requests.memory=128Mi \
              --set ingress.host=api-staging.example.com \
              --wait \
              --timeout 5m
    environment:
        name: staging
        url: https://api-staging.example.com
        on_stop: stop-staging
    rules:
        - if: $CI_COMMIT_BRANCH == "main"

deploy-production:
    extends: .helm-deploy
    stage: deploy
    script:
        - |
            helm upgrade --install go-api ${HELM_CHART_PATH} \
              --namespace production \
              --create-namespace \
              --set image.repository=${DOCKER_IMAGE} \
              --set image.tag=${CI_COMMIT_SHA} \
              --set replicaCount=3 \
              --set resources.requests.cpu=200m \
              --set resources.requests.memory=256Mi \
              --set ingress.host=api.example.com \
              --set podDisruptionBudget.enabled=true \
              --set podDisruptionBudget.minAvailable=2 \
              --wait \
              --timeout 10m
    environment:
        name: production
        url: https://api.example.com
    rules:
        - if: $CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/ # ✅ Only semver tags
    when: manual # ✅ Manual approval

# ✅ Review App — ephemeral environment for each MR
deploy-review:
    extends: .helm-deploy
    stage: deploy
    script:
        - |
            helm upgrade --install review-${CI_MERGE_REQUEST_IID} ${HELM_CHART_PATH} \
              --namespace review \
              --create-namespace \
              --set image.repository=${DOCKER_IMAGE} \
              --set image.tag=${CI_COMMIT_SHA} \
              --set replicaCount=1 \
              --set ingress.host=review-${CI_MERGE_REQUEST_IID}.example.com \
              --wait \
              --timeout 3m
    environment:
        name: review/${CI_MERGE_REQUEST_IID}
        url: https://review-${CI_MERGE_REQUEST_IID}.example.com
        on_stop: stop-review
        auto_stop_in: 2 days # ✅ Auto cleanup after 2 days
    rules:
        - if: $CI_MERGE_REQUEST_IID

stop-review:
    extends: .helm-deploy
    stage: cleanup
    script:
        - helm uninstall review-${CI_MERGE_REQUEST_IID} --namespace review || true
        - kubectl delete namespace review-${CI_MERGE_REQUEST_IID} --ignore-not-found
    environment:
        name: review/${CI_MERGE_REQUEST_IID}
        action: stop
    rules:
        - if: $CI_MERGE_REQUEST_IID
          when: manual
    allow_failure: true
```

> **✅ Outcome**: Kaniko build (no privileged needed), Helm deploy, Review Apps for each MR.
> **⚠️ Note**: Kaniko does not need a Docker daemon → safer than DinD, suitable for K8s runners.

---

Matrix is covered. But deploy promotion needs environment gating — time to gate.

### Example 3: Advanced — GitOps Pipeline (CI + ArgoCD)

> **Goal**: CI only builds + pushes image → updates K8s config repo → ArgoCD auto-syncs
> **Requires**: 2 repos (app + k8s config), ArgoCD installed
> **Outcome**: Full GitOps: CI does not need cluster access, ArgoCD handles deployment

```yaml
# .gitlab-ci.yml — GitOps Pipeline (App Repo)
# ✅ CI only builds image + updates config repo
# ✅ ArgoCD watches config repo → auto deploys

stages:
    - test
    - build
    - gitops-update

variables:
    DOCKER_IMAGE: ${CI_REGISTRY_IMAGE}
    CONFIG_REPO: 'https://deploy-token:${DEPLOY_TOKEN}@gitlab.com/myteam/k8s-config.git'
    CONFIG_REPO_BRANCH: 'main'

# ════════════════════════════════════════════════
# Stage: TEST
# ════════════════════════════════════════════════

test:
    stage: test
    image: golang:1.22-alpine
    script:
        - go test -race -coverprofile=coverage.out ./...
        - go tool cover -func=coverage.out
    coverage: '/total:\s+\(statements\)\s+(\d+\.\d+)%/'

# ════════════════════════════════════════════════
# Stage: BUILD
# ════════════════════════════════════════════════

build:
    stage: build
    image:
        name: gcr.io/kaniko-project/executor:v1.23.0-debug
        entrypoint: ['']
    script:
        - mkdir -p /kaniko/.docker
        - |
            echo "{\"auths\":{\"${CI_REGISTRY}\":{\"auth\":\"$(echo -n ${CI_REGISTRY_USER}:${CI_REGISTRY_PASSWORD} | base64)\"}}}" \
              > /kaniko/.docker/config.json
        - |
            /kaniko/executor \
              --context "${CI_PROJECT_DIR}" \
              --destination "${DOCKER_IMAGE}:${CI_COMMIT_SHA}" \
              --destination "${DOCKER_IMAGE}:latest" \
              --cache=true \
              --cache-repo="${CI_REGISTRY_IMAGE}/cache"
    rules:
        - if: $CI_COMMIT_BRANCH == "main"
        - if: $CI_COMMIT_TAG

# ════════════════════════════════════════════════
# Stage: GITOPS-UPDATE
# ✅ Update K8s config repo → triggers ArgoCD sync
# ════════════════════════════════════════════════

update-staging-config:
    stage: gitops-update
    image: alpine:3.19
    before_script:
        - apk add --no-cache git curl
        # ✅ Install kustomize
        - curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
        - mv kustomize /usr/local/bin/
    script:
        # ✅ Clone K8s config repo
        - git clone --branch ${CONFIG_REPO_BRANCH} ${CONFIG_REPO} config-repo
        - cd config-repo

        # ✅ Update image tag in staging overlay
        - cd overlays/staging
        - kustomize edit set image go-api=${DOCKER_IMAGE}:${CI_COMMIT_SHA}

        # ✅ Commit + push → ArgoCD auto-syncs
        - git config user.email "ci@gitlab.com"
        - git config user.name "GitLab CI"
        - git add .
        - |
            git commit -m "deploy(staging): go-api ${CI_COMMIT_SHORT_SHA}

            Source: ${CI_PROJECT_URL}/-/commit/${CI_COMMIT_SHA}
            Pipeline: ${CI_PIPELINE_URL}
            Author: ${GITLAB_USER_NAME}"
        - git push origin ${CONFIG_REPO_BRANCH}
    rules:
        - if: $CI_COMMIT_BRANCH == "main"

update-production-config:
    stage: gitops-update
    image: alpine:3.19
    before_script:
        - apk add --no-cache git curl
        - curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
        - mv kustomize /usr/local/bin/
    script:
        - git clone --branch ${CONFIG_REPO_BRANCH} ${CONFIG_REPO} config-repo
        - cd config-repo

        # ✅ Update image tag in production overlay
        - cd overlays/production
        - kustomize edit set image go-api=${DOCKER_IMAGE}:${CI_COMMIT_SHA}

        - git config user.email "ci@gitlab.com"
        - git config user.name "GitLab CI"
        - git add .
        - |
            git commit -m "deploy(production): go-api ${CI_COMMIT_SHORT_SHA}

            Tag: ${CI_COMMIT_TAG}
            Source: ${CI_PROJECT_URL}/-/commit/${CI_COMMIT_SHA}
            Pipeline: ${CI_PIPELINE_URL}"
        - git push origin ${CONFIG_REPO_BRANCH}
    rules:
        - if: $CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/ # ✅ Only semver tags
    when: manual # ✅ Manual approve
```

> **✅ Outcome**: GitOps pipeline — CI only builds image + updates Git config repo. ArgoCD in the cluster auto-syncs.
> **⚠️ Note**: CI does NOT need kubectl/kubeconfig. Separation of concerns: CI = build, ArgoCD = deploy.

---

### Example 4: Expert — Multi-Project Pipeline + Dynamic Environments

> **Goal**: Pipeline chain between multiple projects + dynamic child pipelines
> **Requires**: GitLab Premium (or trigger tokens), multiple repos
> **Outcome**: Orchestrated deployment across microservices

```yaml
# .gitlab-ci.yml — Expert: Multi-project + Dynamic Pipeline
stages:
    - test
    - build
    - generate
    - deploy

# ════════════════════════════════════════════════
# Dynamic Child Pipeline
# ✅ Generate .gitlab-ci.yml dynamically based on changes
# ════════════════════════════════════════════════

detect-changes:
    stage: generate
    image: alpine:3.19
    script:
        # ✅ Detect changed services
        - |
            CHANGED_SERVICES=""
            for svc in services/*/; do
              svc_name=$(basename $svc)
              # Check if files in this service changed
              if git diff --name-only HEAD~1 | grep -q "^services/${svc_name}/"; then
                CHANGED_SERVICES="${CHANGED_SERVICES} ${svc_name}"
              fi
            done
            echo "Changed services: ${CHANGED_SERVICES}"

        # ✅ Generate child pipeline YAML
        - |
            cat > child-pipeline.yml << 'HEREDOC'
            stages:
              - build
              - deploy
            HEREDOC

            for svc in ${CHANGED_SERVICES}; do
              cat >> child-pipeline.yml << HEREDOC

            build-${svc}:
              stage: build
              image:
                name: gcr.io/kaniko-project/executor:v1.23.0-debug
                entrypoint: [""]
              script:
                - mkdir -p /kaniko/.docker
                - echo "{\"auths\":{\"${CI_REGISTRY}\":{\"auth\":\"$(echo -n ${CI_REGISTRY_USER}:${CI_REGISTRY_PASSWORD} | base64)\"}}}" > /kaniko/.docker/config.json
                - /kaniko/executor --context services/${svc} --destination ${CI_REGISTRY_IMAGE}/${svc}:${CI_COMMIT_SHA} --cache=true

            deploy-${svc}:
              stage: deploy
              needs: ["build-${svc}"]
              image: alpine/helm:3.14
              script:
                - helm upgrade --install ${svc} ./deploy/helm/${svc} --set image.tag=${CI_COMMIT_SHA} --namespace staging --wait
            HEREDOC
            done
    artifacts:
        paths:
            - child-pipeline.yml

# ✅ Trigger child pipeline
deploy-changed-services:
    stage: deploy
    trigger:
        include:
            - artifact: child-pipeline.yml
              job: detect-changes
        strategy: depend

# ════════════════════════════════════════════════
# Multi-Project Pipeline Trigger
# ✅ Trigger downstream project when upstream changes
# ════════════════════════════════════════════════

trigger-k8s-config:
    stage: deploy
    trigger:
        project: myteam/k8s-config # ✅ Downstream project
        branch: main
        strategy: depend # ✅ Wait for downstream pipeline to complete
    variables:
        UPSTREAM_IMAGE: ${DOCKER_IMAGE}:${CI_COMMIT_SHA}
        UPSTREAM_COMMIT: ${CI_COMMIT_SHA}
        UPSTREAM_PROJECT: ${CI_PROJECT_NAME}
    rules:
        - if: $CI_COMMIT_BRANCH == "main"
```

```yaml
# Dockerfile — Multi-stage build cho Go
# ✅ Production-ready Dockerfile

# Stage 1: Build
FROM golang:1.22-alpine AS builder

# ✅ Build args for metadata
ARG VERSION=unknown
ARG BUILD_DATE=unknown
ARG GIT_COMMIT=unknown

WORKDIR /app

# ✅ Cache dependencies
COPY go.mod go.sum ./
RUN go mod download && go mod verify

# ✅ Copy source and build
COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build -ldflags="-w -s \
      -X main.version=${VERSION} \
      -X main.buildDate=${BUILD_DATE} \
      -X main.gitCommit=${GIT_COMMIT}" \
    -o /app/server ./cmd/server

# Stage 2: Runtime
FROM gcr.io/distroless/static-debian12:nonroot

# ✅ Copy binary
COPY --from=builder /app/server /server

# ✅ Run as non-root
USER nonroot:nonroot

EXPOSE 8080
ENTRYPOINT ["/server"]
```

> **✅ Outcome**: Dynamic pipelines only build/deploy changed services + multi-project orchestration.
> **⚠️ Note**: Dynamic child pipelines are powerful but require thorough testing of generated YAML.

---

You have walked through pipeline, matrix, and promotion. Now comes the dangerous part: runner resource overflow and cache miss — the trap set up from the beginning.

## 4. PITFALLS

Production rarely breaks because you do not know the name of a concept; it breaks because of wrong assumptions and defaults trusted too much. The pitfalls below are the most expensive slips.


| #   | Mistake                                     | Consequence                          | Fix                                        |
| --- | ------------------------------------------- | ------------------------------------ | ------------------------------------------ |
| 1   | Using `latest` tag for deploy               | Deploy version is indeterminate      | Always use `$CI_COMMIT_SHA` or semver      |
| 2   | Docker-in-Docker (DinD) runs slow           | Pipeline slow 30-60s startup         | Use Kaniko — no Docker daemon needed       |
| 3   | Cache key too generic                       | Frequent cache misses                | Use `files: [go.sum]` instead of branch name |
| 4   | K8s credentials hard-coded in variables     | Security risk                        | Use GitLab K8s Agent or GitOps             |
| 5   | No `--wait` when running helm install       | Pipeline passes but deploy fails     | Always use `--wait --timeout`              |
| 6   | Review Apps not cleaned up                  | Resource leak on cluster             | Use `auto_stop_in` + `on_stop` job         |
| 7   | Tests run sequentially                      | Pipeline is slow                     | `go test -parallel` + split test suites    |

---

You have walked through GitLab CI and its traps. The resources below help go deeper.

## 5. REF

| Resource                  | Link                                                                                                                |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| GitLab CI/CD Docs         | [docs.gitlab.com/ee/ci](https://docs.gitlab.com/ee/ci/)                                                             |
| GitLab K8s Agent          | [docs.gitlab.com/ee/user/clusters/agent](https://docs.gitlab.com/ee/user/clusters/agent/)                           |
| GitLab Container Registry | [docs.gitlab.com/ee/user/packages/container_registry](https://docs.gitlab.com/ee/user/packages/container_registry/) |
| Kaniko                    | [github.com/GoogleContainerTools/kaniko](https://github.com/GoogleContainerTools/kaniko)                            |
| GitLab CI Variables       | [docs.gitlab.com/ee/ci/variables](https://docs.gitlab.com/ee/ci/variables/)                                         |
| GitLab Review Apps        | [docs.gitlab.com/ee/ci/review_apps](https://docs.gitlab.com/ee/ci/review_apps/)                                     |
| GitLab Auto DevOps        | [docs.gitlab.com/ee/topics/autodevops](https://docs.gitlab.com/ee/topics/autodevops/)                               |
| Trivy Scanner             | [aquasecurity.github.io/trivy](https://aquasecurity.github.io/trivy/)                                               |

---

## 6. RECOMMEND

The suggested articles below connect directly to the pressures that commonly appear right after you apply these concepts to a real system.


| Extension                        | When                             | Reason                                |
| -------------------------------- | -------------------------------- | ------------------------------------- |
| **GitLab Auto DevOps**           | Quick start for new projects     | Zero-config CI/CD pipeline            |
| **GitLab SAST/DAST**             | Enterprise security requirements | Built-in security scanning            |
| **Merge Train**                  | High-velocity teams              | Auto-rebase + test before merge       |
| **GitLab Releases + Changelog**  | Version management               | Automated release notes from commits  |
| **GitLab Package Registry**      | Go module hosting                | Private Go modules proxy              |
| **Parent-Child Pipelines**       | Monorepo architecture            | Dynamic pipelines per changed service |
| **GitLab Terraform Integration** | Infrastructure provisioning      | Terraform state management in GitLab  |

---

## 🔍 Debug Checklist

| # | Symptom | Cause | Debug Command |
|---|---------|-------|---------------|
| 1 | Build stage fails with "Docker daemon not available" | Using Docker-in-Docker but executor not configured correctly | Switch to Kaniko: `image: gcr.io/kaniko-project/executor:latest` — no Docker daemon needed |
| 2 | Helm deploy fails: "Error: INSTALLATION FAILED: Kubernetes cluster unreachable" | `KUBECONFIG` not configured or K8s Agent not connected | Check `kubectl config view` in job + confirm GitLab K8s Agent is registered |
| 3 | Review App environment not cleaned up after merge | `on_stop` job not triggered or `GIT_STRATEGY: none` missing | Check `environment: on_stop:` config + `when: manual` on stop job |
| 4 | Child pipeline not triggered: "trigger job skipped" | `include: rules:` condition not matching `CI_COMMIT_BRANCH` | Print variables: `echo $CI_COMMIT_BRANCH` before job + check `rules: if:` expression |
| 5 | Image push fails: "unauthorized: authentication required" | `CI_REGISTRY_USER` / `CI_REGISTRY_PASSWORD` incorrect or token expired | `docker login $CI_REGISTRY -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD` manually to test |
| 6 | Cache miss on every pipeline run — dependencies always re-downloaded | Cache key too generic or `policy: pull` after policy change | Use `cache: key: files: [go.sum]` so cache invalidates when dependencies change |
| 7 | SAST/DAST scan reports false positives continuously | Default rules too broad or test code being scanned | Add `SAST_EXCLUDED_PATHS: "spec, test, tests, tmp"` to job variables |

---

## 🃏 Quick Reference

| # | Pattern | Command / Rule |
|---|---------|----------------|
| 1 | Kaniko build (no Docker daemon needed) | `image: gcr.io/kaniko-project/executor:debug` + `executor --context $CI_PROJECT_DIR --destination $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA` |
| 2 | Helm deploy in CI job | `helm upgrade --install <release> ./chart -f values.yaml --set image.tag=$CI_COMMIT_SHA --wait --timeout=5m` |
| 3 | Dynamic child pipeline | `trigger: include: [{artifact: child-pipeline.yml, job: generate-pipeline}]` |
| 4 | Review App with dynamic URL | `environment: name: review/$CI_COMMIT_REF_SLUG` + `url: https://$CI_ENVIRONMENT_SLUG.example.com` |
| 5 | Cache Go modules efficiently | `cache: key: {files: [go.sum]} paths: [.go-cache/]` + `GOPATH: $CI_PROJECT_DIR/.go-cache` |
| 6 | Protected variable injection | Declare variable in GitLab UI with "Protected" + "Masked" — only available on protected branches |
| 7 | Parallel matrix build | `parallel: matrix: [{PLATFORM: [linux/amd64, linux/arm64], GOVERSION: [1.22, 1.23]}]` |
| 8 | GitOps update config repo from CI | `git clone config-repo && sed -i "s/image:.*/image: $NEW_IMAGE/" deployment.yaml && git push` → ArgoCD auto-syncs |

---

## 🎯 Interview Angle

**Relevant system design / technical questions:**
- *"Why should you separate CI (build/test) and CD (deploy) into 2 separate pipelines? How can you combine GitLab CI with ArgoCD?"*
- *"How does Kaniko differ from Docker-in-Docker in terms of security? When should you use Kaniko in a K8s environment?"*
- *"Design a CI/CD pipeline for a monorepo with 15 microservices — how do you only build/deploy services that changed?"*

**Points the interviewer wants to hear:**

| Topic | Talking Point |
|-------|---------------|
| CI vs CD separation | CI writes image tag to config repo (Git push); ArgoCD reads config repo and syncs to K8s — clear separation of responsibilities, clear audit trail |
| Kaniko vs DinD | Kaniko runs unprivileged (no `--privileged`), builds inside container without Docker daemon — safer than DinD for security |
| GitOps integration | Pipeline does not use `kubectl` directly; instead updates image tag in Git, ArgoCD pulls and applies — Git is the single source of truth |
| Review Apps | Each MR creates its own ephemeral environment with dynamic URL; auto-cleanup via `on_stop` job when MR closes |
| Monorepo dynamic pipelines | Use `rules: changes:` combined with `generate-pipeline` job to create child pipeline YAML only for services with changed files |
| Pipeline caching | Cache key based on `go.sum` checksum — invalidates precisely when dependencies change; use `policy: pull` on parallel jobs to avoid overwriting |

**Common follow-up questions:**
- *"How do you handle database migrations in a CD pipeline?"* → Run migration job before deploy job with `needs:` dependency; use `--atomic` with Helm to rollback if migration fails.
- *"How do you secure secrets in GitLab CI?"* → Protected + Masked variables in GitLab UI; or HashiCorp Vault with `vault kv get` in job; absolutely never hardcode in `.gitlab-ci.yml`.
- *"Pipeline fails after merge — how do you debug quickly?"* → Use `CI_DEBUG_TRACE: "true"` for verbose logging; or `gitlab-ci-local` to run pipeline locally before pushing.

---

**Links**: [← ArgoCD](./01-argocd.md) · [→ CI/CD Pipeline Overview](../fundamental/09-cicd-pipeline.md)
