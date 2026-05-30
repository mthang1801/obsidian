<!-- tags: golang --> # 🟢 Go Cơ bản — Cú pháp cơ bản

> Biến, hằng, khai báo, giá trị 0 — nền tảng cho việc đọc và viết thành ngữ Go 📅 Đã tạo: 2026-03-19 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 12 phút đọc

| Khía cạnh | Chi tiết |
| ---------------- | ---------------------------------------------- |
| **Khái niệm** | Khai báo, giá trị 0, quyết định cú pháp ban đầu |
| **Trường hợp sử dụng** | Mọi chương trình Go |
| **Điều kiện tiên quyết** | Không có |
| **CLI** | `go run` , `go build` , `go fmt` |

---

## 1. ĐỊNH NGHĨA

Hãy tưởng tượng một đoạn mã Go có vẻ cực kỳ cơ bản, nhưng thời điểm bạn chuyển ngữ cảnh sang gỡ lỗi hoặc đánh giá mã, các giả định yếu sẽ dễ dàng bị lộ ra. Tại thời điểm đó, ** Go Cơ bản — Cú pháp cơ bản** không còn chỉ là một chỉ mục được định dạng tốt; nó trở thành nơi bạn phải nắm vững các cơ chế cốt lõi của ngôn ngữ.

Bạn vừa sao chép kho lưu trữ Go cho time đầu tiên. Mở `main.go` , bạn thấy `:=` thay vì `var` , các hàm trả về `(int, error)` thay vì ném ngoại lệ và `for` được sử dụng ở cả ba nơi mà C/Java sẽ sử dụng `for` , `while` và `do-while` . Không có từ khóa `class` , không có công cụ sửa đổi `public` / `private` . Bạn cần viết mã mới nhưng không chắc chắn nên khai báo một biến bằng `var` hay `:=` — chọn sai và quá trình xem xét mã sẽ bị từ chối; chọn chính xác và PR hợp nhất ngay lập tức.

Đây chính là vấn đề mà bài viết này giải quyết: hiểu **tại sao** cú pháp Go được thiết kế theo cách nó vốn có, vì vậy mọi dòng mã bạn viết đều là **thành ngữ** — chứ không chỉ được "dịch" từ Java hoặc Python sang Go . Luồng điều khiển và `defer` sẽ chỉ được chạm vào đủ để bạn không đọc sai mã; đi sâu vào các chủ đề đó nằm ở các làn liền kề của cụm này.

### 1.1 Biến & Hằng — Hai phương thức khai báo, hai mục đích Go có **hai phương thức khai báo biến** — không phải do thiếu tính nhất quán mà vì chúng phục vụ hai trường hợp sử dụng riêng biệt:

| Cú pháp | Mô tả | Ví dụ | Khi nào nên sử dụng |
| ------------- | ------------------------------ | -------------------- | ------------------------------------ |
| `var x int` | Khai báo rõ ràng | `var count int = 10` | cấp độ Package , loại rõ ràng docs |
| `x := value` | Khai báo ngắn (kiểu suy luận) | `name := "Go"` | Các hàm bên trong, phân tích kiểu rõ ràng |
| `const X = 1` | Biên dịch- hằng số time | `const Pi = 3.14159` | Giá trị bất biến |
| `iota` | Tự động tăng hằng số | Mẫu Enum | Tạo các lượt thích enum trong các khối `const()` |

> **Tại sao cả `var` và `:=` ?** `var` được sử dụng ở cấp độ package (ngoài các hàm) và khi cần các loại rõ ràng cho tài liệu. `:=` chỉ khả dụng trong các hàm - sẽ ngắn gọn hơn khi trình biên dịch có thể suy ra kiểu từ giá trị bên phải. Chọn sai sẽ không gây ra lỗi nhưng nó vi phạm quy ước Go → việc đánh giá mã sẽ yêu cầu thay đổi.

### 1.2 Giá trị 0 — Chưa bao giờ được khởi tạo Go **không cho phép các trạng thái chưa được khởi tạo** — mọi biến không được khai báo đều được gán một giá trị 0 tương ứng với loại của nó:

| Loại | Giá trị 0 |
| ------------------------------------------------------------------ | ---------- |
| `int` , `float64` | `0` |
| `string` | `""` |
| `bool` | `false` |
| `pointer` , `slice` , `map` , `channel` , `interface` , `func` | `nil` |

> **Tại sao?** Giá trị 0 loại bỏ toàn bộ loại lỗi do "quên khởi tạo" — lỗi phổ biến nhất trong C/C++. `var buf bytes.Buffer` ngay lập tức sẵn sàng để sử dụng mà không cần hàm tạo. Nhưng **hãy cẩn thận**: a `nil map` cho phép đọc (trả về giá trị 0), nhưng **ghi vào nil map sẽ kích hoạt panic **.

### 1.3 Luồng điều khiển — Ít từ khóa hơn, nhiều khả năng hơn Go **chỉ có một từ khóa duy nhất cho các vòng lặp** — `for` xử lý các vai trò của `while` , `do-while` và vòng lặp C-for cổ điển:

| Tuyên bố | Mô tả | Lưu ý |
| --------- | ----------------------------- | ------------------------------- |
| `if` | Hỗ trợ câu lệnh init | `if err := fn(); err != nil {}` |
| `for` | Vòng lặp đơn độc | Thay thế hoàn toàn `while` |
| `switch` | Tự động `break` (không có dự phòng) | Sử dụng `fallthrough` nếu cần |
| `select` | Channel chuyển đổi | Thực thi chặn/không chặn |
| `defer` | Trì hoãn thực thi (LIFO stack ) | Tài nguyên dọn dẹp |

> **Tại sao `if err := fn(); err != nil {}` ?** Câu lệnh khởi tạo trong `if` giới hạn phạm vi của `err` dành riêng cho khối đó — biến không bị rò rỉ ra bên ngoài, dẫn đến mã sạch hơn. Đây là thành ngữ ** Go #1** mà mọi nhà phát triển Go đều phải biết.

### 1.4 Chế độ lỗi

| Lỗi | Nguyên nhân | Hậu quả | Sửa chữa |
| ------------------------- | ---------------------------------------------- | --------------------------------- | ------------------------------------ |
| `unused variable` lỗi | Go thực thi việc sử dụng — không sử dụng = lỗi biên dịch | Xây dựng thất bại | Sử dụng `_` hoặc xóa biến |
| `nil pointer dereference` | Hội thảo một nil pointer | Runtime panic | Kiểm tra nil trước khi hội thảo |
| `nil map` viết panic | Viết cho một map chưa được khởi tạo (không `make()` ) | Runtime panic | Luôn `make(map[K]V)` trước khi viết |
| Biến bị che khuất | `:=` bên trong phạm vi bên trong sẽ tạo ra một var | Lỗi logic - var bên ngoài vẫn còn nguyên | Sử dụng `=` trong phạm vi bên trong |

Các bảng và định nghĩa hiển thị _what_ tồn tại — nhưng khi gặp một dòng mã mới, bạn vẫn phải quyết định: `var` hay `:=` ? `const` hoặc `var` ? Cây quyết định bên dưới giúp bạn chọn đúng trong vòng 3 giây.

---

Các chế độ lỗi ở trên nghe có vẻ dễ tránh - nhưng có những cái bẫy thực sự: sử dụng `:=` trong phạm vi khối sẽ tạo ra biến bóng im lặng và các nhóm `const` sử dụng `iota` sẽ trở nên bù đắp khi một dòng mới được chèn tùy ý. Những cái bẫy đó sẽ xuất hiện trong phần PITFALS.

## 2. HÌNH ẢNH

Các bảng biểu và định nghĩa đã cho bạn biết những gì tồn tại. Phần dễ xảy ra lỗi nhất là quyết định phải được đưa ra vào thời điểm bạn chuẩn bị khai báo một biến mới: `var` , `:=` hoặc `const` . ![Var vs := vs const](./images/01-syntax-variables-decision-map.png) _Hình: Quyết định map nhóm ba câu hỏi quan trọng nhất trước khi khai báo một biến trong Go : phạm vi nào, khả năng biến đổi nào và liệu tín hiệu loại có cần hiển thị rõ ràng trên chính dòng đó hay không._

PNG này không thay thế các giải thích chi tiết. Nó buộc chặt chẽ quá trình suy nghĩ đúng đắn trước khi bạn viết. Khi luồng quyết định đã rõ ràng, ba ví dụ dưới đây sẽ chứng minh lý do tại sao, ngay cả đối với cùng một biến, sự thay đổi trong ngữ cảnh sẽ làm thay đổi hoàn toàn phương thức khai báo mà bạn nên sử dụng. ![Zero values — what is safe and what panics](./images/01-zero-values-nil-traps.png) _Hình: Ma trận an toàn giá trị 0 - đọc vùng chứa nil map / slice / pointer trả về giá trị 0 một cách an toàn, nhưng việc ghi vào vùng chứa any nil sẽ kích hoạt vùng chứa runtime panic . Luôn gọi `make()` trước lần viết đầu tiên._

## 3. MÃ

Với ** Go Cơ bản - Cú pháp cơ bản**, chúng tôi sở hữu map . Bây giờ chúng ta hạ nó xuống mã để xem mỗi lựa chọn nhỏ trong Go thực tế thay đổi cách chương trình thực thi như thế nào.

### Ví dụ 1: Cơ bản — Biến, Hằng, Iota Bạn mở một Go repo cho time đầu tiên và thấy `Read | Write` mang lại `3` . Một đồng nghiệp nói, "đó là những cờ bit sử dụng iota ". Bạn cần hiểu: iota hoạt động như thế nào, tại sao `1 << iota` hoạt động như cờ cấp phép và khi nào nên sử dụng khối `const()` thay vì `var` . Nhưng trước đó - câu hỏi cơ bản hơn: sự khác biệt giữa `var x int` và `x := 10` là gì? Go không có từ khóa `enum` - `iota` trong khối `const()` thay thế nó. `:=` là một khai báo biến ngắn dành riêng cho phạm vi hàm. `var` được sử dụng ở mức package hoặc khi cần có giá trị 0 rõ ràng.

Đầu vào: `Permission: Read | Write` · Đầu ra: `3` (nhị phân `011` ), `hasRead = true````go
package main

import "fmt"

// ✅ Constants with iota — Go lacks an enum keyword; iota replaces it
type Weekday int
const (
    Sunday    Weekday = iota  // 0
    Monday                     // 1
    Tuesday                    // 2
    Wednesday                  // 3
    Thursday                   // 4
    Friday                     // 5
    Saturday                   // 6
)

// ✅ Bit flags with iota — A common pattern for permissions & options
type Permission uint8
const (
    Read    Permission = 1 << iota  // 1  (001)
    Write                            // 2  (010)
    Execute                          // 4  (100)
)

func main() {
    // ✅ Short declaration — The most common within function bodies
    name := "Go"
    age := 15
    pi := 3.14159

// ✅ Multiple declaration — Groups related variables
    var (
        host    = "localhost"
        port    = 8080
        verbose = false
    )

// ✅ Type conversion — Go has NO implicit conversion
    // int → float64 must be explicit, and vice-versa
    var x int = 42
    var y float64 = float64(x)  // ⚠️ Must be cast explicitly
    var z int = int(y)          // ⚠️ Precision is lost if there are decimals

fmt.Println(name, age, pi, host, port, verbose, x, y, z)

// ✅ Bit flag usage — Combine and check using bitwise operators
    perm := Read | Write       // 3 (011)
    hasRead := perm&Read != 0  // true — bitwise AND check
    fmt.Println(perm, hasRead)
}
```> **Kết luận**: Các khối `iota` + `const()` là cách Go tạo enum mà không cần từ khóa chuyên dụng. Mẫu cờ bit ( `1 << iota` ) là phổ biến trong thư viện chuẩn ( `os.FileMode` , `net.Flag` ). Chuyển đổi loại luôn rõ ràng - Go từ chối các kiểu chuyển đổi ngầm định để tránh mất dữ liệu thầm lặng.
>
> **Caveat**: `iota` đặt lại về 0 tại **mỗi khối `const()` mới** — nếu bạn chia các hằng số thành hai khối riêng biệt thì quá trình đếm sẽ bắt đầu lại. Hơn nữa, `iota` không an toàn về loại trong packages : `Weekday(42)` biên dịch hoàn toàn tốt mặc dù 42 không phải là một ngày trong tuần hợp lệ.
>
> **Khi nào nên sử dụng**: Để khai báo các nhóm hằng số liên quan (biểu diễn enum, cờ bit, bộ quyền). Nếu cần biểu diễn chuỗi, hãy cung cấp phương thức `String()` hoặc sử dụng `go generate` cùng với `stringer` .

Các biến và hằng tạo thành nền tảng. Nhưng mã Go thực sự bắt đầu bằng `if` , `for` , `switch` — và đây là nơi Go khác biệt đáng kể so với C/Java: có ít từ khóa hơn nhưng mỗi từ khóa lại có nhiều khả năng hơn.

---

Các biến và hằng đều rõ ràng. Nhưng luồng điều khiển trong Go có các mẫu thành ngữ độc đáo - chúng ta hãy khám phá chúng.

### Ví dụ 2: Trung cấp — Luồng điều khiển & Mẫu thành ngữ

Bạn viết một trình xử lý với bốn lần kiểm tra `if err != nil` liên tiếp. Người đánh giá nhận xét: "sử dụng các câu lệnh init trong `if` để xác định phạm vi các biến" và "thay thế chuỗi if-else bằng `switch` ". Bạn đã quen với các vòng lặp `while` từ các ngôn ngữ khác, nhưng Go chỉ cung cấp `for` . Tại sao Go đề xuất `for range` thay vì `forEach` ? Và chính xác thì type switch là gì? Go luồng điều khiển được thiết kế có chủ ý để tối giản: một từ khóa `for` duy nhất thay thế `for` , `while` và `do-while` . Câu lệnh init `if` xác định phạm vi nghiêm ngặt của các biến — ngăn ngừa rò rỉ. Các câu lệnh `switch` không yêu cầu các lệnh gọi `break` rõ ràng (nó ẩn) và hỗ trợ đầy đủ các xác nhận kiểu.

Đầu vào: `if f, err := os.Open(...); err != nil {}` · Đầu ra: `err` nằm trong khối if và không bị rò rỉ ra bên ngoài```go
package main

import (
    "fmt"
    "os"
    "strings"
)

func main() {
    // ✅ if with init statement — err is tightly scoped to the if block
    if f, err := os.Open("config.yaml"); err != nil {
        fmt.Println("Error:", err)
    } else {
        defer f.Close()
        fmt.Println("Opened:", f.Name())
    }
    // f and err are inaccessible here — they are scoped directly to the if block

// ✅ for — GO ONLY POSSESSES 1 LOOP KEYWORD
    // Classic for (Go 1.22+ supports ranging over integers)
    for i := range 5 {
        fmt.Println(i)
    }

// While-style — omits the init and post statements
    count := 0
    for count < 10 {
        count++
    }

// Range over slice — i=index, v=COPY of element
    fruits := []string{"apple", "banana", "cherry"}
    for i, fruit := range fruits {
        fmt.Printf("%d: %s\n", i, fruit)
    }

// Range over map — ordering is NOT deterministic
    scores := map[string]int{"alice": 95, "bob": 87}
    for name, score := range scores {
        fmt.Printf("%s: %d\n", name, score)
    }

// Range over string — iterates over runes (Unicode code points), NOT bytes
    for i, r := range "Hello, 世界" {
        fmt.Printf("byte %d: %c (U+%04X)\n", i, r, r)
    }

// ✅ Switch — auto break; explicit break is NOT needed per case (unlike C/Java)
    day := "Monday"
    switch day {
    case "Monday", "Tuesday", "Wednesday", "Thursday", "Friday":
        fmt.Println("Weekday")
    case "Saturday", "Sunday":
        fmt.Println("Weekend")
    default:
        fmt.Println("Unknown")
    }

// ✅ Type switch — runtime type assertion
    var val interface{} = "hello"
    switch v := val.(type) {
    case string:
        fmt.Println("String:", strings.ToUpper(v))
    case int:
        fmt.Println("Int:", v*2)
    default:
        fmt.Printf("Unknown type: %T\n", v)
    }
}
```> **Tại sao Go thiếu vòng lặp `while` ?**
> Rob Pike ( Go đồng sáng tạo) đã nêu: _"Nếu bạn có `for` có thể làm mọi thứ, tại sao lại thêm `while` ?"_ `for condition {}` là một vòng lặp `while` ; `for {}` là một `do-while` hoặc vòng lặp vô hạn. Ít từ khóa hơn tương đương với việc giảm tải nhận thức và ít lỗi hơn khi tích cực chuyển đổi ngữ cảnh giữa các kiểu vòng lặp.
>
> **Tại sao câu lệnh `switch` tự động ngắt?**
> Trong C, việc quên [[C8]]] trong switch sẽ gây ra lỗi thất bại — được cho là một trong những lỗi sơ suất phổ biến nhất. Go đảo ngược mặc định một cách an toàn: mọi trường hợp đều tự động ngắt. Bạn phải sử dụng từ khóa `fallthrough` một cách rõ ràng khi bạn thực sự mong muốn hành vi đó. Kết quả là ít lỗi hơn và mục đích rõ ràng hơn.
>
> **Tại sao `range` trên chuỗi lặp lại bằng rune thay vì byte?**
> Chuỗi Go là chuỗi byte UTF-8. Việc lặp lại nghiêm ngặt theo byte sẽ cắt ngắn các ký tự nhiều byte (ví dụ: "世" = 3 byte). `range` tự động giải mã nó thành rune, trả về `(byte_index, rune)` — đảm bảo xử lý Unicode đúng cách mà không làm hỏng dữ liệu.

> **Kết luận**: Luồng điều khiển của Go giữ lại các từ khóa tối thiểu nhưng phù hợp với mọi trường hợp sử dụng. Các câu lệnh `if` init có phạm vi hoàn hảo, `for` đảm nhận quyền kiểm soát tất cả các cấu trúc vòng lặp và các câu lệnh `switch` tự động ngắt. Mỗi lựa chọn thiết kế sẽ loại bỏ một cách có hệ thống toàn bộ loại lỗi phổ biến thường thấy trong C/Java.
>
> **Cảnh báo**: `for range` trên maps **không mang tính quyết định về thứ tự** — nếu các thử nghiệm phụ thuộc vào thứ tự lặp lại, chúng sẽ thất bại ngẫu nhiên theo định kỳ. `fallthrough` trong một chuyển đổi hiếm khi được sử dụng và về cơ bản là khó hiểu — chỉ đưa ra nó khi hành vi thất bại hoàn toàn không thể thương lượng được.
>
> **Khi nào nên sử dụng**: `if` câu lệnh init khi cần xác định phạm vi (đặc biệt là đối với `err` ). `switch` khi gặp ≥ 3 nhánh có điều kiện. Nhập các công tắc khi quản lý động lực học `interface{}` hoặc `any` .

Logic điều khiển luồng điều khiển. Tuy nhiên, khi tài nguyên xuất hiện — xử lý tệp, kết nối database , khóa mutex — bạn phải đảm bảo nghiêm ngặt việc dọn dẹp chúng đúng cách bất kể hàm cuối cùng trả về ở đâu. Đây chính xác là nơi `defer` trở thành một điều cần thiết tuyệt đối.

---

Luồng điều khiển được xử lý an toàn. Hãy để chúng tôi chuyển sang lãnh thổ bấp bênh hơn: defer , panic và recover — vị trí chính xác nơi rò rỉ tài nguyên và sự cố sản xuất thường xuyên bắt nguồn.

### Ví dụ 3: Nâng cao — Defer , Panic , Recover & Pointers Bạn viết một hàm mở một tập tin, xử lý nó và trả về. Hàm này có ba đường dẫn trở lại. Mỗi đường dẫn phải gọi `f.Close()` . Bỏ lỡ một và bộ mô tả tập tin bị rò rỉ. `defer f.Close()` được đặt ngay sau `os.Open()` đảm bảo dọn dẹp bất kể đường dẫn nào thực thi.

Ví dụ này cũng bao gồm `panic` / `recover` cho các lỗi không thể khôi phục và ngữ nghĩa pointer cho các hoạt động sửa đổi tại chỗ.

Đầu vào: `defer f.Close()` sau `os.Open()` · Đầu ra: tệp luôn bị đóng, bất kể đường dẫn trở về```go
package main

import (
    "fmt"
    "os"
)

// ✅ Defer — operates on a LIFO stack, executing unconditionally when the parent function yields
func readFile(path string) error {
    f, err := os.Open(path)
    if err != nil {
        return err
    }
    defer f.Close()  // ✅ Guaranteed cleanup — runs even if a panic occurs later

// ... processing the file
    return nil
}

// ✅ Multiple defers — LIFO structure (Last In, First Out)
func multiDefer() {
    defer fmt.Println("1st defer")  // Initial push → executed last
    defer fmt.Println("2nd defer")
    defer fmt.Println("3rd defer")  // Final push → executed first
    // Standard Output: 3rd → 2nd → 1st
}

// ✅ Pointers — Go has pointers but no pointer arithmetic
func pointers() {
    x := 42
    p := &x     // &x = get the address of x
    *p = 100    // *p = dereference and modify the value at that address
    fmt.Println(x)  // 100 — x was modified through the pointer

// Passing a pointer lets the function modify the original variable
    y := 10
    double(&y)
    fmt.Println(y)  // 20

// new() allocates zeroed memory and returns a pointer
    n := new(int)  // *int, value = 0 (zero value)
    *n = 42
    fmt.Println(*n)
}

func double(n *int) {
    *n *= 2  // modifies the value at the address n points to
}

// ✅ Panic + Recover — only for truly unrecoverable errors
func safeDivide(a, b float64) (result float64, err error) {
    defer func() {
        if r := recover(); r != nil {
            err = fmt.Errorf("recovered: %v", r)
        }
    }()

if b == 0 {
        panic("division by zero")  // ❌ In production, return an error instead of panicking
    }
    return a / b, nil
}

func main() {
    multiDefer()
    pointers()

result, err := safeDivide(10, 0)
    fmt.Println(result, err)  // 0 recovered: division by zero
}
```> **Tại sao `defer` thay vì `finally` ?**
> `finally` của Java nằm cách xa tài nguyên mà nó dọn sạch — bạn mở một tệp ở dòng 10, đóng nó ở dòng 50. `defer` nằm ngay bên cạnh `Open()` , thể hiện rõ ý định: "tài nguyên này sẽ được dọn sạch." `defer` cũng chạy trong `panic` , đóng vai trò là `try-finally` và xử lý ngoại lệ trong một từ khóa.
>
> **Tại sao pointers không có pointer số học?**
> Pointer số học ( `ptr + offset` ) là nguyên nhân sâu xa gây ra lỗi tràn bộ đệm trong C. Go giữ pointers để sửa đổi tại chỗ và tránh các bản sao struct nhưng loại bỏ số học. garbage collector có thể theo dõi mọi pointer một cách an toàn. Đánh đổi: kém linh hoạt hơn, đảm bảo an toàn bộ nhớ.
>
> **Khi nào bạn nên sử dụng `panic` ?**
> Chỉ khi chương trình **không thể tiếp tục**: `init()` không tải được cấu hình cần thiết, một bất biến quan trọng bị vi phạm (lỗi lập trình) hoặc các mẫu `Must*` như `regexp.MustCompile` . Đối với các lỗi dự kiến, luôn luôn `return error` .

> **Kết luận**: Đặt `defer` ngay sau lệnh gọi `Open/Lock/Begin` . Chỉ sử dụng `panic` / `recover` cho các trạng thái thực sự không thể phục hồi — ưu tiên trả về `error` cho mọi trạng thái khác. Sử dụng pointers khi bạn cần sửa đổi tại chỗ hoặc muốn tránh sao chép lớn structs . Xem [03-defer-panic-recover.md](./03-defer-panic-recover.md) để tìm hiểu sâu hơn.

---

## 4. Cạm bẫy

Cú pháp rõ ràng. Mối nguy hiểm thực sự là mã trông có vẻ đúng nhưng lại bị lỗi âm thầm tại runtime hoặc trong quá trình xem lại mã.

| # | Mức độ nghiêm trọng | Cạm bẫy | Hậu quả | Sửa chữa |
| --- | --------- | ------------------------------------ | ------------------------------ | ----------------------------------------------- |
| 1 | 🔴 Gây tử vong | Viết cho `nil map` | Runtime panic — chương trình gặp sự cố | Sử dụng `make(map[K]V)` trước khi viết |
| 2 | 🔴 Gây tử vong | `defer` bên trong một vòng lặp | Bộ mô tả tệp đã cạn kiệt → OOM | Đóng bên trong thân vòng lặp hoặc trích xuất một hàm |
| 3 | 🟡 Chung | `:=` đổ bóng một biến trong phạm vi bên ngoài | Biến bên ngoài không thay đổi - lỗi im lặng | Sử dụng `=` để sửa đổi biến ngoài |
| 4 | 🟡 Chung | Sửa đổi biến vòng lặp `range` | Thay đổi bản sao, không phải bản gốc | Sử dụng `slice[i]` để sửa đổi tại chỗ |
| 5 | 🟡 Chung | Dựa vào thứ tự lặp map | Kiểm tra đôi khi thành công, ngẫu nhiên thất bại | Sắp xếp các khóa trước khi lặp |
| 6 | 🔵 Nhỏ | Các biến nhập hoặc biến không sử dụng | Lỗi biên dịch | Sử dụng `_` hoặc xóa mã không sử dụng |
| 7 | 🔵 Nhỏ | `fallthrough` không cần thiết trong switch | Làm người đánh giá bối rối | Dựa vào tính năng tự động ngắt; chỉ sử dụng `fallthrough` khi được yêu cầu |

Bây giờ bạn đã biết cách khai báo biến, điều khiển luồng và quản lý tài nguyên bằng `defer` . Bước tiếp theo: khám phá sâu từng chủ đề.

---

Nền tảng cú pháp và các bẫy thông thường được đề cập. Các tài liệu tham khảo bên dưới đi sâu hơn vào các quyết định thiết kế của Go .

## 5. GIỚI THIỆU

| Tài nguyên | Loại | Liên kết | Ghi chú |
| ------------------------------ | -------- | ------------------------------------------------------------------------- | ---------------------------------------- |
| Go Chuyến tham quan | Chính thức | [go.dev/tour](https://go.dev/tour/) | Phần giới thiệu tương tác về cú pháp Go |
| Có hiệu lực Go | Chính thức | [go.dev/doc/effective_go](https://go.dev/doc/effective_go) | Quy ước thành ngữ và thực tiễn tốt nhất |
| Go Thông số | Chính thức | [go.dev/ref/spec](https://go.dev/ref/spec) | Đặc tả ngôn ngữ có thẩm quyền |
| Go Blog — Cú pháp khai báo | Blog | [go.dev/blog/declaration-syntax](https://go.dev/blog/declaration-syntax) | Tại sao các khai báo Go lại đọc từ trái sang phải |

---

## 6. KHUYẾN NGHỊ Go những điều cơ bản được đề cập. Mỗi chủ đề dưới đây lấy một khái niệm từ bài viết này và khám phá nó một cách sâu sắc.

| Mở rộng sang | Khi nào | Lý do | Tập tin |
| ----------------------------- | --------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------ |
| Kiểm soát luồng & vòng lặp | Sâu hơn `for` , `switch` , `select` | Số nguyên phạm vi ( Go 1.22+), dấu ngắt có nhãn, công tắc loại | [02-control-flow-loops.md](./02-control-flow-loops.md) |
| Pointers & Bộ nhớ | Stack vs heap , escape analysis | Khi Go phân bổ trên heap so với stack — và tại sao nó quan trọng | [04-pointers-memory.md](./04-pointers-memory.md) |
| Defer , Panic , Recover | Mô hình dọn dẹp tài nguyên | Defer nắm bắt đối số, trả về được đặt tên, mẫu sản xuất | [03-defer-panic-recover.md](./03-defer-panic-recover.md) |
| Slices , Maps , Chuỗi | Kiểu dữ liệu phức tạp | Slice nội bộ, hành vi map , chuyển đổi chuỗi/[]byte | [../types/01-slices-maps-strings.md](../types/01-slices-maps-strings.md) |

---

**Điều hướng**: [← README](../README.md) · [→ Control Flow & Loops](./02-control-flow-loops.md)