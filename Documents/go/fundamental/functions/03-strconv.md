<!-- tags: golang -->
# 🔄 Strconv — Type Conversion & Parsing

> Package `strconv` converts between strings and fundamental data types: int, float, bool. This is the most essential parsing and formatting toolkit in Go.

📅 Created: 2026-03-23 · 🔄 Updated: 2026-04-19 · ⏱️ 14 min read

| Aspect        | Detail                                        |
| ------------- | --------------------------------------------- |
| **Package**   | `strconv`                                     |
| **Use case**  | Parse string → number, format number → string |
| **Go stdlib** | `strconv`, `fmt` (alternative)                |
| **Key rule**  | Always handle errors encountered during parsing |

---

## 1. DEFINE

`strconv.Atoi("42")` returns `(42, nil)`. `strconv.Atoi("42.5")` returns `(0, error)`. `strconv.Atoi("")` also returns `(0, error)`. Three distinct outcomes for three seemingly valid inputs — and if you ignore the `error` return, the zero value `0` becomes a silent vector for data corruption.

> *Every piece of data arriving over HTTP is a string. URL parameters: `?page=2&limit=50`. Query strings: `sort=desc`. Form fields: `price=99.9`. Configuration files: `timeout=30`. Even environment variables: `PORT=8080`.*
>
> *To use these values in business logic, you must convert them safely: `page` to `int`, `price` to `float64`, `debug` to `bool`. The `strconv` package handles this — parsing string inputs and formatting data back into strings. Always check errors during parsing, because user input can be `"hello"` when you expect `"42"`.*

### Core Function Families

| Family      | Parse (string → type) | Format (type → string)     |
| ----------- | --------------------- | -------------------------- |
| **Integer** | `Atoi`, `ParseInt`    | `Itoa`, `FormatInt`        |
| **Float**   | `ParseFloat`          | `FormatFloat`              |
| **Bool**    | `ParseBool`           | `FormatBool`               |
| **Quote**   | `Unquote`             | `Quote`, `QuoteRune`       |
| **Append**  | —                     | `AppendInt`, `AppendFloat` |

### Parse vs Format Naming Convention

```text
Parse___()   → string to type  (may fail → returns an error)
Format___()  → type to string  (cannot fail)
Atoi()       → "ASCII to Integer" (idiomatic shortcut for ParseInt)
Itoa()       → "Integer to ASCII" (idiomatic shortcut for FormatInt)
```

---

These conversion functions look simple — but silent traps exist: calling `Atoi` and ignoring the error gives invisible zero-value injection, and float precision can degrade during format/parse round-trips. Those traps are unpacked in PITFALLS.

## 2. VISUAL

The most common mistake with `strconv` is reaching for a familiar helper function by name before locking down the direction of the data transfer. The visual below forces that exact question upfront: is text entering the type system, or is a typed value exiting onto the wire as a string?

![Strconv decision map](./images/03-strconv-decision-map.png)

*Figure: The `strconv` decision map splits the four primary operational directions: parse, format, append for hot paths, and the silent failure modes triggered if errors or precision checks are ignored.*

Once the directional boundary is established, the code blocks below read much more naturally. You no longer view `Atoi`, `ParseInt`, and `FormatFloat` as disconnected APIs, but as distinct gateways operating on the exact same text-to-type boundary.

## 3. CODE

With **Strconv — Type Conversion & Parsing**, we established the map for parse and format mechanics. Now, let's step down into the code to see how choosing `Atoi` over `ParseInt`, or `FormatFloat` over `Sprintf`, directly influences calculation precision and error handling.

### Example 1: Basic — Atoi, Itoa & ParseBool

HTTP query strings are `string`s: `?page=3&limit=50&active=true`. You must convert these to `int` and `bool` for database queries. `fmt.Sscanf`? Too slow and lacks type safety. `strconv.Atoi` and `strconv.ParseBool` are the standard: fast and they return errors on bad input.

Input: `strconv.Atoi("42")` · Output: `(42, nil)` · `strconv.Atoi("abc")` · Output: `(0, error)`

```go
package main

import (
	"fmt"
	"strconv"
)

func main() {
	// ━━━━━ Atoi — string → int ━━━━━
	n, err := strconv.Atoi("42")
	if err != nil {
		fmt.Println("Error:", err)
		return
	}
	fmt.Println(n)           // 42
	fmt.Printf("Type: %T\n", n) // int

	// ⚠️ Fail cleanly when the string is non-numeric
	_, err = strconv.Atoi("hello")
	fmt.Println(err)          // strconv.Atoi: parsing "hello": invalid syntax

	// ⚠️ Fail cleanly on overflow limits
	_, err = strconv.Atoi("99999999999999999999")
	fmt.Println(err)          // strconv.Atoi: parsing "...": value out of range

	// ━━━━━ Itoa — int → string ━━━━━
	s := strconv.Itoa(255)
	fmt.Println(s)            // "255"
	fmt.Printf("Type: %T\n", s) // string

	// ━━━━━ ParseBool ━━━━━
	// ✅ Accepts: "1", "t", "T", "true", "TRUE", "True"
	//             "0", "f", "F", "false", "FALSE", "False"
	b, _ := strconv.ParseBool("true")
	fmt.Println(b)            // true

	b, _ = strconv.ParseBool("0")
	fmt.Println(b)            // false

	// ━━━━━ FormatBool ━━━━━
	fmt.Println(strconv.FormatBool(true))  // "true"
	fmt.Println(strconv.FormatBool(false)) // "false"
}
```

> **Why can `Atoi` overflow on 32-bit systems?**
> `Atoi` returns `int` — its size depends on platform architecture (32-bit vs 64-bit). On a 32-bit device, input exceeding `int32` range → error. For critical boundaries, use `ParseInt` with explicit bit size.

> **Takeaway**: Use `Atoi`/`Itoa` for simple conversions. `ParseBool` accepts variants (`"1"`, `"t"`, `"true"`) — convenient for config parsing. Always check returned errors.

Basic conversions are standard. However, controlling scientific precision limits via `FormatFloat`, combined with distinct base conversions, demands deeper mechanical understanding.

### Example 2: Intermediate — ParseInt, ParseFloat & FormatFloat

A configuration file provides `timeout=30`, `rate=0.75`, and `port=0x1F90` (hexadecimal). `Atoi` only handles base-10. You need `ParseInt` with a base parameter, and `ParseFloat` with explicit bit-size.

`FormatFloat` controls precision: `'f'` (decimal), `'e'` (scientific), `'g'` (compact) — giving control down to individual digits.

Input: `strconv.ParseInt("1F90", 16, 64)` · Output: `(8080, nil)`

```go
package main

import (
	"fmt"
	"strconv"
)

func main() {
	// ━━━━━ ParseInt(s, base, bitSize) ━━━━━
	// base: 2=binary, 8=octal, 10=decimal, 16=hex, 0=auto-detect
	// bitSize: 0/8/16/32/64 — limits acceptable result range capacity

	// Decimal
	i, _ := strconv.ParseInt("123", 10, 64)
	fmt.Println(i)            // 123

	// Hexadecimal
	hex, _ := strconv.ParseInt("FF", 16, 64)
	fmt.Println(hex)          // 255

	// Binary
	bin, _ := strconv.ParseInt("1010", 2, 64)
	fmt.Println(bin)          // 10

	// Auto-detect base via prefix (0)
	// "0x" → hex, "0o" → octal, "0b" → binary, otherwise assumes decimal
	auto, _ := strconv.ParseInt("0xFF", 0, 64)
	fmt.Println(auto)         // 255

	// ━━━━━ ParseUint — handling strictly unsigned values ━━━━━
	u, _ := strconv.ParseUint("42", 10, 64)
	fmt.Println(u)            // 42 (uint64)

	// ━━━━━ FormatInt(i, base) ━━━━━
	fmt.Println(strconv.FormatInt(255, 16))  // "ff"
	fmt.Println(strconv.FormatInt(255, 2))   // "11111111"
	fmt.Println(strconv.FormatInt(255, 8))   // "377"

	// ━━━━━ ParseFloat(s, bitSize) ━━━━━
	f, _ := strconv.ParseFloat("3.14159", 64)
	fmt.Printf("%.2f\n", f)  // 3.14

	// Scientific notation string logic
	sci, _ := strconv.ParseFloat("1.5e3", 64)
	fmt.Println(sci)          // 1500

	// ━━━━━ FormatFloat(f, fmt, prec, bitSize) ━━━━━
	// fmt: 'f'=decimal, 'e'=scientific, 'g'=auto-simplify, 'b'=binary exp
	// prec: specific number of digits succeeding the decimal (-1 = minimum unique required)

	fmt.Println(strconv.FormatFloat(3.14159, 'f', 2, 64))   // "3.14"
	fmt.Println(strconv.FormatFloat(3.14159, 'e', 4, 64))   // "3.1416e+00"
	fmt.Println(strconv.FormatFloat(3.14159, 'g', -1, 64))  // "3.14159"
	fmt.Println(strconv.FormatFloat(100000.0, 'g', -1, 64)) // "100000"
}
```

> **Why does `FormatFloat` require four distinct parameters?**
> Standardizing float architectures is incredibly complex: `fmt` secures formatting intent ('f' vs 'e'), `prec` locks numeric decay constraints (-1 guaranteeing minimum safe readability), and `bitSize` enforces strict mathematical rounding (32-bit floats behave drastically differently than 64-bit layers). Always bind `ParseFloat` to 64-bit architectures universally unless processing heavily optimized `float32` arrays.

> **Takeaway**: `ParseInt` with base=0 auto-detects `0x`, `0o`, `0b` prefixes — useful for config parsing. `FormatFloat` with prec=-1 gives minimal unique output. Use `ParseUint` for unsigned values.

Formatting is covered. Next: specialized parsing, raw byte operations, and quotation handling.

### Example 3: Advanced — Quote, Append & Real-world Patterns

You are building a JSON logging engine that needs safely escaped strings containing quotes `"`, newlines `\n`, and Unicode. `fmt.Sprintf("%q", s)` works but is slow due to format parsing overhead. `strconv.Quote` is ~3x faster, dedicated to ASCII/Unicode string escaping.

The `Append*` functions (`AppendInt`, `AppendFloat`, `AppendBool`) are faster still — they append directly to `[]byte` slices without creating temporary strings.

Input: `strconv.Quote("hello\nworld")` · Output: `"\"hello\\nworld\""`

```go
package main

import (
	"fmt"
	"strconv"
	"strings"
)

func main() {
	// ━━━━━ Quote / Unquote — String security rendering ━━━━━
	// ✅ Safety-escapes embedded quotes and control characters
	fmt.Println(strconv.Quote(`Hello "World"`))
	// "Hello \"World\""

	fmt.Println(strconv.Quote("tab\there\nnewline"))
	// "tab\there\nnewline"

	// Unquote — reverses Quote
	original, _ := strconv.Unquote(`"Hello \"World\""`)
	fmt.Println(original) // Hello "World"

	// QuoteRune converts a single character
	fmt.Println(strconv.QuoteRune('🚀'))  // '🚀'

	// ━━━━━ AppendXxx — direct []byte manipulation (zero allocations) ━━━━━
	// ✅ Faster than FormatXxx for []byte buffer building
	buf := make([]byte, 0, 64)
	buf = append(buf, "value="...)
	buf = strconv.AppendInt(buf, 42, 10)
	buf = append(buf, "&pi="...)
	buf = strconv.AppendFloat(buf, 3.14, 'f', 2, 64)
	buf = append(buf, "&ok="...)
	buf = strconv.AppendBool(buf, true)

	fmt.Println(string(buf))
	// value=42&pi=3.14&ok=true

	// ━━━━━ Real-world System: Parsing Environmental Configurations ━━━━━
	config := map[string]string{
		"port":     "8080",
		"timeout":  "30",
		"debug":    "true",
		"rate":     "0.75",
	}

	port, _ := strconv.Atoi(config["port"])
	timeout, _ := strconv.Atoi(config["timeout"])
	debug, _ := strconv.ParseBool(config["debug"])
	rate, _ := strconv.ParseFloat(config["rate"], 64)

	fmt.Printf("Port: %d, Timeout: %ds, Debug: %v, Rate: %.2f\n",
		port, timeout, debug, rate)

	// ━━━━━ Real-world System: Iterative CSV Stream Builder ━━━━━
	values := []interface{}{1, "Alice", 3.14, true}
	var b strings.Builder
	for i, v := range values {
		if i > 0 {
			b.WriteByte(',')
		}
		switch val := v.(type) {
		case int:
			b.WriteString(strconv.Itoa(val))
		case string:
			b.WriteString(strconv.Quote(val))
		case float64:
			b.WriteString(strconv.FormatFloat(val, 'f', -1, 64))
		case bool:
			b.WriteString(strconv.FormatBool(val))
		}
	}
	fmt.Println(b.String())
	// 1,"Alice",3.14,true
}
```

> **Why use `AppendInt` instead of `FormatInt` when building `[]byte` buffers?**
> `FormatInt` allocates an intermediate string, which then requires a second conversion to `[]byte` — two allocations per number in your hot path. `AppendInt` writes directly into the existing byte slice, eliminating the intermediate string entirely. Prefer this whenever writing high-throughput logging or serialization code.

> **Takeaway**: Use `Quote`/`Unquote` wherever escape handling is needed. Favor `AppendXxx` in high-performance pipelines. Real-world use cases: config parsing, CSV building, and HTTP query string construction.

---

## 4. PITFALLS

The mechanics of **Strconv** are clear. What remains is recognizing code that looks correct but hides silent runtime bugs.

| # | Severity | Bug | Consequence | Fix |
|---|----------|-----|-------------|-----|
| 1 | 🔴 Fatal | Ignoring error returns from parsing functions | Silent zero-value injection or panics | Always check `err != nil` |
| 2 | 🔴 Fatal | `Atoi` silent overflow on 32-bit platforms | Incorrect numeric values without error | Use `ParseInt` with explicit `bitSize` |
| 3 | 🟡 Common | Using `fmt.Sprintf` instead of `strconv` for number conversion | Up to 5x slower processing | Prefer `strconv.Itoa` or `FormatFloat` |
| 4 | 🔵 Minor | Misunderstanding `-1` precision in `FormatFloat` | Correct output but with trailing digits | `-1` means "minimum digits to represent the value uniquely" |
| 5 | 🔵 Minor | `ParseFloat` accepts `NaN` and `Inf` as valid inputs | Logic errors if not explicitly checked | Validate with `math.IsNaN()` / `math.IsInf()` |

### 🔴 Pitfall #1 — Ignoring error checks creates silent zero-value bombs

`strconv.Atoi("hello")` returns `(0, error)`. If your code runs `port, _ := strconv.Atoi(os.Getenv("PORT"))` and the environment variable is missing or invalid — your port value is `0`. Binding a server to port `0` tells the OS to pick a random free port → all downstream services lose connectivity. The server starts successfully but is unreachable, and nothing is logged.

**Fix**: Always check the conversion error. For critical config values, fail fast: `if err != nil { log.Fatalf("invalid PORT: %v", err) }`.

### 🔴 Pitfall #2 — Atoi overflow on 32-bit platforms

`Atoi` returns a platform-dependent `int`. Parsing `Atoi("3000000000")` on a 32-bit system overflows silently, returning an incorrect value. Use `ParseInt(s, 10, 64)` when you need guaranteed 64-bit width.

---

You have explored strconv from basic `Atoi` through advanced formatting. The resources below go deeper.

## 5. REF

| Resource              | Type     | Link                                                               | Notes |
| --------------------- | -------- | ------------------------------------------------------------------ | ----- |
| `strconv` package     | Official | [pkg.go.dev/strconv](https://pkg.go.dev/strconv)                   | API reference |
| Go Blog — Constants   | Blog     | [go.dev/blog/constants](https://go.dev/blog/constants)             | How untyped constants work in Go |
| Go Spec — Conversions | Official | [go.dev/ref/spec#Conversions](https://go.dev/ref/spec#Conversions) | Language-level conversion rules and limits |

---

## 6. RECOMMEND

The foundations of **Strconv — Type Conversion & Parsing** are clear. The extensions below take you into more complex data transformation scenarios.

| Extension                          | When                             | Why                          | File/Link |
| ---------------------------------- | -------------------------------- | ---------------------------- | --------- |
| `fmt.Sprintf`                      | Complex string interpolation     | Better readability with many variables | [./04-fmt.md](./04-fmt.md) |
| `encoding/json`                    | Marshaling structs and maps      | Automates typed data → string conversion | [pkg.go.dev/encoding/json](https://pkg.go.dev/encoding/json) |
| `math/big`                         | Arbitrarily large numbers        | Required when values exceed int64/float64 | [./05-math.md](./05-math.md) |
| `golang.org/x/exp/constraints`     | Generic numeric constraints      | Type-safe math across generic functions | [pkg.go.dev/golang.org/x/exp](https://pkg.go.dev/golang.org/x/exp) |

---

**Navigation**: [← strings](./02-strings.md) · [→ fmt](./04-fmt.md)
