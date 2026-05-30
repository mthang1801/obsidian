<!-- tags: golang, comparable, generics, constraints -->
# 🔑 Comparable — The Gatekeeper for == and Map Keys

> Understanding comparable: which types qualify, the interface trap, and practical generic patterns

📅 Created: 2026-04-23 · 🔄 Updated: 2026-04-23 · ⏱️ 12 min read

| Aspect            | Detail                                                                      |
| ----------------- | --------------------------------------------------------------------------- |
| **Version**       | Go 1.18+ (refined in Go 1.20)                                              |
| **Use case**      | Map keys, generic `==` operations, Set/Cache/Index patterns                 |
| **Key insight**   | `comparable` is a compile-time gate — but interfaces can bypass it and panic |
| **Go philosophy** | Explicit constraints over implicit runtime checks                           |

---

## 1. DEFINE

Your first generic `Contains[T any]` function — you try `if v == target` and the compiler screams: *"cannot compare v == target (T is not comparable)"*. You change `any` to `comparable` and it compiles. Then a colleague passes `any` holding a `[]int` and the program panics at runtime. Welcome to `comparable`.

> *You need a generic Set, a generic Cache, a generic `Contains` function — any pattern that requires `==` on a type parameter. The `any` constraint is too broad: it accepts slices, maps, and functions — none of which support `==`. The `cmp.Ordered` constraint is too narrow: it excludes `bool`, `struct`, `*T`, and `chan`. `comparable` sits precisely in the middle — it admits exactly the types that the `==` operator accepts.*
>
> *But there is a trap. Since Go 1.20, `any` (and all interfaces) satisfy `comparable` at compile time. If the dynamic value inside the interface is a slice or map, the `==` comparison panics at runtime. This paradox — compile-time safety with a runtime escape hatch — is the single most important subtlety of `comparable`.*

### What `comparable` Means

`comparable` is a **built-in interface constraint**. It restricts a type parameter to types that support `==` and `!=`.

| Constraint     | Operators Allowed       | Package   | Example Types                      |
| -------------- | ----------------------- | --------- | ---------------------------------- |
| `any`          | None (no operators)     | builtin   | Everything including slices, funcs |
| `comparable`   | `==`, `!=`              | builtin   | int, string, struct, *T, [N]T     |
| `cmp.Ordered`  | `==`, `!=`, `<`, `>`, `<=`, `>=` | `cmp` | int, float64, string (no bool, struct) |

### Comparable Type Roster

| Type                        | Comparable? | Why                                             |
| --------------------------- | ----------- | ------------------------------------------------ |
| `int`, `int8`...`int64`     | ✅           | Value equality                                   |
| `uint`, `byte`, `rune`      | ✅           | Value equality                                   |
| `float32`, `float64`        | ✅           | ⚠️ `NaN != NaN` (IEEE 754)                       |
| `complex64`, `complex128`   | ✅           | Real + imaginary compared                        |
| `bool`                      | ✅           | `true == true`, `false == false`                 |
| `string`                    | ✅           | Byte-by-byte comparison                          |
| `*T` (pointers)             | ✅           | Compares **address**, not pointed-to value       |
| `chan T`                     | ✅           | Compares channel identity                        |
| `[N]T` (arrays)             | ✅           | Element-by-element, only if `T` is comparable    |
| `struct{...}`               | ✅           | Field-by-field, only if ALL fields are comparable |
| `[]T` (slices)              | ❌           | Can only compare to `nil`                        |
| `map[K]V`                   | ❌           | Can only compare to `nil`                        |
| `func(...)`                 | ❌           | Can only compare to `nil`                        |
| `interface{}` / `any`       | ⚠️ Special  | Compiles, but may panic at runtime               |

### The Constraint Hierarchy

```text
┌─────────────────────────────────────────────────────────┐
│  any                                                     │
│  Accepts everything. Cannot use ==, <, > on T.           │
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  comparable                                        │  │
│  │  Accepts == and != types. Map keys live here.      │  │
│  │                                                    │  │
│  │  ┌─────────────────────────────────────────────┐  │  │
│  │  │  cmp.Ordered                                 │  │  │
│  │  │  Accepts <, >, <=, >= as well.               │  │  │
│  │  │  int, float64, string — but NOT bool/struct  │  │  │
│  │  └─────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

The definitions are set. The visual below maps these rules into a decision flow to prevent choosing the wrong constraint.

---

## 2. VISUAL

The main risk with `comparable` is not syntax — it is choosing `any` when you meant `comparable`, or trusting `comparable` when the value hides behind an interface. The decision map below forces that check.

![Comparable decision map](./images/04-comparable-decision-map.png)

*Figure: The comparable decision map classifies Go types into four zones: safe comparable, never comparable, the interface trap, and the constraint hierarchy. Zone 3 (Interface Trap) is the source of most production panics.*

The visual is established. The code section below demonstrates each zone in action — from basic equality checks to the interface trap to production-grade generic patterns.

---

## 3. CODE

With **Comparable — The Gatekeeper for == and Map Keys**, the rules and zones are defined. Now let us see how each one behaves in actual code — starting from basic generic equality, through the interface trap, to full production patterns.

### Example 1: Basic — Why `comparable` Exists

> **Goal**: Demonstrate the compiler's enforcement of `comparable`
> **Requires**: Go 1.18+
> **Outcome**: Understanding when `==` is allowed in generic code

```go
package main

import "fmt"

// ✅ comparable constraint — enables == inside generic code
func Contains[T comparable](s []T, target T) bool {
    for _, v := range s {
        if v == target {  // Only compiles because T is comparable
            return true
        }
    }
    return false
}

// ✅ Index — returns position or -1
func Index[T comparable](s []T, target T) int {
    for i, v := range s {
        if v == target {
            return i
        }
    }
    return -1
}

// ❌ This would NOT compile with any:
// func BadContains[T any](s []T, target T) bool {
//     if s[0] == target {}  // ← compile error: operator == not defined for T
// }

func main() {
    // ✅ Works with all comparable types
    fmt.Println(Contains([]int{1, 2, 3}, 2))              // true
    fmt.Println(Contains([]string{"go", "rust"}, "go"))    // true
    fmt.Println(Contains([]float64{1.1, 2.2}, 3.3))       // false
    fmt.Println(Contains([]bool{true, false}, false))      // true

    // ✅ Structs with comparable fields
    type Point struct{ X, Y int }
    fmt.Println(Contains([]Point{{1, 2}, {3, 4}}, Point{3, 4}))  // true

    // ✅ Pointers (compares addresses)
    a := 42
    b := 42
    fmt.Println(Contains([]*int{&a}, &a))  // true  (same address)
    fmt.Println(Contains([]*int{&a}, &b))  // false (different address)

    // ❌ Compile error — slices are not comparable:
    // Contains([][]int{{1}, {2}}, []int{1})
}
```

> **Takeaway**: `comparable` is the minimum constraint for `==`. Without it, the compiler refuses to compare type parameters. With it, you can build `Contains`, `Index`, `Deduplicate`, `Set`, `Cache` — any pattern that requires equality checking.

Basic equality is covered. The next example exposes the most dangerous edge: what happens when interfaces meet `comparable`.

### Example 2: Intermediate — The Interface Trap

> **Goal**: Demonstrate the compile-time vs runtime gap
> **Requires**: Understanding of Go interfaces
> **Outcome**: Knowing when `comparable` can still panic

```go
package main

import "fmt"

func Equal[T comparable](a, b T) bool {
    return a == b
}

func main() {
    // ── Zone 1: Concrete types — always safe ──
    fmt.Println(Equal(42, 42))       // true  ✅
    fmt.Println(Equal("go", "go"))   // true  ✅

    // ── Zone 3: The Interface Trap ──
    // Since Go 1.20, `any` satisfies `comparable`

    var x, y any

    // Safe: dynamic type is int (comparable)
    x, y = 42, 42
    fmt.Println(Equal(x, y))  // true  ✅ — int is comparable

    // Safe: dynamic type is string (comparable)
    x, y = "hello", "hello"
    fmt.Println(Equal(x, y))  // true  ✅ — string is comparable

    // 💥 DANGEROUS: dynamic type is []int (NOT comparable)
    x = []int{1, 2, 3}
    y = []int{1, 2, 3}
    // fmt.Println(Equal(x, y))
    // ↑ COMPILES FINE ✅ ... but PANICS at runtime 💥
    // panic: runtime error: comparing uncomparable type []int

    // 💥 Same trap with maps
    x = map[string]int{"a": 1}
    y = map[string]int{"a": 1}
    // fmt.Println(Equal(x, y))  // PANIC 💥

    // ── How to defend against this ──
    // Option 1: Never pass interface values to comparable generics
    // Option 2: Use reflect at the boundary
    fmt.Println(safeEqual([]int{1, 2}, []int{1, 2})) // false (safely)
}

// safeEqual uses recover to prevent panics from interface comparison
func safeEqual[T comparable](a, b T) (result bool) {
    defer func() {
        if r := recover(); r != nil {
            result = false
        }
    }()
    return a == b
}
```

> **Why does Go allow this?** Before Go 1.20, `any` did NOT satisfy `comparable` — which was safe but too restrictive. You couldn't use `map[any]int` in generic code. Go 1.20 relaxed the rule for practical reasons, accepting the trade-off of possible runtime panics.

> **Takeaway**: The `comparable` constraint guarantees compile-time safety for concrete types. But when the concrete type is `any` (or any other interface), the guarantee downgrades to "compiles, but may panic." Defend with concrete types or `recover`.

The interface trap is understood. The next example puts `comparable` to work in production-grade generic data structures.

### Example 3: Advanced — Production Patterns

> **Goal**: Generic Set, Cache, Frequency, Deduplicate, GroupBy
> **Requires**: Generics + comparable constraint
> **Outcome**: Reusable, type-safe utility library

```go
package main

import (
    "cmp"
    "fmt"
    "maps"
    "slices"
)

// ────────────────────────────────────────────────────────
// Generic Set
// ────────────────────────────────────────────────────────

type Set[T comparable] struct {
    m map[T]struct{}
}

func NewSet[T comparable](vals ...T) Set[T] {
    s := Set[T]{m: make(map[T]struct{}, len(vals))}
    for _, v := range vals {
        s.m[v] = struct{}{}
    }
    return s
}

func (s Set[T]) Has(v T) bool        { _, ok := s.m[v]; return ok }
func (s Set[T]) Add(v T)             { s.m[v] = struct{}{} }
func (s Set[T]) Remove(v T)          { delete(s.m, v) }
func (s Set[T]) Len() int            { return len(s.m) }

func (s Set[T]) Intersection(other Set[T]) Set[T] {
    result := NewSet[T]()
    for k := range s.m {
        if other.Has(k) {
            result.Add(k)
        }
    }
    return result
}

func (s Set[T]) Union(other Set[T]) Set[T] {
    result := NewSet[T]()
    for k := range s.m { result.Add(k) }
    for k := range other.m { result.Add(k) }
    return result
}

func (s Set[T]) Difference(other Set[T]) Set[T] {
    result := NewSet[T]()
    for k := range s.m {
        if !other.Has(k) {
            result.Add(k)
        }
    }
    return result
}

// ────────────────────────────────────────────────────────
// Generic Deduplicate (preserves order)
// ────────────────────────────────────────────────────────

func Deduplicate[T comparable](s []T) []T {
    seen := make(map[T]struct{}, len(s))
    result := make([]T, 0, len(s))
    for _, v := range s {
        if _, exists := seen[v]; !exists {
            seen[v] = struct{}{}
            result = append(result, v)
        }
    }
    return result
}

// ────────────────────────────────────────────────────────
// Generic Frequency Counter
// ────────────────────────────────────────────────────────

func Frequency[T comparable](s []T) map[T]int {
    freq := make(map[T]int, len(s))
    for _, v := range s {
        freq[v]++
    }
    return freq
}

// ────────────────────────────────────────────────────────
// Generic GroupBy
// ────────────────────────────────────────────────────────

func GroupBy[T any, K comparable](s []T, keyFn func(T) K) map[K][]T {
    groups := make(map[K][]T)
    for _, v := range s {
        k := keyFn(v)
        groups[k] = append(groups[k], v)
    }
    return groups
}

// ────────────────────────────────────────────────────────
// Generic Cache
// ────────────────────────────────────────────────────────

type Cache[K comparable, V any] struct {
    data map[K]V
}

func NewCache[K comparable, V any]() *Cache[K, V] {
    return &Cache[K, V]{data: make(map[K]V)}
}

func (c *Cache[K, V]) Get(key K) (V, bool) {
    v, ok := c.data[key]
    return v, ok
}

func (c *Cache[K, V]) Set(key K, value V) {
    c.data[key] = value
}

func (c *Cache[K, V]) GetOrCompute(key K, compute func() V) V {
    if v, ok := c.data[key]; ok {
        return v
    }
    v := compute()
    c.data[key] = v
    return v
}

// ────────────────────────────────────────────────────────

type User struct {
    Name string
    Role string
    Age  int
}

func main() {
    // ── Set operations ──
    a := NewSet(1, 2, 3, 4, 5)
    b := NewSet(4, 5, 6, 7, 8)
    fmt.Println("Intersection:", a.Intersection(b).Len())  // 2 (4, 5)
    fmt.Println("Union:", a.Union(b).Len())                // 8
    fmt.Println("Difference:", a.Difference(b).Len())      // 3 (1, 2, 3)

    tags := NewSet("go", "rust", "python", "go", "rust")
    fmt.Println("Unique tags:", tags.Len())  // 3

    // ── Deduplicate ──
    nums := []int{5, 3, 5, 1, 3, 8, 1}
    fmt.Println(Deduplicate(nums))  // [5 3 1 8]

    // ── Frequency ──
    words := []string{"go", "is", "go", "great", "go"}
    freq := Frequency(words)
    for _, k := range slices.Sorted(maps.Keys(freq)) {
        fmt.Printf("  %s: %d\n", k, freq[k])
    }
    // go: 3, great: 1, is: 1

    // ── GroupBy ──
    users := []User{
        {"Alice", "admin", 30}, {"Bob", "user", 25},
        {"Charlie", "admin", 35}, {"Diana", "user", 28},
    }
    byRole := GroupBy(users, func(u User) string { return u.Role })
    for role, members := range byRole {
        fmt.Printf("  %s: %d members\n", role, len(members))
    }

    // ── Cache with struct keys ──
    type Coord struct{ X, Y int }
    grid := NewCache[Coord, string]()
    grid.Set(Coord{0, 0}, "origin")
    grid.Set(Coord{1, 2}, "point A")
    label, _ := grid.Get(Coord{1, 2})
    fmt.Println("Grid:", label)  // "point A"
}
```

> **Why does `Set` require `comparable`?** Because `Set` is backed by `map[T]struct{}`, and **map keys must be comparable**. This is the fundamental connection: `comparable` is the constraint that enables map keys, and map keys enable Set, Cache, Frequency, and Deduplicate.

> **Takeaway**: `comparable` is the foundation for Go's most common generic patterns. Set, Cache, GroupBy, Deduplicate, Frequency — all require the `==` operator and therefore the `comparable` constraint. The `K comparable, V any` pair is the most common generic signature in production Go code.

---

## 4. PITFALLS

The mechanics of **Comparable — The Gatekeeper for == and Map Keys** are clear. What remains is avoiding the traps that compile successfully but fail at runtime or produce incorrect results.

| # | Severity | Error | Consequence | Fix |
|---|----------|-------|-------------|-----|
| 1 | 🔴 Fatal | Passing interface holding non-comparable value | Runtime panic: `comparing uncomparable type []int` | Only pass concrete comparable types to `comparable` generics; use `recover` at boundaries |
| 2 | 🔴 Fatal | `NaN != NaN` in float comparisons | Set/Map cannot find NaN; duplicates accumulate | Filter NaN with `math.IsNaN()` before inserting into Set/Map |
| 3 | 🟡 Common | Pointer equality checks address, not value | `&Point{1,2} != &Point{1,2}` — same data, different pointers | Dereference and compare the value, or use the value type directly |
| 4 | 🟡 Common | Adding a `[]byte` or `map` field to a struct | Entire struct becomes non-comparable — breaks all generic uses | Use `[N]byte` (array) instead, or redesign |
| 5 | 🟡 Common | Confusing `comparable` with `cmp.Ordered` | `comparable` allows `==` only — no `<`, `>`, sorting | Use `cmp.Ordered` when you need ordering operations |
| 6 | 🔵 Minor | `comparable` does not include `bool` in `cmp.Ordered` | Cannot sort booleans | `bool` satisfies `comparable` but not `cmp.Ordered` — this is correct |

### 🔴 Pitfall #1 — The Interface Trap

This is the most dangerous pitfall. Since Go 1.20, `any` satisfies `comparable` at compile time. But if the runtime value inside the interface is a slice, map, or function — the `==` operator panics.

```go
// This code COMPILES but PANICS:
var a, b any = []int{1, 2}, []int{1, 2}
fmt.Println(a == b)  // 💥 panic: comparing uncomparable type []int

// Defense: never pass interface values to comparable generics
// unless you control the dynamic type.
```

**Rule**: Treat `Equal[any](x, y)` as "compile-time unsafe" — review every call site to ensure the dynamic types are comparable.

### 🔴 Pitfall #2 — NaN Breaks Everything

```go
nan := math.NaN()
set := NewSet(nan, nan, nan)
fmt.Println(set.Len())   // 3 — each NaN is "different" (NaN != NaN)
fmt.Println(set.Has(nan)) // false — can never find NaN
```

**Rule**: Filter `NaN` values before inserting into any `comparable`-based data structure.

### 🟡 Pitfall #3 — Pointer Equality ≠ Value Equality

```go
a := &User{Name: "Alice"}
b := &User{Name: "Alice"}
fmt.Println(a == b)  // false — different memory addresses

set := NewSet(a, b)
fmt.Println(set.Len())  // 2 — two entries for "same" user
```

**Rule**: Use value types (not pointers) as Set/Map keys when you want value-based equality. If you must use pointers, create a custom key type (e.g., `UserID string`).

---

## 5. REF

| Resource | Type | Link | Notes |
| --- | --- | --- | --- |
| Go Spec — Comparable | Official | [go.dev/ref/spec#Comparison_operators](https://go.dev/ref/spec#Comparison_operators) | Source of truth for which types support `==` |
| Go 1.20 Release — Comparable change | Official | [go.dev/doc/go1.20#language](https://go.dev/doc/go1.20#language) | The spec change that made `any` satisfy `comparable` |
| Go Blog — Intro to Generics | Official | [go.dev/blog/intro-generics](https://go.dev/blog/intro-generics) | Covers constraints including `comparable` |
| cmp package | Official | [pkg.go.dev/cmp](https://pkg.go.dev/cmp) | `cmp.Ordered` — the ordering constraint built on top of `comparable` |

---

## 6. RECOMMEND

The core of **Comparable — The Gatekeeper for == and Map Keys** is clear. The branches below connect `comparable` to its adjacent topics.

| Extension | When to Read Next | Rationale | File/Link |
| --- | --- | --- | --- |
| Generics — Type Parameters | When you need the full generics picture | `comparable` is one constraint within the broader generics system | [02-generics.md](./02-generics.md) |
| Type Assertion & Embedding | When interfaces interact with comparable | The interface trap lives at the intersection of interfaces and comparable | [03-type-assertion-embedding.md](./03-type-assertion-embedding.md) |
| Slices, Maps, Strings | When you need to understand why slices aren't comparable | Slice internals explain why `==` is impossible for slices | [01-slices-maps-strings.md](./01-slices-maps-strings.md) |
| cmp package | When you need ordering, not just equality | `cmp.Ordered` extends `comparable` with `<`, `>` operators | [pkg.go.dev/cmp](https://pkg.go.dev/cmp) |

---

**Sequential Navigation**: [← Type Assertion & Embedding](./03-type-assertion-embedding.md) · [→ Generics](./02-generics.md)
