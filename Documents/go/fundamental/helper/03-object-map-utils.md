<!-- tags: golang, map, utils -->
# 🗂️ Object/Map Utils — Keys, Values, Entries, Merge

> JavaScript spreads objects with `{...a, ...b}`. Go has no spread operator — you loop through maps explicitly. Map iteration order is randomized by design. Concurrent map access without a mutex crashes with a fatal runtime error.

📅 Created: 2026-03-23 · 🔄 Updated: 2026-04-19 · ⏱️ 10 min read

## 1. DEFINE

A TypeScript developer ports a configuration merger: `{...defaultConfig, ...envConfig}`. They try `reflect` to merge structs dynamically. The code compiles, runs 10x slower than a manual loop, and panics when a new field is added without updating the reflection logic.

Go maps (`map[K]V`) replace JavaScript's dynamic objects. But maps have two critical differences: iteration order is deliberately randomized (no stable key order), and concurrent reads/writes cause a fatal runtime crash — not a data race, but an unrecoverable `fatal error: concurrent map writes`.

### 1.1 Invariants & Failure Modes

| Boundary | Core Responsibility |
| --- | --- |
| **`map[K]V`** | The dynamic equivalent of JS objects. Keys must be `comparable`; values can be any type. |
| **Random iteration** | Go randomizes `range` order to prevent code from depending on insertion order. |

| Rule | Rationale |
| --- | --- |
| **Never mutate maps in place** | `result[k] = v` mutates the original map. Create a new map for merges. |
| **Sort keys after extraction** | `Keys(m)` returns a random-order slice. Sort if you need deterministic output. |

### 1.2 Failure Cascades

- **The missing key sort:** You extract map keys and write them to a config file. Tests pass locally, fail in CI — because the key order changes between runs.
- **The struct reflection trap:** Using `reflect` to extract struct fields bypasses compile-time safety. Adding a field to the struct silently breaks the reflection code at runtime.

## 2. VISUAL

JavaScript objects and Go maps look similar but behave differently. The visual maps each JS `Object.*` method to its Go generic equivalent.

![Object Map Equivalents](./images/03-object-map-utils-api-map.png)

*Figure: JS `Object.keys/values/entries/assign` mapped to Go generic functions. Go requires explicit loops where JavaScript provides built-in methods.*

## 3. CODE

With the map invariants established, the code below builds six utilities: `Keys`, `Entries`, `Merge`, `Pick`, `Invert`, and `FilterMap`.

### Example 1: Basic — Keys and Entries

> **Goal**: Extract map keys and key-value pairs into typed slices.
> **Approach**: Pre-allocate the result slice with `make([]K, 0, len(m))` to avoid reallocations.
> **Complexity**: O(N) — one pass over the map.

```go
// basic_maps.go
package utils

// Entry represents a key-value pair, equivalent to JS [key, value] tuples.
type Entry[K comparable, V any] struct {
	Key   K
	Value V
}

// Keys returns all map keys as a slice. Order is non-deterministic.
func Keys[K comparable, V any](m map[K]V) []K {
	keys := make([]K, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	return keys
}

// Entries returns all key-value pairs as a slice of Entry structs.
func Entries[K comparable, V any](m map[K]V) []Entry[K, V] {
	entries := make([]Entry[K, V], 0, len(m))
	for k, v := range m {
		entries = append(entries, Entry[K, V]{Key: k, Value: v})
	}
	return entries
}
```

> **Takeaway**: Pre-allocating with `cap = len(m)` avoids slice growth during the loop. Always sort the result if you need deterministic order — `slices.Sort(Keys(m))`.

---

### Example 2: Intermediate — Merge and Pick

> **Goal**: Merge multiple maps (like `Object.assign`) and extract a subset of keys (like Lodash `pick`).
> **Approach**: `Merge` creates a new map and copies entries — later maps overwrite earlier ones. `Pick` selects only the specified keys.
> **Complexity**: O(N+M) for merge; O(K) for pick where K = number of selected keys.

```go
// mutable_config.go
package utils

// Merge combines multiple maps into one. Later maps overwrite earlier entries.
func Merge[K comparable, V any](maps ...map[K]V) map[K]V {
	total := 0
	for _, m := range maps {
		total += len(m)
	}
	
	result := make(map[K]V, total)
	for _, m := range maps {
		for k, v := range m {
			// ✅ Last-write-wins: later maps take priority
			result[k] = v 
		}
	}
	return result
}

// Pick returns a new map containing only the specified keys.
func Pick[K comparable, V any](m map[K]V, keys ...K) map[K]V {
	result := make(map[K]V, len(keys))
	for _, k := range keys {
		if v, ok := m[k]; ok {
			result[k] = v
		}
	}
	return result
}
```

> **Takeaway**: `Merge` always returns a new map — the originals are not modified. This is the Go equivalent of `Object.assign({}, ...maps)` (note the empty object as the first argument).

---

### Example 3: Advanced — Invert and FilterMap

> **Goal**: Swap keys and values for reverse lookups, and filter maps by predicate.
> **Approach**: `Invert` requires both `K` and `V` to be `comparable`. `FilterMap` accepts a predicate over key-value pairs.
> **Complexity**: O(N) — one pass for each operation.

```go
// transform_maps.go
package utils

// Invert swaps keys and values. Duplicate values overwrite earlier entries.
func Invert[K comparable, V comparable](m map[K]V) map[V]K {
	result := make(map[V]K, len(m))
	for k, v := range m {
		// ⚠️ If two keys map to the same value, one entry is lost
		result[v] = k
	}
	return result
}

// FilterMap returns a new map containing only entries that match the predicate.
func FilterMap[K comparable, V any](m map[K]V, predicate func(K, V) bool) map[K]V {
	result := make(map[K]V)
	for k, v := range m {
		if predicate(k, v) {
			result[k] = v
		}
	}
	return result
}
```

> **Takeaway**: `Invert` is lossy when values are not unique. Check uniqueness first, or use `map[V][]K` to preserve all original keys.

## 4. PITFALLS

| # | Defect | Fix |
| --- | --- | --- |
| 1 | Concurrent map reads and writes | Use `sync.RWMutex` or `sync.Map`. Concurrent writes cause `fatal error: concurrent map writes` — unrecoverable. |
| 2 | Expecting deterministic iteration order | Go randomizes `range` order by design. Sort keys after extraction if order matters. |
| 3 | Mutating a map passed as a function argument | Maps are reference types. Mutations inside a function affect the caller. Clone first if you need isolation. |

## 5. REF

| Resource | Link |
| --- | --- |
| `maps` Package (Go 1.21+) | [pkg.go.dev/maps](https://pkg.go.dev/maps) |
| Go Generics Tutorial | [go.dev/doc/tutorial/generics](https://go.dev/doc/tutorial/generics) |

## 6. RECOMMEND

| Extension | When | Rationale |
| --- | --- | --- |
| [Concurrent Maps](./09-set-concurrent-map.md) | When multiple goroutines access the same map | `sync.Map` and mutex-guarded patterns |
| [Array Pipelines](./02-array-pipeline.md) | When processing slices extracted from maps | Generic `Map`, `Filter`, `Reduce` over typed slices |

**Navigation**: [← Array Pipeline](./02-array-pipeline.md) · [→ Promise & Async](./04-promise-async.md)
