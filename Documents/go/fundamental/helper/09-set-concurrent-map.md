<!-- tags: golang, map, concurrency, data-structures -->
# 🗃️ Set & Concurrent Map — TS Set/Map/WeakMap → Go

> JavaScript has built-in `Set<T>` and `Map<K,V>`. Go has neither — you build sets with `map[T]struct{}` and concurrent maps with `sync.RWMutex` wrappers. Concurrent map access without a mutex causes a fatal, unrecoverable crash.

📅 Created: 2026-03-23 · 🔄 Updated: 2026-04-19 · ⏱️ 12 min read

## 1. DEFINE

Five goroutines insert user IDs into a shared `map[string]bool` simultaneously. The Go runtime detects the concurrent writes and crashes with `fatal error: concurrent map writes` — no recovery, no graceful shutdown. The process is killed.

Go maps are not thread-safe. Unlike JavaScript (which runs on a single thread), Go routinely accesses maps from multiple goroutines. Two options exist:

1. **`sync.RWMutex`** — wrap a regular map with read/write locks. Full type safety with generics.
2. **`sync.Map`** — built-in concurrent map, but uses `any` for keys and values (no generics, requires type assertions).

For sets, Go has no `Set` type. Use `map[T]struct{}` — the empty struct occupies zero bytes, making it the most memory-efficient set representation.

### 1.1 Invariants & Failure Modes

| Boundary | Core Responsibility |
| --- | --- |
| **Zero-allocation sets** | `map[T]struct{}` uses zero bytes per value. `map[T]bool` wastes 1 byte per entry. |
| **Thread-safe access** | Unprotected map access from multiple goroutines is a fatal crash, not a data race. |

| Rule | Rationale |
| --- | --- |
| **Never share raw maps across goroutines** | Even concurrent reads with one write crash the process. Use mutex wrappers or `sync.Map`. |
| **Prefer generic wrappers over `sync.Map`** | `sync.Map` stores `any` — every access needs a type assertion. Generic mutex wrappers preserve type safety. |

### 1.2 Failure Cascades

- **The boolean memory tax:** `map[string]bool` with 1 million entries wastes 1 MB on boolean values. `map[string]struct{}` uses exactly zero bytes for values — only keys consume memory.
- **The untyped `sync.Map` trap:** `sync.Map.Load` returns `any`. Forgetting the type assertion silently passes the wrong type downstream, causing panics far from the source.

## 2. VISUAL

JavaScript Sets and Go map-based sets differ in API surface and thread safety. The visual maps the translation.

![Set Concurrent Map Model](./images/09-set-concurrent-map-compare.png)

*Figure: JS `Set` methods mapped to Go `map[T]struct{}` operations. Go requires explicit mutex wrappers for concurrent access.*

## 3. CODE

With the concurrency constraints established, the code below builds three patterns: a generic set, a mutex-protected map, and `sync.Map` usage.

### Example 1: Basic — Generic Set implementation

> **Goal**: Build a type-safe `Set[T]` with `Add`, `Has`, `Delete`, and `Intersection` using zero-allocation values.
> **Approach**: Define `Set[T comparable]` as a type alias for `map[T]struct{}`.
> **Complexity**: O(1) per add/has/delete; O(min(N,M)) for intersection.

```go
// generic_sets.go
package collections

type Set[T comparable] map[T]struct{}

func NewSet[T comparable](items ...T) Set[T] {
	target := make(Set[T], len(items))
	for _, element := range items {
		target[element] = struct{}{} // zero bytes per entry
	}
	return target
}

func (s Set[T]) Add(item T)       { s[item] = struct{}{} }
func (s Set[T]) Has(item T) bool  { _, exists := s[item]; return exists }
func (s Set[T]) Delete(item T)    { delete(s, item) }

func (s Set[T]) Intersection(other Set[T]) Set[T] {
	result := NewSet[T]()
	for element := range s {
		if other.Has(element) {
			result.Add(element)
		}
	}
	return result
}
```

> **Takeaway**: `struct{}` is the idiomatic Go "I only care about the key" value. It occupies zero bytes — `unsafe.Sizeof(struct{}{})` returns 0.

---

### Example 2: Intermediate — Mutex-protected generic map

> **Goal**: Build a concurrent map with full type safety using generics and `sync.RWMutex`.
> **Approach**: `RLock` for reads (multiple concurrent readers allowed), `Lock` for writes (exclusive).
> **Complexity**: O(1) per operation; lock contention scales with goroutine count.

```go
// secure_maps.go
package collections

import "sync"

type SafeMap[K comparable, V any] struct {
	mu    sync.RWMutex
	store map[K]V
}

func NewSafeMap[K comparable, V any]() *SafeMap[K, V] {
	return &SafeMap[K, V]{store: make(map[K]V)}
}

func (sm *SafeMap[K, V]) Set(key K, value V) {
	sm.mu.Lock()
	defer sm.mu.Unlock()
	sm.store[key] = value
}

func (sm *SafeMap[K, V]) Get(key K) (V, bool) {
	sm.mu.RLock()
	defer sm.mu.RUnlock()
	
	val, ok := sm.store[key]
	return val, ok
}
```

> **Takeaway**: `RWMutex` allows multiple concurrent readers — only writes are exclusive. This matters for read-heavy workloads (config caches, session stores). For write-heavy workloads, the mutex becomes a bottleneck.

---

### Example 3: Advanced — Built-in sync.Map

> **Goal**: Use Go's built-in concurrent map for read-heavy, write-rare scenarios.
> **Approach**: `sync.Map` is optimized for two patterns: (1) keys written once and read many times, (2) disjoint key sets across goroutines. It uses `any` for both keys and values.
> **Complexity**: O(1) amortized per operation.

```go
// standard_sync_map.go
package collections

import (
	"fmt"
	"sync"
)

func ExecuteSyncMap() {
	var sharedMap sync.Map

	// Store accepts any key and any value — no type safety
	sharedMap.Store("TargetHost", "127.0.0.1")
	sharedMap.Store("ActivePort", 443)

	payload, exists := sharedMap.Load("TargetHost")
	fmt.Printf("Value: %v (Found: %v)\n", payload, exists)

	// LoadOrStore returns existing value if key exists, stores otherwise
	current, loaded := sharedMap.LoadOrStore("TargetHost", "192.168.1.1")
	fmt.Printf("Value: %v (Was cached: %v)\n", current, loaded)
}
```

> **Takeaway**: `sync.Map` is slower than a mutex-wrapped map for general use. It shines in two specific patterns: stable keys (read-heavy) and disjoint keys (no contention). For everything else, use the generic `SafeMap` from Example 2.

## 4. PITFALLS

| # | Defect | Fix |
| --- | --- | --- |
| 1 | Sharing raw `map` across goroutines | Wrap with `sync.RWMutex` or use `sync.Map`. Concurrent writes are fatal — not a data race, a crash. |
| 2 | Using `sync.Map` for type-safe code | `sync.Map` stores `any`. Use a generic mutex-wrapped map for type safety. |
| 3 | Using `map[T]bool` for sets | Use `map[T]struct{}` — zero bytes per value instead of 1 byte per boolean. |

## 5. REF

| Resource | Link |
| --- | --- |
| `sync.Map` documentation | [pkg.go.dev/sync#Map](https://pkg.go.dev/sync#Map) |
| `sync.RWMutex` documentation | [pkg.go.dev/sync#RWMutex](https://pkg.go.dev/sync#RWMutex) |

## 6. RECOMMEND

| Extension | When | Rationale |
| --- | --- | --- |
| [Goroutines & Channels](../concurrency/01-goroutines-and-channels.md) | When designing concurrent data pipelines | Understanding goroutine lifecycle for safe map access |
| [Map Utilities](./03-object-map-utils.md) | When transforming map data (keys, merge, pick) | Generic utility functions for single-threaded map operations |

**Navigation**: [← Regex & Templates](./08-regex-templates.md) · [→ Iterator Patterns](./10-iterator.md)
