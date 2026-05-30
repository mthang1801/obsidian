<!-- tags: golang --> # 🔐 Giới hạn xác thực & tỷ lệ — Bảo vệ API sản xuất trong Gin

> **Thư viện**: Phần mềm trung gian phân lớp để xác thực JWT, kiểm tra vai trò và giới hạn tốc độ IP/người dùng trong API Gin sản xuất.

📅 Đã cập nhật: 2026-04-19 · ⏱️ 16 phút đọc

## 1. ĐỊNH NGHĨA

API sản xuất cần ba lớp phần mềm trung gian theo thứ tự: **xác thực** (ai đang gọi?), **ủy quyền** (họ có được phép không?), **giới hạn tỷ lệ** (họ có đang lạm dụng không?). Mỗi lớp là một phần mềm trung gian Gin riêng biệt gọi `c.Next()` nếu thành công hoặc `c.Abort*` nếu thất bại.

| Lớp | Mục đích |
| -------------- | ----------------------------------------- |
| Xác thực | Xác thực mã thông báo Bearer, đặt `claims` trong ngữ cảnh |
| Ủy quyền | Kiểm tra vai trò/quyền từ các khiếu nại |
| Giới hạn tỷ lệ | Điều tiết theo ID người dùng hoặc địa chỉ IP |
| Ghi nhật ký kiểm tra | Nhật ký từ chối yêu cầu xem xét bảo mật |

### Bất biến chính

- **Xác thực trước giới hạn tỷ lệ.** Giới hạn tỷ lệ theo ID người dùng yêu cầu biết người dùng là ai trước.
- **Chấp nhận giao diện `TokenVerifier` , không phải lib JWT cụ thể.** Cho phép hoán đổi JWKS, Paseto hoặc giả.

## 2. HÌNH ẢNH ![Production middleware stack — 7 protection layers from rate limiter to handler](./images/04-auth-ratelimit-prod.png) *Hình: Bảo vệ theo lớp — Bộ giới hạn tốc độ → CORS → Tiêu đề bảo mật → Xác thực JWT → RBAC → Ghi nhật ký → Trình xử lý. Mỗi lớp có thể bị đoản mạch; yêu cầu chỉ đến được bộ xử lý nếu tất cả đều đạt.*```mermaid
flowchart LR
    A["Request"] --> B["RateLimiter"]
    B -->|"under limit"| C["AuthMiddleware"]
    C -->|"valid token"| D["RequireRole"]
    D -->|"role match"| E["Handler"]
    B -->|"exceeded"| F["429"]
    C -->|"invalid"| G["401"]
    D -->|"no access"| H["403"]
```*Hình: Chuỗi phần mềm trung gian ba lớp — giới hạn tốc độ (toàn cầu) → xác thực (danh tính) → kiểm tra vai trò (quyền). Mỗi lớp sẽ bị đoản mạch khi bị lỗi.*

### Thứ tự phần mềm trung gian```text
Global:   RateLimit (by IP)
Auth:     AuthMiddleware (Bearer token → claims)
Route:    RequireRole("admin") (per-endpoint)
```## 3. MÃ

### Ví dụ 1: Cơ bản — Xác thực mã thông báo gốc```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Auth middleware: extract Bearer token, verify via interface,
    // set claims in gin.Context for downstream handlers.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package advanced

    import (
        "net/http"
        "strings"
        "github.com/gin-gonic/gin"
    )

    type Claims struct {
        Subject string
        Role    string
    }

    type TokenVerifier interface {
        Verify(token string) (Claims, error)
    }

    func AuthMiddleware(verifier TokenVerifier) gin.HandlerFunc {
        return func(c *gin.Context) {
            header := c.GetHeader("Authorization")
            if !strings.HasPrefix(header, "Bearer ") {
                c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "missing bearer token"})
                return
            }

            claims, err := verifier.Verify(strings.TrimPrefix(header, "Bearer "))
            if err != nil {
                c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid token"})
                return
            }

            c.Set("claims", claims)
            c.Next()
        }
    }
```### Ví dụ 2: Trung cấp — Hạn chế về vai trò được ánh xạ```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Role guard: read claims from context, check role match.
    // 403 if role doesn't match expected value.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package advanced

    import (
        "net/http"
        "github.com/gin-gonic/gin"
    )

    func RequireRole(expected string) gin.HandlerFunc {
        return func(c *gin.Context) {
            value, ok := c.Get("claims")
            if !ok {
                c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "missing auth context"})
                return
            }

            claims, ok := value.(Claims)
            if !ok {
                c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid auth context"})
                return
            }
            if claims.Role != expected {
                c.AbortWithStatusJSON(http.StatusForbidden, gin.H{"error": "forbidden"})
                return
            }

            c.Next()
        }
    }
```### Ví dụ 3: Nâng cao — Khóa ngữ cảnh điều chỉnh```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Per-key rate limiter using x/time/rate. Keyed by user ID
    // (if authenticated) or client IP (fallback).
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package advanced

    import (
        "net/http"
        "sync"
        "github.com/gin-gonic/gin"
        "golang.org/x/time/rate"
    )

    func RateLimitPerKey(limit rate.Limit, burst int, keyFn func(*gin.Context) string) gin.HandlerFunc {
        var (
            mu       sync.Mutex
            limiters = map[string]*rate.Limiter{}
        )

        return func(c *gin.Context) {
            key := keyFn(c)

            mu.Lock()
            limiter, ok := limiters[key]
            if !ok {
                limiter = rate.NewLimiter(limit, burst)
                limiters[key] = limiter
            }
            mu.Unlock()

            if !limiter.Allow() {
                c.Header("Retry-After", "1")
                c.AbortWithStatusJSON(http.StatusTooManyRequests, gin.H{"error": "rate limit exceeded"})
                return
            }

            c.Next()
        }
    }

    func KeyByUserOrIP(c *gin.Context) string {
        if value, ok := c.Get("claims"); ok {
            if claims, ok := value.(Claims); ok && claims.Subject != "" {
                return claims.Subject
            }
        }
        return c.ClientIP()
    }
```---

## 4. Cạm bẫy

| # | Mức độ nghiêm trọng | Khiếm khuyết | Tác động | Sửa chữa |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Gây tử vong | Giới hạn tỷ lệ mà không cần xác thực trước | Khóa giới hạn tốc độ chỉ là IP; người dùng được xác thực chia sẻ giới hạn đằng sau NAT | Chạy phần mềm trung gian xác thực trước bộ giới hạn tốc độ, khóa theo ID người dùng |
| 2 | 🟡 Chung | Bản đồ giới hạn bộ nhớ không giới hạn (không bị trục xuất) | Bộ nhớ tăng trưởng tuyến tính với các IP duy nhất; OOM sau nhiều ngày | Sử dụng bộ đệm dựa trên TTL hoặc bộ giới hạn được Redis hỗ trợ trong sản xuất |

---

## 5. GIỚI THIỆU

| Tài nguyên | Liên kết |
| --- | --- |
| Tài liệu phần mềm trung gian | [gin-gonic.com/en/docs/examples/using-middleware/](https://gin-gonic.com/en/docs/examples/using-middleware/) |

---

## 6. KHUYẾN NGHỊ

| Gia hạn | Khi nào | Cơ sở lý luận | Tài nguyên |
| --- | --- | --- | --- |
| Tải lên phát trực tuyến | Khi bạn xử lý việc tải lên/tải xuống tệp lớn | Truyền phát qua `io.Copy` để tránh tải toàn bộ tệp trong bộ nhớ | [./05-upload-download-streaming.md](./05-upload-download-streaming.md) |