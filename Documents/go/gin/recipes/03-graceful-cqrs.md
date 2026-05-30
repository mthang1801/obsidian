<!-- tags: golang --> # 🔄 Mẫu CQRS — NestJS @nestjs/cqrs → Phân tách lệnh/truy vấn

> **Thư viện**: Tách biệt các mô hình đọc và ghi bằng trình xử lý Lệnh/Truy vấn với luồng dữ liệu rõ ràng.

📅 Cập nhật: 2026-04-19 · ⏱️ 12 phút đọc

## 1. ĐỊNH NGHĨA

CQRS chia các hoạt động đọc và ghi thành các loại trình xử lý riêng biệt. NestJS có `@nestjs/cqrs` với `CommandBus` / `QueryBus` . Trong Go, bạn triển khai điều này dưới dạng cấu trúc đơn giản với phương thức `Handle(ctx, input)` — không cần trừu tượng hóa bus cho hầu hết các dự án.

| NestJS | Gin / Đi |
| ------------------------------------ | ------------------------------------------ |
| `CommandBus.execute(command)` | `handler.Handle(ctx, command)` gọi trực tiếp |
| `QueryBus.execute(query)` | `handler.Handle(ctx, query)` gọi trực tiếp |
| `@CommandHandler(CreateUserCommand)` | `type CreateUserHandler struct` |
| `EventBus.publish(event)` | Xe buýt sự kiện dựa trên kênh hoặc giao diện |
| `@EventsHandler(UserCreatedEvent)` | `type UserCreatedHandler struct` |

### Bất biến chính

- **Lệnh trả về dữ liệu tối thiểu.** Trình xử lý lệnh chỉ trả về ID hoặc lỗi — không phải toàn bộ thực thể.
- **Truy vấn không bao giờ thay đổi trạng thái.** Nếu trình xử lý truy vấn gọi `db.Save()` , sự phân tách bị phá vỡ.

## 2. HÌNH ẢNH ![CQRS pattern — Command (write) vs Query (read) separation](./images/03-cqrs-pattern.png) *Hình: CQRS — Đường dẫn lệnh (POST/PUT/DELETE → xác thực → ghi vào DB chính) được tách biệt khỏi đường dẫn Truy vấn (GET → đọc từ kho lưu trữ/bộ đệm được tối ưu hóa). Mở rộng quy mô độc lập, trách nhiệm rõ ràng.*```mermaid
flowchart LR
    A["POST /users"] --> B["Gin Handler"]
    B -->|"bind + validate"| C["CreateUserHandler"]
    C -->|"write"| D[("Write DB")]
    E["GET /users/:id"] --> F["Gin Handler"]
    F --> G["GetUserHandler"]
    G -->|"read"| H[("Read DB / Cache")]
```*Hình: Ranh giới CQRS - Các tuyến POST đi qua trình xử lý lệnh (đường dẫn ghi); Các tuyến GET đi qua trình xử lý truy vấn (đọc đường dẫn). Mỗi đường dẫn có thể mở rộng quy mô độc lập.*

### Lệnh và Truy vấn```text
Command: POST/PUT/DELETE → validates → mutates → returns ID or error
Query:   GET              → reads     → returns DTO (never mutates)
```## 3. MÃ

### Ví dụ 1: Cơ bản — Trình xử lý lệnh```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Command handler: validates input, hashes password,
    // creates user, returns minimal result (ID + email).
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package commands

    import "context"

    type CreateUserCommand struct {
        Name     string
        Email    string
        Password string
    }

    type CreateUserHandler struct {
        userRepo UserRepository
        hasher   PasswordHasher
    }

    func NewCreateUserHandler(repo UserRepository, hasher PasswordHasher) *CreateUserHandler {
        return &CreateUserHandler{userRepo: repo, hasher: hasher}
    }

    type CreateUserResult struct {
        ID    string
        Email string
    }

    func (h *CreateUserHandler) Handle(ctx context.Context, cmd CreateUserCommand) (*CreateUserResult, error) {
        exists, _ := h.userRepo.ExistsByEmail(ctx, cmd.Email)
        if exists {
            return nil, ErrEmailTaken
        }

        hashed, err := h.hasher.Hash(cmd.Password)
        if err != nil {
            return nil, err
        }

        user := &User{Name: cmd.Name, Email: cmd.Email, Password: hashed}
        if err := h.userRepo.Create(ctx, user); err != nil {
            return nil, err
        }

        return &CreateUserResult{ID: user.ID, Email: user.Email}, nil
    }
```### Ví dụ 2: Trung cấp — Trình xử lý truy vấn```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Query handler: reads from read-optimized repo,
    // returns DTO directly — no mutation, no side effects.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package queries

    import "context"

    type GetUserQuery struct {
        ID string
    }

    type UserDTO struct {
        ID        string `json:"id"`
        Name      string `json:"name"`
        Email     string `json:"email"`
        CreatedAt string `json:"created_at"`
    }

    type GetUserHandler struct {
        readRepo UserReadRepository 
    }

    func NewGetUserHandler(repo UserReadRepository) *GetUserHandler {
        return &GetUserHandler{readRepo: repo}
    }

    func (h *GetUserHandler) Handle(ctx context.Context, q GetUserQuery) (*UserDTO, error) {
        return h.readRepo.FindByID(ctx, q.ID)
    }
```### Ví dụ 3: Nâng cao — Đấu dây CQRS trong Gin Handler```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Wiring CQRS: Gin handler delegates to command/query
    // handlers. Handler never contains business logic.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package http

    import (
        "net/http"
        "myapp/internal/application/commands"
        "myapp/internal/application/queries"
        "github.com/gin-gonic/gin"
    )

    type UserHandler struct {
        createUser *commands.CreateUserHandler
        getUser    *queries.GetUserHandler
    }

    func NewUserHandler(
        createUser *commands.CreateUserHandler,
        getUser *queries.GetUserHandler,
    ) *UserHandler {
        return &UserHandler{createUser: createUser, getUser: getUser}
    }

    func (h *UserHandler) Create(c *gin.Context) {
        var req struct {
            Name     string `json:"name" binding:"required"`
            Email    string `json:"email" binding:"required,email"`
            Password string `json:"password" binding:"required,min=8"`
        }
        if err := c.ShouldBindJSON(&req); err != nil {
            c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
            return
        }

        result, err := h.createUser.Handle(c.Request.Context(), commands.CreateUserCommand{
            Name:     req.Name,
            Email:    req.Email,
            Password: req.Password,
        })
        if err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
            return
        }

        c.JSON(http.StatusCreated, gin.H{"data": result})
    }

    func (h *UserHandler) Get(c *gin.Context) {
        result, err := h.getUser.Handle(c.Request.Context(), queries.GetUserQuery{
            ID: c.Param("id"),
        })
        if err != nil {
            c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
            return
        }

        c.JSON(http.StatusOK, gin.H{"data": result})
    }
```---

## 4. Cạm bẫy

| # | Mức độ nghiêm trọng | Khiếm khuyết | Tác động | Sửa chữa |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Gây tử vong | Trình xử lý truy vấn gọi `db.Save()` hoặc `db.Create()` | Phá vỡ sự phân tách đọc/ghi; đọc bản sao xem dữ liệu cũ | Truy vấn chỉ được gọi các phương thức kho lưu trữ chỉ đọc |
| 2 | 🟡 Chung | Sử dụng CQRS cho CRUD đơn giản không có phân kỳ đọc/ghi | Thêm bản tóm tắt xử lý mà không mang lại lợi ích | Chỉ áp dụng CQRS khi các mô hình đọc và ghi thực sự khác nhau |

---

## 5. GIỚI THIỆU

| Tài nguyên | Liên kết |
| --- | --- |
| Fowler CQRS | [martinfowler.com/bliki/CQRS.html](https://martinfowler.com/bliki/CQRS.html) |

---

## 6. KHUYẾN NGHỊ

| Gia hạn | Khi nào | Cơ sở lý luận | Tài nguyên |
| --- | --- | --- | --- |
| Cơ sở dữ liệu/ORM | Khi bạn cần duy trì các thực thể CQRS | Mẫu kho lưu trữ tích hợp rõ ràng với trình xử lý lệnh/truy vấn | [../techniques/02-database-orm.md](../techniques/02-database-orm.md) |