<!-- tags: golang, testing -->
# 🐳 Integration Testing — Testcontainers, httptest, sqlmock

> Go integration testing: real containers (testcontainers-go), HTTP testing (httptest), DB mocking (sqlmock).

📅 Created: 2026-03-23 · 🔄 Updated: 2026-04-19 · ⏱️ 18 min read

| Aspect          | Detail                                                    |
| --------------- | --------------------------------------------------------- |
| **Scope**       | Integration tests — real dependencies (DB, cache, broker) |
| **Tools**       | `testcontainers-go`, `net/http/httptest`, `sqlmock`       |
| **Distinguish** | Unit test = mock; Integration = real containers           |
| **Go packages** | `github.com/testcontainers/testcontainers-go`             |

---

## 1. DEFINE

Unit test pass, CI green. Deploy staging — API pays 500. Reason: query uses PostgreSQL-specific syntax that sqlmock does not capture, `httptest.Server` does not test TLS negotiation, and test data factory does not reproduce production.

> *Unit tests have passed 100%, coverage 90%. Deploy to staging — service crashes on first DB call. PostgreSQL throws unique constraint violation but mock returns `nil`. You have tested the logic, but not **integration**. Hotfix:
>
> *Integration Testing solves this gap: run real DB, Redis, Kafka in isolated Docker containers. `testcontainers-go` spins up the PostgreSQL container in 2-3 seconds, runs real SQL, then destroys. Each test suite receives fresh database —.

**Integration Testing** Check the interaction between real components: service calls real DB, real cache, real broker. Unlike unit tests (completely mocked), integration tests **run real dependencies** in an isolated Docker container for each test suite.

### Unit Test vs Integration Test vs E2E

| Type | Dependencies   | Speed | What was discovered? | Tool Go                    |
| ----------------- | -------------- | ------- | -------------------------------- | -------------------------- |
| **Unit Test**     | Completely mocked | ⚡ ms   | Error logic in function | `testing`, `testify`       |
| **Integration**   | Real (Docker)  | 🐢 s    | DB/cache/broker interaction error | `testcontainers-go`        |
| **E2E**           | Full system    | 🐌 min  | Actual user flow | `playwright-go`, Postman   |

### Main patterns

| Pattern                       | Describe | When used |
| ----------------------------- | ---------------------------------------------------- | ----------------------------- |
| **httptest.Recorder**         | Test HTTP handler without starting the server | Test handlers, middlewares    |
| **httptest.Server**           | Test HTTP client code with real server | Test HTTP client, webhooks    |
| **Testcontainers PostgreSQL** | Real PostgreSQL in Docker per test                  | Repository layer tests        |
| **Testcontainers Redis**      | Real Redis in Docker per test                       | Cache layer tests             |
| **sqlmock**                   | Mock `database/sql` interface (no Docker needed) | When Docker is not available  |

### Failure Modes

| Failure                      | Consequence | How to avoid |
| ---------------------------- | ----------------------------------------- | ------------------------------------------------- |
| Docker is not running | Tests fail "Cannot connect to daemon"     | `//go:build integration` tag to skip locally |
| Port conflict                | Container bind port is occupied | Use `MappedPort()` — random available port |
| No container cleanup          | Container leaks, disk space exhausted | `t.Cleanup(func() { container.Terminate(ctx) })`  |
| Shared DB state between tests | Flaky tests, ordering dependency          | Each test uses its own database or transaction rollback |
| Slow CI                      | CI pipeline > 10 minutes | Run unit and integration tests separately |

Unit vs integration vs E2E, patterns, failure modes — enough theory. Let's see how the testing pyramid and testcontainers lifecycle look visually.

---
## 2. VISUAL

In integration testing, visuals must follow the lifecycle and cannot just summarize tool names. What the reader needs to remember is the order in which the boundary is brought up, exercised, and then torn down.

![Integration testcontainers workflow](./images/03-integration-testcontainers-workflow.png)

*Figure: Workflow map starts from choosing the right boundary (`httptest` or containerized dependency), goes to setup and readiness, then runs real interactions, and ends with cleanup to prevent flakiness.*

When this lifecycle is in place, the code below will have the payout. You'll see each example as a complete execution flow, not just as several separate tool recipes.

## 3. CODE

With **Integration Testing — Testcontainers, httptest, sqlmock**, we have a decision map. Now lower it down to code to see how each choice — testcontainer or mock, httptest or real server, sqlmock or test database.

### Example 1: Basic — httptest — Testing HTTP Handlers.
> **Objective**: Test HTTP handlers in memory without a real server or network stack.
> **Approach**: `httptest.NewRequest` + `httptest.NewRecorder` + `handler.ServeHTTP()` = complete request/response cycle in memory.
> **Example**: `TestCreateUser_HTTP` sends a POST request and asserts HTTP 201 + response body.
> **Complexity**: O(1) per request; zero TCP overhead.

```go
package handler_test

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

"github.com/stretchr/testify/assert"
)

func TestCreateUser_HTTP(t *testing.T) {
	app := setupApp() // wire real or mock dependencies

body := `{"name":"Alice","email":"alice@test.com"}`
	req := httptest.NewRequest(http.MethodPost, "/api/users", strings.NewReader(body))
	req.Header.Set("Content-Type", "application/json")

rec := httptest.NewRecorder()
	app.ServeHTTP(rec, req) // or app.Test(req) for Fiber

assert.Equal(t, 201, rec.Code)
	assert.Contains(t, rec.Body.String(), "Alice")
}
```

> **Why doesn't `httptest` need a real server?**
> `httptest.NewRecorder()` implements `http.ResponseWriter` interface — handler writes response to recorder instead of network. Zero TCP overhead, zero port conflicts. Test handler logic directly, not through the network stack.

> **Conclusion**: `httptest` provides handler-level testing — fast, isolated, no Docker needed. `NewRequest` + `NewRecorder` + `handler.ServeHTTP()` = complete request/response cycle in memory.

httptest cover handler testing without Docker. But when it comes to testing real SQL queries — unique constraints, foreign keys, indexes — mock is not enough. Need real PostgreSQL in Docker.

### Example 2: Intermediate — Testcontainers — Real PostgreSQL.
> **Objective**: Test repository layer against a real PostgreSQL instance running in Docker.
> **Approach**: `testcontainers-go` spins up a PostgreSQL container, runs real SQL, then destroys it. Each test gets a fresh database.
> **Example**: `TestUserRepo_Create` inserts a user, then reads it back from the real database.
> **Complexity**: ~2-3 seconds for container startup; O(1) per query.

```go
package repo_test

import (
	"context"
	"testing"

"github.com/stretchr/testify/assert"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/modules/postgres"
	"github.com/testcontainers/testcontainers-go/wait"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func setupPostgres(t *testing.T) *gorm.DB {
	ctx := context.Background()

// ✅ Real PostgreSQL in Docker
	container, err := postgres.Run(ctx, "postgres:16",
		postgres.WithDatabase("testdb"),
		postgres.WithUsername("test"),
		postgres.WithPassword("test"),
		testcontainers.WithWaitStrategy(
			wait.ForLog("database system is ready to accept connections").
				WithOccurrence(2),
		),
	)
	assert.NoError(t, err)
	t.Cleanup(func() { container.Terminate(ctx) })

connStr, _ := container.ConnectionString(ctx, "sslmode=disable")
	db, err := gorm.Open(postgres.Open(connStr), &gorm.Config{})
	assert.NoError(t, err)

db.AutoMigrate(&User{})
	return db
}

func TestUserRepo_Create(t *testing.T) {
	db := setupPostgres(t)
	repo := NewUserRepo(db)

user := &User{Name: "Alice", Email: "alice@test.com"}
	err := repo.Create(context.Background(), user)

assert.NoError(t, err)
	assert.NotZero(t, user.ID)

// ✅ Verify in real DB
	found, err := repo.FindByID(context.Background(), user.ID)
	assert.NoError(t, err)
	assert.Equal(t, "Alice", found.Name)
}
```

> **Why `WithOccurrence(2)` when waiting for PostgreSQL?**
> PostgreSQL logs "database system is ready to accept connections" **twice**: first when init, second when ready for connections. Wait for the first occurrence → container is not really ready → connection refused.

> **Conclusion**: `testcontainers-go` modules (postgres, redis) provide pre-configured containers. `t.Cleanup()` ensures the container is destroyed after the test. `MappedPort()` returns a random port — no port conflicts.

PostgreSQL covers SQL testing. But when you need to test the cache layer — Redis TTL, eviction, concurrent access — you need real Redis. Same pattern, but use `GenericContainer` for any Docker image.

### Example 3: Advanced — Testcontainers — Redis.
> **Objective**: Test cache layer against a real Redis instance using `GenericContainer`.
> **Approach**: `GenericContainer` works with any Docker image. No dedicated module needed — specify the image, exposed port, and readiness log.
> **Example**: `setupRedis` starts a Redis container, extracts the dynamic host/port, and returns a connected `redis.Client`.
> **Complexity**: ~1-2 seconds for container startup; O(1) per operation.

```go
func setupRedis(t *testing.T) *redis.Client {
	ctx := context.Background()

container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: testcontainers.ContainerRequest{
			Image:        "redis:7-alpine",
			ExposedPorts: []string{"6379/tcp"},
			WaitingFor:   wait.ForLog("Ready to accept connections"),
		},
		Started: true,
	})
	assert.NoError(t, err)
	t.Cleanup(func() { container.Terminate(ctx) })

host, _ := container.Host(ctx)
	port, _ := container.MappedPort(ctx, "6379")

return redis.NewClient(&redis.Options{
		Addr: fmt.Sprintf("%s:%s", host, port.Port()),
	})
}
```

> **Why does Redis use `GenericContainer` instead of modules?**
> `testcontainers-go` has modules for PostgreSQL, MySQL, MongoDB — but the Redis module is simpler so use `GenericContainer` to illustrate the general pattern. Any Docker image can be used with `GenericContainer`.

> **Conclusion**: `GenericContainer` works with any Docker image. `MappedPort()` handles dynamic port allocation. The same pattern applies to Kafka, RabbitMQ, Elasticsearch — any dependency with a Docker image.

You already know httptest, PostgreSQL testcontainers, and Redis. Now comes the dangerous part: container leak and shared DB state — two traps that have been set up from the beginning of the article.

---

## 4. PITFALLS

The correct mechanism of **Integration Testing — Testcontainers, httptest, sqlmock** is clear. The remaining thing is to recognize the places that are easy to write _approximately_ and then bring flaky integration tests or port conflicts.

| # | Severity | Error | Consequence | Fix |
|---|----------|-----|---------|-----|
| 1 | 🔴 Fatal | Missing `t.Cleanup()` for container | Container leak → exhausted disk space, port exhaustion | `t.Cleanup(func() { container.Terminate(ctx) })` immediately after start |
| 2 | 🔴 Fatal | Shared DB state between tests | Flaky tests, order-dependent failures | Each test uses fresh DB or transaction rollback |
| 3 | 🟡 Common | Docker not running | "Cannot connect to Docker daemon" | `//go:build integration` tag + skip when Docker is unavailable |
| 4 | 🟡 Common | Hardcoded port instead of `MappedPort()` | Port conflict in parallel tests | Always use `container.MappedPort()` for dynamic ports |
| 5 | 🟡 Common | Integration tests run alongside unit tests | CI is 10x slow | Separate build tag: `go test -tags=integration ./...` |
| 6 | 🔵 Minor | Container startup timeout is too short | Flaky on slow CI runners | Increase `WithStartupTimeout(60 * time.Second)` |

### 🔴 Pitfall #1 — Container leak = Resource exhaustion

Forgot `t.Cleanup()` → container is not terminated after test → disk, memory, ports accumulate. Run the test suite 100 times → 100 containers. The CI runner runs out of disk and ports → pipeline fails. Always call `t.Cleanup(func() { container.Terminate(ctx) })` immediately after starting the container.

### 🔴 Pitfall #2 — Shared DB state = Flaky tests

Test A inserts data, test B reads A's data → pass. Change order → fail. Each test needs fresh state: `t.Cleanup` truncate tables, or each test uses transaction rollback (`go-txdb`).

You've come across the httptest, testcontainers, and resource exhaustion pitfalls. The resources below help go deeper.

---

## 5. REF

| Resource          | Type | Link                                                                 | Note |
| ----------------- | -------- | -------------------------------------------------------------------- | ------- |
| testcontainers-go | Library  | [golang.testcontainers.org](https://golang.testcontainers.org/)      | Docker containers for Go tests |
| httptest          | Official | [pkg.go.dev/net/http/httptest](https://pkg.go.dev/net/http/httptest) | In-memory HTTP testing |
| sqlmock           | Library  | [github.com/DATA-DOG/go-sqlmock](https://github.com/DATA-DOG/go-sqlmock) | Mock database/sql without Docker |
| go-txdb           | Library  | [github.com/DATA-DOG/go-txdb](https://github.com/DATA-DOG/go-txdb)   | Per-test transaction isolation |

---

## 6. RECOMMEND

The core part of **Integration Testing — Testcontainers, httptest, sqlmock** is clear. The extension branches below help you bring integration testing into production with test isolation, Kafka/Mongo modules, and CI optimization.

| Extend | When | Reason | File/Link |
| ------- | ------- | ----- | --------- |
| Table-driven + mocking | Unit test layer | Complement integration tests | [01-table-driven-mocking.md](./01-table-driven-mocking.md) |
| Benchmark & Fuzz | Performance testing | Measure query performance on real DB | [02-benchmark-fuzz.md](./02-benchmark-fuzz.md) |
| go-txdb | Test isolation | Each test runs in a rolled-back transaction — faster than one container per test | [github.com/DATA-DOG/go-txdb](https://github.com/DATA-DOG/go-txdb) |
| Testcontainers modules | Kafka, MongoDB, etc. | Pre-configured containers for common services | [golang.testcontainers.org/modules](https://golang.testcontainers.org/modules/) |

---

**Navigation**: [← Benchmark & Fuzz](./02-benchmark-fuzz.md) · [→ Interfaces](../interfaces/01-implicit-io-patterns.md)
