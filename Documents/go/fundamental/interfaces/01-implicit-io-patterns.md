<!-- tags: golang, interfaces --> # 🔌 Interfaces — Ẩn, io.Reader/Writer, Trống Interface > Go interfaces : sự hài lòng ngầm, gõ vịt, mẫu io, generics 📅 Đã tạo: 20-03-2026 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 17 phút đọc

| Khía cạnh | Chi tiết |
| --------------- | --------------------------------------------- |
| **Khái niệm** | Hợp đồng hành vi, thực hiện ngầm định |
| **Trường hợp sử dụng** | Trừu tượng hóa, dependency injection , thử nghiệm |
| **Thông tin chi tiết quan trọng** | KHÔNG có từ khóa `implements` - ngầm định! |
| ** Go tục ngữ** | "Chấp nhận interfaces , trả về structs " |

---

## 1. ĐỊNH NGHĨA

Nhà sản xuất xác định phương thức 8 interfaces buộc người tiêu dùng thực hiện các hành vi mà họ không bao giờ sử dụng. Sau đó, các thử nghiệm yêu cầu triển khai mock đầy đủ cho một phương thức duy nhất. Cách khắc phục: người tiêu dùng xác định interface tối thiểu họ cần.

> * `exportReport(dest ???)` bắt đầu ghi vào một tập tin. Lần chạy nước rút tiếp theo: S3. Tiếp theo: bộ đệm thử nghiệm. Mã hóa cứng `*os.File` có nghĩa là ba thay đổi signature trên toàn bộ cơ sở mã — ba rủi ro hồi quy.*
>
> * Go giải quyết vấn đề này bằng `io.Writer` — **1 phương thức**: `Write([]byte) (int, error)` . Các tệp, phản hồi HTTP, `bytes.Buffer` , `strings.Builder` và người viết S3 đều đáp ứng điều đó. Các hàm chấp nhận `io.Writer` không cần thay đổi khi đích thay đổi. **không có từ khóa `implements` ** — một loại thỏa mãn interface bằng cách sử dụng đúng phương thức signatures . Đây là kiểu gõ cấu trúc.*

Sự hài lòng tiềm ẩn có một khía cạnh sắc nét: Go interfaces lưu trữ `(type, value)` nội bộ. A nil `*bytes.Buffer` được gán cho một `io.Writer` là **không** a nil interface — `w != nil` trả về `true` và `w.Write()` hoảng loạn. Cái bẫy này được giải nén trong PITFALS.

### 1.1 Interface Quy tắc

| Quy tắc | Mô tả |
| ----------- | ------------------------------------------------------ |
| ngầm định | Không có từ khóa `implements` — phương thức đối sánh signatures là đủ |
| Nhỏ | Ưu tiên 1–2 phương pháp để có khả năng kết hợp tối đa |
| Đặt tên | Phương thức đơn interfaces sử dụng hậu tố `-er` : `Reader` , `Writer` |
| Composition | Nhúng interfaces để kết hợp: `ReadWriter = Reader + Writer` |
| `any` | Bí danh `interface{}` - chấp nhận loại any |

### 1.2 Thư viện chuẩn Interfaces — Tham khảo

| Interface | Phương pháp | Package | Trường hợp sử dụng |
| ---------------- | ------------------------------- | ------------- | ---------------------------- |
| `io.Reader` | `Read([]byte) (int, error)` | io | Đọc từ nguồn byte |
| `io.Writer` | `Write([]byte) (int, error)` | io | Ghi vào đích byte |
| `io.Closer` | `Close() error` | io | Phát hành một nguồn tài nguyên |
| `fmt.Stringer` | `String() string` | fmt | Biểu diễn chuỗi tùy chỉnh |
| `error` | `Error() string` | dựng sẵn | Giá trị lỗi |
| `sort.Interface` | `Len, Less, Swap` | sắp xếp | Sắp xếp bộ sưu tập tùy chỉnh |
| `http.Handler` | `ServeHTTP(w, r)` | mạng/http | Trình xử lý yêu cầu HTTP |
| `json.Marshaler` | `MarshalJSON() ([]byte, error)` | mã hóa/json | Mã hóa JSON tùy chỉnh |

> **Tại sao lại ngầm hiểu sự hài lòng?** Trong Java/C#, việc triển khai interface yêu cầu nhập package xác định nó — kết nối nhà sản xuất và người tiêu dùng. Go đảo ngược điều này: người tiêu dùng xác định interface , nhà sản xuất không bao giờ nhập nó. Kết quả: **không khớp nối** và loại any từ any package có thể đáp ứng hợp đồng.

Tiêu chuẩn interfaces ở trên bao gồm hầu hết các trường hợp sử dụng. Các chế độ thất bại bên dưới bộc lộ những cái bẫy có thể bắt được ngay cả những nhà phát triển Go có kinh nghiệm.

### 1.3 Các kiểu lỗi

| Khiếm khuyết | Nguyên nhân | Hậu quả | Sửa chữa |
| --- | ------------ | ------ | --- |
| Nil interface vs interface giữ nil | `var w io.Writer` ( nil ) vs `var w io.Writer = (*bytes.Buffer)(nil)` (không- nil !) | `w != nil` là đúng → `w.Write()` hoảng sợ | Trả về `nil` một cách rõ ràng, không phải là nil pointer |
| Pointer receiver so với giá trị | `func (t *T) Method()` → chỉ `*T` thỏa mãn interface , không phải `T` | Lỗi biên dịch im lặng | Sử dụng pointer một cách nhất quán |
| Chất béo interfaces (>3 phương pháp) | Quá nhiều phương thức trong một interface | Khó mock , khó kiểm tra | Phân tách thành interfaces nhỏ hơn |

---

Lý thuyết là rõ ràng. Điều nguy hiểm là sự thỏa mãn tiềm ẩn có thể bị phá vỡ một cách âm thầm: thêm một phương thức vào interface và mọi loại đã thỏa mãn trước đó sẽ ngừng biên dịch - không có dòng `implements` để tìm kiếm.

## 2. HÌNH ẢNH

Hầu hết sự nhầm lẫn interface xuất phát từ việc chiếu hệ thống phân cấp lớp OOP lên kiểu cấu trúc của Go . Hình ảnh này củng cố ba điều bạn cần nắm giữ đồng thời: sự hài lòng tiềm ẩn, cặp `(type, value)` và bẫy nil - interface . ![Implicit interfaces mental model](./images/01-implicit-io-patterns-mental-model.png) *Hình: Mô hình tinh thần cho Go interfaces — sự hài lòng tiềm ẩn, interface composition , và sự khác biệt giữa nil - interface so với nil -value.*

Với mô hình này, mã bên dưới có cách đọc khác nhau: bạn sẽ thấy không chỉ chức năng của từng mẫu mà còn thấy hợp đồng ngầm có thể bị phá vỡ ở đâu.

## 3. MÃ

Lý thuyết được lập bản đồ. Bây giờ chúng ta hãy xem sự hài lòng tiềm ẩn, `io.Reader/Writer` composition và gõ các xác nhận trong hành động.

### Ví dụ 1: Cơ bản — Triển khai ngầm & Polymorphism Cả `Rectangle` và `Circle` đều thực hiện `Shape` mà không cần khai báo. `PrintShape` chấp nhận any `Shape` - phương thức kiểm tra trình biên dịch signatures tại biên dịch time .```go
package main

import "fmt"

// ✅ Define interface — small, focused (2 methods)
type Shape interface {
    Area() float64
    Perimeter() float64
}

// ✅ Rectangle implements Shape IMPLICITLY
type Rectangle struct {
    Width, Height float64
}

func (r Rectangle) Area() float64      { return r.Width * r.Height }
func (r Rectangle) Perimeter() float64 { return 2 * (r.Width + r.Height) }
func (r Rectangle) String() string     { return fmt.Sprintf("Rect(%gx%g)", r.Width, r.Height) }

// ✅ Circle also implements Shape — no "implements" keyword
type Circle struct {
    Radius float64
}

func (c Circle) Area() float64      { return 3.14159 * c.Radius * c.Radius }
func (c Circle) Perimeter() float64 { return 2 * 3.14159 * c.Radius }

// ✅ Accept interface → works with ANY Shape implementation
func PrintShape(s Shape) {
    fmt.Printf("Area=%.2f Perimeter=%.2f\n", s.Area(), s.Perimeter())
}

func TotalArea(shapes []Shape) float64 {
    total := 0.0
    for _, s := range shapes {
        total += s.Area()
    }
    return total
}

func main() {
    shapes := []Shape{
        Rectangle{10, 5},
        Circle{7},
        Rectangle{3, 4},
    }
    for _, s := range shapes {
        PrintShape(s)
    }
    fmt.Printf("Total: %.2f\n", TotalArea(shapes))
}
```> **Takeaway**: Không có từ khóa `implements` — phương thức đối sánh signatures là yêu cầu duy nhất. `[]Shape` giữ loại any đáp ứng hợp đồng.

Thang đo mức độ hài lòng ngầm định vì stdlib sử dụng cùng một mẫu: `io.Reader` là phương thức 1 interface được hàng trăm loại thỏa mãn. Ví dụ tiếp theo cho thấy cách soạn thảo và trang trí cho người đọc.

---

### Ví dụ 2: Trung cấp — Mẫu io.Reader/Writer `CountWords()` chấp nhận `io.Reader` — nó hoạt động với chuỗi, tệp, nội dung HTTP hoặc trình đọc tùy chỉnh any . `UpperReader` bao bọc any `io.Reader` và viết hoa đầu ra - mẫu decorator không có inheritance .```go
package main

import (
    "bytes"
    "fmt"
    "io"
    "os"
    "strings"
)

// ✅ Custom type implementing io.Reader — decorator pattern
type UpperReader struct {
    reader io.Reader
}

func (u *UpperReader) Read(p []byte) (int, error) {
    n, err := u.reader.Read(p)
    for i := range n {
        if p[i] >= 'a' && p[i] <= 'z' {
            p[i] -= 32  // Convert to uppercase
        }
    }
    return n, err
}

// ✅ Accept io.Reader → works with ANY reader
func CountWords(r io.Reader) (int, error) {
    data, err := io.ReadAll(r)
    if err != nil {
        return 0, err
    }
    words := strings.Fields(string(data))
    return len(words), nil
}

func main() {
    // ✅ strings.Reader implements io.Reader
    count, _ := CountWords(strings.NewReader("hello world foo bar"))
    fmt.Println("Words:", count)  // 4

// ✅ bytes.Buffer implements io.Reader AND io.Writer
    var buf bytes.Buffer
    buf.WriteString("data from buffer")
    count, _ = CountWords(&buf)
    fmt.Println("Words:", count)  // 3

// ✅ io.Copy — works with ANY Reader→Writer pair
    src := strings.NewReader("Hello, 世界")
    io.Copy(os.Stdout, src)
    fmt.Println()

// ✅ Compose readers — decorator pattern: UpperReader wraps any Reader
    upper := &UpperReader{reader: strings.NewReader("hello go")}
    io.Copy(os.Stdout, upper)  // HELLO GO
    fmt.Println()
}
```> **Tại sao 1 phương thức interfaces ?** Một hàm chấp nhận `io.Reader` hoạt động với mọi loại có `Read` . Thêm phương thức thứ hai và bạn loại trừ một nửa stdlib. interfaces nhỏ tối đa hóa khả năng kết hợp.
>
> **Tại sao trang trí?** Go không có inheritance . Thay vào đó, hãy bọc một `io.Reader` bên trong một `io.Reader` khác để thêm hành vi. Stack họ: `&GzipReader{&UpperReader{fileReader}}` . Mỗi lớp là độc lập và có thể kiểm tra được.

> **Takeaway**: Chấp nhận `io.Reader` / `io.Writer` để tách khỏi các loại bê tông. Trình trang trí thay thế inheritance cho hành vi phân lớp.

---

### Ví dụ 3: Nâng cao — Interface Composition & Type Assertion Soạn interfaces nhỏ thành lớn hơn ( `ReadWriteCloser = Reader + Writer + Closer` ). Sử dụng xác nhận loại và chuyển đổi loại cho công văn runtime . Sử dụng bộ bảo vệ biên dịch- time ( `var _ Writer = (*MyWriter)(nil)` ) để sớm phát hiện các phương thức bị thiếu.```go
package main

import "fmt"

// ✅ Small interfaces — 1 method each
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type Closer interface {
    Close() error
}

// ✅ Interface composition — embed to combine
type ReadWriter interface {
    Reader
    Writer
}

type ReadWriteCloser interface {
    Reader
    Writer
    Closer
}

// ✅ Type assertion — safe comma-ok pattern
func describe(i interface{}) {
    // ❌ UNSAFE: s := i.(string) — panics if wrong type

// ✅ Safe assertion with comma-ok
    if s, ok := i.(string); ok {
        fmt.Println("String:", s)
        return
    }

// ✅ Type switch — runtime dispatch by type
    switch v := i.(type) {
    case int:
        fmt.Println("Int:", v*2)
    case string:
        fmt.Println("String:", v)
    case bool:
        fmt.Println("Bool:", v)
    default:
        fmt.Printf("Unknown: %T = %v\n", v, v)
    }
}

// ✅ Compile-time interface guard — fails at compile if not satisfied
type MyWriter struct{}

func (w *MyWriter) Write(p []byte) (int, error) {
    return len(p), nil
}

// This line fails at compile-time if *MyWriter doesn't implement Writer
var _ Writer = (*MyWriter)(nil)

func main() {
    describe(42)
    describe("hello")
    describe(true)
    describe(3.14)
}
```> **Tại sao soạn interfaces ?** Mỗi interface nhỏ nắm bắt một khả năng. Embedding kết hợp chúng mà không tạo hệ thống phân cấp lớp. Khách hàng chỉ phụ thuộc vào phương pháp họ sử dụng - Interface Nguyên tắc phân tách.
>
> **Tại sao biên dịch- time bảo vệ?** `var _ Writer = (*MyWriter)(nil)` không biên dịch được time nếu `*MyWriter` không triển khai `Writer` . Điều này phát hiện các phương thức còn thiếu trước khi chạy thử nghiệm.

> **Takeaway**: Soạn nhỏ interfaces qua embedding . Sử dụng `var _ I = (*T)(nil)` để biên dịch- time xác minh. Loại công tắc xử lý công văn runtime một cách an toàn.

---

## 4. Cạm bẫy

Cơ chế của ** Interfaces ** rất rõ ràng. Những gì còn lại là nhận dạng các mẫu trông có vẻ chính xác nhưng gây ra lỗi runtime hoặc lỗi loại im lặng.

| # | Mức độ nghiêm trọng | Khiếm khuyết | Hậu quả | Sửa chữa |
|---|----------|------|----------|------|
| 1 | 🔴 Gây tử vong | Nil interface vs interface giữ nil | `w != nil` là đúng nhưng `w.Write()` hoảng sợ | Trả về `nil` một cách rõ ràng, không phải là nil pointer |
| 2 | 🔴 Gây tử vong | Không an toàn type assertion `i.(string)` | Hoảng sợ nếu gõ sai | Sử dụng dấu phẩy-ok: `s, ok := i.(string)` |
| 3 | 🟡 Chung | Pointer receiver không bao gồm sự hài lòng về giá trị | `T` không đáp ứng interface yêu cầu phương thức `*T` | Sử dụng pointer receivers một cách nhất quán |
| 4 | 🟡 Chung | Chất béo interfaces (>3 phương pháp) | Khó mock , khó kiểm tra | Phân tách thành phương thức 1–2 interfaces |
| 5 | 🟡 Chung | Trả về interfaces thay vì các loại cụ thể | Người gọi không thể truy cập các phương thức cụ thể | "Chấp nhận interfaces , trả về structs " |
| 6 | 🔵 Nhỏ | Lạm dụng `interface{}` / `any` | Mất an toàn kiểu | Thay vào đó, hãy sử dụng generics ( Go 1.18+) |

### 🔴 Cạm bẫy #1 — Nil interface bẫy

A Go interface lưu trữ `(type, value)` . Trả về một nil pointer đã nhập sẽ bao bọc nó trong một nil interface - `w != nil` là `true` , nhưng việc gọi phương thức any sẽ gây hoảng loạn.```go
func getWriter() io.Writer {
    var buf *bytes.Buffer // nil
    return buf            // ❌ interface{type: *Buffer, value: nil} — w != nil is true!
}
// Fix: return nil explicitly
func getWriter() io.Writer { return nil }
```**Quy tắc**: Không bao giờ trả lại nil pointer đã nhập dưới dạng interface . Trả về `nil` trực tiếp.

### 🔴 Cạm bẫy #2 — Xác nhận kiểu panic `s := i.(string)` hoảng sợ nếu `i` không phải là một chuỗi. Không giống như các ngôn ngữ khác, Go không trả về giá trị mặc định - nó bị lỗi.

**Khắc phục**: Luôn sử dụng dạng dấu phẩy-ok: `s, ok := i.(string)` .

---

---

## 5. GIỚI THIỆU

| Tài nguyên | Loại | Liên kết | Mô tả |
| ------------- | -------- | -------------------------------------------------------------------------------- | ------- |
| Go Chuyến tham quan | Chính thức | [go.dev/tour/methods/9](https://go.dev/tour/methods/9) | Hướng dẫn tương tác interface |
| io Package | Chính thức | [pkg.go.dev/io](https://pkg.go.dev/io) | Truyền phát lõi interfaces |
| Có hiệu lực Go | Chính thức | [go.dev/doc/effective_go#interfaces](https://go.dev/doc/effective_go#interfaces) | Hướng dẫn đặt tên và thiết kế |

---

## 6. KHUYẾN NGHỊ

Nền tảng của ** Interfaces ** đã được giải quyết. Các tiện ích mở rộng bên dưới kết nối các mẫu interface với thử nghiệm, generics và HTTP sản xuất.

| Gia hạn | Khi nào | Tại sao | Tệp/Liên kết |
| ------- | ------- | ----- | --------- |
| DI & Mocking | Thử nghiệm với các phần phụ thuộc bị cô lập | Thay thế các triển khai thực tế bằng mocks qua interfaces | [02-di-mocking-patterns.md](./02-di-mocking-patterns.md) |
| Generics | Các chức năng tái sử dụng an toàn kiểu | Ràng buộc các tham số loại với interfaces | [../types/02-generics.md](../types/02-generics.md) |
| Trình xử lý HTTP | Xây dựng dịch vụ web | `http.Handler` là phương thức 1 interface | [../../concurrency/03-context.md](../../concurrency/03-context.md) |
| loại. Interface | Sắp xếp tùy chỉnh | `Len` , `Less` , `Swap` để đặt hàng bộ sưu tập | [pkg.go.dev/sort](https://pkg.go.dev/sort) |

---

**Điều hướng**: [← Structs](../structs/) · [→ DI & Mocking Patterns](./02-di-mocking-patterns.md)