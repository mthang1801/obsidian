<!-- tags: golang, concurrency, goroutines, overview -->
# Go Concurrency — Overview & Guide

> Router for the `concurrency` lane: use it to choose between primitives, shared-state safety, cancellation, pipelines, and production helpers.

📅 Updated: 2026-04-19 · ⏱️ 7 min read

## 1. DEFINE

This lane does not teach "just use goroutines." It teaches how to decide between channels, mutexes, context, pipelines, semaphores, worker pools, and queue helpers based on the system's actual workload.

Most Go production bugs do not come from syntax. They come from picking the wrong primitive for the coordination problem: using a channel to protect shared state, using a mutex to model ownership transfer, or forgetting the shutdown path so goroutine leaks accumulate silently.

### 1.1 Signals & Boundaries

- Open this hub when symptoms involve races, deadlocks, blocked goroutines, leaks, backpressure, or bounded concurrency.
- This is a router hub for the `concurrency` lane, not a replacement for detailed articles.
- A sensible reading order is primitives first, orchestration and libraries second.

### 1.2 Learning Lanes

- `01-goroutines-and-channels.md` is the default entry point when you need to reset your mental model of execution and communication.
- `02-mutex-and-race-condition.md` is the right entry when shared memory is the real problem.
- `03-context.md` should open early if code involves HTTP, RPC, background jobs, or a cancellation tree.
- `07-pipeline.md` and the orchestration articles should open only after ownership and shutdown are clear.

## 2. VISUAL

This hub becomes useful only when the visual separates concurrency "jobs" from each other instead of lumping everything under the keyword `goroutine`.

![Concurrency learning lanes](./images/concurrency-router-map.png)

*Each lane in `concurrency` carries a different kind of decision: primitives, shared-state safety, cancellation, orchestration, and production helpers.*

When you look through this router, you will see why "channel vs mutex" is not a philosophical debate. It is choosing a tool based on the type of ownership problem.

## 3. CODE

The visual has divided the lanes. The artifact below compresses that routing logic into a very short router.

### Example 1: Router artifact — choose a concurrency topic by symptom

> **Goal**: Pick the right starting article in the `concurrency` lane.
> **Approach**: Map symptom to the corresponding primitive or orchestration concern.
> **Example**: Only open library-heavy docs after the foundational primitives are correct.
> **Complexity**: O(1) at the routing level; the hard part is naming the symptom correctly.

```go
func chooseConcurrencyTopic(problem string) string {
	switch problem {
	case "goroutine-basics", "channels", "select":
		return "./01-goroutines-and-channels.md"
	case "shared-state", "race", "rwmutex":
		return "./02-mutex-and-race-condition.md"
	case "cancel", "deadline", "request-lifecycle":
		return "./03-context.md"
	case "stage-pipeline", "backpressure", "shutdown":
		return "./07-pipeline.md"
	case "grouped-errors":
		return "./05-errgroup.md"
	case "bounded-concurrency":
		return "./10-semaphore.md"
	default:
		return "./README.md"
	}
}
```

If this router makes you hesitate between two branches, that is usually a sign you are mixing two different coordination jobs in the same design.

## 4. PITFALLS

| # | Severity | Mistake | Consequence | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Fatal | Learning library helpers before understanding primitives | Knowing tool names without understanding failure modes | Start from `01`, `02`, `03` first |
| 2 | 🟡 Common | Turning "channel vs mutex" into a religious debate | Choosing the wrong primitive for the wrong problem | Ask whether the real job is handoff or shared-state protection |
| 3 | 🟡 Common | Focusing only on the happy path, forgetting the shutdown path | Goroutine leaks, queue buildup, deadlocks | Always read ownership and cancellation in parallel |
| 4 | 🔵 Minor | Using the hub as a static link list | Missing how lanes connect to each other | Use the router map to pick a starting article |

## 5. REF

| Resource | Type | Link | Notes |
| --- | --- | --- | --- |
| Go Concurrency Patterns | Official blog | https://go.dev/blog/pipelines | Foundational article on pipelines, cancellation, and coordination |
| Share Memory By Communicating | Official blog | https://go.dev/blog/codelab-share | Go's channel-first philosophy |
| Effective Go | Official docs | https://go.dev/doc/effective_go | Core guidelines for goroutines, channels, and errors |
| The Go Memory Model | Official docs | https://go.dev/ref/mem | When you need to connect concurrency with visibility guarantees |

## 6. RECOMMEND

After this hub, continue along the specific coordination problem you are solving.

| Next step | When to read | Reason | File/Link |
| --- | --- | --- | --- |
| 01 — Goroutines & Channels | When you need a baseline for execution and communication | Lock down goroutine lifecycle, buffering, and select | [01-goroutines-and-channels.md](./01-goroutines-and-channels.md) |
| 02 — Mutex & Race Condition | When shared memory is the real problem | Separate lock boundaries from ownership transfer | [02-mutex-and-race-condition.md](./02-mutex-and-race-condition.md) |
| 03 — Context | When request lifecycle and cancellation are the main concern | Pull concurrency into service/runtime reality | [03-context.md](./03-context.md) |
| 07 — Pipeline Pattern | When work flows through multiple stages | Connect primitives to orchestration and shutdown | [07-pipeline.md](./07-pipeline.md) |
| Go Programming | When you need to switch clusters away from `concurrency` | Return to the root hub to choose another lane | [../README.md](../README.md) |
