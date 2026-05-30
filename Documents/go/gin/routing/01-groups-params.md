<!-- tags: golang --> # 🛤️ Định tuyến - Nhóm, Thông số, Phiên bản

> **Thư viện**: Sắp xếp các tuyến đường với `RouterGroup` , trích xuất thông số đường dẫn/truy vấn và áp dụng phần mềm trung gian cho các nhóm cụ thể.

📅 Cập nhật: 2026-04-19 · ⏱️ 12 phút đọc

## 1. ĐỊNH NGHĨA `RouterGroup` của Gin cho phép bạn thêm tiền tố vào các tuyến đường, đính kèm phần mềm trung gian vào các tập hợp con và các nhóm lồng nhau để phân cấp tài nguyên. Nếu không có nhóm, mọi tuyến đường sẽ lặp lại phần đính kèm tiền tố và phần mềm trung gian — một cơn ác mộng về bảo trì trong các API có hơn 50 điểm cuối.

| Tính năng | Vai trò | Cú pháp |
| -------------- | ---------------------------------------- | --------------------------------- |
| **Tiền tố** | Tiền tố URL được chia sẻ cho một nhóm tuyến đường | `r.Group("/api/v1")` |
| **Phần mềm trung gian** | Chạy trên mọi tuyến đường trong nhóm | `r.Group("/", authMiddleware)` |
| **Lồng nhau** | Các nhóm con cho hệ thống phân cấp tài nguyên | `v1.Group("/users")` |
| **Tĩnh** | Phục vụ các tập tin từ một thư mục cục bộ | `r.Static("/assets", "./public")` |

### Bất biến chính

- **Thứ tự phần mềm trung gian là thứ tự cuộc gọi.** `v1.Use(A, B)` chạy A trước B trên mọi yêu cầu trong v1.
- **Xung đột tuyến đường diễn ra im lặng.** Hai nhóm đăng ký `GET /api/users` sẽ theo dõi nhau mà không có lỗi.

## 2. HÌNH ẢNH ![Route group hierarchy with middleware scoping](./images/01-route-groups-hierarchy.png) *Hình: Phân cấp nhóm định tuyến — Công cụ phân nhánh thành `/api` công khai (không có phần mềm trung gian) và [[C10]]] được bảo vệ (với authMiddleware). Các nhóm con `/users` và `/products` kế thừa phạm vi phần mềm trung gian.*```mermaid
flowchart TD
    A["r := gin.Default()"] --> B["api := r.Group('/api/v1')"]
    B --> C["users := api.Group('/users')"]
    C --> D["GET /users"]
    C --> E["GET /users/:id"]
    C --> F["POST /users"]
    B --> G["products := api.Group('/products')"]
```*Hình: Phân cấp tuyến đường — Động cơ → nhóm `/api/v1` → nhóm con `/users` với tuyến đường `:id` được tham số hóa.*

### Giải quyết lộ trình```text
GET /api/health          → public group (no middleware)
GET /api/v1/users        → v1 group → authMiddleware → listUsers handler
GET /api/v1/users/:id    → v1 group → authMiddleware → getUser handler
POST /api/v1/users       → v1 group → authMiddleware → createUser handler
```## 3. MÃ

### Ví dụ 1: Cơ bản — Phiên bản điểm cuối```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Public routes need no auth. Protected routes (v1) share authMiddleware.
    // c.Param("id") extracts :id from the path; c.DefaultQuery provides fallbacks.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package main

    import (
        "net/http"
        "github.com/gin-gonic/gin"
    )

    func main() {
        r := gin.Default()

        public := r.Group("/api")
        {
            public.GET("/health", healthHandler)
        }

        v1 := r.Group("/api/v1")
        v1.Use(authMiddleware())  
        {
            users := v1.Group("/users")
            {
                users.GET("", listUsers)        
                users.GET("/:id", getUser)      
                users.POST("", createUser)      
            }
        }

        r.Run(":8080")
    }

    func healthHandler(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{"status": "ok"})
    }

    func listUsers(c *gin.Context) {
        page := c.DefaultQuery("page", "1")
        limit := c.DefaultQuery("limit", "20")

        c.JSON(http.StatusOK, gin.H{
            "page":  page,
            "limit": limit,
            "users": []gin.H{},
        })
    }

    func getUser(c *gin.Context) {
        id := c.Param("id")
        c.JSON(http.StatusOK, gin.H{"id": id, "name": "Alice"})
    }

    func createUser(c *gin.Context) { c.JSON(201, gin.H{"message": "created"}) }

    func authMiddleware() gin.HandlerFunc {
        return func(c *gin.Context) {
            token := c.GetHeader("Authorization")
            if token == "" {
                c.AbortWithStatusJSON(401, gin.H{"error": "unauthorized"})
                return
            }
            c.Next()
        }
    }
```### Ví dụ 2: Trung cấp — Đăng ký tuyến đường mô-đun```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Each domain package owns a RegisterRoutes function.
    // Setup() wires public vs protected groups with their middleware.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package router

    import "github.com/gin-gonic/gin"

    func Setup(r *gin.Engine) {
        public := r.Group("/api")
        RegisterAuthRoutes(public)

        protected := r.Group("/api")
        protected.Use(AuthMiddleware())
        RegisterUserRoutes(protected)
    }

    func RegisterUserRoutes(rg *gin.RouterGroup) {
        users := rg.Group("/users")
        handler := NewUserHandler()  
        {
            users.GET("", handler.List)
            users.GET("/:id", handler.Get)
            users.POST("", handler.Create)
        }
    }
```---

## 4. Cạm bẫy

| # | Mức độ nghiêm trọng | Khiếm khuyết | Tác động | Sửa chữa |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Gây tử vong | Đăng ký các đường dẫn trùng lặp giữa các nhóm (ví dụ: hai `GET /api/users` ) | Trình xử lý thứ hai âm thầm che giấu | Kiểm tra tất cả các nhóm về xung đột đường dẫn; sử dụng `gin.DebugPrintRouteFunc` |
| 2 | 🟡 Chung | Áp dụng phần mềm trung gian xác thực ở cấp công cụ thay vì cấp nhóm | Kiểm tra tình trạng và điểm cuối công cộng cũng yêu cầu mã thông báo | Đính kèm phần mềm trung gian vào các nhóm cụ thể chứ không phải công cụ |

---

## 5. GIỚI THIỆU

| Tài nguyên | Liên kết |
| --- | --- |
| Bộ định tuyến Gin | [gin-gonic.com/en/docs](https://gin-gonic.com/en/docs/) |
| HttpRouter | [github.com/julienschmidt/httprouter](https://github.com/julienschmidt/httprouter) |

---

## 6. KHUYẾN NGHỊ

| Gia hạn | Khi nào | Cơ sở lý luận | Tài nguyên |
| --- | --- | --- | --- |
| Lập phiên bản & Chuyển hướng | Khi bạn cần ngừng sử dụng các phiên bản API cũ | Bao gồm các quy tắc chuyển hướng và mẫu đàm phán phiên bản | [./02-versioning-redirect.md](./02-versioning-redirect.md) |