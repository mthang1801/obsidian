<!-- tags: golang, error-handling --> # 🔗 Lỗi Sentinel, Gói & lỗi.Join — Go Mẫu lỗi

> Go 1.13+ được giới thiệu error wrapping với `%w` . Go 1.20 đã thêm `errors.Join` để tổng hợp nhiều lỗi. Cùng với các biến trọng điểm và các loại tùy chỉnh, các công cụ này hình thành nên khả năng xử lý lỗi hoàn chỉnh của Go strategy .

📅 Đã tạo: 23-03-2026 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 14 phút đọc

| TS/NestJS | Go |
| ----------------------------------- | ------------------------------------------ |
| `throw new Error("msg")` | `errors.New("msg")` |
| `class NotFoundError extends Error` | `var ErrNotFound = errors.New("not found")` |
| `error.cause` | `fmt.Errorf("...: %w", err)` |
| `AggregateError` | `errors.Join(err1, err2)` ( Go 1.20+) |
| `instanceof NotFoundError` | `errors.Is(err, ErrNotFound)` |
| `error as CustomError` | `errors.As(err, &target)` |

| Khía cạnh | Chi tiết |
| --------------- | ------------------------------------------------------------- |
| **Khái niệm** | Lỗi trọng điểm, gói ngữ nghĩa và tổng hợp nhiều lỗi |
| **Trường hợp sử dụng** | Định tuyến lỗi an toàn loại trên các lớp dịch vụ |
| **Thông tin chi tiết quan trọng** | `errors.Is()` đi khắp chuỗi để tìm trận đấu trọng điểm |
| ** Go tục ngữ** | "Lỗi là giá trị — lập trình với chúng" |

---

## 1. ĐỊNH NGHĨA `GetUser(id)` của bạn trả về `"not found"` dưới dạng một chuỗi. Nhưng "không tìm thấy" có hai nghĩa khác nhau: một bản ghi database bị thiếu (trả về HTTP 404) và thời gian chờ mạng trong đó database không thể truy cập được (trả về HTTP 503). So sánh `err.Error() == "not found"` không thể phân biệt được chúng. Khi trình điều khiển database cập nhật thông báo của nó từ `"not found"` thành `"no rows in result set"` , phép so sánh của bạn sẽ không hoạt động — không có lỗi biên dịch, không có lỗi kiểm tra, chỉ là mã trạng thái HTTP sai trong quá trình sản xuất.

Lỗi Sentinel giải quyết điều này. `var ErrNotFound = errors.New("not found")` tạo ra pointer ổn định. `errors.Is(err, ErrNotFound)` so sánh theo danh tính, không phải theo nội dung chuỗi. Người lái xe có thể tự do thay đổi tin nhắn của mình — việc kiểm tra trọng điểm của bạn vẫn hoạt động.

Nhưng chỉ lính gác thôi thì chưa đủ. Khi kho lưu trữ đưa lỗi GORM vào trọng điểm của bạn, bạn sẽ mất dấu vết stack ban đầu. `fmt.Errorf("UserRepo.FindByID: %w", err)` bảo tồn chuỗi. Và khi quá trình xác thực tạo ra ba lỗi cùng một lúc, `errors.Join` sẽ tổng hợp chúng thành một lỗi duy nhất mà `errors.Is` vẫn có thể kiểm tra.

### Mẫu lỗi kiến trúc

| Kỹ thuật | Mô tả | Trường hợp sử dụng |
| ------------------- | ----------------------------------------------------- | -------------------------------------------- |
| **Lỗi trọng điểm** | Package -level `var ErrFoo = errors.New(...)` | Kiểm tra danh tính ổn định trên packages |
| **Gói `%w` ** | `fmt.Errorf("context: %w", err)` bảo toàn chuỗi | Thêm mẩu bánh mì trong khi vẫn giữ nguyên nguyên nhân gốc rễ |
| ** `errors.Is` ** | Đi theo chuỗi để phù hợp với một lính canh cụ thể | Quyết định định tuyến (404 so với 500) |
| ** `errors.As` ** | Đi theo chuỗi để trích xuất một loại lỗi cụ thể | Truy cập siêu dữ liệu (mã HTTP, tên hoạt động) |
| ** `errors.Join` ** | Tổng hợp nhiều lỗi thành một ( Go 1.20+) | Lỗi xác thực, hoạt động hàng loạt |

### Chế độ lỗi

| # | Mức độ nghiêm trọng | Khiếm khuyết | Hậu quả | Sửa chữa |
| --- | --------- | ---------------------------------------- | --------------------------------------------- | --------------------------------------------------- |
| 1 | 🔴 Gây tử vong | Tạo `errors.New()` bên trong một hàm | Mỗi lệnh gọi trả về một pointer khác nhau — `errors.Is` không bao giờ khớp | Xác định trọng điểm ở cấp độ package là `var` |
| 2 | 🔴 Gây tử vong | Thiếu `Unwrap()` trên loại custom error | `errors.Is/As` không thể đi qua nó | Triển khai `Unwrap() error` trên mọi loại trình bao bọc |
| 3 | 🟡 Chung | Quên `nil` kiểm tra sau `errors.Join` | `errors.Join` trả về `nil` khi không có lỗi nào — an toàn, nhưng người gọi có thể không mong đợi điều đó | Tài liệu tham gia trống = nil |

---

Với lý thuyết đã được thiết lập, hình ảnh bên dưới cho thấy cách trọng điểm, gói và liên kết tương tác với nhau trong kiến trúc dịch vụ thực tế.

## 2. HÌNH ẢNH

Phần khó nhất trong việc xử lý lỗi là nhìn thấy chuỗi. Ba lớp gói tạo ra một danh sách lỗi được liên kết. `errors.Is` duyệt danh sách này từ trên xuống dưới. `errors.Join` tạo một cây thay vì danh sách — một lỗi với nhiều con. ![Sentinel wrapping join decision map](./images/02-sentinel-wrapping-join-decision-map.png) *Hình: Quyết định map để lựa chọn giữa trọng điểm, gói, loại tùy chỉnh và tham gia. Bắt đầu với tùy chọn đơn giản nhất (sentinel) và chỉ chuyển lên cấp cao hơn khi trường hợp sử dụng yêu cầu tổng hợp hoặc siêu dữ liệu phong phú hơn.*

Với quyết định map được định tuyến, phần mã bên dưới thể hiện từng mẫu một cách riêng biệt và sau đó kết hợp chúng trong trình xử lý lỗi kiểu sản xuất.

## 3. MÃ

Quyết định map được thiết lập. Giờ đây, chúng tôi neo từng nhánh trong mã: lỗi trọng điểm để so sánh ổn định, gói chuỗi để theo dõi đường dẫn cuộc gọi, loại tùy chỉnh cho siêu dữ liệu có cấu trúc và `errors.Join` để xác thực nhiều lỗi.

### Ví dụ 1: Cơ bản — Lỗi Sentinel

Ứng dụng của bạn có sáu chế độ lỗi phổ biến: không tìm thấy, trái phép, bị cấm, xung đột, xác thực và lỗi nội bộ. Mỗi người cần một danh tính ổn định mà người gọi có thể kiểm tra mà không cần phân tích chuỗi.

> **Mục tiêu**: Xác định các lỗi trọng điểm cấp độ package với nhận dạng pointer ổn định.
> **Phương pháp tiếp cận**: `var ErrNotFound = errors.New("not found")` ở cấp độ package — một pointer , được chia sẻ giữa tất cả người gọi.
> **Quy tắc**: Không bao giờ tạo trọng điểm bên trong hàm. `errors.New()` bên trong một hàm trả về một pointer mới trên mỗi lệnh gọi — `errors.Is` sẽ không bao giờ khớp.```go
package apperror

import "errors"

// ✅ Sentinel errors — package-level constants
// Convention: Err prefix + PascalCase name
var (
	ErrNotFound      = errors.New("not found")
	ErrUnauthorized  = errors.New("unauthorized")
	ErrForbidden     = errors.New("forbidden")
	ErrConflict      = errors.New("conflict")
	ErrValidation    = errors.New("validation error")
	ErrInternal      = errors.New("internal server error")
)

// Usage:
//   return apperror.ErrNotFound
//   if errors.Is(err, apperror.ErrNotFound) { ... }
```> **Kết luận**: Các biến trọng điểm cung cấp cho người gọi một mục tiêu so sánh ổn định. `errors.Is(err, apperror.ErrNotFound)` hoạt động bất kể có bao nhiêu lớp bao bọc lỗi. Giá trị canh gác pointer không bao giờ thay đổi — không giống như các tin nhắn chuỗi, sẽ âm thầm ngắt khi được nâng cấp.
>
> **Khi nào nên sử dụng**: Xuất thông tin cảnh báo khi người gọi từ packages khác cần khớp với các điều kiện lỗi cụ thể. Giữ chúng trong một `apperror` package chuyên dụng để có thể khám phá.

Người canh gác xác định *điều gì* đã xảy ra. Nhưng khi bạn cần theo dõi *ở đâu* thì nó đã sai — kho lưu trữ nào, dịch vụ nào, tham số nào — việc gói sẽ thêm ngữ cảnh đó.

---

### Ví dụ 2: Chuỗi trung gian — Error Wrapping Trình xử lý HTTP của bạn gọi một dịch vụ gọi một kho lưu trữ. Kho lưu trữ maps lỗi GORM vào trọng điểm của bạn. Dịch vụ bao bọc nó bằng tên hoạt động. Trình xử lý kiểm tra trọng điểm và trả về trạng thái HTTP chính xác.

> **Mục tiêu**: Xây dựng chuỗi gói 3 lớp (kho lưu trữ → dịch vụ → trình xử lý) để duy trì danh tính trọng điểm.
> **Phương pháp tiếp cận**: Lỗi kho lưu trữ maps ORM đối với trọng điểm ứng dụng. Dịch vụ kết thúc bằng `%w` . Trình xử lý kiểm tra với `errors.Is` .
> **Ví dụ**: `FindByID` trả về `apperror.ErrNotFound` . `GetByID` bao bọc nó bằng ID người dùng. Trình xử lý khớp `ErrNotFound` qua chuỗi và trả về HTTP 404.```go
package service

import (
	"context"
	"errors"
	"fmt"

	"myapp/internal/apperror"

	"gorm.io/gorm"
	"github.com/gofiber/fiber/v2"
)

// ✅ Repository — maps ORM error to app sentinel
func (r *UserRepo) FindByID(ctx context.Context, id string) (*User, error) {
	var user User
	err := r.db.WithContext(ctx).First(&user, "id = ?", id).Error
	if errors.Is(err, gorm.ErrRecordNotFound) {
		// Map ORM error → app sentinel
		return nil, apperror.ErrNotFound
	}
	if err != nil {
		return nil, fmt.Errorf("UserRepo.FindByID: %w", err)
	}
	return &user, nil
}

// ✅ Service — wraps with operation context
func (s *UserService) GetByID(ctx context.Context, id string) (*User, error) {
	user, err := s.repo.FindByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("UserService.GetByID(%s): %w", id, err)
	}
	return user, nil
}

// ✅ Handler — checks sentinel through the wrapping chain
func handler(c fiber.Ctx) error {
	user, err := userService.GetByID(c.Context(), c.Params("id"))
	if err != nil {
		// errors.Is traverses: handler wrap → service wrap → sentinel ✅
		if errors.Is(err, apperror.ErrNotFound) {
			return fiber.NewError(404, "user not found")
		}
		return err // → 500
	}
	return c.JSON(user)
}
```> **Tại sao map GORM lại xảy ra lỗi với bộ phận giám sát ứng dụng?**
> Người xử lý của bạn không nên biết về GORM . Nếu bạn chuyển từ GORM sang `pgx` , mọi kiểm tra `errors.Is(err, gorm.ErrRecordNotFound)` trong lớp xử lý sẽ bị hỏng. Kho lưu trữ dịch các lỗi cụ thể ORM thành các trọng điểm cấp ứng dụng. Trình xử lý chỉ phụ thuộc vào việc triển khai `apperror.ErrNotFound` - database vẫn bị ẩn sau ranh giới kho lưu trữ.
>
> **Kết luận**: Chuỗi gói đọc giống như một lệnh gọi stack : `UserService.GetByID(abc123): not found` . Mỗi lớp thêm chính xác một phần bối cảnh. `errors.Is` đi theo chuỗi từ trên xuống dưới và tìm thấy trọng điểm ở gốc.

Sentinel + gói bao gồm việc kiểm tra danh tính bằng ngữ cảnh. Nhưng khi trình xử lý lỗi của bạn cần dữ liệu có cấu trúc - mã trạng thái HTTP, phần mở rộng loại lỗi, thông báo hướng tới người dùng - loại custom error mang siêu dữ liệu đó.

---

### Ví dụ 3: Nâng cao — Custom Error Loại + lỗi.Như

API của bạn trả về phản hồi lỗi JSON với trường `type` ( `NOT_FOUND` , `BAD_REQUEST` ), mã trạng thái HTTP và thông báo mà con người có thể đọc được. Một `error` interface đơn giản không thể mang các trường này. Bạn cần một struct .

> **Mục tiêu**: Xây dựng loại custom error mang trạng thái HTTP, loại lỗi, thông báo và nguyên nhân cơ bản.
> **Cách tiếp cận**: `AppError` struct với `Error()` và `Unwrap()` . Trình trợ giúp của hàm xây dựng thực thi tính nhất quán. Trình xử lý lỗi trung tâm sử dụng `errors.As` để trích xuất struct .
> **Ví dụ**: Trình xử lý gọi `errors.As(err, &appErr)` để trích xuất mã trạng thái HTTP và trả về phản hồi JSON có cấu trúc.```go
package apperror

import "fmt"

// ✅ Custom error type — carries structured metadata
type AppError struct {
	Code    int    // HTTP status code
	Type    string // Error type slug (NOT_FOUND, BAD_REQUEST)
	Message string // User-facing message
	Cause   error  // Original error (wrapped)
}

func (e *AppError) Error() string {
	if e.Cause != nil {
		return fmt.Sprintf("%s: %v", e.Message, e.Cause)
	}
	return e.Message
}

// ✅ Unwrap — allows errors.Is/As to traverse through AppError
func (e *AppError) Unwrap() error {
	return e.Cause
}

// ✅ Constructors — enforce consistent creation
func NewNotFound(msg string, cause error) *AppError {
	return &AppError{Code: 404, Type: "NOT_FOUND", Message: msg, Cause: cause}
}

func NewBadRequest(msg string, cause error) *AppError {
	return &AppError{Code: 400, Type: "BAD_REQUEST", Message: msg, Cause: cause}
}

// ✅ Central error handler — errors.As extracts the AppError struct
func errorHandler(c fiber.Ctx, err error) error {
	var appErr *AppError
	if errors.As(err, &appErr) {
		return c.Status(appErr.Code).JSON(fiber.Map{
			"type":    appErr.Type,
			"message": appErr.Message,
		})
	}
	// Fallback — unknown error type
	return c.Status(500).JSON(fiber.Map{"message": "internal error"})
}
```> **Tại sao `errors.As` thay vì type assertion ?**
> type assertion `err.(*AppError)` trực tiếp chỉ phù hợp với lỗi cấp cao nhất. Nếu `AppError` được gói trong một lỗi khác, xác nhận sẽ không thành công. `errors.As` đi qua toàn bộ chuỗi - nó tìm thấy `AppError` thậm chí qua nhiều lớp gói. Điều này làm cho trình xử lý lỗi của bạn có khả năng phục hồi tốt trước những thay đổi về gói trong tương lai.
>
> **Kết luận**: Các loại lỗi tùy chỉnh biến Go 's `error` interface thành dữ liệu có cấu trúc. Trình xử lý lỗi trung tâm sử dụng `errors.As` một lần, trích xuất tất cả siêu dữ liệu trong một lần kiểm tra. Các loại lỗi mới (ví dụ: `NewForbidden` , `NewConflict` ) được đưa vào mà không thay đổi logic xử lý.

Các loại tùy chỉnh xử lý các lỗi đơn lẻ bằng siêu dữ liệu. Nhưng việc xác thực thường xuyên tạo ra nhiều lỗi cùng một lúc. Go 1.20's `errors.Join` giải quyết vấn đề này.

---

### Ví dụ 4: Expert — error.Join ( Go 1.20+)

Hàm `validateUser` của bạn sẽ kiểm tra tên, email và tuổi. Cả ba đều có thể thất bại một cách độc lập. Thay vì quay lại lần thất bại đầu tiên, bạn thu thập tất cả các lỗi và trả lại chúng như một lỗi.

> **Mục tiêu**: Tổng hợp nhiều lỗi xác thực thành một giá trị `error` mà `errors.Is` vẫn có thể kiểm tra.
> **Phương pháp tiếp cận**: Thu thập lỗi vào một `[]error` slice . `errors.Join(errs...)` kết hợp chúng. Trả về `nil` khi slice trống.
> **Ví dụ**: `validateUser` với tên trống và tuổi không hợp lệ sẽ trả về cả hai lỗi trong một giá trị.```go
package validation

import "errors"

// ✅ Multi-error validation using errors.Join (Go 1.20+)
func validateUser(u *User) error {
	var errs []error

	if u.Name == "" {
		errs = append(errs, errors.New("name is required"))
	}
	if u.Email == "" {
		errs = append(errs, errors.New("email is required"))
	}
	if u.Age < 18 {
		errs = append(errs, errors.New("must be 18+"))
	}

	// Returns nil if errs is empty — no wrapper, no allocation
	return errors.Join(errs...)
}

// Usage:
// err := validateUser(user)
// if err != nil {
//     fmt.Println(err)
//     // name is required
//     // must be 18+
// }
// errors.Is(err, specificErr) still works — Join preserves Is/As traversal
```> **Tại sao `errors.Join` thay vì `ValidationError` struct tùy chỉnh ?**
> `errors.Join` là một hàm thư viện tiêu chuẩn — không có kiểu tùy chỉnh, không có bản soạn sẵn. Nó trả về `nil` khi không có lỗi nào, điều này giúp loại bỏ sự cần thiết phải kiểm tra `if len(errs) > 0` . Và `errors.Is` có thể kiểm tra từng lỗi riêng lẻ bên trong kết quả đã nối. Đối với hầu hết các trường hợp sử dụng xác thực, `errors.Join` đơn giản hơn struct chuyên dụng.
>
> **Khi nào nên ưu tiên một tùy chỉnh struct **: Khi bạn cần các trường có cấu trúc (mã HTTP, tên trường, quy tắc xác thực) được đính kèm với mỗi lỗi. Trong trường hợp đó, hãy tạo một `ValidationError` struct và nối nhiều phiên bản.
>
> **Kết luận**: `errors.Join` tổng hợp nhiều lỗi độc lập thành một giá trị lỗi. `errors.Is` kiểm tra từng đứa trẻ. Kết hợp với các lỗi nghiêm trọng, điều này bao gồm việc xác thực hàng loạt, các hoạt động song song và dọn dẹp trong đó nhiều bước có thể bị lỗi một cách độc lập.

---

## 4. Cạm bẫy

Cú pháp của canh gác, gói và nối rất đơn giản. Các lỗi ẩn giấu trong việc sử dụng sai mục đích một cách tinh vi trong quá trình biên dịch, vượt qua các bài kiểm tra và gián đoạn trong quá trình sản xuất.

| # | Mức độ nghiêm trọng | Khiếm khuyết | Hậu quả | Sửa chữa |
| --- | --------- | -------------------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------- |
| 1 | 🔴 Gây tử vong | Sử dụng `%v` thay vì `%w` | Ngắt chuỗi - `errors.Is/As` trả về sai | Luôn sử dụng `%w` trong `fmt.Errorf` |
| 2 | 🔴 Gây tử vong | Tạo trọng điểm bên trong các hàm | Mỗi cuộc gọi trả về một pointer mới — `errors.Is` không bao giờ khớp | Xác định trọng điểm ở cấp độ package là `var` |
| 3 | 🟡 Chung | Bao bọc quá mức ở mọi lớp | Thông báo lỗi trở thành chuỗi 300 ký tự | Chỉ gói khi lớp thêm ngữ cảnh mới |
| 4 | 🟡 Chung | Ghi nhật ký và gói ở cùng một lớp | Lỗi tương tự xuất hiện hai lần trong nhật ký | Hoặc ghi hoặc gói - không phải cả hai |
| 5 | 🔵 Nhỏ | Bỏ qua giá trị trả về `errors.Join` của `nil` | An toàn nhưng đáng ngạc nhiên - việc tham gia không có lỗi nào trả về `nil` , không phải lỗi trống | Tài liệu tham gia trống = nil |

---

## 5. GIỚI THIỆU

| Tài nguyên | Loại | Liên kết | Ghi chú |
| --------------- | -------- | ------------------------------------------------------------------------ | ---------------------------------------------- |
| Go Blog | Chính thức | [go.dev/blog/go1.13-errors](https://go.dev/blog/go1.13-errors) | Giới thiệu `%w` , `errors.Is` , `errors.As` |
| Có hiệu lực Go | Chính thức | [go.dev/doc/effective_go#errors](https://go.dev/doc/effective_go#errors) | Các mẫu và quy ước xử lý lỗi thành ngữ |

---

## 6. KHUYẾN NGHỊ

Các lỗi trọng điểm, cách gói, loại tùy chỉnh và phép nối đều được đề cập. Bước tiếp theo phụ thuộc vào việc bạn cần xem lại những điều cơ bản hay đi sâu vào kiểm tra chuỗi lỗi.

| Mở rộng | Khi nào | Cơ sở lý luận | Tệp/Liên kết |
| -------------- | ---------------------------------------- | ---------------------------------------------------------------- | -------------------------------------------------- |
| Error Wrapping Khái niệm cơ bản | Khi bạn cần ôn lại các nguyên tắc cơ bản về `%w` , `errors.Is/As` | Bao gồm ba ví dụ về mã (cơ bản, trung cấp, nâng cao) từ đầu | [01-wrapping-custom.md](./01-wrapping-custom.md) |

---

**Điều hướng**: [← Error Wrapping](./01-wrapping-custom.md) · [→ Interfaces](../interfaces/01-implicit-io-patterns.md)