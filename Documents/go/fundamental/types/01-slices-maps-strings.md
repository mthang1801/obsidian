<!-- tags: golang, data-structures --> # 📦 Hệ thống loại — Slices , Maps , Chuỗi

> Hệ thống loại Go : các loại tích hợp, slices (động arrays ), maps (hashmap), chuỗi (UTF-8 bất biến)

📅 Đã tạo: 2026-03-20 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 15 phút đọc

| Khía cạnh | Chi tiết |
| ----------------- | -------------------------------------- |
| **Khái niệm** | Loại giá trị so với loại tham chiếu |
| **Trường hợp sử dụng** | Cấu trúc dữ liệu, bộ sưu tập |
| **Thông tin chi tiết quan trọng** | Slices = tham chiếu đến array cơ bản |
| ** Go triết lý** | Composition > inheritance |

---

## 1. ĐỊNH NGHĨA `sub := original[1:3]` — trông giống như một bản sao, nhưng việc thay đổi `sub[0]` sẽ âm thầm biến đổi `original[1]` . `var cache map[string]int` theo sau là `cache["key"] = 1` — panic . `len("Hello, 世界")` trả về 13, không phải 9. Ba vấn đề cổ điển này có chung một nguyên nhân gốc rễ: hệ thống kiểu của Go phân biệt ngữ nghĩa giá trị với ngữ nghĩa tham chiếu theo những cách mâu thuẫn với trực giác ban đầu của hầu hết các nhà phát triển.

> *Bạn viết `sub := original[1:3]` — nó trông giống như một bản sao, nhưng nó là bí danh. `sub[0] = 99` và `original[1]` cũng trở thành 99. Sau đó, bạn viết `var cache map[string]int` và gọi `cache["key"] = 1` — ngay lập tức panic vì map chưa bao giờ được khởi tạo.*
>
> *Đây là những vấn đề cổ điển của hệ thống loại của Go : a slice là một tham chiếu đến phần sao lưu array (không phải bản sao), a map phải được khởi tạo trước khi ghi và một chuỗi là một chuỗi byte UTF-8 bất biến. Hiểu được ba sự thật này sẽ giúp ngăn ngừa phần lớn các lỗi mà người mới gặp phải trong Go .*

### Các loại tích hợp

| Danh mục | Các loại | Giá trị 0 |
| ----------- | ------------------------------------------------ | ---------- |
| **Boolean** | `bool` | `false` |
| **Số nguyên** | `int` , `int8/16/32/64` , `uint` , `uint8/16/32/64` | `0` |
| **Nổi** | `float32` , `float64` | `0` |
| **Phức tạp** | `complex64` , `complex128` | `(0+0i)` |
| **Chuỗi** | `string` (UTF-8 bất biến) | `""` |
| **Byte** | `byte` (bí danh `uint8` ) | `0` |
| **Chữ rune** | `rune` (bí danh `int32` , Unicode) | `0` |

### Các loại tổng hợp

| Loại | Mô tả | Có thể thay đổi | Giá trị 0 |
| ----------- | -------------------- | ------- | --------------- |
| ** Array ** | Kích thước cố định `[n]T` | ✅ | Phần tử không |
| ** Slice ** | Động `[]T` | ✅ | `nil` |
| ** Map ** | Băm map `map[K]V` | ✅ | `nil` |
| ** Struct ** | Ghi `struct{...}` | ✅ | Trường không |
| ** Channel ** | `chan T` | ✅ | `nil` |

### Slice Nội bộ

| Lĩnh vực | Mô tả |
| ----- | ----------------------------------- |
| `ptr` | Pointer đến array cơ bản |
| `len` | Số phần tử |
| `cap` | Năng lực (có thể tăng trước khi cấp vốn) |

Vẫn còn một cái bẫy cổ điển: tiêu đề slice (ptr, len, cap) là một loại giá trị. Chuyển nó vào một hàm, nối vào bên trong hàm đó và người gọi không bao giờ nhìn thấy slice mới. Cái bẫy đó xuất hiện trong PITFALS.

---
## 2. HÌNH ẢNH

Phần khó không phải là tên loại - đó là ba nhóm giá trị này thất bại theo ba cách khác nhau. Hình ảnh bên dưới hợp nhất chúng thành một thẻ mô hình tinh thần. ![Slices maps strings mental model](./images/01-slices-maps-strings-mental-model.png) *Hình: Bốn sự kiện quan trọng cần nắm giữ đồng thời — slice là một bộ mô tả, nil slice khác với nil map , một chuỗi là byte trước các ký tự và ranh giới đột biến là câu hỏi xem xét mã quan trọng.*

Với mô hình này đã được khóa, mỗi ví dụ mã bên dưới sẽ trở thành một bài kiểm tra ngữ nghĩa thay vì một bản demo API bị ngắt kết nối.

## 3. MÃ

Mô hình tinh thần đã được thiết lập. Bây giờ map mỗi quyết định — sub- slice so với bản sao, nil map so với thực hiện, `+=` so với Builder — để viết mã tiết lộ hành vi thực tế.

### Ví dụ 1: Cơ bản — Slices — Hoạt động cốt lõi
> **Mục tiêu**: Thể hiện việc tạo, cắt phụ, biểu thức slice đầy đủ, sao chép và xóa.
> **Độ phức tạp**: O(1) cho mỗi thao tác; phần bổ sung được khấu hao O(1).```go
package main

import "fmt"

func main() {
    // ✅ Create slices
    s1 := []int{1, 2, 3, 4, 5}           // Literal
    s2 := make([]int, 5)                   // make(type, len)
    s3 := make([]int, 0, 10)              // make(type, len, cap)

fmt.Println(len(s1), cap(s1))  // 5, 5
    fmt.Println(len(s3), cap(s3))  // 0, 10

// ✅ Append — may allocate new array if cap exceeded
    s3 = append(s3, 1, 2, 3)
    s3 = append(s3, s1...)        // Spread operator

// ✅ Slice expression (sub-slice)
    sub := s1[1:3]    // [2, 3] — shares underlying array!
    sub[0] = 99        // ⚠️ s1[1] is now 99 too!
    fmt.Println(s1)    // [1, 99, 3, 4, 5]

// ✅ Full slice expression — limit capacity
    safe := s1[1:3:3]  // [low:high:max] — cap = max - low
    // Now append to `safe` won't affect s1

// ✅ Copy — detach from original
    dst := make([]int, len(s1))
    copy(dst, s1)
    dst[0] = 999  // s1 unaffected

// ✅ Delete element at index 2
    s := []int{1, 2, 3, 4, 5}
    i := 2
    s = append(s[:i], s[i+1:]...)  // [1, 2, 4, 5]

// ✅ Go 1.21+ slices package
    // slices.Delete(s, i, i+1)
    // slices.Contains(s, 3)
    // slices.Sort(s)

fmt.Println(s2, s3, sub, safe, dst, s)
}
```> **Takeaway**: Slice sub- slices chia sẻ bộ nhớ — sử dụng `copy()` hoặc biểu thức slice đầy đủ `[a:b:b]` để tách. `append` có thể phân bổ array mới → luôn sử dụng `s = append(s, ...)` . Slices bao gồm dữ liệu tuần tự. Maps cung cấp tra cứu khóa-giá trị O(1) - nhưng việc ghi nil map là ngay lập tức panic .

### Ví dụ 2: Trung cấp — Maps > **Mục tiêu**: CRUD, mẫu dấu phẩy-ok, map -as-set và khởi tạo map lồng nhau.
> **Độ phức tạp**: O(1) mỗi lần tra cứu/chèn/xóa.```go
package main

import "fmt"

func main() {
    // ✅ Create maps
    m := map[string]int{
        "alice": 95,
        "bob":   87,
    }
    m2 := make(map[string][]string)  // map[string]→[]string

// ✅ CRUD
    m["charlie"] = 92               // Create/Update
    score := m["alice"]             // Read (95)
    delete(m, "bob")                // Delete

// ✅ Check existence (comma ok pattern)
    val, ok := m["bob"]
    if !ok {
        fmt.Println("bob not found")  // ← this prints
    }
    _ = val

// ✅ Iterate (random order!)
    for name, score := range m {
        fmt.Printf("%s: %d\n", name, score)
    }

// ✅ Map as set
    seen := make(map[string]struct{})  // struct{} = 0 bytes
    seen["apple"] = struct{}{}
    if _, exists := seen["apple"]; exists {
        fmt.Println("apple exists")
    }

// ✅ Nested map
    m2["fruits"] = []string{"apple", "banana"}
    m2["vegs"] = []string{"carrot"}

fmt.Println(m, m2, score)
}
```> **Tại sao `struct{}` cho map -as-set thay vì `bool` ?**
> `struct{}` = 0 byte bộ nhớ. `bool` = 1 byte. Đối với map có 1M mục nhập: giúp tiết kiệm 1 MB. Ngoài ra, `struct{}{}` báo hiệu ý định rõ ràng: "chỉ sự tồn tại của khóa là quan trọng, giá trị là không liên quan".

> **Bài học rút ra**: Thứ tự lặp lại Map là ngẫu nhiên — sắp xếp các khóa nếu cần kết quả đầu ra xác định. Mẫu dấu phẩy-ok kiểm tra sự tồn tại. `struct{}` cho mẫu map -as-set. Slices xử lý các chuỗi, maps xử lý tra cứu. Các chuỗi trông đơn giản nhưng lại ẩn chứa nhiều bẫy: `len()` đếm byte, `+=` trong một vòng lặp là O(n²).

### Ví dụ 3: Nâng cao — Chuỗi — UTF-8, Runes, Builder > **Mục tiêu**: Thể hiện ngữ nghĩa byte và ngọc, phép lặp `range` , chuyển đổi ngọc và `strings.Builder` .
> **Độ phức tạp**: O(n) cho phép lặp và Builder ; O(n²) cho concat `+=` ngây thơ.```go
package main

import (
    "fmt"
    "strings"
    "unicode/utf8"
)

func main() {
    // ✅ Strings are immutable UTF-8 byte sequences
    s := "Hello, 世界"
    fmt.Println(len(s))                      // 13 (bytes, NOT characters!)
    fmt.Println(utf8.RuneCountInString(s))   // 9 (runes = characters)

// ✅ Iterate by rune (character)
    for i, r := range s {
        fmt.Printf("byte %2d: %c (U+%04X)\n", i, r, r)
    }
    // byte  7: 世 (U+4E16)  — 3 bytes per CJK character

// ✅ Rune vs Byte
    r := []rune(s)       // Convert to rune slice → can modify
    r[7] = '🌍'
    modified := string(r)
    fmt.Println(modified)

// ✅ String operations
    fmt.Println(strings.Contains(s, "世界"))      // true
    fmt.Println(strings.Split("a,b,c", ","))      // [a b c]
    fmt.Println(strings.TrimSpace("  hello  "))   // "hello"
    fmt.Println(strings.ReplaceAll(s, "Hello", "Hi"))

// ✅ String Builder — efficient concatenation (no allocs)
    var b strings.Builder
    for i := range 100 { // Go 1.22+
        fmt.Fprintf(&b, "item-%d ", i)
    }
    result := b.String()
    _ = result
    // ❌ DON'T: s += "..." in loop (O(n²) allocations)
    // ✅ DO: strings.Builder or strings.Join
}
```> **Tại sao `strings.Builder` thay vì `+=` trong một vòng lặp?**
> `s += "x"` trong một vòng lặp: mỗi lần lặp lại phân bổ một chuỗi mới, sao chép toàn bộ nội dung hiện có cộng với phần mới → phân bổ O(n²). `strings.Builder` : phân bổ trước một bộ đệm, thêm vào tổng số O(1) khấu hao → O(n). Với 100 lần lặp: `+=` tạo ra ~5000 phân bổ, Builder ~4 phân bổ.

> **Takeaway**: `len(string)` = byte, `utf8.RuneCountInString()` = ký tự. Chuỗi không thể thay đổi → chuyển đổi thành `[]rune` để sửa đổi. Sử dụng `strings.Builder` cho các vòng lặp nối.

---

## 4. Cạm bẫy

Cơ chế rõ ràng. Điều còn lại là nhận ra những điểm mà mã _gần như đúng_ mang các giả định sai vào quá trình sản xuất.

| # | Mức độ nghiêm trọng | Lỗi | Hậu quả | Sửa chữa |
|---|----------|-------|-------------|------|
| 1 | 🔴 Gây tử vong | nil map viết | `m["key"] = 1` hoảng sợ khi `m` không được `make()` d | Luôn `make(map[K]V)` trước khi viết |
| 2 | 🔴 Gây tử vong | Slice sub- slice chia sẻ bộ nhớ | Sửa đổi sub- slice → sửa đổi dữ liệu gốc | `copy()` hoặc đầy đủ slice `[a:b:b]` |
| 3 | 🟡 Chung | `len(string)` = byte, không phải ký tự | Đếm sai chuỗi UTF-8 | `utf8.RuneCountInString()` |
| 4 | 🟡 Chung | Thứ tự lặp Map là ngẫu nhiên | Đầu ra không xác định | Sắp xếp các khóa: `slices.Sort(maps.Keys(m))` |
| 5 | 🟡 Chung | Chuỗi concat `+=` trong vòng lặp | Phân bổ O(n²), chậm | `strings.Builder` hoặc `strings.Join` |
| 6 | 🔵 Nhỏ | Nối thêm mà không cần chỉ định lại | `append` có thể trả về một slice mới, biến cũ trở nên cũ | Luôn `s = append(s, ...)` |

### 🔴 Cạm bẫy #1 — Nil map write = instant panic `var m map[string]int; m["k"] = 1` → panic . A map phải là `make()` d trước khi viết. Đọc từ nil map trả về giá trị 0 (không panic ) - vì vậy lỗi chỉ xuất hiện khi ghi, có thể ở xa trang khai báo.

### 🔴 Cạm bẫy #2 — Sub- slice chia sẻ bộ nhớ `sub := original[1:3]` không sao chép dữ liệu - `sub` và `original` có chung cơ sở array . Sửa đổi `sub[0]` → `original[1]` được thay đổi. Biểu thức slice đầy đủ `original[1:3:3]` giới hạn phụ- slice → `append` phải phân bổ một array mới.

Các tài nguyên dưới đây đi sâu hơn vào nội bộ.

---

## 5. GIỚI THIỆU

| Tài nguyên | Loại | Liên kết | Ghi chú |
| -------------- | -------- | ------------------------------------------------------------ | ----- |
| Go Slices | Chính thức | [go.dev/blog/slices-intro](https://go.dev/blog/slices-intro) | Slice lặn sâu bên trong |
| Go Maps | Chính thức | [go.dev/blog/maps](https://go.dev/blog/maps) | Map triển khai |
| Go Chuỗi | Chính thức | [go.dev/blog/strings](https://go.dev/blog/strings) | UTF-8, rune, byte |
| slices package | Chính thức | [pkg.go.dev/slices](https://pkg.go.dev/slices) | Go 1.21+ generic người trợ giúp |

---

## 6. KHUYẾN NGHỊ

Những phần mở rộng này kết nối kiến thức về cấu trúc dữ liệu vào mã sản xuất an toàn, hiệu quả.

| Gia hạn | Khi nào | Cơ sở lý luận | Tệp/Liên kết |
| --------- | ---- | --------- | --------- |
| Generics | Bộ sưu tập an toàn loại | `Filter[T]` , `Map[T,U]` , generic container | [02-generics.md](./02-generics.md) |
| `sync.Map` | Truy cập đồng thời map | Thread -safe map cho các tình huống có tính cạnh tranh cao | [../helper/09-set-concurrent-map.md](../helper/09-set-concurrent-map.md) |
| `slices` package | Go 1.21+ người trợ giúp | `slices.Sort` , `slices.Contains` , `slices.Delete` | [pkg.go.dev/slices](https://pkg.go.dev/slices) |
| `strings.Builder` | Vòng lặp nối chuỗi | Thay thế hiệu quả cho `+=` (O(n) vs O(n²)) | [../functions/02-strings.md](../functions/02-strings.md) |

**Điều hướng**: [← Basics](../basics/README.md) · [→ Generics](./02-generics.md)