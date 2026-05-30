<!-- tags: golang, testing -->
# 🏋️ Benchmark & Fuzz Testing — Go Testing Beyond Unit Tests

> Go ships built-in benchmarks (`b.N`, `b.Loop()`) and fuzzing (`f.Fuzz()`) — no external libraries needed.

📅 Created: 2026-03-23 · 🔄 Updated: 2026-04-19 · ⏱️ 12 min read

| Aspect | Detail |
| --- | --- |
| **Concept** | Benchmark, alloc measurement, fuzzing, corpus-driven input mutation |
| **Use case** | Performance, regression detection, parser hardening, unexpected input discovery |
| **Key insight** | Correctness test is not enough; New benchmarks and fuzz expose performance and input edge case |
| **Go stdlib** | `testing`, `cmp`, `bytes`, `context` |

| TS/Jest                | Go testing                                   |
| ---------------------- | -------------------------------------------- |
| `jest-bench`           | `func BenchmarkX(b *testing.B)` (built-in)   |
| Property-based testing | `func FuzzX(f *testing.F)` (built-in, 1.18+) |
| `performance.now()`    | `b.ResetTimer()`, `b.StopTimer()`            |

---

## 1. DEFINE

"Optimize this — it's slow." You measure with `time.Now()` before and after — results fluctuate by ±40%. Go has `testing.B` built in. It benchmarks properly without third-party libraries, but the compiler can optimize away your target function if you are not careful.

> *"Why is my API slow?" Log shows p99 latency at 800ms. Unit tests pass. Nothing looks broken. The problem: unit tests only check **correctness**, not **performance**. You add a benchmark first.*
>
> *Go has a built-in benchmark framework — no libraries needed. `BenchmarkXxx(b *testing.B)` runs the function `b.N` times (the runtime adjusts `N` for stability). `b.ReportAllocs()` reports memory usage. `benchstat` compares two runs to detect regressions. Fuzzing (Go 1.18+) covers the next layer: input robustness.*

### Benchmark vs Unit Test vs Fuzz

| Technique       | Purpose | When to run? | Output                          |
| --------------- | ------------------- | ----------------------------- | ------------------------------- |
| **Unit test**   | Correctness         | `go test`                     | Pass / Fail                     |
| **Benchmark**   | Performance (ns/op) | `go test -bench .`            | ns/op, B/op, allocs/op          |
| **Fuzz test**   | Edge cases / crash  | `go test -fuzz=FuzzXxx`       | Crash input if a bug is found |
| **Example**     | Documentation       | `go test`                     | Output match / Fail             |

**Why `b.Loop()` instead of `for i := 0; i < b.N; i++`?** `b.Loop()` (Go 1.24+) handles timer reset and `b.N` adjustment internally — no manual `b.ResetTimer()` needed. Cleaner, less error-prone. `for i := range b.N` (Go 1.22+) is a better intermediate, but `b.Loop()` is the preferred form going forward.

### Fuzz: Find bugs you didn't think of.

Fuzz testing is based on **property testing**: instead of asserting specific results, you assert **invariants** — properties that must always be true for all inputs:

| Property         | For example |
| ---------------- | ---------------------------------------------- |
| Round-trip       | `decode(encode(x)) == x`                       |
| Idempotency      | `f(f(x)) == f(x)`                              |
| No crash         | Function does not panic with any input |
| Length preserved | `len(transform(s)) == len(s)`                  |

**Why is fuzz more effective than manual test cases?** Developers write cases based on what they expect. The fuzzer generates random inputs and mutations from the seed corpus — it finds edge cases you never imagined. `FuzzReverse` has caught Unicode bugs that no hand-written test covered.

Benchmark vs fuzz vs unit — enough theory. Let's see how the testing pyramid and benchmark workflow looks visually.

---
## 2. VISUAL

Benchmarks and fuzz tests are often grouped under "advanced testing." The taxonomy card below separates them by purpose, so you do not confuse benchmark (performance) with fuzz (robustness) or unit test (correctness).

![Benchmark fuzz taxonomy](./images/02-benchmark-fuzz-taxonomy.png)

*Figure: Taxonomy card places unit tests, benchmarks, fuzz tests, and comparison tools as four different layers within the same confidence system: correctness, performance, robustness, and statistical judgment.*

Once the taxonomy is clear, the code below will feel less like a tool tour. Each example will answer “what type of risk is being controlled?” before talking about specific flags or commands.

## 3. CODE

With **Benchmark & Fuzz Testing — Go Testing Beyond Unit Tests**, we have a mental model of performance and robustness testing. Now we anchor it in code to see how each choice — sub-benchmark, allocation tracking, fuzz corpus — changes the test output and confidence level.

### Example 1: Basic — Benchmarks.
> **Objective**: Measure function performance with built-in benchmarks, allocation tracking, and sub-benchmarks.
> **Approach**: Start with a simple benchmark, then add setup exclusion and parameterized sub-benchmarks.
> **Example**: String concatenation via `+` vs `strings.Builder` — sub-benchmarks reveal the allocation difference.
> **Complexity**: O(1) per operation; the benchmark loop scales `b.N` automatically.

```go
package utils_test

import "testing"

// ━━━━━ Basic benchmark ━━━━━

func BenchmarkStringConcat(b *testing.B) {
	for b.Loop() { // Go 1.24+ — preferred
		_ = "hello" + " " + "world"
	}
}

func BenchmarkStringBuilder(b *testing.B) {
	for b.Loop() {
		var sb strings.Builder
		sb.WriteString("hello")
		sb.WriteString(" ")
		sb.WriteString("world")
		_ = sb.String()
	}
}

// ━━━━━ With setup (excluded from timing) ━━━━━

func BenchmarkDBQuery(b *testing.B) {
	db := setupTestDB() // setup — not timed
	b.ResetTimer()       // ✅ start timing from here

for b.Loop() {
		var users []User
		db.Find(&users)
	}
}

// ━━━━━ Sub-benchmarks (like table-driven tests) ━━━━━

func BenchmarkSort(b *testing.B) {
	sizes := []int{100, 1000, 10000}
	for _, size := range sizes {
		b.Run(fmt.Sprintf("size=%d", size), func(b *testing.B) {
			data := generateSlice(size)
			b.ResetTimer()
			for b.Loop() {
				slices.Sort(slices.Clone(data))
			}
		})
	}
}

// ━━━━━ Memory allocation tracking ━━━━━

func BenchmarkAllocs(b *testing.B) {
	b.ReportAllocs() // ✅ report allocs/op
	for b.Loop() {
		_ = fmt.Sprintf("user-%d", 42)
	}
}

// Run: go test -bench=. -benchmem -count=5
// Output:
// BenchmarkStringConcat-20    50000000   25.3 ns/op   48 B/op   2 allocs/op
// BenchmarkStringBuilder-20   80000000   18.1 ns/op   64 B/op   2 allocs/op
```

> **Why is `b.ReportAllocs()` important?**
> `ns/op` only measures time — not memory pressure. A function of 10ns but 3 allocs/op will create GC pressure at scale. `b.ReportAllocs()` report `B/op` (bytes) and `allocs/op` — helps detect hidden allocations in hot paths.

> **Conclusion**: `b.Loop()` (Go 1.24+) replaces `for i := 0; i < b.N; i++`. Sub-benchmarks enable parameterized testing (size=100, size=1000). `-benchmem` or `b.ReportAllocs()` tracks allocation cost.

Benchmark cover performance measurement. But benchmarks only test cases you come up with. Fuzz testing finds bugs you didn't think of — by generating random inputs from the seed corpus.

### Example 2: Intermediate — Fuzz Testing (Go 1.18+).
> **Objective**: Find edge cases and crashes with fuzz testing — property-based assertions on random inputs.
> **Approach**: Define a seed corpus, then assert invariants (round-trip, length preservation, no panic).
> **Example**: `FuzzReverse` verifies that double-reversing a string returns the original. `FuzzJSONParse` verifies that successful parse implies successful re-marshal.
> **Complexity**: O(1) per iteration; the fuzzer generates thousands of inputs from the seed corpus.

```go
package utils_test

import (
	"testing"
	"unicode/utf8"
)

// ━━━━━ Basic fuzz test ━━━━━

func FuzzReverse(f *testing.F) {
	// Seed corpus — starting inputs
	f.Add("hello")
	f.Add("世界")
	f.Add("")
	f.Add("!@#$%")

// ✅ Fuzz function — Go generates random inputs
	f.Fuzz(func(t *testing.T, input string) {
		result := Reverse(input)

// Property 1: double-reverse = original
		if Reverse(result) != input {
			t.Errorf("double reverse failed: %q", input)
		}

// Property 2: same length
		if utf8.RuneCountInString(result) != utf8.RuneCountInString(input) {
			t.Errorf("length mismatch: %q → %q", input, result)
		}
	})
}

// Run:
// go test -fuzz=FuzzReverse -fuzztime=30s

// ━━━━━ Fuzz JSON parsing ━━━━━

func FuzzJSONParse(f *testing.F) {
	f.Add([]byte(`{"name":"alice"}`))
	f.Add([]byte(`{}`))
	f.Add([]byte(`null`))

f.Fuzz(func(t *testing.T, data []byte) {
		var result map[string]any
		err := json.Unmarshal(data, &result)

if err == nil {
			// If parse succeeds, re-marshal must also succeed
			_, err2 := json.Marshal(result)
			if err2 != nil {
				t.Errorf("marshal failed after unmarshal: %v", err2)
			}
		}
		// If err != nil, input is invalid JSON — that's OK
	})
}
```

> **Why property-based instead of result-based assertions?**
> The fuzzer generates random inputs — you do not know the input beforehand, so you cannot assert specific results. Instead, assert **invariants**: `decode(encode(x)) == x`, `len(transform(s)) == len(s)`, or simply "does not panic". Properties must hold for all inputs.

> **Conclusion**: Fuzz seed corpus provides starting points. The Go fuzzer mutates from seed inputs to find crashes. Results are stored in `testdata/fuzz/` — commit them to the repo for CI reproduction. `-fuzztime=30s` limits CI runtime.

Benchmark and fuzz cover measurement and robustness. But one benchmark run is not enough — results have variance from CPU throttling, GC timing, and OS scheduling. You need multiple runs and statistical comparison. That is where `benchstat` enters.

### Example 3: Advanced — Comparing Benchmark Results.
> **Objective**: Compare benchmark results across code changes with statistical significance.
> **Approach**: Run benchmarks with `-count=10`, save results, make changes, re-run, and compare with `benchstat`.
> **Example**: `benchstat old.txt new.txt` shows a 28% improvement in `StringConcat` with a p-value below 0.05.
> **Complexity**: O(1) per comparison; `benchstat` handles the statistics.

```bash
# Install benchstat
go install golang.org/x/perf/cmd/benchstat@latest

# Run benchmarks, save results
go test -bench=. -count=10 > old.txt

# Make changes, re-run
go test -bench=. -count=10 > new.txt

# Compare
benchstat old.txt new.txt
# Output:
# name           old time/op  new time/op  delta
# StringConcat   25.3ns       18.1ns       -28.46%
```

> **Why `-count=10` when comparing benchmarks?**
> Benchmark results have variance from CPU throttling, GC timing, and OS scheduling. `-count=10` runs 10 times — `benchstat` calculates the mean and confidence interval. If `p < 0.05`, the change is a real regression or improvement, not noise.

> **Conclusion**: `benchstat` compares benchmark runs with statistical significance. Use it in CI: baseline branch vs PR branch. `-count≥5` gives a reliable comparison.

You now know benchmark, fuzz, and `benchstat`. The most dangerous part remains: the compiler can optimize away benchmark results — the trap seeded at the beginning of this article that produces meaningless `0 ns/op` output.

---

## 4. PITFALLS

The mechanics of **Benchmark & Fuzz Testing** are clear. What remains is recognizing the spots where almost-correct code produces misleading benchmark results.

| # | Severity | Error | Consequence | Fix |
|---|----------|-----|---------|-----|
| 1 | 🔴 Fatal | Compiler optimizes away result | `0 ns/op` — meaningless benchmark | Assign result to `var sink T` package-level |
| 2 | 🟡 Common | Setup included in benchmark | Measure setup time instead of target code | `b.ResetTimer()` after setup, or `b.StopTimer()`/`b.StartTimer()` |
| 3 | 🟡 Common | Fuzz runs forever in CI | CI pipeline timeout/hang | `-fuzztime=30s` limit time, `-fuzzminimizetime=10s` |
| 4 | 🟡 Common | `for i := 0; i < b.N; i++` (old style) | Timer issues, verbose | `for b.Loop()` (Go 1.24+) or `for range b.N` (Go 1.22+) |
| 5 | 🔵 Minor | Benchmark does not use `-count` | Single run = unreliable data | `-count=5` minimum, `benchstat` for comparison |

### 🔴 Pitfall #1 — Compiler optimizes away benchmark

The Go compiler finds the result unused and eliminates the function call entirely — `0 ns/op`. The fix: assign the result to a package-level `var sink T`. The compiler cannot optimize it away because the variable is visible outside the function scope.

```go
var sink int // package-level
func BenchmarkFib(b *testing.B) {
    for b.Loop() {
        sink = Fib(20) // compiler keeps it because sink is package-level
    }
}
```

You've gone through benchmark, fuzz, benchstat, and compiler optimization traps. The resources below help go deeper.

---

## 5. REF

| Resource      | Type | Link                                                                                             | Note |
| ------------- | -------- | ------------------------------------------------------------------------------------------------ | ------- |
| Go Benchmarks | Official | [pkg.go.dev/testing#hdr-Benchmarks](https://pkg.go.dev/testing#hdr-Benchmarks)                   | Built-in benchmark API |
| Go Fuzzing    | Official | [go.dev/doc/security/fuzz](https://go.dev/doc/security/fuzz/)                                    | Fuzz testing guide (Go 1.18+) |
| benchstat     | Tool     | [pkg.go.dev/golang.org/x/perf/cmd/benchstat](https://pkg.go.dev/golang.org/x/perf/cmd/benchstat) | Statistical benchmark comparison |
| b.Loop() proposal | Official | [go.dev/blog/benchmarkloop](https://go.dev/blog/benchmarkloop) | Go 1.24 benchmark loop |

---

## 6. RECOMMEND

The core of **Benchmark & Fuzz Testing** is clear. The branches below extend performance testing into production with profiling, property-based testing, and regression detection.

| Extend | When | Reason | File/Link |
| ------- | ------- | ----- | --------- |
| pprof profiling | After benchmark identifies slow function | Line-by-line allocation + CPU analysis | [../../advanced/05-performance-pprof.md](../../advanced/05-performance-pprof.md) |
| Integration tests | Test real DB/Redis/Kafka | Beyond unit + benchmark — real dependencies | [03-integration-testcontainers.md](./03-integration-testcontainers.md) |
| Property-based testing | Complex business logic | Complement fuzz with hypothesis-style properties | [github.com/flyingmutant/rapid](https://github.com/flyingmutant/rapid) |
| CI benchmark regression | PR performance gates | Auto-detect performance regressions | `benchstat` in GitHub Actions |

---

**Navigation**: [← Table-driven Tests](./01-table-driven-mocking.md) · [→ Integration Tests](./03-integration-testcontainers.md)
