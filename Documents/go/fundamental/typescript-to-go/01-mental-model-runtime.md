<!-- tags: golang, typescript, runtime -->
# 🧭 Mental Model & Runtime — From Type Layer to Compiled Language.

> First lesson for TypeScript engineers migrating to Go: key differences in runtime, ownership, package boundaries, zero value, and how Go wants you to design your code.

📅 Created: 2026-04-06 · 🔄 Updated: 2026-04-19 · ⏱️ 16 min read

| Aspect | Detail |
| --- | --- |
| **Focus** | Runtime model, value semantics, package boundaries |
| **Use case** | The first 1-3 days when starting to write Go after many years in TypeScript |
| **Key diff** | TypeScript is a type layer on top of JavaScript; Go is a compiled language with its own runtime |
| **Go stdlib** | `context`, `fmt`, `net/http`, `sync/atomic` |

## 1. DEFINE

You have just ported a handler from NestJS to Go. The function name is similar, the DTO is similar, the compiler is green. But a few hours later, you encounter three surprises.

- A field that is not initialized but still has a valid value because of zero value.
- A method modifies the state but nothing changes because you use a value receiver.
- An interface does not need `implements`, but the compiler still considers it satisfied.

That is when you realize: the real difference is not syntax. TypeScript mainly helps you verify your JavaScript program before running it. Go brings the type system, package boundaries, memory layout, and build tooling into a single compiled binary.

### 1.1 TypeScript and Go protect you at two different layers.

TypeScript, according to the official Handbook, is a static typechecker for JavaScript programs. Its strongest guarantees operate before runtime — after compilation, you still run on the JavaScript engine and its event loop.

This entails three consequences:

1. In TypeScript, many guarantees reside in the compiler or framework.
2. In Go, guarantees are in language + package boundary + runtime behavior.
3. In TypeScript, you often optimize developer ergonomics through abstraction. In Go, you often optimize for readability, predictability, and explicitness.

### 1.2 4 rewires you must do soon.

**Packages are architectural boundaries, not decorative folders.** 
In Go, lowercase/uppercase is more than just style — it decides the public API of the package. You hide invariants behind export boundaries, without needing `private/protected`.

**Zero value is a feature, not a bug.** 
`var cfg Config` is a valid object at the language level. But whether it is business-valid is still the responsibility of the constructor or validation function.

**Value vs pointer is a behavioral decision.** 
In TypeScript, objects follow shared reference semantics at runtime. In Go, you must decide when to copy values and when to use pointers — the method set changes accordingly.

**Interfaces are defined by the consumer.** 
Go does not want you to build a class hierarchy and then fill in `implements`. It wants the package that uses a dependency to say "I need exactly these 1-2 methods", then lets the compiler check implicitly.

### 1.3 Invariants & Failure Modes

- Zero value is convenient, but does not automatically encode business variables. `User{}` compiling does not mean the domain is valid.
- Pointer receiver should be the default choice when the mutate state or struct method is large enough that copying is pointless.
- Don't bring the decorators, DI container, request-scoped provider model from NestJS into Go just because "the team is used to it". Most of the time you are importing framework complexity without getting additional value.

## 2. VISUAL

The most confusing part is not the definition, but where the guarantee actually lies. The two diagrams below pull that exact point into view.

### Level 1

```text
TypeScript path
source.ts
    -> tsc checks types
        -> output JavaScript
            -> Node.js / browser runtime
                -> framework / library conventions

Go path
source.go
    -> go build / go test
        -> native binary
            -> Go runtime
                -> stdlib + package boundaries
```

![Mental model runtime compare card](./images/01-mental-model-runtime-compare.png)

*Figure: Level 1 shows that TypeScript and Go both compile, but where the actual guarantee is implemented is very different.*.

### Level 2

```text
TypeScript
  type safety ........ mostly before runtime
  object model ....... JavaScript semantics
  async model ........ event loop + Promise
  architecture ....... framework shapes a lot of decisions

Go
  type safety ........ compiler + method sets + package exports
  object model ....... structs, pointers, zero values
  async model ........ goroutines + channels + context
  architecture ....... stdlib + simple composition
```

*Figure: Level 2 emphasizes the origin of most system conversion bugs: you think you are changing the syntax, but actually you are changing the operating mechanism.*.

## 3. CODE

When the mental model is not locked, it is very easy for Go code to "look right". The three examples below summarize the places that most often fool TypeScript engineers.

### Example 1: Basic — zero value is useful, but the new constructor holds invariant.

> **Goal**: Understand that zero value in Go is a language feature, but invariants must still be enforced explicitly.
> **Approach**: Use a struct with reasonable defaults, but enforce required fields through a constructor.
> **Example**: `NewServerConfig("billing")` creates valid config; `ServerConfig{}` is just a zero value — it may not be business-valid.

TypeScript version you usually start from:

```typescript
type ServerConfig = {
  serviceName: string;
  timeoutMs: number;
  maxConns: number;
};

function createServerConfig(serviceName: string): ServerConfig {
  if (!serviceName) {
    throw new Error("service name is required");
  }

  return {
    serviceName,
    timeoutMs: 2000,
    maxConns: 100,
  };
}

const cfg = createServerConfig("billing");
console.log(cfg);
```

Corresponding Go version:

```go
package main

import (
	"fmt"
	"time"
)

type ServerConfig struct {
	ServiceName string
	Timeout     time.Duration
	MaxConns    int
}

func NewServerConfig(serviceName string) (ServerConfig, error) {
	if serviceName == "" {
		return ServerConfig{}, fmt.Errorf("service name is required")
	}

	return ServerConfig{
		ServiceName: serviceName,
		Timeout:     2 * time.Second, // zero value will not give you this default
		MaxConns:    100,
	}, nil
}

func main() {
	var zero ServerConfig
	fmt.Printf("zero value: %+v\n", zero)

	cfg, err := NewServerConfig("billing")
	if err != nil {
		panic(err)
	}

	fmt.Printf("constructed: %+v\n", cfg)
}
```

> **Takeaway**: Zero value gives you a language-valid object. A constructor gives you a domain-valid object. These are not the same thing.

### Example 2: Intermediate — consumer-defined interface, no `implements` needed.

> **Goal**: Understand that Go prioritizes small contracts defined where dependencies are consumed, not in the provider package.
> **Approach**: Define the interface in the consumer package. Let the concrete type satisfy it implicitly.
> **Example**: `ProfileService` only needs a single `Load` method.

Familiar TypeScript version:

```typescript
interface Profile {
  id: string;
  name: string;
}

interface ProfileLoader {
  load(id: string): Promise<Profile>;
}

class MemoryStore implements ProfileLoader {
  constructor(private readonly data: Record<string, Profile>) {}

  async load(id: string): Promise<Profile> {
    const profile = this.data[id];
    if (!profile) {
      throw new Error(`profile ${id} not found`);
    }
    return profile;
  }
}

class ProfileService {
  constructor(private readonly loader: ProfileLoader) {}

  async greeting(id: string): Promise<string> {
    const profile = await this.loader.load(id);
    return `hello ${profile.name}`;
  }
}
```

Corresponding Go version:

```go
package main

import (
	"context"
	"fmt"
)

type Profile struct {
	ID   string
	Name string
}

type ProfileLoader interface {
	Load(ctx context.Context, id string) (Profile, error)
}

type MemoryStore struct {
	data map[string]Profile
}

func (s MemoryStore) Load(ctx context.Context, id string) (Profile, error) {
	profile, ok := s.data[id]
	if !ok {
		return Profile{}, fmt.Errorf("profile %s not found", id)
	}
	return profile, nil
}

type ProfileService struct {
	loader ProfileLoader
}

func NewProfileService(loader ProfileLoader) ProfileService {
	return ProfileService{loader: loader}
}

func (s ProfileService) Greeting(ctx context.Context, id string) (string, error) {
	profile, err := s.loader.Load(ctx, id)
	if err != nil {
		return "", err
	}
	return "hello " + profile.Name, nil
}

func main() {
	store := MemoryStore{
		data: map[string]Profile{"u-1": {ID: "u-1", Name: "Mina"}},
	}

	service := NewProfileService(store)
	msg, err := service.Greeting(context.Background(), "u-1")
	if err != nil {
		panic(err)
	}

	fmt.Println(msg)
}
```

> **Why?** TypeScript engineers are used to interfaces being defined in provider packages or tied into DI containers. Go reverses this: the consumer declares what it needs, and the producer just has to have the right methods.

> **Takeaway**: Let the consuming package define the interface. This is one of the biggest mental shifts from OOP-heavy TypeScript to Go.

### Example 3: Advanced — pointer receiver vs value receiver completely changes the outcome.

> **Goal**: Avoid the mistake of thinking you mutated state when you actually edited a copy.
> **Approach**: Compare methods on value receiver vs pointer receiver.
> **Example**: `Add` on a value receiver does not change the original counter; `AddInPlace` on a pointer receiver does.

TypeScript version, where default object mutation follows reference semantics:

```typescript
class Counter {
  total = 0;

  add(n: number) {
    this.total += n;
  }
}

const counter = new Counter();
counter.add(5);
console.log("after add:", counter.total); // 5

const alias = counter;
alias.add(10);
console.log("after alias add:", counter.total); // 15
```

Corresponding Go version:

```go
package main

import "fmt"

type Counter struct {
	total int
}

// Value receiver: operates on a copy
func (c Counter) Add(n int) {
	c.total += n
}

// Pointer receiver: modifies the original
func (c *Counter) AddInPlace(n int) {
	c.total += n
}

func main() {
	counter := Counter{}

	counter.Add(5)
	fmt.Println("after Add:", counter.total) // 0

	counter.AddInPlace(5)
	fmt.Println("after AddInPlace:", counter.total) // 5

	copyCounter := counter
	copyCounter.AddInPlace(10)
	fmt.Println("copy:", copyCounter.total)   // 15
	fmt.Println("orig:", counter.total)       // 5
}
```

> **Why?** In Go, method receivers are part of the semantics, not just syntax. TypeScript developers are used to object mutations following references naturally. Go forces you to be explicit: copy is copy, pointer is pointer.

> **Takeaway**: If a method needs to mutate state or the struct is large enough that copying is wasteful, use a pointer receiver. Do not mix value/pointer receivers unless you understand method sets and their implications.

## 4. PITFALLS

| # | Severity | Error | Consequence | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Fatal | Treating zero value as a default business object | Entity/config compiles but violates invariants | Use a constructor or `Validate()` to separate syntax validity from domain validity |
| 2 | 🟡 Common | Bringing class hierarchies or DI containers from TypeScript to Go | Code is heavy on abstraction, hard to read, hard to debug, and not idiomatic | Start with struct + small interface + explicit constructor |
| 3 | 🔵 Minor | Mixing value and pointer receivers without intention | Mutation does not behave as expected | Convention: mutating methods and large structs use pointer receivers |

## 5. REF

| Resource | Type | Link | Note |
| --- | --- | --- | --- |
| The TypeScript Handbook | Official | https://www.typescriptlang.org/docs/handbook/intro.html | Confirm TypeScript is a static typechecker for JavaScript |
| Effective Go | Official | https://go.dev/doc/effective_go | Idiomatic baseline for package boundaries, interfaces, receivers, and composition |
| Go Spec — Method sets | Official | https://go.dev/ref/spec#Method_sets | Source of truth differentiates value receiver vs pointer receiver |

## 6. RECOMMEND

The core of **Mental Model & Runtime** is clear. The extension branches below help you bring Go runtime understanding into production with types, error handling, and concurrency.
| Extension | When | Rationale | Link |
| --- | --- | --- | --- |
| Types & Data Modeling | When starting to port DTOs, entities, and configs | The correct mental model must come with the correct data shape | [→ 02-types-data-modeling](./02-types-data-modeling.md) |
| Class → Struct | When you want to translate classes to structs one-to-one | Helps gradually eliminate unnecessary OOP abstractions | [→ 12-class-struct](../helper/12-class-struct.md) |
| Type Assertion & Embedding | When method sets, interface satisfaction, or embedding remains ambiguous | Goes deeper into the type mechanics behind the mental model | [→ 03-type-assertion-embedding](../types/03-type-assertion-embedding.md) |
| Project Layout, Tooling, Testing | When you understand Go code but are unfamiliar with how Go teams build and ship | Differentiates workflow, not just syntax | [→ 04-project-layout-tooling](./04-project-layout-tooling-testing.md) |

**Navigation**: [← Previous](./README.md) · [→ Next](./02-types-data-modeling.md)
