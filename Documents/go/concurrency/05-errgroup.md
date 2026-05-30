<!-- tags: golang -->
# 05 — Errgroup

> **Foundation**: Managing a group of goroutines with error propagation + context cancellation.

📅 Created: 2026-03-20 · 🔄 Updated: 2026-04-19 · ⏱️ 15 min read

| Aspect         | Detail                                                          |
| -------------- | --------------------------------------------------------------- |
| **Concept**    | errgroup.Group — goroutine orchestration with error + cancel    |
| **Use case**   | Parallel API calls, fan-out workers, pipeline error handling    |
| **Go stdlib**  | `golang.org/x/sync/errgroup`, `SetLimit`, `WithContext`         |
| **Key insight**| 1 goroutine fails → cancel all — replaces WaitGroup + manual err |

---

## 1. DEFINE

Running N goroutines concurrently is easy. Handling the first error, cancelling the rest, and collecting results without a race condition — that is the hard part. `errgroup` wraps `sync.WaitGroup` + `context.WithCancel` + error propagation into a single, composable API that eliminates an entire class of boilerplate bugs.

You call 3 external APIs in parallel using `sync.WaitGroup` + channels. Service 2 fails — but the other 2 goroutines keep running, wasting resources. And the error from service 2 gets swallowed because WaitGroup has no mechanism for returning errors. You would have to add a mutex, error channel, context manually. `errgroup.Group` solves all of that: error propagation, auto cancel, and concurrency limit — in 1 clean API. But there is a trap: a goroutine panic inside errgroup **kills the entire process** and is not recovered like an error. That trap will surface in PITFALLS.

### Definition

**`errgroup.Group`** (from `golang.org/x/sync/errgroup`) manages a group of goroutines running subtasks of a larger task. When **any goroutine returns an error** → the context auto-cancels → other goroutines receive the stop signal.

### WaitGroup vs Errgroup

| Property            | sync.WaitGroup               | errgroup.Group              |
| ------------------- | ---------------------------- | --------------------------- |
| **Error handling**  | ❌ No                        | ✅ Returns first error      |
| **Context cancel**  | ❌ No                        | ✅ Cancels on error         |
| **API**             | `Add(n)`, `Done()`, `Wait()` | `Go(func)`, `Wait() error`  |
| **Goroutine limit** | ❌ No                        | ✅ `SetLimit(n)` (Go 1.20+) |

### Invariants

- `eg.Wait()` **blocks** until all goroutines complete
- `eg.Wait()` returns the **first error** (first non-nil error)
- `errgroup.WithContext(ctx)` → when 1 goroutine errors → ctx auto-cancels
- `eg.SetLimit(n)` limits N goroutines running concurrently (Go 1.20+)

### Failure Modes

| Failure                  | Cause                              | Prevention                   |
| ------------------------ | ---------------------------------- | ---------------------------- |
| **Missed error**         | Not checking `eg.Wait()` return    | Always handle error from Wait |
| **Goroutine leak**       | Goroutine does not check ctx.Done() | Always check ctx in loop     |
| **Too many goroutines**  | Not using SetLimit                 | Use `eg.SetLimit(n)`         |

Errgroup, WaitGroup comparison, invariants — theory is covered. Let us see what cascade error and SetLimit throttle look like visually.

---
## 2. VISUAL

`errgroup` becomes easy to remember only when you see it as a fail-fast workflow rather than a package that replaces `WaitGroup`.

![errgroup fail-fast workflow](./images/05-errgroup-fail-fast-workflow.png)

*The key value of `errgroup` is that it unifies worker start, first error, sibling cancellation, and join point into a single flow.*

### Errgroup Flow

```
                    ┌──────────────────┐
                    │  errgroup.Group  │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         eg.Go(G1)      eg.Go(G2)      eg.Go(G3)
              │              │              │
              │              │         return error ← G3 fails!
              │              │              │
              │         ctx cancel ◀────────┘  (auto)
              │              │
         ctx.Done() ◀────────┘     G1 and G2 receive cancel signal
              │
              ▼
          eg.Wait() → returns G3's error (first error)
```

*Errgroup cascade — G3 returns error → ctx auto-cancels → G1, G2 receive stop signal via ctx.Done(). Wait() returns the first error.*

### Errgroup with SetLimit

```
eg.SetLimit(3)      ← max 3 goroutines at a time

eg.Go(G1) → start  ━━━━━━━━━━━━━ done
  eg.Go(G2) → start  ━━━━━━━━━━━ done
  eg.Go(G3) → start  ━━━━━━━ done
  eg.Go(G4) → WAIT ──────── start ━━━━━━━ done    (waits for G3)
   eg.Go(G5) → WAIT ─────────── start ━━━━━ done   (waits for G1)
```

*SetLimit(3) — G4 and G5 must WAIT until a slot frees up, throttling automatically without a semaphore.*

The diagrams give an overview of error cascade and SetLimit throttle. Now let us implement — starting from parallel API calls, then SetLimit concurrency, then production pipeline, then HTTP fanout + GORM.

---

## 3. CODE

You have seen the flow of signals, requests, and goroutines in **Errgroup**. Now shift to code to check which parts must be written tightly to avoid paying the production price.

---

### Example 1: Basic — Parallel API calls

You call 3 services using `WaitGroup` + error channel. Service 2 returns an error — but the other 2 goroutines keep running, wasting resources. And the error gets swallowed because WaitGroup has no mechanism for returning errors.

`errgroup.WithContext` wraps everything: 1 goroutine returns an error → ctx auto-cancels → other goroutines receive the stop signal → `Wait()` returns the first error.

```go
package main

import (
    "context"
    "fmt"
    "math/rand/v2" // Go 1.22+
    "time"

"golang.org/x/sync/errgroup"
)

func fetchFromService(ctx context.Context, name string) (string, error) {
    // Simulate API call: 100-500ms
    delay := time.Duration(100+rand.IntN(400)) * time.Millisecond

select {
    case <-ctx.Done():
        return "", ctx.Err() // ← cancelled by errgroup
    case <-time.After(delay):
        // 20% chance of failure
        if rand.Float32() < 0.2 {
            return "", fmt.Errorf("%s: service unavailable", name)
        }
        return fmt.Sprintf("%s: OK (%v)", name, delay), nil
    }
}

func main() {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // errgroup.WithContext:
    // - Creates a derived context
    // - When 1 goroutine returns error → ctx auto-cancels
    // - All other goroutines receive the cancel signal
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    eg, ctx := errgroup.WithContext(context.Background())

services := []string{"UserService", "OrderService", "PaymentService"}
    results := make([]string, len(services))

for i, svc := range services {
        i, svc := i, svc // capture loop variable
        eg.Go(func() error {
            result, err := fetchFromService(ctx, svc)
            if err != nil {
                return err // ← errgroup cancels ctx on error
            }
            results[i] = result // ← safe: each goroutine writes to a different index
            return nil
        })
    }

// Wait: blocks until all goroutines complete
    if err := eg.Wait(); err != nil {
        fmt.Println("❌ Failed:", err)
        return
    }

fmt.Println("✅ All services responded:")
    for _, r := range results {
        fmt.Println(" ", r)
    }
}
```

**Achieved**: 3 services called in parallel (3x faster than sequential). 1 service fails → cancels all, returns the first error.

**Caveat**: `results[i]` is safe because each goroutine writes to its own index — no mutex needed. If you need **all errors** (not just the first): use the `multierr` package or collect into a slice.

**Use when**: Calling N services/APIs in parallel with fail-fast semantics — dashboard aggregation, health checks, BFF.

Parallel API calls cover basic error propagation. But when you need to process 50 tasks with only 5 running at once — SetLimit replaces a custom semaphore.

---

### Example 2: Intermediate — SetLimit — Limiting concurrency

Parallel API calls run all at once. But 100 tasks simultaneously = 100 goroutines = overwhelm DB connections, API rate limits. Before Go 1.20, you had to build a semaphore with a buffered channel + acquire/release. `SetLimit(n)` is built-in from Go 1.20 — `Go()` blocks automatically when the limit is reached.

```go
package main

import (
    "context"
    "fmt"
    "time"

"golang.org/x/sync/errgroup"
)

func main() {
    eg, ctx := errgroup.WithContext(context.Background())

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // SetLimit: max 5 goroutines concurrently
    // eg.Go() will BLOCK if the limit is reached
    // Replaces custom semaphore/worker pool
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    eg.SetLimit(5)

for i := range 50 { // Go 1.22+
        i := i
        eg.Go(func() error { // ← blocks if 5 goroutines are already running
            select {
            case <-ctx.Done():
                return ctx.Err()
            default:
            }

fmt.Printf("[Task %2d] Processing...\n", i)
            time.Sleep(200 * time.Millisecond)
            fmt.Printf("[Task %2d] Done ✅\n", i)
            return nil
        })
    }

if err := eg.Wait(); err != nil {
        fmt.Println("Error:", err)
        return
    }
    fmt.Println("All 50 tasks completed!")
}
```

**Achieved**: 50 tasks but only 5 run concurrently. Automatic throttle — no custom semaphore needed.

**Caveat**: `SetLimit` must be called **before** `Go()`. `SetLimit(-1)` = no limit (default). This is a built-in replacement for Tunny worker pool for many simple use cases.

**Use when**: Batch processing, bulk API calls, file processing — where you need to limit concurrent goroutines without a full worker pool.

> **Why `SetLimit` instead of a buffered channel as a semaphore?**
> Before Go 1.20, limiting concurrency required manual work: `sem := make(chan struct{}, N)`, acquire before spawning, release in defer. The downside: boilerplate repeated everywhere, easy to forget release on panic. `SetLimit(N)` embeds this logic into errgroup — `Go()` blocks automatically at the limit, no separate channel needed, and error propagation still works normally.

SetLimit covers throttle. But production needs a full pipeline: producer → errgroup workers → consumer, with nested errgroup for worker coordination.

---

### Example 3: Advanced — Errgroup + Context + Channels — Production Pattern

SetLimit throttles goroutines. But a production pipeline typically has 3 stages: a producer creates jobs, N workers process in parallel, and a consumer collects results. Each stage needs its own error propagation — but all must stop when any stage fails.

Nested errgroup solves this: an outer group for pipeline structure, an inner group for workers.

```go
package main

import (
    "context"
    "fmt"
    "math/rand/v2" // Go 1.22+
    "time"

"golang.org/x/sync/errgroup"
)

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
    defer cancel()

input := make(chan int, 10)
    output := make(chan string, 10)

eg, ctx := errgroup.WithContext(ctx)

// ━━━━━ Producer: create 30 jobs ━━━━━
    eg.Go(func() error {
        defer close(input)
        for i := range 30 { // Go 1.22+
            select {
            case <-ctx.Done():
                return ctx.Err()
            case input <- i:
            }
        }
        return nil
    })

// ━━━━━ Workers: 4 goroutines processing in parallel ━━━━━
    // Use closure to share WaitGroup for workers
    workerEg, workerCtx := errgroup.WithContext(ctx)
    workerEg.SetLimit(4)

eg.Go(func() error {
        for num := range input {
            num := num
            workerEg.Go(func() error {
                select {
                case <-workerCtx.Done():
                    return workerCtx.Err()
                default:
                }

// Simulate work
                duration := time.Duration(50+rand.IntN(200)) * time.Millisecond
                time.Sleep(duration)

// 5% chance of error
                if rand.Float32() < 0.05 {
                    return fmt.Errorf("worker error processing %d", num)
                }

result := fmt.Sprintf("%d² = %d (took %v)", num, num*num, duration)
                select {
                case <-workerCtx.Done():
                    return workerCtx.Err()
                case output <- result:
                }
                return nil
            })
        }

// Wait for all workers to complete, then close output
        err := workerEg.Wait()
        close(output)
        return err
    })

// ━━━━━ Consumer: read and print results ━━━━━
    eg.Go(func() error {
        for result := range output {
            fmt.Println("✅", result)
        }
        return nil
    })

// ━━━━━ Wait for all ━━━━━
    if err := eg.Wait(); err != nil {
        fmt.Println("\n❌ Pipeline error:", err)
    } else {
        fmt.Println("\n✅ Pipeline completed successfully!")
    }
}
```

**Achieved**: Producer → Workers (4 concurrent) → Consumer — full pipeline. 1 worker error → cancels all. 3s context timeout protects the entire pipeline.

**Caveat**: `close(output)` **must** come after `workerEg.Wait()` — waits for all workers to finish sending. Closing early = panic when a worker sends to a closed channel.

**Use when**: Image processing pipelines, ETL batch jobs, multi-stage data transformations — where you need error propagation + concurrency limit + graceful shutdown.

> **Why use nested errgroup (outer + inner) instead of a single errgroup?**
> The outer errgroup manages 3 stages (producer, worker-coordinator, consumer). The inner errgroup (`workerEg`) manages N workers inside stage 2. If you put everything in 1 group: you cannot know when all workers finish to `close(output)` — because `eg.Wait()` also waits for the consumer. Separating them allows: `workerEg.Wait()` → `close(output)` → consumer drains → outer `eg.Wait()` returns. Without this step: the consumer blocks forever or output gets closed early causing a panic.

Production pipeline covers nested errgroup + channels. But when you need real HTTP APIs + DB persistence — errgroup + GORM is the most common pattern in API gateways and BFFs.

---

### Example 4: Expert — HTTP API Fanout + GORM — Aggregate Data from Multiple Services

Nested pipeline uses channels for data flow. But in a real API gateway / BFF, you call 3 real HTTP APIs, aggregate results, then save to DB. Channels are unnecessary here — each goroutine writes to its own variable, and `Wait()` guarantees happens-before.

This is the most common production pattern: errgroup + real HTTP + GORM.

**Components**: 3 services (User, Order, Payment) → aggregate → save DashboardSnapshot.

```go
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "time"

"golang.org/x/sync/errgroup"
    "gorm.io/driver/postgres"
    "gorm.io/gorm"
)

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Models: API responses + GORM destination
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
type UserStats struct {
    TotalUsers  int `json:"total_users"`
    ActiveUsers int `json:"active_users"`
}

type OrderStats struct {
    TotalOrders   int     `json:"total_orders"`
    TotalRevenue  float64 `json:"total_revenue"`
}

type PaymentStats struct {
    PendingCount  int     `json:"pending_count"`
    FailedCount   int     `json:"failed_count"`
    SuccessRate   float64 `json:"success_rate"`
}

// DashboardSnapshot: aggregated result → saved to DB
type DashboardSnapshot struct {
    ID            uint      `gorm:"primarykey;autoIncrement"`
    TotalUsers    int       `gorm:"column:total_users"`
    ActiveUsers   int       `gorm:"column:active_users"`
    TotalOrders   int       `gorm:"column:total_orders"`
    TotalRevenue  float64   `gorm:"column:total_revenue"`
    PaymentSucc   float64   `gorm:"column:payment_success_rate"`
    PendingPay    int       `gorm:"column:pending_payments"`
    SnapshotAt    time.Time `gorm:"column:snapshot_at;index"`
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// fetchJSON: generic HTTP GET + JSON decode
// Reusable for any API call — DRY principle
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
func fetchJSON[T any](ctx context.Context, client *http.Client, url string) (T, error) {
    var result T
    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return result, fmt.Errorf("create request: %w", err)
    }

resp, err := client.Do(req)
    if err != nil {
        return result, fmt.Errorf("fetch %s: %w", url, err)
    }
    defer resp.Body.Close()

if resp.StatusCode != http.StatusOK {
        return result, fmt.Errorf("API %s returned %d", url, resp.StatusCode)
    }

if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
        return result, fmt.Errorf("decode %s: %w", url, err)
    }
    return result, nil
}

func aggregateDashboard(ctx context.Context, db *gorm.DB) error {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // errgroup.WithContext: cancel all if 1 API fails
    // SetLimit(3): only 3 goroutines (1 per API call)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    eg, egCtx := errgroup.WithContext(ctx)
    eg.SetLimit(3)

client := &http.Client{Timeout: 5 * time.Second}

// Results — each goroutine writes to its own variable → NO RACE
    var users UserStats
    var orders OrderStats
    var payments PaymentStats

// ━━━ Goroutine 1: Fetch User Stats ━━━
    eg.Go(func() error {
        var err error
        users, err = fetchJSON[UserStats](egCtx, client, "http://user-service:8080/api/stats")
        if err != nil {
            return fmt.Errorf("user service: %w", err)
        }
        log.Printf("[Users] Total=%d, Active=%d", users.TotalUsers, users.ActiveUsers)
        return nil
    })

// ━━━ Goroutine 2: Fetch Order Stats ━━━
    eg.Go(func() error {
        var err error
        orders, err = fetchJSON[OrderStats](egCtx, client, "http://order-service:8080/api/stats")
        if err != nil {
            return fmt.Errorf("order service: %w", err)
        }
        log.Printf("[Orders] Total=%d, Revenue=$%.2f", orders.TotalOrders, orders.TotalRevenue)
        return nil
    })

// ━━━ Goroutine 3: Fetch Payment Stats ━━━
    eg.Go(func() error {
        var err error
        payments, err = fetchJSON[PaymentStats](egCtx, client, "http://payment-service:8080/api/stats")
        if err != nil {
            return fmt.Errorf("payment service: %w", err)
        }
        log.Printf("[Payments] Success=%.1f%%, Pending=%d", payments.SuccessRate*100, payments.PendingCount)
        return nil
    })

// ━━━ Wait: all 3 goroutines finish (or 1 fails → cancel rest) ━━━
    if err := eg.Wait(); err != nil {
        return fmt.Errorf("aggregate failed: %w", err)
    }

// ━━━ Save aggregated result to DB ━━━
    snapshot := DashboardSnapshot{
        TotalUsers:   users.TotalUsers,
        ActiveUsers:  users.ActiveUsers,
        TotalOrders:  orders.TotalOrders,
        TotalRevenue: orders.TotalRevenue,
        PaymentSucc:  payments.SuccessRate,
        PendingPay:   payments.PendingCount,
        SnapshotAt:   time.Now(),
    }

if err := db.WithContext(ctx).Create(&snapshot).Error; err != nil {
        return fmt.Errorf("save snapshot: %w", err)
    }

log.Printf("✅ Dashboard snapshot saved (ID: %d)", snapshot.ID)
    return nil
}

func main() {
    dsn := "host=localhost user=app dbname=dashboard port=5432 sslmode=disable"
    db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
    if err != nil {
        log.Fatal(err)
    }
    db.AutoMigrate(&DashboardSnapshot{})

ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()

if err := aggregateDashboard(ctx, db); err != nil {
        log.Fatal("❌", err)
    }
}
```

**Achieved**: 3 API calls in parallel — latency = max(3 calls) instead of sum. End-to-end error propagation: HTTP → errgroup → GORM → DB. Each goroutine writes to its own variable — no race condition.

**Caveat**: `http.Client` is thread-safe — share across goroutines. Errgroup cancels on first failure — if you need retry on individual calls, wrap each with `avast/retry-go`. If fanning out 100 APIs → `SetLimit(10)` to avoid overloading downstream.

**Use when**: API gateway aggregation, dashboard data collection, BFF pattern — where you need to call N services in parallel then merge results.

> **Why can each goroutine write to its own variable (`users`, `orders`, `payments`) without a mutex?**
> Each goroutine writes to exactly 1 separate variable — no other goroutine reads or writes the same variable concurrently. `eg.Wait()` waits for all goroutines to finish before reading — creating a happens-before relationship. Using a shared slice (`results[i]`) is also safe since each index is separate. But using a shared map or appending to the same slice → needs a mutex because concurrent writes are not safe.

You now know parallel calls, SetLimit, nested pipeline, and HTTP fanout. Here comes the dangerous part: closing a channel too early and goroutine panics — traps set up from the beginning of this article.

---

## 4. PITFALLS

The correct mechanism of **Errgroup** is in place. The traps below are where people get timing, ownership, or evidence wrong — and only realize it when the incident has already exploded.

| # | Severity | Mistake | Consequence | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Fatal | **Close channel too early** | Panic when worker sends to closed channel | Close AFTER `egWorkers.Wait()` |
| 2 | 🔴 Fatal | **Race on shared slice** | Data corruption, index out of range | Each G writes its own index, or use mutex |
| 3 | 🟡 Common | **Forget to handle Wait() error** | Error gets swallowed, hidden bug | Always: `if err := eg.Wait(); err != nil` |
| 4 | 🟡 Common | **Goroutine does not check ctx** | Goroutine keeps running despite cancel | `select { case <-ctx.Done() }` in loop |
| 5 | 🟡 Common | **SetLimit too large** | Overwhelm downstream resources | Match with resource capacity (CPU, DB connections) |

You have covered parallel calls, SetLimit, nested pipeline, HTTP fanout, and the close/race/panic traps. The resources below help you go deeper.

---

## 5. REF

| Resource | Type | Link | Notes |
| --- | --- | --- | --- |
| errgroup package | Official docs | [pkg.go.dev/golang.org/x/sync/errgroup](https://pkg.go.dev/golang.org/x/sync/errgroup) | API reference |
| Go Blog — Pipelines | Core team blog | [go.dev/blog/pipelines](https://go.dev/blog/pipelines) | Pipeline + cancellation |
| errgroup source code | Source code | [cs.opensource.google/go/x/sync](https://cs.opensource.google/go/x/sync/+/master:errgroup/) | Implementation details |

---

## 6. RECOMMEND

You just went from parallel calls (basic) → throttled processing (SetLimit) → nested pipeline (producer/worker/consumer) → real HTTP+GORM fanout. From here, expand based on orchestration complexity.

| Next step | When | Reason | File/Link |
| --- | --- | --- | --- |
| **sourcegraph/conc ErrorPool** | Collect ALL errors | Panic recovery built-in | [13-conc.md](./13-conc.md) |
| **errgroup.SetLimit(n)** | Simple limiting | Replaces semaphore | `golang.org/x/sync/errgroup` |
| **x/sync/semaphore** | Weighted limiting | Mixed workloads | [10-semaphore.md](./10-semaphore.md) |
| **GORM batch** | Parallel batch insert | `errgroup + db.CreateInBatches` | [../orm/02-crud.md](../orm/02-crud.md) |
| **HTTP fanout** | Parallel API calls | Shared error handling | `errgroup + http.Client` |
| **Asynq task groups** | Distributed | Cross-process error propagation | [15-asynq.md](./15-asynq.md) |

---

**Links**: [← sync.Pool](./04-sync-pool.md) · [→ Fan-out / Fan-in](./06-fan-out-fan-in.md)
