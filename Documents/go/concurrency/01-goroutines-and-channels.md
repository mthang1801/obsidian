<!-- tags: golang, concurrency, goroutines -->
# 01 — Goroutines & Channels

> **Foundation**: The most fundamental building block — every concurrency pattern builds on top of this.

📅 Created: 2026-03-19 · 🔄 Updated: 2026-04-19 · ⏱️ 18 min read

| Aspect         | Detail                                                        |
| -------------- | ------------------------------------------------------------- |
| **Concept**    | Goroutine — lightweight coroutine, Channel — typed FIFO pipe  |
| **Use case**   | Concurrent I/O, fan-out/fan-in, pipeline, background workers  |
| **Go stdlib**  | `go`, `chan`, `select`, `sync.WaitGroup`                      |
| **Key insight**| Share memory by communicating — channel-first, mutex-second   |

---

## 1. DEFINE

Every Go concurrency pattern — pipelines, fan-out, worker pools, semaphores — is built from two primitives: **goroutines** (lightweight execution) and **channels** (typed communication). If your mental model of these two is shaky, every pattern you layer on top will feel like magic you cannot debug.

You have an API endpoint that calls 5 external services to aggregate data. Sequential calls: 200ms × 5 = 1 second. Traffic grows to 10,000 req/s? An OS thread costs ~1MB of stack — 10,000 threads means 10GB of RAM just for stacks. You need a way to run concurrently without burning resources exponentially.

Goroutines solve this: each goroutine costs only ~2KB of stack (auto-grows when needed), and the Go runtime uses M:N scheduling to map millions of goroutines onto a few OS threads. Channels let goroutines communicate — the "share memory by communicating" philosophy. But there is a dangerous trap: a goroutine that nobody cancels is a **goroutine leak**. 1,000 requests × 1 leaked goroutine = 1,000 zombies eating memory and file descriptors, leading to OOM within hours. That trap will surface in PITFALLS.

### Goroutine

A **goroutine** is a concurrently executing function managed by the **Go runtime** (not an OS thread). Lightweight (~2KB stack, auto-grows), it allows creating millions of goroutines.

```text
go myFunction()        // create a goroutine
go func() { ... }()   // anonymous goroutine
```

### Channel

A **channel** is the communication mechanism between goroutines — Go's philosophy:

> _"Don't communicate by sharing memory; share memory by communicating."_

### Unbuffered vs Buffered

| Property          | Unbuffered `make(chan T)`              | Buffered `make(chan T, N)`           |
| ----------------- | -------------------------------------- | ------------------------------------ |
| **Sync**          | Sender & Receiver are fully synchronous | Sender blocks only when buffer is full |
| **Use case**      | Handoff, signaling                     | Decouple producer/consumer speed     |
| **Throughput**    | Lower (they wait for each other)       | Higher (buffer absorbs bursts)       |
| **Deadlock risk** | High if you forget the receiver        | Lower but still possible             |

### Directional Channels

| Type          | Syntax     | Meaning                      |
| ------------- | ---------- | ---------------------------- |
| Bidirectional | `chan T`   | Send and receive             |
| Send-only     | `chan<- T` | Send only — compiler-enforced  |
| Receive-only  | `<-chan T` | Receive only — compiler-enforced |

### Select

**`select`** is a multiplexer — it waits on multiple channel operations simultaneously. When multiple cases are ready, Go picks one **at random** (fairness).

### Actors

| Actor            | Role                                             |
| ---------------- | ------------------------------------------------- |
| **Goroutine**    | Unit of concurrent execution                      |
| **Channel**      | Data pipe between goroutines                      |
| **Go Scheduler** | M:N scheduler — maps M goroutines onto N OS threads |
| **`select`**     | Multiplexer — waits on multiple channels at once  |

### Invariants

- **Only the sender closes a channel** — a receiver must NEVER close it
- **Close only once** — closing an already-closed channel causes a `panic`
- **Send to a closed channel → `panic`**
- **Receive from a closed channel → zero value** — use `v, ok := <-ch`

### Failure Modes

| Failure             | Cause                    | Prevention                        |
| ------------------- | ------------------------ | --------------------------------- |
| **Goroutine leak**  | Goroutine blocks forever on a channel | Always use `context.Context`     |
| **Deadlock**        | All goroutines are blocked | Sender/receiver must be paired   |
| **Race condition**  | Shared memory without sync | Use channels instead of shared memory |
| **Panic on closed** | Send to a closed channel   | Only the sender should close     |

Goroutine, channel, select, invariants — theory is covered. Let us see what M:N scheduling and channel mechanics look like visually.

---
## 2. VISUAL

The "see it to understand it" section of this article has two distinct jobs: lifecycle ownership of goroutine/channel, and the trade-off between buffered and unbuffered channels. Separating them makes both far easier to remember.

### Lifecycle & Ownership

![Goroutine and channel lifecycle](./images/01-goroutines-and-channels-lifecycle-workflow.png)

*This diagram answers the article's biggest question: which goroutine spawns, how they communicate, who owns the right to close the channel, and where clean shutdown happens.*

### Buffered vs Unbuffered Trade-off

![Buffered vs unbuffered channels](./images/01-goroutines-and-channels-buffered-vs-unbuffered-compare.png)

*This diagram is not about syntax. It is about coordination pressure: immediate rendezvous or a small queue that absorbs bursts.*

### Supporting View: `select` is the control plane of concurrency

```text
select
├── case <-ctx.Done(): stop work
├── case v := <-dataCh: process value
├── case err := <-errCh: fail fast or route error
└── default: optional non-blocking branch
```

*When channels are the data plane, `select` is the control plane that coordinates timeout, cancellation, input, and error streams in a single loop.*

Keep both PNG diagrams in mind before reading the code: which goroutine creates the resource, which goroutine closes it, and whether a queue truly helps or just delays the blocking point.

---

## 3. CODE

The flow of **Goroutines & Channels** is clear. Now let us bring it down to code to see what constraints make this mechanism hold up, not just intuition.

---

### Example 1: Basic — Unbuffered Channel — Synchronous Handoff

You need goroutine A to finish preparing data and then hand it off to the main goroutine — not sooner, not later. Without a synchronization mechanism, main may exit before the data arrives.

An unbuffered channel solves this with **synchronous handoff**: the sender blocks until the receiver is ready, and vice versa. The two sides "shake hands" naturally — no timer, no polling.

```go
package main

import "fmt"

func main() {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Unbuffered channel: capacity = 0
    // Sender BLOCKS until a receiver is ready.
    // Receiver BLOCKS until a sender is ready.
    // → The two sides "shake hands" — synchronous handoff.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ch := make(chan string) // unbuffered — capacity = 0

// Goroutine: send a message
    go func() {
        fmt.Println("[Sender] Preparing message...")
        ch <- "Hello from goroutine!" // ← BLOCKS here until main receives
        fmt.Println("[Sender] Message sent!")
    }()

// Main goroutine: receive the message
    msg := <-ch // ← BLOCKS here until the goroutine sends
    fmt.Println("[Main] Received:", msg)
}
```

An unbuffered channel is a synchronization point. Two goroutines need to know nothing about each other beyond the channel's type — and the handoff mechanism guarantees data arrives at the right time.

**Achieved**: The sender blocks until the receiver is ready — print order is always `[Sender] Preparing...` → `[Main] Received...` → `[Sender] Message sent!`

**Caveat**: If no goroutine receives: **deadlock** — `fatal error: all goroutines are asleep`. Unbuffered channels suit **signaling** and **handoff**, not high-throughput data.

**Use when**: You need a guarantee that data has been received before the sender continues — for example, transferring ownership of a resource, or signaling "job done."

Unbuffered channels cover synchronous handoff. But when the producer is faster than the consumer — sending 10 jobs while the consumer processes each in 200ms — the sender blocks constantly. Buffered channels decouple their speeds.

---

### Example 2: Intermediate — Buffered Channel — Producer/Consumer

The unbuffered channel above forces the sender to wait for the receiver — perfect synchronous handoff. But imagine the producer creates 10 jobs per second while the consumer takes 200ms per job. The sender blocks continuously and throughput drops.

A buffered channel adds a small queue in between: the producer sends up to N items without blocking, and the consumer pulls them out when ready. When the buffer is full, the sender pauses — natural back-pressure without a rate limiter.

```go
package main

import (
    "fmt"
    "time"
)

func main() {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Buffered channel: capacity = 5
    // Producer sends up to 5 items without blocking.
    // Blocks only when the buffer is full (5/5).
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    jobs := make(chan int, 5) // buffered — capacity = 5

// Producer: create 10 jobs (fast)
    go func() {
        defer close(jobs) // ← IMPORTANT: only the sender closes the channel
        for i := 1; i <= 10; i++ {
            fmt.Printf("→ Producing job %d\n", i)
            jobs <- i // blocks when buffer is full (5/5)
        }
        fmt.Println("→ Producer done!")
    }()

// Consumer: process jobs (slow — 200ms per job)
    for job := range jobs { // ← range stops automatically when channel closes
        fmt.Printf("  ← Processing job %d\n", job)
        time.Sleep(200 * time.Millisecond)
    }

fmt.Println("All jobs done!")
}
```

**Achieved**: The producer sends the first 5 jobs without blocking. From job 6 onward, the sender pauses until the consumer pulls items out — back-pressure works without any additional component.

**Caveat**: Buffer size is a throughput tuning knob — too small and the producer blocks constantly, too large and it wastes memory while hiding a slow consumer. Rule of thumb: buffer = number of items the consumer processes in one burst.

**Use when**: Producer and consumer run at different speeds and you need decoupling while keeping back-pressure. **ALWAYS `defer close(ch)`** on the sender side — forgetting to close means the consumer's `range` blocks forever, causing a silent goroutine leak.

> **Why does a buffered channel create automatic backpressure without extra logic?**
> When the buffer is full, `ch <- item` **blocks** the producer goroutine until the consumer reads something. This is Go's natural channel backpressure — the producer cannot overwhelm the consumer. With an unbuffered channel (`make(chan T)`), each send must have a ready receiver — synchronous handoff. A buffer lets the producer run ahead by N items without blocking.

Buffered channels cover producer/consumer decoupling. But a bidirectional `chan T` means the consumer can close the channel while the producer is still sending → panic. Directional channels enforce who sends and who receives at compile time.

---

### Example 3: Advanced — Directional Channels — Type Safety

Buffered channels decouple speed — but a bidirectional `chan T` has a vulnerability: the consumer can call `close(ch)` or `ch <- data`. If the consumer closes while the producer is still sending — panic. This bug does not show up when writing code; it shows up at 2 AM when traffic spikes.

Directional channels (`chan<-` send-only and `<-chan` receive-only) push this bug to **compile time** — the compiler enforces who sends, who receives, and who closes. Zero runtime cost.

```go
package main

import "fmt"

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Directional channels let the compiler check:
// - producer can only SEND (chan<- T)
// - consumer can only RECEIVE (<-chan T)
// If you write it wrong → compile error, not a runtime bug.
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

// producer can only SEND to the channel
func producer(out chan<- int, count int) {
    defer close(out)
    for i := range count { // Go 1.22+
        out <- i * i
    }
    // out = <-out  // ← COMPILE ERROR: cannot receive from send-only channel
}

// consumer can only RECEIVE from the channel
func consumer(in <-chan int) {
    for v := range in {
        fmt.Printf("Received: %d\n", v)
    }
    // in <- 42  // ← COMPILE ERROR: cannot send to receive-only channel
}

func main() {
    ch := make(chan int, 5) // bidirectional

go producer(ch, 5) // ch auto-casts → chan<- int
    consumer(ch)       // ch auto-casts → <-chan int
}
```

**Achieved**: The compiler enforces ownership — the producer cannot receive, the consumer cannot send or close. The "consumer closes channel" bug disappears entirely at compile time.

**Caveat**: Go auto-casts `chan T` → `chan<- T` or `<-chan T` when passing to a function, so no explicit conversion is needed at the call site.

**Use when**: Every function signature that accepts a channel should use directional types — this is Go convention, not a "nice-to-have." If a function takes `chan T` instead of `<-chan T`, ask: does it really need both send and receive?

> **Why do directional channels have zero runtime cost?**
> `chan<- T` and `<-chan T` are **compile-time constraints** — at runtime it is still the same channel object. The compiler only restricts operations without changing the data structure. This is free type safety.

Directional channels cover type safety. But when you need to wait on multiple channels at once — responses from 2 services, a timeout, cancellation — you need the `select` multiplexer.

---

### Example 4: Expert — Select — Timeout, Multiple Channels, Non-blocking

Directional channels guarantee type safety. But production does not involve just 1 channel — you wait for responses from 2 services, need a 1-second timeout, and want to check results without blocking if nothing is ready. All three needs point to the same primitive: `select`.

`select` is Go's multiplexer — it waits on multiple channel operations at once and picks the first ready case. When multiple cases are ready, Go picks one **at random** (fair scheduling, not undefined behavior).

```go
package main

import (
    "fmt"
    "math/rand/v2" // Go 1.22+
    "time"
)

func main() {
    ch1 := make(chan string)
    ch2 := make(chan string)

// Goroutine 1: slow response (500-1500ms)
    go func() {
        time.Sleep(time.Duration(500+rand.IntN(1000)) * time.Millisecond)
        ch1 <- "Response from Service A"
    }()

// Goroutine 2: faster response (100-500ms)
    go func() {
        time.Sleep(time.Duration(100+rand.IntN(400)) * time.Millisecond)
        ch2 <- "Response from Service B"
    }()

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Select: wait for responses from both services
    // Whichever responds first gets processed first (non-deterministic)
    // Timeout after 1 second if neither has responded.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    for range 2 { // Go 1.22+
        select {
        case msg := <-ch1:
            fmt.Println("✅", msg)
        case msg := <-ch2:
            fmt.Println("✅", msg)
        case <-time.After(1 * time.Second):
            fmt.Println("⏰ Timeout!")
            return
        }
    }

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Non-blocking select: use default
    // If no case is ready → run default immediately
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ch3 := make(chan int, 1)
    select {
    case v := <-ch3:
        fmt.Println("Got:", v)
    default:
        fmt.Println("Channel empty — not blocking!")
    }
}
```

**Achieved**: Multi-channel I/O concurrency, timeout via `time.After`, and non-blocking check via `default` — the three primary tools of production concurrency code.

**Caveat**: `time.After` creates a goroutine + timer on every call. Inside a loop, use `time.NewTimer` + `timer.Reset()` to avoid timer leaks. `default` turns select into non-blocking — watch out for busy loops if used in `for` without a sleep.

**Use when**: You need to wait on multiple data sources with a timeout or cancel signal — for example, an API gateway aggregating results from micro-services, or a health check polling multiple backends.

> **Why does `select` pick randomly when multiple cases are ready?**
> If Go always picked the first case, starvation would occur: the channel in case 1 always gets serviced while case 2 starves. Random selection ensures **fair scheduling** — every channel has an equal chance of being picked. This is an intentional design decision by the Go runtime.

Select covers multi-channel I/O. But when you need a long-running goroutine that runs continuously and stops gracefully, the `done` channel pattern is the foundation that predates `context.Context`.

---

### Example 5: Expert — Channel Patterns — Done Signal & For-Select Loop

`select` gives you a multiplexer. But one question remains unanswered: when a goroutine runs indefinitely (worker, listener, poller), how do you stop it gracefully without leaking?

The `done` channel pattern is Go's answer from before `context.Context` existed: `close(done)` broadcasts a signal to **all** goroutines that are listening — not point-to-point, nobody gets missed.

```go
package main

import (
    "fmt"
    "time"
)

// worker runs continuously until it receives a stop signal from the done channel
func worker(id int, done <-chan struct{}, results chan<- string) {
    defer fmt.Printf("[Worker %d] Cleaned up and exiting\n", id)

counter := 0
    for {
        select {
        case <-done:
            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            // When the done channel is closed, all
            // goroutines listening will receive the signal
            // (close broadcasts to all receivers)
            // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            return
        default:
            counter++
            results <- fmt.Sprintf("Worker %d: item %d", id, counter)
            time.Sleep(100 * time.Millisecond)
        }
    }
}

func main() {
    done := make(chan struct{}) // signal channel — struct{} costs zero memory
    results := make(chan string, 10)

// Start 3 workers
    for i := 1; i <= 3; i++ {
        go worker(i, done, results)
    }

// Collect results for 500ms
    timeout := time.After(500 * time.Millisecond)
    count := 0
loop:
    for {
        select {
        case msg := <-results:
            fmt.Println(msg)
            count++
        case <-timeout:
            fmt.Printf("\n⏰ Timeout! Collected %d results\n", count)
            break loop
        }
    }

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // close(done) → broadcast signal to ALL workers
    // Every goroutine selecting on <-done will receive it.
    // This is the BASIC cancel pattern before context existed.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    close(done)
    time.Sleep(100 * time.Millisecond) // wait for worker cleanup
}
```

**Achieved**: `close(done)` broadcasts a signal to all goroutines at once. A `struct{}` channel uses 0 bytes — Go convention for signal channels. The for-select loop is the most common pattern for long-running goroutines.

**Caveat**: The `done` channel is the predecessor of `context.Context` — in production, prefer context because it supports deadlines, value propagation, and tree cancellation. `break` inside select only breaks out of select, **NOT out of for** — use a label (`break loop`).

**Use when**: You need graceful shutdown for N continuously running workers. When N = 1, `close(done)` and `done <- struct{}{}` are equivalent. When N > 1, `close` is the only way to broadcast.

> **Why `close(done)` instead of `done <- struct{}{}` for signaling?**
> `done <- struct{}{}` signals only **1 goroutine** (point-to-point). `close(done)` broadcasts to **all** goroutines waiting on `<-done` — every receiver gets the zero value immediately. This is Go's broadcast mechanism, and it is the foundation of `context.WithCancel` under the hood.

You now know unbuffered, buffered, directional, select, and done signal channels. Next comes the most dangerous part: goroutine leaks — the trap set up from the beginning of this article, the invisible OOM killer.

---

## 4. PITFALLS

Knowing the correct path of **Goroutines & Channels** is not enough. The part that costs teams the most lies in wrong assumptions that dashboards and code demos do not reveal.

| # | Severity | Mistake | Wrong code | Correct code | Consequence |
| --- | --- | --- | --- | --- | --- |
| 1 | 🔴 Fatal | **Goroutine leak** | `go func() { <-ch }()` — nobody closes `ch` | Use `context.WithCancel` or `close(ch)` | Memory/FD leak accumulates, OOM |
| 2 | 🔴 Fatal | **Close from receiver** | Receiver calls `close(ch)` | Only the **sender** closes the channel | Panic when sender sends again |
| 3 | 🔴 Fatal | **Send to closed** | `close(ch); ch <- 1` → panic | Use `sync.Once` or check state | Runtime panic |
| 4 | 🟡 Common | **Forget range/ok** | `for { v := <-ch }` — infinite loop | `for v := range ch` or `v, ok := <-ch` | Goroutine never stops when channel closes |
| 5 | 🟡 Common | **Unbuffered deadlock** | `ch := make(chan int); ch <- 1` in same goroutine | Use buffered channel or a separate goroutine | `fatal error: all goroutines are asleep` |
| 6 | 🟡 Common | **time.After in loop** | `for { select { case <-time.After(1s) } }` — timer leak | Use `time.NewTimer` + `timer.Reset()` | Timer goroutine leaks every iteration |
| 7 | 🔵 Minor | **break in select** | `break` only exits select, not for | Use label: `break outerLoop` | Logic error, loop runs forever |

### 🔴 Pitfall #1 — Goroutine leak: the invisible OOM killer

Returning to the trap set up at the beginning. This code compiles, runs, and even passes tests:

```go
func fetchData(url string) {
    ch := make(chan []byte)
    go func() {
        resp, _ := http.Get(url)
        body, _ := io.ReadAll(resp.Body)
        ch <- body // ← blocks forever if nobody receives
    }()
    select {
    case data := <-ch:
        process(data)
    case <-time.After(2 * time.Second):
        log.Println("timeout") // goroutine is still alive, nobody receives from ch
    }
}
```

When timeout fires, the goroutine is still blocked on `ch <- body`. Nobody will ever receive from `ch` — the goroutine lives forever, holding `resp.Body`, the `[]byte`, and the connection. 1,000 timed-out requests = 1,000 zombies.

**Fix**: Use a buffered channel (`make(chan []byte, 1)`) so the goroutine can send and exit even when nobody receives. Or use `context.WithTimeout` so the goroutine cancels itself.

You have covered goroutines, channels, select, done signal, and the leak/deadlock/panic traps. The resources below help you go deeper.

---

## 5. REF

| Resource | Type | Link | Notes |
| --- | --- | --- | --- |
| Go Tour — Concurrency | Official tutorial | [go.dev/tour/concurrency](https://go.dev/tour/concurrency) | Interactive playground |
| Effective Go — Concurrency | Official guide | [go.dev/doc/effective_go#concurrency](https://go.dev/doc/effective_go#concurrency) | Goroutine + channel patterns |
| Go Blog — Share Memory By Communicating | Core team blog | [go.dev/blog/codelab-share](https://go.dev/blog/codelab-share) | Channel-first philosophy |
| Go Blog — Pipelines and Cancellation | Core team blog | [go.dev/blog/pipelines](https://go.dev/blog/pipelines) | Pipeline + done channel |

---

## 6. RECOMMEND

You just went from handoff (unbuffered) → decoupling (buffered) → type safety (directional) → multiplexing (select) → graceful shutdown (done signal). Goroutines and channels are the foundation — from here, each next step is a different kind of coordination problem.

| Next step | When | Reason | File/Link |
| --- | --- | --- | --- |
| **03 — Context** | When a goroutine needs a deadline or cancellation tree | Production standard to replace scattered `done` channels | [03-context.md](./03-context.md) |
| **02 — Mutex & Race Condition** | When coordination is actually shared-state protection | Separate handoff problems from lock problems | [02-mutex-and-race-condition.md](./02-mutex-and-race-condition.md) |
| **05 — errgroup** | When a group of goroutines must fail-fast with shared context | Structured cancellation cleaner than manual plumbing | [05-errgroup.md](./05-errgroup.md) |
| **06 — Fan-out/Fan-in** | When a single stream needs N workers and one merged sink | Elevate primitives into an orchestration pattern | [06-fan-out-fan-in.md](./06-fan-out-fan-in.md) |
| **07 — Pipeline Pattern** | When work flows through multiple sequential stages | Connect channel semantics to ownership, shutdown, and backpressure | [07-pipeline.md](./07-pipeline.md) |

---

## 7. QUICK REF

| Goal                              | Pattern                                    | Code snippet                              |
| ---------------------------------- | ------------------------------------------ | ----------------------------------------- |
| Run a task asynchronously          | goroutine                                  | `go func() { ... }()`                    |
| Send/receive values between goroutines | unbuffered channel                     | `ch := make(chan int)`                    |
| Avoid blocking when channel is full | buffered channel                          | `ch := make(chan int, 100)`               |
| Wait for N goroutines to finish    | `sync.WaitGroup`                           | `wg.Add(1); go f(); wg.Wait()`            |
| Cancel a goroutine externally      | `done` channel or `context`               | `ctx, cancel := context.WithCancel(...)`  |
| Fan-out: 1 input → N workers      | range channel in N goroutines              | see [06-fan-out-fan-in.md](./06-fan-out-fan-in.md) |
| Detect goroutine leak in tests     | `goleak`                                   | `defer goleak.VerifyNone(t)`              |
| Race condition detector            | `-race` flag                               | `go test -race ./...`                     |
| Select on multiple channels        | `select { case v := <-ch1: ... }`          | Non-blocking with `default:`              |
| Close a channel correctly          | Producer closes, consumer checks `ok`      | `v, ok := <-ch; if !ok { return }`       |

**Links**: [→ Mutex & Race Condition](./02-mutex-and-race-condition.md) · [→ Context](./03-context.md)
