<!-- tags: golang, packages, modules --> # 📦 Packages & Modules > Go thực thi cách ly module nghiêm ngặt bằng các biểu đồ phụ thuộc chính xác, packages dựa trên thư mục và khả năng hiển thị do trình biên dịch thực thi.

📅 Đã tạo: 2026-03-20 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 15 phút đọc

| Khía cạnh | Chi tiết |
| --------------- | ----------------------------------------- |
| **Khái niệm** | Khai báo Module , bố cục package , quản lý phụ thuộc |
| **Trường hợp sử dụng** | Cấu trúc dự án, cách ly phụ thuộc, tổ chức mã |
| **Thông tin chi tiết quan trọng** | Package = thư mục. Chữ hoa = đã xuất. `internal/` = ranh giới được thực thi bởi trình biên dịch |
| **CLI** | `go mod` , `go get` , `go work` |

---

## 1. ĐỊNH NGHĨA

Sao chép any repo có cấu trúc tốt Go và bạn sẽ thấy ngay kiến trúc của nó: `cmd/` cho các điểm vào, `internal/` cho riêng tư packages , `pkg/` cho các thư viện dùng chung. Cây thư mục **là** biểu đồ module . Việc nhập từ `internal/` bên ngoài cha mẹ module sẽ gây ra lỗi trình biên dịch - không phải là quy ước, mà là sự đảm bảo cứng rắn.

> * `exportReport()` sống ở `internal/report` . Máy chủ API trong `cmd/server` nhập nó một cách tự do. Nhưng người tiêu dùng bên ngoài `go get` là module của bạn không thể - trình biên dịch chặn nó. Đây là `internal/` thực thi: zero-config encapsulation .*
>
> * Go Mô hình hiển thị của cũng đơn giản không kém: mã định danh chữ hoa = đã xuất, chữ thường = chưa xuất. Không có từ khóa `public` / `private` / `protected` . Một ký tự quyết định phạm vi truy cập.*

### Package Quy tắc Go thực thi **5 quy tắc cơ bản** cho tổ chức package :

| Quy tắc | Mô tả |
| -------------------------- | ---------------------------------- |
| Thư mục = Package | Mỗi thư mục là một package |
| Chữ hoa = Đã xuất | Mã định danh viết hoa là công khai |
| `internal/` Ranh giới | Trình biên dịch chặn nhập từ bên ngoài của `internal/` packages |
| `main` Điểm vào | Package `main` + `func main()` = nhị phân thực thi |
| Không nhập khẩu tuần hoàn | Trình biên dịch từ chối chu kỳ nhập |

**Tại sao hiển thị theo trường hợp?** Nó loại bỏ hoàn toàn các từ khóa `public` / `private` / `protected` . Nhìn lướt qua một cái tên sẽ cho bạn biết phạm vi truy cập của nó.

### Bố cục dự án (Tiêu chuẩn)```
project/
├── cmd/
│   ├── server/main.go       # API server entrypoint
│   └── worker/main.go       # Worker entrypoint
├── internal/                 # Private packages
│   ├── domain/               # Business entities
│   ├── usecase/              # Business logic
│   ├── repository/           # Data access
│   └── handler/              # HTTP handlers
├── pkg/                      # Public packages (reusable)
├── go.mod                    # Module definition
├── go.sum                    # Dependency checksums
└── Makefile
```**Tại sao có nhiều tệp nhị phân `cmd/` ?** Một module có thể tạo ra nhiều tệp thực thi (máy chủ API, nhân viên, công cụ CLI) trong khi chia sẻ `internal/` packages . Mỗi `cmd/*/main.go` là một mục tiêu xây dựng riêng biệt.

### đi mod Lệnh

| Lệnh | Mô tả |
| ---------------------- | ------------------------------- |
| `go mod init <module>` | Khởi tạo module mới |
| `go mod tidy` | Thêm phần còn thiếu, xóa phần phụ thuộc không sử dụng |
| `go mod download` | Tải các phần phụ thuộc xuống bộ đệm cục bộ |
| `go mod vendor` | Sao chép các phần phụ thuộc vào `vendor/` |
| `go mod graph` | In biểu đồ phụ thuộc module |
| `go get pkg@version` | Thêm hoặc nâng cấp phần phụ thuộc |
| `go work init` | Khởi tạo đa- module workspace |

**Tại sao nên chạy `go mod tidy` thường xuyên?** Nó loại bỏ các phần phụ thuộc không được sử dụng và thêm những phần phụ thuộc còn thiếu — giữ cho `go.mod` và `go.sum` chính xác. Các mục nhập cũ gây ra lỗi CI và lỗi nhập khó hiểu.

---

Các quy tắc là rõ ràng. Hình ảnh bên dưới maps cách packages , modules và ranh giới `internal/` tương tác trong một dự án thực.

## 2. HÌNH ẢNH

Hầu hết sự nhầm lẫn về Go packages xuất phát từ việc kết hợp các thư mục với đường dẫn nhập. Hình ảnh bên dưới maps mối quan hệ giữa cấu trúc thư mục, khai báo module và các ranh giới do trình biên dịch thực thi. ![Modules layout workflow](./images/01-modules-layout-workflow.png) *Hình: Bố cục Module hiển thị các ranh giới `cmd/` , `internal/` và `pkg/` với các mũi tên hướng nhập và các điểm thực thi trình biên dịch.*

Với mô hình này, các ví dụ mã bên dưới hiển thị từng lớp đang hoạt động - từ cấu trúc dự án cơ bản thông qua việc thực thi `internal/` đến đa module workspaces .

## 3. MÃ

Ba cấp độ tiến triển: cấu trúc dự án cơ bản, ranh giới package và đa module workspaces .

### Ví dụ 1: Cơ bản — Cấu trúc dự án

Bố cục dự án Go tiêu chuẩn với điểm vào `go.mod` , `cmd/` và phân lớp `internal/` packages .```go
// go.mod
module github.com/myorg/myapp

go 1.22

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/jackc/pgx/v5 v5.5.3
)
```

```go
// cmd/server/main.go — Entry point
package main

import (
    "log"
    "github.com/myorg/myapp/internal/handler"
    "github.com/myorg/myapp/internal/repository"
    "github.com/myorg/myapp/internal/usecase"
)

func main() {
    repo := repository.NewUserRepo("postgres://...")
    uc := usecase.NewUserUseCase(repo)
    h := handler.NewUserHandler(uc)

log.Fatal(h.Start(":8080"))
}
```

```go
// internal/domain/user.go — Domain entity
package domain

import "time"

type User struct {
    ID        int64
    Email     string
    FullName  string
    CreatedAt time.Time
}

// ✅ Exported interface — defines contract
type UserRepository interface {
    FindByID(id int64) (*User, error)
    Create(user *User) error
}
```

```go
// internal/repository/user_repo.go
package repository

import "github.com/myorg/myapp/internal/domain"

type userRepo struct {
    dsn string     // ✅ unexported
}

func NewUserRepo(dsn string) domain.UserRepository {
    return &userRepo{dsn: dsn}
}

func (r *userRepo) FindByID(id int64) (*domain.User, error) {
    // ... database query
    return nil, nil
}

func (r *userRepo) Create(user *domain.User) error {
    // ... database insert
    return nil
}
```> **Takeaway**: `cmd/` nối các phụ thuộc, `internal/` ẩn việc triển khai, `domain/` xác định hợp đồng. Cây thư mục là sơ đồ kiến ​​trúc.

---

### Ví dụ 2: Trung cấp — nội bộ/ Package Thư mục `internal/` được thực thi bởi trình biên dịch: chỉ cha mẹ module mới có thể nhập packages trong `internal/` . Người tiêu dùng bên ngoài gặp lỗi xây dựng.```go
// internal/auth/token.go — ONLY accessible by this module
package auth

import "errors"

var ErrInvalidToken = errors.New("invalid token")

// ✅ Exported within internal
func ValidateToken(token string) (int64, error) {
    if token == "" {
        return 0, ErrInvalidToken
    }
    // ... validate JWT
    return 42, nil
}

// unexported
func generateSecret() string {
    return "secret"
}
```

```
// ✅ Import rules:
// cmd/server/main.go      → CAN import internal/auth
// internal/handler/user.go → CAN import internal/auth
// external-module          → CANNOT import internal/auth ← blocked!
```> **Tại sao `internal/` ?** Nó cung cấp encapsulation mà không cần cấu hình. Không có thẻ xây dựng, không có công cụ sửa đổi truy cập — chỉ là tên thư mục mà trình biên dịch nhận ra.

> **Takeaway**: Sử dụng `internal/` cho any package không nên là một phần của API công khai của module của bạn. Trình biên dịch thực thi điều này một cách tự động.

---

### Ví dụ 3: Nâng cao — Go Workspace (Multi- module )

Khi một monorepo chứa nhiều modules phụ thuộc lẫn nhau, `go work` cho phép bạn phát triển chúng đồng thời mà không cần xuất bản các phiên bản trung gian.```bash
# ✅ Multi-module monorepo
mkdir myproject && cd myproject

# Module 1: shared library
mkdir -p libs/common && cd libs/common
go mod init github.com/myorg/common
cd ../..

# Module 2: API service
mkdir -p services/api && cd services/api
go mod init github.com/myorg/api
cd ../..

# ✅ Create workspace
go work init
go work use ./libs/common
go work use ./services/api
```

```go
// go.work
go 1.22

use (
    ./libs/common
    ./services/api
)
```> **Takeaway**: `go work` thay thế các lệnh `replace` để phát triển đa module cục bộ. Nó ở trong `.gitignore` và không gây ô nhiễm `go.mod` .

---

## 4. Cạm bẫy

Các quy tắc bố trí rất đơn giản. Những cái bẫy bên dưới bắt những đội bỏ qua `go mod tidy` hoặc sử dụng sai `internal/` .

| # | Mức độ nghiêm trọng | Lỗi | Hậu quả | Sửa chữa |
|---|----------|------|----------|------|
| 1 | 🔴 Gây tử vong | Nhập vòng tròn giữa packages | Trình biên dịch từ chối bản dựng | Tái cấu trúc các loại được chia sẻ thành một package | riêng biệt
| 2 | 🟡 Chung | Cũ `go.mod` với các phụ thuộc không được sử dụng | Lỗi CI, lỗi nhập khó hiểu | Chạy `go mod tidy` trước mỗi lần xác nhận |

---

## 5. GIỚI THIỆU

| Tài nguyên | Loại | Liên kết | Mô tả |
| -------------- | -------- | ------------------------------------------------------------------------------------------------ | ------- |
| Go Modules | Chính thức | [go.dev/ref/mod](https://go.dev/ref/mod) | Hoàn thành tham chiếu hệ thống module |
| Bố cục dự án | Cộng đồng | [github.com/golang-standards/project-layout](https://github.com/golang-standards/project-layout) | Cấu trúc dự án chuẩn cộng đồng |
| Go Workspaces | Chính thức | [go.dev/doc/tutorial/workspaces](https://go.dev/doc/tutorial/workspaces) | Multi- module workspace hướng dẫn |

---

## 6. KHUYẾN NGHỊ

Nền tảng của ** Packages & Modules ** đã được giải quyết. Tiện ích mở rộng bên dưới kết nối với quy trình công việc workspace và vendoring .

| Gia hạn | Khi nào | Tại sao | Tệp/Liên kết |
| ------- | ------- | ----- | --------- |
| Go Workspaces & Vendoring | Multi- module repos, bản dựng ngoại tuyến, đăng ký riêng tư | Bao gồm `go work` , `vendor/` , `GOPRIVATE` | [02-workspaces-vendoring.md](./02-workspaces-vendoring.md) |

**Điều hướng**: [← Errors](../errors/) · [→ Testing](../testing/)