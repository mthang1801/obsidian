<!-- tags: golang, memory -->
# 🎯 Pointers & Memory — Stack, Heap, Escape, Alloc

> Stack vs heap, pointer semantics, allocation paths, escape analysis, and alloc tuning in Go.

📅 Created: 2026-03-20 · 🔄 Updated: 2026-04-19 · ⏱️ 24 min read

| Aspect | Detail |
| --- | --- |
| **Concept** | Pointer semantics, stack vs heap, allocation, escape analysis |
| **Use case** | Reading compiler outputs correctly, reducing allocs/op, avoiding GC pressure |
| **Go stdlib** | `unsafe`, `testing`, `sync`, `bytes`, `strings` |
| **Key insight** | Go does not allow you to choose stack or heap by syntax; the compiler and runtime decide |

---

## 1. DEFINE

Imagine getting a regression after what seemed like a harmless optimization. The old handler returned `User` by value. A refactor changed it to `*User` to "reduce copies". Other helpers were changed to `new(T)`. Small benchmarks showed no issues. But under real traffic, `allocs/op` spiked, the heap profile grew, and GC slowed down the hot path.

If you have been in that situation, you know the problem is not "is a pointer better than a value". The problem is using a simple mental model where the compiler, runtime, stack growth, heap allocation, and escape analysis are all intervening. This article replaces that mental model with an accurate one for code review, benchmarks, and debugging.

### 1.1 Value vs Pointer Semantics

In Go, the first question is not "stack or heap", but "are we passing a value or passing access to a shared object".

| Mechanism | What is Passed | Core Consequence |
| --- | --- | --- |
| `func f(x T)` | A copy of `T` | The function gets a separate value; changes do not affect the caller |
| `func f(x *T)` | The address to `T` | The function can mutate the original data, but must face `nil` and shared state |
| Method value receiver | A copy of the receiver | Safe for small types and immutable state |
| Method pointer receiver | The address of the receiver | Use when needing to mutate or avoid copying large structs |

A pointer exclusively solves two things:

- Avoid copying a large or mutation-sensitive value
- Allow multiple code sections to see the same object

A pointer **does not** automatically mean:

- The object is definitely on the heap
- The code is definitely faster
- The GC will have a harder or easier time

### 1.2 What Stack vs Heap Actually Means In Go

`stack` and `heap` are not keywords. They are two different memory spaces that the runtime and compiler select for your data.

| Property | Stack | Heap |
| --- | --- | --- |
| Allocation | Tied to a stack frame or internal compiler backing storage | Managed by the runtime |
| Lifetime | Ends when the frame no longer needs the data | Extended until the object is no longer reachable |
| Cost | Extremely cheap if the compiler proves a short lifetime | More expensive due to allocator and GC involvement |
| Ownership | Resides close to the current execution flow | Can outlive the scope of the current function |
| GC | No mark/sweep required for stack frames | Garbage Collector is involved |

The most important point: in Go, **you do not write syntax to choose stack or heap**. You write code. The compiler analyzes it. If the compiler proves the object does not need to outlive the current scope, it can keep the object on the stack or in registers. If it cannot prove this, the object must go to the heap.

### 1.3 Allocation Paths: `var`, `new`, `make`, Composite Literal

This is where many Go learners are tricked by syntax.

| Syntax | What it does | What it **does not** guarantee |
| --- | --- | --- |
| `var x T` | Creates a zero value of `T` | Does not guarantee `x` is on the stack or heap |
| `x := T{...}` | Creates a value of `T` | Does not guarantee the value won't escape |
| `new(T)` | Returns a `*T` pointing to a zero value | Does not mean "always heap" |
| `make([]T, ...)` | Creates slice/map/channel runtime header | Does not mean the backing storage is definitely on the stack |
| `&T{...}` | Returns a pointer to a composite literal | Does not automatically mean "bad" or "heap-heavy" |

Points to keep in mind:

- `new(T)` gives you **pointer semantics**
- `make` creates runtime-managed structures like slices, maps, and channels
- The actual data placement is ultimately an escape analysis and runtime problem

If you just memorize `new = heap`, you will misread compiler outputs from the very beginning.

### 1.4 Escape Analysis: The Hidden Decision

Escape analysis is the phase where the compiler asks a direct question:

> "Does this object need to outlive the scope where it was created?"

If the answer is "no", the compiler can keep it on the stack. If the answer is "yes", or "I cannot prove it is no", the compiler must put the object on the heap.

Common signals that cause objects to escape:

- Returning a pointer to local data
- Passing a value into an interface where the compiler cannot keep it purely local
- Capturing a local variable within a closure that might outlive the parent frame
- Passing a reference to a different goroutine
- Creating an object that is too large or whose shape prevents the compiler from keeping it on the stack

Two facts must be clearly distinguished:

1. Using a pointer is **not enough** to conclude an object is on the heap
2. Not using a pointer **does not guarantee** the object is on the stack

### 1.5 Invariants & Failure Modes

This is the expert layer of this topic: facts that hold true whether you like them or not.

- `new(T)` returns a `*T`, but placement is still decided by the compiler.
- `return &x` is valid in Go because the compiler can transfer `x` to the heap when needed.
- A slice header might be local, but its backing array is what you actually care about when discussing allocs.
- `[]T` vs `[]*T` is not just a style choice. They change cache locality, GC scan costs, and mutation models.
- Benchmarks do not tell the whole story if you do not also look at `allocs/op`, `B/op`, and heap profiles.

The theory up to this point is enough to stop confusing names with mechanisms. But if you do not visualize object lifetime, you will still guess wrong about where the allocation actually happens.

---

The failure modes above are worth re-reading before your next allocation debugging session. The most common trap: seeing `new(T)` and concluding "heap", or switching from `[]T` to `[]*T` without checking locality and GC scan cost.

## 2. VISUAL

Tables and invariants describe _what exists_ — but lifetime does not appear visibly. You only see the consequences via alloc counts, heap profiles, or GC pressure. This is why the visual section must directly target the mental model, not just draw pretty pointer diagrams.

![Pointers and memory mental model](./images/04-pointers-memory-mental-model.png)

*Figure: Mental-model card separating the four most confusing aspects of Go memory behavior: the local value path, the pointer myth, common escape paths, and the rule of measuring instead of guessing.*

When these four ideas are correctly positioned, the code below becomes valuable: you will read examples by asking _what lifetime is the compiler seeing?_ instead of guessing _is this on the heap or stack?_.

![Escape analysis decision tree](./images/04-escape-analysis-tree.png)

_Figure: The compiler's escape analysis decision tree — four questions determine stack vs heap placement. Verify with `go build -gcflags='-m'` instead of guessing._

## 3. CODE

We now have the mental model for **Pointers & Memory — Stack, Heap, Escape, Alloc**. Let us map it to code to see how every small decision — value or pointer, preallocating or not, pooling or newly creating — actually changes allocation behavior.

### Example 1: Basic — How pointer semantics differ from value semantics

> **Goal**: Anchor the difference between copying and shared access before discussing stack/heap.
> **Approach**: Use a struct large enough to show copying is real, but small enough to avoid making you assume pointers are always optimal.
> **Example**: `markShippedByValue(order)` does not modify the original order; `markShippedByPointer(&order)` does.
> **Complexity**: O(1) time, O(1) space.

```go
package main

import "fmt"

type Order struct {
	ID       int64
	Status   string
	Amount   int64
	Currency string
}

func markShippedByValue(o Order) {
	// o is a copy of the caller's value.
	o.Status = "shipped"
}

func markShippedByPointer(o *Order) {
	if o == nil {
		return
	}
	// o points to the exact object the caller holds.
	o.Status = "shipped"
}

func main() {
	order := Order{
		ID:       42,
		Status:   "pending",
		Amount:   150_000,
		Currency: "VND",
	}

	markShippedByValue(order)
	fmt.Println("after value call:", order.Status) // pending

	markShippedByPointer(&order)
	fmt.Println("after pointer call:", order.Status) // shipped
}
```

> **Takeaway**: At a basic level, a pointer is primarily a choice of semantics: you either want to mutate the original object or work with a copy.
> **Caveat**: Nothing in this example is sufficient to conclude if the object is on the stack or heap. Pointer semantics and allocation placement are two different questions.
> **When to use**: When you are reviewing code and need to distinguish between copy-semantics bugs versus allocation/lifetime bugs.

### Example 2: Intermediate — `new`, `&value`, closures, and escape analysis

> **Goal**: Connect escape analysis theory to everyday Go patterns.
> **Approach**: Place similar-looking functions side-by-side that have different lifetimes, then read `-gcflags="-m -m"` alongside the code.
> **Example**: `buildValue()` returns a value, `buildPointer()` returns a pointer, `captureInClosure()` keeps a local variable alive via a closure.
> **Complexity**: O(1) time, O(1) space per call; the important part is the allocation behavior.

```go
package main

import "fmt"

type User struct {
	ID   int64
	Name string
}

func buildValue() User {
	u := User{ID: 1, Name: "Lan"}
	return u
}

func buildPointer() *User {
	u := User{ID: 2, Name: "Minh"}
	return &u
}

func buildWithNew() *User {
	u := new(User)
	u.ID = 3
	u.Name = "Anh"
	return u
}

func captureInClosure() func() string {
	label := "request-hot-path"
	return func() string {
		return label
	}
}

func main() {
	fmt.Println(buildValue())
	fmt.Println(buildPointer())
	fmt.Println(buildWithNew())

	next := captureInClosure()
	fmt.Println(next())
}
```

```bash
go build -gcflags="-m -m" main.go
```

```text
# illustrative output, exact wording varies by Go version
./main.go:14:6: can inline buildValue
./main.go:20:2: u escapes to heap
./main.go:24:10: new(User) escapes to heap
./main.go:31:2: label escapes to heap
```

> **Why isn't `new(User)` always "heap syntax"?**
> `new(User)` only means you want a `*User`. Heap or stack placement still depends on whether that pointer needs to outlive the current scope. In this example, `buildWithNew()` returns a pointer, so the object must live after the function finishes; thus, the compiler places it on the heap. But in another path, if the pointer is only used internally and does not escape, the compiler might keep the object local.
>
> **Why do closures often cause people to misread allocations?**
> On the surface, it is just a tiny `label` string variable. But a closure detaches the lifetime of `label` from the current stack frame. When a closure can outlive its parent function, the compiler has to choose the safe path.

> **Takeaway**: Escape analysis does not care what syntax you prefer. It only cares whether an object needs to live beyond the current scope.
> **Caveat**: Do not memorize every line of compiler output as a rigid rule. The same code block can yield slightly different output depending on the compiler version.
> **When to use**: When reading `-gcflags="-m -m"` and mapping compiler messages to the correct lifetime problem in your source code.

### Example 3: Advanced — Alloc pressure often comes from the data path's shape

> **Goal**: Show that alloc pressure does not just come from `return &x`, but also from choosing `[]T` versus `[]*T`, pre-allocating versus not, and forcing the runtime to continuously grow backing storage.
> **Approach**: Compare two data paths doing the same thing: accumulating users and returning the result. One path continuously creates pointers and appends without preallocating; the other keeps a `[]User` contiguous and allocates the exact capacity upfront.
> **Example**: `buildPointerSlice` vs `buildValueSlice`.
> **Complexity**: O(n) time; allocation behavior is distinctly different.

```go
package main

import "fmt"

type User struct {
	ID   int64
	Name string
}

func buildPointerSlice(n int) []*User {
	var users []*User
	for i := 0; i < n; i++ {
		u := &User{
			ID:   int64(i),
			Name: fmt.Sprintf("user-%d", i),
		}
		users = append(users, u)
	}
	return users
}

func buildValueSlice(n int) []User {
	users := make([]User, 0, n)
	for i := 0; i < n; i++ {
		users = append(users, User{
			ID:   int64(i),
			Name: fmt.Sprintf("user-%d", i),
		})
	}
	return users
}

func main() {
	fmt.Println(len(buildPointerSlice(4)))
	fmt.Println(len(buildValueSlice(4)))
}
```

```bash
go test -bench=. -benchmem
```

> **Why isn't `[]*User` always bad, but often more expensive than you think?**
> `[]*User` is useful when every object requires its own identity, shared mutation, or is too massive for value-copying to be efficient. But the trade-off is having far more objects on the heap, worse memory locality, and requiring the GC to scan many more pointers. For batch data processing or read-heavy paths, `[]User` generally provides a compact and cache-friendly memory layout.
>
> **Why is preallocation more important than many realize?**
> If you already know `n`, utilizing `make([]User, 0, n)` does more than just reduce reallocations. It also reduces the number of times the backing array must grow and copy its underlying data. In a hot path, this type of simple optimization is far more sustainable than attempting tricks with the `unsafe` package.

> **Takeaway**: A significant portion of allocation pressure originates from data shapes and growth patterns, not just a single `return &x` line.
> **Caveat**: Do not mechanically refactor all `[]*T` to `[]T`. If the underlying object mandates shared mutation or holds massive amounts of data, the performance trade-offs will differ completely.
> **When to use**: When investigating high `allocs/op` inside batch processing paths, serialization layers, or data aggregation code.

### Example 4: Expert — Optimizing allocs without deceiving yourself

> **Goal**: Turn the mental model into a measurable pattern: preallocation, buffer reuse, and benchmarking using `allocs/op`.
> **Approach**: Utilize `bytes.Buffer` in a hot path, but do not create new ones endlessly; integrate `sync.Pool` alongside benchmarks to locate genuinely optimizable areas.
> **Example**: Render payloads repeatedly using `strings.Builder`/`bytes.Buffer`, measured by `testing.B`.
> **Complexity**: O(n) time per render; the true value lies in cutting down allocation counts and relieving GC pressure.

```go
package main

import (
	"bytes"
	"fmt"
	"sync"
	"testing"
)

var payloadPool = sync.Pool{
	New: func() any {
		return new(bytes.Buffer)
	},
}

func renderWithPool(id int64, status string) string {
	buf := payloadPool.Get().(*bytes.Buffer)
	buf.Reset()
	defer payloadPool.Put(buf)

	// Buffer is reused across multiple calls instead of allocating fresh per request.
	fmt.Fprintf(buf, `{"id":%d,"status":"%s"}`, id, status)

	// String() generates its own distinct string result, so returning the buffer to the pool is entirely safe here.
	return buf.String()
}

func BenchmarkRenderWithPool(b *testing.B) {
	b.ReportAllocs()
	for i := 0; i < b.N; i++ {
		_ = renderWithPool(int64(i), "ok")
	}
}

func main() {
	_ = renderWithPool(1, "ok")
}
```

```bash
go test -bench=RenderWithPool -benchmem
```

> **Why is `sync.Pool` a conditional optimization, not magic?**
> `sync.Pool` is useful only when you constantly generate very short-lived temporary objects that are verifiably safe to reuse. It cannot replace solid business logic, cannot fix a terrible data layout, and does not serve as a persistent cache. The GC can sweep the pool completely at its own discretion. If you cannot explicitly prove that an object sits directly on a hot path causing verifiable allocation pressure, introducing `sync.Pool` only makes the code harder to read.
>
> **Why must a benchmark include a narrative on allocations?**
> If you only look at `ns/op`, you easily miss the fact that the heap is inflating rapidly or that the GC is paying a heavy tax for you over a sustained workload. The metrics `allocs/op` and `B/op` are where the mental model becomes empirical evidence.

> **Takeaway**: Good allocation optimization is evidence-based optimization. It starts strictly from object lifetimes and data shapes, not by scattering pointers or `sync.Pool` blindly everywhere.
> **Caveat**: If payloads are minute, throughput is minimal, or the execution path isn't "hot", simpler code is almost always more valuable than saving a few tiny allocations.
> **When to use**: When you possess hard evidence via benchmarks or profiles proving that alloc pressure is genuinely contributing heavily to system latency or memory churn.

Understanding the right path is still not enough, because this domain is highly susceptible to _saying individual truths but making globally incorrect decisions_. The pitfalls section outlines where this specifically happens.

## 4. PITFALLS

The theory is clear. What remains is avoiding conclusions that sound correct but lead to wrong optimizations in code reviews and production.

| # | Severity | Error | Consequence | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Fatal | Assuming `new(T)` always allocates on the heap | Misreading compiler output, optimizing wrong spots | Check lifetime; run `-gcflags="-m -m"` on the real path |
| 2 | 🔴 Fatal | Using `*T` everywhere because "pointers are faster" | Shared mutation bugs, poor locality, higher GC scan cost | Use pointers for semantic need or measured cost, not habit |
| 3 | 🔴 Fatal | Returning objects to `sync.Pool` without resetting state | Data leaks between requests, non-reproducible corruption | Call `Reset()` or zero the object before `Put()` |
| 4 | 🟡 Common | Switching from `[]T` to `[]*T` prematurely | More heap objects, worse cache locality | Keep `[]T` for batch/read-heavy paths unless shared identity is needed |
| 5 | 🟡 Common | Benchmarking only `ns/op`, ignoring `allocs/op` and `B/op` | Fast benchmarks, but production is GC-bound | Always report allocation metrics alongside latency |
| 6 | 🟡 Common | Rewriting architecture after one escape analysis output line | Over-engineering without fixing the real bottleneck | Cross-check compiler output with benchmarks and heap profiles |
| 7 | 🔵 Minor | Confusing "stack/heap" with "safe/unsafe" memory | Wrong abstraction in code reviews | Separate three questions: semantics, lifetime, measurement |

Once you see these traps, the correct next step is not hunting every allocation. Instead: read evidence at the right layer (compiler, benchmark, profile) and only then draw conclusions.

---

## 5. REF

| Resource | Type | Link | Notes |
| --- | --- | --- | --- |
| Go Spec | Official | [go.dev/ref/spec](https://go.dev/ref/spec) | Definitive source for value, pointer, and composite literal semantics |
| Effective Go | Official | [go.dev/doc/effective_go](https://go.dev/doc/effective_go) | Practical idioms for choosing values vs pointers |
| GC Guide | Official | [tip.golang.org/doc/gc-guide](https://tip.golang.org/doc/gc-guide) | GC costs and memory tuning |
| `sync.Pool` docs | Official | [pkg.go.dev/sync#Pool](https://pkg.go.dev/sync#Pool) | Requirements and caveats for object pools |
| `unsafe` docs | Official | [pkg.go.dev/unsafe](https://pkg.go.dev/unsafe) | `unsafe.Pointer` rules and struct offset regulations |
| Profiling Go Programs | Official | [go.dev/blog/profiling-go-programs](https://go.dev/blog/profiling-go-programs) | Connects allocation questions to concrete profile evidence |

## 6. RECOMMEND

Go basics are covered. Each topic below takes one concept from this article and explores it in depth.

| Extension | When to Read Next | Reason | File |
| --- | --- | --- | --- |
| Defer, Panic, Recover | Mixing object lifetime with cleanup timing | Separate object lifecycle from resource cleanup | [./03-defer-panic-recover.md](./03-defer-panic-recover.md) |
| Control Flow & Loops | Allocation bugs tied to closures inside loops | Many accidental allocations start from loop semantics | [./02-control-flow-loops.md](./02-control-flow-loops.md) |
| Slices, Maps, Strings | Questions about backing arrays, slice growth, conversions | Natural next step beyond pointer semantics into collection layout | [../types/01-slices-maps-strings.md](../types/01-slices-maps-strings.md) |
| Performance Profiling | You suspect alloc pressure and need hard evidence | Connects `allocs/op` with heap profiles and flame graphs | [../../advanced/05-performance-pprof.md](../../advanced/05-performance-pprof.md) |
| GC Internals | Understanding heap growth and GC pacing | Logical next step after mastering stack/heap behavior | [../../advanced/01-garbage-collector.md](../../advanced/01-garbage-collector.md) |
| `sync.Pool` & Buffer Pool | Hot path creates too many temporary objects | Moves from allocation reasoning into object reuse patterns | [../../concurrency/04-sync-pool.md](../../concurrency/04-sync-pool.md) |

---

**Sequential Navigation**: [← Defer/Panic](./03-defer-panic-recover.md) · [→ Types](../types/README.md)

