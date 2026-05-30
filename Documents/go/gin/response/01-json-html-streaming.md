<!-- tags: golang --> # 📤 Phản hồi - JSON, HTML, Truyền phát, SSE

> **Thư viện**: Phương thức phản hồi Gin — `c.JSON` , `c.HTML` , `c.File` , `c.Stream` — và xây dựng một phạm vi API nhất quán.

📅 Cập nhật: 2026-04-19 · ⏱️ 12 phút đọc

## 1. ĐỊNH NGHĨA

Gin cung cấp các phương thức phản hồi được nhập để đặt `Content-Type` và tuần tự hóa dữ liệu trong một lệnh gọi. Gói chúng trong một phong bì chung `APIResponse` để mọi điểm cuối đều trả về `{success, data, error}` .

| Phương pháp | Loại nội dung | Trường hợp sử dụng |
| ------------------------------ | ---------------------------- | ---------------- |
| `c.JSON(code, obj)` | `application/json` | API REST |
| `c.String(code, fmt, args)` | `text/plain` | Văn bản đơn giản |
| `c.HTML(code, name, data)` | `text/html` | Mẫu |
| `c.File(path)` | Tự động phát hiện | Tải xuống/xem trước |

### Bất biến chính

- **Chỉ viết một lần cho mỗi yêu cầu.** Gọi `c.JSON` sau `c.HTML` gây hoảng loạn với "tiêu đề đã được viết."
- **Luôn luôn `return` sau một phản hồi lỗi.** Nếu không, trình xử lý sẽ ghi phần nội dung thứ hai.

## 2. HÌNH ẢNH ![Response methods comparison — JSON, HTML, File, SSE Stream](./images/01-response-methods.png) *Hình: Bốn làn phản hồi — API JSON (c.JSON), Mẫu HTML (c.HTML), Tải xuống tệp (c.File/c.FileAttachment), Luồng SSE (c.Stream + c.SSEvent). Chỉ viết một lần cho mỗi yêu cầu.*```mermaid
flowchart TD
    A["Handler"] --> B{"Response type?"}
    B -->|"JSON"| C["c.JSON(200, data)"]
    B -->|"HTML"| D["c.HTML(200, 'tpl', data)"]
    B -->|"Stream"| E["c.Stream(callback)"]
    B -->|"File"| F["c.File(path)"]
```*Hình: Hình dạng phản hồi — JSON cho API, HTML cho mẫu, Luồng cho thời gian thực, Tệp để tải xuống.*

### Quyết định phản hồi```text
Structured API data?        → c.JSON(status, envelope)
Server-rendered HTML?       → c.HTML(status, template, data)
File download/preview?      → c.File(path) / c.FileAttachment(path, name)
Real-time server push?      → c.Stream() + c.SSEvent()
```## 3. MÃ

### Ví dụ 1: Cơ bản — Phong bì JSON```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Unified envelope: {success, data, error}.
    // RespondOK/RespondError ensure every endpoint matches this shape.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package main

    import (
        "net/http"
        "github.com/gin-gonic/gin"
    )

    type APIResponse struct {
        Success bool        `json:"success"`
        Data    interface{} `json:"data,omitempty"`
        Error   *APIError   `json:"error,omitempty"`
    }

    type APIError struct {
        Code    string `json:"code"`
        Message string `json:"message"`
    }

    func RespondOK(c *gin.Context, data interface{}) {
        c.JSON(http.StatusOK, APIResponse{
            Success: true,
            Data:    data,
        })
    }

    func RespondError(c *gin.Context, status int, code, message string) {
        c.JSON(status, APIResponse{
            Success: false,
            Error: &APIError{
                Code:    code,
                Message: message,
            },
        })
    }

    func main() {
        r := gin.Default()

        r.GET("/users/:id", func(c *gin.Context) {
            user := gin.H{"id": 1, "name": "Alice"}
            RespondOK(c, user)
        })

        r.GET("/not-found", func(c *gin.Context) {
            RespondError(c, 404, "USER_NOT_FOUND", "user does not exist")
        })

        r.Run(":8080")
    }
```### Ví dụ 2: Trung cấp — Tệp phản hồi```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // c.File serves inline; c.FileAttachment forces download.
    // c.Data writes raw bytes with a custom Content-Type.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    func setupResponses(r *gin.Engine) {
        
        r.GET("/preview/:filename", func(c *gin.Context) {
            filename := c.Param("filename")
            filepath := path.Join("uploads", filename)
            c.File(filepath)
        })

        r.GET("/download/:filename", func(c *gin.Context) {
            filename := c.Param("filename")
            filepath := path.Join("uploads", filename)
            c.FileAttachment(filepath, filename)
        })

        r.GET("/report/csv", func(c *gin.Context) {
            data := "id,name\n1,Alice"
            c.Data(http.StatusOK, "text/csv", []byte(data))
        })
    }
```### Ví dụ 3: Nâng cao — Phát trực tiếp```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // SSE via c.Stream + c.SSEvent. Ping keeps connection alive.
    // Context.Done() detects client disconnect.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    func sseHandler(c *gin.Context) {
        c.Header("Content-Type", "text/event-stream")
        c.Header("Cache-Control", "no-cache")
        c.Header("Connection", "keep-alive")

        messageChan := make(chan string)

        c.Stream(func(w io.Writer) bool {
            select {
            case msg := <-messageChan:
                c.SSEvent("message", msg)
                return true  
            case <-c.Request.Context().Done():
                return false  
            case <-time.After(30 * time.Second):
                c.SSEvent("ping", gin.H{"status": "alive"})
                return true
            }
        })
    }
```---

## 4. Cạm bẫy

| # | Mức độ nghiêm trọng | Khiếm khuyết | Tác động | Sửa chữa |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Gây tử vong | Gọi `c.JSON()` hai lần trong cùng một trình xử lý | Hoảng loạn: "tiêu đề đã được viết" | Luôn `return` sau khi phản hồi lỗi |
| 2 | 🟡 Chung | Sử dụng `c.File()` với đầu vào của người dùng chưa được dọn dẹp | Tấn công truyền tải đường đi | Sử dụng `filepath.Clean` và hạn chế tải lên thư mục |

---

## 5. GIỚI THIỆU

| Tài nguyên | Liên kết |
| --- | --- |
| Kết xuất Gin | [gin-gonic.com/en/docs](https://gin-gonic.com/en/docs/) |

---

## 6. KHUYẾN NGHỊ

| Gia hạn | Khi nào | Cơ sở lý luận | Tài nguyên |
| --- | --- | --- | --- |
| SSE & WebSocket | Khi bạn cần liên lạc hai chiều theo thời gian thực | SSE để đẩy máy chủ, WebSocket cho song công hoàn toàn | [./02-sse-websocket.md](./02-sse-websocket.md) |