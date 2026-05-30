<!-- tags: golang, data-structures -->
# 10 — Semaphore

> **Package**: `golang.org/x/sync/semaphore` — Weighted semaphore for concurrent access control.

📅 Created: 2026-03-20 · 🔄 Updated: 2026-04-19 · ⏱️ 15 min read

| Aspect         | Detail                                                        |
| -------------- | ------------------------------------------------------------- |
| **Concept**    | Weighted semaphore — N concurrent slots, weighted acquire     |
| **Use case**   | DB connection limit, file I/O cap, mixed resource weights     |
| **Go stdlib**  | `golang.org/x/sync/semaphore.Weighted`                        |
| **Key insight**| Semaphore = Mutex(N) — allows N instead of 1, with configurable weight |

---

## 1. DEFINE

A worker pool limits goroutines. A semaphore limits *concurrent access to a resource* — database connections, file handles, API rate limits. The difference matters: a worker pool owns the goroutine lifecycle; a semaphore is a permit counter that any goroutine can acquire and release, making it composable with pipelines, fan-out, and HTTP handlers.

Your DB pool has max 20 connections. The API server spawns 100 goroutines querying in parallel → 80 goroutines get rejected because connections are exhausted. `errgroup.SetLimit(20)` works but only counts goroutines. If you need to limit by **weight** (light query = 1 slot, heavy query = 5 slots), semaphore is the precise tool: acquire N slots before running, release after completion. But there is a trap: `Acquire` blocks forever if the context has no timeout — caller goroutine stuck. And releasing the wrong weight = semaphore permanently broken. That trap will surface in PITFALLS.

### Definition

A **Semaphore** is a mechanism that limits the number of goroutines accessing a resource concurrently. Unlike Mutex (allows only 1), semaphore allows **up to N** goroutines simultaneously.

**`semaphore.Weighted`** is the implementation in the Go x/ library — supports weighted acquire (each goroutine can "claim" more than 1 slot).

### Semaphore vs Mutex vs Channel

| Mechanism              | Max concurrent   | Weighted? | Blocking?           | Context? |
| ---------------------- | ---------------- | --------- | ------------------- | -------- |
| **Mutex**              | 1                | ❌        | Lock blocks         | ❌       |
| **Channel (buffered)** | N (buffer size)  | ❌        | Send blocks when full | ❌     |
| **semaphore.Weighted** | N (configurable) | ✅        | `Acquire` blocks    | ✅ `ctx` |
| **errgroup.SetLimit**  | N                | ❌        | `Go` blocks         | ✅       |

### Use cases

| Use case                | Example                                             |
| ----------------------- | --------------------------------------------------- |
| **Rate limiting**       | Max 10 concurrent HTTP requests to external API     |
| **Resource protection** | Max 5 concurrent DB connections                     |
| **Weighted resources**  | GPU tasks need 2 slots, CPU tasks need 1 slot       |
| **Batch processing**    | Process 1000 files but only 20 at a time            |

### Invariants

- `Acquire(ctx, n)` blocks until ≥ n slots are available
- `Release(n)` frees n slots — **MUST** release the exact number acquired
- `TryAcquire(n)` is non-blocking — returns false if not enough slots
- Total slots released ≤ total slots acquired — violation = panic

### Failure Modes

| Failure             | Cause                        | Prevention             |
| ------------------- | ---------------------------- | ---------------------- |
| **Deadlock**        | Acquire more than max weight | Acquire ≤ max weight   |
| **Resource leak**   | Forget Release               | `defer sem.Release(n)` |
| **Context expired** | Timeout before acquire       | Handle `ctx.Err()`     |

Semaphore, weighted access control, invariants — theory is covered. Let us see what the acquire/release flow looks like visually.

---
## 2. VISUAL

Semaphore is easily misunderstood as "mutex for multiple slots". The PNG below should be the primary visual because it clarifies permit flow and saturation signal before you look at ASCII examples.

![Semaphore permit flow](./images/10-semaphore-permit-flow.png)

*What is memorable about semaphore is not the acquire/release API, but how permit count transforms resource pressure into intentional wait time.*

### Semaphore Flow

```
  Semaphore(3)        ← max 3 concurrent slots
  ┌──────────────┐
  │ ■ ■ ■        │    3 slots available
  └──────────────┘

G1: Acquire(1)  → ■ □ □  (2 remaining)
  G2: Acquire(1)  → ■ ■ □  (1 remaining)
  G3: Acquire(1)  → ■ ■ ■  (0 remaining)
  G4: Acquire(1)  → BLOCK  (waits for Release)

G1: Release(1)  → ■ ■ □  (1 available → G4 unblocks)
  G4: acquired!   → ■ ■ ■  (0 remaining)
```

### Weighted Semaphore

```
  Semaphore(4)        ← 4 slots total

GPU Task: Acquire(2)  → ■ ■ □ □   (needs 2 slots)
  CPU Task: Acquire(1)  → ■ ■ ■ □   (needs 1 slot)
  CPU Task: Acquire(1)  → ■ ■ ■ ■   (full)
  GPU Task: Acquire(2)  → BLOCK     (needs 2 but only 0 available)

CPU Release(1):       → ■ ■ ■ □   (1 available, GPU needs 2 → still blocks)
  CPU Release(1):       → ■ ■ □ □   (2 available → GPU unblocks!)
```

The diagrams give an overview of weighted semaphore. Now let us implement — starting from basic Acquire, then TryAcquire, then weighted, then Gin middleware.

---

## 3. CODE

The flow of **Semaphore** is visible. Now let us lower it into code to see what constraints make this mechanism hold, not just intuition.

---

### Example 1: Basic — Limiting concurrent HTTP requests
> **Goal**: Demonstrate limiting concurrent HTTP requests in the right context so the reader understands why this technique exists.
> **Approach**: Start from a basic example then attach necessary technical decisions instead of jumping straight into hard code.
> **Example**: A job or request passes through multiple goroutines while preserving cancellation, concurrency limits, and clear error handling.
> **Complexity**: O(1) orchestration in application code; real cost depends on data, goroutines, or I/O being demonstrated.

**Goal**: Max 5 concurrent requests to an external API. 20 URLs to fetch, semaphore ensures only 5 goroutines run at a time.

**Requirements**: `golang.org/x/sync/semaphore`, `context`.

```go
package main

import (
    "context"
    "fmt"
    "math/rand/v2" // Go 1.22+
    "sync"
    "time"

"golang.org/x/sync/semaphore"
)

func main() {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // semaphore.NewWeighted(5): max 5 concurrent
    // Each Acquire(ctx, 1) claims 1 slot
    // Each Release(1) returns 1 slot
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    sem := semaphore.NewWeighted(5)
    ctx := context.Background()

urls := make([]string, 20)
    for i := range urls {
        urls[i] = fmt.Sprintf("https://api.example.com/data/%d", i+1)
    }

var wg sync.WaitGroup
    var mu sync.Mutex
    results := make([]string, 0, 20)

for _, url := range urls {
        wg.Add(1)
        go func(u string) {
            defer wg.Done()

// ━━━ Acquire 1 slot — blocks if full ━━━
            if err := sem.Acquire(ctx, 1); err != nil {
                fmt.Printf("❌ Acquire failed for %s: %v\n", u, err)
                return
            }
            defer sem.Release(1) // ← ALWAYS defer Release

// Simulate HTTP request
            delay := time.Duration(100+rand.IntN(300)) * time.Millisecond
            time.Sleep(delay)

result := fmt.Sprintf("✅ %s (took %v)", u, delay)

mu.Lock()
            results = append(results, result)
            mu.Unlock()
        }(url)
    }

wg.Wait()
    fmt.Printf("Fetched %d/%d URLs (max 5 concurrent)\n", len(results), len(urls))
}
```

This example is appropriate for grasping the baseline of limiting concurrent HTTP requests. When you need to handle more edge cases or coordinate additional abstractions, move to the next example.

**Achieved**:

- 20 URLs but only 5 running at a time — avoids overwhelming the API.
- `Acquire` blocks excess goroutines, auto-unblocks when a slot opens.

**Caveats**:

- `defer sem.Release(1)` **immediately after** Acquire — avoids leaking slots.
- `Acquire(ctx, 1)` supports context — cancel = unblock waiting goroutines.
- Different from `errgroup.SetLimit(5)`: semaphore allows **weighted** access.

Basic semaphore covers bounded concurrency. But when you need a non-blocking check (circuit breaker, graceful degradation) — TryAcquire returns immediately instead of blocking.

---

### Example 2: Intermediate — TryAcquire — Non-blocking check
> **Goal**: Demonstrate TryAcquire — non-blocking check in the right context so the reader understands why this technique exists.
> **Approach**: Start from an intermediate example then attach necessary technical decisions instead of jumping straight into hard code.
> **Example**: A job or request passes through multiple goroutines while preserving cancellation, concurrency limits, and clear error handling.
> **Complexity**: O(1) orchestration; total complexity depends on the number of coordination steps and related data structures.

**Goal**: Try to acquire without blocking — if not enough slots, skip or fallback.

**Requirements**: `semaphore` package.

```go
package main

import (
    "fmt"
    "time"

"golang.org/x/sync/semaphore"
)

func main() {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Scenario: Request handler with rate limiting
    // If all slots busy → return "429 Too Many Requests"
    // instead of blocking the caller (unlike Acquire)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    sem := semaphore.NewWeighted(3) // max 3 concurrent handlers

for i := 1; i <= 10; i++ {
        // ━━━ TryAcquire: returns true/false immediately ━━━
        if !sem.TryAcquire(1) {
            fmt.Printf("Request %d: 🚫 429 Too Many Requests (all slots busy)\n", i)
            continue
        }

go func(reqID int) {
            defer sem.Release(1)
            fmt.Printf("Request %d: ✅ Processing...\n", reqID)
            time.Sleep(500 * time.Millisecond) // simulate work
            fmt.Printf("Request %d: ✅ Done\n", reqID)
        }(i)

time.Sleep(100 * time.Millisecond) // simulate request arrival rate
    }

time.Sleep(2 * time.Second) // wait for processing
}
```

This level starts being useful for real code because it coordinates multiple techniques. The caveat is to keep the API compact so the reader does not lose track of reasoning.

**Achieved**:

- Requests 1-3: processed (3 slots available).
- Requests 4+: depending on timing — if slots busy → reject immediately (429).
- **Non-blocking**: caller does not have to wait.

**Caveats**:

- `TryAcquire` is suitable for **HTTP handlers** — return 429/503 instead of timeout.

> **Why use `TryAcquire` instead of `Acquire` with a short timeout?**
> `Acquire` with timeout still holds 1 goroutine waiting for the timeout duration. `TryAcquire` returns immediately (true/false) — zero blocking. In a high-traffic HTTP handler, you want to return 429 right away rather than keeping the connection open waiting for a slot.

- `Acquire` is suitable for **background workers** — wait for an available slot.

TryAcquire covers non-blocking. But when resource costs differ (light vs heavy queries) — weighted semaphore lets each task acquire a different weight.

---

### Example 3: Advanced — Weighted Semaphore — Different resource weights
> **Goal**: Demonstrate weighted semaphore — different resource weights in the right context so the reader understands why this technique exists.
> **Approach**: Start from an advanced example then attach necessary technical decisions instead of jumping straight into hard code.
> **Example**: A job or request passes through multiple goroutines while preserving cancellation, concurrency limits, and clear error handling.
> **Complexity**: O(1) orchestration at the example layer; real complexity lies in concurrency, memory, and integration underneath.

**Goal**: Tasks with different weights: GPU task needs 2 slots, CPU task needs 1 slot. 4 total slots — coordinate resource allocation.

**Requirements**: `semaphore` package to demonstrate weighted allocation.

```go
package main

import (
    "context"
    "fmt"
    "sync"
    "time"

"golang.org/x/sync/semaphore"
)

type Task struct {
    Name   string
    Weight int64  // slots needed
    Work   time.Duration
}

func main() {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Total capacity: 4 slots
    // GPU tasks: need 2 slots each
    // CPU tasks: need 1 slot each
    //
    // Scenario:
    //   2 GPU tasks (2 slots each) = 4 slots → full
    //   4 CPU tasks (1 slot each) = 4 slots → full
    //   1 GPU + 2 CPU = 2 + 2 = 4 slots → full
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    sem := semaphore.NewWeighted(4)
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()

tasks := []Task{
        {"GPU-Render-1", 2, 800 * time.Millisecond},
        {"CPU-Hash-1",   1, 300 * time.Millisecond},
        {"GPU-Train-1",  2, 1200 * time.Millisecond},
        {"CPU-Hash-2",   1, 200 * time.Millisecond},
        {"CPU-Hash-3",   1, 400 * time.Millisecond},
        {"GPU-Render-2", 2, 600 * time.Millisecond},
        {"CPU-Hash-4",   1, 150 * time.Millisecond},
    }

var wg sync.WaitGroup
    for _, task := range tasks {
        wg.Add(1)
        go func(t Task) {
            defer wg.Done()

fmt.Printf("[%s] ⏳ Waiting for %d slot(s)...\n", t.Name, t.Weight)

// Acquire: wait for enough slots (weight)
            if err := sem.Acquire(ctx, t.Weight); err != nil {
                fmt.Printf("[%s] ❌ Context cancelled: %v\n", t.Name, err)
                return
            }
            defer sem.Release(t.Weight) // ← release the EXACT number acquired

fmt.Printf("[%s] ▶️  Running (using %d slot(s))...\n", t.Name, t.Weight)
            time.Sleep(t.Work)
            fmt.Printf("[%s] ✅ Done\n", t.Name)
        }(task)
    }

wg.Wait()
    fmt.Println("\nAll tasks completed!")
}
```

This is the closest to production level in this article. Only keep this complexity when the trade-off yields clear benefits in correctness, throughput, or maintainability.

**Achieved**:

- GPU tasks (weight=2) claim more slots than CPU tasks (weight=1).
- The scheduler self-balances: GPU tasks wait longer if not enough slots.
- Context timeout protects everything — tasks waiting too long get cancelled.

**Caveats**:

- `Release(n)` must = `Acquire(n)` — releasing too many = **panic**.
- Weighted semaphore is ideal for **mixed workloads** (GPU/CPU, heavy/light tasks).

> **Why weighted semaphore instead of multiple separate semaphores?**
> If you use 2 separate semaphores (1 for heavy, 1 for light), total concurrency is not controlled: 10 heavy + 10 light could run at the same time even though the system can only handle 10 units. Weighted semaphore sharing 1 pool: heavy = 5 units, light = 1 unit, total = 10 — guarantees a global bound.

- If all tasks have weight=1 → use channel semaphore or `errgroup.SetLimit` for simplicity.

Weighted semaphore covers resource-aware limiting. Combining with Gin HTTP middleware + GORM = production API rate limiter.

---

### Example 4: Expert — Semaphore + Gin Middleware + GORM — API Rate Limiter
> **Goal**: Demonstrate semaphore + Gin middleware + GORM — API rate limiter in the right context so the reader understands why this technique exists.
> **Approach**: Start from an expert example then attach necessary technical decisions instead of jumping straight into hard code.
> **Example**: A job or request passes through multiple goroutines while preserving cancellation, concurrency limits, and clear error handling.
> **Complexity**: O(1) orchestration at the application layer; the hard parts lie in reliability, scale, and operations.

**Goal**: HTTP middleware using semaphore to limit concurrent requests for DB-heavy API routes. Lightweight routes (health check) are not limited. Combining semaphore + Gin + GORM for a real-world API server.

**Requirements**: `golang.org/x/sync/semaphore`, `github.com/gin-gonic/gin`, `gorm.io/gorm`.

**Components**: API server with 2 routes: `/reports` (heavy — max 5 concurrent) and `/health` (lightweight — no limit). Middleware auto-injects semaphore based on route weight.

```go
package main

import (
    "context"
    "fmt"
    "log"
    "net/http"
    "time"

"github.com/gin-gonic/gin"
    "golang.org/x/sync/semaphore"
    "gorm.io/driver/postgres"
    "gorm.io/gorm"
)

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// GORM Model
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
type Report struct {
    ID        uint      `gorm:"primarykey" json:"id"`
    Title     string    `gorm:"column:title" json:"title"`
    Data      string    `gorm:"column:data;type:text" json:"data"`
    CreatedAt time.Time `json:"created_at"`
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// ConcurrencyLimiter Middleware
// Limits concurrent requests using weighted semaphore
//
// Why semaphore instead of rate limiter?
// - Rate limiter: limits REQUESTS PER SECOND (throughput)
// - Semaphore: limits CONCURRENT REQUESTS (concurrency)
// - DB-heavy routes: need concurrency limit (avoid connection exhaustion)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
func ConcurrencyLimiter(sem *semaphore.Weighted, weight int64, timeout time.Duration) gin.HandlerFunc {
    return func(c *gin.Context) {
        // Context with timeout for acquire
        ctx, cancel := context.WithTimeout(c.Request.Context(), timeout)
        defer cancel()

// ━━━ Try Acquire — if timeout exceeded → 503 ━━━
        if err := sem.Acquire(ctx, weight); err != nil {
            c.AbortWithStatusJSON(http.StatusServiceUnavailable, gin.H{
                "error":   "server busy",
                "message": "too many concurrent requests, please retry",
            })
            log.Printf("🚫 Request rejected (semaphore full): %s %s", c.Request.Method, c.Request.URL.Path)
            return
        }

// ━━━ Release when response is done ━━━
        defer sem.Release(weight)

c.Next()
    }
}

func main() {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Setup: GORM + Gin + Semaphore
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    dsn := "host=localhost user=app dbname=api port=5432 sslmode=disable"
    db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
    if err != nil {
        log.Fatal(err)
    }
    db.AutoMigrate(&Report{})

// Semaphore: max 5 concurrent DB-heavy requests
    // Why 5? DB connection pool = 10 connections
    // 5 report queries (each needing ~2 connections) = 10 connections max
    dbSem := semaphore.NewWeighted(5)

r := gin.Default()

// ━━━ Route 1: Health check — NO semaphore (always available) ━━━
    r.GET("/health", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{"status": "ok"})
    })

// ━━━ Route 2: Reports — Semaphore protected (max 5 concurrent) ━━━
    reports := r.Group("/reports")
    reports.Use(ConcurrencyLimiter(dbSem, 1, 5*time.Second))
    {
        // GET /reports — list all reports (DB-heavy: full table scan)
        reports.GET("", func(c *gin.Context) {
            var reportList []Report
            if err := db.WithContext(c.Request.Context()).
                Order("created_at DESC").
                Limit(100).
                Find(&reportList).Error; err != nil {
                c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
                return
            }

c.JSON(http.StatusOK, reportList)
        })

// POST /reports — generate report (VERY heavy: aggregation query)
        reports.POST("", func(c *gin.Context) {
            // Simulate heavy DB aggregation
            var report Report
            if err := c.ShouldBindJSON(&report); err != nil {
                c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
                return
            }

// Heavy query simulation
            time.Sleep(2 * time.Second)

if err := db.WithContext(c.Request.Context()).Create(&report).Error; err != nil {
                c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
                return
            }

c.JSON(http.StatusCreated, report)
        })
    }

// ━━━ Route 3: Export — weighted=2 (needs more resources) ━━━
    r.GET("/export", ConcurrencyLimiter(dbSem, 2, 10*time.Second), func(c *gin.Context) {
        // Export claims 2 slots — twice as heavy as a regular report
        var allReports []Report
        db.WithContext(c.Request.Context()).Find(&allReports)

// Format as CSV, PDF, etc.
        c.JSON(http.StatusOK, gin.H{
            "count":   len(allReports),
            "message": "export complete",
        })
    })

fmt.Println("Server running on :8080")
    fmt.Println("  GET  /health  — no limit")
    fmt.Println("  GET  /reports — max 5 concurrent (weight=1)")
    fmt.Println("  POST /reports — max 5 concurrent (weight=1)")
    fmt.Println("  GET  /export  — max 5 concurrent (weight=2)")
    r.Run(":8080")
}
```

This level is only appropriate when the team is already comfortable with the abstractions and related libraries. If there is no corresponding operational need, a simpler version is usually better.

**Achieved**:

- **Per-route concurrency control**: heavy routes (reports, export) are limited, lightweight (health) is not.
- **Weighted limiting**: `/export` claims 2 slots → max 2 concurrent exports (or 1 export + 3 reports).
- **503 instead of timeout**: client receives a fast response with retry hint.
- **GORM + context**: cancel propagation from HTTP request → DB query.

**Caveats**:

- **Timeout in middleware**: 5s acquire timeout → if server is too busy, client receives 503 within 5s instead of waiting forever.
- **Weighted semaphore advantage**: `/export` (weight=2) naturally limits fewer concurrent than `/reports` (weight=1).
- **Production**: add Prometheus metrics for `sem` occupancy, 503 count.

> **Why semaphore as HTTP rate limiter instead of `rate.Limiter`?**
> `rate.Limiter` (token bucket) limits **requests per second** — throughput-based. Semaphore limits **concurrent requests** — concurrency-based. Use semaphore when you want "only 10 requests running in parallel", use rate limiter when you want "max 100 requests/s". Two different problems, often combined together.

- Comparison with `rate.Limiter` (`x/time/rate`): rate limiter limits requests/second, semaphore limits concurrent. Choose based on use case.

You now know basic, TryAcquire, weighted, and Gin middleware. Here comes the dangerous part: Acquire blocking forever and releasing the wrong weight — traps set up from the beginning of this article.

---

## 4. PITFALLS

Knowing the right path of **Semaphore** is not enough. The part that costs teams the most lies in wrong assumptions that dashboards or code demos do not tell you.

| # | Severity | Mistake | Consequence | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Fatal | **Release != Acquire** | Panic at runtime | Release the EXACT number acquired — excess = panic |
| 2 | 🔴 Fatal | **Forget Release** | Resource leak, slots drain | `defer sem.Release(n)` immediately after Acquire |
| 3 | 🔴 Fatal | **Acquire > max weight** | Deadlock forever | Acquire(10) with max=5 → never resolves |
| 4 | 🟡 Common | **Not checking ctx error** | Silent failure | `Acquire` returns error when ctx cancels — must handle |

You have covered basic, TryAcquire, weighted, Gin middleware, and the block/weight/ctx traps. The resources below help you go deeper.

---

## 5. REF

| Resource | Type | Link | Notes |
| --- | --- | --- | --- |
| semaphore package | Official docs | [pkg.go.dev/golang.org/x/sync/semaphore](https://pkg.go.dev/golang.org/x/sync/semaphore) | Weighted semaphore API |
| Go x/sync repo | GitHub | [github.com/golang/sync](https://github.com/golang/sync) | Source code |

---

## 6. RECOMMEND

Once you have seen **Semaphore** in action and where it breaks, the next step is to open the right related branch for deeper exploration instead of optimizing blindly.

| Next step | When | Reason | File/Link |
| --- | --- | --- | --- |
| **errgroup.SetLimit(n)** | Simple limiting | Simpler when weighted is not needed | [05-errgroup.md](./05-errgroup.md) |
| **Buffered channel** | Lightweight semaphore | `make(chan struct{}, N)` for simple cases | Pattern |
| **x/time/rate** | Rate limiter | Token bucket — limits rate, not just concurrency | `golang.org/x/time/rate` |
| **Semaphore + Gin/Echo** | HTTP middleware | Limit concurrent requests per route | Pattern |
| **Semaphore + GORM** | DB connection | Limit concurrent DB queries | [orm/01](../orm/01-models-and-connection.md) |
| **Ants pool** | Combined with Ants | Worker pool = semaphore + goroutine reuse | [12-ants.md](./12-ants.md) |
