<!-- tags: golang, structs --> # 🏷️ Struct Thẻ, Tùy chọn & Builder Mẫu

> **Ba mẫu xây dựng**: Thẻ Struct kiểm soát việc tuần tự hóa và xác thực ở cấp trường. Các tùy chọn chức năng tạo ra các hàm tạo linh hoạt với các giá trị mặc định hợp lý. Người xây dựng thực thi việc lắp ráp đối tượng từng bước với quá trình xác thực cuối cùng.

📅 Đã tạo: 23-03-2026 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 12 phút đọc

| Khía cạnh | Chi tiết |
| --- | --- |
| **Khái niệm** | Thẻ Struct , tùy chọn chức năng, mẫu builder |
| **Trường hợp sử dụng** | Tuần tự hóa JSON, xây dựng linh hoạt, lắp ráp từng bước |
| **Thông tin chi tiết quan trọng** | Thẻ là các chuỗi được phân tích cú pháp tại runtime thông qua sự phản chiếu - không biên dịch- time an toàn |
| ** Go stdlib** | `encoding/json` , `reflect` , `net/url` |

| Mô hình bên ngoài | Go Mẫu |
| --------------------------------- | ---------------------------------------- |
| Trang trí `@Column()` , `@Prop()` | Thẻ Struct : `json:"name"` , `gorm:"..."` |
| Quá tải hàm tạo | Hệ thống tùy chọn chức năng |
| Lớp mẫu Builder | Cấu trúc đột biến chuỗi pointer |

---

## 1. ĐỊNH NGHĨA

Thẻ `json:"-"` bị thiếu trên trường `Password` làm rò rỉ thông tin đăng nhập trong mọi phản hồi API. Một lỗi đánh máy trong `json:"naem"` đã âm thầm loại bỏ một trường khỏi đầu ra JSON. Cả hai lỗi đều không tạo ra cảnh báo biên dịch- time - thẻ struct là các chuỗi thô được phân tích cú pháp bằng sự phản chiếu tại runtime .

 Thẻ Struct kiểm soát cách các hệ thống bên ngoài (bộ mã hóa JSON, ORM, trình xác thực) diễn giải các trường struct . Các tùy chọn chức năng thay thế việc nạp chồng hàm tạo - mỗi tùy chọn là một closure làm thay đổi cấu hình mặc định. Phương thức chuỗi mẫu Builder gọi để tập hợp các đối tượng phức tạp, trì hoãn việc xác thực đến bước `Build()` cuối cùng.

### Struct Giải phẫu thẻ```text
type User struct {
    ID    uint   `json:"id" gorm:"primaryKey" validate:"required"`
    //            ↑json tag  ↑gorm tag         ↑validate tag
}
```### Hệ thống thẻ — Bảng tham khảo

| Hệ thống thẻ | Package | Mục đích |
| --- | --- | --- |
| `json:"name"` | `encoding/json` | Ánh xạ tên trường JSON |
| `gorm:"column"` | `gorm.io/gorm` | Liên kết cột Database |
| `validate:"required"` | `go-playground/validator` | Quy tắc xác thực đầu vào |
| `form:"field"` | Chất xơ/gin | Liên kết biểu mẫu/truy vấn HTTP |
| `env:"VAR"` | `caarlos0/env` | Ràng buộc biến môi trường |

Thẻ, tùy chọn, builder — ba mẫu, một mục tiêu chung: kiểm soát cách structs tương tác với thế giới bên ngoài hệ thống loại của Go . Hình ảnh bên dưới maps khi nào cần tiếp cận từng cái.

## 2. HÌNH ẢNH ![Tags options builder decision map](./images/02-tags-options-builder-decision-map.png) *Hình: Quyết định map định tuyến ba áp lực xây dựng — điều khiển format bên ngoài (thẻ), mặc định linh hoạt (tùy chọn chức năng) và lắp ráp tuần tự với xác thực ( builder ) — đến mẫu chính xác dựa trên hình dạng vấn đề.*

## 3. MÃ

### Ví dụ 1: Cơ bản — Thẻ Struct > **Mục tiêu**: Trình bày cách thẻ struct kiểm soát đầu ra JSON và ẩn các trường nhạy cảm.
> **Phương pháp tiếp cận**: Sử dụng `json:"-"` để loại trừ mật khẩu và `omitempty` để bỏ qua nil pointers .
> **Độ phức tạp**: Cơ bản```go
package main

import (
	"encoding/json"
	"fmt"
	"strings"
	"time"
)

type User struct {
	ID        uint      `json:"id" gorm:"primaryKey"`
	Name      string    `json:"name" gorm:"size:100" validate:"required"`
	Password  string    `json:"-" gorm:"size:255"` // Hidden from JSON output
	Bio       *string   `json:"bio,omitempty"`     // Skipped when nil
	CreatedAt time.Time `json:"created_at" gorm:"autoCreateTime"`
}

func main() {
	bio := "Gopher limits API logic"
	user := User{
		ID:        42,
		Name:      "Alice",
		Password:  "super-secret",
		Bio:       &bio,
		CreatedAt: time.Now(),
	}

	data, err := json.MarshalIndent(user, "", "  ")
	if err != nil {
		panic(err)
	}

	fmt.Println(string(data))
	fmt.Println("Password leaked?", strings.Contains(string(data), "super-secret"))
}
```> **Takeaway**: `json:"-"` ngăn trường xuất hiện trong đầu ra JSON. `omitempty` bỏ qua các trường có giá trị bằng 0. Thẻ là chuỗi - trình biên dịch không thể bắt lỗi chính tả. Chạy `go vet` để xác thực cú pháp thẻ.

### Ví dụ 2: Trung cấp — Mẫu tùy chọn chức năng

> **Mục tiêu**: Xây dựng một hàm khởi tạo linh hoạt hỗ trợ các tham số tùy chọn mà không làm gián đoạn các phương thức gọi hiện có.
> **Phương pháp tiếp cận**: Mỗi tùy chọn là một `func(*Server)` closure đặt một trường. Hàm tạo áp dụng các giá trị mặc định trước, sau đó lặp lại các tùy chọn.
> **Độ phức tạp**: Trung cấp```go
package main

import (
	"fmt"
	"time"
)

type Server struct {
	host         string
	port         int
	readTimeout  time.Duration
	enableTLS    bool
}

// Option is a function that modifies Server config.
type Option func(*Server)

func WithPort(port int) Option {
	return func(s *Server) {
		if port > 0 {
			s.port = port
		}
	}
}

func WithTLS() Option {
	return func(s *Server) { s.enableTLS = true }
}

// NewServer creates a Server with sensible defaults, then applies options.
func NewServer(host string, opts ...Option) *Server {
	s := &Server{
		host:        host,
		port:        8080,
		readTimeout: 15 * time.Second,
	}
	
	for _, opt := range opts {
		opt(s)
	}
	return s
}

func main() {
	customServer := NewServer("0.0.0.0", WithPort(3000), WithTLS())
	fmt.Printf("Server configured on %s:%d\n", customServer.host, customServer.port)
}
```> **Bài học rút ra**: Các tùy chọn chức năng tách biệt mối quan tâm về cấu hình khỏi hàm tạo. Việc thêm tùy chọn mới không làm thay đổi hàm tạo signature — khả năng tương thích ngược được giữ nguyên theo mặc định.

### Ví dụ 3: Mẫu nâng cao — Builder > **Mục tiêu**: Tập hợp truy vấn SQL từng bước, xác thực tất cả các trường bắt buộc trong lệnh gọi `Build()` cuối cùng.
> **Phương pháp tiếp cận**: Mỗi phương thức trả về `*QueryBuilder` cho chuỗi. `Build()` xác thực các trường bắt buộc trước khi tạo đầu ra.
> **Độ phức tạp**: Nâng cao```go
package main

import (
	"errors"
	"fmt"
	"strings"
)

type QueryBuilder struct {
	table      string
	conditions []string
	limit      int
}

func NewQuery(table string) *QueryBuilder {
	return &QueryBuilder{table: table}
}

func (q *QueryBuilder) Where(condition string) *QueryBuilder {
	q.conditions = append(q.conditions, condition)
	return q // Returns the same pointer — enables method chaining
}

func (q *QueryBuilder) Limit(n int) *QueryBuilder {
	q.limit = n
	return q
}

// Build assembles the final SQL string and validates required fields.
func (q *QueryBuilder) Build() (string, error) {
	if q.table == "" {
		return "", errors.New("table name required")
	}

	sql := "SELECT * FROM " + q.table
	if len(q.conditions) > 0 {
		sql += " WHERE " + strings.Join(q.conditions, " AND ")
	}
	if q.limit > 0 {
		sql += fmt.Sprintf(" LIMIT %d", q.limit)
	}
	return sql, nil
}

func main() {
	sql, err := NewQuery("users").Where("role = admin").Limit(20).Build()
	if err != nil {
		panic(err)
	}
	fmt.Println(sql)
}
```> **Takeaway**: Mẫu Builder trì hoãn xác thực thành `Build()` , ngăn các đối tượng được xây dựng một phần thoát ra. Mỗi phương thức xâu chuỗi sẽ tích lũy trạng thái; xác nhận chạy một lần ở cuối.

## 4. Cạm bẫy

 Mỗi thẻ Struct , tùy chọn chức năng và trình tạo đều có một chế độ lỗi riêng biệt.

| # | Mức độ nghiêm trọng | Khiếm khuyết | Sửa chữa |
|---|----------|--------|------|
| 1 | 🔴 Gây tử vong | Thiếu `json:"-"` trên các trường nhạy cảm (mật khẩu, mã thông báo) làm rò rỉ thông tin đăng nhập trong phản hồi API | Kiểm tra tất cả các trường struct chạm vào phản hồi HTTP — thêm `json:"-"` vào mọi trường bí mật |
| 2 | 🟡 Chung | Lỗi đánh máy thẻ ( `json:"naem"` thay vì `json:"name"` ) âm thầm loại bỏ trường khỏi đầu ra JSON | Chạy `go vet` trên mọi bản dựng - nó bắt các thẻ struct không đúng định dạng |
| 3 | 🟡 Chung | Việc sử dụng `omitempty` trên các trường `bool` sẽ làm giảm giá trị `false` — máy khách không nhận được trường nào thay vì `false` | Tránh `omitempty` trên các trường boolean trong đó `false` mang ý nghĩa ngữ nghĩa |

## 5. GIỚI THIỆU

| Tài nguyên | Liên kết |
| ------------ | ------------------------------------------------------------------------------ |
| Struct Thẻ | [pkg.go.dev/reflect#StructTag](https://pkg.go.dev/reflect#StructTag) |
| Có hiệu lực Go | [go.dev/doc/effective_go#embedding](https://go.dev/doc/effective_go#embedding) |

---