<!-- tags: golang -->
# 08 — Worker Pool & Tunny

> **Pattern**: Limit the number of goroutines processing in parallel. Tunny = worker pool library for Go.

📅 Created: 2026-03-20 · 🔄 Updated: 2026-04-19 · ⏱️ 15 min read

| Aspect         | Detail                                                     |
| -------------- | ---------------------------------------------------------- |
| **Concept**    | Worker Pool — fixed goroutine pool, job queue, result      |
| **Use case**   | Rate limiting, resource protection, batch processing       |
| **Go stdlib**  | `chan`, `sync.WaitGroup` (DIY) or `github.com/Jeffail/tunny` |
| **Key insight**| Pool = bounded concurrency + reuse — prevents goroutine explosion |

---

## 1. DEFINE

Fan-out spawns a goroutine per task. At 100K tasks, that means 100K goroutines — each consuming stack memory, scheduler time, and potentially file descriptors. A worker pool caps the goroutine count to N, feeds tasks through a shared channel, and reuses workers across the entire workload. Tunny adds a clean API on top: bounded pool, synchronous dispatch, and graceful shutdown.

Your API server receives 1,000 requests/second and each request spawns 1 goroutine calling an external service. 1,000 concurrent goroutines → the external service is overwhelmed, returning 429 Too Many Requests. You need to limit down to 10 concurrent calls. Worker Pool is the answer: 10 fixed workers, jobs queue up, each worker picks a job from the queue. But there is a trap: `Process()` without a timeout = caller goroutine blocks forever when no worker is available. That trap will surface in PITFALLS.

### Worker Pool

**Worker Pool** is a pattern that pre-creates N worker goroutines. Jobs are sent via a channel, and an idle worker picks up the next job. Limits concurrency to avoid overwhelming resources (CPU, memory, DB connections).

### Tunny

**[Tunny](https://github.com/Jeffail/tunny)** is a Go library providing a worker pool with:

- **Fixed pool size**: N fixed workers
- **Blocking `Process()`**: caller blocks until a worker is available
- **Timeout `ProcessTimed()`**: returns error if no worker is available within the timeout
- **Context `ProcessCtx()`**: cancels when context cancels

### Comparing Worker Pool approaches

| Approach                      | Pros                           | Cons                     |
| ----------------------------- | ------------------------------ | ------------------------ |
| **Channel-based (DIY)**       | Full control, no dependency    | Must handle many things yourself |
| **Tunny**                     | Production-ready, timeout, ctx | External dependency      |
| **errgroup.SetLimit**         | Built-in, error handling       | Does not reuse goroutines |
| **Semaphore (chan struct{})** | Simple                         | Not a true pool          |

### Invariants

- Pool size should = **resources available** (CPU cores, DB pool size)
- `Process()` is **synchronous** — caller blocks until result returns
- Worker goroutines **reuse** — created once, process many jobs
- `defer pool.Close()` — release workers when done

### Failure Modes

| Failure               | Cause                                   | Prevention                                |
| --------------------- | --------------------------------------- | ----------------------------------------- |
| **Pool too small**    | Jobs queue up, latency increases        | Benchmark, tune pool size                 |
| **Pool too large**    | Context switch overhead, resource waste | Start with NumCPU, scale gradually        |
| **Forget Close()**    | Workers leak forever                    | `defer pool.Close()`                      |
| **Process() timeout** | No worker available                     | Use `ProcessTimed()` or `ProcessCtx()`    |

Worker pool, Tunny, DIY, invariants — theory is covered. Let us see what job flow and pool mechanics look like visually.

---
## 2. VISUAL

The primary visual for this article is the bounded-flow map: when a job must enter the queue, when worker count truly becomes admission control, and why pool shutdown must be part of the design.

![Worker pool with Tunny](./images/08-worker-pool-tunny-bounded-flow.png)

*If you think of Tunny as "goroutines managed for me", you miss the key point: the pool exists to turn saturation into a visible signal.*

### Worker Pool Architecture

```
                    ┌────────────────────────────────────┐
                    │         Worker Pool (N=4)          │
                    │                                    │
  Job Queue   ──────┤  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ │
  (channel)         │  │ W1   │ │ W2   │ │ W3   │ │ W4   │ │
                    │  │ busy │ │ idle │ │ busy │ │ idle │ │
  Process(job) ─────┤  └──────┘ └──────┘ └──────┘ └──────┘ │
  → block until     │         ▲                    ▲       │
    worker free     │         │ W2 picks up job    │       │
                    └─────────┼────────────────────┼───────┘
                              │                    │
                    Result ◀──┘      Result ◀──────┘
```

### Tunny vs DIY workflow

```
Tunny:
  caller ── pool.Process(data) ── [BLOCK] ── result
                     │
              worker picks up
              processes
              returns result

DIY (Channel):
  caller ── jobs <- data ── worker reads ── results <- output ── caller reads
            (may block)      (goroutine)     (need separate channel)
```

The diagrams give an overview of job flow and DIY vs Tunny. Now let us implement — starting from DIY channel-based, then Tunny basic, then ProcessCtx/Timed, then Tunny + sync.Pool + errgroup combo.

---

## 3. CODE

The visual of **Worker Pool & Tunny** gives you the big picture. Code is where decisions about cancellation, ownership, or sequencing become real behavior.

---

### Example 1: Basic — DIY Worker Pool — Channel-based

1,000 requests/second, each request spawns 1 goroutine calling an external service. 1,000 concurrent goroutines → the external service is overwhelmed. Need to limit to 4 fixed workers, jobs queue up. DIY channel-based is the way to understand the core concept before using a library.

```go
package main

import (
    "fmt"
    "math/rand/v2" // Go 1.22+
    "sync"
    "time"
)

// Job describes 1 unit of work
type Job struct {
    ID    int
    Input int
}

// Result describes the output after a worker processes a job
type Result struct {
    JobID    int
    WorkerID int
    Output   int
    Duration time.Duration
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// worker: goroutine running continuously
// - Reads jobs from channel (blocks when no jobs)
// - Processes → sends result
// - Stops when jobs channel closes (range auto-stops)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
func worker(id int, jobs <-chan Job, results chan<- Result, wg *sync.WaitGroup) {
    defer wg.Done()
    for job := range jobs {
        start := time.Now()

// Simulate CPU work
        time.Sleep(time.Duration(50+rand.IntN(200)) * time.Millisecond)
        output := job.Input * job.Input

results <- Result{
            JobID:    job.ID,
            WorkerID: id,
            Output:   output,
            Duration: time.Since(start),
        }
    }
    fmt.Printf("[Worker %d] No more jobs, exiting\n", id)
}

func main() {
    const numWorkers = 4
    const numJobs = 15

jobs := make(chan Job, numJobs)
    results := make(chan Result, numJobs)

// ━━━ Start worker pool ━━━
    var wg sync.WaitGroup
    for w := 1; w <= numWorkers; w++ {
        wg.Add(1)
        go worker(w, jobs, results, &wg)
    }

// ━━━ Submit jobs ━━━
    for j := 1; j <= numJobs; j++ {
        jobs <- Job{ID: j, Input: j}
    }
    close(jobs) // ← signal workers: no more jobs

// ━━━ Close results when all workers done ━━━
    go func() {
        wg.Wait()
        close(results)
    }()

// ━━━ Consume results ━━━
    for r := range results {
        fmt.Printf("Job %2d: %d² = %3d  [Worker %d, %v]\n",
            r.JobID, r.JobID, r.Output, r.WorkerID, r.Duration)
    }
}
```

**Achieved**: 15 jobs processed by 4 workers. Workers pick up the next job when idle — natural load balancing. Faster workers handle more jobs.

**Caveat**: `close(jobs)` signals workers to stop via `range`. `close(results)` must come after `wg.Wait()`. DIY pool is good for learning, but Tunny is better for production (timeout, ctx, reuse).

**Use when**: Learning the core concept, or when you want full control without adding a dependency.

DIY pool covers basics. But Tunny has goroutine reuse, type-safe API, and built-in Process/ProcessCtx — production-ready without boilerplate.

---

### Example 2: Intermediate — Tunny — Basic Usage

DIY pool requires building jobs/results channels, WaitGroup, close logic — boilerplate repeated everywhere. Tunny wraps it all: `NewFunc(size, handler)` + `Process(data)` + `Close()`. Goroutine reuse built-in, zero alloc for goroutine creation.

```go
package main

import (
    "fmt"
    "math/rand/v2" // Go 1.22+
    "sync"
    "time"

"github.com/Jeffail/tunny"
)

func main() {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // tunny.NewFunc: create pool with function handler
    //   - Arg 1: pool size (number of workers)
    //   - Arg 2: function to process each job
    //   - Returns interface{} → needs type assertion
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pool := tunny.NewFunc(4, func(payload interface{}) interface{} {
        n := payload.(int)
        // Simulate work
        time.Sleep(time.Duration(100+rand.IntN(200)) * time.Millisecond)
        return n * n
    })
    defer pool.Close() // ← IMPORTANT: release workers

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // pool.Process(data):
    // - BLOCKING: caller waits until worker finishes
    // - If all workers busy → caller waits for a free worker
    // - Returns: result from worker function
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    var wg sync.WaitGroup
    for i := 1; i <= 20; i++ {
        wg.Add(1)
        go func(n int) {
            defer wg.Done()
            result := pool.Process(n) // ← blocking call
            fmt.Printf("%d² = %d\n", n, result.(int))
        }(i)
    }
    wg.Wait()

fmt.Println("\nPool size:", pool.GetSize()) // 4
}
```

**Achieved**: Simple API: `NewFunc` + `Process` + `Close`. 20 concurrent callers but only 4 workers running at a time. `Process()` is blocking — the caller automatically waits for a free worker.

**Caveat**: `Process()` returns `interface{}` → must type assert (type-unsafe). `pool.Close()` releases workers — **ALWAYS `defer Close()`**. Workers reuse goroutines — no new goroutine created for each job.

**Use when**: Simple production worker pools — batch processing, API rate limiting, background jobs.

> **Why does Tunny use goroutine reuse instead of spawning a new one each time?**
> Each goroutine costs ~2KB stack (can grow to MB). Spawning 10K goroutines/s = 10K alloc/s = GC pressure. Tunny keeps N goroutines pre-created; each goroutine blocks waiting for a job via channel. Receives job → processes → returns to wait. Zero alloc for goroutine creation.

Tunny basic covers reuse. But when the caller needs timeout or context cancellation — `ProcessCtx` and `ProcessTimed` handle unavailable workers or workers running too long.

---

### Example 3: Advanced — Tunny — ProcessCtx + ProcessTimed

Tunny basic `Process()` blocks indefinitely when no worker is available. In an HTTP handler, the caller blocking forever = request timeout not handled. `ProcessTimed` returns error after N ms. `ProcessCtx` integrates with request context — client disconnect = worker stop.

```go
package main

import (
    "context"
    "fmt"
    "math/rand/v2" // Go 1.22+
    "time"

"github.com/Jeffail/tunny"
)

func main() {
    // Small pool (2 workers) to easily observe timeout/busy
    pool := tunny.NewFunc(2, func(payload interface{}) interface{} {
        n := payload.(int)
        // Simulate heavy work: 500ms - 2s
        duration := time.Duration(500+rand.IntN(1500)) * time.Millisecond
        time.Sleep(duration)
        return fmt.Sprintf("%d² = %d (took %v)", n, n*n, duration)
    })
    defer pool.Close()

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // ProcessTimed: timeout if no worker available within N ms
    // Returns error on timeout
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    fmt.Println("=== ProcessTimed (timeout 1s) ===")
    for i := 1; i <= 5; i++ {
        go func(n int) {
            result, err := pool.ProcessTimed(n, time.Second)
            if err != nil {
                fmt.Printf("❌ Job %d: %v\n", n, err) // timeout
                return
            }
            fmt.Printf("✅ Job %d: %s\n", n, result.(string))
        }(i)
    }
    time.Sleep(3 * time.Second) // wait for completion

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // ProcessCtx: cancel via context
    // Integrates with HTTP request context, parent context...
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    fmt.Println("\n=== ProcessCtx (context timeout 800ms) ===")
    ctx, cancel := context.WithTimeout(context.Background(), 800*time.Millisecond)
    defer cancel()

result, err := pool.ProcessCtx(ctx, 42)
    if err != nil {
        fmt.Printf("❌ ProcessCtx: %v\n", err) // context deadline exceeded
    } else {
        fmt.Printf("✅ ProcessCtx: %s\n", result.(string))
    }
}
```

**Achieved**: `ProcessTimed` returns error on timeout. `ProcessCtx` integrates context — HTTP handler cancel = worker stop.

**Caveat**: Timeout = total time (waiting for worker + processing). The worker goroutine still runs after the caller times out — only the result is discarded. Use `ProcessCtx` in HTTP handlers (already have `r.Context()`).

**Use when**: HTTP handlers, API gateways, anywhere the caller must not block indefinitely.

> **Why does the worker still run after the caller times out?**
> Tunny uses channel communication between caller and worker. When the caller times out, it stops waiting for the result — but the worker does not know (no ctx propagation into the worker function). `ProcessCtx` partially solves this: it passes ctx into the worker so the worker can check `ctx.Done()`. But the check logic is the developer's responsibility — Tunny does not auto-kill the goroutine.

ProcessCtx/Timed covers timeout. But production needs combining Tunny (concurrency) + sync.Pool (memory) + errgroup (error handling) = triple-layer pattern.

---

### Example 4: Expert — Worker Pool Manager — Tunny + sync.Pool + Errgroup

ProcessCtx covers timeout. But production needs 3 dimensions: Tunny (bounded concurrency) + sync.Pool (memory reuse) + errgroup (error propagation + context cancel). `PoolManager` wraps all 3 into 1 abstraction.

```go
package main

import (
    "context"
    "fmt"
    "math/rand/v2" // Go 1.22+
    "sync"
    "time"

"github.com/Jeffail/tunny"
    "golang.org/x/sync/errgroup"
)

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// PoolManager: manages worker pool + buffer pool
// - Tunny: limits concurrency
// - sync.Pool: reuses buffers (reduces GC)
// - Errgroup: error propagation + context cancel
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
type PoolManager struct {
    workerPool *tunny.Pool
    bufferPool *sync.Pool
}

func NewPoolManager(workerCount int, bufferSize int) *PoolManager {
    pm := &PoolManager{
        bufferPool: &sync.Pool{
            New: func() interface{} {
                return make([]byte, bufferSize)
            },
        },
    }

pm.workerPool = tunny.NewFunc(workerCount, func(payload interface{}) interface{} {
        task := payload.(Task)

// GET buffer from pool
        buf := pm.bufferPool.Get().([]byte)
        defer pm.bufferPool.Put(buf) // PUT back when done

// Simulate processing with buffer
        copy(buf, []byte(fmt.Sprintf("task-%d-data", task.ID)))
        time.Sleep(time.Duration(50+rand.IntN(200)) * time.Millisecond)

// 3% chance of error
        if rand.Float32() < 0.03 {
            return TaskResult{ID: task.ID, Error: fmt.Errorf("processing failed")}
        }

return TaskResult{
            ID:     task.ID,
            Output: fmt.Sprintf("Processed: %s", buf[:20]),
        }
    })

return pm
}

func (pm *PoolManager) Close() {
    pm.workerPool.Close()
}

type Task struct {
    ID int
}

type TaskResult struct {
    ID     int
    Output string
    Error  error
}

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()

// ━━━ Create Pool Manager: 4 workers, 1KB buffers ━━━
    pm := NewPoolManager(4, 1024)
    defer pm.Close()

eg, ctx := errgroup.WithContext(ctx)
    results := make(chan TaskResult, 50)

// ━━━ Submit 30 tasks via errgroup ━━━
    for i := 1; i <= 30; i++ {
        i := i
        eg.Go(func() error {
            // ProcessCtx: cancel when context cancels
            raw, err := pm.workerPool.ProcessCtx(ctx, Task{ID: i})
            if err != nil {
                return fmt.Errorf("task %d: %w", i, err)
            }

result := raw.(TaskResult)
            if result.Error != nil {
                return fmt.Errorf("task %d: %w", i, result.Error)
            }

results <- result
            return nil
        })
    }

// ━━━ Collect results ━━━
    go func() {
        eg.Wait()
        close(results)
    }()

// ━━━ Print results ━━━
    success := 0
    for r := range results {
        success++
        if success <= 5 {
            fmt.Printf("✅ Task %2d: %s\n", r.ID, r.Output)
        }
    }

if err := eg.Wait(); err != nil {
        fmt.Printf("\n❌ Pipeline error: %v\n", err)
    }
    fmt.Printf("\n📊 Results: %d/%d tasks succeeded\n", success, 30)
}
```

**Achieved**: `PoolManager` wraps: Tunny (concurrency) + sync.Pool (memory) + errgroup (errors). 30 tasks, 4 concurrent, buffer reuse, context-aware.

**Caveat**: `PoolManager` should be a singleton or dependency-injected. `pm.Close()` releases workers — ALWAYS cleanup. 3 patterns solve 3 different dimensions: concurrency, memory, error handling.

**Use when**: Production image processing, batch data jobs, API aggregation — where you need bounded concurrency + memory reuse + coordinated error handling.

> **Why combine 3 patterns (Tunny + sync.Pool + errgroup) instead of just 1?**
> Each pattern solves 1 different dimension: Tunny = bounded goroutines (concurrency), sync.Pool = reused buffers (memory), errgroup = coordinated cancellation (error handling). Using only 1: Tunny does not solve memory waste, sync.Pool does not limit concurrency, errgroup does not reuse goroutines. Combining all 3 = production-grade.

You now know DIY, Tunny basic, ProcessCtx, and the triple-combo. Here comes the dangerous part: Process() blocking forever and forgetting Close() — traps set up from the beginning of this article.

---

## 4. PITFALLS

From here, with **Worker Pool & Tunny**, the focus is no longer making it run, but avoiding the kinds of execution that seem fine while silently creating operational debt.

| # | Severity | Mistake | Consequence | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Fatal | **Forget `pool.Close()`** | Worker goroutines leak forever | `defer pool.Close()` |
| 2 | 🟡 Common | **Pool size too large** | Overhead > benefit | Start NumCPU, benchmark |
| 3 | 🟡 Common | **Process() blocks forever** | Caller goroutine stuck | Use ProcessTimed or ProcessCtx |
| 4 | 🔵 Minor | **Type assertion fail** | Tunny returns interface{} — runtime panic | Check type or use wrapper |

You have covered DIY, Tunny, ProcessCtx, triple-combo, and the block/leak/type traps. The resources below help you go deeper.

---

## 5. REF

| Resource | Type | Link | Notes |
| --- | --- | --- | --- |
| Tunny GitHub | Library | [github.com/Jeffail/tunny](https://github.com/Jeffail/tunny) | Source + README |
| Tunny GoDoc | Official docs | [pkg.go.dev/github.com/Jeffail/tunny](https://pkg.go.dev/github.com/Jeffail/tunny) | API reference |
| Go Worker Pool Pattern | Tutorial | [gobyexample.com/worker-pools](https://gobyexample.com/worker-pools) | Basic pattern |

---

## 6. RECOMMEND

You just went from DIY channel-based → Tunny basic → ProcessCtx/Timed (timeout) → triple-combo (Tunny + sync.Pool + errgroup). From here, expand based on scale or distributed needs.

| Next step | When | Reason | File/Link |
| --- | --- | --- | --- |
| **Ants** | High-perf pool | Auto-scale, pre-allocate, panic recovery | [12-ants.md](./12-ants.md) |
| **conc ResultPool** | Typed results | Generic results, no interface{} | [13-conc.md](./13-conc.md) |
| **Asynq** | Distributed workers | Cross-process worker pool with Redis | [15-asynq.md](./15-asynq.md) |
| **sync.Pool** | Buffer reuse | Workers reuse goroutines + Pool reuses buffers | [04-sync-pool.md](./04-sync-pool.md) |
| **x/time/rate** | Rate limiting | Token bucket rate limiter | `golang.org/x/time/rate` |
| **Gin/Echo** | HTTP handler pool | Limit concurrent request processing | Web framework |

---

**Links**: [← Pipeline](./07-pipeline.md) · [→ Or-done & Tee Channels](./09-or-done-tee-channels.md)
