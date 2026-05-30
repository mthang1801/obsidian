<!-- tags: golang, data-structures, arrays -->
# 🔗 Array Pipeline — Map, Filter, Reduce, Some, Every

> JavaScript chains `.filter().map().reduce()` with implicit garbage collection. Go demands explicit `for` loops — each functional pipeline allocates a new slice. Generics (Go 1.18+) bring type safety to utility functions, but hot paths still need manual loops.

📅 Created: 2026-03-23 · 🔄 Updated: 2026-04-19 · ⏱️ 18 min read

## 1. DEFINE

A senior frontend developer processes 50,000 employee records using `Filter(employees).Map(extractName)`. Each pipeline step allocates a fresh slice and copies structs. Two steps on 50K records = 100K allocations. The container runs out of memory.

JavaScript hides this cost behind its garbage collector. Go makes it explicit: every `append` to a new slice costs memory. Generics (Go 1.18+) let you write type-safe `Map`, `Filter`, and `Reduce` functions — but they still allocate intermediate slices. For hot paths, a manual `for` loop with a single pre-allocated result slice is 3-5x faster.

### 1.1 Invariants & Failure Modes

| Boundary | Core Responsibility |
| --- | --- |
| **Pipeline types** | JavaScript chains mutate data implicitly. Go utilities pass explicit closures over typed slices. |
| **Performance** | Declarative pipelines prioritize readability. Hot-path loops prioritize minimal allocations. |

| Rule | Rationale |
| --- | --- |
| **Avoid deep chaining** | `Reduce(Map(Filter(data)))` destroys readability. Break into intermediate variables. |
| **Value copies vs pointers** | `Map` over `[]User` copies each struct. For large structs, use `[]*User` to avoid copying. |

### 1.2 Failure Cascades

- **The phantom element:** `Find` returns a zero-value struct and `false` when no match exists. If you ignore the boolean, you process `User{ID: 0}` — which might accidentally match a real record in your database.
- **The comparable crash:** `Includes(slice, target)` requires `comparable` constraint. Passing a slice of maps triggers a compile error. Use `Some` with a predicate instead.

## 2. VISUAL

The gap between JavaScript chaining and Go explicit loops is the allocation model. The visual maps each JS array method to its Go equivalent.

![Array Pipeline Operations](./images/02-array-pipeline-compare.png)

*Figure: JS array methods mapped to Go generic equivalents. Each Go function accepts a typed slice and a closure. Unlike JS, each step allocates a new slice.*

## 3. CODE

With the allocation trade-offs established, the code below builds the five core utilities (`Map`, `Filter`, `Reduce`, `Find`, `Includes`) and two advanced helpers (`FlatMap`, `Chunk`).

### Example 1: Basic — The Core 5 Utilities

> **Goal**: Build type-safe `Map`, `Filter`, and `Reduce` using Go generics.
> **Approach**: Each function takes a `[]T` and a closure, returning a new slice.
> **Complexity**: O(N) per function — one pass over the input slice.

```go
// core_pipeline.go
package utils

// Map transforms each element using the mapper function.
func Map[T any, R any](slice []T, mapper func(T) R) []R {
	result := make([]R, len(slice))
	for i, item := range slice {
		result[i] = mapper(item)
	}
	return result
}

// Filter returns elements where the predicate returns true.
func Filter[T any](slice []T, predicate func(T) bool) []T {
	var result []T
	for _, item := range slice {
		if predicate(item) {
			result = append(result, item)
		}
	}
	return result
}

// Reduce collapses a slice into a single value using an accumulator.
func Reduce[T any, R any](slice []T, reducer func(R, T) R, initial R) R {
	result := initial
	for _, item := range slice {
		result = reducer(result, item)
	}
	return result
}
```

> **Takeaway**: `make([]R, len(slice))` pre-allocates the exact capacity for `Map`. `Filter` uses `append` because the output size is unknown. Pre-allocating with `make([]T, 0, len(slice))` reduces reallocations when the filter retains most elements.

---

### Example 2: Intermediate — Search and Validation

> **Goal**: Find elements and validate slice conditions with early termination.
> **Approach**: `Find` returns `(T, bool)` — the boolean replaces JavaScript's `undefined`. `Includes` requires the `comparable` constraint.
> **Complexity**: O(1) best case — both short-circuit on first match.

```go
// validation_logic.go
package utils

// Find returns the first element matching the predicate, plus a boolean.
func Find[T any](slice []T, predicate func(T) bool) (T, bool) {
	for _, item := range slice {
		if predicate(item) {
			return item, true
		}
	}
	
	var zero T
	return zero, false
}

// Includes checks if a value exists in the slice.
// Requires comparable constraint — maps and slices cannot use ==.
func Includes[T comparable](slice []T, target T) bool {
	for _, item := range slice {
		if item == target {
			return true
		}
	}
	return false
}
```

> **Takeaway**: Always check the boolean return from `Find`. The zero value of a struct is a valid value — `User{ID: 0}` is a real struct, not `nil`. Ignoring the boolean leads to processing phantom records.

---

### Example 3: Advanced — FlatMap and Chunk

> **Goal**: Flatten nested slices and split large collections into batches.
> **Approach**: `FlatMap` maps each element to a slice and concatenates. `Chunk` splits by fixed size.
> **Complexity**: O(N×M) for `FlatMap` expansion; O(N) for `Chunk`.

```go
// complex_restructuring.go
package utils

// FlatMap maps each element to a slice and flattens the results.
func FlatMap[T any, R any](slice []T, fn func(T) []R) []R {
	var result []R
	for _, item := range slice {
		result = append(result, fn(item)...)
	}
	return result
}

// Chunk splits a slice into batches of the given size.
func Chunk[T any](slice []T, size int) [][]T {
	if size <= 0 {
		return nil
	}
	
	result := make([][]T, 0, (len(slice)+size-1)/size)
	for i := 0; i < len(slice); i += size {
		end := i + size
		if end > len(slice) {
			end = len(slice)
		}
		
		result = append(result, slice[i:end])
	}
	return result
}
```

> **Takeaway**: `Chunk` sub-slices share the backing array with the original slice. Modifying elements in a chunk modifies the original. If you need isolation, copy each chunk with `slices.Clone`.

## 4. PITFALLS

| # | Defect | Fix |
| --- | --- | --- |
| 1 | Nesting `Reduce(Map(Filter(...)))` into one expression | Break into intermediate variables — readability matters more than one-liners |
| 2 | Ignoring the boolean return from `Find` | Always check `ok` — zero values are valid structs, not null |
| 3 | Using generic `Map` on hot paths with large structs | Replace with a manual `for` loop that pre-allocates and avoids copies |
| 4 | Modifying slice elements inside `Filter` | Slice elements are copies for value types. For mutation, use `[]*T` |

## 5. REF

| Resource | Link |
| --- | --- |
| `samber/lo` Utility Library | [github.com/samber/lo](https://github.com/samber/lo) |
| Standard `slices` Package | [pkg.go.dev/slices](https://pkg.go.dev/slices) |

## 6. RECOMMEND

| Extension | When | Rationale |
| --- | --- | --- |
| [Object Maps](./03-object-map-utils.md) | When working with dynamic key-value data | Generic `Keys`, `Merge`, `Pick` for `map[K]V` |
| [Optional Types](./11-optional-nullable.md) | When handling nullable or absent values | `Find` returns zero values — optionals make absence explicit |

**Navigation**: [← Data Conversion](./01-data-conversion.md) · [→ Object Maps](./03-object-map-utils.md)
