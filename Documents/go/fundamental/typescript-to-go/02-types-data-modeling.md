<!-- tags: golang, typescript, data-structures -->
# 🧱 Types & Data Modeling — From Union, Optional, Class to Structure and Named Types.

> How to map shape data from TypeScript to Go without dropping invariants: optionals, enums, unions, interfaces, slices/maps, and boundaries between DTO and domain.

📅 Created: 2026-04-06 · 🔄 Updated: 2026-04-19 · ⏱️ 17 min read

| Aspect | Detail |
| --- | --- |
| **Focus** | Structs, named types, optionals, enum-like types, interfaces |
| **Use case** | Port DTO, entity, config, request/response contract from TypeScript to Go |
| **Key diff** | TypeScript prioritizes shape flexibility; Go prioritizes explicit data models and invariant near data |
| **Go stdlib** | `encoding/json`, `errors`, `fmt` |

## 1. DEFINE

You are porting a contract API from TypeScript:

- `status: "draft" | "paid" | "cancelled"`
- `couponCode?: string`
- `customer: User | Guest`
- `class Order { ... }`

If you try to translate line by line into Go, you will quickly fall into three familiar mistakes:

- Turn all optional fields into pointers, making the model heavy and difficult to read.
- Use `interface{}` or `map[string]any` to simulate unions quickly.
- Insert domain behavior into every struct as if preserving the TypeScript class model.

Go does not prohibit you from doing so. But it also does not reward you for doing so. Good data models in Go are usually small, explicit, and encode boundaries clearly: DTO is DTO, domain is domain, persistence is persistence.

### 1.1 How are TypeScript's structural typing and Go's named types different?

TypeScript is very powerful at inferring shape compatibility between objects. That is extremely useful for frontend-heavy and API-heavy codebases. Go prioritizes named types, method sets, and field visibility more explicitly. Interfaces in Go are satisfied implicitly — the struct just needs the right methods.

A pragmatic rule:

- If data goes across network or file boundary: use struct with clear tags.
- If the value has its own domain meaning: create a named type instead of leaving the `string` bare.
- If status has a finite set: use `type Status string` + constants + validation.

### 1.2 Optional, nullable, zero value: these three things are not one.

In TypeScript, `field?: string`, `field: string | null`, and `field: string | undefined` is often used quite flexibly. In Go, you should clearly separate:

- **Required field but has a valid zero value**: use value type directly.
- **Field is truly optional at boundary**: use pointer or custom wrapper.
- **Field required in domain but optional in input**: DTO can use pointer, domain cannot.

Don't let the entire model turn into a pointer forest just because the JSON input allows it to be left blank.

### 1.3 Invariants & Failure Modes

- `nil map` can be read, but writing will panic.
- `nil slice` is safer than `nil map`; append, JSON behavior is different depending on the intent of the API.
- `map[string]any` and `interface{}` are a quick exit, but also the fastest way to bring dynamic typing back.

Before writing another `struct`, look at this problem as a data transformation pipeline.

## 2. VISUAL

The most dangerous point of data modeling is not in the syntax, but in mixing boundary and invariant. The diagram below separates them.

### Level 1

```text
TypeScript input shape
    -> DTO / schema
        -> domain object
            -> persistence shape

Go input shape
    -> request DTO struct
        -> validation / translation
            -> domain struct with invariants
                -> storage DTO or row model
```

![Types data modeling compare card](./images/02-types-data-modeling-compare.png)

*Figure: Level 1 emphasizes that Go encourages you to translate data across boundaries instead of keeping a "use-everywhere" shape.*.

### Level 2

```text
TS concept                Go mapping
------------------------------------------------------------
optional field            pointer field or separate DTO layer
string literal union      named string type + const + Validate
class with methods        struct + methods or service around struct
discriminated union       interface + concrete structs + type switch
Record<string, T>         map[string]T
readonly domain field     unexported field + constructor/getter
```

*Image: Level 2 is not an absolute one-to-one translation table; it is a safe starting point to avoid syntax over-porting.*.

## 3. CODE

If the mental model is correct but the data model is wrong, you will still have a bug. The three examples below lock down the most important mappings.

### Example 1: Basic — DTO optional at boundary, domain is explicit.

> **Goal**: Separate request DTO from domain object instead of using one struct for everything.
> **Approach**: The request struct uses pointers for optional fields; the domain object enforces invariants via its constructor.
> **Example**: `couponCode` can be absent from the JSON, but the `Order` domain does not need to embrace all that optionality.

Your TypeScript version is usually available at the API boundary:

```typescript
type CreateOrderRequest = {
  id: string;
  amount: number;
  couponCode?: string;
};

class Order {
  constructor(
    readonly id: string,
    readonly amount: number,
    readonly couponCode: string = "",
  ) {
    if (!id) throw new Error("id is required");
    if (amount <= 0) throw new Error("amount must be positive");
  }
}

const req: CreateOrderRequest = { id: "ord-1", amount: 1200 };
const order = new Order(req.id, req.amount, req.couponCode ?? "");
console.log(order);
```

Corresponding Go version:

```go
package main

import (
	"encoding/json"
	"fmt"
)

type CreateOrderRequest struct {
	ID         string  `json:"id"`
	Amount     int64   `json:"amount"`
	CouponCode *string `json:"couponCode,omitempty"`
}

type Order struct {
	ID         string
	Amount     int64
	CouponCode string
}

func NewOrder(req CreateOrderRequest) (Order, error) {
	if req.ID == "" {
		return Order{}, fmt.Errorf("id is required")
	}
	if req.Amount <= 0 {
		return Order{}, fmt.Errorf("amount must be positive")
	}

	order := Order{ID: req.ID, Amount: req.Amount}
	if req.CouponCode != nil {
		order.CouponCode = *req.CouponCode
	}
	return order, nil
}

func main() {
	raw := []byte(`{"id":"ord-1","amount":1200}`)

	var req CreateOrderRequest
	if err := json.Unmarshal(raw, &req); err != nil {
		panic(err)
	}

	order, err := NewOrder(req)
	if err != nil {
		panic(err)
	}

	fmt.Printf("%+v\n", order)
}
```

> **Takeaway**: Optionality is a boundary concern. Domain objects should be more invariant than boundary objects.

Boundary has finished separating. But if the state is still a bare `string`, the invariant is still leaking somewhere else.

### Example 2: Intermediate — string union in TypeScript should be a named type with validation.

> **Goal**: Avoid bare `string` for state values that have a finite set of valid options.
> **Approach**: Use a named string type with constants and a `Validate()` method.
> **Example**: `OrderStatus` instead of `"draft" | "paid" | "cancelled"`.

TypeScript versions usually start from a literal union:

```typescript
type OrderStatus = "draft" | "paid" | "cancelled";

type Order = {
  id: string;
  status: OrderStatus;
};

function createOrder(id: string, status: OrderStatus): Order {
  if (!id) {
    throw new Error("id is required");
  }
  return { id, status };
}

console.log(createOrder("ord-2", "paid"));
```

Corresponding Go version:

```go
package main

import "fmt"

type OrderStatus string

const (
	StatusDraft     OrderStatus = "draft"
	StatusPaid      OrderStatus = "paid"
	StatusCancelled OrderStatus = "cancelled"
)

func (s OrderStatus) Validate() error {
	switch s {
	case StatusDraft, StatusPaid, StatusCancelled:
		return nil
	default:
		return fmt.Errorf("invalid order status %q", s)
	}
}

type Order struct {
	ID     string
	Status OrderStatus
}

func NewOrder(id string, status OrderStatus) (Order, error) {
	if id == "" {
		return Order{}, fmt.Errorf("id is required")
	}
	if err := status.Validate(); err != nil {
		return Order{}, err
	}
	return Order{ID: id, Status: status}, nil
}

func main() {
	order, err := NewOrder("ord-2", StatusPaid)
	if err != nil {
		panic(err)
	}
	fmt.Printf("%+v\n", order)
}
```

> **Why?** TypeScript literal unions give you compile-time constraints very naturally. In Go, named type + constants + validation is the simplest way to preserve the same intent without over-engineering. It is more explicit and scales well.

> **Takeaway**: If a value has its own domain meaning, give it its own type. Bare `string` is an expensive liability as the codebase grows.

At this point, the data shape is more solid. The rest is when a value has many behavioral variations, not just many fields.

### Example 3: Advanced — union behavior should be a small interface + controlled switch type.

> **Goal**: See how Go handles "one of many variations" without falling into `map[string]any`.
> **Approach**: Use small interfaces for common behavior, then type switches when specific branches are needed.
> **Example**: `Customer` can be a guest or a registered user.

TypeScript version with discriminated union:

```typescript
type GuestCustomer = {
  kind: "guest";
  email: string;
};

type RegisteredCustomer = {
  kind: "registered";
  id: string;
  email: string;
};

type Customer = GuestCustomer | RegisteredCustomer;

function shippingRule(customer: Customer): string {
  switch (customer.kind) {
    case "guest":
      return `guest checkout for ${customer.email}`;
    case "registered":
      return `saved profile checkout for ${customer.email}`;
  }
}
```

Corresponding Go version:

```go
package main

import "fmt"

type Customer interface {
	Label() string
	IsGuest() bool
}

type GuestCustomer struct {
	Email string
}

func (g GuestCustomer) Label() string { return "guest:" + g.Email }
func (g GuestCustomer) IsGuest() bool { return true }

type RegisteredCustomer struct {
	ID    string
	Email string
}

func (r RegisteredCustomer) Label() string { return "user:" + r.ID }
func (r RegisteredCustomer) IsGuest() bool { return false }

func shippingRule(c Customer) string {
	switch v := c.(type) {
	case GuestCustomer:
		return "guest checkout for " + v.Email
	case RegisteredCustomer:
		return "saved profile checkout for " + v.Email
	default:
		return "unsupported customer"
	}
}

func main() {
	customers := []Customer{
		GuestCustomer{Email: "guest@example.com"},
		RegisteredCustomer{ID: "u-1", Email: "mina@example.com"},
	}

	for _, c := range customers {
		fmt.Println(c.Label(), "->", shippingRule(c))
	}
}
```

> **Why?** TypeScript discriminated unions are powerful because of control-flow narrowing. Go does not have the same mechanism, so the most practical pattern is a small interface for common behavior and type switches at exactly the points where you need variant-specific logic.

> **Takeaway**: When you need union-like modeling, start from common behavior and branch at the boundary. Do not jump straight to dynamic maps.

## 4. PITFALLS

This is when many ports still look good on PR but start to fail after a few sprints.

Bugs don't come from syntax. It comes from a semantically incorrect model.

| # | Severity | Error | Consequence | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Fatal | Using `map[string]any` to quickly simulate flexible unions/objects | Loss of compile-time guarantees, increased type assertion errors | Use dynamic maps only at deserialization boundaries; create named types everywhere else |
| 2 | 🟡 Common | Turning every optional field into a pointer | Model is heavy, code checks nil everywhere | Use pointers only for meaningful optionality at the boundary; domain holds required fields explicitly |
| 3 | 🔵 Minor | Using bare `string` for status, role, kind | Invalid state penetrates deeply into the system, revealing bugs late | Create named type + constants + validation |

## 5. REF

| Resource | Type | Link | Note |
| --- | --- | --- | --- |
| Type Compatibility | Official | https://www.typescriptlang.org/docs/handbook/type-compatibility.html | TypeScript's structural typing foundation |
| Go Spec — Types | Official | https://go.dev/ref/spec#Types | Source of truth for named types, struct fields, assignability, and composite types |
| Go Blog — JSON and Go | Official | https://go.dev/blog/json | Good reference for DTO boundary, tags, optionality, and serialization behavior |

## 6. RECOMMEND

The core part of **Types & Data Modeling** is clear. The extension branches below help you bring the Go type system into production with errors, concurrency, and project layout.

It is there that good or bad data models begin to show up under real load.

| Extension | When | Rationale | Link |
| --- | --- | --- | --- |
| Slices, Maps, Strings | When you need to understand Go's collection semantics at the runtime level | Primer for slice growth, map behavior, and string internals | [→ 01-slices-maps-strings](../types/01-slices-maps-strings.md) |
| Enum & Union Types | When the model has a state machine, enum, or discriminated union | Helps choose named type, constants, or interface + type switch | [→ 06-enum-union-types](../helper/06-enum-union-types.md) |
| Optional & Nullable | When input has `undefined`, `null`, partial updates, or nullable DB fields | Helps choose pointer, zero value, or wrapper type intentionally | [→ 11-optional-nullable](../helper/11-optional-nullable.md) |
| Error Handling | Once the data model is locked and you start writing domain flow | Good invariants must come with a clear error model | [→ 07-error-handling](../helper/07-error-handling.md) |
| Errors, Concurrency, Context | Once DTO/domain is solid and the service starts calling I/O in parallel | Where the data model meets runtime semantics | [→ 03-errors-concurrency-context](./03-errors-concurrency-context.md) |
| Class → Struct | When the data model is still too class-heavy | Helps reduce unnecessary abstractions | [→ 12-class-struct](../helper/12-class-struct.md) |

**Navigation**: [← Previous](./01-mental-model-runtime.md) · [→ Next](./03-errors-concurrency-context.md)
