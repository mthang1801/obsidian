<!-- tags: golang -->
# 🖨️ Fmt — Formatting, Printing & Scanning

> Package `fmt` is the central I/O formatting hub in Go: print routines, format string construction, and input scanning. Understanding format verbs accelerates debugging and ensures precise output.

📅 Created: 2026-03-23 · 🔄 Updated: 2026-04-19 · ⏱️ 15 min read

| Aspect         | Detail                                    |
| -------------- | ----------------------------------------- |
| **Package**    | `fmt`                                     |
| **Use case**   | Print, format strings, scan input, debug  |
| **Interfaces** | `Stringer`, `GoStringer`, `Formatter`     |
| **Key rule**   | `%v` for general, `%+v` for struct fields |

---

## 1. DEFINE

`fmt.Sprintf("%v", obj)` is convenient but 5x slower than `strconv.Itoa()`. `fmt.Errorf("%w", err)` wraps the error chain; `%v` does not. Production Go demands knowing when to use `fmt`, when to reach for `strconv`, and when to pivot to `strings.Builder`.

> *You are debugging a production bug. The API returns wrong data but you cannot tell at which step. You need to print variable values, format log output, and build error messages with context. In Go, all formatted output flows through a single package: `fmt`.*
>
> *`fmt` is far more than `println`. It is a versatile formatting toolkit: `Sprintf` builds strings safely, `Fprintf` writes to any `io.Writer` (files, HTTP responses, buffers), and `Errorf` with `%w` creates wrapped errors that preserve the causal chain. Mastering `fmt` means mastering how Go communicates — with the developer via logs, with the caller via errors, and with the client via API responses.*

### Print Functions

| Function   | Output        | Newline? | Format? |
| ---------- | ------------- | -------- | ------- |
| `Print`    | stdout        | ❌       | ❌      |
| `Println`  | stdout        | ✅       | ❌      |
| `Printf`   | stdout        | ❌       | ✅      |
| `Sprint`   | return string | ❌       | ❌      |
| `Sprintf`  | return string | ❌       | ✅      |
| `Sprintln` | return string | ✅       | ❌      |
| `Fprint`   | io.Writer     | ❌       | ❌      |
| `Fprintf`  | io.Writer     | ❌       | ✅      |
| `Errorf`   | return error  | ❌       | ✅      |

### Format Verbs — Reference Table

| Verb  | Description              | Example output            |
| ----- | ------------------------ | ------------------------- |
| `%v`  | Default format           | `{Alice 25}`              |
| `%+v` | Struct with field names  | `{Name:Alice Age:25}`     |
| `%#v` | Go syntax representation | `main.User{Name:"Alice"}` |
| `%T`  | Type                     | `main.User`               |
| `%d`  | Integer (decimal)        | `42`                      |
| `%b`  | Integer (binary)         | `101010`                  |
| `%o`  | Integer (octal)          | `52`                      |
| `%x`  | Integer (hex lowercase)  | `2a`                      |
| `%X`  | Integer (hex uppercase)  | `2A`                      |
| `%f`  | Float (decimal)          | `3.141593`                |
| `%e`  | Float (scientific)       | `3.141593e+00`            |
| `%g`  | Float (compact)          | `3.14159`                 |
| `%s`  | String                   | `hello`                   |
| `%q`  | Quoted string            | `"hello"`                 |
| `%c`  | Character (rune)         | `A`                       |
| `%p`  | Pointer address          | `0xc000014080`            |
| `%t`  | Boolean                  | `true`                    |
| `%%`  | Literal %                | `%`                       |

### Width & Precision

| Syntax  | Description                | Example output |
| ------- | -------------------------- | -------------- |
| `%10d`  | Width 10, right-aligned    | `        42`   |
| `%-10d` | Width 10, left-aligned     | `42        `   |
| `%010d` | Width 10, zero-padded      | `0000000042`   |
| `%.2f`  | 2 decimal places           | `3.14`         |
| `%8.2f` | Width 8, 2 decimals        | `    3.14`     |
| `%.5s`  | Truncate string to 5 chars | `Hello`        |

---

These format verbs look familiar — but real traps exist: `%v` on a pointer prints the address instead of the value, and `Sprintf` in a hot loop creates an allocation storm. Those traps surface in PITFALLS.

## 2. VISUAL

`fmt` looks like a flat package, but the correct mental model starts from the *destination* rather than the function name. The visual below reorganizes the API into family groups: where does the output go, how is a string created, and what controls verb resolution.

![Fmt API map](./images/04-fmt-api-map.png)

*Figure: API-family map for `fmt` grouping four families — `Print`, `Sprint`, `Fprint`, `Scan` — then anchoring the verb resolution layer where `Stringer`, `error`, width, and precision begin to shape the actual output.*

Once destination and resolution order are visible, the code below stops feeling like "memorize the verb." Instead, you will see why the same value produces entirely different output when you switch families or verbs.

## 3. CODE

With **Fmt — Formatting, Printing & Scanning**, we mapped format verbs and output patterns. Now let's step into the code to see how each choice — `%v` vs `%+v`, `Sprintf` vs `Fprintf`, `Stringer` vs manual format — actually changes debug output and log quality.

### Example 1: Basic — Print Functions & Format Verbs

You are debugging a struct and need field names plus values. `Println` only prints values. `Printf("%v")` also only prints values. `Printf("%+v")` adds field names. `Printf("%#v")` adds the type name as well — but when should you use which?

The `fmt` package has 3 verb groups: general (`%v`, `%T`), integer (`%d`, `%x`), and string (`%s`, `%q`) — each verb serves a distinct purpose.

Input: `fmt.Printf("%+v", User{"Go", 15})` · Output: `{Name:Go Age:15}`

```go
package main

import "fmt"

type User struct {
	Name string
	Age  int
}

func main() {
	u := User{"Alice", 25}

	// ━━━━━ Print vs Println vs Printf ━━━━━
	fmt.Print("no newline")
	fmt.Println("with newline")
	fmt.Printf("formatted: %s is %d years old\n", u.Name, u.Age)

	// ━━━━━ %v variants ━━━━━
	fmt.Printf("%%v:  %v\n", u)       // {Alice 25}
	fmt.Printf("%%+v: %+v\n", u)     // {Name:Alice Age:25}
	fmt.Printf("%%#v: %#v\n", u)     // main.User{Name:"Alice", Age:25}
	fmt.Printf("%%T:  %T\n", u)      // main.User

	// ━━━━━ Number formats ━━━━━
	n := 255
	fmt.Printf("Decimal:  %d\n", n)   // 255
	fmt.Printf("Binary:   %b\n", n)   // 11111111
	fmt.Printf("Octal:    %o\n", n)   // 377
	fmt.Printf("Hex:      %x\n", n)   // ff
	fmt.Printf("Hex:      %X\n", n)   // FF
	fmt.Printf("Unicode:  %U\n", 'A') // U+0041

	// ━━━━━ Float formats ━━━━━
	pi := 3.14159265358979
	fmt.Printf("Default:    %f\n", pi)   // 3.141593
	fmt.Printf("Scientific: %e\n", pi)   // 3.141593e+00
	fmt.Printf("Compact:    %g\n", pi)   // 3.14159265358979
	fmt.Printf("2 decimals: %.2f\n", pi) // 3.14

	// ━━━━━ String formats ━━━━━
	s := "Hello"
	fmt.Printf("String:  %s\n", s)    // Hello
	fmt.Printf("Quoted:  %q\n", s)    // "Hello"
	fmt.Printf("Bytes:   %x\n", s)    // 48656c6c6f

	// ━━━━━ Pointer ━━━━━
	p := &n
	fmt.Printf("Pointer: %p\n", p)    // 0xc000014088
}
```

> `%v` outputs `{Alice 25}` — you cannot tell which field is which. `%+v` outputs `{Name:Alice Age:25}` — explicit. `%#v` even provides Go syntax `main.User{Name:"Alice", Age:25}` — copy-paste ready. `%T` gives the type name — useful when an interface hides the concrete type.

> **Takeaway**: `%v` for general output, `%+v` for debugging structs, `%#v` for dump-to-code, `%T` for type inspection. Number formats: `%d` decimal, `%x` hex, `%b` binary.

Print basics are covered. But format verbs go deeper: `%+v`, `%#v`, width/precision, and the Stringer interface.

### Example 2: Intermediate — Width, Padding & Sprintf

You print a data table to the terminal: columns stick together, numbers misalign. `Printf` provides width and padding: `%10d` right-aligns within 10 characters, `%-10s` left-aligns, `%08x` pads with zeros. `Sprintf` returns a string instead of printing — use it to build formatted strings for logging and reporting.

Input: `fmt.Sprintf("%-10s %5d", "Go", 42)` · Output: `"Go              42"`

```go
package main

import "fmt"

func main() {
	// ━━━━━ Width & Alignment ━━━━━
	fmt.Printf("|%10d|\n", 42)     // |        42|   right-aligned
	fmt.Printf("|%-10d|\n", 42)    // |42        |   left-aligned
	fmt.Printf("|%010d|\n", 42)    // |0000000042|   zero-padded
	fmt.Printf("|%+d|\n", 42)     // |+42|          show sign
	fmt.Printf("|%+d|\n", -42)    // |-42|          show sign

	// ━━━━━ Float precision ━━━━━
	fmt.Printf("|%10.2f|\n", 3.14)   // |      3.14|
	fmt.Printf("|%-10.2f|\n", 3.14)  // |3.14      |

	// ━━━━━ String width ━━━━━
	fmt.Printf("|%15s|\n", "hello")    // |          hello|
	fmt.Printf("|%-15s|\n", "hello")   // |hello          |
	fmt.Printf("|%.3s|\n", "hello")    // |hel|   truncate

	// ━━━━━ Sprintf — build formatted string ━━━━━
	name := "API"
	version := 2
	url := fmt.Sprintf("https://example.com/%s/v%d", name, version)
	fmt.Println(url) // https://example.com/API/v2

	// ━━━━━ Errorf — create formatted error ━━━━━
	id := 42
	err := fmt.Errorf("user %d not found", id)
	fmt.Println(err) // user 42 not found

	// ✅ Wrap error (Go 1.13+)
	originalErr := fmt.Errorf("connection refused")
	wrappedErr := fmt.Errorf("failed to get user %d: %w", id, originalErr)
	fmt.Println(wrappedErr) // failed to get user 42: connection refused

	// ━━━━━ Tabular output ━━━━━
	type Product struct {
		Name  string
		Price float64
		Stock int
	}
	products := []Product{
		{"Laptop", 999.99, 5},
		{"Mouse", 29.99, 150},
		{"Keyboard", 79.99, 42},
	}

	fmt.Printf("%-12s %10s %6s\n", "PRODUCT", "PRICE", "STOCK")
	fmt.Println("─────────────────────────────────")
	for _, p := range products {
		fmt.Printf("%-12s %10.2f %6d\n", p.Name, p.Price, p.Stock)
	}
}
```

> `%w` wraps the error — preserving the entire error chain. `errors.Is()` and `errors.As()` can traverse the chain to find the root cause. Without `%w`, the error chain is lost and callers cannot type-check. `%v` formats the error into a plain string — losing type information entirely.

> **Takeaway**: `Sprintf` for string building, `Errorf` + `%w` for error wrapping. Width and padding for tabular output. `%010d` zero-pads, `%-10s` left-aligns.

Format verbs are covered. Next: custom Stringer/GoStringer, the `fmt.Formatter` interface, and high-performance logging alternatives.

### Example 3: Advanced — Stringer Interface & Fprint

You have a `Money` struct with `Amount` and `Currency`. Every time you print, you manually write `fmt.Printf("%s %.2f", m.Currency, m.Amount)`. Implement the `fmt.Stringer` interface (a `String() string` method) and `fmt.Println(m)` will automatically call that method — DRY and consistent.

The `Fprint` family writes to any `io.Writer` (file, network, buffer) instead of stdout — forming the foundation of structured logging and template rendering.

Input: `fmt.Println(Money{42.5, "USD"})` · Output: `USD 42.50`

```go
package main

import (
	"fmt"
	"os"
	"strings"
)

// ━━━━━ Stringer interface — custom %v output ━━━━━

type Color struct {
	R, G, B uint8
}

// ✅ Implement fmt.Stringer → controls %v and %s output
func (c Color) String() string {
	return fmt.Sprintf("#%02X%02X%02X", c.R, c.G, c.B)
}

// ✅ Implement fmt.GoStringer → controls %#v output
func (c Color) GoString() string {
	return fmt.Sprintf("Color{R:%d, G:%d, B:%d}", c.R, c.G, c.B)
}

// ━━━━━ Custom type with Stringer ━━━━━

type LogLevel int

const (
	DEBUG LogLevel = iota
	INFO
	WARN
	ERROR
)

func (l LogLevel) String() string {
	names := [...]string{"DEBUG", "INFO", "WARN", "ERROR"}
	if int(l) < len(names) {
		return names[l]
	}
	return fmt.Sprintf("LogLevel(%d)", l)
}

func main() {
	// ━━━━━ Stringer in action ━━━━━
	red := Color{255, 0, 0}
	fmt.Println(red)              // #FF0000
	fmt.Printf("Color: %v\n", red) // Color: #FF0000
	fmt.Printf("Go:    %#v\n", red) // Go: Color{R:255, G:0, B:0}

	// ━━━━━ Enum formatting ━━━━━
	level := WARN
	fmt.Printf("Level: %v (%d)\n", level, level) // Level: WARN (2)

	// ━━━━━ Fprint — write to any io.Writer ━━━━━
	// ✅ Write to stderr
	fmt.Fprintln(os.Stderr, "This goes to stderr")

	// ✅ Write to strings.Builder
	var b strings.Builder
	fmt.Fprintf(&b, "Name: %s, Age: %d", "Bob", 30)
	result := b.String()
	fmt.Println(result) // Name: Bob, Age: 30

	// ✅ Write to file
	f, err := os.CreateTemp("", "output-*.txt")
	if err != nil {
		fmt.Println("Error:", err)
		return
	}
	defer f.Close()
	defer os.Remove(f.Name())

	fmt.Fprintf(f, "Report generated\n")
	fmt.Fprintf(f, "Users: %d\n", 42)
}
```

> **Why is the Stringer interface the most important pattern in `fmt`?**
> Implementing `String() string` on a custom type means `fmt.Println(myType)` automatically calls that method. No `toString()` override or decorator needed — just one method. Apply it to enum logging (`LogLevel.String()`), color formatting, money display. `Fprint` + `io.Writer` decouples the output destination from the formatting logic.

> **Takeaway**: Stringer for custom `%v`/`%s` output. GoStringer for `%#v`. `Fprint*` for writing to any `io.Writer`. Combine with `strings.Builder` for efficient string building.

---

## 4. PITFALLS

The core mechanics of **Fmt — Formatting, Printing & Scanning** are clear. What remains is recognizing syntax that looks _almost right_ but introduces format bugs or performance traps into production.

| # | Severity | Bug | Consequence | Fix |
|---|----------|-----|-------------|-----|
| 1 | 🔴 Fatal | Stringer infinite loop — `String()` calls `Sprintf` with its own receiver | Stack overflow panic | Use fields directly, not `%v` with the receiver |
| 2 | 🟡 Common | `Printf` missing `\n` | Output does not advance to the next line | Append `\n` or use `Println` |
| 3 | 🟡 Common | Mismatched verb → output `%!d(string=hello)` | Debug output becomes unreadable | Match the verb to the correct type |
| 4 | 🟡 Common | `Sprintf` is slower than `strconv` for number conversion | Performance degradation in hot paths | Prefer `strconv.Itoa()` when you only need number→string |
| 5 | 🔵 Minor | `%w` only works inside `Errorf` | Compiles fine but behaves incorrectly at runtime | `%w` wraps errors exclusively via `fmt.Errorf` |

### 🔴 Pitfall #1 — Stringer infinite loop crash

You write a `String()` method for type `MyType` and inside it call `fmt.Sprintf("%v", m)` — accidentally creating infinite recursion:

```go
type MyType struct{ Name string }

func (m MyType) String() string {
    return fmt.Sprintf("MyType: %v", m) // ❌ %v calls String() again → infinite loop!
}
// Fix: fmt.Sprintf("MyType: %s", m.Name)  ← use the field directly
```

`fmt` sees `%v` on a type that has `String()` → calls `String()` → encounters `%v` again → calls `String()` → stack overflow. This bug only surfaces at runtime — the compiler issues no warning.

---

You have explored the `fmt` package from `Printf` through custom formatters. The resources below will take you deeper.

## 5. REF

| Resource                 | Type     | Link                                                                                                                    | Notes |
| ------------------------ | -------- | ----------------------------------------------------------------------------------------------------------------------- | ----- |
| `fmt` package            | Official | [pkg.go.dev/fmt](https://pkg.go.dev/fmt)                                                                                | API reference |
| Effective Go — Printing  | Official | [go.dev/doc/effective_go#printing](https://go.dev/doc/effective_go#printing)                                            | Best practices |
| Format verbs cheat sheet | External | [yourbasic.org/golang/fmt-printf-reference-cheat-sheet](https://yourbasic.org/golang/fmt-printf-reference-cheat-sheet/) | Quick reference |

---

## 6. RECOMMEND

The foundations of **Fmt — Formatting, Printing & Scanning** are clear. The extensions below help you bring formatting into production with structured logging, CLI alignment, and template generation.

| Extension            | When                    | Why                                    | File/Link |
| -------------------- | ----------------------- | -------------------------------------- | --------- |
| `log` / `slog`       | Structured logging      | Production logging instead of fmt.Println | [pkg.go.dev/log/slog](https://pkg.go.dev/log/slog) |
| `text/tabwriter`     | Aligned tabular output  | Auto-align columns                     | [pkg.go.dev/text/tabwriter](https://pkg.go.dev/text/tabwriter) |
| `text/template`      | Complex text generation | Built-in template engine               | [pkg.go.dev/text/template](https://pkg.go.dev/text/template) |
| `encoding/json`      | Structured output       | JSON marshaling for APIs               | [pkg.go.dev/encoding/json](https://pkg.go.dev/encoding/json) |
| `fmt.Formatter`      | Custom format verbs     | Implement for complex custom types     | [pkg.go.dev/fmt#Formatter](https://pkg.go.dev/fmt#Formatter) |

---

**Navigation**: [← strconv](./03-strconv.md) · [→ math](./05-math.md)
