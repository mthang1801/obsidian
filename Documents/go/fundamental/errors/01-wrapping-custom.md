<!-- tags: golang, error-handling --> # ❌ Xử lý lỗi — Wrapping, Sentinel, Custom Error

> Go coi lỗi là giá trị — không có ngoại lệ, không thử bắt. Bạn gói các lỗi với ngữ cảnh bằng cách sử dụng `%w` , kiểm tra chuỗi bằng `errors.Is()` và trích xuất các loại có cấu trúc bằng `errors.As()` .

📅 Đã tạo: 20-03-2026 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 17 phút đọc

| Khía cạnh | Chi tiết |
| --------------- | ---------------------------------------------- |
| **Khái niệm** | Lỗi gói, lỗi trọng điểm, loại custom error |
| **Trường hợp sử dụng** | Xử lý lỗi có cấu trúc trên các lớp dịch vụ |
| **Thông tin chi tiết quan trọng** | `%w` bảo toàn chuỗi; `errors.Is/As` kiểm tra nó |
| ** Go tục ngữ** | "Đừng chỉ kiểm tra lỗi, hãy xử lý chúng một cách khéo léo" |

---

## 1. ĐỊNH NGHĨA

Trình xử lý API của bạn gọi một dịch vụ, dịch vụ này gọi một kho lưu trữ, gọi là PostgreSQL. Truy vấn không thành công với `connection refused` . Nhật ký xử lý: `"something went wrong"` . Ba giờ sau, kỹ sư trực vẫn không thể tìm ra nguyên nhân gốc rễ vì mỗi lớp đều nuốt lỗi ban đầu và thay thế bằng một chuỗi mới.

Đây là vấn đề Go của error wrapping giải quyết. Mỗi lớp thêm ngữ cảnh riêng của nó — tên hàm, giá trị tham số, mô tả hoạt động — trong khi vẫn giữ nguyên lỗi ban đầu ở cuối chuỗi. Khi lỗi đến trình xử lý, `errors.Is(err, pgx.ErrNoRows)` vẫn trả về `true` , thậm chí thông qua ba lớp gói. Kỹ sư đọc một dòng nhật ký và biết chính xác truy vấn nào, tham số nào và lỗi cơ sở hạ tầng nào đã gây ra sự cố.

Nhưng có một cái bẫy. Sử dụng `%v` thay vì `%w` trong `fmt.Errorf` âm thầm phá vỡ chuỗi. Thông báo lỗi trông giống hệt trong nhật ký, nhưng `errors.Is` ngừng hoạt động. Các bài kiểm tra vượt qua vì chúng so sánh các chuỗi. Việc ngừng sản xuất do phần mềm trung gian kiểm tra các loại lỗi.

### 1.1 Loại lỗi — 4 mẫu Go cung cấp bốn mẫu lỗi. Mỗi cái phục vụ một mục đích khác nhau:

| Loại | Mô tả | Trường hợp sử dụng |
| --------------- | ------------------------------------ | --------------------------------------------- |
| **Trọng điểm** | Package -biến xuất cấp | `var ErrNotFound = errors.New("not found")` |
| **Loại tùy chỉnh** | Struct triển khai `error` interface | Mang trạng thái HTTP, tên hoạt động, siêu dữ liệu |
| **Đã gói** | Chuỗi lỗi thông qua `fmt.Errorf("context: %w", err)` | Thêm mẩu bánh mì trong khi vẫn bảo tồn nguyên nhân gốc rễ |
| **Đục** | Trả về `error` mà không để lộ nội bộ | Ẩn chi tiết triển khai trên các ranh giới package |

> **Tại sao có lỗi trọng điểm?** Việc so sánh các chuỗi lỗi rất dễ vỡ. Nếu trình điều khiển database thay đổi `"not found"` thành `"no rows"` , kiểm tra `err.Error() == "not found"` của bạn sẽ im lặng. Các biến quan trọng như `ErrNotFound` cung cấp cho bạn mục tiêu so sánh ổn định, an toàn về loại thông qua `errors.Is(err, ErrNotFound)` .

### 1.2 Hàm lỗi ( Go 1.13+)

| Chức năng | Mô tả |
| ---------------------------- | ----------------------------------------------- |
| `errors.New("msg")` | Tạo một giá trị lỗi đơn giản |
| `fmt.Errorf("ctx: %w", err)` | Bao bọc lỗi bằng ngữ cảnh bổ sung |
| `errors.Is(err, target)` | Đi theo chuỗi và kiểm tra một lính canh cụ thể |
| `errors.As(err, &target)` | Đi theo chuỗi và trích xuất một loại lỗi cụ thể |
| `errors.Unwrap(err)` | Trả về lỗi tiếp theo trong chuỗi |
| `errors.Join(err1, err2)` | Kết hợp nhiều lỗi thành một ( Go 1.20+) |

> **Tại sao `%w` thay vì `%v` ?** `%v` chuyển lỗi được gói thành một chuỗi phẳng — `errors.Is` và `errors.As` không thể đi qua chuỗi được nữa. `%w` giữ nguyên lỗi ban đầu dưới dạng giá trị được liên kết, giữ cho toàn bộ chuỗi có thể kiểm tra được.

### 1.3 Các kiểu lỗi

| # | Mức độ nghiêm trọng | Khiếm khuyết | Hậu quả | Sửa chữa |
|---|----------|-------------------------------------------------|-------------------------------------------------------|------------------------------------------------|
| 1 | 🔴 Gây tử vong | Sử dụng `%v` thay vì `%w` | Lỗi đứt chuỗi; `errors.Is` trả về sai | Luôn sử dụng `%w` khi gói lỗi |
| 2 | 🔴 Gây tử vong | So sánh các chuỗi lỗi ( `err.Error() == "..."` ) | Ngắt khi thông báo lỗi thay đổi | Sử dụng các biến trọng điểm với `errors.Is` |
| 3 | 🟠 Thiếu tá | Gọi `panic` cho các lỗi dự kiến ​​| Sự cố toàn bộ quá trình | Trả về `error` cho các điều kiện dự kiến ​​|
| 4 | 🟡 Chung | Gói gọn từng lớp mà không tăng thêm giá trị | Thông điệp tường trình trở thành chuỗi không thể đọc được | Chỉ thêm ngữ cảnh khi nó cung cấp thông tin mới |

---

Bốn loại lỗi và chức năng của chúng tạo thành nền tảng. Hình ảnh bên dưới cho thấy cách gói tạo nên một chuỗi — và cách `errors.Is` đi qua chuỗi đó.

## 2. HÌNH ẢNH

Khía cạnh nguy hiểm nhất của việc xử lý lỗi không phải là cú pháp - đó là chuỗi vô hình. Khi ba lớp, mỗi lớp bao bọc một lỗi, nhà phát triển cần xem đường dẫn mở gói đầy đủ để hiểu lý do tại sao `errors.Is` khớp hoặc không thành công. ![Error wrapping workflow](./images/01-wrapping-custom-workflow.png) *Hình: Lỗi gói chuỗi từ kho lưu trữ thông qua dịch vụ đến trình xử lý. Mỗi gói `%w` sẽ giữ nguyên lỗi ban đầu. `errors.Is` đi qua toàn bộ chuỗi từ trên xuống dưới. Sử dụng `%v` tại lớp any sẽ cắt đứt chuỗi vĩnh viễn.*

Với cơ chế chuỗi hiển thị, phần mã bên dưới thể hiện ba kiểu leo thang: lỗi trọng điểm khi bao bọc, custom error loại với `errors.As` và chuỗi nhiều lớp với `errors.Join` .

## 3. MÃ

Với **Xử lý lỗi — Gói, Trọng điểm, Lỗi tùy chỉnh**, chuỗi gói sẽ rõ ràng. Bây giờ chúng tôi map mã hóa: lỗi trọng điểm để so sánh ổn định, loại tùy chỉnh cho siêu dữ liệu phong phú và `errors.Join` để tổng hợp các lỗi xác thực.

### Ví dụ 1: Cơ bản — Lỗi Sentinel & Gói

Bạn mở một tập tin config. Tập tin không tồn tại. Hàm của bạn sẽ xử lý lỗi bằng đường dẫn tệp và người gọi sẽ kiểm tra `os.ErrNotExist` thông qua chuỗi. Một gói, một kiểm tra - mẫu đơn giản nhất.

> **Mục tiêu**: Bao bọc lỗi `os` bằng ngữ cảnh và xác minh lỗi đó thông qua chuỗi bằng cách sử dụng `errors.Is` .
> **Phương pháp**: `fmt.Errorf("readConfig(%s): %w", path, err)` bảo toàn chuỗi. `errors.Is(err, os.ErrNotExist)` đi ngang qua nó.
> **Ví dụ**: `readConfig("/nonexistent")` → lỗi gói → `errors.Is` vẫn tìm thấy `os.ErrNotExist` .```go
package main

import (
    "errors"
    "fmt"
    "os"
)

// ✅ Sentinel errors — package level, exported
var (
    ErrNotFound     = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
    ErrForbidden    = errors.New("forbidden")
)

// ✅ Always check errors — Go idiom #1
func readConfig(path string) ([]byte, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        // ✅ Wrap with context using %w — preserve error chain
        return nil, fmt.Errorf("readConfig(%s): %w", path, err)
    }
    return data, nil
}

func main() {
    data, err := readConfig("/nonexistent")
    if err != nil {
        fmt.Println("Error:", err)
        // Error: readConfig(/nonexistent): open /nonexistent: no such file or directory

        // ✅ errors.Is() traverses the chain — finds os.ErrNotExist despite wrapping
        if errors.Is(err, os.ErrNotExist) {
            fmt.Println("File does not exist")
        }
        return
    }
    fmt.Println(string(data))
}
```> **Kết luận**: `%w` thêm đường dẫn tệp để gỡ lỗi mà không làm đứt chuỗi. Người gọi sử dụng `errors.Is` để khớp với `os.ErrNotExist` thông qua gói. Nếu bạn thay thế `%w` bằng `%v` , nhật ký trông giống nhau — nhưng `errors.Is` âm thầm ngừng hoạt động.
>
> **Khi nào nên sử dụng**: Lỗi Sentinel hoạt động hiệu quả nhất khi người gọi từ packages khác cần kiểm tra các điều kiện cụ thể. Xuất trọng điểm ( `var ErrNotFound` ) và bọc ngữ cảnh ở mỗi lớp.

Lỗi Sentinel xử lý việc kiểm tra danh tính đơn giản. Nhưng khi bạn cần mang siêu dữ liệu có cấu trúc — mã trạng thái HTTP, tên hoạt động, ID yêu cầu — loại custom error là công cụ phù hợp.

---

### Ví dụ 2: Loại trung cấp — Custom Error API của bạn trả về HTTP 404, nhưng trình xử lý không thể trích xuất mã trạng thái từ `error` đơn giản. Bạn cần một `struct` thỏa mãn `error` interface trong khi mang các trường cho mã HTTP, tên hoạt động và lỗi cơ bản.

> **Mục tiêu**: Xây dựng loại custom error mang siêu dữ liệu có cấu trúc và hỗ trợ truyền tải chuỗi `errors.Is` / `errors.As` .
> **Cách tiếp cận**: `AppError` struct với các phương thức `Error()` và `Unwrap()` . Trình trợ giúp của nhà xây dựng thực thi việc tạo nhất quán.
> **Ví dụ**: `GetUser(42)` trả về `AppError` . Trình xử lý trích xuất mã trạng thái HTTP thông qua `errors.As` .```go
package main

import (
    "errors"
    "fmt"
    "net/http"
)

// ✅ Custom error type — carries structured context
type AppError struct {
    Code    int    `json:"code"`
    Message string `json:"message"`
    Op      string `json:"op"`    // Operation that failed
    Err     error  `json:"-"`     // Underlying error (wrapped)
}

func (e *AppError) Error() string {
    if e.Err != nil {
        return fmt.Sprintf("[%s] %s: %v", e.Op, e.Message, e.Err)
    }
    return fmt.Sprintf("[%s] %s", e.Op, e.Message)
}

// ✅ Implement Unwrap() so errors.Is/As can traverse through AppError
func (e *AppError) Unwrap() error {
    return e.Err
}

// ✅ Constructor helpers — enforcing consistent error creation
func NewNotFoundError(op string, err error) *AppError {
    return &AppError{Code: http.StatusNotFound, Message: "not found", Op: op, Err: err}
}

func NewValidationError(op, msg string) *AppError {
    return &AppError{Code: http.StatusBadRequest, Message: msg, Op: op}
}

// ✅ Service using custom errors
var ErrUserNotFound = errors.New("user not found")

func GetUser(id int64) (*struct{ Name string }, error) {
    if id <= 0 {
        return nil, NewValidationError("GetUser", "id must be positive")
    }
    return nil, NewNotFoundError("GetUser", fmt.Errorf("id=%d: %w", id, ErrUserNotFound))
}

func main() {
    _, err := GetUser(42)
    if err != nil {
        // ✅ errors.Is — sentinel check through the chain
        if errors.Is(err, ErrUserNotFound) {
            fmt.Println("User not found!")
        }

        // ✅ errors.As — extract typed error to access structured fields
        var appErr *AppError
        if errors.As(err, &appErr) {
            fmt.Printf("HTTP %d: %s (op: %s)\n", appErr.Code, appErr.Message, appErr.Op)
        }
    }
}
```> **Tại sao lại có cả `errors.Is` và `errors.As` ?**
> `errors.Is` câu trả lời "liệu lính gác cụ thể này có ở đâu đó trong chuỗi không?" - kiểm tra danh tính boolean. `errors.As` trả lời "có `*AppError` ở đâu đó trong chuỗi không, và nếu có, hãy cho tôi tài liệu tham khảo về nó." Bạn cần cả hai: `Is` để đưa ra quyết định định tuyến, `As` để trích xuất siêu dữ liệu như mã trạng thái HTTP hoặc tên hoạt động.
>
> **Kết luận**: Các loại lỗi tùy chỉnh chuyển lỗi từ chuỗi mờ thành dữ liệu có cấu trúc. `Unwrap()` giữ cho chuỗi có thể đi qua được. Trình trợ giúp của trình xây dựng thực thi việc tạo nhất quán trên toàn bộ cơ sở mã.

Các loại tùy chỉnh xử lý các lỗi đơn lẻ bằng siêu dữ liệu phong phú. Nhưng việc xác thực thường không thành công vì nhiều lý do cùng một lúc — thiếu tên, email không hợp lệ, mật khẩu yếu. Go [[C8]]] của 1.20 tổng hợp chúng thành một giá trị lỗi duy nhất.

---

### Ví dụ 3: Nâng cao — Error Wrapping Chuỗi & Nhiều lỗi

Trình xử lý của bạn gọi một dịch vụ gọi một kho lưu trữ. Mỗi lớp bao bọc lỗi bằng tên hàm của nó. Thông báo lỗi cuối cùng có nội dung giống như một cuộc gọi stack : `handler.GetUser: service.GetUser: query users WHERE id=42: connection refused` . Trong khi đó, chức năng xác thực của bạn thu thập nhiều lỗi và trả về chúng dưới dạng một lỗi.

> **Mục tiêu**: Xây dựng chuỗi gói 3 lớp và tổng hợp nhiều lỗi xác thực với `errors.Join` .
> **Phương pháp tiếp cận**: Mỗi lớp sử dụng `fmt.Errorf("layer: %w", err)` . Quá trình xác thực thu thập các lỗi vào một slice và nối chúng lại.
> **Ví dụ**: `handler_GetUser(42)` tạo ra lỗi đường dẫn cuộc gọi đầy đủ. `validateUser("", "a")` tạo ra hai lỗi trong một.```go
package main

import (
    "errors"
    "fmt"
)

// ✅ Error wrapping chain — each layer adds its context
func repository_FindUser(id int64) error {
    return fmt.Errorf("query users WHERE id=%d: %w", id, errors.New("connection refused"))
}

func service_GetUser(id int64) error {
    err := repository_FindUser(id)
    if err != nil {
        return fmt.Errorf("service.GetUser: %w", err)
    }
    return nil
}

func handler_GetUser(id int64) error {
    err := service_GetUser(id)
    if err != nil {
        return fmt.Errorf("handler.GetUser: %w", err)
    }
    return nil
}

// ✅ Multi-error — aggregate validation failures into one error
func validateUser(name, email string) error {
    var errs []error
    if name == "" {
        errs = append(errs, errors.New("name is required"))
    }
    if email == "" {
        errs = append(errs, errors.New("email is required"))
    }
    if len(email) > 0 && len(email) < 5 {
        errs = append(errs, errors.New("email too short"))
    }
    return errors.Join(errs...)  // nil if no errors ← elegant!
}

func main() {
    // ✅ Error chain shows full call path
    err := handler_GetUser(42)
    fmt.Println(err)
    // handler.GetUser: service.GetUser: query users WHERE id=42: connection refused

    // ✅ Multi-error — both failures reported in one value
    err = validateUser("", "a")
    if err != nil {
        fmt.Println(err)
        // name is required
        // email too short
    }
}
```> **Tại sao phải gói lớp thay vì ghi lại từng lớp?**
> Việc ghi nhật ký ở mỗi lớp sẽ tạo ra các thông báo trùng lặp — cùng một lỗi xuất hiện ba lần trong ba tệp nhật ký. Việc gói sẽ trì hoãn quyết định ghi nhật ký ở lớp trên cùng (trình xử lý hoặc phần mềm trung gian). Mỗi lớp đóng góp bối cảnh; chỉ lớp trên cùng mới quyết định đăng nhập, trả về HTTP hay kích hoạt cảnh báo.
>
> **Kết luận**: Chuỗi gói tạo ra đường dẫn cuộc gọi có cấu trúc. `errors.Join` ( Go 1.20+) tổng hợp nhiều lỗi độc lập thành một lỗi mà `errors.Is` vẫn có thể kiểm tra. Cả hai mẫu đều xử lý lỗi rõ ràng mà không trùng lặp đầu ra nhật ký.

---

## 4. Cạm bẫy

Cú pháp xử lý lỗi rất đơn giản. Mối nguy hiểm thực sự là mã biên dịch, vượt qua các bài kiểm tra và âm thầm phá vỡ trong quá trình sản xuất.

| # | Mức độ nghiêm trọng | Lỗi | Hậu quả | Sửa chữa |
|---|----------|--------------------------------------------------------|------------------------------------------------------|-------------------------------------------------------------------|
| 1 | 🔴 Gây tử vong | Sử dụng `%v` thay vì `%w` trong `fmt.Errorf` | đứt dây chuyền; `errors.Is/As` trả về sai | Luôn sử dụng `%w` để duy trì chuỗi lỗi |
| 2 | 🔴 Gây tử vong | So sánh `err.Error() == "not found"` | Bị ngắt khi văn bản thông báo lỗi thay đổi | Xác định các biến trọng điểm; sử dụng `errors.Is(err, ErrNotFound)` |
| 3 | 🟡 Chung | Bao bọc cùng một lỗi ở mọi lớp | Đầu ra nhật ký trở thành chuỗi 200 ký tự không thể đọc được | Chỉ thêm ngữ cảnh khi lớp cung cấp thông tin mới |
| 4 | 🟡 Chung | Gọi `panic` để tìm lỗi logic nghiệp vụ | Sự cố quá trình; không có sự xuống cấp duyên dáng | Dự trữ `panic` cho các lỗi lập trình; trả về `error` nếu không thì |
| 5 | 🔵 Nhỏ | Quên `Unwrap()` trên các loại custom error | `errors.Is/As` không thể duyệt qua loại | Triển khai `Unwrap() error` trên mọi loại trình bao bọc |

---

## 5. GIỚI THIỆU

| Tài nguyên | Loại | Liên kết | Ghi chú |
| -------------- | -------- | ------------------------------------------------------------------------ | -------------------------------------- |
| Go Lỗi Blog | Chính thức | [go.dev/blog/go1.13-errors](https://go.dev/blog/go1.13-errors) | Giới thiệu `%w` , `errors.Is` , `errors.As` |
| Có hiệu lực Go | Chính thức | [go.dev/doc/effective_go#errors](https://go.dev/doc/effective_go#errors) | Quy ước xử lý lỗi thành ngữ |

---

## 6. KHUYẾN NGHỊ

Lỗi gói và các loại tùy chỉnh được bảo hiểm. Bước tiếp theo phụ thuộc vào việc bạn cần cơ chế chuỗi sâu hơn hay một miền lỗi hoàn toàn khác.

| Mở rộng | Khi nào | Cơ sở lý luận | Tệp/Liên kết |
| --------------------- | ------------------------------ | ---------------------------------------------------------------- | ------------------------------------------------- |
| Sentinel + Gói + Tham gia | Khi kết hợp lính canh, chuỗi gói và mẫu nhiều lỗi | Đi sâu vào `errors.Join` ( Go 1.20+), `errors.Is` với các lính gác được bao bọc và kiểm tra nhiều lỗi | [02-sentinel-wrapping-join.md](./02-sentinel-wrapping-join.md) |

---

**Điều hướng**: [← Interfaces](../interfaces/README.md) · [→ Sentinel, Wrapping, Join](./02-sentinel-wrapping-join.md)