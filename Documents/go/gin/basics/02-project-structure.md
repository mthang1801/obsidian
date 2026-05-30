<!-- tags: golang, structs, modules --> # 🏗️ Cấu trúc dự án — Mô-đun NestJS → Kiến trúc Go Gin

> **Thư viện**: Ánh xạ mẫu Mô-đun/Bộ điều khiển/Dịch vụ của NestJS tới kiến trúc dựa trên gói của Go trong Gin.

📅 Đã cập nhật: 19-04-2026 · ⏱️ 15 phút đọc

## 1. ĐỊNH NGHĨA

NestJS sử dụng các trình trang trí ( `@Controller` , `@Injectable` , `@Module` ) để sắp xếp mã thành các mô-đun được chèn phụ thuộc. Go không có khung DI — bạn sắp xếp theo **gói** và kết nối các phần phụ thuộc theo cách thủ công thông qua các hàm khởi tạo.

| Khái niệm NestJS | Tương đương Gin |
| --------------------- | ------------------------------ |
| `@Controller()` | Cấu trúc trình xử lý với các phương thức `*gin.Context` |
| `@Injectable()` | Cấu trúc dịch vụ, được đưa vào thông qua hàm tạo |
| `@Module()` | Hàm `RegisterRoutes(r *gin.RouterGroup)` |
| `@Inject()` | Tham số hàm tạo: `NewHandler(svc *Service)` |
| `main.ts bootstrap` | `cmd/api/main.go` với hệ thống dây điện thủ công |
| DTO (trình xác thực lớp) | Cấu trúc với thẻ `binding:"required"` |

### Bất biến chính

- **Một gói cho mỗi tên miền** (ví dụ: `internal/users/` ). Chu kỳ nhập trong Go là lỗi biên dịch chứ không phải cảnh báo.
- **Trình xử lý phụ thuộc vào Dịch vụ, Dịch vụ phụ thuộc vào Kho lưu trữ.** Không bao giờ nhập trình xử lý từ dịch vụ.

## 2. HÌNH ẢNH ![Layered architecture — cmd/ bootstraps, internal/ contains domain packages](./images/02-project-architecture.png) *Hình: Cấu trúc dự án Go Gin — `cmd/api/main.go` nối các phần phụ thuộc vào các gói miền ( `internal/user` , `internal/product` ), mỗi phần sau một trình xử lý → dịch vụ → phân lớp kho lưu trữ.*```mermaid
flowchart TD
    A["cmd/api/main.go"] -->|"wire"| B["internal/user"]
    B --> C["handler.go"]
    C --> D["service.go"]
    D --> E["repository.go"]
    E --> F[("PostgreSQL")]
    A -->|"wire"| G["internal/product"]
    G --> H["handler.go"]
```*Hình: Kiến trúc phân lớp — `cmd/` khởi động ứng dụng, `internal/` chứa các gói miền, mỗi gói có trình xử lý → dịch vụ → kho lưu trữ.*

### Luồng phụ thuộc```text
cmd/api/main.go
    │
    ├── Creates *gorm.DB, *gin.Engine
    ├── Wires: repo := NewRepository(db)
    ├── Wires: svc  := NewService(repo)
    ├── Wires: handler := NewHandler(svc)
    └── Calls: RegisterRoutes(router, handler)
```## 3. MÃ

### Ví dụ 1: Cơ bản — Trình xử lý cấu trúc```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Handler struct holds a service dependency. Methods map to HTTP routes.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package users

    import (
        "net/http"
        "github.com/gin-gonic/gin"
    )

    type Handler struct {
        service *Service 
    }

    func NewHandler(service *Service) *Handler {
        return &Handler{service: service}
    }

    func (h *Handler) List(c *gin.Context) {
        users, err := h.service.FindAll(c.Request.Context())
        if err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
            return
        }
        c.JSON(http.StatusOK, gin.H{"data": users})
    }

    func (h *Handler) GetByID(c *gin.Context) {
        id := c.Param("id")
        user, err := h.service.FindByID(c.Request.Context(), id)
        if err != nil {
            c.JSON(http.StatusNotFound, gin.H{"error": "user not found"})
            return
        }
        c.JSON(http.StatusOK, gin.H{"data": user})
    }
```### Ví dụ 2: Giao diện trung gian — Dịch vụ + Kho lưu trữ```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Service depends on a Repository interface, not a concrete type.
    // This allows swapping implementations for testing.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package users

    import "context"

    type Service struct {
        repo Repository 
    }

    func NewService(repo Repository) *Service {
        return &Service{repo: repo}
    }

    func (s *Service) FindAll(ctx context.Context) ([]User, error) {
        return s.repo.FindAll(ctx)
    }

    func (s *Service) FindByID(ctx context.Context, id string) (*User, error) {
        return s.repo.FindByID(ctx, id)
    }

    type Repository interface {
        FindAll(ctx context.Context) ([]User, error)
        FindByID(ctx context.Context, id string) (*User, error)
        Create(ctx context.Context, user *User) (*User, error)
    }
```### Ví dụ 3: Nâng cao — Chức năng đăng ký lộ trình```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Each domain package exports a RegisterRoutes function.
    // main.go calls it to mount the package’s endpoints on the router.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package users

    import "github.com/gin-gonic/gin"

    func RegisterRoutes(r *gin.RouterGroup, service *Service) {
        handler := NewHandler(service)

        users := r.Group("/users")
        {
            users.GET("", handler.List)
            users.GET("/:id", handler.GetByID)
            users.POST("", handler.Create)
        }
    }
```---

## 4. Cạm bẫy

| # | Mức độ nghiêm trọng | Khiếm khuyết | Tác động | Sửa chữa |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Gây tử vong | Đưa tất cả các trình xử lý, dịch vụ và mô hình vào một gói | Chu kỳ nhập khẩu không thể bị phá vỡ; khối nguyên khối không thể kiểm chứng | Một gói cho mỗi miền: `internal/users/` , `internal/orders/` |
| 2 | 🔴 Gây tử vong | Trình xử lý gọi trực tiếp cơ sở dữ liệu (bỏ qua lớp dịch vụ) | Logic nghiệp vụ nằm rải rác trên các trình xử lý HTTP; không tái sử dụng | Trình xử lý → Dịch vụ → Kho lưu trữ; xử lý chỉ gọi phương thức dịch vụ |

---

## 5. GIỚI THIỆU

| Tài nguyên | Liên kết |
| --- | --- |
| Bố cục NestJS | [docs.nestjs.com/controllers](https://docs.nestjs.com/controllers) |
| Bố cục chuẩn | [github.com/golang-standards/project-layout](https://github.com/golang-standards/project-layout) |

---

## 6. KHUYẾN NGHỊ

| Gia hạn | Khi nào | Cơ sở lý luận | Tài nguyên |
| --- | --- | --- | --- |
| Định tuyến | Khi bạn cần nhóm tuyến đường, phiên bản hoặc thông số đường dẫn | Xây dựng trên mẫu `RegisterRoutes` để tổ chức các API phức tạp | [../routing/01-groups-params.md](../routing/01-groups-params.md) |