<!-- tags: golang --> # 🔄 Strconv — Chuyển đổi kiểu & phân tích cú pháp

> Package `strconv` chuyển đổi giữa các chuỗi và các kiểu dữ liệu cơ bản: int, float, bool. Đây là bộ công cụ phân tích cú pháp và định dạng cần thiết nhất trong Go .

📅 Đã tạo: 23-03-2026 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 14 phút đọc

| Khía cạnh | Chi tiết |
| ------------- | --------------------------------------------- |
| ** Package ** | `strconv` |
| **Trường hợp sử dụng** | Phân tích chuỗi → số, format số → chuỗi |
| ** Go stdlib** | `strconv` , `fmt` (thay thế) |
| **Quy tắc chính** | Luôn xử lý các lỗi gặp phải trong quá trình phân tích cú pháp |

---

## 1. ĐỊNH NGHĨA `strconv.Atoi("42")` trả về `(42, nil)` . `strconv.Atoi("42.5")` trả về `(0, error)` . `strconv.Atoi("")` cũng trả về `(0, error)` . Ba kết quả riêng biệt cho ba đầu vào có vẻ hợp lệ — và nếu bạn bỏ qua kết quả trả về `error` thì giá trị 0 `0` sẽ trở thành một vectơ im lặng dẫn đến hỏng dữ liệu.

> *Mỗi phần dữ liệu đến qua HTTP đều là một chuỗi. Tham số URL: `?page=2&limit=50` . Chuỗi truy vấn: `sort=desc` . Các trường biểu mẫu: `price=99.9` . Tệp cấu hình: `timeout=30` . Các biến môi trường chẵn: `PORT=8080` .*
>
> *Để sử dụng các giá trị này trong logic nghiệp vụ, bạn phải chuyển đổi chúng một cách an toàn: `page` thành `int` , `price` thành `float64` , `debug` thành `bool` . `strconv` package xử lý việc này - phân tích cú pháp đầu vào chuỗi và định dạng lại dữ liệu thành chuỗi. Luôn kiểm tra lỗi trong quá trình phân tích cú pháp, vì đầu vào của người dùng có thể là `"hello"` khi bạn mong đợi `"42"` .*

### Nhóm chức năng cốt lõi

| Gia đình | Phân tích cú pháp (chuỗi → loại) | Format (loại → chuỗi) |
| ----------- | --------------------- | -------------------------- |
| **Số nguyên** | `Atoi` , `ParseInt` | `Itoa` , `FormatInt` |
| **Nổi** | `ParseFloat` | `FormatFloat` |
| **Bôn** | `ParseBool` | `FormatBool` |
| **Trích dẫn** | `Unquote` | `Quote` , `QuoteRune` |
| **Nối** | — | `AppendInt` , `AppendFloat` |

### Quy ước đặt tên và phân tích cú pháp Format```text
Parse___()   → string to type  (may fail → returns an error)
Format___()  → type to string  (cannot fail)
Atoi()       → "ASCII to Integer" (idiomatic shortcut for ParseInt)
Itoa()       → "Integer to ASCII" (idiomatic shortcut for FormatInt)
```---

Các hàm chuyển đổi này trông đơn giản — nhưng tồn tại các bẫy thầm lặng: gọi `Atoi` và bỏ qua lỗi sẽ đưa ra giá trị 0 vô hình và độ chính xác của float có thể giảm trong format /các chuyến đi khứ hồi. Những cái bẫy đó được giải nén trong những cái bẫy.

## 2. HÌNH ẢNH

Lỗi phổ biến nhất với `strconv` là truy cập chức năng trợ giúp quen thuộc theo tên trước khi khóa hướng truyền dữ liệu. Hình ảnh bên dưới buộc phải trả lời trước câu hỏi chính xác đó: văn bản có nhập vào hệ thống loại hay giá trị đã nhập sẽ xuất hiện trên dây dưới dạng chuỗi? ![Strconv decision map](./images/03-strconv-decision-map.png) *Hình: Quyết định `strconv` map chia bốn hướng hoạt động chính: phân tích cú pháp, format , nối thêm các đường dẫn nóng và chế độ lỗi im lặng được kích hoạt nếu lỗi hoặc kiểm tra độ chính xác bị bỏ qua.*

Khi ranh giới định hướng được thiết lập, các khối mã bên dưới sẽ đọc tự nhiên hơn nhiều. Bạn không còn xem `Atoi` , `ParseInt` và `FormatFloat` dưới dạng các API bị ngắt kết nối mà là các cổng riêng biệt hoạt động trên cùng một ranh giới chuyển văn bản thành loại.

## 3. MÃ

Với ** Strconv — Chuyển đổi loại và phân tích cú pháp**, chúng tôi đã thiết lập map cho cơ chế phân tích cú pháp và format . Bây giờ, hãy xem mã để xem cách chọn `Atoi` trên `ParseInt` hoặc `FormatFloat` trên `Sprintf` , ảnh hưởng trực tiếp đến độ chính xác của phép tính và xử lý lỗi.

### Ví dụ 1: Cơ bản — Atoi, Itoa & ParseBool

Chuỗi truy vấn HTTP là `string` s: `?page=3&limit=50&active=true` . Bạn phải chuyển đổi chúng thành `int` và `bool` cho truy vấn database . `fmt.Sscanf` ? Quá chậm và thiếu an toàn về loại. `strconv.Atoi` và `strconv.ParseBool` là tiêu chuẩn: nhanh và chúng trả về lỗi khi đầu vào không hợp lệ.

Đầu vào: `strconv.Atoi("42")` · Đầu ra: `(42, nil)` · `strconv.Atoi("abc")` · Đầu ra: `(0, error)````go
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
```> **Tại sao `Atoi` có thể tràn trên hệ thống 32-bit?**
> `Atoi` trả về `int` — kích thước của nó phụ thuộc vào kiến trúc nền tảng (32-bit so với 64-bit). Trên thiết bị 32 bit, đầu vào vượt quá phạm vi `int32` → lỗi. Đối với các ranh giới quan trọng, hãy sử dụng `ParseInt` với kích thước bit rõ ràng.

> **Takeaway**: Sử dụng `Atoi` / `Itoa` để chuyển đổi đơn giản. `ParseBool` chấp nhận các biến thể ( `"1"` , `"t"` , `"true"` ) — thuận tiện cho việc phân tích cú pháp cấu hình. Luôn kiểm tra lỗi trả về.

Chuyển đổi cơ bản là tiêu chuẩn. Tuy nhiên, việc kiểm soát các giới hạn độ chính xác khoa học thông qua `FormatFloat` , kết hợp với các chuyển đổi cơ sở riêng biệt, đòi hỏi sự hiểu biết cơ học sâu sắc hơn.

### Ví dụ 2: Trung cấp — ParseInt, ParseFloat & FormatFloat

Tệp cấu hình cung cấp `timeout=30` , `rate=0.75` và `port=0x1F90` (thập lục phân). `Atoi` chỉ xử lý cơ sở 10. Bạn cần `ParseInt` với tham số cơ sở và `ParseFloat` với kích thước bit rõ ràng. `FormatFloat` kiểm soát độ chính xác: `'f'` (thập phân), `'e'` (khoa học), `'g'` (thu gọn) — trao quyền kiểm soát đến từng chữ số riêng lẻ.

Đầu vào: `strconv.ParseInt("1F90", 16, 64)` · Đầu ra: `(8080, nil)````go
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
```> **Tại sao `FormatFloat` yêu cầu bốn tham số riêng biệt?**
> Việc chuẩn hóa kiến trúc float cực kỳ phức tạp: `fmt` đảm bảo mục đích định dạng ('f' so với 'e'), `prec` khóa các ràng buộc phân rã số (-1 đảm bảo khả năng đọc an toàn tối thiểu) và `bitSize` thực thi làm tròn toán học nghiêm ngặt (các float 32 bit hoạt động hoàn toàn khác so với các lớp 64 bit). Luôn liên kết `ParseFloat` với các kiến ​​trúc 64-bit một cách phổ biến trừ khi xử lý được tối ưu hóa nhiều `float32` arrays .

> **Takeaway**: `ParseInt` với các tiền tố base=0 tự động phát hiện `0x` , `0o` , `0b` — hữu ích cho việc phân tích cú pháp cấu hình. `FormatFloat` với prec=-1 cho đầu ra duy nhất tối thiểu. Sử dụng `ParseUint` cho các giá trị không dấu.

Định dạng được bảo hiểm. Tiếp theo: phân tích cú pháp chuyên biệt, hoạt động byte thô và xử lý trích dẫn.

### Ví dụ 3: Nâng cao - Trích dẫn, Nối thêm & Các mẫu trong thế giới thực

Bạn đang xây dựng một công cụ ghi nhật ký JSON cần các chuỗi thoát an toàn chứa dấu ngoặc kép `"` , dòng mới `
` và Unicode. `fmt.Sprintf("%q", s)` hoạt động nhưng chậm do chi phí phân tích cú pháp format . `strconv.Quote` nhanh hơn ~3 lần, dành riêng cho việc thoát chuỗi ASCII/Unicode.

Các hàm `Append*` ( `AppendInt` , `AppendFloat` , `AppendBool` ) vẫn nhanh hơn — chúng nối trực tiếp vào `[]byte` slices mà không tạo các chuỗi tạm thời.

Đầu vào: `strconv.Quote("hello
world")` · Đầu ra: `"\"hello\nworld\""````go
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
```> **Tại sao nên sử dụng `AppendInt` thay vì `FormatInt` khi xây dựng bộ đệm `[]byte` ?**
> `FormatInt` phân bổ một chuỗi trung gian, sau đó yêu cầu chuyển đổi thứ hai thành `[]byte` — hai phân bổ cho mỗi số trong đường dẫn nóng của bạn. `AppendInt` ghi trực tiếp vào byte hiện có slice , loại bỏ hoàn toàn chuỗi trung gian. Ưu tiên điều này bất cứ khi nào viết mã ghi nhật ký hoặc mã tuần tự hóa thông lượng cao.

> **Takeaway**: Sử dụng `Quote` / `Unquote` bất cứ khi nào cần xử lý thoát. Ưu tiên `AppendXxx` trong các đường ống hiệu suất cao. Các trường hợp sử dụng trong thế giới thực: phân tích cú pháp cấu hình, xây dựng CSV và xây dựng chuỗi truy vấn HTTP.

---

## 4. Cạm bẫy

Cơ chế của ** Strconv ** rất rõ ràng. Những gì còn lại là nhận dạng mã có vẻ chính xác nhưng lại ẩn các lỗi runtime im lặng.

| # | Mức độ nghiêm trọng | Lỗi | Hậu quả | Sửa chữa |
|---|----------|------|-------------|------|
| 1 | 🔴 Gây tử vong | Bỏ qua lỗi trả về từ các hàm phân tích cú pháp | Im lặng tiêm giá trị 0 hoặc hoảng loạn | Luôn kiểm tra `err != nil` |
| 2 | 🔴 Gây tử vong | `Atoi` tràn im lặng trên nền tảng 32 bit | Giá trị số không chính xác mà không có lỗi | Sử dụng `ParseInt` với `bitSize` |
| 3 | 🟡 Chung | Sử dụng `fmt.Sprintf` thay vì `strconv` để chuyển đổi số | Xử lý chậm hơn tới 5 lần | Thích `strconv.Itoa` hoặc `FormatFloat` |
| 4 | 🔵 Nhỏ | Hiểu sai độ chính xác của `-1` trong `FormatFloat` | Đầu ra đúng nhưng có chữ số ở cuối | `-1` có nghĩa là "chữ số tối thiểu để biểu thị giá trị duy nhất" |
| 5 | 🔵 Nhỏ | `ParseFloat` chấp nhận `NaN` và `Inf` làm đầu vào hợp lệ | Lỗi logic nếu không được kiểm tra rõ ràng | Xác thực bằng `math.IsNaN()` / `math.IsInf()` |

### 🔴 Cạm bẫy số 1 - Bỏ qua việc kiểm tra lỗi sẽ tạo ra những quả bom có giá trị bằng 0 thầm lặng `strconv.Atoi("hello")` trả về `(0, error)` . Nếu mã của bạn chạy `port, _ := strconv.Atoi(os.Getenv("PORT"))` và biến môi trường bị thiếu hoặc không hợp lệ — giá trị cổng của bạn là `0` . Liên kết máy chủ với cổng `0` yêu cầu HĐH chọn một cổng trống ngẫu nhiên → tất cả các dịch vụ hạ nguồn đều mất kết nối. Máy chủ khởi động thành công nhưng không thể truy cập được và không có gì được ghi lại.

**Khắc phục**: Luôn kiểm tra lỗi chuyển đổi. Đối với các giá trị cấu hình quan trọng, hãy nhanh chóng thực hiện: `if err != nil { log.Fatalf("invalid PORT: %v", err) }` .

### 🔴 Cạm bẫy #2 — Tràn Atoi trên nền tảng 32-bit `Atoi` trả về phụ thuộc vào nền tảng `int` . Phân tích cú pháp `Atoi("3000000000")` trên hệ thống 32 bit tràn âm thầm, trả về giá trị không chính xác. Sử dụng `ParseInt(s, 10, 64)` khi bạn cần đảm bảo độ rộng 64-bit.

---

Bạn đã khám phá strconv từ `Atoi` cơ bản đến định dạng nâng cao. Các tài nguyên dưới đây đi sâu hơn.

## 5. GIỚI THIỆU

| Tài nguyên | Loại | Liên kết | Ghi chú |
| --------------------- | -------- | ------------------------------------------------------------------ | ----- |
| `strconv` package | Chính thức | [pkg.go.dev/strconv](https://pkg.go.dev/strconv) | Tham chiếu API |
| Go Blog — Hằng số | Blog | [go.dev/blog/constants](https://go.dev/blog/constants) | Cách các hằng số chưa được gõ hoạt động trong Go |
| Go Spec — Chuyển đổi | Chính thức | [go.dev/ref/spec#Conversions](https://go.dev/ref/spec#Conversions) | Quy tắc và giới hạn chuyển đổi cấp độ ngôn ngữ |

---

## 6. KHUYẾN NGHỊ

Nền tảng của ** Strconv — Chuyển đổi loại & phân tích cú pháp** rất rõ ràng. Các tiện ích mở rộng bên dưới sẽ đưa bạn vào các tình huống chuyển đổi dữ liệu phức tạp hơn.

| Gia hạn | Khi nào | Tại sao | Tệp/Liên kết |
| ---------------------------------- | -------------------------------- | ---------------------------- | --------- |
| `fmt.Sprintf` | Nội suy chuỗi phức tạp | Khả năng đọc tốt hơn với nhiều biến | [./04-fmt.md](./04-fmt.md) |
| `encoding/json` | Thống chế structs và maps | Tự động nhập dữ liệu → chuyển đổi chuỗi | [pkg.go.dev/encoding/json](https://pkg.go.dev/encoding/json) |
| `math/big` | Số lượng lớn tùy ý | Bắt buộc khi giá trị vượt quá int64/float64 | [./05-math.md](./05-math.md) |
| `golang.org/x/exp/constraints` | Generic ràng buộc số | Toán học an toàn kiểu trên các hàm generic | [pkg.go.dev/golang.org/x/exp](https://pkg.go.dev/golang.org/x/exp) |

---

**Điều hướng**: [← strings](./02-strings.md) · [→ fmt](./04-fmt.md)