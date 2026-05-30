<!-- tags: golang, packages, data-structures -->
# 📦 Slices & Maps — Built-in Functions & Package `slices`/`maps`

> A comprehensive guide to built-in functions for slices and maps: `append`, `copy`, `delete`, `clear`, along with Go 1.21+ packages `slices` and `maps`.

📅 Created: 2026-03-23 · 🔄 Updated: 2026-04-19 · ⏱️ 18 min read

| Aspect       | Detail                                                    |
| ------------ | --------------------------------------------------------- |
| **Built-in** | `append`, `copy`, `delete`, `clear`, `len`, `cap`, `make` |
| **Packages** | `slices` (Go 1.21+), `maps` (Go 1.21+)                    |
| **Use case** | CRUD operations, sort, search, transform                  |
| **Key rule** | `append` may create a new slice — always reassign          |

---

## 1. DEFINE

Go 1.21 introduced `slices.Contains()`, `slices.Sort()`, `maps.Keys()` — finally eliminating the need to hand-roll utility functions for basic operations. But a wider API surface does not mean easier correctness: `slices.Delete()` modifies the slice in-place yet returns a new slice, and `maps.Keys()` makes no guarantees about order.

> *You just deployed a new API. Production logs read: `index out of range [5] with length 3`. The server crashes, returning 500s to every client. You open the code and find `data := users[2:5]` — a sub-slice referencing an underlying array that `append` in another goroutine has already shrunk. Two lines of code that looked perfectly harmless are silently sharing memory you never knew about.*
>
> *A slice in Go is not an array — it is a **view** into the array underneath. `append` may allocate a brand-new array or overwrite the existing one depending on capacity. Maps, meanwhile, deliberately randomize iteration order — not a bug, but Go's way of forcing you never to depend on traversal sequence. Misunderstanding these two data structures is the single most common source of production bugs in Go.*

### Built-in Functions for Slices

| Function | Signature                       | Description                       |
| -------- | ------------------------------- | --------------------------------- |
| `make`   | `make([]T, len, cap)`           | Create slice with len and capacity |
| `append` | `append(s []T, elems ...T) []T` | Add elements, may reallocate       |
| `copy`   | `copy(dst, src []T) int`        | Copy elements, returns count copied |
| `len`    | `len(s []T) int`                | Current number of elements         |
| `cap`    | `cap(s []T) int`                | Capacity (allocated memory)        |
| `clear`  | `clear(s []T)` (Go 1.21+)       | Set all elements to zero value     |

### Built-in Functions for Maps

| Function | Signature                     | Description                       |
| -------- | ----------------------------- | --------------------------------- |
| `make`   | `make(map[K]V, hint)`         | Create map, hint = expected size   |
| `delete` | `delete(m map[K]V, key K)`    | Remove key; no-op if key absent    |
| `len`    | `len(m map[K]V) int`          | Number of key-value pairs          |
| `clear`  | `clear(m map[K]V)` (Go 1.21+) | Remove all entries                 |

### Package `slices` (Go 1.21+)

| Function          | Description                    |
| ----------------- | ------------------------------ |
| `slices.Sort`     | Sort slice in-place            |
| `slices.SortFunc` | Sort with custom comparator    |
| `slices.Contains` | Check whether element exists   |
| `slices.Index`    | Find index of element          |
| `slices.Delete`   | Remove elements by range       |
| `slices.Insert`   | Insert elements at position    |
| `slices.Compact`  | Remove consecutive duplicates  |
| `slices.Reverse`  | Reverse slice in-place         |
| `slices.Clip`     | Reduce capacity to length      |

---

The operations above look deceptively simple on paper. The part most likely to mislead you is how state actually mutates at runtime. The visual below pulls those hidden mechanics into a mental model you should keep in mind every time you debug a memory issue.

## 2. VISUAL

This topic is easy to misjudge because the API surface is so small. It looks like just a handful of basic operations, yet real bugs explode at the intersection of aliasing, nil semantics, and mutation boundaries. The visual below brings exactly those three pressure points to the surface.

![Slices and maps mental model](./images/06-slices-maps-mental-model.png)

*Figure: Mental-model card combining the four things you need to hold in your head simultaneously when working with slices and maps: the slice header, shared backing array, nil-map semantics, and the practical role of the `slices`/`maps` packages.*

With those boundaries now visible, the code below will read very differently: you will not just see what each function does, but whether the operation silently retains an alias or opens a path for the caller to corrupt data.

## 3. CODE

With the map of collection operations laid out in **Slices & Maps**, it is time to bring it down to code — to see how each choice (`append` vs `slices.Concat`, manual `delete` vs `slices.Delete`, raw map iteration vs `maps.Keys`) actually shifts API clarity and safety.

### Example 1: Basic — Built-in Slice & Map Operations

You have a list of users and need to: add a new user (`append`), remove a user by index, and copy the list for backup. Slices and maps are the two data structures you use most in Go — but they come loaded with gotchas: `append` may not modify the original slice, and `delete` on a map does not panic if the key is missing.

Understanding built-in operations (`make`, `append`, `copy`, `delete`, `len`, `cap`) is the foundation for everything you do with data in Go.

Input: `append([]int{1,2}, 3)` · Output: `[1, 2, 3]`

```go
package main

import "fmt"

func main() {
	// ━━━━━ Slice basics ━━━━━
	s := make([]int, 0, 5)
	fmt.Printf("len=%d cap=%d %v\n", len(s), cap(s), s) // len=0 cap=5 []

	// ✅ Append — always reassign because append may create a new slice
	s = append(s, 1, 2, 3)
	fmt.Println(s) // [1 2 3]

	// Append another slice
	more := []int{4, 5, 6}
	s = append(s, more...) // ✅ Spread operator
	fmt.Println(s)          // [1 2 3 4 5 6]

	// ━━━━━ Copy ━━━━━
	src := []int{10, 20, 30}
	dst := make([]int, len(src))
	n := copy(dst, src)
	fmt.Printf("Copied %d items: %v\n", n, dst) // Copied 3 items: [10 20 30]

	// ⚠️ Copy only copies min(len(dst), len(src)) items
	small := make([]int, 2)
	copy(small, src)
	fmt.Println(small) // [10 20] — only 2 items

	// ━━━━━ Slice expressions ━━━━━
	a := []int{0, 1, 2, 3, 4, 5}
	fmt.Println(a[2:4])   // [2 3]     — from index 2 to 3
	fmt.Println(a[:3])    // [0 1 2]   — first 3
	fmt.Println(a[3:])    // [3 4 5]   — from index 3

	// ━━━━━ Map basics ━━━━━
	m := map[string]int{
		"go":     1,
		"python": 2,
		"rust":   3,
	}

	// Access
	fmt.Println(m["go"])            // 1

	// ✅ Comma-ok pattern — check whether key exists
	val, ok := m["java"]
	fmt.Printf("val=%d, exists=%v\n", val, ok) // val=0, exists=false

	// Delete
	delete(m, "python")
	fmt.Println(len(m)) // 2

	// ✅ Clear (Go 1.21+) — remove all entries, keep map
	clear(m)
	fmt.Println(len(m)) // 0
}
```

> When `len == cap`, there is no room left in the underlying array. `append` allocates a new array (typically 2× capacity), copies the old data, and adds the new element. The return value is a new slice header pointing to the new array — if you do not reassign (`s = append(s, v)`), you lose the reference.

> **Takeaway**: Always `s = append(s, v)`. Use the comma-ok idiom `val, ok := m[key]` to check key existence safely. `clear()` (Go 1.21+) resets a collection while retaining its allocated memory. `copy` only transfers `min(len(dst), len(src))` items.

Those basic operations are sufficient for simple logic. But hand-writing loops for searching, sorting, or range deletion is fragile at the edges — which is exactly why Go 1.21 pulled the generic `slices` and `maps` packages into the standard library.

### Example 2: Intermediate — Package `slices` (Go 1.21+)

Before Go 1.21, sorting a slice required `sort.Slice(s, func(i, j int) bool {...})` — verbose and non-generic. Finding an element meant writing a loop. Comparing two slices meant iterating element by element.

Package `slices` (Go 1.21+) provides generic functions: `slices.Sort`, `slices.Contains`, `slices.Equal`, `slices.Compact` — type-safe, concise, and typically faster than hand-written code.

Input: `slices.Contains([]string{"a","b","c"}, "b")` · Output: `true`

```go
package main

import (
	"cmp"
	"fmt"
	"slices"
)

func main() {
	// ━━━━━ Sort ━━━━━
	nums := []int{5, 3, 8, 1, 9, 2}
	slices.Sort(nums)
	fmt.Println(nums) // [1 2 3 5 8 9]

	// SortFunc — custom comparator
	type User struct {
		Name string
		Age  int
	}
	users := []User{
		{"Charlie", 30},
		{"Alice", 25},
		{"Bob", 28},
	}
	slices.SortFunc(users, func(a, b User) int {
		return cmp.Compare(a.Age, b.Age) // ✅ cmp.Compare for type-safe comparison
	})
	fmt.Println(users)
	// [{Alice 25} {Bob 28} {Charlie 30}]

	// ━━━━━ Search ━━━━━
	names := []string{"Alice", "Bob", "Charlie", "David"}
	fmt.Println(slices.Contains(names, "Bob"))    // true
	fmt.Println(slices.Contains(names, "Eve"))    // false
	fmt.Println(slices.Index(names, "Charlie"))   // 2
	fmt.Println(slices.Index(names, "Eve"))       // -1

	// ━━━━━ Insert / Delete ━━━━━
	s := []int{1, 2, 5, 6}

	// Insert at index 2
	s = slices.Insert(s, 2, 3, 4)
	fmt.Println(s) // [1 2 3 4 5 6]

	// Delete range [1, 3) — removes indices 1 and 2
	s = slices.Delete(s, 1, 3)
	fmt.Println(s) // [1 4 5 6]

	// ━━━━━ Compact — remove consecutive duplicates ━━━━━
	dup := []int{1, 1, 2, 2, 2, 3, 3, 1}
	dup = slices.Compact(dup)
	fmt.Println(dup) // [1 2 3 1] — only consecutive dups removed

	// ✅ For unique values: sort first, then compact
	all := []int{3, 1, 4, 1, 5, 9, 2, 6, 5, 3}
	slices.Sort(all)
	all = slices.Compact(all)
	fmt.Println(all) // [1 2 3 4 5 6 9]

	// ━━━━━ Other utilities ━━━━━
	r := []int{1, 2, 3, 4, 5}
	slices.Reverse(r)
	fmt.Println(r) // [5 4 3 2 1]

	fmt.Println(slices.Min([]int{5, 2, 8, 1})) // 1
	fmt.Println(slices.Max([]int{5, 2, 8, 1})) // 8
}
```

> `sort.Slice` uses `interface{}` + reflection — slower. `slices.Sort` uses generics — type-safe, zero reflection, ~30% faster. `slices.SortFunc` + `cmp.Compare` provides a custom comparator that is safer than a manual `if a < b return -1`.

> **Takeaway**: Use `slices.Contains`/`Index` for search, `slices.Delete` for range removal, Sort + Compact for unique values. `slices.Reverse` works in-place. `slices.Min`/`Max` cover comparable types.

The `slices` package handles the one-dimensional array world well. But the thorniest problems live in map territory — where systems demand config merges, isolated data clones, and group-by aggregations, and where careless shallow copies breed silent bugs. That is what the `maps` package was built for.

### Example 3: Advanced — Package `maps` & Real-world Patterns

You have a config map and need to: merge defaults with user overrides, clone a map to avoid shared state, and collect all keys for sorted output. Before Go 1.21, each of these operations required hand-written utility functions.

Package `maps` (Go 1.21+) provides `maps.Clone`, `maps.Copy`, `maps.Keys`, `maps.Values`, `maps.Equal` — eliminating boilerplate and avoiding common bugs like shallow copy vs deep copy confusion.

Input: `maps.Clone(map[string]int{"a": 1})` · Output: an independent copy; modifying it does not affect the original

```go
package main

import (
	"fmt"
	"maps"
	"slices"
)

func main() {
	// ━━━━━ maps.Keys / maps.Values ━━━━━
	inventory := map[string]int{
		"laptop":   5,
		"mouse":    50,
		"keyboard": 30,
	}

	// ✅ Get sorted keys
	keys := slices.Sorted(maps.Keys(inventory))
	fmt.Println("Products:", keys) // [keyboard laptop mouse]

	values := slices.Collect(maps.Values(inventory))
	fmt.Println("Counts:", values)

	// ━━━━━ maps.Clone — shallow copy ━━━━━
	clone := maps.Clone(inventory)
	clone["laptop"] = 10 // ✅ Does not affect original
	fmt.Println("Original:", inventory["laptop"]) // 5
	fmt.Println("Clone:", clone["laptop"])         // 10

	// ━━━━━ maps.Equal — compare maps ━━━━━
	m1 := map[string]int{"a": 1, "b": 2}
	m2 := map[string]int{"a": 1, "b": 2}
	m3 := map[string]int{"a": 1, "b": 3}
	fmt.Println(maps.Equal(m1, m2)) // true
	fmt.Println(maps.Equal(m1, m3)) // false

	// ━━━━━ maps.Copy — merge maps ━━━━━
	defaults := map[string]string{
		"host":    "localhost",
		"port":    "8080",
		"mode":    "debug",
	}
	overrides := map[string]string{
		"port":    "3000",
		"mode":    "production",
	}
	// ✅ Copy overrides into defaults — overrides win
	maps.Copy(defaults, overrides)
	fmt.Println(defaults)
	// map[host:localhost mode:production port:3000]

	// ━━━━━ Pattern: Group by ━━━━━
	type Item struct {
		Name     string
		Category string
	}
	items := []Item{
		{"Go", "language"},
		{"Python", "language"},
		{"Docker", "tool"},
		{"Rust", "language"},
		{"K8s", "tool"},
	}

	grouped := make(map[string][]Item)
	for _, item := range items {
		grouped[item.Category] = append(grouped[item.Category], item)
	}
	for cat, group := range grouped {
		fmt.Printf("%s: %d items\n", cat, len(group))
	}

	// ━━━━━ Pattern: Frequency counter ━━━━━
	text := "go is great and go is fast"
	freq := make(map[string]int)
	for _, word := range []string{"go", "is", "great", "and", "go", "is", "fast"} {
		freq[word]++
	}
	fmt.Println(freq)
	// map[and:1 fast:1 go:2 great:1 is:2]
	_ = text
}
```

> **Why does `maps.Copy` overwrite keys?**
> `maps.Copy(dst, src)` copies all key-value pairs from `src` into `dst`. If a key collides, src wins. This is the merge pattern: defaults + overrides. `maps.Clone` produces a shallow copy — nested maps/slices still share references. `maps.Equal` performs O(n) deep equality on map values.

> **Takeaway**: `maps.Clone` for shallow copy, `maps.Copy` for merge/override. Group-by pattern: `map[key][]Item` + `append`. Frequency counter: `map[key]int` + `++`.

---

## 4. PITFALLS

The correct mechanics are in hand. What remains is recognizing the spots where code looks _almost right_ but silently plants a slice mutation bug or a map ordering issue straight into production.

| # | Severity | Bug | Consequence | Fix |
|---|----------|-----|-------------|-----|
| 1 | 🔴 Fatal | Not reassigning `append` — `append(s, v)` loses data | Data loss | Always `s = append(s, v)` |
| 2 | 🔴 Fatal | Concurrent map read+write → panic | Runtime crash | `sync.RWMutex` or `sync.Map` |
| 3 | 🔴 Fatal | Nil map write → panic | Runtime crash | `make(map[K]V)` or literal `map[K]V{}` |
| 4 | 🟡 Common | Slice shares underlying array | Sub-slice modification affects original | `slices.Clone()` or `copy()` |
| 5 | 🟡 Common | Iterate + delete slice → skip elements | Logic error | Iterate in reverse or use `slices.DeleteFunc` |

### 🔴 Pitfall #1 — Append silently swallows data

This code compiles, runs, and looks perfectly correct:

```go
func addItem(items []int, val int) {
    append(items, val) // ← looks reasonable, but data is lost
}
```

`append` returns a **new** slice (potentially pointing to a new array if capacity was full). If you do not reassign `items = append(items, val)`, the new value is discarded. The Go compiler issues no warning — this is a pure logic error. Worse: if capacity remains, `append` writes into the original array but the slice header's `len` is not updated — the data exists but is invisible.

**Fix**: Always `s = append(s, v)`. If you need to modify a slice inside a function: return the new slice or use `*[]T`.

### 🔴 Pitfall #2 — Map concurrent crash that you cannot reproduce

Maps in Go are **not thread-safe**. Two goroutines reading and writing the same map simultaneously trigger a runtime panic (not a data race — the Go runtime **intentionally crashes** via concurrent map detection):

```go
m := map[string]int{}
go func() { m["a"] = 1 }()
go func() { _ = m["a"] }()
// fatal error: concurrent map read and map write
```

This bug is not stable — it only surfaces when the scheduler interleaves at exactly the right timing. Tests pass, staging passes, production crashes. Use `sync.RWMutex` for concurrent access or `sync.Map` for read-heavy workloads.

### 🔴 Pitfall #3 — Nil map: silent on reads, lethal on writes

This line will never survive a single request:

```go
var config map[string]string // nil map — points to nothing
config["host"] = "localhost" // panic: assignment to entry in nil map
```

This is a rudimentary but classic mistake when config injection or JSON parsing skips initialization. A nil map allows reads safely (it behaves as an empty map and returns zero values without crashing), but any write causes an immediate panic. Always use `make(map[K]V)` — and pass a size hint if you know the expected number of entries.

### 🟡 Pitfall #4 — Slice shared memory

The example below demonstrates how a sub-slice (a view) reaches through the boundary and modifies the original array:

```go
package main

import "fmt"

func main() {
	original := []int{1, 2, 3, 4, 5}
	sub := original[1:3] // [2 3] — shares underlying array!

	sub[0] = 99
	fmt.Println(original) // [1 99 3 4 5] — ⚠️ original was modified!

	// ✅ Fix: clone before modifying
	safe := make([]int, len(original[1:3]))
	copy(safe, original[1:3])
	safe[0] = 42
	fmt.Println(original) // [1 99 3 4 5] — unaffected
}
```

### 🟡 Pitfall #5 — Iterate-and-delete: the index leap

The habit of deleting elements while looping forward is a trap — the array shrinks under your feet:

```go
users := []string{"Bob", "Alice", "Alice", "Eve"}
for i, u := range users {
	if u == "Alice" {
		users = append(users[:i], users[i+1:]...) // ⚠ Index shifts, skipping adjacent element
	}
}
```

Scanning a slice front-to-back while removing elements causes index displacement that silently skips neighboring items. The definitive solution is `slices.DeleteFunc`, which handles the full sweep without any risk of skipping the next iteration.

---

You have walked through slices & maps from basics to concurrent patterns. The resources below will take you deeper.

## 5. REF

| Resource                  | Type     | Link                                                         | Notes |
| ------------------------- | -------- | ------------------------------------------------------------ | ----- |
| `slices` package          | Official | [pkg.go.dev/slices](https://pkg.go.dev/slices)               | Go 1.21+ generic slices |
| `maps` package            | Official | [pkg.go.dev/maps](https://pkg.go.dev/maps)                   | Go 1.21+ generic maps |
| Go Blog — Slices intro    | Blog     | [go.dev/blog/slices-intro](https://go.dev/blog/slices-intro) | Internal mechanics |
| Go Blog — Go Slices usage | Blog     | [go.dev/blog/slices](https://go.dev/blog/slices)             | Best practices |
| Go Wiki — SliceTricks     | Wiki     | [go.dev/wiki/SliceTricks](https://go.dev/wiki/SliceTricks)   | Classic patterns |

---

## 6. RECOMMEND

You have just mastered slice and map operations in the comfortable world of single-goroutine, sequential execution. The code runs predictably — but real production workloads rarely operate in isolation.

When thousands of concurrent requests hit your service and goroutines start fighting over a shared config map, every lesson about plain maps from this article suddenly collapses. That is when `sync.Map` enters the picture. And when you need a data structure that can efficiently yield the highest-priority element instead of scanning an entire slice, `container/heap` is the next door to open.

| Extension              | When                  | Why                             | File/Link |
| ---------------------- | --------------------- | ------------------------------- | --------- |
| `sync.Map` | Concurrent map access | Thread-safe map built-in        | [pkg.go.dev/sync#Map](https://pkg.go.dev/sync#Map) |
| `container/heap` | Priority queue        | Heap interface for custom types | [pkg.go.dev/container/heap](https://pkg.go.dev/container/heap) |
| `container/list` | Doubly linked list    | O(1) insert/remove middle       | [pkg.go.dev/container/list](https://pkg.go.dev/container/list) |
| `container/ring` | Circular buffer       | Fixed-size rotating buffer      | [pkg.go.dev/container/ring](https://pkg.go.dev/container/ring) |
| Generics collections | Type-safe utilities   | `lo`, `samber/lo` library       | [github.com/samber/lo](https://github.com/samber/lo) |

---

**Navigation**: [← math](./05-math.md) · [→ Functions README](./README.md)
