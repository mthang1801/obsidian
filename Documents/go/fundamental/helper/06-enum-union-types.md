<!-- tags: golang, typing, enums -->
# 🏷️ Enum & Union Types — TS → Go Patterns

> TypeScript has `enum` keywords and discriminated unions (`type Shape = Circle | Square`). Go has neither. You simulate enums with `const` + `iota`, and union types with sealed interfaces containing unexported methods.

📅 Created: 2026-03-23 · 🔄 Updated: 2026-04-19 · ⏱️ 14 min read

## 1. DEFINE

A frontend engineer defines API states with `type Status = "ACTIVE" | "INACTIVE"`. TypeScript rejects `Status = "UNKNOWN"` at compile time. The engineer ports this to Go as `type Status string` — but Go lets anyone write `Status("UNKNOWN")` and the compiler accepts it silently. The invalid status reaches the database, corrupting records.

Go provides no literal types, no `enum` keyword, and no exhaustive `switch` checks. You get two tools:

1. **`const` + `iota`** for numeric enums with auto-incrementing values.
2. **Sealed interfaces** for union types — an unexported method prevents external packages from adding new variants.

Both require explicit validation: Go will not catch missing `switch` cases at compile time.

### 1.1 Invariants & Failure Modes

| Boundary | Core Responsibility |
| --- | --- |
| **`iota` groups** | Auto-incrementing constants within a `const` block. Resets to 0 in each new block. |
| **Sealed interfaces** | An interface with an unexported method (`sealed()`) restricts implementations to the current package. |

| Rule | Rationale |
| --- | --- |
| **Skip zero with `_`** | `iota` starts at 0. If zero is a valid default, accidental zero-values create phantom matches. Skip it. |
| **Add `.IsValid()` methods** | String constants have no exhaustive checks. Attach a validation method to reject unknown values. |

### 1.2 Failure Cascades

- **The resetting iota:** You split a `const` block into two blocks thinking `iota` continues counting. It resets to 0 in the second block — two different constants get the same numeric value, causing silent collisions.
- **The broken assertion:** You write `s.(Circle)` without the comma-ok idiom. If `s` is not a `Circle`, Go panics. Use `v, ok := s.(Circle)` or a `switch s.(type)` block.

## 2. VISUAL

TypeScript enums and union types map to Go's `const`/`iota` blocks and sealed interfaces. The visual shows the translation.

![Enum Typologies Compare](./images/06-enum-union-types-compare.png)

*Figure: TS enums become `const` blocks with `iota`. TS discriminated unions become sealed interfaces with type switches. Neither provides compile-time exhaustiveness in Go.*

## 3. CODE

With the constraints established, the code below demonstrates three patterns: numeric and string enums, sealed union interfaces, and a generic `Result[T]` type.

### Example 1: Basic — Numeric constants and string enums

> **Goal**: Define bounded status values that reject invalid inputs at runtime.
> **Approach**: Use `const` + `iota` for numeric priorities, `const` with explicit string values for statuses. Add `.IsValid()` for runtime validation.
> **Complexity**: O(1) per validation check.

```go
// core_enums.go
package helper

import "fmt"

type Priority int

const (
	// Skip zero to avoid accidental default matches
	_ Priority = iota 
	PriorityLow
	PriorityHigh
)

type Status string

const (
	StatusActive   Status = "ACTIVE"
	StatusInactive Status = "INACTIVE"
)

func (s Status) IsValid() bool {
	switch s {
	case StatusActive, StatusInactive:
		return true
	}
	return false
}

func ExecuteStatusGuard(input Status) {
	if !input.IsValid() {
		fmt.Println("Blocked invalid state")
		return
	}
	fmt.Println("Processing valid state")
}
```

> **Takeaway**: `Status("UNKNOWN")` compiles — Go does not restrict named type casting. The `.IsValid()` method is the only defense. Call it at the boundary (HTTP handler, message consumer) before passing values into business logic.

---

### Example 2: Intermediate — Sealed union interfaces

> **Goal**: Simulate TypeScript's `type Command = StartCommand | StopCommand` with compile-time variant control.
> **Approach**: Define an interface with an unexported `sealed()` method. Only structs in the same package can implement it.
> **Complexity**: O(1) per type switch.

```go
// sealed_unions.go
package helper

import "fmt"

// TS: type Command = StartCommand | StopCommand
type Command interface {
	Execute() error
	// ✅ Unexported method prevents external packages from adding variants
	sealed() 
}

type StartCommand struct{ TargetID string }
func (s StartCommand) Execute() error { return nil }
func (StartCommand) sealed()          {}

type StopCommand struct{ Graceful bool }
func (s StopCommand) Execute() error { return nil }
func (StopCommand) sealed()          {}

func ProcessCommand(c Command) string {
	// TS: switch (c.kind) 
	switch v := c.(type) {
	case StartCommand:
		return fmt.Sprintf("Starting %s", v.TargetID)
	case StopCommand:
		return fmt.Sprintf("Stopping: graceful=%v", v.Graceful)
	default:
		return "Unknown command"
	}
}
```

> **Takeaway**: The `sealed()` method is unexported — external packages cannot add new `Command` variants. This gives you package-level control over the union. Always include a `default` case in the type switch to catch impossible states during refactoring.

---

### Example 3: Advanced — Generic Result type

> **Goal**: Build a `Result[T]` container that forces callers to check success before accessing the value, similar to Rust's `Result<T, E>`.
> **Approach**: Generic struct with `ok` boolean, `value`, and `err` fields. `Unwrap()` returns `(T, error)`.
> **Complexity**: O(1) per unwrap.

```go
// generic_results.go
package helper

import "fmt"

// TS: type Result<T> = { ok: true, value: T } | { ok: false, error: Error }
type Result[T any] struct {
	value T
	err   error
	ok    bool
}

func Ok[T any](value T) Result[T] {
	return Result[T]{value: value, ok: true}
}

func Err[T any](err error) Result[T] {
	return Result[T]{err: err, ok: false}
}

func (r Result[T]) Unwrap() (T, error) {
	if r.ok {
		return r.value, nil
	}
	return r.value, r.err
}

func DemonstrateFunctionalReturn() {
	result := Ok("Valid Config")
	
	val, err := result.Unwrap()
	if err != nil {
		fmt.Println("Failed:", err)
		return
	}
	fmt.Println("Processed:", val)
}
```

> **Takeaway**: In most Go code, `(T, error)` return values are idiomatic enough. `Result[T]` is useful in pipeline scenarios where you want to chain operations without checking errors at every step — but it fights Go conventions. Use judiciously.

## 4. PITFALLS

| # | Defect | Fix |
| --- | --- | --- |
| 1 | Splitting `const` blocks and expecting `iota` to continue | Keep all values in a single `const` block. `iota` resets in each new block. |
| 2 | Using zero as a valid enum value | Skip zero with `_ = iota` so uninitialized variables do not accidentally match a valid state. |
| 3 | Missing `default` in type switches | Always add a `default` case. It catches new variants added during refactoring. |

## 5. REF

| Resource | Link |
| --- | --- |
| Iota Specification | [go.dev/ref/spec#Iota](https://go.dev/ref/spec#Iota) |
| `stringer` Tool | [pkg.go.dev/golang.org/x/tools/cmd/stringer](https://pkg.go.dev/golang.org/x/tools/cmd/stringer) |

## 6. RECOMMEND

| Extension | When | Rationale |
| --- | --- | --- |
| [Data Conversion](./01-data-conversion.md) | When parsing enum values from incoming payloads | Validate string-to-enum conversion at the boundary |
| [Error Handling](./07-error-handling.md) | When validation failures need structured error responses | Combine enum validation with sentinel errors |

**Navigation**: [← Date/Time](./05-date-time.md) · [→ Error Handling](./07-error-handling.md)
