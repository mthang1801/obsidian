<!-- tags: golang -->
# 13 — Conc

> **Library**: `github.com/sourcegraph/conc` — Structured concurrency, type-safe, panic-safe.

📅 Created: 2026-03-20 · 🔄 Updated: 2026-04-19 · ⏱️ 15 min read

---

## 1. DEFINE

`errgroup` handles error propagation and cancellation but leaves panic recovery and type safety to you. `conc` (by Sourcegraph) wraps `errgroup` with generics, automatic panic-to-error recovery, and structured concurrency guarantees — making it harder to write goroutine code that leaks, panics, or silently drops errors.

> *5 goroutines collect panic cancel. WaitGroup channel=40. conc=5.*

### Definition

**Conc** (by Sourcegraph) provides higher-level concurrency primitives built on top of `errgroup`. Key advantages: **type-safe generics**, **panic recovery built-in**, **structured concurrency** (goroutines are always cleaned up). But there is a trap: panic recovery can mask bugs if you do not monitor panic errors — and `ForEach` on shared state without a mutex = silent race condition. That trap will surface in PITFALLS.

### Core Components

| Component                 | Description                      | Equivalent                 |
| ------------------------- | -------------------------------- | -------------------------- |
| `pool.Pool`               | Goroutine pool — fire-and-forget | `errgroup.Group`           |
| `pool.ResultPool[T]`      | Pool returning type-safe results | errgroup + channel + mutex |
| `pool.ErrorPool`          | Pool with error propagation      | `errgroup.Group`           |
| `pool.ResultErrorPool[T]` | Pool returning results + errors  | Combined                   |
| `iter.ForEach[T]`         | Parallel iteration over slice    | Custom fan-out             |
| `iter.Map[T, R]`          | Parallel map — transform slice   | Custom fan-out + fan-in    |

### Conc vs Errgroup vs Ants

| Feature             | Conc                | Errgroup       | Ants      |
| ------------------- | ------------------- | -------------- | --------- |
| **Type-safe**       | ✅ Generics         | ❌             | ❌        |
| **Panic recovery**  | ✅ Auto             | ❌             | ✅ Option |
| **Return results**  | ✅ `ResultPool[T]`  | ❌             | ❌        |
| **Parallel iter**   | ✅ `ForEach`, `Map` | ❌             | ❌        |
| **Goroutine reuse** | ❌                  | ❌             | ✅        |
| **Error handling**  | ✅ All errors       | ✅ First error | ❌        |
| **Dependency**      | x/sync              | x/sync         | None      |

### Invariants

- Panics are ALWAYS recovered and re-raised when `Wait()` is called — panic info is never lost
- `ResultPool[T]` returns `[]T` type-safe — no type assertion needed
- Pool `Wait()` waits for ALL goroutines — structured concurrency
- `WithMaxGoroutines(n)` limits concurrency (like errgroup.SetLimit)

Conc pool types, structured concurrency, iter — theory is covered. Let us see what the pool lifecycle looks like visually.

---
## 2. VISUAL

`conc` should be remembered as a map of safer building blocks, not as magic that replaces understanding context and channels.

![Conc structured concurrency map](./images/13-conc-structured-concurrency-map.png)

*This PNG gathers the most memorable parts of `conc`: group helpers, typed pools, panic safety, and the real limits of the library.*

### Conc Pool Types

```
  pool.Pool              pool.ErrorPool         pool.ResultPool[T]
  ┌────────────┐         ┌────────────┐         ┌─────────────────┐
  │ Go(func()) │         │ Go(func()  │         │ Go(func() T)    │
  │            │         │   error)   │         │                 │
  │ Wait()     │         │ Wait()     │         │ Wait() []T      │
  │            │         │   error    │         │                 │
  └────────────┘         └────────────┘         └─────────────────┘
   fire-and-forget        error propagation       type-safe results
   + panic recovery       + panic recovery        + panic recovery
```

### iter.Map Flow

```
  Input:  [1, 2, 3, 4, 5]

iter.Map(input, func(n int) string {
      return fmt.Sprintf("%d²=%d", n, n*n)
  })

Worker 1: 1 → "1²=1"   ──┐
  Worker 2: 2 → "2²=4"   ──┤
  Worker 3: 3 → "3²=9"   ──┼──▶ Output: ["1²=1", "2²=4", "3²=9", ...]
  Worker 4: 4 → "4²=16"  ──┤      (ORDER PRESERVED!)
  Worker 5: 5 → "5²=25"  ──┘
```

The diagram gives an overview of pool types. Now let us implement — starting from basic pool types, then iter.ForEach/Map, then panic safety.

---

## 3. CODE

You have seen the flow of signals, requests, and goroutines in **Conc**. Now shift to code to check which parts must be written tightly to avoid paying the production price.

---

### Example 1: Basic — Pool types — fire-and-forget, errors, results
> **Goal**: Demonstrate pool types — fire-and-forget, errors, results in the right context so the reader understands why this technique exists.
> **Approach**: Start from a basic example then attach necessary technical decisions instead of jumping straight into hard code.
> **Example**: A job or request passes through multiple goroutines while preserving cancellation, concurrency limits, and clear error handling.
> **Complexity**: O(1) orchestration in application code; real cost depends on data, goroutines, or I/O being demonstrated.

**Goal**: Compare 3 pool types: `Pool`, `ErrorPool`, `ResultPool[T]`. Each for a different use case.

**Requirements**: `go get github.com/sourcegraph/conc`.

```go
package main

import (
    "fmt"
    "math/rand/v2" // Go 1.22+
    "time"

"github.com/sourcegraph/conc/pool"
)

func main() {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // 1. pool.Pool — fire-and-forget
    // Panic-safe: panic in Go → recovered, re-raised at Wait
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    fmt.Println("=== Pool (fire-and-forget) ===")
    p := pool.New().WithMaxGoroutines(4) // max 4 concurrent
    for i := range 10 { // Go 1.22+
        i := i
        p.Go(func() {
            time.Sleep(time.Duration(rand.IntN(100)) * time.Millisecond)
            fmt.Printf("  Task %d done\n", i)
        })
    }
    p.Wait() // block + re-raise panics if any
    fmt.Println()

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // 2. pool.ErrorPool — fire-and-forget + error collection
    // Collects ALL errors (unlike errgroup which only returns first error)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    fmt.Println("=== ErrorPool (with errors) ===")
    ep := pool.New().WithErrors().WithMaxGoroutines(4)
    for i := range 10 { // Go 1.22+
        i := i
        ep.Go(func() error {
            if i%3 == 0 {
                return fmt.Errorf("task %d failed", i)
            }
            fmt.Printf("  Task %d OK\n", i)
            return nil
        })
    }
    if err := ep.Wait(); err != nil {
        fmt.Printf("  ❌ Errors: %v\n", err) // multi-error
    }
    fmt.Println()

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // 3. pool.ResultPool[T] — type-safe results
    // Wait() returns []T — no channel + mutex needed
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    fmt.Println("=== ResultPool[string] (typed results) ===")
    rp := pool.NewWithResults[string]().WithMaxGoroutines(4)
    for i := range 5 { // Go 1.22+
        i := i
        rp.Go(func() string {
            return fmt.Sprintf("Result-%d: %d²=%d", i, i, i*i)
        })
    }
    results := rp.Wait() // []string — type-safe!
    for _, r := range results {
        fmt.Printf("  %s\n", r)
    }
}
```

This example is appropriate for grasping the baseline of pool types — fire-and-forget, errors, results. When you need to handle more edge cases or coordinate additional abstractions, move to the next example.

**Achieved**:

- `Pool`: fire-and-forget, panic-safe.
- `ErrorPool`: collects ALL errors (multi-error).
- `ResultPool[string]`: type-safe results, no channel/mutex needed.

**Caveats**:

- **Panic recovery**: Conc pools ALWAYS recover panics and re-raise at `Wait()`. Errgroup does NOT.
- `ErrorPool` collects **ALL** errors — errgroup only returns the **first** error.
- `WithMaxGoroutines(n)` = `errgroup.SetLimit(n)`.

Pool types cover fire-and-forget, errors, results. But when you need parallel iteration on a collection — `iter.ForEach` and `iter.Map` preserve order which errgroup cannot.

---

### Example 2: Intermediate — iter.ForEach & iter.Map — Parallel iteration
> **Goal**: Demonstrate iter.ForEach & iter.Map — parallel iteration in the right context so the reader understands why this technique exists.
> **Approach**: Start from an intermediate example then attach necessary technical decisions instead of jumping straight into hard code.
> **Example**: The code below goes from basic operation to a more practical variant so the reader sees how the same concept is used.
> **Complexity**: O(1) orchestration; total complexity depends on the number of coordination steps and related data structures.

**Goal**: Parallel iteration over slices: `ForEach` for side-effects, `Map` for transformation. Order preserved.

**Requirements**: `github.com/sourcegraph/conc/iter`.

```go
package main

import (
    "fmt"
    "strings"
    "time"

"github.com/sourcegraph/conc/iter"
)

type User struct {
    ID    int
    Name  string
    Email string
}

func main() {
    users := []User{
        {1, "Alice", "alice@example.com"},
        {2, "Bob", "bob@example.com"},
        {3, "Charlie", "charlie@example.com"},
        {4, "Diana", "diana@example.com"},
        {5, "Eve", "eve@example.com"},
    }

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // iter.ForEach: parallel for-each (side-effects)
    // Each element processed in parallel, waits for all to finish
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    fmt.Println("=== ForEach (send welcome emails) ===")
    iter.ForEach(users, func(u *User) {
        time.Sleep(100 * time.Millisecond) // simulate sending email
        fmt.Printf("  📧 Sent welcome email to %s (%s)\n", u.Name, u.Email)
    })
    fmt.Println()

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // iter.Map: parallel map — transform slice
    // ✅ ORDER PRESERVED (unlike fan-out/fan-in)
    // Input [T] → Output [R] (type-safe)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    fmt.Println("=== Map (transform users → display names) ===")
    displayNames := iter.Map(users, func(u *User) string {
        time.Sleep(50 * time.Millisecond) // simulate processing
        return fmt.Sprintf("%s <%s>", strings.ToUpper(u.Name), u.Email)
    })
    for i, name := range displayNames {
        fmt.Printf("  [%d] %s\n", i, name)
    }
    // Output ORDER = Input ORDER ✅

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // iter.Map with numbers
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    fmt.Println("\n=== Map (parallel square) ===")
    numbers := []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
    squares := iter.Map(numbers, func(n *int) int {
        return (*n) * (*n)
    })
    fmt.Println("  Squares:", squares) // [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
}
```

This level starts being useful for real code because it coordinates multiple techniques. The caveat is to keep the API compact so the reader does not lose track of reasoning.

**Achieved**:

- `ForEach`: parallel side-effects (send emails, update cache).
- `Map`: parallel transformation — **ORDER PRESERVED** (unlike fan-out/fan-in).
- Type-safe: `iter.Map[User, string]` → `[]string`.

**Caveats**:

- **Order preserved** in `Map` — very convenient compared to fan-out + sort.
- Default concurrency = `runtime.NumCPU()`. Use `iter.ForEachIdx` for index access.
- Conc `iter` callbacks receive a **pointer** (`*User`) — modify in-place if needed.
- `ForEach` is blocking — waits for ALL elements to complete.

> **Why does Conc preserve order in `Map` while errgroup does not?**
> Errgroup has no result collection — you append to a slice yourself (race if no lock). Conc `iter.Map` pre-allocates a result slice with the same size, each goroutine writes to its own index (no race). Results always match input order — zero sorting cost.

iter.ForEach/Map covers parallel collections. But the key selling point of Conc vs Errgroup is panic safety — 1 goroutine panicking does not crash the process.

---

### Example 3: Advanced — Panic safety — Conc vs Errgroup comparison
> **Goal**: Demonstrate panic safety — Conc vs Errgroup comparison in the right context so the reader understands why this technique exists.
> **Approach**: Start from an advanced example then attach necessary technical decisions instead of jumping straight into hard code.
> **Example**: A job or request passes through multiple goroutines while preserving cancellation, concurrency limits, and clear error handling.
> **Complexity**: O(1) orchestration at the example layer; real complexity lies in concurrency, memory, and integration underneath.

**Goal**: Prove that Conc recovers panics gracefully, while errgroup crashes.

```go
package main

import (
    "fmt"

"github.com/sourcegraph/conc/pool"
)

func main() {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Conc: panic recovered, re-raised as panic at Wait()
    // Errgroup: panic → crashes process (unrecovered)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

// Safe way: recover panic from Conc pool
    func() {
        defer func() {
            if r := recover(); r != nil {
                fmt.Printf("✅ Recovered panic from pool: %v\n", r)
            }
        }()

p := pool.New().WithMaxGoroutines(2)
        p.Go(func() {
            fmt.Println("  Task 1: working...")
        })
        p.Go(func() {
            panic("💥 Task 2 panicked!")
        })
        p.Go(func() {
            fmt.Println("  Task 3: working...")
        })
        p.Wait() // ← re-raises panic here
    }()

fmt.Println("\n✅ Program continues after pool panic!")
    fmt.Println("   (errgroup would have crashed the entire process)")
}
```

This is the closest to production level in this article. Only keep this complexity when the trade-off yields clear benefits in correctness, throughput, or maintainability.

**Achieved**:

- Conc pool recovers panic → re-raises at `Wait()` → caller can handle.
- Program continues running after panic (if caller recovers).

**Caveats**:

- **Errgroup does not recover panics** — 1 goroutine panic = crash process.
- Conc panic recovery = production safety net — no lost requests.
- Stack trace preserved in panic info — easy debugging.

> **Why does Conc recover panics while errgroup does not?**
> Go philosophy: explicit > implicit. Errgroup is stdlib-style — does not hide panics, lets devs know and fix root cause. Conc is a production-oriented library — 1 goroutine panic should not crash the entire process. Trade-off: Conc is safer but can mask bugs if you do not monitor panic errors.

You now know pool types, iter, and panic safety. Here comes the dangerous part: shared state races and panic masking — traps set up from the beginning of this article.

---

## 4. PITFALLS

The correct mechanism of **Conc** is in place. The traps below are where people get timing, ownership, or evidence wrong — and only realize it when the incident has already exploded.

| # | Severity | Mistake | Consequence | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Fatal | **Forget WithMaxGoroutines** | Unlimited goroutines | Always set limit |
| 2 | 🔴 Fatal | **Modify shared state in ForEach** | Race condition | Use mutex or per-element |
| 3 | 🟡 Common | **Ignore Wait() panic** | Un-recovered panic | Always defer recover if needed |
| 4 | 🔵 Minor | **Map callback heavy** | All CPUs busy | Tune max goroutines |

You have covered pool types, iter, panic safety, and the shared-state/panic traps. The resources below help you go deeper.

---

## 5. REF

| Resource | Type | Link | Notes |
| --- | --- | --- | --- |
| Conc GitHub | GitHub | [github.com/sourcegraph/conc](https://github.com/sourcegraph/conc) | Source code |
| Conc GoDoc | Official docs | [pkg.go.dev/github.com/sourcegraph/conc](https://pkg.go.dev/github.com/sourcegraph/conc) | API reference |
| Conc Blog Post | Blog | [about.sourcegraph.com](https://about.sourcegraph.com/blog/building-conc-better-structured-concurrency-for-go) | Design rationale |

---

## 6. RECOMMEND

You have enough context from **Conc** to proceed with purpose. The directions below help expand to the right tooling, runtime, or related pattern layer.

| Next step | When | Reason | File/Link |
| --- | --- | --- | --- |
| **Ants** | High-perf | Goroutine reuse, auto-scale | [12-ants.md](./12-ants.md) |
| **Asynq** | Distributed | Cross-process tasks | [15-asynq.md](./15-asynq.md) |
| **iter.Map + GORM** | GORM + Map | Parallel DB reads type-safe | [orm/03](../orm/03-querying.md) |
| **conc.ErrorPool + http.Client** | HTTP fanout | Parallel API calls + collect all errors | Pattern |
| **conc.Pool + channels** | Stream processing | Structured concurrency for pipeline stages | Pattern |
| **conc panics re-raised** | Testing | Easier to test than errgroup — panics not swallowed | `conc` |
