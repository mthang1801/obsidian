<!-- tags: golang, structs, design-patterns -->
# 🏗️ Class → Struct — TS OOP → Go Composition

> TypeScript uses `class` inheritance with `extends` and `super()`. Go has no classes, no inheritance, and no `super`. You build behavior through struct embedding (composition) and interface satisfaction (implicit implementation).

📅 Created: 2026-03-23 · 🔄 Updated: 2026-04-19 · ⏱️ 16 min read

## 1. DEFINE

An architect ports a NestJS controller hierarchy: `UserController extends BaseController`. They embed `BaseController` in a Go struct, expecting `super.handleRequest()` to dispatch polymorphically. It does not. Go embedding is syntactic sugar for field access — it copies the parent's methods but does not create an inheritance chain. The embedded struct's methods always refer to the embedded type, not the outer struct.

Go replaces inheritance with two mechanisms:

1. **Struct embedding** — promotes fields and methods from the inner struct. Useful for reusing implementation, but no polymorphic dispatch.
2. **Interfaces** — implicit satisfaction. Any struct with the right methods implements the interface, no `implements` keyword. This is Go's polymorphism.

### 1.1 Invariants & Failure Modes

| Boundary | Core Responsibility |
| --- | --- |
| **Composition over inheritance** | Embedding promotes field access. It does not override methods — the embedded type's receiver is always itself. |
| **Implicit interfaces** | A struct satisfies an interface by having all required methods. No declaration needed. |

| Rule | Rationale |
| --- | --- |
| **Use `NewXxx()` constructors** | Go has no constructor syntax. Convention: `NewCustomer(id, email)` returns a validated `*Customer`. |
| **Use functional options** | Large struct configs with many optional fields get unreadable. `WithTimeout(5s)` option functions scale cleanly. |

### 1.2 Failure Cascades

- **The shadowed method trap:** You embed `BaseLogger` and define your own `Log()` method. The outer method shadows the inner one — code calling `base.Log()` through the embedded field still runs the original, not your override. This is not polymorphism.
- **The value receiver mutation:** You attach methods to `func (c Customer)` (value receiver). Inside the method, `c.Email = "new"` modifies a copy. The caller's struct is unchanged. Use pointer receivers `func (c *Customer)` for mutations.

## 2. VISUAL

JavaScript class hierarchies and Go compositional structs solve the same problem differently.

![Class to Struct Comparison](./images/12-class-struct-compare.png)

*Figure: TS class inheritance (left) vs Go struct embedding + interface (right). Go promotes fields through embedding but dispatches methods statically — no virtual method table.*

## 3. CODE

With composition and interfaces established, the code below demonstrates three patterns: struct constructors with encapsulation, interface-based polymorphism, and functional options for configuration.

### Example 1: Basic — Structs, constructors, and receivers

> **Goal**: Replace a TypeScript `class Customer` with a Go struct, constructor function, and methods.
> **Approach**: Unexported fields (lowercase) enforce encapsulation. `NewCustomer` validates input. Pointer receivers enable mutation.
> **Complexity**: O(1) per construction.

```go
// core_entities.go
package domain

import "errors"

// Replaces: class Customer { private id: string; email: string }
type Customer struct {
	identifier string // unexported = private
	Email      string // exported = public
}

// Replaces: constructor(id: string, email: string)
func NewCustomer(id, email string) (*Customer, error) {
	if id == "" {
		return nil, errors.New("id is required")
	}
	return &Customer{
		identifier: id,
		Email:      email,
	}, nil
}

// Getter for the private field
func (c *Customer) ID() string {
	return c.identifier
}

// Pointer receiver: mutations affect the original struct
func (c *Customer) UpdateEmail(email string) {
	c.Email = email
}
```

> **Takeaway**: Go uses capitalization for access control — uppercase = exported (public), lowercase = unexported (private to the package). There is no `protected` — package boundaries are the only access scope.

---

### Example 2: Intermediate — Interface-based polymorphism

> **Goal**: Define a `Transmitter` interface that multiple structs satisfy, replacing `abstract class Transmitter`.
> **Approach**: The interface defines the contract. Structs implement it implicitly by having the right methods. Embedding reuses the `Protocol()` implementation.
> **Complexity**: O(1) per dispatch.

```go
// polymorphic_engines.go
package domain

import "fmt"

// TS: abstract class Transmitter { abstract dispatch(payload: Buffer): void }
type Transmitter interface {
	Dispatch(payload []byte) error
	Protocol() string
}

type BaseNetwork struct {
	targetURL string
}

func (b *BaseNetwork) Protocol() string {
	return "HTTPS"
}

// Embeds BaseNetwork — gets Protocol() for free
type SecureTransmitter struct {
	BaseNetwork
	Certificate string
}

func NewSecureTransmitter(url string, cert string) *SecureTransmitter {
	return &SecureTransmitter{
		BaseNetwork: BaseNetwork{targetURL: url},
		Certificate: cert,
	}
}

func (s *SecureTransmitter) Dispatch(payload []byte) error {
	fmt.Printf("Transmitting via %s: %s\n", s.Protocol(), s.targetURL)
	return nil
}
```

> **Takeaway**: `SecureTransmitter` satisfies `Transmitter` without declaring `implements`. It gets `Protocol()` from embedding and defines `Dispatch()` directly. This is composition — not inheritance.

---

### Example 3: Advanced — Functional options pattern

> **Goal**: Replace large constructor parameter lists with composable option functions.
> **Approach**: Define `type Option func(*Config)`. Each option modifies one field. The constructor applies all options in order.
> **Complexity**: O(N) where N = number of options applied.

```go
// functional_options.go
package domain

import "time"

type Application struct {
	endpoint string
	timeout  time.Duration
	debug    bool
}

type AppOption func(*Application)

func WithTimeout(d time.Duration) AppOption {
	return func(app *Application) {
		app.timeout = d
	}
}

func WithDebugMode() AppOption {
	return func(app *Application) {
		app.debug = true
	}
}

func NewApplication(endpoint string, opts ...AppOption) *Application {
	// Sensible defaults
	app := &Application{
		endpoint: endpoint,
		timeout:  30 * time.Second,
		debug:    false,
	}

	for _, opt := range opts {
		opt(app)
	}
	
	return app
}
```

> **Takeaway**: Functional options scale to any number of optional parameters without breaking the constructor signature. Each option is self-documenting: `WithTimeout(5 * time.Second)` reads better than a positional argument. This pattern is used by `grpc.NewServer`, `http.NewServeMux`, and most production Go libraries.

## 4. PITFALLS

| # | Defect | Fix |
| --- | --- | --- |
| 1 | Using value receivers for mutation methods | Use pointer receivers `func (c *Customer)`. Value receivers operate on a copy. |
| 2 | Expecting method overriding through embedding | Embedding is not inheritance. The embedded struct's methods always bind to the embedded type. |
| 3 | Using large config structs with many zero-valued fields | Use functional options pattern — each option function is self-documenting and composable. |

## 5. REF

| Resource | Link |
| --- | --- |
| Pointers vs Values | [go.dev/doc/effective_go#pointers_vs_values](https://go.dev/doc/effective_go#pointers_vs_values) |
| Embedding | [go.dev/doc/effective_go#embedding](https://go.dev/doc/effective_go#embedding) |

## 6. RECOMMEND

| Extension | When | Rationale |
| --- | --- | --- |
| [Optional Properties](./11-optional-nullable.md) | When constructor parameters are optional | Pointer fields and functional options serve different use cases |
| [Map Utilities](./03-object-map-utils.md) | When building configuration from dynamic key-value sources | Generic map operations for config merging |

**Navigation**: [← Optional & Nullable](./11-optional-nullable.md) · [→ Directory Overview](./README.md)
