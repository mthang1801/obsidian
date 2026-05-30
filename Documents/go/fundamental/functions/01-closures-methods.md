<!-- tags: golang -->
# ⚙️ Functions — Closures, Variadic, Methods

> Go functions: first-class, closures, variadic args, method receivers

📅 Created: 2026-03-20 · 🔄 Updated: 2026-04-19 · ⏱️ 17 min read

| Aspect            | Detail                                  |
| ----------------- | --------------------------------------- |
| **Concept**       | Functions as values, methods on types   |
| **Use case**      | Code reuse, composition                 |
| **Key insight**   | Value receiver vs pointer receiver      |
| **Go philosophy** | Functions > methods when state is not required |

---

## 1. DEFINE

> *You are writing an HTTP middleware. It needs to count requests, rate-limit by IP, and inject a logger into the request context. All of this boils down to returning a function — `func(http.Handler) http.Handler` — but that function must "remember" state: a counter, configuration, and a logger. This is where closures shine: a function carrying its own living environment.*
>
> *Go functions are first-class citizens: they can be assigned to variables, passed as arguments, or returned from other functions. A closure is a function combined with its captured variables — a construct powerful enough to implement middleware, factory patterns, event handlers, and option patterns without needing classes or objects. Method receivers govern something else entirely: value receivers use copies, while pointer receivers use references. Confusing the two is the root cause of countless elusive bugs.*

### Function Features

Go functions possess **6 features** that make them true first-class citizens:

| Feature          | Description                   | Example                       |
| ---------------- | ----------------------- | --------------------------- |
| Multiple returns | Return multiple values     | `func() (int, error)`       |
| Named returns    | Named return values     | `func() (n int, err error)` |
| Variadic         | Variable arguments           | `func(nums ...int)`         |
| First-class      | Assign to variable      | `fn := func() {}`           |
| Closure          | Capture outer variables | `func() { x++ }`            |
| Defer            | Execute on return       | `defer f.Close()`           |

**Why Multiple returns?** Go lacks exceptions — errors must be explicitly returned as the second value. The `(result, error)` pattern forces callers to handle errors explicitly rather than letting them slip through like forgotten try/catch blocks.

### Method Receivers

Choosing between a **Value vs Pointer receiver** is one of the most critical decisions when defining a method in Go:

| Receiver    | Syntax                      | Modifies? | Copy?   | Use when                 |
| ----------- | --------------------------- | --------- | ------- | ------------------------ |
| **Value**   | `func (s Struct) Method()`  | ❌        | Copy    | Read-only, small structs |
| **Pointer** | `func (s *Struct) Method()` | ✅        | Pointer | Mutations, large structs    |

**Why not always use pointer receivers?** Value receivers have a distinct advantage: compiler optimization — no heap escape, no garbage collection tracking needed. For small, read-only structs, value receivers are faster and implicitly thread-safe.

---

The theory is clear — now let's see how closure capture and receiver mechanics behave visually.

These concepts look straightforward — but lethal traps lurk: closure captures turning loops into reference hazards, and method interfaces evaluating differently for pointers versus values. Those traps are unpacked in PITFALLS.

## 2. VISUAL

This topic rarely breaks because of syntax. It breaks because of hidden state: what a closure retains, what a receiver copies, and what method set an interface sees. The visual below consolidates those three sources of confusion into one mental model.

![Closures and methods mental model](./images/01-closures-methods-mental-model.png)

*Figure: Mental-model card of closures and methods placed side-by-side highlighting four main concepts: closure capture, value receivers, pointer receivers, and middleware-style composition.*

Once hidden state is exposed, the code below becomes much more effective. You will read each example as a test of ownership and mutation semantics, rather than just independent function declarations.

## 3. CODE

With **Functions — Closures, Variadic, Methods**, we established a mental model for hidden state and receiver semantics. Now, let's step down into the code to see how every choice — value or pointer receiver, closure or struct, capture or copy — actually alters mutation behavior.

### Example 1: Basic — Functions & Multiple Returns

You call `os.Open(path)` and receive 2 values: `file` and `error`. If coming from Java or Python, you are accustomed to try/catch — but Go has no exceptions. Why? Because exceptions can be "forgotten" — nothing forces you to write that try/catch block. Go mandates explicit error handling via multiple returns `(result, error)`.

Combine named returns for complex calculations and variadic `...T` for flexible argument lists.

Input: `divide(10, 3)` · Output: `(3.33, nil)` · `divide(10, 0)` · Output: `(0, "division by zero")`

```go
package main

import (
    "errors"
    "fmt"
)

// ✅ Multiple returns — idiomatic Go error handling
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

// ✅ Named returns — useful for complex functions
func stats(nums []int) (min, max, sum int) {
    if len(nums) == 0 {
        return
    }
    min, max = nums[0], nums[0]
    for _, n := range nums {
        if n < min { min = n }
        if n > max { max = n }
        sum += n
    }
    return  // naked return — returns named values implicitly
}

// ✅ Variadic function
func sumAll(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}

func main() {
    result, err := divide(10, 3)
    if err != nil {
        fmt.Println("Error:", err)
        return
    }
    fmt.Println("Result:", result)

	min, max, sum := stats([]int{3, 1, 4, 1, 5, 9, 2, 6})
    fmt.Printf("min=%d max=%d sum=%d\n", min, max, sum)

	fmt.Println(sumAll(1, 2, 3, 4, 5))     // 15
    nums := []int{10, 20, 30}
    fmt.Println(sumAll(nums...))              // Spread slice
}
```

> **Why does Go lack exceptions?**
> Multiple returns `(result, error)` compel the caller to handle errors explicitly — you cannot "forget" a try/catch. Named returns are useful for complex functions, but naked returns (calling `return` without arguments) can cause confusion — use them sparingly and only in short functions.

> **Takeaway**: `(result, error)` is idiomatic Go. Variadic `...T` accepts zero or more arguments — you can spread a slice using `nums...`. Named returns organize complex calculations, but avoid naked returns in long functions.
>
> **Caveat**: Named returns initialize zero-value variables at the start of the function — do not forget to assign values before returning. Variadics spread with `append(a, b...)` — forgetting the `...` results in a compilation error.
>
> **When to use**: Multiple returns for any function that might fail. Variadic for utility functions (like loggers or formatters). Named returns for functions returning 3 or more values.

Multiple returns provide explicit error handling. But when you need to "remember" state across multiple calls — counters, configurations, handler chains — closures are the solution.

### Example 2: Intermediate — Closures & Higher-order Functions

You need to implement a rate limiter for an HTTP server. Each endpoint requires a separate counter and configuration, yet uses identical counting logic. Creating a `RateLimiter` struct for every endpoint is heavy-handed. Closures solve this elegantly: `func makeRateLimiter(limit int) func() bool` — each call to `makeRateLimiter(100)` yields a function that "remembers" its own specific limit and counter.

This pattern extends into middleware (wrapping handlers), iterators (stateful step resolution), and factories (generating functions based on configurations).

Input: `multiplier(3)(5)` · Output: `15` — the closure captures `factor=3` from the outer scope

```go
package main

import "fmt"

// ✅ Function as parameter (higher-order)
func apply(nums []int, fn func(int) int) []int {
    result := make([]int, len(nums))
    for i, n := range nums {
        result[i] = fn(n)
    }
    return result
}

// ✅ Function returning function (closure factory)
func multiplier(factor int) func(int) int {
    return func(n int) int {
        return n * factor  // ✅ Captures `factor` from outer scope
    }
}

// ✅ Closure as iterator
func fibonacci() func() int {
    a, b := 0, 1
    return func() int {
        a, b = b, a+b
        return a
    }
}

// ✅ Middleware pattern (very common in Go)
type Handler func(string) string

func withLogging(h Handler) Handler {
    return func(input string) string {
        fmt.Printf("Input: %s\n", input)
        result := h(input)
        fmt.Printf("Output: %s\n", result)
        return result
    }
}

func main() {
    // ✅ Higher-order functions
    doubled := apply([]int{1, 2, 3}, func(n int) int { return n * 2 })
    fmt.Println(doubled)  // [2 4 6]

	// ✅ Closure factory
    triple := multiplier(3)
    fmt.Println(triple(5))  // 15

	// ✅ Iterator pattern
    fib := fibonacci()
    for i := range 10 { // Go 1.22+
        fmt.Print(fib(), " ")
    }
    fmt.Println()  // 1 1 2 3 5 8 13 21 34 55

	// ✅ Middleware
    handler := withLogging(func(s string) string {
        return "Hello, " + s
    })
    handler("Go")
}
```

> **Why do closures capture references instead of copying values?**
> A closure must "remember" variables from the outer scope. If it copied the value, subsequent modifications (like `counter++`) would never reflect in future invocations. Go closures capture **variables** (by reference), not values — this is why `fibonacci()` functions correctly: with each call, `a` and `b` are updated sequentially.

> **Takeaway**: Closure = function + captured variables. Higher-order functions (`apply`) enable map/filter patterns. Middleware patterns wrap logic around handlers — an incredibly common paradigm in HTTP frameworks.
>
> **Caveat**: Closures capture **variables** (references) — not values. In loops (pre-Go 1.22): all spawned closures will reference the same final variable iteration unless you forcefully copy it via `v := v`.
>
> **When to use**: Rate limiters, middleware, iterators, factories. Whenever you need to encapsulate state without explicitly declaring a struct.

Closures hold state within a function. When state needs to be bound to a specific data type, method receivers attach behavior directly to structs.

### Example 3: Advanced — Method Receivers

You define a `Counter` struct with an `Inc()` method. You call `c.Inc()` — but the counter does not increase. Where is the bug? A value receiver: `func (c Counter) Inc()` receives a complete copy of `c`, increments the copy, and immediately discards it upon exiting. You must use a pointer receiver `func (c *Counter) Inc()` to mutate the original struct itself.

But deciding between value and pointer receivers is not solely about mutation. Method set rules dictate interface satisfaction: value types only satisfy interfaces equipped with value receivers. Mixing receivers means your type fails to implement interfaces consistently.

Input: `p.Translate(1, 1)` with a pointer receiver · Output: `p` modified in-place

```go
package main

import (
    "fmt"
    "math"
)

type Point struct {
    X, Y float64
}

// ✅ Value receiver — does NOT modify original
func (p Point) Distance(other Point) float64 {
    dx := p.X - other.X
    dy := p.Y - other.Y
    return math.Sqrt(dx*dx + dy*dy)
}

// ✅ Pointer receiver — CAN modify original
func (p *Point) Translate(dx, dy float64) {
    p.X += dx
    p.Y += dy
}

// ✅ Stringer interface (like toString)
func (p Point) String() string {
    return fmt.Sprintf("(%g, %g)", p.X, p.Y)
}

// ✅ Method on custom type (non-struct)
type StringSlice []string

func (ss StringSlice) Contains(target string) bool {
    for _, s := range ss {
        if s == target {
            return true
        }
    }
    return false
}

func main() {
    p := Point{3, 4}
    origin := Point{0, 0}
    fmt.Println(p.Distance(origin))  // 5

	p.Translate(1, 1)
    fmt.Println(p)  // (4, 5) — modified!

	tags := StringSlice{"go", "rust", "python"}
    fmt.Println(tags.Contains("go"))    // true
    fmt.Println(tags.Contains("java"))  // false
}
```

> **Why should you use pointer receivers for all methods if only one method requires it?**
> Method set rules: a value type only satisfies interfaces requiring value receivers. A pointer type satisfies both. Mixing receivers guarantees your type cannot consistently fit interface requirements. Beyond compiler mechanics, consistency gives developers immediate confidence: "every method takes `*T`" — removing the need to drill down and check the safety of each distinct operation.

> **Takeaway**: Value receivers are for read-only use cases and small structs. Pointer receivers are strictly for mutations and large structs. Methods can also be defined on non-struct custom types (e.g., `StringSlice`) to append domain-specific behavior.
>
> **Caveat**: Methods with value receivers satisfy interfaces — but methods with pointer receivers DO NOT automatically satisfy them for value types. Mixing receivers creates jagged interface reliability. Rule of thumb: if 1 method needs a pointer, elevate them all to pointer receivers.
>
> **When to use**: Pointer receivers cover roughly ≥90% of production types. Reserve value receivers exclusively for small, immutable types where thread-safety is critical.

---

## 4. PITFALLS

The core mechanics of **Functions — Closures, Variadic, Methods** should be clear. What is left is recognizing the syntax that looks _almost right_ but ultimately introduces silent mutation bugs straight into production.

| # | Severity | Bug | Consequence | Fix |
|---|----------|-----|-------------|-----|
| 1 | 🔴 Fatal | Value receiver intended for mutation | Changes are lost — method mutates an isolated copy | Enforce a pointer receiver `*T` |
| 2 | 🔴 Fatal | Nil pointer receiver crashes | Runtime panic | Verify `if t == nil` at the start of the method |
| 3 | 🟡 Common | Mixed value and pointer receivers | Inconsistent interface satisfaction | Choose 1 unified style for the entire type |
| 4 | 🟡 Common | Closure captures loop variable (pre Go 1.22) | All spawned closures point to the final iterated variable | Add `v := v` inside the loop body to force a copy |
| 5 | 🔵 Minor | Named returns combined with defer | `defer` silently modifies named returns | Standardize your execution order logic |

### 🔴 Pitfall #1 — Value receivers "swallowing" mutations

Perhaps the most universally encountered bug for newcomers. You write a method to modify a field, the test runs — but the field remains unchanged:

```go
type User struct{ Name string }

func (u User) SetName(name string) { u.Name = name } // ❌ value receiver = pure copy
func (u *User) SetName(name string) { u.Name = name } // ✅ pointer receiver
```

A value receiver operates on a **copy** of the struct. Modifications die the moment the method scope terminates — the caller never observes the changes. The compiler issues zero warnings because the code is syntactically valid.

### 🔴 Pitfall #2 — Nil pointer receiver panics

Go allows `nil` pointers to invoke methods — but the instant that method attempts to access a structural field, it panics:

```go
var u *User // nil
u.SetName("Alice") // panic: nil pointer dereference
```

**Fix**: Always check for nil within the method body: `if u == nil { return }`. Alternatively, ensure your constructors universally reject or circumvent returning nil boundaries.

---

You have explored Closures & Methods from primary basics all the way through higher-order functional design patterns. The resources below will carry you deeper.

## 5. REF

| Resource     | Type     | Link                                                                           | Notes |
| ------------ | -------- | ------------------------------------------------------------------------------ | ----- |
| Go Functions | Tutorial | [go.dev/tour/moretypes/24](https://go.dev/tour/moretypes/24)                   | Function values, closures |
| Methods      | Tutorial | [go.dev/tour/methods/1](https://go.dev/tour/methods/1)                         | Method receivers |
| Effective Go | Official | [go.dev/doc/effective_go#functions](https://go.dev/doc/effective_go#functions) | Best practices |
| Go Spec      | Official | [go.dev/ref/spec#Function_types](https://go.dev/ref/spec#Function_types)       | Language specification |

---

## 6. RECOMMEND

The foundations of **Functions — Closures, Variadic, Methods** are settled. The extensions below connect function values and method receivers to the broader type system, interface boundaries, and production lifecycles.

| Extension                      | When                      | Why                                     | File/Link |
| ------------------------------ | ------------------------- | --------------------------------------- | --------- |
| Struct Tags, Options & Builder | When constructors need complex configuration | Where closures and methods meet API design | [../structs/02-tags-options-builder.md](../structs/02-tags-options-builder.md) |
| Interfaces — Implicit, io.Reader/Writer | When function types must cross dependency lines | Bridges function values into Go’s interface mechanics | [../interfaces/01-implicit-io-patterns.md](../interfaces/01-implicit-io-patterns.md) |
| Type Assertion, Embedding & Aliases | When method sets and interface satisfaction feel ambiguous | The type mechanics running beneath receiver behavior | [../types/03-type-assertion-embedding.md](../types/03-type-assertion-embedding.md) |
| Generics — Constraints and Patterns | Building type-safe reusable higher-order helpers | Natural transition after closures for reusable utilities | [../types/02-generics.md](../types/02-generics.md) |
| Context | When closure middleware requires timeouts or cancellation | Where function logic meets request lifecycle | [../../concurrency/03-context.md](../../concurrency/03-context.md) |

**Navigation**: [← Types](../types/README.md) · [→ strings](./02-strings.md)
