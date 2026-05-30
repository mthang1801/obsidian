<!-- tags: golang --> # 📋 Ghi nhật ký — NestJS Logger → Đi slog/zap/zerolog

> **Thư viện**: Ghi nhật ký có cấu trúc với Go 1.21+ `log/slog` , ngữ cảnh trong phạm vi yêu cầu và ID tương quan.

📅 Đã cập nhật: 19-04-2026 · ⏱️ 10 phút đọc

## 1. ĐỊNH NGHĨA

 Nhật ký `fmt.Println` không thể tìm kiếm được. Nhật ký JSON có cấu trúc với ID yêu cầu, phương thức, đường dẫn, trạng thái và thời lượng cho phép bạn `grep` bất kỳ yêu cầu nào trong quá trình sản xuất. Đi 1.21+ gửi `log/slog` trong thư viện tiêu chuẩn.

| NestJS | Đi tương đương |
| ------------------------------ | ------------------------------------- |
| `Logger.log/warn/error()` | `slog.Info/Warn/Error()` |
| `app.useLogger(WinstonModule)` | `slog.SetDefault(jsonHandler)` |
| `@Injectable() LoggerService` | Tiêm `*slog.Logger` qua hàm tạo |
| Yêu cầu nhật ký | Phương thức/đường dẫn/trạng thái/thời lượng nhật ký phần mềm trung gian |

### Bất biến chính

- **ID yêu cầu nhật ký ở mỗi dòng.** Nếu không có ID này, bạn không thể liên kết nhật ký giữa phần mềm trung gian và trình xử lý.
- **Không bao giờ đăng nhập mật khẩu, mã thông báo hoặc PII.** Xóa các trường nhạy cảm trước khi đăng nhập.

## 2. HÌNH ẢNH ![Structured logging flow — RequestID + Logger middleware with slog/zerolog/zap comparison](./images/05-logging.png) *Hình: Luồng ghi nhật ký — Phần mềm trung gian requestID tạo UUID → Phần mềm trung gian ghi nhật ký kết thúc c.Next() với thời gian → đầu ra JSON có cấu trúc với phương thức, đường dẫn, trạng thái, độ trễ, request_id.*```mermaid
flowchart LR
    A["Request"] --> B["Logger Middleware"]
    B -->|"inject logger+reqID"| C["Handler"]
    C -->|"logger.Info(msg)"| D["slog.JSONHandler"]
    D --> E["stdout / file"]
```*Hình: Yêu cầu → phần mềm trung gian chèn X-Request-ID vào trình ghi nhật ký phạm vi yêu cầu → trình xử lý nhật ký có cấu trúc JSON thông qua slog.*

### Tương quan nhật ký```text
Request arrives → RequestID middleware generates UUID
    → Creates slog.Logger.With("request_id", uuid)
    → Stores in c.Set("logger", logger)
    → Handler: logger.Info("user created", "user_id", 42)
    → Output: {"level":"INFO","request_id":"abc-123","msg":"user created","user_id":42}
```## 3. MÃ

### Ví dụ 1: Cơ bản — Ghi nhật ký cấu trúc gốc```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // slog.NewJSONHandler outputs structured JSON logs.
    // RequestLogger middleware logs method/path/status/duration.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package main

    import (
        "log/slog"
        "os"
        "time"
        "github.com/gin-gonic/gin"
    )

    func main() {
        logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
            Level: slog.LevelInfo,
        }))
        slog.SetDefault(logger)

        r := gin.New() 
        r.Use(RequestLogger(logger), gin.Recovery())

        r.GET("/health", func(c *gin.Context) {
            slog.Info("health check", "status", "ok")
            c.JSON(200, gin.H{"status": "ok"})
        })

        r.Run(":8080")
    }

    func RequestLogger(logger *slog.Logger) gin.HandlerFunc {
        return func(c *gin.Context) {
            start := time.Now()

            c.Next()

            logger.LogAttrs(c.Request.Context(), slog.LevelInfo, "http request",
                slog.String("method", c.Request.Method),
                slog.String("path", c.Request.URL.Path),
                slog.Int("status", c.Writer.Status()),
                slog.Duration("duration", time.Since(start)),
                slog.String("ip", c.ClientIP()),
            )
        }
    }
```### Ví dụ 2: Trung cấp — Phạm vi theo ngữ cảnh```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // RequestID middleware: generates UUID, creates scoped logger,
    // stores in gin.Context for downstream handlers.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package middleware

    import (
        "log/slog"
        "github.com/gin-gonic/gin"
        "github.com/google/uuid"
    )

    func RequestID() gin.HandlerFunc {
        return func(c *gin.Context) {
            id := c.GetHeader("X-Request-ID")
            if id == "" {
                id = uuid.New().String()
            }
            c.Set("requestID", id)
            c.Header("X-Request-ID", id)

            logger := slog.Default().With(
                "request_id", id,
                "method", c.Request.Method,
                "path", c.Request.URL.Path,
            )
            c.Set("logger", logger)

            c.Next()
        }
    }
```---

## 4. Cạm bẫy

| # | Mức độ nghiêm trọng | Khiếm khuyết | Tác động | Sửa chữa |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Gây tử vong | Ghi nhật ký mật khẩu, mã thông báo JWT hoặc số thẻ tín dụng | Thông tin xác thực được hiển thị trong trình tổng hợp nhật ký | Chà sạch các lĩnh vực nhạy cảm; không bao giờ ghi lại giá trị tiêu đề `Authorization` |
| 2 | 🟡 Chung | Sử dụng `fmt.Println` thay vì trình ghi nhật ký có cấu trúc | Nhật ký không thể tìm kiếm được, không có mối tương quan với yêu cầu | Sử dụng `slog` với trình xử lý JSON và ID yêu cầu |

---

## 5. GIỚI THIỆU

| Tài nguyên | Liên kết |
| --- | --- |
| nhật ký/slog | [pkg.go.dev/log/slog](https://pkg.go.dev/log/slog) |

---

## 6. KHUYẾN NGHỊ

| Gia hạn | Khi nào | Cơ sở lý luận | Tài nguyên |
| --- | --- | --- | --- |
| Phiên & Cookie | Khi bạn cần duy trì trạng thái người dùng qua các yêu cầu | Dữ liệu phiên liên kết với ID yêu cầu để gỡ lỗi luồng xác thực | [./06-session-cookies.md](./06-session-cookies.md) |