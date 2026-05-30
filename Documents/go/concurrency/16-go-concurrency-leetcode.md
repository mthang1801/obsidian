<!-- tags: leetcode, algorithms, coding-interview -->
# ⚡ Go Concurrency Patterns for LeetCode

> Goroutines, channels, select, sync primitives — solving LeetCode concurrency problems and real-world applications

📅 Created: 2026-03-20 · 🔄 Updated: 2026-04-19 · ⏱️ 15 min read

| Aspect         | Detail                                                |
| -------------- | ----------------------------------------------------- |
| **Complexity** | O(n/p) with p workers                                 |
| **Use case**   | Parallel processing, producer-consumer, rate limiting |
| **Go stdlib**  | `sync`, `sync/atomic`, `context`, channel             |
| **LeetCode**   | #1114, #1115, #1116, #1117, #1195, #1226              |

---

## 0. TEMPLATE

> Copy-paste when encountering this type of problem in an interview.

```text
// ── Print In Order (channel barrier) ─────────────────────────
ch1, ch2 := make(chan struct{}, 1), make(chan struct{}, 1)
// first(): print, close(ch1)
// second(): <-ch1; print; close(ch2)
// third():  <-ch2; print

// ── Worker Pool ───────────────────────────────────────────────
jobs := make(chan int, numJobs)
results := make(chan int, numJobs)
for w := 0; w < numWorkers; w++ {
    go func() {
        for j := range jobs { results <- process(j) }
    }()
}
for _, j := range work { jobs <- j }
close(jobs)

// ── WaitGroup ─────────────────────────────────────────────────
var wg sync.WaitGroup
for _, item := range items {
    wg.Add(1)
    go func(v T) { defer wg.Done(); process(v) }(item)
}
wg.Wait()

// ── Semaphore (limit concurrency) ────────────────────────────
sem := make(chan struct{}, maxConcurrent)
go func() { sem <- struct{}{}; defer func() { <-sem }(); work() }()

// ── Context timeout ───────────────────────────────────────────
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
select {
case result := <-resultCh: use(result)
case <-ctx.Done(): handleTimeout()
}
```

---

## 1. DEFINE

Concurrency interview problems test one thing: can you coordinate goroutines with the right primitive under time pressure? This reference maps each classic LeetCode concurrency problem to the Go pattern that solves it — channels, mutexes, WaitGroups, or condition variables — so you spend the interview writing code, not rediscovering the pattern.

> *FizzBuzz goroutine ordered. Channel sync concurrent puzzle.*

### Go Concurrency Primitives

| Primitive            | Description                      | Use case                |
| -------------------- | -------------------------------- | ----------------------- |
| **goroutine**        | Lightweight thread               | Parallel execution      |
| **channel**          | Communication between goroutines | Data passing, signaling |
| **buffered channel** | Channel with capacity            | Rate limiting, batching |
| **select**           | Wait on multiple channels        | Timeout, fan-in         |
| **sync.Mutex**       | Mutual exclusion                 | Shared state protection |
| **sync.WaitGroup**   | Wait for goroutines to finish    | Fork-join parallelism   |
| **sync.Once**        | Execute exactly once             | Lazy initialization     |
| **sync.Cond**        | Condition variable               | Wait for condition      |
| **context.Context**  | Cancellation propagation         | Timeout, deadline       |

### Concurrency Patterns

| Pattern               | Description                         | Use                     |
| --------------------- | ----------------------------------- | ----------------------- |
| **Fan-out/Fan-in**    | Distribute work → collect results   | Parallel processing     |
| **Pipeline**          | Stage 1 → Stage 2 → Stage 3        | Data transformation     |
| **Worker Pool**       | N workers consume from job channel  | Bounded parallelism     |
| **Producer-Consumer** | Produce → channel → consume         | Decoupled processing    |
| **Semaphore**         | Buffered channel as semaphore       | Limit concurrent access |
| **Barrier**           | sync.WaitGroup or channel           | Synchronize at point    |

The primitives and patterns above form the foundation. But the smallest traps are the most dangerous: goroutine leak from forgetting to close a channel, context leak from forgetting to defer cancel. That trap will surface in PITFALLS.

Concurrency primitives and patterns — theory is covered. Let us see what barrier and pipeline look like visually.

---
## 2. VISUAL

The main visual of this article is a pattern chooser: not every problem with threads needs a goroutine, and not every concurrency task should reach for channels first.

![Go concurrency LeetCode pattern map](./images/16-go-concurrency-leetcode-pattern-map.png)

*This decision map holds the core focus of the article: read the problem statement then map it to ordering, bounded work, shared state, or lifecycle control.*

### Print In Order (Barrier Pattern)

```text
Thread A: "first"  → must print 1st
Thread B: "second" → must print 2nd
Thread C: "third"  → must print 3rd

Solution: Channels as barriers
  A prints "first"  → close(ch1) signals B
  B waits on ch1    → prints "second" → close(ch2) signals C
  C waits on ch2    → prints "third"
```

### Pipeline Pattern

```text
Generator → Square → Print

gen(1,2,3) ─ch1→ square() ─ch2→ print()

Output: 1, 4, 9
```

The diagram gives an overview of concurrency patterns. Now let us implement — starting from ordering/barrier, then alternating/pipeline, then worker pool/rate limiter.

---

## 3. CODE

You have seen the flow of signals, requests, and goroutines in **Go Concurrency Patterns for LeetCode**. Now shift to code to check which parts must be written tightly to avoid paying the production price.

### Example 1: Basic — Print In Order & FizzBuzz [LC #1114, #1195]

> **Goal**: Ordering goroutines, synchronization
> **Requirements**: Channel barriers, sync primitives
> **Achieved**: Deterministic execution order

```go
// leetcode/concurrency_basic.go
package leetcode

import (
    "sync"
)

// ✅ LC #1114: Print in Order
// Ensure three functions execute in order: first → second → third
type Foo struct {
    ch1 chan struct{} // ✅ Signal: first done
    ch2 chan struct{} // ✅ Signal: second done
}

func NewFoo() *Foo {
    return &Foo{
        ch1: make(chan struct{}),
        ch2: make(chan struct{}),
    }
}

func (f *Foo) First(printFirst func()) {
    printFirst()
    close(f.ch1) // ✅ Signal second to proceed
}

func (f *Foo) Second(printSecond func()) {
    <-f.ch1 // ✅ Wait for first
    printSecond()
    close(f.ch2) // ✅ Signal third to proceed
}

func (f *Foo) Third(printThird func()) {
    <-f.ch2 // ✅ Wait for second
    printThird()
}

// ✅ LC #1195: Fizz Buzz Multithreaded
type FizzBuzz struct {
    n    int
    curr int
    mu   sync.Mutex
    cond *sync.Cond
    done bool
}

func NewFizzBuzz(n int) *FizzBuzz {
    fb := &FizzBuzz{n: n, curr: 1}
    fb.cond = sync.NewCond(&fb.mu)
    return fb
}

func (fb *FizzBuzz) Fizz(printFizz func()) {
    for {
        fb.mu.Lock()
        for fb.curr <= fb.n && !(fb.curr%3 == 0 && fb.curr%5 != 0) {
            fb.cond.Wait()
        }
        if fb.curr > fb.n {
            fb.mu.Unlock()
            return
        }
        printFizz()
        fb.curr++
        fb.cond.Broadcast() // ✅ Wake all waiters
        fb.mu.Unlock()
    }
}

func (fb *FizzBuzz) Buzz(printBuzz func()) {
    for {
        fb.mu.Lock()
        for fb.curr <= fb.n && !(fb.curr%5 == 0 && fb.curr%3 != 0) {
            fb.cond.Wait()
        }
        if fb.curr > fb.n {
            fb.mu.Unlock()
            return
        }
        printBuzz()
        fb.curr++
        fb.cond.Broadcast()
        fb.mu.Unlock()
    }
}

func (fb *FizzBuzz) FizzBuzzPrint(printFizzBuzz func()) {
    for {
        fb.mu.Lock()
        for fb.curr <= fb.n && !(fb.curr%3 == 0 && fb.curr%5 == 0) {
            fb.cond.Wait()
        }
        if fb.curr > fb.n {
            fb.mu.Unlock()
            return
        }
        printFizzBuzz()
        fb.curr++
        fb.cond.Broadcast()
        fb.mu.Unlock()
    }
}

func (fb *FizzBuzz) Number(printNumber func(int)) {
    for {
        fb.mu.Lock()
        for fb.curr <= fb.n && (fb.curr%3 == 0 || fb.curr%5 == 0) {
            fb.cond.Wait()
        }
        if fb.curr > fb.n {
            fb.mu.Unlock()
            return
        }
        printNumber(fb.curr)
        fb.curr++
        fb.cond.Broadcast()
        fb.mu.Unlock()
    }
}
```

This example is appropriate for grasping the baseline of Print In Order & FizzBuzz [LC #1114, #1195]. When you need to handle more edge cases or coordinate additional abstractions, move to the next example.

> **✅ Achieved**: Print ordering via channel barriers, FizzBuzz via Cond variables.
> **⚠️ Caveats**: `close(ch)` broadcasts to all receivers. `Cond.Broadcast()` wakes all waiters.

Print ordering covers the barrier pattern. But when you need strict alternation between 2 goroutines — channel ping-pong is the Go-idiomatic solution.

---

### Example 2: Intermediate — Alternating Print & Pipeline [LC #1115]

> **Goal**: Alternating execution, Go pipeline pattern
> **Requirements**: Channel ping-pong
> **Achieved**: Strict alternation, data pipeline

```go
// leetcode/concurrency_intermediate.go
package leetcode

import (
    "fmt"
    "sync"
)

// ✅ LC #1115: Print FooBar Alternately
// Thread 1: "foo" → Thread 2: "bar" → repeat n times
type FooBar struct {
    n      int
    fooCh  chan struct{} // ✅ Signal foo's turn
    barCh  chan struct{} // ✅ Signal bar's turn
}

func NewFooBar(n int) *FooBar {
    fb := &FooBar{
        n:     n,
        fooCh: make(chan struct{}, 1),
        barCh: make(chan struct{}, 1),
    }
    fb.fooCh <- struct{}{} // ✅ Foo goes first
    return fb
}

func (fb *FooBar) Foo(printFoo func()) {
    for i := 0; i < fb.n; i++ {
        <-fb.fooCh   // ✅ Wait for turn
        printFoo()
        fb.barCh <- struct{}{} // ✅ Signal bar
    }
}

func (fb *FooBar) Bar(printBar func()) {
    for i := 0; i < fb.n; i++ {
        <-fb.barCh   // ✅ Wait for turn
        printBar()
        fb.fooCh <- struct{}{} // ✅ Signal foo
    }
}

// ═══════════════════════════════════════════
// Go Pipeline Pattern (practical application)
// ═══════════════════════════════════════════

// ✅ Pipeline: Generator → Transform → Consumer
func pipeline() {
    // Stage 1: Generate numbers
    gen := func(nums ...int) <-chan int {
        out := make(chan int)
        go func() {
            defer close(out)
            for _, n := range nums {
                out <- n
            }
        }()
        return out
    }

// Stage 2: Square numbers
    square := func(in <-chan int) <-chan int {
        out := make(chan int)
        go func() {
            defer close(out)
            for n := range in {
                out <- n * n
            }
        }()
        return out
    }

// ✅ Pipeline execution
    ch := gen(2, 3, 4)
    result := square(ch)

for v := range result {
        fmt.Println(v) // 4, 9, 16
    }
}

// ✅ Fan-out / Fan-in: Multiple workers, single collector
func fanOutFanIn(jobs []int, workerCount int) []int {
    jobCh := make(chan int, len(jobs))
    resultCh := make(chan int, len(jobs))

// ✅ Fan-out: spawn workers
    var wg sync.WaitGroup
    for w := 0; w < workerCount; w++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobCh {
                resultCh <- job * job // ✅ Process
            }
        }()
    }

// ✅ Send jobs
    go func() {
        for _, j := range jobs {
            jobCh <- j
        }
        close(jobCh) // ✅ Signal no more jobs
    }()

// ✅ Fan-in: collect results
    go func() {
        wg.Wait()
        close(resultCh)
    }()

results := []int{}
    for r := range resultCh {
        results = append(results, r)
    }
    return results
}
```

This level starts being useful for real code because it coordinates multiple techniques. The caveat is to keep the API compact so the reader does not lose track of reasoning.

> **✅ Achieved**: FooBar alternation via ping-pong channels, Go pipeline, fan-out/fan-in.
> **⚠️ Caveats**: Pipeline: `defer close(out)` ensures downstream knows when upstream is done.

> **Why use 2 alternating channels instead of mutex + condition variable?**
> Mutex + cond: the caller must manage state manually (whose turn?), easy to get wrong. 2 channels = turnA, turnB — goroutine A waits on `<-turnA`, prints, then sends `turnB <- struct{}{}`. Zero shared state, zero race condition. Channel-based synchronization is more Go-idiomatic than mutex for coordination patterns.

Alternating/pipeline covers coordination. But production needs worker pool + rate limiter + context cancellation — all in one example.

---

### Example 3: Advanced — Worker Pool, Rate Limiter & Context [Practical Go]

> **Goal**: Production concurrency patterns
> **Requirements**: Bounded concurrency, cancellation
> **Achieved**: Resource-safe concurrent processing

```go
// leetcode/concurrency_advanced.go
package leetcode

import (
    "context"
    "sync"
    "time"
)

// ✅ Worker Pool Pattern
// Bounded concurrency: at most N goroutines running
type WorkerPool struct {
    workers int
    jobs    chan func()
    wg      sync.WaitGroup
}

func NewWorkerPool(workers int) *WorkerPool {
    wp := &WorkerPool{
        workers: workers,
        jobs:    make(chan func(), workers*2), // ✅ Buffered
    }

// ✅ Start workers
    for i := 0; i < workers; i++ {
        wp.wg.Add(1)
        go func() {
            defer wp.wg.Done()
            for job := range wp.jobs {
                job() // ✅ Execute job
            }
        }()
    }

return wp
}

func (wp *WorkerPool) Submit(job func()) {
    wp.jobs <- job
}

func (wp *WorkerPool) Shutdown() {
    close(wp.jobs) // ✅ Signal no more jobs
    wp.wg.Wait()    // ✅ Wait for completion
}

// ✅ Semaphore Pattern (buffered channel)
// Limit concurrent access to a resource
type Semaphore chan struct{}

func NewSemaphore(max int) Semaphore {
    return make(Semaphore, max)
}

func (s Semaphore) Acquire() { s <- struct{}{} }
func (s Semaphore) Release() { <-s }

// Usage: limit to 3 concurrent operations
func processWithLimit(items []int) {
    sem := NewSemaphore(3)
    var wg sync.WaitGroup

for _, item := range items {
        wg.Add(1)
        sem.Acquire() // ✅ Block if 3 already running

go func(n int) {
            defer wg.Done()
            defer sem.Release()
            // process(n)
        }(item)
    }

wg.Wait()
}

// ✅ Context with Timeout — prevent goroutine leak
func processWithTimeout(ctx context.Context) (int, error) {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()

resultCh := make(chan int, 1)

go func() {
        // ✅ Long computation
        result := heavyComputation()
        select {
        case resultCh <- result:
        case <-ctx.Done():
            return // ✅ Context cancelled, exit goroutine
        }
    }()

select {
    case result := <-resultCh:
        return result, nil
    case <-ctx.Done():
        return 0, ctx.Err() // ✅ Timeout or cancelled
    }
}

func heavyComputation() int {
    time.Sleep(2 * time.Second) // Simulate work
    return 42
}

// ✅ Rate Limiter Pattern (Token Bucket)
type RateLimiter struct {
    tokens chan struct{}
    quit   chan struct{}
}

func NewRateLimiter(rate int, interval time.Duration) *RateLimiter {
    rl := &RateLimiter{
        tokens: make(chan struct{}, rate),
        quit:   make(chan struct{}),
    }

// ✅ Refill tokens periodically
    go func() {
        ticker := time.NewTicker(interval / time.Duration(rate))
        defer ticker.Stop()
        for {
            select {
            case <-ticker.C:
                select {
                case rl.tokens <- struct{}{}:
                default: // ✅ Bucket full, discard token
                }
            case <-rl.quit:
                return
            }
        }
    }()

return rl
}

func (rl *RateLimiter) Allow() { <-rl.tokens }
func (rl *RateLimiter) Stop()  { close(rl.quit) }
```

This is the closest to production level in this article. Only keep this complexity when the trade-off yields clear benefits in correctness, throughput, or maintainability.

> **✅ Achieved**: Worker pool, semaphore, context timeout, rate limiter — production Go patterns.
> **⚠️ Caveats**: Always `defer cancel()` when using context. Always handle `ctx.Done()` in goroutines.

> **Why does the rate limiter use `time.Ticker` instead of `time.Sleep`?**
> `time.Sleep(d)` in a loop: interval = sleep + processing time → cumulative drift. `time.Ticker` uses wall clock — fixed ticks regardless of processing time. With high-frequency rate limiting (1000 req/s), drift from Sleep can make the actual rate deviate significantly.

You now know barrier, alternating, pipeline, worker pool, and rate limiter. Here comes the dangerous part: goroutine leak and context leak — traps set up from the beginning of this article.

---

## 4. PITFALLS

The correct mechanism of **Go Concurrency Patterns for LeetCode** is in place. The traps below are where people get timing, ownership, or evidence wrong — and only realize it when the incident has already exploded.

| # | Severity | Mistake | Consequence | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Fatal | Goroutine leak: forget to close channel | Goroutine hangs forever | `defer close(ch)` when producer is done |
| 2 | 🔴 Fatal | Race condition: shared state no mutex | Data corruption | `sync.Mutex` or channels |
| 3 | 🔴 Fatal | Deadlock: send/receive on same goroutine | Program hangs | Use buffered channel or separate goroutine |
| 4 | 🟡 Common | `close()` on nil channel | Panic | Check nil before close |
| 5 | 🔴 Fatal | Context leak: forget cancel | Goroutine + resource leak | `defer cancel()` RIGHT AFTER `context.With*()` |
| 6 | 🟡 Common | WaitGroup: Add after Wait | Race condition | `wg.Add()` BEFORE `go func()` |
| 7 | 🔵 Minor | Range over closed channel | None (correct behavior) | `range ch` exits when ch closed — this is correct |

You have covered barrier, alternating, pipeline, worker pool, rate limiter, and the leak/race/sleep traps. The resources below help you go deeper.

---

## 5. REF

| Resource | Type | Link | Notes |
| --- | --- | --- | --- |
| LC #1114 Print In Order | LeetCode | [leetcode.com/problems/print-in-order](https://leetcode.com/problems/print-in-order/) | Channel barrier |
| LC #1115 Print FooBar | LeetCode | [leetcode.com/problems/print-foobar-alternately](https://leetcode.com/problems/print-foobar-alternately/) | Ping-pong channels |
| Go Concurrency Patterns | Official blog | [go.dev/blog/pipelines](https://go.dev/blog/pipelines) | Pipeline pattern |
| Go context | Official docs | [pkg.go.dev/context](https://pkg.go.dev/context) | Cancellation |
| Go sync | Official docs | [pkg.go.dev/sync](https://pkg.go.dev/sync) | Sync primitives |

---

## 6. RECOMMEND

You have enough context from **Go Concurrency Patterns for LeetCode** to proceed with purpose. The directions below help expand to the right tooling, runtime, or related pattern layer.

| Next step | When | Reason | File/Link |
| --- | --- | --- | --- |
| **errgroup** | Error propagation | `golang.org/x/sync/errgroup` | [05-errgroup.md](./05-errgroup.md) |
| **singleflight** | Deduplicate requests | Cache thundering herd | [11-singleflight.md](./11-singleflight.md) |
| **sync.Pool** | Object reuse | Reduce GC pressure | [04-sync-pool.md](./04-sync-pool.md) |
| **atomic operations** | Lock-free counters | `sync/atomic` | [02-mutex-and-race-condition.md](./02-mutex-and-race-condition.md) |

---

## 7. QUICK REF

| # | Pattern | Code |
|---|---------|------|
| 1 | Channel barrier | `ch := make(chan struct{}, 1); close(ch)` to signal |
| 2 | Worker pool | `for w := 0; w < n; w++ { go func() { for j := range jobs { ... } }() }` |
| 3 | WaitGroup | `wg.Add(1); go func() { defer wg.Done(); ... }(); wg.Wait()` |
| 4 | Semaphore | `sem := make(chan struct{}, limit); sem <- struct{}{}; defer <-sem` |
| 5 | Mutex protect | `var mu sync.Mutex; mu.Lock(); defer mu.Unlock()` |
| 6 | Context timeout | `ctx, cancel := context.WithTimeout(ctx, d); defer cancel()` |
| 7 | Select default | `select { case v := <-ch: use(v); default: noBlock() }` |
| 8 | Complexity | `// Worker pool O(n/p) · p goroutines · O(1) channel ops` |

---

**Links**: [← DP Sequences](../../leet-codes/23-dp-sequences.md) · [→ README](./README.md)
