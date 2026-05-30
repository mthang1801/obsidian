<!-- tags: golang, memory, pointers -->
# ❓ Optional & Nullable — TS `T?` / `undefined` → Go Pointers & zero values

> TypeScript distinguishes `undefined` (not set) from `null` (explicitly empty) and provides optional chaining (`?.`). Go has no `undefined` — unset variables get zero values (`""`, `0`, `false`, `nil`). You distinguish "not set" from "set to zero" using pointers.

📅 Created: 2026-03-23 · 🔄 Updated: 2026-04-19 · ⏱️ 12 min read

> [!TIP]
> Go 1.26 adds `new(expr)` for creating pointers to literal values, replacing verbose `Ptr()` helper functions.

## 1. DEFINE

Your API accepts `PATCH` requests with partial JSON: `{"age": 0}`. The struct field `Age int` gets zero-value `0` — but was it explicitly set to 0, or was it absent from the request? With `int`, you cannot tell. Both "not sent" and "sent as 0" produce the same value.

The fix: use `*int`. When the JSON field is absent, the pointer is `nil`. When the field is present with value 0, the pointer points to `0`. The pointer distinguishes absence from zero.

This pattern applies to all PATCH endpoints, optional config fields, and nullable database columns: use pointers when "not set" and "zero" mean different things.

### 1.1 Invariants & Failure Modes

| Boundary | Core Responsibility |
| --- | --- |
| **Pointers `*T`** | `nil` means "not set." Non-nil means "set to this value." Zero values no longer collide with absence. |
| **Nil dereference** | Accessing `*ptr` when `ptr == nil` panics. Always check `ptr != nil` before dereferencing. |

| Rule | Rationale |
| --- | --- |
| **Always nil-check pointers** | `*ptr` on a nil pointer is a fatal panic — not a recoverable error. |
| **Use `sql.NullString` for DB columns** | Database drivers use `NullString`/`NullInt64` instead of pointers for nullable columns. |

### 1.2 Failure Cascades

- **The zero-value erasure:** A PATCH request sends `{"priority": 0}`. The handler uses `Priority int`, sees `0`, and skips the update ("zero means unchanged"). The user's explicit 0 is silently ignored.
- **The chaining panic:** You port `user?.address?.city` to Go as `user.Address.City`. If `Address` is nil, the access panics. Go has no optional chaining — you must check each pointer.

## 2. VISUAL

The decision between `T`, `*T`, and `Optional[T]` depends on whether zero is a valid value.

![Optional Strategy Map](./images/11-optional-nullable-decision-map.png)

*Figure: Decision tree for optional values. Use `T` when zero is never valid. Use `*T` when zero and "not set" need different handling. Use `Optional[T]` when you want functional chaining.*

## 3. CODE

With the pointer-vs-value decision clarified, the code below demonstrates three patterns: basic pointer handling, partial struct patches, and a generic `Optional[T]` type.

### Example 1: Basic — Pointer defaults and nil checks

> **Goal**: Implement the Go equivalent of TypeScript's `customer?.name ?? "Anonymous"`.
> **Approach**: Check `ptr != nil` before dereferencing. Use `OrDefault` for fallback values.
> **Complexity**: O(1) per check.

```go
// basic_pointers.go
package pointers

import "fmt"

type Customer struct {
	Name string
}

// TS: function connect(customer?: Customer)
func ConnectSession(customer *Customer) string {
	// TS: customer?.name ?? "Anonymous"
	if customer == nil {
		return "Anonymous"
	}
	return "Connected: " + customer.Name
}

func OrDefault[T any](ptr *T, fallback T) T {
	if ptr != nil {
		return *ptr
	}
	return fallback
}

func ExecuteDefaults() {
	var inputPointer *string
	fmt.Println("Empty:", OrDefault(inputPointer, "Offline"))
	
	// Go 1.26: new(expr) creates a pointer to a literal
	inputPointer = new("Active")
	fmt.Println("Active:", OrDefault(inputPointer, "Offline"))
}
```

> **Takeaway**: Go has no `??` operator. `OrDefault` is the generic equivalent. For pre-1.26 Go, use a `Ptr[T](v T) *T` helper to create pointers to literals — `Ptr("Active")` instead of declaring a variable and taking its address.

---

### Example 2: Intermediate — Partial struct patching

> **Goal**: Deserialize a PATCH JSON body where absent fields should not overwrite existing values.
> **Approach**: Use `*string` and `*int` in the patch struct. `nil` means "not sent." Non-nil means "update to this value."
> **Complexity**: O(1) per field.

```go
// partial_structs.go
package pointers

import "encoding/json"

type Schema struct {
	Category string `json:"category"`
	Priority int    `json:"priority"`
}

// Partial<Schema> equivalent: pointer fields distinguish absence from zero
type PatchPayload struct {
	Category *string `json:"category,omitempty"`
	Priority *int    `json:"priority,omitempty"`
}

func (s *Schema) ApplyPatch(payload PatchPayload) {
	if payload.Category != nil {
		s.Category = *payload.Category
	}
	if payload.Priority != nil {
		s.Priority = *payload.Priority
	}
}

func DeserializePatch(data []byte) (*Schema, error) {
	var payload PatchPayload
	if err := json.Unmarshal(data, &payload); err != nil {
		return nil, err
	}
	
	base := Schema{Category: "General", Priority: 5}
	base.ApplyPatch(payload)
	
	return &base, nil
}
```

> **Takeaway**: `json:"priority,omitempty"` with `*int` means: if `priority` is absent in JSON → `nil`. If `priority` is `0` in JSON → `*int` pointing to `0`. The pointer preserves the caller's intent.

---

### Example 3: Advanced — Generic Optional type

> **Goal**: Build a functional `Optional[T]` that prevents nil dereference panics through a safe API.
> **Approach**: Wrap the value and a `present` boolean. `UnwrapOr` provides a fallback. `Map` transforms the value if present.
> **Complexity**: O(1) per operation.

```go
// functional_optionals.go
package pointers

type Optional[T any] struct {
	element T
	present bool
}

func Some[T any](value T) Optional[T] {
	return Optional[T]{element: value, present: true}
}

func None[T any]() Optional[T] {
	return Optional[T]{present: false}
}

func (o Optional[T]) UnwrapOr(fallback T) T {
	if o.present {
		return o.element
	}
	return fallback
}

func (o Optional[T]) Map(transform func(T) T) Optional[T] {
	if o.present {
		return Some(transform(o.element))
	}
	return None[T]()
}
```

> **Takeaway**: `Optional[T]` is safer than `*T` — no nil dereference panics. But it fights Go idioms: most Go code uses `(T, bool)` returns (like `map` lookup) or `(T, error)`. Use `Optional[T]` in pipeline-heavy code where chaining `.Map().Map().UnwrapOr()` reads better.

## 4. PITFALLS

| # | Defect | Fix |
| --- | --- | --- |
| 1 | Dereferencing a pointer without nil check | Always check `if ptr != nil` before `*ptr`. Nil dereference is a fatal panic. |
| 2 | Using `int` for optional JSON fields | Use `*int` — both absent and `0` deserialize as `int(0)`, making them indistinguishable. |
| 3 | Omitting `omitempty` on pointer fields | Without `omitempty`, nil pointers serialize as `null` in JSON. Add `omitempty` to skip them. |

## 5. REF

| Resource | Link |
| --- | --- |
| Zero values specification | [go.dev/ref/spec#The_zero_value](https://go.dev/ref/spec#The_zero_value) |
| JSON and Go blog | [go.dev/blog/json](https://go.dev/blog/json) |

## 6. RECOMMEND

| Extension | When | Rationale |
| --- | --- | --- |
| [Data Conversion](./01-data-conversion.md) | When deserializing complex payloads | Pointer fields combine with streaming JSON decoding |
| [Iterator Patterns](./10-iterator.md) | When iterators produce nullable values | `Optional[T]` integrates with `iter.Seq[Optional[T]]` for safe lazy pipelines |

**Navigation**: [← Iterator Patterns](./10-iterator.md) · [→ Class → Struct](./12-class-struct.md)
