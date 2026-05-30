<!-- tags: golang -->
# 06 — Fan-out / Fan-in

> **Pattern**: Distribute work across multiple workers (fan-out), merge results into one place (fan-in).

📅 Created: 2026-03-20 · 🔄 Updated: 2026-04-19 · ⏱️ 15 min read

| Aspect         | Detail                                                          |
| -------------- | --------------------------------------------------------------- |
| **Concept**    | Fan-out (1→N workers), Fan-in (N→1 merge)                     |
| **Use case**   | Parallel processing, batch I/O, aggregation                     |
| **Go stdlib**  | `chan`, `sync.WaitGroup`, `select`                               |
| **Key insight**| Order is NOT preserved — whoever finishes first pushes first (non-deterministic) |

---

## 1. DEFINE

A single goroutine processes items from a channel. Throughput is limited by its speed. Fan-out splits the work across N workers consuming the same channel; fan-in merges their results back into one stream. The pattern is simple, but the shutdown path is not: if even one worker leaks, memory grows silently until OOM.

You have 1,000 images to resize. Sequential processing: 500ms/image × 1,000 = 500 seconds. The machine has 8 cores but uses only 1. Fan-out solves this: split 1,000 images across 8 workers processing in parallel, and when done, merge results into one place (fan-in). Time drops to ~63 seconds. But there is a trap: unbounded fan-out = 100K URLs → 100K goroutines → OOM. Worker count must match resource capacity. That trap will surface in PITFALLS.

### Fan-out vs Fan-in

| Concept     | Direction | Description                                              |
| ----------- | --------- | -------------------------------------------------------- |
| **Fan-out** | 1 → N     | 1 input channel → N worker goroutines processing in parallel |
| **Fan-in**  | N → 1     | N source channels → merge into 1 output channel         |

### Use cases

- **Fan-out**: CPU-intensive tasks (image processing, hash), I/O-bound tasks (HTTP requests, DB queries)
- **Fan-in**: Aggregate results from multiple sources, merge multiple log streams

### Invariants

- **Order** is NOT preserved — whichever goroutine finishes first pushes first (non-deterministic)
- Output channel must be **closed at the right time** — after ALL workers complete
- Use `sync.WaitGroup` or `errgroup` to track workers

### Failure Modes

| Failure              | Cause                                 | Prevention                          |
| -------------------- | ------------------------------------- | ----------------------------------- |
| **Close output early** | Close before workers finish → panic | `wg.Wait()` then `close()`          |
| **Goroutine leak**   | Worker blocks on full output channel  | Buffer output or check ctx          |
| **Memory spike**     | Fan-out too many workers              | Limit workers = `runtime.NumCPU()`  |

Fan-out, fan-in, invariants — theory is covered. Let us see what data flow and merge patterns look like visually.

---
## 2. VISUAL

If you stop at the definition of **Fan-out / Fan-in**, you can easily misjudge where ownership and merge logic start becoming dangerous. The PNG diagram below is the primary visual; the ASCII views below serve as supporting detail.

![Fan-out / fan-in flow](./images/06-fan-out-fan-in-flow-map.png)

*The main diagram emphasizes ingress ownership, split to worker set, correct merge, then draining cleanly to avoid blocked sends or partial shutdown.*

### Fan-out: 1 → N

```
                    Fan-out
                    ┌──────────▶ Worker 1 ──▶ result
                    │
  input channel ────┼──────────▶ Worker 2 ──▶ result
                    │
                    └──────────▶ Worker 3 ──▶ result

1 channel, multiple goroutines reading (Go channel is safe for multi-reader)
```

*Fan-out — 1 input channel is read by multiple workers; each worker processes 1 item independently.*

### Fan-in: N → 1

```
  Source 1 ────┐
               │
  Source 2 ────┼──────────▶ merge() ──▶ 1 output channel
               │
  Source 3 ────┘

N channels → 1 goroutine merge → 1 output
```

*Fan-in — merge multiple source channels into 1 output, combining results from multiple sources.*

### Combined Fan-out + Fan-in

```
                   Fan-out                          Fan-in
               ┌──▶ Worker 1 ──┐
               │                │
  input ───────┼──▶ Worker 2 ──┼──── merge() ────▶ output
               │                │
               └──▶ Worker 3 ──┘

Timing (non-deterministic):
  W1: ━━━━━━━━━━━ done (300ms)           output: W2, W3, W1
  W2: ━━━━━ done (150ms)                 (whoever finishes first pushes first)
  W3: ━━━━━━━ done (220ms)
```

*Combined fan-out + fan-in — 3 workers process in parallel; results merge in completion order (non-deterministic).*

The diagrams give an overview of data flow and merge patterns. Now let us implement — starting from fan-out workers, then fan-in merge, then the complete pipeline with context.

---

## 3. CODE

The visual of **Fan-out / Fan-in** gives you the big picture. Code is where decisions about cancellation, ownership, or sequencing become real behavior.

---

### Example 1: Basic — Fan-out — Multiple workers reading from 1 channel

1,000 images to resize. Sequential = 500 seconds. The machine has 8 cores but uses only 1. Fan-out solves this: split jobs across N workers reading from 1 channel. Go channels are thread-safe for multi-reader — each job is processed by exactly 1 worker.

```go
package main

import (
    "fmt"
    "math/rand/v2" // Go 1.22+
    "sync"
    "time"
)

func worker(id int, jobs <-chan int, results chan<- string, wg *sync.WaitGroup) {
    defer wg.Done()
    for job := range jobs {
        // ━━━ Simulate CPU work ━━━
        duration := time.Duration(50+rand.IntN(200)) * time.Millisecond
        time.Sleep(duration)

results <- fmt.Sprintf("Worker %d: job %d → %d² = %d (took %v)",
            id, job, job, job*job, duration)
    }
}

func main() {
    const numWorkers = 4
    const numJobs = 20

jobs := make(chan int, numJobs)
    results := make(chan string, numJobs)

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Fan-out: 4 workers reading from 1 channel
    // Go channel is thread-safe for multi-reader:
    // each job is processed by EXACTLY 1 worker
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    var wg sync.WaitGroup
    for w := 1; w <= numWorkers; w++ {
        wg.Add(1)
        go worker(w, jobs, results, &wg)
    }

// Producer: send 20 jobs
    for j := 1; j <= numJobs; j++ {
        jobs <- j
    }
    close(jobs) // ← signal workers to stop

// Goroutine: close results when all workers finish
    go func() {
        wg.Wait()
        close(results)
    }()

// Consumer: read results
    for r := range results {
        fmt.Println(r)
    }
}
```

**Achieved**: 20 jobs distributed evenly across 4 workers. Output order is non-deterministic — whichever worker finishes first pushes first.

**Caveat**: `close(jobs)` is critical: workers using `range` stop automatically when the channel closes. `close(results)` must come **after** `wg.Wait()` — closing early = panic.

**Use when**: CPU-intensive batch processing (image resize, hash), I/O-bound tasks (parallel HTTP requests, DB queries).

Fan-out covers work distribution. But when multiple sources send data — 3 API streams, log files — you need fan-in to merge into 1 channel.

---

### Example 2: Intermediate — Fan-in — Merge multiple channels into 1

Fan-out splits 1 source across N workers. But when multiple sources send data — 3 API streams, log files from multiple servers — the consumer wants to read from 1 place. `merge()` is the fan-in function: combining N channels into 1.

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// merge: fan-in N channels → 1 output channel
//
// How it works:
// - 1 goroutine per source channel (reads + sends to output)
// - WaitGroup counts all sources done → close output
// - Output is <-chan: caller can only read, not write
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
func merge(channels ...<-chan string) <-chan string {
    out := make(chan string)
    var wg sync.WaitGroup

// 1 goroutine per source channel
    for _, ch := range channels {
        wg.Add(1)
        go func(c <-chan string) {
            defer wg.Done()
            for val := range c {
                out <- val // forward all values to output
            }
        }(ch)
    }

// Goroutine: close output when all sources are closed
    go func() {
        wg.Wait()
        close(out)
    }()

return out // ← returns immediately, data streams lazily
}

// Simulate 1 data source
func source(name string, count int, interval time.Duration) <-chan string {
    ch := make(chan string)
    go func() {
        defer close(ch)
        for i := 1; i <= count; i++ {
            time.Sleep(interval)
            ch <- fmt.Sprintf("[%s] item %d", name, i)
        }
    }()
    return ch
}

func main() {
    // ━━━ 3 sources with different speeds ━━━
    fast := source("Fast", 5, 50*time.Millisecond)     // 50ms/item
    medium := source("Medium", 3, 150*time.Millisecond) // 150ms/item
    slow := source("Slow", 2, 300*time.Millisecond)     // 300ms/item

// ━━━ Fan-in: merge all into 1 stream ━━━
    merged := merge(fast, medium, slow)

for msg := range merged {
        fmt.Println(msg)
    }
    fmt.Println("\nAll sources drained!")
}
```

**Achieved**: 3 sources merge into 1 output — consumer reads from 1 place. Output is interleaved: Fast items arrive first due to shorter interval. `merge()` returns a lazy channel.

**Caveat**: N sources = N goroutines inside merge — be careful with large numbers. `merge()` is reusable for any `<-chan string`.

**Use when**: Aggregate logs from multiple servers, merge API stream responses, combine sensor data.

> **Why does merge need WaitGroup + close instead of just select?**
> `select` reads from only 1 channel at a time. Merging N channels requires N goroutines — each goroutine reads 1 source and sends to the shared output. WaitGroup counts when all N goroutines finish → close output → consumer knows all data is done. Without WaitGroup: closing output early → panic when an unfinished goroutine still sends.

Fan-out and fan-in separately cover each direction. Combining both in a complete pipeline with context cancellation = production pattern.

---

### Example 3: Advanced — Fan-out + Fan-in — Complete pipeline

Fan-out and fan-in separately cover 2 directions. Combining both: producer generates URLs → N workers fetch in parallel (fan-out) → merge results into 1 stream (fan-in) → consumer drains. Context timeout protects the entire pipeline.

```go
package main

import (
    "context"
    "fmt"
    "math/rand/v2" // Go 1.22+
    "runtime"
    "sync"
    "time"
)

// stage1: generate URLs to crawl
func generateURLs(ctx context.Context) <-chan string {
    out := make(chan string)
    go func() {
        defer close(out)
        urls := []string{
            "https://api.example.com/users",
            "https://api.example.com/orders",
            "https://api.example.com/products",
            "https://api.example.com/categories",
            "https://api.example.com/reviews",
            "https://api.example.com/inventory",
            "https://api.example.com/payments",
            "https://api.example.com/shipping",
        }
        for _, url := range urls {
            select {
            case <-ctx.Done():
                return
            case out <- url:
            }
        }
    }()
    return out
}

// stage2: fan-out — N workers fetch URLs concurrently
func fetchAll(ctx context.Context, urls <-chan string, numWorkers int) <-chan string {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Each worker creates its own output channel
    // Then merge all into 1 channel (fan-in)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    var channels []<-chan string

// Fan-out: create N workers
    for i := range numWorkers { // Go 1.22+
        ch := make(chan string)
        channels = append(channels, ch)
        go func(workerID int, out chan<- string) {
            defer close(out)
            for url := range urls {
                select {
                case <-ctx.Done():
                    return
                default:
                }

// Simulate HTTP fetch
                delay := time.Duration(100+rand.IntN(300)) * time.Millisecond
                time.Sleep(delay)
                out <- fmt.Sprintf("[W%d] Fetched %s (%v)", workerID, url, delay)
            }
        }(i+1, ch)
    }

// Fan-in: merge all worker outputs
    return mergeChannels(channels...)
}

// mergeChannels: fan-in helper — merge N channels into 1
func mergeChannels(channels ...<-chan string) <-chan string {
    out := make(chan string)
    var wg sync.WaitGroup
    for _, ch := range channels {
        wg.Add(1)
        go func(c <-chan string) {
            defer wg.Done()
            for v := range c {
                out <- v
            }
        }(ch)
    }
    go func() {
        wg.Wait()
        close(out)
    }()
    return out
}

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

// Pipeline: generate → fan-out/fan-in fetch → consume results
    numWorkers := runtime.NumCPU()
    fmt.Printf("Starting pipeline with %d workers\n\n", numWorkers)

urls := generateURLs(ctx)
    results := fetchAll(ctx, urls, numWorkers)

// Consume results
    count := 0
    for result := range results {
        count++
        fmt.Printf("#%d %s\n", count, result)
    }
    fmt.Printf("\nTotal: %d URLs fetched\n", count)
}
```

**Achieved**: 8 URLs distributed across `NumCPU()` workers. Total time ≈ total / workers. Context timeout protects the entire pipeline.

**Caveat**: `runtime.NumCPU()` is a good default for CPU-bound work. For I/O-bound work: workers can be >> NumCPU (50-100). Output order is non-deterministic — if you need ordering, use index + sort.

**Use when**: Parallel URL crawling, batch file processing, multi-source data aggregation — the foundation for the Pipeline pattern (see `07-pipeline.md`).

> **Why is `runtime.NumCPU()` a good default for CPU-bound but not for I/O-bound?**
> CPU-bound work: each goroutine uses 100% CPU. More goroutines than cores → context switch overhead > throughput gain. I/O-bound work: goroutines wait for network/disk 99% of the time → CPU is idle. 100 goroutines waiting for I/O on 8 cores still only use 8 cores when data arrives. So I/O-bound workers should be >> NumCPU.

You now know fan-out, fan-in, and the complete pipeline. Here comes the dangerous part: closing output early and unbounded workers — traps set up from the beginning of this article.

---

## 4. PITFALLS

From here, with **Fan-out / Fan-in**, the focus is no longer making it run, but avoiding the kinds of execution that seem fine while silently creating operational debt.

| # | Severity | Mistake | Consequence | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Fatal | **Close output before wg.Wait()** | Panic — worker sends to closed channel | Always: `wg.Wait()` → `close(out)` |
| 2 | 🔴 Fatal | **Forget to cancel context** | Workers leak if context is not cancelled | `defer cancel()` |
| 3 | 🟡 Common | **Worker blocks on full output** | Pipeline stall, goroutine leak | Buffer output channel or check ctx.Done() |
| 4 | 🟡 Common | **Too many workers** | Overhead > benefit | CPU-bound: `NumCPU()` · I/O-bound: benchmark |

You have covered fan-out, fan-in, pipeline, and the close/leak/unbounded traps. The resources below help you go deeper.

---

## 5. REF

| Resource | Type | Link | Notes |
| --- | --- | --- | --- |
| Go Blog — Pipelines and Cancellation | Core team blog | [go.dev/blog/pipelines](https://go.dev/blog/pipelines) | Fan-out/fan-in patterns |
| Go Concurrency Patterns (Rob Pike) | Official talk | [go.dev/talks/2012/concurrency.slide](https://go.dev/talks/2012/concurrency.slide) | Foundational talk |
| Concurrency in Go (O'Reilly) | Book | ISBN: 978-1491941195 | Chapter on fan-out/fan-in |

---

## 6. RECOMMEND

You just went from fan-out (1→N workers) → fan-in (N→1 merge) → complete pipeline (generate → fan-out/fan-in → consume). From here, expand based on orchestration optimization or distributed scale.

| Next step | When | Reason | File/Link |
| --- | --- | --- | --- |
| **Ants / Tunny** | Reuse goroutines | Limit concurrency + reuse | [12-ants.md](./12-ants.md) |
| **conc.iter.Map** | Typed fan-out | Type-safe, order-preserved parallel map | [13-conc.md](./13-conc.md) |
| **Kafka/NATS** | Distributed fan-out | Cross-process fan-out for microservices | External services |
| **Ordered fan-in** | Preserve order | Heap merge / indexed results | Pattern |
| **GORM + fan-out** | Parallel queries | errgroup fan-out → merge results | `errgroup` |
| **OpenTelemetry** | Observability | Trace fan-out latency distribution | `otel.Tracer` |

---

**Links**: [← Errgroup](./05-errgroup.md) · [→ Pipeline](./07-pipeline.md)
