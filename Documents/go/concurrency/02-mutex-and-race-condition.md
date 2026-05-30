<!-- tags: golang -->
# 02 — Mutex & Race Condition

> **Foundation**: Protecting shared memory when multiple goroutines access it concurrently.

📅 Created: 2026-03-20 · 🔄 Updated: 2026-04-19 · ⏱️ 15 min read

| Aspect         | Detail                                                        |
| -------------- | ------------------------------------------------------------- |
| **Concept**    | Mutex (mutual exclusion), RWMutex, sync/atomic                |
| **Use case**   | Protecting shared state, concurrent counters, read-heavy caches |
| **Go stdlib**  | `sync.Mutex`, `sync.RWMutex`, `sync/atomic`, `-race` flag     |
| **Key insight**| Race conditions are silent killers — `-race` is a mandatory vaccine |

---

## 1. DEFINE

Channels solve ownership transfer. Mutexes solve shared-state protection. Picking the wrong one for the job — or forgetting both — creates race conditions: bugs that pass tests 99 out of 100 times, corrupt data silently, and only surface as a Sev-1 in production at peak traffic.

You have a simple counter: 100 goroutines all increment `counter++`. Expected result is 100, but after running you see 97, 99, 100 — different every time. Worse, production reports no errors — data silently goes wrong and nobody knows. That is a **race condition**: multiple goroutines read and write the same variable without synchronization. **Mutex** exists to solve exactly this: it guarantees only 1 goroutine enters the critical section at a time. But there is a trap: passing a `SafeCounter` by value (copying the struct) copies the mutex — 2 copies share lock state → race condition returns. That trap will surface in PITFALLS.

### Race Condition

A **race condition** occurs when ≥ 2 goroutines access the same variable concurrently, and at least 1 goroutine **writes**. The result depends on execution order — **non-deterministic**.

### Mutex (Mutual Exclusion)

**`sync.Mutex`** ensures only **1 goroutine** accesses the critical section at a time.

### Mutex vs RWMutex vs Atomic

| Mechanism        | Use case                        | Performance        |
| ---------------- | ------------------------------- | ------------------ |
| **sync.Mutex**   | Read + Write — exclusive access | Moderate           |
| **sync.RWMutex** | Many readers, few writers       | Good for read-heavy |
| **sync/atomic**  | Single variable (counter, flag) | Fastest            |
| **Channel**      | Communication-based sync        | Most flexible      |

### Invariants

- **Lock first, Unlock after** — always `defer mu.Unlock()` right after `mu.Lock()`
- **Do not lock twice** (same goroutine) → deadlock
- **RWMutex**: multiple `RLock` concurrently is fine; `Lock` must wait for all `RUnlock` calls
- **Atomic**: only for a single variable, not for structs or multi-field updates

### Failure Modes

| Failure         | Cause                                | Prevention                   |
| --------------- | ------------------------------------ | ---------------------------- |
| **Data race**   | Read + Write without sync            | Use Mutex or channel         |
| **Deadlock**    | Different lock order across goroutines | Always lock in the same order |
| **Forgot Unlock** | Missing `mu.Unlock()`              | Always `defer mu.Unlock()`   |
| **Nested lock** | Lock then Lock again → deadlock      | Design to avoid nesting      |

Race condition, mutex, RWMutex, atomic, invariants — theory is covered. Let us see what race conditions and mutex mechanics look like visually.

---
## 2. VISUAL

This article has two distinct visual jobs: choosing the right primitive for a shared-state problem, and spotting common failure modes before they become production bugs.

### Shared-State Protection vs Ownership Transfer

![Mutex vs channel for coordination](./images/02-mutex-and-race-condition-mutex-vs-channel-compare.png)

*If the job is protecting a shared structure, mutex is usually the right tool. If the job is transferring ownership or coordinating multiple stages, channel is the more natural framework.*

### Race & Locking Failure Modes

![Race and locking failure modes](./images/02-mutex-and-race-condition-failure-modes.png)

*The most dangerous part of lock-based code is not just data races. It is also a lock scope that is too wide, split ownership, or choosing RWMutex for a workload that is not truly read-heavy.*

### Supporting View: `RWMutex` wins only when read dominance is real

```text
Readers: RLock ━━━━━━━━━ RUnlock
Readers:   RLock ━━━━━━━━━━━ RUnlock
Writer:                    Lock ━━━ Unlock

If writes are still frequent or the critical section is long,
RWMutex may be more complex without being faster than Mutex.
```

*`RWMutex` is not a default upgrade from `Mutex`. It is only worth it when reads overwhelm writes and the lock scope is short enough.*

Looking at both PNG visuals first will help you read code with the right question: is the problem shared memory or staged communication, and which failure mode must be blocked from the design phase.

---

## 3. CODE

You have seen the flow of signals, requests, or goroutines in **Mutex & Race Condition**. Now shift to code to check which parts must be written tightly to avoid paying the production price.

---

### Example 1: Basic — Race Condition — Detection with Race Detector

100 goroutines all increment `counter++`. Expected result: 100. Actual result: 97, 99, 100 — different every time. Production reports no errors — data silently goes wrong.

This is a race condition in its simplest form. The first step is not to fix — it is to **prove** it exists using the `-race` flag.

```go
package main

import (
    "fmt"
    "sync"
)

func main() {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // ❌ BUG: Race condition!
    // 100 goroutines increment counter without sync.
    // Run: go run -race main.go → you will see a WARNING
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    counter := 0
    var wg sync.WaitGroup

for range 100 { // Go 1.22+
        wg.Add(1)
        go func() {
            defer wg.Done()
            // All 100 goroutines read + write counter simultaneously
            // → data race: result is non-deterministic
            counter++ // ← RACE! Read-modify-write is not atomic
        }()
    }

wg.Wait()
    // Expected: 100
    // Actual: could be 97, 99, 100, ... (non-deterministic)
    fmt.Println("Counter:", counter)
}
```

**Detection**:

```bash
go run -race main.go
# WARNING: DATA RACE
# Write at 0x00c0000b4010 by goroutine 7:
# Previous write at 0x00c0000b4010 by goroutine 6:
```

**Achieved**: Proved the race condition exists — results differ on each run. The `-race` flag catches it immediately during development.

**Caveat**: `-race` slows execution 2-10x, so use it only in dev/test, not production. More importantly: the race detector only finds races on **executed code paths** — missing tests means missing coverage.

**Use when**: Always. **ALWAYS** run `go test -race ./...` — this is a mandatory vaccine, not a "nice-to-have."

The race detector only detects. To fix, you need Mutex — ensuring only 1 goroutine enters the critical section at a time.

---

### Example 2: Intermediate — sync.Mutex — Fixing Race Conditions

The race detector pointed out the broken spot. The problem: `counter++` is read-modify-write — 3 steps where the scheduler can interleave at any point.

`sync.Mutex` solves this: wrap the critical section in `Lock()/Unlock()`, guaranteeing only 1 goroutine enters at a time. The standard pattern is to embed Mutex in the struct that holds shared data.

```go
package main

import (
    "fmt"
    "sync"
)

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// SafeCounter: goroutine-safe counter using Mutex
// Pattern: embed Mutex in the struct holding shared data
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
type SafeCounter struct {
    mu    sync.Mutex // protects counter
    count int
}

func (c *SafeCounter) Increment() {
    c.mu.Lock()         // ← Only 1 goroutine enters the critical section
    defer c.mu.Unlock() // ← ALWAYS defer Unlock right after Lock
    c.count++           // ← Critical section: safe read-modify-write
}

func (c *SafeCounter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.count // ← Reads also need a lock to avoid stale values
}

func main() {
    counter := &SafeCounter{}
    var wg sync.WaitGroup

for range 1000 { // Go 1.22+
        wg.Add(1)
        go func() {
            defer wg.Done()
            counter.Increment()
        }()
    }

wg.Wait()
    fmt.Println("Counter:", counter.Value()) // Always = 1000 ✅
}
```

**Achieved**: Counter **always equals 1000** — deterministic, race-free. `go run -race` shows no warnings.

**Caveat**: Mutex is NOT reentrant — locking twice in the same goroutine causes a deadlock. **Reads also need a lock** if another goroutine is writing — skipping the lock on `Value()` is a hidden bug.

**Use when**: Any struct with shared state between goroutines. Standard pattern: embed `sync.Mutex` in the struct; expose methods, not fields.

> **Why `defer mu.Unlock()` instead of calling it directly?**
> If the function has multiple `return` paths or panics mid-way, `mu.Unlock()` at the end will never run → permanent deadlock. `defer` guarantees Unlock always runs when the function exits. Cost: nanoseconds. Cost of debugging a deadlock: hours.

Mutex fixes races by allowing only 1 goroutine into the critical section. But when reads far outweigh writes (cache, config), Mutex blocks readers unnecessarily. RWMutex allows parallel readers.

---

### Example 3: Advanced — sync.RWMutex — Optimizing read-heavy workloads

Mutex protects shared state — but it blocks **all** goroutines, even those that only read. An in-memory cache read 10,000 times/second, written 10 times/second — 99.9% of traffic gets serialized unnecessarily.

`sync.RWMutex` separates read locks (multiple goroutines concurrently) from write locks (exclusive). But RWMutex is NOT "a better Mutex" — it wins only when reads **overwhelm** writes.

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Cache: read-heavy → use RWMutex
// - Multiple goroutines read concurrently: RLock (no blocking)
// - 1 goroutine writes: Lock (blocks all readers and writers)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
type Cache struct {
    mu    sync.RWMutex
    items map[string]string
}

func NewCache() *Cache {
    return &Cache{items: make(map[string]string)}
}

// Get: multiple goroutines can call concurrently (RLock)
func (c *Cache) Get(key string) (string, bool) {
    c.mu.RLock()         // ← Read lock: does not block other readers
    defer c.mu.RUnlock()
    val, ok := c.items[key]
    return val, ok
}

// Set: only 1 goroutine writes at a time (Lock)
func (c *Cache) Set(key, value string) {
    c.mu.Lock()          // ← Write lock: blocks ALL readers + writers
    defer c.mu.Unlock()
    c.items[key] = value
}

func main() {
    cache := NewCache()
    var wg sync.WaitGroup

// 1 writer (slow)
    wg.Add(1)
    go func() {
        defer wg.Done()
        for i := range 5 { // Go 1.22+
            key := fmt.Sprintf("key-%d", i)
            cache.Set(key, fmt.Sprintf("value-%d", i))
            fmt.Printf("[Writer] Set %s\n", key)
            time.Sleep(100 * time.Millisecond)
        }
    }()

// 10 readers (fast, concurrent)
    for r := range 10 { // Go 1.22+
        wg.Add(1)
        go func(readerID int) {
            defer wg.Done()
            for i := range 5 { // Go 1.22+
                key := fmt.Sprintf("key-%d", i)
                if val, ok := cache.Get(key); ok {
                    fmt.Printf("[Reader %d] Got %s=%s\n", readerID, key, val)
                }
                time.Sleep(50 * time.Millisecond)
            }
        }(r)
    }

wg.Wait()
}
```

**Achieved**: 10 readers run **in parallel** — they do not block each other. The writer only blocks the goroutine currently holding the lock — better throughput than Mutex for read-heavy workloads.

**Caveat**: RWMutex pays off only when reads far outweigh writes (ratio ≥ 10:1). If reads ≈ writes, the overhead of managing two lock types makes RWMutex **slower** than Mutex. The writer can also suffer **starvation** if readers continuously hold RLock.

**Use when**: Caches, config stores, read-heavy data where writes are rare. Accidentally using `RLock` for a write operation creates a race condition — the compiler does not catch this mistake.

> **Why not use RWMutex instead of Mutex for everything?**
> RWMutex manages a reader count + writer exclusion — higher overhead than Mutex. With a read ≈ write workload, that overhead gains nothing because readers do not truly read concurrently more often. RWMutex benefits only when reads **overwhelm** writes.

RWMutex covers read-heavy workloads. But when you only need an atomic increment/decrement on a single variable — counter, flag — Mutex overhead is unnecessary. `sync/atomic` uses CPU instructions and is 2-5x faster.

---

### Example 4: Expert — sync/atomic — Lightweight for a single variable

RWMutex optimizes read-heavy workloads, but you only need to increment a counter. Lock, defer unlock, unlock — that overhead is unnecessary for a single `+= 1`.

`sync/atomic` uses CPU instructions directly (LOCK CMPXCHG on x86) — no syscall, no context switch. 2-5x faster than Mutex. But: **only for a single variable**.

```go
package main

import (
    "fmt"
    "sync"
    "sync/atomic"
)

func main() {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // atomic: CPU-level instruction, no lock needed
    // Only for SINGLE variables: int32, int64, uint64, uintptr, pointer
    // 2-5x faster than Mutex for simple operations
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    var counter atomic.Int64 // Go 1.19+ — type-safe atomic
    var wg sync.WaitGroup

for range 1000 { // Go 1.22+
        wg.Add(1)
        go func() {
            defer wg.Done()
            counter.Add(1) // ← Atomic increment: hardware-level, no lock
        }()
    }

wg.Wait()
    fmt.Println("Counter:", counter.Load()) // Always = 1000 ✅

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Compare-And-Swap (CAS) — conditional atomic update
    // "Only update if the current value equals expected"
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    var flag atomic.Bool
    swapped := flag.CompareAndSwap(false, true) // ← Set true only if currently false
    fmt.Println("Swapped:", swapped)            // true (first time)
    swapped = flag.CompareAndSwap(false, true)
    fmt.Println("Swapped:", swapped)            // false (already true)
}
```

**Achieved**: Counter always equals 1000 with atomic — 2-5x faster than Mutex. `CompareAndSwap` opens the door to lock-free algorithms.

**Caveat**: Only for a **single variable** — 2 atomic ops on 2 different variables do not guarantee atomicity of the pair. Go 1.19+: use `atomic.Int64`, `atomic.Bool` — far more type-safe than `atomic.AddInt64(&x, 1)`.

**Use when**: Counters, flags, metrics — anywhere you need concurrent increment/load on a single variable. When you need to update > 1 field at the same time → fall back to Mutex.

> **Why is atomic faster than mutex?**
> Mutex uses an OS-level syscall (futex on Linux) under contention — context switches cost microseconds. Atomic uses CPU instructions — no syscall, no context switch, completes in nanoseconds. But atomic is only safe for a single variable — do not try to use 2 atomic ops to fake a multi-field update.

Returning to the trap from the beginning: passing a `SafeCounter` by value copies the mutex. You now know race detection, Mutex, RWMutex, and atomic. Here comes the most dangerous part.

---

## 4. PITFALLS

The correct mechanism of **Mutex & Race Condition** is in place. The traps below are where people get timing, ownership, or evidence wrong — and only realize it when the incident has already exploded.

| # | Severity | Mistake | Consequence | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Fatal | **Copy Mutex** | Both copies share lock state → race | Mutex must NOT be copied (pass by value) → use pointers |
| 2 | 🔴 Fatal | **Nested lock** | Lock A → Lock B → Deadlock | Always lock in the same order |
| 3 | 🔴 Fatal | **RLock for write** | Race condition — multiple goroutines write concurrently | Use `Lock()` for every write operation |
| 4 | 🟡 Common | **Forget `defer Unlock`** | Unlock gets skipped if function panics or returns early | Always `defer mu.Unlock()` right after `Lock()` |
| 5 | 🟡 Common | **Forget `-race` flag** | Hidden race condition, only exposed in production | Always: `go test -race ./...` |
| 6 | 🔵 Minor | **Atomic for struct** | Atomic works only for single vars — structs need multiple fields | Use Mutex for structs |

### 🔴 Pitfall #1 — Copy Mutex: a hidden bug in struct passed by value

This code looks entirely correct:

```go
type SafeCounter struct {
    mu    sync.Mutex
    count int
}

func (c SafeCounter) Value() int { // ← receiver by value = COPY struct
    c.mu.Lock()                     // locks the COPY, not the original
    defer c.mu.Unlock()
    return c.count
}
```

`Value()` receives `SafeCounter` by value → Go copies the entire struct, including `sync.Mutex`. Result: `c.mu` inside `Value()` is a copy — locking it protects nothing. Other goroutines still access the original freely.

**Fix**: Always use a pointer receiver for structs containing a Mutex: `func (c *SafeCounter) Value() int`.

You have covered race detection, Mutex, RWMutex, atomic, and the copy/nested/starvation traps. The resources below help you go deeper.

---

## 5. REF

| Resource | Type | Link | Notes |
| --- | --- | --- | --- |
| Go Blog — Race Detector | Official blog | [go.dev/doc/articles/race_detector](https://go.dev/doc/articles/race_detector) | How to use the `-race` flag |
| sync package | Official docs | [pkg.go.dev/sync](https://pkg.go.dev/sync) | Mutex, RWMutex, WaitGroup |
| sync/atomic | Official docs | [pkg.go.dev/sync/atomic](https://pkg.go.dev/sync/atomic) | Lock-free atomic operations |
| Go Memory Model | Official spec | [go.dev/ref/mem](https://go.dev/ref/mem) | Happens-before guarantees |

---

## 6. RECOMMEND

You just went from detecting races (detector) → fixing races (Mutex) → optimizing read-heavy (RWMutex) → optimizing single-var (atomic). From here, each next step depends on whether the real problem is shared-state protection or coordination.

| Next step | When | Reason | File/Link |
| --- | --- | --- | --- |
| **01 — Goroutines & Channels** | When you still confuse handoff with shared memory | Lock down the boundary between channel jobs and lock jobs | [01-goroutines-and-channels.md](./01-goroutines-and-channels.md) |
| **03 — Context** | When lock contention accompanies request cancellation or timeout | Separate shared-state safety from lifecycle control | [03-context.md](./03-context.md) |
| **11 — singleflight** | When multiple goroutines duplicate the same work item | Duplicate suppression is often more accurate than a coarse lock | [11-singleflight.md](./11-singleflight.md) |
| **03 — Memory Model** | When you want to understand happens-before behind locks and atomics | Connect the race detector to visibility guarantees | [../advanced/03-memory-model.md](../advanced/03-memory-model.md) |
| **05 — Performance & pprof** | When you suspect contention or a critical section that is too wide | Use evidence instead of guessing which lock is hot | [../advanced/05-performance-pprof.md](../advanced/05-performance-pprof.md) |

---

**Links**: [← Goroutines & Channels](./01-goroutines-and-channels.md) · [→ Context](./03-context.md)
