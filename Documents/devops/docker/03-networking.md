<!-- tags: docker, containerization, networking -->
# 🌐 Docker Networking

> Container networking — bridge, host, overlay, DNS resolution between services.

📅 Created: 2026-03-20 · 🔄 Updated: 2026-04-20 · ⏱️ 12 min read

| Aspect           | Detail                                   |
| ---------------- | ---------------------------------------- |
| **Concept**      | Bridge, host, overlay, macvlan networks  |
| **Use case**     | Service discovery, isolation, multi-host |
| **Go relevance** | Go services connect via container DNS    |
| **CLI**          | `docker network`, service DNS names      |

---

## 1. DEFINE

Picture bugs that do not live in your application code but in the fact that containers cannot see each other, port mapping is wrong, or internal DNS goes off-path. Networking in Docker is simple until you have to debug a request that never reaches its destination.

### Network Drivers

| Driver      | Scope       | Description                       | Use case            |
| ----------- | ----------- | --------------------------------- | ------------------- |
| **bridge**  | Single host | Default, isolated network         | Dev, single-server  |
| **host**    | Single host | Share host network stack          | Max performance     |
| **overlay** | Multi-host  | Docker Swarm cross-node           | Production clusters |
| **macvlan** | Single host | Direct attach to physical network | Legacy apps need L2 |
| **none**    | N/A         | No networking                     | Batch processing    |

### DNS Resolution

| Scenario        | Hostname         | Example              |
| --------------- | ---------------- | -------------------- |
| Compose service | Service name     | `postgres:5432`      |
| Custom network  | Container name   | `my-container:8080`  |
| Default bridge  | IP only (no DNS) | `172.17.0.2:8080`    |
| Host network    | `localhost`      | `localhost:5432`     |

### Port Mapping

| Format                     | Description             | Example        |
| -------------------------- | ----------------------- | -------------- |
| `host:container`           | Map specific port       | `8080:8080`    |
| `container`                | Random host port        | `8080`         |
| `host:container/protocol`  | Specify protocol        | `53:53/udp`    |
| `127.0.0.1:host:container` | Bind specific interface | Localhost only |

### Failure Modes

| Error                               | Cause                   | Fix                                |
| ----------------------------------- | ----------------------- | ---------------------------------- |
| Container cannot resolve hostname   | Default bridge (no DNS) | Use custom bridge network          |
| Port already in use                 | Host port conflict      | Change port mapping                |
| Cross-container connection refused  | Different networks      | Connect containers to same network |
| Slow DNS resolution                 | Docker DNS cache        | Restart Docker daemon              |

---

Those failure modes sound easy to avoid. But there is a trap: containers on the default bridge get no DNS resolution, and published port conflicts cause bind failures. That trap appears in PITFALLS.

## 2. VISUAL

The definition locked the vocabulary. The visual below shows how network isolation and DNS resolution actually work when containers, networks, and port mappings interact.

![Docker Network Types — Bridge, Host, Overlay, None with DNS resolution and port mapping](./images/docker-network-types.png)

### Network Architecture

```mermaid
flowchart TD
  subgraph Host["HOST MACHINE"]
    subgraph Default["docker0 (default bridge)"]
      CA["Container A — ❌ No DNS"]
    end
    subgraph App["app-network (custom bridge)"]
      API["go-api ✅ DNS"] -->|query| PG["postgres ✅ DNS"]
      API -->|cache| RD["redis ✅ DNS"]
    end
    subgraph Front["frontend-network"]
      NGX["nginx"] -->|proxy| API2["go-api (both networks)"]
    end
  end
  Browser["Browser"] -->|host:80| NGX
```

*Figure: Custom bridge provides DNS resolution between containers. Default bridge does not. Multi-network setup isolates frontend from database.*

---

## 3. CODE

The diagram showed the main path. The code, manifests, and commands below pull it down to the artifact level that on-call or reviewers actually use.

### Example 1: Basic — Custom Bridge Network

> **Goal**: Create a custom network for DNS resolution between containers.
> **Requires**: Docker.
> **Result**: Containers communicate by name.

```bash
# ✅ Create custom bridge network
docker network create app-network

# ✅ Run PostgreSQL on custom network
docker run -d \
  --name postgres \
  --network app-network \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=myapp \
  postgres:16-alpine

# ✅ Run Go API on same network
docker run -d \
  --name go-api \
  --network app-network \
  -p 8080:8080 \
  -e DATABASE_URL="postgres://appuser:secret@postgres:5432/myapp?sslmode=disable" \
  go-api:latest

# ✅ DNS works — "postgres" resolves to PostgreSQL container IP
docker exec go-api ping postgres
# PING postgres (172.20.0.3): 56 data bytes

# ✅ Inspect network
docker network inspect app-network
```

```go
// ✅ Go app connects using container DNS name
package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	_ "github.com/lib/pq"
)

func main() {
	// "postgres" resolves via Docker DNS to the PostgreSQL container
	dbURL := os.Getenv("DATABASE_URL")
	// = postgres://appuser:secret@postgres:5432/myapp?sslmode=disable
	//                              ^^^^^^^^ Docker DNS name

	db, err := sql.Open("postgres", dbURL)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	if err := db.Ping(); err != nil {
		log.Fatal(fmt.Errorf("❌ Cannot reach postgres: %w", err))
	}
	log.Println("✅ Connected to PostgreSQL via Docker DNS")
}
```

**Result**: DNS-based service discovery, no IP hardcoding.
**Note**: Default bridge (`docker0`) has NO DNS resolution. Always use a custom network.

---

Bridge network is covered. But service discovery needs a custom network — time to create one.

### Example 2: Intermediate — Multi-network Isolation

> **Goal**: Frontend → API → Database isolation.
> **Requires**: Multiple containers, security requirements.
> **Result**: Network segmentation — DB not exposed to frontend.

```yaml
# docker-compose.yaml — Multi-network setup
services:
    nginx:
        image: nginx:alpine
        ports:
            - '80:80'
        networks:
            - frontend # ✅ Only frontend network
        volumes:
            - ./nginx.conf:/etc/nginx/nginx.conf:ro
        depends_on:
            api: { condition: service_healthy }

    api:
        build: .
        networks:
            - frontend # ✅ Nginx can reach API
            - backend # ✅ API can reach DB
        environment:
            DATABASE_URL: postgres://appuser:secret@postgres:5432/myapp?sslmode=disable
            REDIS_URL: redis://redis:6379
        healthcheck:
            test: ['CMD', 'curl', '-f', 'http://localhost:8080/healthz']
            interval: 10s
        # ❌ NO ports exposed — only through nginx

    postgres:
        image: postgres:16-alpine
        networks:
            - backend # ✅ Only backend network
        environment:
            POSTGRES_USER: appuser
            POSTGRES_PASSWORD: secret
            POSTGRES_DB: myapp
        volumes:
            - pgdata:/var/lib/postgresql/data
        healthcheck:
            test: ['CMD-SHELL', 'pg_isready -U appuser']
            interval: 5s
        # ❌ NO ports exposed — security!

    redis:
        image: redis:7-alpine
        networks:
            - backend # ✅ Only backend network
        volumes: [redisdata:/data]

networks:
    frontend:
        driver: bridge
    backend:
        driver: bridge
        internal: true # ✅ No external access — extra isolation

volumes:
    pgdata:
    redisdata:
```

```text
# Network isolation matrix:
#
#              nginx    api    postgres    redis
# nginx          -      ✅       ❌         ❌
# api           ✅       -       ✅         ✅
# postgres      ❌      ✅        -         ❌
# redis         ❌      ✅       ❌          -
#
# ✅ = can communicate
# ❌ = isolated (different networks)
```

**Result**: Frontend ↔ API ↔ Backend isolated. DB not exposed.
**Note**: `internal: true` on backend network means no internet access from that network.

---

Custom network is covered. But multi-host needs overlay — time to expand.

### Example 3: Advanced — Host Network + Performance

> **Goal**: Maximum network performance for benchmarking.
> **Requires**: Linux host (host network does not work on macOS).
> **Result**: Zero overhead networking.

```bash
# ✅ Host network — container shares host's network stack
docker run -d \
  --name go-api \
  --network host \
  -e PORT=8080 \
  go-api:latest

# Container listens directly on host:8080
# No port mapping needed — no NAT overhead
# DNS uses host's /etc/resolv.conf

# ✅ Performance comparison
# Bridge network: ~0.1ms latency overhead per request
# Host network:   ~0ms (native performance)
```

```go
// benchmark/network_test.go — Measure Docker network overhead
package benchmark

import (
	"net/http"
	"testing"
	"time"
)

func BenchmarkDockerBridge(b *testing.B) {
	client := &http.Client{Timeout: 5 * time.Second}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		resp, err := client.Get("http://localhost:8080/healthz")
		if err != nil {
			b.Fatal(err)
		}
		resp.Body.Close()
	}
}

// Results (typical):
// BenchmarkDockerBridge-8    10000    112μs/op  (bridge)
// BenchmarkDockerHost-8      10000     98μs/op  (host)
// BenchmarkNative-8          10000     95μs/op  (no container)
```

**Result**: Near-native performance, suitable for latency-sensitive apps.
**Note**: Host network means no isolation. Use only when maximum performance is required.

---

You have covered bridge, custom network, and host mode. Now comes the dangerous part: no DNS resolution and port conflicts — the trap set up from the beginning.

## 4. PITFALLS

Knowing how to do it right is only half the story. The other half is the places where it is easy to get almost right and pay the price when the cluster or OS shakes.

| #   | Mistake                              | Consequence                                           | Fix                                              |
| --- | ------------------------------------ | ----------------------------------------------------- | ------------------------------------------------ |
| 1   | Default bridge has no DNS            | Containers cannot resolve each other's hostname       | Always use a custom bridge network               |
| 2   | Port conflict with host network      | Container cannot bind port, exits                     | Container and host ports must not clash           |
| 3   | `internal: true` blocks internet     | Container cannot pull images or call external APIs    | Pull images first, use only for backend services |
| 4   | macOS does not support host network  | Network does not work, container is isolated          | Use bridge + port mapping on macOS               |
| 5   | Container restart changes IP         | Hard-coded IP connections break                       | Use DNS names, never hardcode IPs                |

---

You have covered Docker Networking and the traps. The resources below help go deeper.

## 5. REF

| Resource           | Link                                                                                      |
| ------------------ | ----------------------------------------------------------------------------------------- |
| Docker Networking  | [docs.docker.com/network](https://docs.docker.com/network/)                               |
| Bridge Networks    | [docs.docker.com/network/drivers/bridge](https://docs.docker.com/network/drivers/bridge/) |
| Compose Networking | [docs.docker.com/compose/networking](https://docs.docker.com/compose/networking/)         |

---

## 6. RECOMMEND

Now that you have seen what this lane solves and where it commonly breaks, the resources below expand along the nearest operational pressure.

| Next step                | When                  | Reason                             |
| ------------------------ | --------------------- | ---------------------------------- |
| **Traefik**              | Dynamic reverse proxy | Auto-discover Docker services      |
| **Caddy**                | Simple HTTPS          | Auto TLS, zero config              |
| **WireGuard**            | Cross-host networking | Secure tunnel between Docker hosts |
| **Cilium**               | eBPF networking       | Advanced network policies          |
| **Docker Swarm Overlay** | Multi-host            | Built-in overlay networking        |

---

**Links**: [← Docker Compose](./02-docker-compose.md) · [→ Volumes & Data](./04-volumes-data.md)
