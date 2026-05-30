<!-- tags: golang, overview, migration -->
# 🧰 Helper Utilities — TS/JS to Go Migration

> Recipe-level mapping from TypeScript/JavaScript utilities to idiomatic Go equivalents: data conversion, array pipelines, object manipulation, async patterns, and date/time handling.

📅 Updated: 2026-04-19 · ⏱️ 6 min read

## 1. DEFINE

A senior Node.js developer ports `Array.filter().map().reduce()` into Go by importing a generic utility library. The result: type assertion overhead everywhere, GC pressure from boxing/unboxing, and a codebase that reads like neither TypeScript nor Go.

This hub maps specific JavaScript/TypeScript utility patterns to their idiomatic Go equivalents. It is a recipe reference — not a theory doc.

### 1.1 Invariants & Failure Modes

| Target Domain | Migration Approach |
| --- | --- |
| **Collections** | Replace `Array.filter/map/reduce` with explicit `for range` loops or Go 1.23+ iterators |
| **Concurrency** | Replace `Promise.all` with `errgroup.Group` |
| **Objects** | Replace `Object.keys/assign` with struct fields or map iteration |

| Rule | Rationale |
| --- | --- |
| **No `lodash` equivalents** | Idiomatic Go avoids generic utility libraries. Build specific loops for specific problems. |
| **Explicit pointer semantics** | JavaScript passes objects by reference implicitly. Go passes by value — use pointers only when mutation is intended. |

### 1.2 Failure Cascades

- **The Missing Map:** Simulating `Array.map` with `interface{}` slices forces type assertions at every step. The runtime GC pays the cost.
- **The Promise Panic:** Porting `async/await` with bare goroutines and no synchronization causes channel deadlocks and memory leaks.

## 2. VISUAL

![TS to Go Migration Map](./images/helper-router-map.png)

*Figure: Translation map routing JavaScript/TypeScript utilities to their Go equivalents.*

## 3. CODE

### Example 1: Basic — Router Artifact Selection

> **Goal**: Navigate to the correct migration recipe by problem domain.
> **Approach**: Map the TS/JS pattern to the correct helper article.
> **Complexity**: O(1) navigation.

```go
// router_bridge.go
package helper

// ResolveMigrationPath routes a TS/JS pattern to the correct Go migration article.
func ResolveMigrationPath(domain string) string {
	switch domain {
	case "data_conversion":
		return "./01-data-conversion.md"
	case "array_pipeline":
		return "./02-array-pipeline.md"
	case "promise_async":
		// Directs async patterns to errgroup-based equivalents.
		return "./04-promise-async.md"
	case "date_time":
		return "./05-date-time.md"
	default:
		return "./README.md"
	}
}
```

> **Takeaway**: Translate paradigms structurally. Porting TS syntax 1:1 into Go produces hybrid code that is neither idiomatic nor maintainable.

## 4. PITFALLS

| # | Defect | Fix |
| --- | --- | --- |
| 1 | Porting `Promise.all` with bare goroutines | Use `sync.WaitGroup` or `errgroup.Group` for structured concurrency |
| 2 | Simulating `Object.assign` with `interface{}` maps | Use explicit struct initialization with named fields |
| 3 | Emulating `Array.reduce` with generic utility libraries | Write an explicit `for range` loop with a typed accumulator |

## 5. REF

| Resource | Link |
| --- | --- |
| Go Standard Library | [pkg.go.dev/std](https://pkg.go.dev/std) |
| Effective Go | [go.dev/doc/effective_go](https://go.dev/doc/effective_go) |

## 6. RECOMMEND

| Extension | When | Rationale |
| --- | --- | --- |
| [Data Conversion](./01-data-conversion.md) | Type parsing, hex/base64 encoding | Maps `parseInt`, `Buffer.from`, `JSON.parse` to Go equivalents |
| [Array Pipeline](./02-array-pipeline.md) | Collection transformation | Converts `map/filter/reduce` to `for range` loops and iterators |
| [Promise & Async](./04-promise-async.md) | Async I/O patterns | Maps `Promise.all`, `async/await` to `errgroup`, channels, context |

**Navigation**: [← Fundamental Hub](../README.md) · [→ Data Conversion](./01-data-conversion.md)
