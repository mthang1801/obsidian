<!-- tags: golang, error-handling -->

# ⏸️ Defer, Panic, Recover — Resource Management & Error Recovery

> Defer stack, panic/recover flow, resource cleanup patterns — production essentials

📅 Created: 2026-03-20 · 🔄 Updated: 2026-04-19 · ⏱️ 20 min read

| Aspect          | Detail                                                                                                             |
| --------------- | ------------------------------------------------------------------------------------------------------------------ |
| **Concept**     | Defer stack, panic propagation, recover boundaries, cleanup timing                                                 |
| **Use case**    | File/socket/lock cleanup, startup failure, panic boundary, transaction rollback                                    |
| **Key insight** | `defer` is a control-flow primitive for cleanup; `panic`/`recover` are boundary tools, not the default error model |

## 1. DEFINE

> _Imagine writing a function that opens a file, connects to a database, and acquires a lock — and it has 5 different return points. Missing just one close operation creates a resource leak. Missing one unlock triggers a deadlock._

### 1.1 What is Defer — Runtime Mechanism

When the Go runtime encounters `defer`, it:

1. **Evaluates all arguments immediately** — capturing their values at that exact moment.
2. **Pushes a defer record onto the defer stack** of the current goroutine.
3. **Delays execution** until the enclosing function concludes.

### 1.2 Argument Capture — Detailed Rules

Go applies two core mechanisms capturing arguments:

| Mechanism        | Example                          | When to evaluate                     |
| ---------------- | -------------------------------- | ------------------------------------ |
| Direct argument  | `defer f(x)`                     | **Immediately upon execution**       |
| Closure          | `defer func() { use(x) }()`      | **When defer runs**                  |
| Pointer receiver | `defer obj.Method()` (pointer)   | **When defer runs** (via pointer)    |
| Value receiver   | `defer obj.Method()` (value)     | **Immediately upon execution** (copy)|

### 1.3 Named Return Interaction — Deep Mechanics

Named return variables live in the enclosing function's stack frame. A deferred closure can read and modify them before the function actually returns.

```go
func queryDB(id int) (user User, err error) {
    defer func() {
        if err != nil {
            err = fmt.Errorf("queryDB(id=%d): %w", id, err)
        }
    }()
    // ...if the query fails, err will automatically be richly wrapped
}
```

### 1.4 `measureTime("name")()` — Pattern Anatomy

The pattern `defer f()()` is a double-invocation: the outer call runs immediately to set up, the returned function runs at defer time.

```go
// ✅ CORRECT: start time captured at the defer line, cleanup runs on return
defer measureTime("fn")()
```

### 1.5 Panic Flow

```
panic("msg")
    ↓
① Current function stops executing immediately
    ↓
② All deferred functions in scope run in LIFO order
    ↓
③ If any defer calls recover() → panic stops, function returns with named return values
    ↓
④ If no recover → panic propagates up the call stack, crashing the goroutine
```

## 2. VISUAL

Developers most often get confused when three different flows interact: normal defer execution, panic unwinding, and recover catching.

![Defer panic recover runtime state trace](./images/03-defer-panic-recover-workflow.png)

_Figure: Runtime state trace — defer registration, panic unwind, and the single boundary where recover catches the panic._

![Defer captures arguments, not closures](./images/03-defer-closure-capture.png)

_Figure: Side-by-side comparison of defer argument capture (by value — correct) vs closure capture (by reference — bug). Arguments freeze at `defer` time; closures read the variable at execution time._

## 3. CODE

### Example 1: Basic — Defer for Resource Cleanup

> **Goal**: Guarantee closing resources across all early validation checks safely.

```go
package main

import (
    "database/sql"
    "fmt"
    "io"
    "net/http"
    "os"
    "sync"
)

// ✅ File cleanup — defer right after Open
func copyFile(src, dst string) (int64, error) {
    source, err := os.Open(src)
    if err != nil {
        return 0, fmt.Errorf("open source: %w", err)
    }
    defer source.Close() 

    dest, err := os.Create(dst)
    if err != nil {
        return 0, fmt.Errorf("create dest: %w", err)
    }
    defer dest.Close()

    n, err := io.Copy(dest, source)
    dest.Sync()

    return n, err
}

func fetchURL(url string) ([]byte, error) {
    resp, err := http.Get(url)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    return io.ReadAll(resp.Body)
}
```

> **Takeaway**: Place `defer resp.Body.Close()` right after a successful `http.Get()`. Missing it leaks file descriptors silently.

### Example 2: Intermediate — Defer Gotchas & Named Returns

> **Goal**: Understand when defer evaluates arguments vs when closures capture live references.

```go
package main

import (
    "fmt"
    "os"
)

// GOTCHA 1: Arguments evaluated immediately
func deferArgsTrap() {
    x := 10
    defer fmt.Println("defer with arg:", x) // ✅ x=10 captured NOW
    x = 20
}

// GOTCHA 3: Defer within loops causes Resource Leaks
func deferInLoopBAD(files []string) {
    for _, path := range files {
        f, _ := os.Open(path)
        defer f.Close() // ❌ BAD! Defer closure hits exclusively AFTER the function returns
    }
}
```

> **Takeaway**: Closures capture references to variables, not copies. Arguments passed directly to defer are evaluated at the defer line.

### Example 3: Advanced — Panic/Recover in Production

> **Goal**: Catch panics inside an HTTP handler and return a valid JSON error instead of crashing the server.

```go
package main

import (
    "log"
    "net/http"
    "runtime/debug"
)

func recoveryMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if err := recover(); err != nil {
                stack := debug.Stack()
                log.Printf("PANIC recovered: %v\nStack:\n%s", err, stack)
                
                w.WriteHeader(http.StatusInternalServerError)
                w.Write([]byte(`{"error":"internal server error"}`))
            }
        }()
        next.ServeHTTP(w, r)
    })
}

// ✅ Safe abstract goroutine wrapper
func safeGo(fn func()) {
    go func() {
        defer func() {
            if r := recover(); r != nil {
                log.Printf("Goroutine isolated panic: %v", r)
            }
        }()
        fn()
    }()
}
```

> **Takeaway**: A recovery middleware at the HTTP boundary prevents one panicking handler from crashing the entire server.

### Example 4: Expert — Defer-based Resource Pool & Cleanup Chain

> **Goal**: Build a cleanup chain that runs multiple resource release functions in reverse order, collecting all errors.

```go
package main

import (
    "errors"
    "log"
)

type CleanupFunc func() error

type ResourceManager struct {
    cleanups []CleanupFunc
}

func (rm *ResourceManager) Add(name string, fn CleanupFunc) {
    rm.cleanups = append(rm.cleanups, func() error {
        log.Printf("Cleaning: %s", name)
        return fn()
    })
}

func (rm *ResourceManager) CleanupAll() error {
    var errs []error
    for i := len(rm.cleanups) - 1; i >= 0; i-- {
        if err := rm.cleanups[i](); err != nil {
            errs = append(errs, err)
        }
    }
    return errors.Join(errs...)
}
```

> **Takeaway**: When multiple resources depend on each other, a cleanup chain with reverse-order execution and error collection prevents partial cleanup failures from masking other errors.

## 4. PITFALLS

| #   | Severity  | Error                                            | Fix                                           |
| --- | --------- | ---------------------------------------------- | --------------------------------------------- |
| 1   | 🔴 Fatal  | Defer inside a loop = resource leak              | Extract to a function or explicitly close     |
| 2   | 🔴 Fatal  | Panic crossing a goroutine boundary              | Use a `safeGo()` wrapper with recover       |
| 3   | 🟡 Common | `defer f(x)` — x evaluated instantly             | Use a closure to purposefully capture updates |

## 5. REF

| Resource | Link |
| --- | --- |
| Go Blog: Defer | https://go.dev/blog/defer-panic-and-recover |
| Go Spec | https://go.dev/ref/spec#Defer_statements |


---

**Navigation**: [← Syntax & Variables](./01-syntax-variables.md) · [→ Pointers & Memory](./04-pointers-memory.md)
