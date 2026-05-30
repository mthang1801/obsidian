<!-- tags: golang, typescript, concurrency -->
# ⚙️ Errors, Concurrency, Context — From `throw` and `await` to `err`, goroutine, context.

> The most important articles when porting services from TypeScript to Go: explicit error flow, safe fan-out, cancellation, timeout, and bounded concurrency.

📅 Created: 2026-04-06 · 🔄 Updated: 2026-04-19 · ⏱️ 18 min read

| Aspect | Detail |
| --- | --- |
| **Focus** | Error returns, wrapping, goroutines, `context`, `errgroup` |
| **Use case** | Port service is using `async/await`, `Promise.all`, timeout, abort logic |
| **Key diff** | TypeScript async runs on the event loop; Go concurrency is a language-level primitive with explicit lifecycle control |
| **Go stdlib** | `context`, `errors`, `fmt`, `time` |

## 1. DEFINE

You have a TypeScript service that does exactly what you want:

- Call 3 APIs at once using `Promise.all`.
- Timeout with `AbortController`
- `throw` when downstream fails
- `catch` in the outer layer and then map it to an HTTP response.

When switching to Go, most engineers think they only need:

- `await` -> `<-ch`
- `Promise.all` -> several goroutines
- `throw` -> `panic`

That is the most dangerous slip. In Go, error is not an exception flow. Cancellation does not propagate itself unless you pass `context.Context`. Goroutines do not limit themselves, do not clean up after themselves, and do not stop unless you design a clear exit path.

### 1.1 Errors in Go are data, not runtime side effects.

TypeScript can use `throw` or reject a Promise as a valid control flow path. Go prioritizes returning `error` explicitly at each boundary. This looks more verbose, but it makes the error path and associated metadata much easier to trace.

Pragmatic rule:

- Business or I/O failure: `return err`.
- Invariant is broken by the caller and cannot continue: consider panic at a very narrow boundary.
- Library code: almost always `return err`, very rarely `panic`.

### 1.2 Concurrency in Go is more powerful than Promise, but also easier to create leaks.

TypeScript async is essentially non-blocking I/O orchestration on the event loop. Go gives you very cheap goroutines, but cheap doesn't mean free. Any goroutine without a clear stopping path can become a leak.

Therefore, when porting code from TypeScript:

- `Promise.all` usually maps well to `errgroup`.
- `AbortController` usually maps to `context.WithCancel` or `WithTimeout`.
- `Promise.race` usually maps to `select`.
- Fire-and-forget almost always needs a review.

### 1.3 Invariants & Failure Modes

- Not passing `context` down to the dependency means timeout/cancel on the upper layer is almost useless.
- Goroutine sent to the channel without a consumer will be blocked permanently.
- Using `panic` instead of error propagation in service code will make incident debugging worse, not better.

In short: syntax port is fast. Lifecycle port is slow.

And it is that slow part that determines the incident.

## 2. VISUAL

You only see the difference between TypeScript and Go when looking at the parallel request lifecycle. These two diagrams give that exact angle.

### Level 1

```text
TypeScript request
request
  -> async function
      -> Promise.all([...])
          -> await results
              -> catch error

Go request
request
  -> context.WithTimeout(...)
      -> errgroup.WithContext(ctx)
          -> g.Go(...) x N
              -> g.Wait()
```

![Errors concurrency context compare card](./images/03-errors-concurrency-context-compare.png)

*Figure: Level 1 shows that Go fan-out is not just "running in parallel", but is also a lifecycle with clear context and error fan-in.*.

### Level 2

```text
request starts
  -> spawn goroutines
      -> one downstream fails
          -> cancel shared context
              -> siblings must observe ctx.Done()
                  -> return early
                      -> g.Wait() closes the loop
```

*Figure: Level 2 emphasizes what determines production quality: an error in one branch must stop the remaining branches on purpose, not by luck.*.

## 3. CODE

Most migration bugs lie in error flow and cancellation being written "similarly". The three examples below lock down the more production-safe version.

### Example 1: Basic — wrap errors with context instead of throwing vague exceptions.

> **Goal**: Build a `return err` + wrap pattern with context at each boundary.
> **Approach**: Separate parse, validate, and persist. Each layer adds context to the error.
> **Example**: Creating a user with invalid input or a storage failure.

Common TypeScript versions:

```typescript
type User = { email: string };

function parseEmail(rawEmail: string): string {
  if (!rawEmail) {
    throw new Error("email is empty");
  }
  return rawEmail;
}

async function saveUser(email: string): Promise<void> {
  if (email === "downstream@fail.local") {
    throw new Error("storage unavailable");
  }
}

async function createUser(rawEmail: string): Promise<User> {
  try {
    const email = parseEmail(rawEmail);
    await saveUser(email);
    return { email };
  } catch (error) {
    throw new Error(`create user failed: ${String(error)}`);
  }
}
```

Corresponding Go version:

```go
package main

import "fmt"

type User struct {
	Email string
}

func parseEmail(raw string) (string, error) {
	if raw == "" {
		return "", fmt.Errorf("email is empty")
	}
	return raw, nil
}

func saveUser(email string) error {
	if email == "downstream@fail.local" {
		return fmt.Errorf("storage unavailable")
	}
	return nil
}

func createUser(rawEmail string) (User, error) {
	email, err := parseEmail(rawEmail)
	if err != nil {
		return User{}, fmt.Errorf("create user: parse email: %w", err)
	}

	if err := saveUser(email); err != nil {
		return User{}, fmt.Errorf("create user: save user %q: %w", email, err)
	}

	return User{Email: email}, nil
}

func main() {
	user, err := createUser("mina@example.com")
	if err != nil {
		panic(err)
	}
	fmt.Println(user.Email)
}
```

> **Takeaway**: In Go, the right verbosity gives you the ability to debug cheaply at 3 AM.

Wrapping the error properly helps you know what's going on. Production also requires you to stop the branches that should not be continued.

### Example 2: Intermediate — `Promise.all` should map to `errgroup` + shared context.

> **Goal**: Fan-out 3 downstream calls with timeout and fail-fast safety.
> **Approach**: Use `errgroup.WithContext` to collect errors and propagate cancellation.
> **Example**: Load profile, balance, and invoices in parallel within 500ms.

Familiar TypeScript version:

```typescript
async function fetchPart(name: string, delayMs: number, signal: AbortSignal): Promise<string> {
  await new Promise((resolve, reject) => {
    const timer = setTimeout(resolve, delayMs);
    signal.addEventListener("abort", () => {
      clearTimeout(timer);
      reject(signal.reason ?? new Error("aborted"));
    });
  });

  if (name === "balance") {
    throw new Error(`${name} service timeout`);
  }
  return `${name}:ok`;
}

async function loadDashboard(): Promise<Record<string, string>> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(new Error("timeout")), 500);

  try {
    const [profile, balance, invoices] = await Promise.all([
      fetchPart("profile", 200, controller.signal),
      fetchPart("balance", 200, controller.signal),
      fetchPart("invoices", 200, controller.signal),
    ]);

    return { profile, balance, invoices };
  } finally {
    clearTimeout(timeout);
  }
}
```

Corresponding Go version:

```go
package main

import (
	"context"
	"fmt"
	"sync"
	"time"

	"golang.org/x/sync/errgroup"
)

func fetch(ctx context.Context, name string, d time.Duration) (string, error) {
	select {
	case <-time.After(d):
		if name == "balance" {
			return "", fmt.Errorf("%s service timeout", name)
		}
		return name + ":ok", nil
	case <-ctx.Done():
		return "", ctx.Err()
	}
}

func loadDashboard(ctx context.Context) (map[string]string, error) {
	ctx, cancel := context.WithTimeout(ctx, 500*time.Millisecond)
	defer cancel()

	results := map[string]string{}
	var mu sync.Mutex
	g, ctx := errgroup.WithContext(ctx)

	for _, name := range []string{"profile", "balance", "invoices"} {
		name := name
		g.Go(func() error {
			val, err := fetch(ctx, name, 200*time.Millisecond)
			if err != nil {
				return fmt.Errorf("fetch %s: %w", name, err)
			}
			mu.Lock()
			results[name] = val
			mu.Unlock()
			return nil
		})
	}

	if err := g.Wait(); err != nil {
		return nil, err
	}
	return results, nil
}

func main() {
	out, err := loadDashboard(context.Background())
	fmt.Println("results:", out)
	fmt.Println("error:", err)
}
```

> **Why?** This is the closest equivalent to `Promise.all`, but with one production-critical difference: `errgroup` ties fan-out to a shared context. If one branch fails, the remaining branches can observe cancellation and stop early, rather than continuing pointlessly.

> **Takeaway**: When porting `Promise.all`, think immediately of `errgroup + context`, not "3 goroutines and hope for the best".

Fail-fast is available. But if the batch grows to 1,000 jobs, the question changes to: how many jobs do you allow to run at once?

### Example 3: Advanced — bounded concurrency + cancellation is the production version of "fire many tasks".

> **Goal**: Avoid spawning infinite goroutines when processing large batches.
> **Approach**: Limit worker count, respect `ctx.Done()`, and close channels with discipline.
> **Example**: Handle 6 jobs with a maximum of 2 workers.

TypeScript version with explicitly limited pool:

```typescript
async function runWorkerPool(jobs: number[], workerCount: number): Promise<string[]> {
  const results: string[] = [];
  let nextIndex = 0;

  async function worker(id: number) {
    while (nextIndex < jobs.length) {
      const job = jobs[nextIndex++];
      await new Promise((resolve) => setTimeout(resolve, 50));
      results.push(`worker-${id} handled job-${job}`);
    }
  }

  await Promise.all(
    Array.from({ length: workerCount }, (_, index) => worker(index + 1)),
  );

  return results;
}
```

Corresponding Go version:

```go
package main

import (
	"context"
	"fmt"
	"sync"
	"time"
)

func worker(ctx context.Context, id int, jobs <-chan int, results chan<- string, wg *sync.WaitGroup) {
	defer wg.Done()

	for {
		select {
		case <-ctx.Done():
			return
		case job, ok := <-jobs:
			if !ok {
				return
			}

			time.Sleep(50 * time.Millisecond)
			results <- fmt.Sprintf("worker-%d handled job-%d", id, job)
		}
	}
}

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 300*time.Millisecond)
	defer cancel()

	jobs := make(chan int)
	results := make(chan string)

	var wg sync.WaitGroup
	for workerID := 1; workerID <= 2; workerID++ {
		wg.Add(1)
		go worker(ctx, workerID, jobs, results, &wg)
	}

	go func() {
		defer close(jobs)
		for i := 1; i <= 6; i++ {
			jobs <- i
		}
	}()

	go func() {
		wg.Wait()
		close(results)
	}()

	for result := range results {
		fmt.Println(result)
	}
}
```

> **Why?** TypeScript teams are used to very cheap async I/O, so they often unconsciously treat "more concurrency" as a good default. Go allows you to go further, but also requires you to manage the lifecycle of every goroutine.

> **Takeaway**: When batches are large or downstream is expensive, limiting concurrency is an operational requirement, not arbitrary optimization.

## 4. PITFALLS

The three errors below all have one thing in common: reviews seem reasonable to the naked eye.

They only show up when timeout, retry, and traffic arrive at the same time.

| # | Severity | Error | Consequence | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Fatal | Use `panic` as `throw` in a regular flow service | Crash goroutine or process, lost error context right boundary | Return `error`, wrap error, panic only in narrow invariant or process startup |
| 2 | 🟡 Common | Spawn goroutine without `context` or stop condition | Goroutine leak, keeps connection/open file useless | Pass `ctx` throughout and always design an escape route |
| 3 | 🔵 Minor | Use channel when `errgroup` or return value is sufficient | Code is harder to read and reason than necessary | Starting from the simplest primitive; Only add channels when there is a real streaming/co-ordination need |

## 5. REF

| Resource | Type | Link | Note |
| --- | --- | --- | --- |
| Go for Cloud & Network Services | Official | https://go.dev/solutions/cloud | Official source for Go concurrency, services, tooling |
| `context` package | Official | https://pkg.go.dev/context | Source of truth for cancellation, timeout, and deadlines |
| Effective Go — Errors | Official | https://go.dev/doc/effective_go#errors | The standard convention for `error` return, wrap, and boundary handles error handling |

## 6. RECOMMEND

The core of **Errors, Concurrency & Context** is clear. The extension branches below help you bring error handling and concurrency into production with project layout, tooling, and testing.

The next part is to turn that reflection into a team pattern that can be used every day.

| Extension | When | Rationale | Link |
| --- | --- | --- | --- |
| Promise & Async | When the team still thinks in `Promise.all`, `AbortController`, or async combinators | Closest mapping recipe after understanding Go's lifecycle control | [→ 04-promise-async](../helper/04-promise-async.md) |
| Error Handling | When `throw`, `try/catch`, and wrapping strategy are still confusing | Connects directly from TypeScript error model to Go error chain | [→ 07-error-handling](../helper/07-error-handling.md) |
| Table-driven Tests & Mocking | When the async flow is solid and you need to harden it with tests | Go testing rhythm is significantly different from TS/Jest | [→ 01-table-driven-mocking](../testing/01-table-driven-mocking.md) |
| Project Layout, Tooling, Testing | When the team starts standardizing the new codebase | Correct error/concurrency must be accompanied by correct workflow | [→ 04-project-layout-tooling](./04-project-layout-tooling-testing.md) |
| Go Concurrency Overview | When you want to go deeper into goroutine/channel patterns | Next step after TS-to-Go mapping | [→ Concurrency README](../../concurrency/README.md) |

**Navigation**: [← Previous](./02-types-data-modeling.md) · [→ Next](./04-project-layout-tooling-testing.md)
