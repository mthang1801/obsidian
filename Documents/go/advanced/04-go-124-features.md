<!-- tags: golang -->
# 🆕 Go 1.22 → 1.26 — New Features & Changes

> A compilation of the most important new features from Go 1.22 to Go 1.26 (latest version, released February 2026). These are changes that directly affect how you write Go code daily.

📅 Created: 2026-03-19 · 🔄 Updated: 2026-04-19 · ⏱️ 8 min read

| Version     | Release  | Highlights                                                                         |
| ----------- | -------- | ---------------------------------------------------------------------------------- |
| **Go 1.22** | Feb 2024 | Loop variable fix, enhanced routing, rangefunc experiment                          |
| **Go 1.23** | Aug 2024 | Range over function iterators, unique package, timer changes                       |
| **Go 1.24** | Feb 2025 | Generic type aliases, Swiss table maps, `os.Root`, weak pointers                   |
| **Go 1.25** | Aug 2025 | Green Tea GC (experimental), testing improvements                                  |
| **Go 1.26** | Feb 2026 | Green Tea GC default, `new(expr)`, self-ref generics, SIMD, goroutine leak profile |

---

## 1. DEFINE

You upgraded from Go 1.21 to 1.24. Tests pass. CI is green. Six weeks later, a colleague discovers `iter.Seq` would have eliminated an entire goroutine pool from the pipeline — and `os.Root` would have removed 30 lines of path-sanitization code. The upgrade gave you the binary, but nobody read the changelog closely enough to harvest the wins.

> *Every Go release ships features that can simplify real code. Missing them means carrying complexity that the language already solved.*

---

### 🔹 Go 1.22 — Loop Variable Fix & Routing

#### Loop Variable Change (IMPORTANT)

Before Go 1.22: loop variable **shared** across iterations → classic bug.
Go 1.22+: each iteration **creates its own copy** — fixes a 10-year-old bug!

```text
// Pre-1.22 — BUG!
for i, v := range items {
    go func() {
        fmt.Println(i, v) // ❌ All goroutines capture the same final loop variable.
    }()
}

// Go 1.22+ — FIXED automatically!
for i, v := range items {
    go func() {
        fmt.Println(i, v) // ✅ Each iteration gets its own copy.
    }()
}
```

#### Enhanced `net/http` Routing

Go 1.22 adds **method matching** and **path parameters** to stdlib:

```text
mux := http.NewServeMux()

// ✅ Method matching Go 1.22
mux.HandleFunc("GET /users", listUsers)
mux.HandleFunc("POST /users", createUser)

// ✅ Path parameters Go 1.22
mux.HandleFunc("GET /users/{id}", func(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id") // ← extract path param
    fmt.Fprintf(w, "User: %s", id)
})

// ✅ Wildcard — catch-all
mux.HandleFunc("GET /files/{path...}", serveFile)
```

---

### 🔹 Go 1.23 — Range Over Functions & Unique

#### Range Over Function Iterators

Go 1.23 allows `for range` on **functions** — creating custom iterators:

```text
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Iterator function type: func(yield func(V) bool)
// yield returns false terminating loops early
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

// Custom iterator: generate Fibonacci numbers
func Fibonacci(n int) iter.Seq[int] {
    return func(yield func(int) bool) {
        a, b := 0, 1
        for i := 0; i < n; i++ {
            if !yield(a) {
                return // terminate loop immediately
            }
            a, b = b, a+b
        }
    }
}

// Usage — idiomatic Go iteration!
for fib := range Fibonacci(10) {
    fmt.Println(fib) // 0, 1, 1, 2, 3, 5, 8, 13, 21, 34
}

// Seq2: key-value iterator
func Enumerate[T any](s []T) iter.Seq2[int, T] {
    return func(yield func(int, T) bool) {
        for i, v := range s {
            if !yield(i, v) {
                return
            }
        }
    }
}

for i, v := range Enumerate([]string{"a", "b", "c"}) {
    fmt.Printf("%d: %s\n", i, v)
}
```

#### `unique` Package

Canonical interning — create unique handles for values (save memory):

```text
import "unique"

h1 := unique.Make("hello")
h2 := unique.Make("hello")
fmt.Println(h1 == h2) // true — same handle (pointer equality)
fmt.Println(h1.Value()) // "hello"

// Use case: string deduplication in large datasets
```

#### Timer/Ticker Changes

Go 1.23: `time.Timer` and `time.Ticker` channels are now **unbuffered** when created by `time.NewTimer`/`time.NewTicker`. No need to drain the channel before `Reset()` anymore.

```text
// Go 1.23+ — simpler timer usage
timer := time.NewTimer(5 * time.Second)
// ...
timer.Reset(3 * time.Second) // ✅ No need to drain channel first
```

---

### 🔹 Go 1.24 — Generic Type Aliases, Swiss Tables, os.Root

#### Generic Type Aliases (Full Support)

Go 1.24 allows **parameterized type aliases**:

```text
// ✅ Go 1.24: Generic type alias
type Set[T comparable] = map[T]struct{}

// Usage
var s Set[string]
s = make(Set[string])
s["hello"] = struct{}{}
```

#### Swiss Table Map Implementation

Go 1.24 changes internal map implementation to **Swiss tables** → performance improvement:

- **2-3% CPU reduction** on average
- Better memory layout (cache-friendly)
- Faster lookups for small maps

```text
// ✅ No code changes needed — runtime applies Swiss tables automatically.
m := map[string]int{"a": 1, "b": 2}
v := m["a"] // Faster lookup internally
```

#### `os.Root` — Sandboxed Filesystem

Restrict filesystem operations to a specific directory — prevent path traversal attacks:

```text
import "os"

// ✅ os.Root — sandbox filesystem access
root, err := os.OpenRoot("/var/data")
if err != nil {
    log.Fatal(err)
}
defer root.Close()

// Access is sandboxed inside /var/data.
f, err := root.Open("users.json") // OK: /var/data/users.json
// root.Open("../etc/passwd")     // ❌ Error: path traversal blocked!

// Methods available:
// root.Open(name)
// root.Create(name)
// root.Remove(name)
// root.Mkdir(name, perm)
// root.Stat(name)
```

#### `go tool` — Tool Dependency Management

```bash
# ✅ Go 1.24: Track tool dependencies in go.mod
go get -tool golang.org/x/tools/cmd/stringer

# go.mod now has:
# tool golang.org/x/tools/cmd/stringer

# Run tool:
go tool stringer -type=Color

# Tools are cached — subsequent runs are fast
```

#### Crypto Packages

```text
// ✅ Go 1.24 Features:
import (
    "crypto/mlkem"   // Post-quantum: ML-KEM-768, ML-KEM-1024
    "crypto/hkdf"    // HMAC-based Key Derivation
    "crypto/pbkdf2"  // Password-based Key Derivation
    "crypto/sha3"    // SHA-3 hash
)
```

#### `testing.B.Loop` — Better Benchmarks

```text
// Go 1.24: testing.B.Loop replaces b.N pattern
func BenchmarkNew(b *testing.B) {
    for b.Loop() { // ✅ New — cleaner, prevents compiler optimizations
        doWork()
    }
}

// Old pattern (still works):
func BenchmarkOld(b *testing.B) {
    for i := 0; i < b.N; i++ {
        doWork()
    }
}
```

#### Weak Pointers

```text
import "weak"

// ✅ Go 1.24: Weak pointers — don't prevent GC
type Cache struct {
    entries map[string]weak.Pointer[ExpensiveObject]
}

// Cache entries use weak pointers — GC can collect them when memory is tight.
p := weak.Make(&obj)
if v := p.Value(); v != nil {
    // Object is still alive — use it.
} else {
    // Object was collected — recreate if needed.
}
```

---

### 🔹 Go 1.25 — Green Tea GC (Experimental)

Go 1.25 introduces **Green Tea GC** as an experiment — a new garbage collector improving performance for marking and scanning small objects through better locality.

```bash
# Go 1.25: Enable Green Tea GC (experimental)
GOEXPERIMENT=greenteagc go build .
```

---

### 🔹 Go 1.26 — Green Tea GC Default, Language Changes, SIMD

#### `new(expr)` — Enhanced `new` Built-in

Go 1.26 allows `new()` to accept an **expression** instead of just a type — very useful for optional pointer fields:

```text
// Pre-1.26: helper function needed
func intPtr(v int) *int { return &v }

type Person struct {
    Name string `json:"name"`
    Age  *int   `json:"age"` // nil = unknown
}

// ❌ Required a helper function.
p := Person{Name: "Alice", Age: intPtr(30)}

// ✅ Go 1.26: new(expression) — clean!
p := Person{
    Name: "Alice",
    Age:  new(yearsSince(born)), // accepts expressions directly
}
```

#### Self-Referencing Generic Types

Go 1.26 removes the restriction: generic types can now **reference themselves** in the type parameter list:

```text
// ❌ Pre-1.26: compile error
// ✅ Go 1.26: OK!
type Adder[A Adder[A]] interface {
    Add(A) A
}

func algo[A Adder[A]](x, y A) A {
    return x.Add(y)
}

// Use case: recursive data structures, self-referencing constraints
```

#### Green Tea Garbage Collector (Default)

Green Tea GC is now **enabled by default** (experimental in Go 1.25). Results:

- **10-40% reduction** in GC overhead for GC-heavy programs
- **+10% additional** on newer CPUs (Intel Ice Lake+, AMD Zen 4+) — using vector instructions
- Better locality and CPU scalability for marking/scanning small objects

```bash
# ✅ Go 1.26: Green Tea GC ON by default
go build .  # defaults using Green Tea GC

# Disable if you hit regressions.
GOEXPERIMENT=nogreenteagc go build .
```

#### `go fix` Modernizers

`go fix` has been **completely rewritten** — now the primary tool to modernize Go code:

```bash
# ✅ Modernize codebase to latest Go idioms.
go fix ./...

# Automated fixes include:
# - sort.Slice → slices.Sort
# - manual loops → range-over-int
# - manual path handling → os.Root
# - Source-level inliner via //go:fix inline directives
```

#### Faster cgo Calls

Go 1.26 reduces **~30% baseline runtime overhead** for cgo calls.

#### Heap Base Address Randomization

On 64-bit platforms, heap base address is now **randomized** at startup → security enhancement against exploits.

#### Goroutine Leak Profiler (Experimental)

Detect goroutines that are **leaked** — blocked forever on concurrency primitives:

```text
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Enable:
// GOEXPERIMENT=goroutineleakprofile go build .
//
// HTTP endpoint: /debug/pprof/goroutineleak
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

// Goroutine leak signatures exposing profiler warnings:
func processWorkItems(ws []workItem) ([]workResult, error) {
    ch := make(chan result) // unbuffered!
    for _, w := range ws {
        go func() {
            res, err := processWorkItem(w)
            ch <- result{res, err} // ❌ Blocks forever if the caller returns early.
        }()
    }

    var results []workResult
    for range len(ws) {
        r := <-ch
        if r.err != nil {
            return nil, r.err // ❌ LEAK: remaining goroutines block forever.
        }
        results = append(results, r.res)
    }
    return results, nil
}

// GC detects unreachable channels and flags the goroutine as leaked.
```

#### SIMD Package (Experimental)

```text
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// GOEXPERIMENT=simd go build .
// Currently amd64 only.
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
import "simd/archsimd"

// Int8x16 — 128-bit vector of 16 int8s
var a, b archsimd.Int8x16
c := a.Add(b) // SIMD vector addition — single instruction!

// Float64x8 — 512-bit vector of 8 float64s
var x, y archsimd.Float64x8
z := x.Add(y) // AVX-512 vector add
```

#### `crypto/hpke` Package

```text
import "crypto/hpke" // Hybrid Public Key Encryption (RFC 9180)
// Supports Hybrid Public Key Encryption (RFC 9180).
```

#### `runtime/secret` (Experimental)

```text
// GOEXPERIMENT=runtimesecret go build .
import "runtime/secret"
// Securely erase temporaries (registers, stack, heap)
// after use to prevent cryptographic key leakage.
```

#### Compiler: Stack Allocation Improvements

The compiler can now **allocate slice backing store on the stack** in more cases → reducing heap allocations.

Features from Go 1.22–1.24 are extensive — theory is covered. Now see what the version timeline looks like visually.

---

These advanced patterns sound powerful — but there is a real trap when using them in production: complexity increases while the team lacks the expertise to maintain. That trap will surface in PITFALLS.
## 2. VISUAL

New Go versions are often remembered as a list of release notes. The PNG below groups features by the pressure they resolve, helping you remember them much longer than a plain timeline.

![Go 1.22 to 1.26 feature map](./images/04-go-124-features-taxonomy.png)

*Figure: Instead of learning releases by timeline alone, learn by the type of pain point each feature cluster alleviates.*

### Go Version Timeline

```text
  Go 1.22 (Feb 2024)    Go 1.23 (Aug 2024)     Go 1.24 (Feb 2025)
  ─────────────────      ─────────────────       ─────────────────
  ✅ Loop var fix         ✅ Range over func       ✅ Generic type alias
  ✅ HTTP routing         ✅ unique package        ✅ Swiss table maps
  ✅ math/rand/v2         ✅ Timer changes         ✅ os.Root sandbox
                          ✅ Iterators stdlib      ✅ Weak pointers
                                                  ✅ go tool mgmt

Go 1.25 (Aug 2025)    Go 1.26 (Feb 2026)
  ─────────────────      ─────────────────
  ✅ Green Tea GC (exp)   ✅ Green Tea GC default
  ✅ Testing improvements ✅ new(expr)
                          ✅ Self-ref generics
                          ✅ go fix modernizers
                          ✅ Goroutine leak profile
                          ✅ SIMD (experimental)
                          ✅ crypto/hpke
                          ✅ cgo ~30% faster
                          ✅ Heap randomization
```

The diagram gives an overview of the timeline. Now let us consolidate all features into a practical example — an HTTP server using routing, range-over-func, and structured logging.

---

## 3. CODE

The visual of **Go 1.22 → 1.26 — New Features & Changes** gives you the big picture. Code is where decisions about cancellation, ownership, or sequencing become real behavior.

### Example 1: Advanced — complete modern Go HTTP server

> **Goal**: Consolidate many new features from Go 1.22-1.24 into a sufficiently practical example so readers see how they combine.
> **Approach**: Use the new stdlib routing, `iter.Seq`, generic type alias, and a small HTTP server for illustration.
> **Example**: Input is a CRUD user API with tag filtering; output is a server using newer syntax and runtime features.
> **Complexity**: Advanced

```go
package main

import (
    "encoding/json"
    "fmt"
    "iter"
    "log"
    "net/http"
    "os"
    "slices"
    "strings"
    "sync"
)

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Features used: Go 1.22 routing, Go 1.23 iterators,
// Go 1.24 generic type aliases
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

// Go 1.24: Generic type alias
type Set[T comparable] = map[T]struct{}

type User struct {
    ID    string `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
    Tags  Set[string] `json:"tags"`
}

var (
    users = make(map[string]User)
    mu    sync.RWMutex
)

// Go 1.23: Custom iterator — filter users by tag
func UsersByTag(tag string) iter.Seq[User] {
    return func(yield func(User) bool) {
        mu.RLock()
        defer mu.RUnlock()
        for _, u := range users {
            if _, ok := u.Tags[tag]; ok {
                if !yield(u) {
                    return
                }
            }
        }
    }
}

func main() {
    mux := http.NewServeMux()

// ✅ Go 1.22: Method + path param routing
    mux.HandleFunc("GET /api/users", func(w http.ResponseWriter, r *http.Request) {
        tag := r.URL.Query().Get("tag")
        var result []User

mu.RLock()
        if tag != "" {
            // ✅ Go 1.23: Range over function iterator
            for u := range UsersByTag(tag) {
                result = append(result, u)
            }
        } else {
            for _, u := range users {
                result = append(result, u)
            }
        }
        mu.RUnlock()

// ✅ Go 1.23: slices.SortFunc
        slices.SortFunc(result, func(a, b User) int {
            return strings.Compare(a.Name, b.Name)
        })

json.NewEncoder(w).Encode(result)
    })

mux.HandleFunc("GET /api/users/{id}", func(w http.ResponseWriter, r *http.Request) {
        id := r.PathValue("id") // ✅ Go 1.22 path params
        mu.RLock()
        user, ok := users[id]
        mu.RUnlock()
        if !ok {
            http.Error(w, "Not found", 404)
            return
        }
        json.NewEncoder(w).Encode(user)
    })

mux.HandleFunc("POST /api/users", func(w http.ResponseWriter, r *http.Request) {
        var user User
        if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
            http.Error(w, err.Error(), 400)
            return
        }
        mu.Lock()
        users[user.ID] = user
        mu.Unlock()
        w.WriteHeader(201)
        json.NewEncoder(w).Encode(user)
    })

// ✅ Go 1.24: os.Root for static files (sandboxed)
    if _, err := os.Stat("./public"); err == nil {
        mux.Handle("GET /static/{path...}",
            http.StripPrefix("/static/",
                http.FileServer(http.Dir("./public"))))
    }

addr := ":8080"
    fmt.Printf("🚀 Server (Go 1.24) listening on %s\n", addr)
    log.Fatal(http.ListenAndServe(addr, mux))
}
```

This example achieves the goal of "combining features into a real program" instead of just listing release notes. The caveat is that this is still a consolidated demo; when upgrading a real codebase, apply each feature based on need instead of trying to stuff everything in at once.

You have seen the new features consolidated. Now comes the dangerous part: loop variable capture still bites when using closures pre-1.22, and ServeMux routing precedence can cause surprises. The trap was formed in the feature list.

---

## 4. PITFALLS

From this point, with **Go 1.22 → 1.26 — New Features & Changes**, the focus is no longer making it work, but avoiding patterns that seem fine but silently create operational debt.

| # | Severity | Defect | Consequence | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Fatal | **Range func iterator leak** | Goroutine leak if producer does not check yield return | Return `false` from yield on break |
| 2 | 🟡 Common | **Loop var old behavior assumed** | Bug if using the `v := v` pattern no longer needed | Go 1.22+ auto-copies — remove `v := v` for cleaner code |
| 3 | 🟡 Common | **Timer.Reset without drain** (pre-1.23) | Stale value in channel causes wrong logic | Go 1.23+ fix — no need to drain |
| 4 | 🟡 Common | **`new(expr)` only Go 1.26+** | Compile error on older Go | Check `go` version in `go.mod` before using |
| 5 | 🟡 Common | **SIMD not yet stable** | API changes, amd64 only | `GOEXPERIMENT=simd` — use only for prototypes |
| 6 | 🔵 Minor | **Swiss table iteration order** | Depending on order will fail | Map iteration order is still random — do not depend on it |
| 7 | 🔵 Minor | **os.Root path escaping** | Using wrong path API outside Root | os.Root auto-blocks path traversal |
| 8 | 🔵 Minor | **Disable Green Tea GC** without reporting | Opt-out will be removed in Go 1.27 | Test thoroughly before relying on `nogreenteagc` |

You have covered features, demo, and the upgrade traps. The resources below help go deeper.

---

## 5. REF

| Resource | Type | Link | Notes |
| --- | --- | --- | --- |
| Go 1.26 Release Notes | Official docs | [go.dev/doc/go1.26](https://go.dev/doc/go1.26) | Green Tea GC, new(expr), SIMD |
| Go 1.24 Release Notes | Official docs | [go.dev/doc/go1.24](https://go.dev/doc/go1.24) | Swiss tables, os.Root, weak pointers |
| Go 1.23 Release Notes | Official docs | [go.dev/doc/go1.23](https://go.dev/doc/go1.23) | Range over func, unique, timer changes |
| Go 1.22 Release Notes | Official docs | [go.dev/doc/go1.22](https://go.dev/doc/go1.22) | Loop var fix, HTTP routing |
| Range Over Function Proposal | Proposal | [go.dev/wiki/RangefuncExperiment](https://go.dev/wiki/RangefuncExperiment) | iter.Seq design rationale |
| Routing Enhancements | Core team blog | [go.dev/blog/routing-enhancements](https://go.dev/blog/routing-enhancements) | Method matching, path params |
| Goroutine Leak Profile Proposal | Proposal | [go.dev/issue/74609](https://go.dev/issue/74609) | Experimental in Go 1.26 |
| SIMD Proposal | Proposal | [go.dev/issue/73787](https://go.dev/issue/73787) | amd64 only, experimental |

---

## 6. RECOMMEND

The most important point of **Go 1.22 → 1.26 — New Features & Changes** is clear. The extension below is for when you need to turn this understanding into a more complete investigation or operational workflow.

| Extension | When | Rationale | File/Link |
| --- | --- | --- | --- |
| **Migrate to Go 1.22 routing** | Simple APIs without needing a framework | Stdlib routing is now powerful enough with method matching and path params | [go.dev/blog/routing-enhancements](https://go.dev/blog/routing-enhancements) |
| **Adopt iter.Seq** | Custom collection types | Idiomatic iteration, zero goroutine overhead | [06-generator.md](./06-generator.md) |
| **os.Root** | File serving, multi-tenant | Security: prevent path traversal attack | [pkg.go.dev/os#OpenRoot](https://pkg.go.dev/os#OpenRoot) |
| **weak.Pointer** | Caches, canonical maps | Memory-efficient caching, GC-friendly | [pkg.go.dev/weak](https://pkg.go.dev/weak) |
| **`go fix ./...`** | Modernize codebase | Auto-upgrade to latest idioms, slices.Sort, range-over-int | CLI tool |
| **Goroutine leak profile** | CI/testing | Automatically detect goroutine leaks in test suite | [09-goroutine-leak-detection-and-containment.md](./09-goroutine-leak-detection-and-containment.md) |
| **Green Tea GC** | Performance-critical apps | 10-40% GC overhead reduction, default since 1.26 | [01-garbage-collector.md](./01-garbage-collector.md) |

---

**Navigation**: [← Memory Model](./03-memory-model.md) · [→ Performance & pprof](./05-performance-pprof.md)
