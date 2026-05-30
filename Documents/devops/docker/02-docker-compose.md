<!-- tags: docker, containerization, docker-compose -->
# 🐙 Docker Compose

> Multi-container orchestration for development — Go API + PostgreSQL + Redis in one command.

📅 Created: 2026-03-20 · 🔄 Updated: 2026-04-20 · ⏱️ 16 min read

| Aspect           | Detail                                     |
| ---------------- | ------------------------------------------ |
| **Tool**         | Docker Compose v2 (built-in plugin)        |
| **Use case**     | Local development, testing, staging        |
| **Go relevance** | Go API + database + cache + worker         |
| **CLI**          | `docker compose up`, `docker compose down` |

---

## 1. DEFINE

You want to stand up an app, database, cache, and queue on your local machine or staging, but forgetting a single dependency means the environment runs differently from production. Docker Compose becomes useful exactly when you need to orchestrate multiple containers while keeping everything easy to reproduce.

### Compose File Structure

| Section    | Description           | Required |
| ---------- | --------------------- | -------- |
| `services` | Container definitions | ✅       |
| `volumes`  | Named volumes         | ❌       |
| `networks` | Custom networks       | ❌       |
| `secrets`  | Docker secrets        | ❌       |
| `configs`  | Config files mount    | ❌       |

### Service Configuration

| Field              | Role                  | Example                            |
| ------------------ | --------------------- | ---------------------------------- |
| `image`            | Pre-built image       | `postgres:16-alpine`               |
| `build`            | Build from Dockerfile | `build: .`                         |
| `ports`            | Port mapping          | `"8080:8080"`                      |
| `environment`      | Env vars              | `DB_HOST=postgres`                 |
| `env_file`         | Load env from file    | `.env`                             |
| `volumes`          | Mount volumes         | `./data:/var/lib/data`             |
| `depends_on`       | Start order           | `depends_on: [postgres]`           |
| `healthcheck`      | Health check          | `curl -f http://localhost/healthz` |
| `restart`          | Restart policy        | `unless-stopped`                   |
| `profiles`         | Optional services     | `profiles: [debug]`                |
| `deploy.resources` | Resource limits       | Memory, CPU                        |

### depends_on Conditions

| Condition                        | Description                 |
| -------------------------------- | --------------------------- |
| `service_started`                | Container started (default) |
| `service_healthy`                | Healthcheck passed ✅       |
| `service_completed_successfully` | Container exited 0          |

### Failure Modes

| Error                        | Cause                                | Fix                               |
| ---------------------------- | ------------------------------------ | --------------------------------- |
| Service cannot connect to DB | DB not ready, only `service_started` | Use `service_healthy`             |
| Port conflict                | Port already bound on host           | Change port mapping               |
| Volume permission denied     | UID mismatch                         | Set `user:` or chown              |
| Build cache stale            | Code changed but old image used      | `docker compose build --no-cache` |

---

Those failure modes are clear. But there is a trap: depends_on without waiting for service readiness causes startup race conditions, and wrong volume mount paths cause data loss. That trap appears in PITFALLS.

## 2. VISUAL

The concept has a name. In the diagram, the more important part emerges: how requests, workloads, and signals flow through these layers.

![Docker Compose — web, api, db, cache, worker services on Docker network with depends_on and healthchecks](./images/docker-compose-topology.png)

### Compose Architecture

```mermaid
flowchart TD
  subgraph Network["Docker Compose Network (bridge: app-network)"]
    API["go-api :8080<br/>build: ."] -->|query| PG["postgres :5432<br/>image: pg:16"]
    API -->|cache| Redis["redis :6379<br/>image: redis:7"]
    Worker["worker<br/>no ports"] -->|consume| PG
    Worker -->|consume| Redis
    Migrate["migrate<br/>one-shot, exit:0"] -->|schema| PG
  end
  Browser["Browser / curl"] -->|host:8080| API
```

*Figure: Compose wires the API, database, cache, worker, and migration into one network. The browser hits port 8080 on the host, which routes to the API container.*

---

## 3. CODE

Code and config show how the decisions discussed above are enforced by real constraints, not just a nice diagram.

### Example 1: Basic — Go API + PostgreSQL

> **Goal**: Basic Docker Compose for Go app + database.
> **Requires**: Go project + Dockerfile.
> **Result**: One-command development environment.

```yaml
# docker-compose.yaml
services:
    # ✅ Go API — build from source
    api:
        build:
            context: .
            dockerfile: Dockerfile
        ports:
            - '8080:8080'
        environment:
            - DATABASE_URL=postgres://appuser:secret@postgres:5432/myapp?sslmode=disable
            - REDIS_URL=redis://redis:6379
            - GIN_MODE=debug
        depends_on:
            postgres:
                condition: service_healthy # ✅ Wait for DB to be healthy
            redis:
                condition: service_healthy
        volumes:
            - .:/app # ✅ Bind mount for hot-reload (dev only)
        restart: unless-stopped

    # ✅ PostgreSQL
    postgres:
        image: postgres:16-alpine
        environment:
            POSTGRES_USER: appuser
            POSTGRES_PASSWORD: secret
            POSTGRES_DB: myapp
        ports:
            - '5432:5432' # ✅ Expose for local tools (DBeaver, pgAdmin)
        volumes:
            - pgdata:/var/lib/postgresql/data
            - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql # ✅ Init script
        healthcheck:
            test: ['CMD-SHELL', 'pg_isready -U appuser -d myapp']
            interval: 5s
            timeout: 5s
            retries: 5

    # ✅ Redis
    redis:
        image: redis:7-alpine
        ports:
            - '6379:6379'
        volumes:
            - redisdata:/data
        healthcheck:
            test: ['CMD', 'redis-cli', 'ping']
            interval: 5s
            timeout: 3s
            retries: 5
        command: redis-server --appendonly yes # ✅ Persistent

volumes:
    pgdata: # ✅ Named volume — persist across restarts
    redisdata:
```

```bash
# ✅ Start all services
docker compose up -d

# ✅ Check status
docker compose ps
# NAME       STATUS          PORTS
# api        Up (healthy)    0.0.0.0:8080->8080/tcp
# postgres   Up (healthy)    0.0.0.0:5432->5432/tcp
# redis      Up (healthy)    0.0.0.0:6379->6379/tcp

# ✅ View logs
docker compose logs -f api

# ✅ Stop & remove
docker compose down           # Stop containers
docker compose down -v        # Stop + remove volumes (⚠️ deletes data)
```

**Result**: Full dev environment, one-command start, persistent data.
**Note**: `depends_on: service_healthy` ensures DB readiness. Do not use `service_started`!

---

Basic compose is covered. But healthcheck needs readiness — time to wait properly.

### Example 2: Intermediate — Multi-service + Profile + Hot-Reload

> **Goal**: Go API + Worker + Migration + optional debug tools.
> **Requires**: Multiple Go services, Air for hot-reload.
> **Result**: Full development workflow.

```yaml
# docker-compose.yaml
services:
    api:
        build:
            context: .
            dockerfile: Dockerfile
            target: builder # ✅ Use builder stage for dev (has Go tools)
        ports:
            - '8080:8080'
        environment:
            DATABASE_URL: postgres://appuser:secret@postgres:5432/myapp?sslmode=disable
            REDIS_URL: redis://redis:6379
            ENV: development
        depends_on:
            postgres: { condition: service_healthy }
            redis: { condition: service_healthy }
            migrate: { condition: service_completed_successfully } # ✅ Wait for migration
        volumes:
            - .:/app
        # ✅ Hot-reload with Air
        command: ['air', '-c', '.air.toml']
        restart: unless-stopped

    # ✅ Background worker
    worker:
        build:
            context: .
            target: builder
        environment:
            DATABASE_URL: postgres://appuser:secret@postgres:5432/myapp?sslmode=disable
            REDIS_URL: redis://redis:6379
        depends_on:
            postgres: { condition: service_healthy }
            redis: { condition: service_healthy }
        volumes:
            - .:/app
        command: ['go', 'run', './cmd/worker']
        restart: unless-stopped

    # ✅ One-shot migration
    migrate:
        build:
            context: .
            target: builder
        environment:
            DATABASE_URL: postgres://appuser:secret@postgres:5432/myapp?sslmode=disable
        depends_on:
            postgres: { condition: service_healthy }
        volumes:
            - ./migrations:/app/migrations
        command: ['go', 'run', './cmd/migrate', 'up']
        restart: 'no' # ✅ Run once, don't restart

    postgres:
        image: postgres:16-alpine
        environment:
            POSTGRES_USER: appuser
            POSTGRES_PASSWORD: secret
            POSTGRES_DB: myapp
        ports: ['5432:5432']
        volumes:
            - pgdata:/var/lib/postgresql/data
        healthcheck:
            test: ['CMD-SHELL', 'pg_isready -U appuser -d myapp']
            interval: 5s
            timeout: 5s
            retries: 5

    redis:
        image: redis:7-alpine
        ports: ['6379:6379']
        volumes: [redisdata:/data]
        healthcheck:
            test: ['CMD', 'redis-cli', 'ping']
            interval: 5s
            timeout: 3s
            retries: 5

    # ═══════════════════════════════════════════
    # Optional services (profiles)
    # ═══════════════════════════════════════════

    # ✅ pgAdmin — only when needed
    pgadmin:
        image: dpage/pgadmin4:latest
        profiles: ['debug'] # ✅ Only starts with: docker compose --profile debug up
        environment:
            PGADMIN_DEFAULT_EMAIL: admin@example.com
            PGADMIN_DEFAULT_PASSWORD: admin
        ports: ['5050:80']
        depends_on:
            postgres: { condition: service_healthy }

    # ✅ Redis Commander
    redis-commander:
        image: rediscommander/redis-commander:latest
        profiles: ['debug']
        environment:
            REDIS_HOSTS: local:redis:6379
        ports: ['8081:8081']
        depends_on:
            redis: { condition: service_healthy }

    # ✅ Mailhog — fake SMTP server
    mailhog:
        image: mailhog/mailhog:latest
        profiles: ['debug']
        ports:
            - '1025:1025' # SMTP
            - '8025:8025' # Web UI

volumes:
    pgdata:
    redisdata:
```

```bash
# ✅ Start core services
docker compose up -d

# ✅ Start with debug tools
docker compose --profile debug up -d

# ✅ Rebuild single service
docker compose up -d --build api

# ✅ Scale worker
docker compose up -d --scale worker=3

# ✅ Run migration manually
docker compose run --rm migrate
```

**Result**: Hot-reload, migration-first, optional debug tools via profiles.
**Note**: `profiles: ["debug"]` means the service does not start by default.

---

Healthcheck is covered. But multi-profile needs environment separation — time to split.

### Example 3: Advanced — Production-like Compose + .env Management

> **Goal**: Compose file for staging/CI — resource limits, health checks, logging.
> **Requires**: Production-like environment.
> **Result**: Portable deployment for non-K8s environments.

```yaml
# docker-compose.prod.yaml
services:
    api:
        image: ghcr.io/myorg/go-api:${APP_VERSION:-latest}
        ports:
            - '${API_PORT:-8080}:8080'
        env_file:
            - .env
            - .env.production
        depends_on:
            postgres: { condition: service_healthy }
            redis: { condition: service_healthy }
        deploy:
            resources:
                limits:
                    memory: 512M
                    cpus: '1.0'
                reservations:
                    memory: 128M
                    cpus: '0.25'
            replicas: 2 # ✅ Multiple replicas (Compose v2)
        restart: unless-stopped
        healthcheck:
            test: ['CMD', '/server', 'healthcheck']
            interval: 30s
            timeout: 10s
            start_period: 15s
            retries: 3
        logging:
            driver: json-file
            options:
                max-size: '10m'
                max-file: '5'

    postgres:
        image: postgres:16-alpine
        env_file: .env.production
        volumes:
            - pgdata:/var/lib/postgresql/data
            - ./backups:/backups
        deploy:
            resources:
                limits: { memory: 1G, cpus: '2.0' }
                reservations: { memory: 256M }
        healthcheck:
            test: ['CMD-SHELL', 'pg_isready -U ${POSTGRES_USER}']
            interval: 10s
            timeout: 5s
            retries: 10
        restart: always

    redis:
        image: redis:7-alpine
        command: >
            redis-server
            --appendonly yes
            --maxmemory 256mb
            --maxmemory-policy allkeys-lru
            --requirepass ${REDIS_PASSWORD}
        volumes: [redisdata:/data]
        deploy:
            resources:
                limits: { memory: 512M }
        healthcheck:
            test: ['CMD', 'redis-cli', '-a', '${REDIS_PASSWORD}', 'ping']
            interval: 10s
            timeout: 3s
            retries: 5
        restart: always

    # ✅ Nginx reverse proxy
    nginx:
        image: nginx:alpine
        ports:
            - '80:80'
            - '443:443'
        volumes:
            - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
            - ./nginx/certs:/etc/nginx/certs:ro
        depends_on:
            api: { condition: service_healthy }
        restart: always

    # ✅ Periodic backup job
    backup:
        image: postgres:16-alpine
        profiles: ['maintenance']
        environment:
            PGPASSWORD: ${POSTGRES_PASSWORD}
        volumes:
            - ./backups:/backups
        entrypoint: >
            sh -c 'pg_dump -h postgres -U ${POSTGRES_USER} ${POSTGRES_DB}
            | gzip > /backups/backup_$$(date +%Y%m%d_%H%M%S).sql.gz
            && echo "Backup completed"'

volumes:
    pgdata:
        driver: local
    redisdata:
        driver: local
```

```bash
# ✅ Start production stack
docker compose -f docker-compose.prod.yaml --env-file .env.production up -d

# ✅ Scale API
docker compose -f docker-compose.prod.yaml up -d --scale api=3

# ✅ Run backup
docker compose -f docker-compose.prod.yaml --profile maintenance run --rm backup

# ✅ Rolling update (zero downtime)
docker compose -f docker-compose.prod.yaml pull api
docker compose -f docker-compose.prod.yaml up -d --no-deps api
```

**Result**: Resource limits, logging, health checks, backup, rolling updates.
**Note**: Compose production ≠ K8s. Use for simple deployments, staging, CI.

---

You have covered compose, healthcheck, and profiles. Now comes the dangerous part: depends_on races and volume paths — the trap set up from the beginning.

## 4. PITFALLS

Production rarely breaks because you do not know a concept's name. It breaks because of wrong assumptions and blindly trusted defaults. The pitfalls below are the most expensive slips.

| #   | Mistake                                | Consequence                                   | Fix                                                |
| --- | -------------------------------------- | --------------------------------------------- | -------------------------------------------------- |
| 1   | DB not ready → app crash               | App fails to start, connection refused         | `depends_on: { condition: service_healthy }`       |
| 2   | Data lost with `docker compose down -v`| All DB data gone, no recovery                  | Backup first, be careful with the `-v` flag        |
| 3   | ENV variable not loaded                | Service starts with wrong config, runtime error| Check `.env` file location, `env_file` path        |
| 4   | Port conflict                          | Service fails to start, bind error             | `${API_PORT:-8080}:8080` — configurable port       |
| 5   | Build cache stale                      | Running old code, bugs not fixed               | `docker compose build --no-cache service`          |
| 6   | Compose v1 syntax                      | Commands not recognized, new features missing  | Use `docker compose` (v2), not `docker-compose`    |

---

You have covered Docker Compose and the traps. The resources below help go deeper.

## 5. REF

| Resource              | Link                                                                                                           |
| --------------------- | -------------------------------------------------------------------------------------------------------------- |
| Compose Specification | [docs.docker.com/compose/compose-file](https://docs.docker.com/compose/compose-file/)                          |
| Compose Profiles      | [docs.docker.com/compose/profiles](https://docs.docker.com/compose/profiles/)                                  |
| Air (Hot-reload)      | [github.com/air-verse/air](https://github.com/air-verse/air)                                                   |
| Docker Healthcheck    | [docs.docker.com/reference/dockerfile/#healthcheck](https://docs.docker.com/reference/dockerfile/#healthcheck) |

---

## 6. RECOMMEND

After this article, read the topic closest to your current decision so the production mental model does not fragment.

| Next step                | When                     | Reason                            |
| ------------------------ | ------------------------ | --------------------------------- |
| **Docker Compose Watch** | File sync dev            | Auto-rebuild on change            |
| **Testcontainers**       | Go integration test      | Programmatic container management |
| **Tilt**                 | K8s development          | Smart rebuilds for K8s            |
| **Podman Compose**       | Rootless alternative     | Docker-compatible, daemonless     |
| **devcontainers**        | VS Code dev environments | Reproducible dev setup            |

---

**Links**: [← Dockerfile](./01-dockerfile-multistage.md) · [→ Networking](./03-networking.md)
