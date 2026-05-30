<!-- tags: golang --> # 🛡️ Middleware — Logger, Recovery, Auth, CORS, Custom

> **Thư viện**: Chuỗi các hàm phần mềm trung gian chạy trước/sau mỗi trình xử lý — ghi nhật ký, khôi phục, xác thực, CORS, ID yêu cầu.

📅 Đã cập nhật: 19-04-2026 · ⏱️ 15 phút đọc

## 1. ĐỊNH NGHĨA

Phần mềm trung gian Gin là `gin.HandlerFunc` chạy trong một chuỗi trước (và tùy chọn sau) trình xử lý cuối cùng. `c.Next()` chuyển sang phần mềm trung gian tiếp theo; `c.Abort()` dừng chuỗi. Middleware có thể được áp dụng trên toàn cầu, theo nhóm hoặc theo tuyến.

| Phạm vi | Ứng dụng | Trường hợp sử dụng |
| ---------- | -------------- | ---------------------------- |
| **Toàn cầu** | `r.Use(mw)` | Trình ghi nhật ký, phục hồi, CORS |
| **Nhóm** | `g.Use(mw)` | Xác thực cho các tuyến đường `/api/v1` |
| **Tuyến đường** | `r.GET(p, mw, h)` | Giới hạn tốc độ trên một điểm cuối duy nhất |

### Bất biến chính

- **Gọi `c.Next()` để tiếp tục chuỗi.** Nếu không có nó, trình xử lý xuôi dòng sẽ không bao giờ thực thi.
- **Gọi `return` sau `c.Abort*()` .** Nếu không có `return` , phần mềm trung gian hiện tại sẽ tiếp tục thực thi sau khi hủy bỏ.

## 2. HÌNH ẢNH ![Middleware chain execution — global, group, and route scopes with c.Next() and c.Abort() paths](./images/01-middleware-chain.png) *Hình: Chuỗi phần mềm trung gian — Trình ghi nhật ký và ID yêu cầu là toàn cầu (r.Use), Auth nằm trong phạm vi nhóm (g.Use). Con đường hạnh phúc chảy qua c.Next(); hủy bỏ đường dẫn ngắn mạch với c.AbortWithStatusJSON(401).*```mermaid
flowchart LR
    A["Request"] --> B["Logger MW"]
    B --> C["RequestID MW"]
    C --> D["Auth MW"]
    D --> E["Handler"]
    E -->|"c.Next() returns"| D
    D --> C
    C --> B
    B -->|"log status"| F["Response"]
```*Hình: Chuỗi phần mềm trung gian — Trình ghi nhật ký → ID yêu cầu → Xác thực → Trình xử lý → (ghi nhật ký trình xử lý sau trong quá trình sao lưu).*```text
Before c.Next() → pre-processing (set headers, validate, start timer)
c.Next()         → runs next middleware / handler
After c.Next()   → post-processing (log status, record duration)
```*Hình: Luồng trước/sau — `c.Next()` chạy xuôi dòng, sau đó điều khiển quay trở lại để xử lý hậu kỳ (thời gian, ghi nhật ký trạng thái).*

### Lệnh thi hành```text
Request arrives
  → Logger (before)  → RequestID (before)  → Handler executes
  ← Logger (after: logs status + duration) ← RequestID (after)
Response sent
```## 3. MÃ

### Ví dụ 1: Cơ bản — Chuỗi tích hợp```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Two custom middleware: RequestLogger (before/after via c.Next)
    // and RequestID (reads or generates X-Request-Id header).
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package main

    import (
        "fmt"
        "log"
        "time"
        "github.com/gin-gonic/gin"
    )

    func main() {
        r := gin.Default()

        r.Use(RequestLogger())
        r.Use(RequestID())

        r.GET("/ping", func(c *gin.Context) {
            requestID := c.GetString("requestID")
            c.JSON(200, gin.H{
                "message":    "pong",
                "request_id": requestID,
            })
        })

        r.Run(":8080")
    }

    func RequestLogger() gin.HandlerFunc {
        return func(c *gin.Context) {
            start := time.Now()
            path := c.Request.URL.Path
            method := c.Request.Method

            log.Printf("→ %s %s", method, path)

            c.Next()  

            duration := time.Since(start)
            status := c.Writer.Status()
            log.Printf("← %s %s %d %v", method, path, status, duration)
        }
    }

    func RequestID() gin.HandlerFunc {
        return func(c *gin.Context) {
            requestID := c.GetHeader("X-Request-Id")
            if requestID == "" {
                requestID = generateID()  
            }

            c.Set("requestID", requestID)
            c.Header("X-Request-Id", requestID)

            c.Next()
        }
    }

    func generateID() string {
        return fmt.Sprintf("%d", time.Now().UnixNano())
    }
```### Ví dụ 2: Trung cấp — Bảo vệ JWT và CORS```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // JWTAuth: aborts with 401 if Authorization header is missing.
    // CORSMiddleware: sets CORS headers; handles OPTIONS preflight.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    func JWTAuth() gin.HandlerFunc {
        return func(c *gin.Context) {
            authHeader := c.GetHeader("Authorization")

            if authHeader == "" {
                c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
                    "error": "missing authorization header",
                })
                return
            }

            c.Set("userID", 123) 

            c.Next()
        }
    }

    func CORSMiddleware() gin.HandlerFunc {
        return func(c *gin.Context) {
            c.Header("Access-Control-Allow-Origin", "*")
            c.Header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            c.Header("Access-Control-Allow-Headers", "Authorization, Content-Type")

            if c.Request.Method == "OPTIONS" {
                c.AbortWithStatus(http.StatusNoContent)
                return
            }

            c.Next()
        }
    }
```### Ví dụ 3: Nâng cao — Khôi phục tùy chỉnh```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // CustomRecovery replaces gin.Recovery() to return JSON error
    // bodies instead of default text/plain panic output.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    func CustomRecovery() gin.HandlerFunc {
        return gin.CustomRecovery(func(c *gin.Context, err any) {
            log.Printf("PANIC: %v", err)

            c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{
                "error":   "internal server error",
                "message": "an unexpected error occurred",
            })
        })
    }
```---

## 4. Cạm bẫy

| # | Mức độ nghiêm trọng | Khiếm khuyết | Tác động | Sửa chữa |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Gây tử vong | Gọi `c.Abort()` không có `return` trong cùng chức năng | Mã sau khi hủy bỏ vẫn thực thi; có thể viết những phản hồi trái ngược nhau | Luôn viết `c.AbortWithStatusJSON(...); return` |
| 2 | 🔴 Gây tử vong | Đặt phần mềm trung gian Recovery sau Logger | Sự hoảng loạn trong Logger làm hỏng quá trình mà không thể khôi phục | Recovery phải là phần mềm trung gian đầu tiên trong chuỗi |

---

## 5. GIỚI THIỆU

| Tài nguyên | Liên kết |
| --- | --- |
| Phần mềm trung gian tùy chỉnh | [gin-gonic.com/docs/examples/custom-middleware](https://gin-gonic.com/docs/examples/custom-middleware/) |
| Gin CORS | [github.com/gin-contrib/cors](https://github.com/gin-contrib/cors) |

---

## 6. KHUYẾN NGHỊ

| Gia hạn | Khi nào | Cơ sở lý luận | Tài nguyên |
| --- | --- | --- | --- |
| Vệ binh & Đánh chặn | Khi bạn cần quyền truy cập dựa trên vai trò hoặc xử lý lỗi có cấu trúc | Xây dựng trên phần mềm trung gian để triển khai Bộ bảo vệ/Bộ chặn/Bộ lọc kiểu NestJS | [./02-guards-interceptors.md](./02-guards-interceptors.md) |