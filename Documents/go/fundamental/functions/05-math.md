<!-- tags: golang -->
# 🔢 Math — Numeric Functions & Constants

> Package `math` provides fundamental mathematical functions: abs, min/max, round, sqrt, pow, trigonometry — and critical constants like Pi and MaxInt.

📅 Created: 2026-03-23 · 🔄 Updated: 2026-04-19 · ⏱️ 16 min read

| Aspect         | Detail                                        |
| -------------- | --------------------------------------------- |
| **Package**    | `math`, `math/rand/v2`, `math/big`            |
| **Use case**   | Arithmetic, random numbers, arbitrary precision |
| **Input type** | `float64` (mostly), `int` (min/max Go 1.21+)  |
| **Key rule**   | Always check NaN/Inf when working with floats  |

---

## 1. DEFINE

> *You are calculating shipping fees based on distance. Or rounding prices for an invoice. Or implementing a clustering algorithm that needs Euclidean distance. Or generating unpredictable random test data. All of these require `math` — Go's standard library includes `math`, `math/rand/v2`, and `math/big`.*
>
> *The first thing to know: most functions in `math` accept and return `float64`. This is why you cannot call `math.Sqrt(25)` with an `int` — you must cast: `math.Sqrt(float64(25))`. Go 1.21 added built-in `min`/`max` for any comparable type — reducing boilerplate significantly. And `math/rand/v2` (Go 1.22+) completely replaces the old `math/rand` with a simpler API and a cryptographically stronger default source.*

### Function Families

The `math` package is organized into **6 functional groups** — each addressing a different domain:

| Family         | Functions                                                |
| -------------- | -------------------------------------------------------- |
| **Basic**      | `Abs`, `Max`, `Min`, `Ceil`, `Floor`, `Round`            |
| **Power/Root** | `Pow`, `Sqrt`, `Cbrt`, `Exp`, `Log`, `Log2`, `Log10`     |
| **Trig**       | `Sin`, `Cos`, `Tan`, `Asin`, `Acos`, `Atan`, `Atan2`     |
| **Special**    | `IsNaN`, `IsInf`, `NaN`, `Inf`, `Mod`, `Remainder`       |
| **Bit**        | `math/bits` — `OnesCount`, `Len`, `LeadingZeros`         |
| **Random**     | `math/rand/v2` — `IntN`, `Float64`, `N[T]`               |
| **Big**        | `math/big` — `Int`, `Float`, `Rat` (arbitrary precision) |

**Why `math/rand/v2` instead of `math/rand`?** The old package has global state, is not thread-safe without manual seeding, and has a verbose API (`rand.Intn(n)` vs v2's `rand.IntN(n)`). v2 uses the `ChaCha8` PRNG by default — faster, better distribution, and no manual seeding required.

### Important Constants

| Constant                      | Value / Description                  |
| ----------------------------- | ------------------------------------ |
| `math.Pi`                     | 3.14159265358979...                  |
| `math.E`                      | 2.71828182845904... (Euler's number) |
| `math.MaxInt`                 | Max value of `int`                   |
| `math.MinInt`                 | Min value of `int`                   |
| `math.MaxFloat64`             | 1.7976931348623157e+308              |
| `math.SmallestNonzeroFloat64` | 5e-324                               |
| `math.MaxInt64`               | 9223372036854775807                  |

### Built-in min/max (Go 1.21+)

```text
Go < 1.21:  math.Max(float64, float64) float64  ← float64 only
Go >= 1.21: min(x, y)  /  max(x, y)             ← built-in, any comparable type
```

**Why did it take until Go 1.21?** Built-in generic functions required generics (Go 1.18+) and additional time to generalize the type system. Before that, you had to write type-specific helpers or use `math.Max` with float64.

---

These math functions look standard — but dangerous traps exist: float64 comparison with `==` fails due to precision loss, and integer overflow wraps around silently. Those traps surface in PITFALLS.

## 2. VISUAL

With `math`, the issue is not that the package lacks organization. The issue is that you easily lump all numeric functions into one mental bucket and forget that each group answers a fundamentally different type of question. The visual below separates those families first.

![Math taxonomy](./images/05-math-taxonomy.png)

*Figure: Taxonomy card for the `math` lane dividing the package by problem family: rounding surface, math core, constants and numeric limits, plus extensions like random, big numbers, and bit helpers.*

Once the problem family is clear, the code below reveals the details worth focusing on: how negative numbers change rounding behavior, where precision loss appears, and when you must leave `math` for `math/big` or `math/bits`.

## 3. CODE

With **Math — Numeric Functions & Constants**, we now have the map of numeric operations. Let's step into the code to see how each choice — `math.Round` vs manual truncation, `math/rand` vs `crypto/rand` — actually changes precision and security.

### Example 1: Basic — Math Functions & Constants

You are calculating the Euclidean distance between 2 points: `d = √((x₂-x₁)² + (y₂-y₁)²)`. You need `math.Sqrt`, `math.Pow`. Calculating the circumference of a circle: `C = 2πr` — hardcode `3.14159`? Use `math.Pi` instead — it is accurate to 15+ digits.

Package `math` provides constants (`Pi`, `E`, `MaxFloat64`) and functions (`Abs`, `Ceil`, `Floor`, `Round`) for all fundamental arithmetic needs.

Input: `math.Sqrt(16)` · Output: `4` · `math.Pi` · Output: `3.141592653589793`

```go
package main

import (
	"fmt"
	"math"
)

func main() {
	// ━━━━━ Constants ━━━━━
	fmt.Printf("Pi:       %.10f\n", math.Pi)         // 3.1415926536
	fmt.Printf("E:        %.10f\n", math.E)          // 2.7182818285
	fmt.Printf("MaxInt64: %d\n", math.MaxInt64)       // 9223372036854775807

	// ━━━━━ Abs ━━━━━
	fmt.Println(math.Abs(-42.5))                       // 42.5

	// ✅ Go 1.21+ built-in min/max (works with int, float, string)
	fmt.Println(min(3, 7))                    // 3
	fmt.Println(max(3, 7))                    // 7
	fmt.Println(min("apple", "banana"))       // "apple"

	// ━━━━━ Rounding ━━━━━
	x := 2.7
	fmt.Println(math.Floor(x))                         // 2
	fmt.Println(math.Ceil(x))                          // 3
	fmt.Println(math.Round(x))                         // 3
	fmt.Println(math.Trunc(x))                         // 2

	// ✅ Round to N decimal places
	price := 19.456
	rounded := math.Round(price*100) / 100
	fmt.Printf("%.2f\n", rounded)                      // 19.46

	// ━━━━━ Power & Root ━━━━━
	fmt.Println(math.Pow(2, 10))                       // 1024
	fmt.Println(math.Sqrt(144))                        // 12
	fmt.Println(math.Cbrt(27))                         // 3
	fmt.Println(math.Log(math.E))                      // 1
	fmt.Println(math.Log2(1024))                       // 10
	fmt.Println(math.Log10(1000))                      // 3

	// ━━━━━ Mod & Remainder ━━━━━
	fmt.Println(math.Mod(10, 3))                       // 1
	fmt.Println(math.Remainder(10, 3))                 // 1

	// ━━━━━ Special values ━━━━━
	fmt.Println(math.IsNaN(math.NaN()))                // true
	fmt.Println(math.IsInf(math.Inf(1), 1))            // true (positive infinity)
	fmt.Println(math.IsInf(math.Inf(-1), -1))          // true (negative infinity)
}
```

> Go designers decided against function overloading. `Abs` for `int` is trivial: `if n < 0 { n = -n }`. Go 1.21+ has built-in `min`/`max` for any comparable type — but there is still no built-in generic `Abs`. Rounding to N decimal places: `math.Round(x*100)/100` — the multiply-then-divide trick.

> **Takeaway**: `math.Pi`, `math.E` for constants. Built-in `min`/`max` (Go 1.21+) replaces `math.Max/Min`. `math.Round(x*N)/N` for N decimal places. Always check `IsNaN`/`IsInf` after float operations.

Math basics are covered. But floating-point arithmetic has precision traps that many developers overlook.

### Example 2: Intermediate — Random Numbers (math/rand/v2)

You need to generate a random token for session IDs, a random port for testing, or shuffle a playlist. Go 1.22+ provides `math/rand/v2` with a cleaner API and auto-seeding (no more `rand.Seed()` like v1). But `math/rand` is not cryptographically secure — fine for game logic, but for security tokens you must use `crypto/rand`.

Input: `rand.IntN(100)` · Output: random int in `[0, 100)` · `rand.Float64()` · Output: random float in `[0, 1)`

```go
package main

import (
	"fmt"
	"math/rand/v2"
)

func main() {
	// ━━━━━ math/rand/v2 (Go 1.22+) ━━━━━
	// ✅ Automatically seeded, no need for rand.Seed()

	// Random int [0, n)
	fmt.Println(rand.IntN(100))          // random 0-99

	// Random float [0.0, 1.0)
	fmt.Println(rand.Float64())          // random 0.0-0.999...

	// ✅ Generic N[T] — works with any integer type
	var n int32 = rand.N[int32](1000)
	fmt.Println(n)                        // random int32 0-999

	// ━━━━━ Random in range [min, max] ━━━━━
	randomInRange := func(min, max int) int {
		return rand.IntN(max-min+1) + min
	}
	fmt.Println(randomInRange(1, 6))     // dice roll: 1-6

	// ━━━━━ Random element from slice ━━━━━
	colors := []string{"red", "green", "blue", "yellow"}
	randomColor := colors[rand.IntN(len(colors))]
	fmt.Println("Random color:", randomColor)

	// ━━━━━ Shuffle slice ━━━━━
	deck := []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
	rand.Shuffle(len(deck), func(i, j int) {
		deck[i], deck[j] = deck[j], deck[i]
	})
	fmt.Println("Shuffled:", deck)

	// ━━━━━ Random string ━━━━━
	const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	randomString := func(length int) string {
		b := make([]byte, length)
		for i := range b {
			b[i] = charset[rand.IntN(len(charset))]
		}
		return string(b)
	}
	fmt.Println("Random ID:", randomString(8))
}
```

> The old package: global state, manual `rand.Seed()`, verbose API (`Intn` vs `IntN`). v2 uses `ChaCha8` PRNG — auto-seeded, thread-safe, better distribution. Generic `rand.N[T]()` for type-safe random. `Shuffle` uses Fisher-Yates — O(n) in-place.

> **Takeaway**: `rand.IntN(n)` for [0,n), `rand.Float64()` for [0,1). `Shuffle` to randomize slices. Random string: build from charset with `IntN(len(charset))`.

Float precision is covered. Next: `math/big` for arbitrary precision, `crypto/rand` for secure random, and overflow-safe arithmetic.

### Example 3: Advanced — Geometry, Statistics & Big Numbers

Computing Fibonacci(200)? `int64` overflows at Fibonacci(93). Calculating compound interest over 500 periods? `float64` loses precision. Package `math/big` solves this: `big.Int` for integers of unlimited size, `big.Float` for arbitrary precision arithmetic.

Combined with geometry (distance, area) and statistics (mean, standard deviation) to show the `math` package in production context.

Input: `big.NewInt(0).Fib(200)` · Output: a 42-digit number, no overflow

```go
package main

import (
	"fmt"
	"math"
	"math/big"
	"sort"
)

// ━━━━━ Geometry functions ━━━━━

func distance(x1, y1, x2, y2 float64) float64 {
	return math.Hypot(x2-x1, y2-y1) // ✅ Hypot = sqrt(x² + y²) — numerically stable
}

func degToRad(deg float64) float64 {
	return deg * math.Pi / 180
}

func radToDeg(rad float64) float64 {
	return rad * 180 / math.Pi
}

// ━━━━━ Statistics ━━━━━

func mean(nums []float64) float64 {
	sum := 0.0
	for _, n := range nums {
		sum += n
	}
	return sum / float64(len(nums))
}

func median(nums []float64) float64 {
	sorted := make([]float64, len(nums))
	copy(sorted, nums)
	sort.Float64s(sorted)

	n := len(sorted)
	if n%2 == 0 {
		return (sorted[n/2-1] + sorted[n/2]) / 2
	}
	return sorted[n/2]
}

func stddev(nums []float64) float64 {
	avg := mean(nums)
	sumSq := 0.0
	for _, n := range nums {
		diff := n - avg
		sumSq += diff * diff
	}
	return math.Sqrt(sumSq / float64(len(nums)))
}

func main() {
	// ━━━━━ Geometry ━━━━━
	d := distance(0, 0, 3, 4)
	fmt.Printf("Distance: %.2f\n", d) // 5.00

	angle := math.Atan2(4, 3)
	fmt.Printf("Angle: %.2f rad = %.2f deg\n", angle, radToDeg(angle))

	// ━━━━━ Statistics ━━━━━
	data := []float64{4, 8, 15, 16, 23, 42}
	fmt.Printf("Mean:   %.2f\n", mean(data))
	fmt.Printf("Median: %.2f\n", median(data))
	fmt.Printf("StdDev: %.2f\n", stddev(data))

	// ━━━━━ math/big — Arbitrary precision ━━━━━
	// ✅ Compute Fibonacci(100) — exceeds int64 range
	a := big.NewInt(0)
	b := big.NewInt(1)
	for i := range 100 { // Go 1.22+
		a.Add(a, b)
		a, b = b, a
	}
	fmt.Printf("Fibonacci(100) = %s\n", a.String())
	// 354224848179261915075

	// ✅ Big factorial
	factorial := big.NewInt(1)
	for i := int64(1); i <= 50; i++ {
		factorial.Mul(factorial, big.NewInt(i))
	}
	fmt.Printf("50! = %s\n", factorial.String())
}
```

> **Why use `math.Hypot` instead of manual `sqrt(x²+y²)`?**
> `Hypot` handles overflow/underflow in a numerically stable way — when `x` or `y` is extremely large or small, the manual formula can overflow at `x²`. `Hypot` normalizes before computing. Statistics functions (mean/median/stddev) are building blocks — Go's stdlib does not include them; you must implement them yourself or use `gonum`.

> **Takeaway**: `math/big` for arbitrary precision (beyond int64/float64). `math.Hypot` for numerically stable distance. Statistics require manual implementation or an external library.

---

## 4. PITFALLS

The core mechanics of **Math — Numeric Functions & Constants** are clear. What remains is recognizing syntax that looks _almost right_ but introduces floating-point bugs or security issues into production.

| # | Severity | Bug | Consequence | Fix |
|---|----------|-----|-------------|-----|
| 1 | 🔴 Fatal | NaN comparison: `NaN != NaN` | Condition is always false | Use `math.IsNaN()` |
| 2 | 🔴 Fatal | Integer overflow does not error | Silent wrong value | Check: `if a > math.MaxInt64 - b` |
| 3 | 🟡 Common | Float precision: `0.1 + 0.2 != 0.3` | Logic error in comparisons | Epsilon: `math.Abs(a-b) < 1e-9` |
| 4 | 🟡 Common | `math.Max/Min` only accepts float64 (pre Go 1.21) | Type conversion overhead | Built-in `min()`/`max()` Go 1.21+ |
| 5 | 🔵 Minor | `rand.IntN(0)` panics | Runtime crash | Check `n > 0` before calling |

### 🔴 Pitfall #1 — NaN is a "virus" in your code

`NaN` (Not a Number) is a special value: **every comparison with NaN returns false**, including `NaN == NaN`. Once NaN appears in a computation pipeline, it propagates through every operation: `NaN + 5 = NaN`, `NaN * 0 = NaN`. The result: a report displays `NaN` for the revenue column and nobody knows when it started going wrong.

**Fix**: Check `math.IsNaN()` after every float division. Especially note that `0.0 / 0.0 = NaN` (it does not panic like integer division by zero).

### 🔴 Pitfall #2 — Integer overflow is silent

Go does not panic on integer overflow — it **wraps around** using modular arithmetic. `math.MaxInt64 + 1` equals `math.MinInt64` (a negative number!). In financial calculations, this turns `+$9.2 quintillion` into `-$9.2 quintillion` with no error whatsoever.

**Fix**: Check before adding: `if a > math.MaxInt64 - b { /* overflow */ }`. Or use `math/big` for numbers exceeding the range.

---

You have explored the math package from basics through arbitrary precision. The resources below go deeper.

## 5. REF

| Resource       | Type     | Link                                                       | Notes |
| -------------- | -------- | ---------------------------------------------------------- | ----- |
| `math` package | Official | [pkg.go.dev/math](https://pkg.go.dev/math)                 | API reference |
| `math/rand/v2` | Official | [pkg.go.dev/math/rand/v2](https://pkg.go.dev/math/rand/v2) | Go 1.22+ random |
| `math/big`     | Official | [pkg.go.dev/math/big](https://pkg.go.dev/math/big)         | Arbitrary precision |
| `math/bits`    | Official | [pkg.go.dev/math/bits](https://pkg.go.dev/math/bits)       | Bit manipulation |

---

## 6. RECOMMEND

The foundations of **Math — Numeric Functions & Constants** are clear. The extensions below help you bring numeric operations into production with crypto-safe random, big numbers, and scientific computing.

| Extension                 | When                     | Why                             | File/Link |
| ------------------------- | ------------------------ | ------------------------------- | --------- |
| `math/bits`               | Bit manipulation         | OnesCount, Len, RotateLeft      | [pkg.go.dev/math/bits](https://pkg.go.dev/math/bits) |
| `crypto/rand`             | Security-critical random | Cryptographic random numbers    | [pkg.go.dev/crypto/rand](https://pkg.go.dev/crypto/rand) |
| `gonum.org/v1/gonum`      | Scientific computing     | Linear algebra, statistics, FFT | [gonum.org](https://gonum.org) |
| `math/cmplx`              | Complex numbers          | Mandelbrot, signal processing   | [pkg.go.dev/math/cmplx](https://pkg.go.dev/math/cmplx) |
| `constraints` generic     | Type-safe math           | Clamp, Abs for any numeric type | [pkg.go.dev/golang.org/x/exp/constraints](https://pkg.go.dev/golang.org/x/exp/constraints) |

---

**Navigation**: [← fmt](./04-fmt.md) · [→ slices & maps](./06-slices-maps.md)
