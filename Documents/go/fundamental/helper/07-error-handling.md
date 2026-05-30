<!-- tags: golang, error-handling -->
# ⚠️ Error Handling — TS try/catch → Go error patterns

> TypeScript wraps entire call stacks in one `try/catch`. Go returns errors as values — every function call gets its own `if err != nil` check. This is verbose by design: errors are handled at the exact point they occur, not at some distant catch block.

📅 Created: 2026-03-23 · 🔄 Updated: 2026-04-19 · ⏱️ 16 min read

## 1. DEFINE

A frontend engineer replaces `throw new Error("invalid")` with `panic("invalid")` and wraps the caller in `defer/recover`. The code works in tests. In production, the panic kills the entire goroutine stack — including unrelated concurrent work sharing that goroutine.

Go treats errors as **values**, not exceptions. Functions return `(T, error)` tuples. The caller checks `err != nil` immediately — no stack unwinding, no distant catch blocks. `panic` is reserved for unrecoverable bugs (nil pointer, impossible state) that should crash the program. Routine failures (file not found, invalid input, network timeout) return errors.

### 1.1 Invariants & Failure Modes

| Boundary | Core Responsibility |
| --- | --- |
| **`(T, error)` returns** | Every fallible function returns an error. The caller checks `err != nil` before using `T`. |
| **`errors.Is` / `errors.As`** | `Is` matches sentinel values through wrapped chains. `As` extracts typed errors for field access. |

| Rule | Rationale |
| --- | --- |
| **Never use `panic` for control flow** | `panic` unwinds the entire goroutine stack. Use it only for programmer bugs, not runtime errors. |
| **Wrap with `%w`, not `%v`** | `fmt.Errorf("context: %w", err)` preserves the error chain. `%v` converts to a string — `errors.Is` stops working. |

### 1.2 Failure Cascades

- **The lost chain:** You wrap an error with `fmt.Errorf("failed: %v", err)`. The `%v` verb formats the error as a string and discards the original. Downstream `errors.Is(err, ErrNotFound)` returns `false` because the chain is broken.
- **The ignored tuple:** You write `result, _ := Execute()`. If `Execute` returns an error, `result` is a zero value. You insert an empty record into the database without noticing.

## 2. VISUAL

JavaScript catches errors at a distance. Go catches them at the source. The visual compares both flows.

![Error Flow Mapping](./images/07-error-handling-compare.png)

*Figure: JS `try/catch` wraps multiple calls. Go checks `err != nil` after each call. The Go pattern is verbose but pinpoints exactly which operation failed.*

## 3. CODE

With the error philosophy established, the code below demonstrates three patterns: wrapping sentinel errors, custom domain error types, and multi-error aggregation with `errors.Join`.

### Example 1: Basic — Wrapping sentinel errors

> **Goal**: Return domain-specific errors that callers can match with `errors.Is`.
> **Approach**: Define sentinels with `errors.New`. Wrap with `fmt.Errorf("context: %w", err)` to add context while preserving the chain.
> **Complexity**: O(1) per wrap/check.

```go
// sentinel_wrapping.go
package errors

import (
	"errors"
	"fmt"
)

var (
	ErrNotFound   = errors.New("record missing")
	ErrValidation = errors.New("invalid payload")
)

func QueryDatabase(id int) (string, error) {
	if id <= 0 {
		// ✅ %w preserves the sentinel — errors.Is(err, ErrValidation) works
		return "", fmt.Errorf("query validation failure id=%d: %w", id, ErrValidation)
	}
	return "Record_Hash", nil
}

func ExecuteLookup() {
	_, err := QueryDatabase(-5)
	
	if err != nil {
		// TS: if (err instanceof ValidationError)
		if errors.Is(err, ErrValidation) {
			fmt.Println("Blocked invalid query")
			return
		}
		fmt.Println("Unhandled error:", err)
	}
}
```

> **Takeaway**: `%w` is the only format verb that preserves the error chain. Replace every `%v` in error wrapping with `%w`.

---

### Example 2: Intermediate — Custom domain error types

> **Goal**: Attach structured metadata (HTTP status code, domain message) to errors for API responses.
> **Approach**: Implement `error` and `Unwrap()` interfaces on a struct. Use `errors.As` to extract fields.
> **Complexity**: O(1) per type assertion.

```go
// custom_domains.go
package errors

import (
	"errors"
	"fmt"
)

type DomainError struct {
	Code    int  
	Message string
	Err     error
}

func (e *DomainError) Error() string {
	if e.Err != nil {
		return fmt.Sprintf("[%d] %s: %v", e.Code, e.Message, e.Err)
	}
	return fmt.Sprintf("[%d] %s", e.Code, e.Message)
}

func (e *DomainError) Unwrap() error {
	return e.Err
}

func ExtractDomain(err error) {
	var target *DomainError
	
	// TS: if (e instanceof DomainError)
	if errors.As(err, &target) {
		fmt.Printf("API Code: %d\n", target.Code)
		return
	}
}
```

> **Takeaway**: `errors.As` walks the error chain and extracts the first match. `Unwrap()` enables this traversal. Without `Unwrap`, wrapped errors are opaque to `errors.As`.

---

### Example 3: Advanced — Multi-error aggregation

> **Goal**: Collect all validation failures instead of stopping at the first one, like a form validator.
> **Approach**: Accumulate errors in a slice and combine with `errors.Join` (Go 1.20+). Each individual error is still matchable with `errors.Is`.
> **Complexity**: O(N) — one error per validation rule.

```go
// aggregate_joins.go
package errors

import (
	"errors"
	"fmt"
)

func ValidateFields(name string, age int) error {
	var aggregated []error

	if name == "" {
		aggregated = append(aggregated, errors.New("name is required"))
	}
	
	if age < 0 || age > 150 {
		aggregated = append(aggregated, fmt.Errorf("invalid age: %d", age))
	}

	if len(aggregated) > 0 {
		// ✅ Join combines multiple errors into one; errors.Is checks each
		return errors.Join(aggregated...)
	}
	return nil
}

func VerifyAggregates() {
	err := ValidateFields("", -5)
	if err != nil {
		fmt.Println("Validation errors:", err)
	}
}
```

> **Takeaway**: `errors.Join` preserves each error individually — `errors.Is(joined, ErrSpecific)` works if any sub-error matches. This is the Go equivalent of collecting validation errors in an array.

## 4. PITFALLS

| # | Defect | Fix |
| --- | --- | --- |
| 1 | Passing wrong pointer type to `errors.As` | Pass `&target` where `target` is a `*DomainError`. Double pointer is required. |
| 2 | Using `recover` for routine error handling | `recover` is for panics only. Use `if err != nil` for normal errors. |
| 3 | Returning raw errors without context | Wrap with `fmt.Errorf("functionName: %w", err)` to add call-site context. |

## 5. REF

| Resource | Link |
| --- | --- |
| `errors` package | [pkg.go.dev/errors](https://pkg.go.dev/errors) |
| Effective Go: Errors | [go.dev/doc/effective_go#errors](https://go.dev/doc/effective_go#errors) |

## 6. RECOMMEND

| Extension | When | Rationale |
| --- | --- | --- |
| [Custom Error Wrappers](../errors/01-wrapping-custom.md) | When building multi-layer microservice error hierarchies | Domain-specific error types with HTTP codes and metadata |
| [Defer/Panic/Recover](../basics/03-defer-panic-recover.md) | When handling truly unrecoverable states | `defer`/`recover` patterns for panic-safe goroutines |

**Navigation**: [← Enum Types](./06-enum-union-types.md) · [→ Regex & Templates](./08-regex-templates.md)
