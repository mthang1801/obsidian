<!-- tags: golang, concurrency, goroutines -->
# ⚡ Promise & Async — Concurrency TS → Go

> TypeScript runs async code on a single-thread event loop. Go distributes goroutines across multiple OS threads. Translating `Promise.all` requires explicit channel synchronization — goroutines without exit conditions leak memory.

📅 Created: 2026-03-23 · 🔄 Updated: 2026-04-19 · ⏱️ 18 min read

## 1. DEFINE

A frontend developer builds a backend endpoint that aggregates three API calls. They write `go fetchUser()`, `go fetchOrders()`, `go fetchPermissions()` — three goroutines fire off. But the `main` function returns immediately after launching them. Unlike JavaScript, where `await Promise.all(...)` blocks until all promises resolve, Go's `main` exits and the goroutines are silently killed.

The fix requires explicit synchronization: `sync.WaitGroup` for fire-and-forget tasks, or `errgroup` for tasks that return errors. `errgroup` is the direct equivalent of `Promise.all` — it waits for all goroutines to complete and cancels the group if any one fails.

### 1.1 Invariants & Failure Modes

| Boundary | Core Responsibility |
| --- | --- |
| **Goroutines** | Lightweight threads multiplexed over OS threads. Never spawn without a concrete exit condition. |
| **`errgroup`** | The direct `Promise.all` replacement. Cancels sibling goroutines when one returns an error. |

| Rule | Rationale |
| --- | --- |
| **Always pass `context.Context`** | The Go equivalent of `AbortController`. Provides timeout and cancellation propagation. |
| **Buffer channels to match concurrency** | Unbuffered channels block the sender until a receiver reads. If no one reads, the goroutine leaks. |

### 1.2 Failure Cascades

- **The zombie goroutine:** A goroutine calls an external API without a context timeout. The API hangs. The goroutine blocks forever, leaking memory across the process lifetime.
- **The data race return:** Developers assign results to shared variables inside goroutines — `user = fetchUser()`. Two goroutines write to the same variable without synchronization. The race detector catches it; production without `-race` silently corrupts data.

## 2. VISUAL

JavaScript's event loop serializes async operations on one thread. Go's scheduler distributes goroutines across all CPU cores. The visual maps the conceptual difference.

![Promise Async Compare](./images/04-promise-async-compare.png)

*Figure: JS event loop (left) serializes callbacks on one thread. Go scheduler (right) distributes goroutines across multiple OS threads. Channels replace `Promise.then()` for passing results between goroutines.*

## 3. CODE

With the concurrency model established, the code below demonstrates three patterns: basic `await` via channels, `Promise.all` via `errgroup`, and `Promise.race` via `select`.

### Example 1: Basic — The await translation

> **Goal**: Wait for a background operation, equivalent to `const result = await fetchUser(1)`.
> **Approach**: Return a buffered channel from the async function. The caller reads with `<-ch` which blocks until the value arrives.
> **Complexity**: O(1) — one goroutine, one channel send/receive.

```go
// basic_async.go
package async

import (
	"fmt"
	"time"
)

// TS: async function fetchUser(id) { return "User" }
func FetchUserAsync(id int) <-chan string {
	ch := make(chan string, 1) // Buffer prevents block if receiver vanishes.
	
	go func() {
		time.Sleep(100 * time.Millisecond) // Simulate IO
		ch <- fmt.Sprintf("User_%d", id)
	}()
	
	return ch
}

func ExecuteAwait() {
	// TS: const user = await fetchUser(1)
	userChannel := FetchUserAsync(1)
	
	result := <-userChannel // Blocks until the goroutine sends
	fmt.Println("Result", result)
}
```

> **Takeaway**: The buffered channel (`make(chan string, 1)`) is critical. If the caller abandons the channel, an unbuffered send blocks forever — the goroutine leaks. A buffer of 1 lets the goroutine send and exit even without a receiver.

---

### Example 2: Intermediate — Promise.all with errgroup

> **Goal**: Run multiple concurrent tasks and wait for all, equivalent to `await Promise.all([...])`.
> **Approach**: `errgroup.WithContext` creates a group that cancels all goroutines if any one returns an error.
> **Complexity**: O(N) — one goroutine per task.

```go
// errgroup_sync.go
package async

import (
	"context"
	"fmt"
	"time"
	"golang.org/x/sync/errgroup"
)

func ExecutePromiseAll() error {
	var user, metadata string
	
	group, _ := errgroup.WithContext(context.Background())
	
	group.Go(func() error {
		time.Sleep(100 * time.Millisecond)
		user = "Alice"
		return nil
	})
	
	group.Go(func() error {
		time.Sleep(150 * time.Millisecond)
		metadata = "Authorized"
		return nil
	})
	
	// TS: await Promise.all([task1, task2])
	if err := group.Wait(); err != nil {
		return err
	}
	
	fmt.Printf("Results: %s, %s\n", user, metadata)
	return nil
}
```

> **Why `errgroup` instead of `sync.WaitGroup`?** `WaitGroup` has no error handling — if one goroutine fails, the others keep running and the caller never learns about the failure. `errgroup` returns the first error and (when created with `WithContext`) cancels the derived context so other goroutines can check `ctx.Err()` and exit early.

---

### Example 3: Advanced — Promise.race with select

> **Goal**: Return the fastest response and discard slower ones, equivalent to `await Promise.race([...])`.
> **Approach**: `select` blocks until the first channel receives a value. `time.After` provides a timeout fallback.
> **Complexity**: O(N) goroutine spawns; O(1) selection.

```go
// race_condition.go
package async

import (
	"fmt"
	"time"
)

func ExecutePromiseRace() string {
	fastChannel := make(chan string, 1)
	slowChannel := make(chan string, 1)

	// TS: const result = await Promise.race([task1, task2])
	go func() {
		time.Sleep(50 * time.Millisecond)
		fastChannel <- "Primary DB"
	}()

	go func() {
		time.Sleep(200 * time.Millisecond)
		slowChannel <- "Fallback DB"
	}()

	select {
	case result := <-fastChannel:
		return result
	case result := <-slowChannel:
		return result
	case <-time.After(300 * time.Millisecond):
		return "Timeout"
	}
}
```

> **Takeaway**: The losing goroutine keeps running after `select` picks a winner. It sends to its channel, but nobody reads — the buffered channel absorbs the value and the goroutine exits cleanly. Without buffering, the losing goroutine would block forever.

## 4. PITFALLS

| # | Defect | Fix |
| --- | --- | --- |
| 1 | Spawning goroutines without context cancellation | Always pass `context.WithCancel` or `context.WithTimeout`. Cancel on error or function exit. |
| 2 | Writing results to shared variables from goroutines | Use channels to return values, or protect shared state with `sync.Mutex`. |
| 3 | Missing timeouts on long-running goroutines | Bind `time.After` or `context.WithTimeout` in `select` blocks to prevent infinite waits. |

## 5. REF

| Resource | Link |
| --- | --- |
| Context Package | [pkg.go.dev/context](https://pkg.go.dev/context) |
| Go Concurrency Patterns | [go.dev/blog/pipelines](https://go.dev/blog/pipelines) |

## 6. RECOMMEND

| Extension | When | Rationale |
| --- | --- | --- |
| [Context Patterns](../../concurrency/03-context.md) | When propagating timeouts through call chains | Deep cancellation trees with `context.WithTimeout` |
| [Worker Pools](../../concurrency/08-worker-pool-tunny.md) | When limiting concurrent goroutine count | Prevent memory exhaustion from unbounded goroutine spawning |

**Navigation**: [← Map Utils](./03-object-map-utils.md) · [→ Date Time Utilities](./05-date-time.md)
