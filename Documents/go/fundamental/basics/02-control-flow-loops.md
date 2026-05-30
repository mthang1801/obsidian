<!-- tags: golang -->
# 🔀 Control Flow & Loops — if, for, switch, select

> Go controls logic flow with four keywords. `for` replaces `while`. `switch` auto-breaks. `select` multiplexes channels. Fewer keywords, fewer bugs.

📅 Created: 2026-03-20 · 🔄 Updated: 2026-04-19 · ⏱️ 12 min read

| Aspect            | Detail                                                                       |
| ----------------- | ---------------------------------------------------------------------------- |
| **Concept**       | Go control flow primitives: `if`, `for`, `switch`, `select`                  |
| **Use case**      | Logic branching, iteration, channel multiplexing                             |
| **Key insight**   | `for` replaces `while`. `switch` auto-breaks. `select` handles channels.     |
| **Go philosophy** | Fewer keywords → less cognitive load → fewer bugs                            |

---

## 1. DEFINE

You switch from Java to Go and reach for `while`. The compiler rejects it. You write a `switch` case and forget `break`. The code works — because Go auto-breaks. You try `forEach` on a slice. It does not exist. `for range` does the job.

Go collapses the typical 6–8 control flow keywords found in C/Java into four: `if`, `for`, `switch`, and `select`. Each keyword absorbs multiple roles. The result: less syntax to memorize, fewer opportunities for classic bugs like C's fall-through `switch` or Java's accidental infinite `while(true)`.

### 1.1 Control Flow Keywords

| Statement | Purpose                         | Example                         |
| --------- | ------------------------------- | ------------------------------- |
| `if`      | Conditional with optional init  | `if err := fn(); err != nil {}` |
| `for`     | The only loop keyword           | `for i := 0; i < n; i++ {}`    |
| `switch`  | Multi-branch with auto-break    | `switch v.(type) {}`            |
| `select`  | Channel multiplexer             | `select { case <-ch: }`         |
| `goto`    | Label jump (rare)               | Error cleanup paths             |
| `defer`   | Deferred call (LIFO stack)      | `defer f.Close()`               |

> **Why no `while`?** Rob Pike: *"If `for` can do everything, why add `while`?"* `for condition {}` is a while loop. `for {}` is an infinite loop. One keyword. Zero ambiguity.

### 1.2 For Loop Variants

| Variant       | Syntax                        | Equivalent in C/Java |
| ------------- | ----------------------------- | -------------------- |
| Classic       | `for i := 0; i < n; i++ {}`  | C-style for          |
| While         | `for condition {}`            | while loop           |
| Infinite      | `for {}`                      | while(true)          |
| Range slice   | `for i, v := range slice {}`  | forEach              |
| Range map     | `for k, v := range map {}`   | forEach key-value    |
| Range string  | `for i, r := range "utf8" {}` | Unicode rune iter    |
| Range channel | `for v := range ch {}`        | Receive until close  |
| Range integer | `for i := range 5 {}`         | Go 1.22+ only        |

> **Why does `range string` yield runes?** Go strings are UTF-8 byte sequences. A single character like "世" occupies 3 bytes. `range` decodes each character into a rune, returning `(byteIndex, rune)` — correct Unicode handling without manual decoding.

### 1.3 Switch Mechanics

| Feature          | Description                                  |
| ---------------- | -------------------------------------------- |
| Auto-break       | Each case terminates automatically           |
| Multi-value      | `case "a", "b", "c":` matches any            |
| Expressionless   | `switch { case x > 0: }` replaces if-else   |
| Type switch      | `switch v := x.(type) { case int: }`         |
| `fallthrough`    | Explicit opt-in to execute the next case     |

> **Why auto-break?** Forgetting `break` in C switch statements causes silent fall-through bugs. Go inverts the default: cases break automatically. Use `fallthrough` only when you genuinely need it.

### 1.4 Select Multiplexing

`select` blocks until one of its channel operations is ready:

| Pattern       | Syntax                               | Behavior                   |
| ------------- | ------------------------------------ | -------------------------- |
| Multi-channel | `select { case <-ch1: case <-ch2: }` | Blocks until one is ready  |
| Timeout       | `case <-time.After(1s):`             | Bounds the wait duration   |
| Non-blocking  | `default:` case                      | Proceeds immediately       |
| Cancellation  | `case <-ctx.Done():`                 | Respects context signals   |

> **What if two channels are ready simultaneously?** Go selects one at random. This prevents starvation and guarantees fairness across channels.

### 1.5 Failure Modes

| Error                        | Cause                                    | Fix                                    |
| ---------------------------- | ---------------------------------------- | -------------------------------------- |
| Infinite loop                | Missing loop exit condition              | Always have a bounded condition or `break` |
| `time.After` leak in loop    | Creates a new timer every iteration      | Use `time.NewTimer` with `.Stop()`     |
| Nested `break` misfire       | `break` exits `select`, not outer `for`  | Use labeled break: `break outerLoop`   |
| Range copy mutation          | Modifying the copy, not the original     | Use index: `slice[i].field = val`      |

---

The keywords and their mechanics are clear. But how do you choose the right one when facing a branching decision for the first time?

## 2. VISUAL

![Control flow decision map](./images/02-control-flow-loops-decision-map.png)

*Figure: Decision map for Go control flow — start with the question type (branch? repeat? wait for channel?) and arrive at the correct keyword. `if` for simple branches, `switch` for 3+ conditions, `for` for all loops, `select` for channel multiplexing.*

The decision map answers "which keyword?" The examples below show how each keyword behaves in production code.

![For loop — one keyword, four forms](./images/02-for-loop-variants.png)

_Figure: The four idiomatic forms of Go's `for` loop — classic, while, infinite, and range — each selected by what you need to control. One keyword replaces `for`, `while`, `do-while`, and `forEach`._

## 3. CODE

### Example 1: Basic — If Init Statement & For Range

> **Goal**: Scope error variables tightly using `if` init statements.
> **Approach**: Combine `if` initialization with `for range` iteration.
> **Complexity**: Basic

```go
package main

import (
    "fmt"
    "os"
)

func main() {
    // err is scoped to this if block — it does not leak.
    if f, err := os.Open("config.yaml"); err != nil {
        fmt.Println("Cannot open:", err)
    } else {
        defer f.Close()
        fmt.Println("Opened:", f.Name())
    }

    // Range returns (index, copy). Modifying the copy does not change the slice.
    fruits := []string{"Apple", "Banana", "Cherry"}
    for i, fruit := range fruits {
        fmt.Printf("[%d] %s\n", i, fruit)
    }

    // Go 1.22+: range over integers
    for i := range 5 {
        fmt.Print(i, " ")
    }
}
```

> **Takeaway**: The `if` init statement confines `err` to the block where it is relevant. `for range` handles indices and values in one line, replacing manual counter loops.

### Example 2: Intermediate — Switch Patterns & Type Switch

> **Goal**: Replace long `if-else` chains with cleaner switch expressions.
> **Approach**: Use expressionless switch for ranges and type switch for runtime type inspection.
> **Complexity**: Intermediate

```go
package main

import "fmt"

// Expressionless switch replaces if-else chains for range checks.
func classify(score int) string {
    switch {
    case score >= 90:
        return "A — Excellent"
    case score >= 80:
        return "B — Good"
    default:
        return "F — Fail"
    }
}

// Type switch extracts the concrete type from an interface.
func describe(val any) string {
    switch v := val.(type) {
    case int:
        return fmt.Sprintf("integer: %d", v)
    case string:
        return fmt.Sprintf("string(%d chars): %q", len(v), v)
    default:
        return fmt.Sprintf("unknown type: %T", v)
    }
}

func main() {
    fmt.Println(classify(85))   // B — Good
    fmt.Println(describe(42))   // integer: 42
}
```

> **Takeaway**: Expressionless `switch` reads cleaner than `if-else` chains when comparing ranges. Type switches safely extract concrete types from `any` / `interface{}` values without manual assertion.

### Example 3: Advanced — Select + Timeout + Context Cancellation

> **Goal**: Multiplex channels with timeout and cancellation support.
> **Approach**: Use `select` to race a result channel against `time.After`, and `ctx.Done()` for graceful shutdown.
> **Complexity**: Advanced

```go
package main

import (
    "context"
    "fmt"
    "time"
)

// select races the result against a timeout deadline.
func fetchWithTimeout(url string, timeout time.Duration) (string, error) {
    result := make(chan string, 1)

    go func() {
        time.Sleep(100 * time.Millisecond) // simulate network call
        result <- fmt.Sprintf("Response from %s", url)
    }()

    select {
    case data := <-result:
        return data, nil
    case <-time.After(timeout):
        return "", fmt.Errorf("timeout after %v", timeout)
    }
}

// ctx.Done() exits the worker loop when the parent cancels.
func worker(ctx context.Context, tasks <-chan int) {
    for {
        select {
        case <-ctx.Done():
            fmt.Println("worker: context cancelled")
            return
        case task, ok := <-tasks:
            if !ok {
                return // channel closed
            }
            fmt.Println("processing:", task)
        }
    }
}

func main() {
    data, err := fetchWithTimeout("api.example.com", 300*time.Millisecond)
    if err != nil {
        fmt.Println(err)
    } else {
        fmt.Println(data)
    }
}
```

> **Takeaway**: `select` turns channel operations into a decision point — whichever channel fires first wins. `time.After` provides a timeout boundary. `ctx.Done()` enables the parent to signal shutdown without force-killing goroutines.

---

## 4. PITFALLS

| #   | Severity  | Pitfall                                       | Consequence                                 | Fix                                                |
| --- | --------- | --------------------------------------------- | ------------------------------------------- | -------------------------------------------------- |
| 1   | 🔴 Fatal  | `time.After` inside a tight loop              | Creates a new timer each iteration → memory leak | Use `time.NewTimer` and call `.Stop()` after use   |
| 2   | 🔴 Fatal  | `break` inside `select` within a `for` loop   | Breaks `select`, not the outer loop         | Use a labeled break: `break outerLoop`             |
| 3   | 🟡 Common | Modifying `for range` loop variable           | Changes a copy, not the original element    | Use index access: `slice[i].field = val`           |
| 4   | 🟡 Common | Relying on map iteration order                | Order is randomized — tests become flaky    | Sort keys before iteration                         |
| 5   | 🔵 Minor  | Using `fallthrough` in switch                 | Confuses reviewers; rarely the right choice | Leave auto-break; use `fallthrough` only when unavoidable |

---

## 5. REF

| Resource               | Type     | Link                                                                                            | Note                            |
| ---------------------- | -------- | ----------------------------------------------------------------------------------------------- | ------------------------------- |
| Go Spec — Statements   | Official | [go.dev/ref/spec#Statements](https://go.dev/ref/spec#Statements)                                | Authoritative language spec     |
| Go Tour — Flow Control | Official | [go.dev/tour/flowcontrol/1](https://go.dev/tour/flowcontrol/1)                                  | Interactive tutorial             |
| Effective Go — Control | Official | [go.dev/doc/effective_go#control-structures](https://go.dev/doc/effective_go#control-structures) | Idiomatic patterns              |

---

## 6. RECOMMEND

Control flow tells the program what to do. The next question: what happens when things go wrong — files left open, panics crashing production, resources leaking?

| Expand to                 | When                                    | Reason                                                  | File                                                            |
| ------------------------- | --------------------------------------- | ------------------------------------------------------- | --------------------------------------------------------------- |
| Defer, Panic, Recover     | Resource cleanup across return paths    | `defer` guarantees cleanup; `recover` catches panics    | [03-defer-panic-recover.md](./03-defer-panic-recover.md)        |
| Pointers & Memory         | Understanding pass-by-value vs pointer  | Go passes copies by default; pointers modify the original | [04-pointers-memory.md](./04-pointers-memory.md)               |
| Syntax & Variables        | Reviewing `var` vs `:=` declaration     | Foundational syntax that this article builds on         | [01-syntax-variables.md](./01-syntax-variables.md)              |
| Goroutines & Channels     | Taking `select` deeper into concurrency | `select` is the gateway to Go concurrency patterns      | [../../concurrency/01-goroutines-and-channels.md](../../concurrency/01-goroutines-and-channels.md) |

---

**Navigation**: [← Syntax & Variables](./01-syntax-variables.md) · [→ Defer, Panic, Recover](./03-defer-panic-recover.md)
