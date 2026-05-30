<!-- tags: golang, context --> # 🚀 Khái niệm cơ bản về Gin — Bộ định tuyến, Ngữ cảnh, Trình xử lý

> **Thư viện**: Ba nguyên hàm cốt lõi của Gin — Engine (bộ định tuyến), Ngữ cảnh (trạng thái theo yêu cầu) và Trình xử lý (điểm vào logic nghiệp vụ).

📅 Cập nhật: 2026-04-19 · ⏱️ 14 phút đọc

## 1. ĐỊNH NGHĨA

Mọi ứng dụng Gin đều bắt đầu với ba nguyên hàm: **Engine** (tạo bộ định tuyến và giữ phần mềm trung gian), **Context** (mang dữ liệu yêu cầu, trình soạn thảo phản hồi và lưu trữ khóa-giá trị theo yêu cầu thông qua chuỗi phần mềm trung gian) và **Handler** (một hàm có chữ ký `func(c *gin.Context)` xử lý một yêu cầu duy nhất).

| Thành phần | Vai trò | Mã |
| --------------- | -------------------------------------------- | ---------------------- |
| **Động cơ** | Tạo bộ định tuyến; đăng ký tuyến đường và phần mềm trung gian | `gin.Default()` |
| **Bối cảnh** | Phong bì theo yêu cầu: thông số, truy vấn, tiêu đề, nội dung, cửa hàng KV | `*gin.Context` |
| **Người xử lý** | Điểm vào logic nghiệp vụ cho một tuyến đường duy nhất | `func(c *gin.Context)` |
| **Nhóm bộ định tuyến** | Nhóm các tuyến theo bộ tiền tố và phần mềm trung gian được chia sẻ | `/api/v1` |
| **gin.H** | Viết tắt cho `map[string]any` - được sử dụng trong phản hồi JSON | `gin.H{"key": "val"}` |

### Bất biến chính

- **Ngữ cảnh KHÔNG an toàn cho goroutine.** Việc chuyển `*gin.Context` vào một goroutine mà không có `.Copy()` sẽ gây ra tình trạng chạy đua và hoảng loạn dữ liệu.
- ** `gin.Default()` bao gồm phần mềm trung gian Logger và Recovery.** Sử dụng `gin.New()` cho động cơ trần khi bạn muốn toàn quyền kiểm soát.

## 2. HÌNH ẢNH ![Request lifecycle — Engine route match → middleware chain → handler → response](./images/01-request-lifecycle.png) *Hình: Vòng đời yêu cầu Gin — Yêu cầu HTTP đi vào cây cơ số của Engine để khớp tuyến, đi qua chuỗi phần mềm trung gian (Logger → Recovery → Custom), đến trình xử lý với `gin.Context` được điền đầy đủ và ghi phản hồi.*```mermaid
flowchart LR
    A["HTTP Request"] --> B["gin.Engine"]
    B -->|"route match"| C["Middleware Chain"]
    C --> D["Handler"]
    D -->|"c.JSON / c.HTML"| E["Response"]
```*Hình: Vòng đời yêu cầu — yêu cầu HTTP đến → So khớp lộ trình công cụ → chuỗi phần mềm trung gian → trình xử lý → phản hồi.*```mermaid
flowchart TD
    A["gin.Context"] --> B["Params: c.Param('id')"]
    A --> C["Query: c.Query('page')"]
    A --> D["Body: c.ShouldBindJSON()"]
    A --> E["Headers: c.GetHeader()"]
    A --> F["KV Store: c.Set / c.Get"]
```*Hình: Ranh giới bối cảnh — mỗi yêu cầu có `gin.Context` riêng với các thông số, truy vấn, tiêu đề, nội dung và kho lưu trữ KV.*

### Luồng yêu cầu```text
Client HTTP Request
    │
    ├── Engine matches route via radix tree
    ├── Middleware chain executes (Logger → Recovery → Custom)
    ├── Handler receives *gin.Context with all request data
    └── Handler writes response via c.JSON / c.HTML / c.String
```## 3. MÃ

### Ví dụ 1: Cơ bản — Khởi động động cơ```go
package main

import (
    "net/http"
    "github.com/gin-gonic/gin"
)

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// gin.Default() creates an Engine with Logger + Recovery middleware.
// Each HTTP verb (GET, POST, PUT, DELETE) maps a path to a handler.
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
func main() {
    r := gin.Default()

    r.GET("/ping", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{
            "message": "pong",
        })
    })

    r.POST("/users", func(c *gin.Context) {
        c.JSON(http.StatusCreated, gin.H{
            "message": "user created",
        })
    })

    r.PUT("/users/:id", func(c *gin.Context) {
        id := c.Param("id")
        c.JSON(http.StatusOK, gin.H{
            "message": "user updated",
            "id":      id,
        })
    })

    r.DELETE("/users/:id", func(c *gin.Context) {
        id := c.Param("id")
        c.JSON(http.StatusOK, gin.H{
            "message": "user deleted",
            "id":      id,
        })
    })

    r.Any("/health", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{
            "status": "ok",
            "method": c.Request.Method,
        })
    })

    r.NoRoute(func(c *gin.Context) {
        c.JSON(http.StatusNotFound, gin.H{
            "error": "route not found",
            "path":  c.Request.URL.Path,
        })
    })

    r.Run(":8080")
}
```### Ví dụ 2: Trung cấp — Trích xuất ngữ cảnh```go
package main

import (
    "fmt"
    "net/http"
    "time"
    "github.com/gin-gonic/gin"
)

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Context provides typed accessors for all request data:
// Param (path), Query (querystring), Header, ClientIP, Get/Set (KV store)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
func main() {
    r := gin.Default()

    r.GET("/users/:id", func(c *gin.Context) {
        id := c.Param("id")                  
        c.JSON(http.StatusOK, gin.H{"id": id})
    })

    r.GET("/search", func(c *gin.Context) {
        query := c.Query("q")                          
        page := c.DefaultQuery("page", "1")            
        limit := c.DefaultQuery("limit", "20")         
        sort := c.Query("sort")                        

        c.JSON(http.StatusOK, gin.H{
            "query": query,
            "page":  page,
            "limit": limit,
            "sort":  sort,
        })
    })

    r.GET("/headers", func(c *gin.Context) {
        contentType := c.GetHeader("Content-Type")
        userAgent := c.GetHeader("User-Agent")
        auth := c.GetHeader("Authorization")
        clientIP := c.ClientIP()

        c.JSON(http.StatusOK, gin.H{
            "content_type": contentType,
            "user_agent":   userAgent,
            "auth":         auth,
            "client_ip":    clientIP,
        })
    })

    r.GET("/context-demo", func(c *gin.Context) {
        c.Set("userID", 42)
        c.Set("role", "admin")
        
        userID, _ := c.Get("userID")

        c.JSON(http.StatusOK, gin.H{
            "userID": userID,
            "role":   c.GetString("role"),
        })
    })

    r.Run(":8080")
}
```### Ví dụ 3: Nâng cao — Công cụ mục tiêu sản xuất```go
package main

import (
    "context"
    "log"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"
    "github.com/gin-gonic/gin"
)

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Production setup: gin.New() (no default middleware), custom recovery,
// trusted proxies, timeouts, and graceful shutdown via os.Signal.
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
func main() {
    gin.SetMode(gin.ReleaseMode)
    r := gin.New()

    r.Use(gin.CustomRecovery(func(c *gin.Context, err any) {
        c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{
            "error":   "internal server error",
            "message": "something went wrong",
        })
    }))

    r.SetTrustedProxies([]string{"127.0.0.1", "10.0.0.0/8"})
    r.MaxMultipartMemory = 8 << 20 

    r.GET("/health", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{"status": "ok"})
    })

    srv := &http.Server{
        Addr:         ":8080",
        Handler:      r,
        ReadTimeout:  10 * time.Second,
        WriteTimeout: 30 * time.Second,
        IdleTimeout:  120 * time.Second,
    }

    go func() {
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatalf("listen: %s\n", err)
        }
    }()

    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()

    if err := srv.Shutdown(ctx); err != nil {
        log.Fatal("Server forced to shutdown:", err)
    }
}
```---

## 4. Cạm bẫy

| # | Mức độ nghiêm trọng | Khiếm khuyết | Tác động | Sửa chữa |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Gây tử vong | Sử dụng `gin.Default()` trong sản xuất mà không cần khôi phục tùy chỉnh | Nhật ký khôi phục mặc định chuyển sang thiết bị xuất chuẩn nhưng không trả về phản hồi lỗi có cấu trúc | Sử dụng `gin.New()` + `gin.CustomRecovery(...)` để trả về nội dung lỗi JSON |
| 2 | 🔴 Gây tử vong | Truyền `*gin.Context` tới một goroutine không có `.Copy()` | Cuộc đua dữ liệu: bối cảnh được tái chế sau khi trình xử lý trả về | Gọi `cCopy := c.Copy()` và sử dụng `cCopy` trong goroutine |

---

## 5. GIỚI THIỆU

| Tài nguyên | Liên kết |
| --- | --- |
| Gin chính thức | [gin-gonic.com/en/docs/](https://gin-gonic.com/en/docs/) |
| Gin Repo | [github.com/gin-gonic/gin](https://github.com/gin-gonic/gin) |

---

## 6. KHUYẾN NGHỊ

| Gia hạn | Khi nào | Cơ sở lý luận | Tài nguyên |
| --- | --- | --- | --- |
| Định tuyến | Khi bạn cần nhóm tuyến đường, thông số đường dẫn hoặc phiên bản API | Xây dựng trên Engine và Context để tổ chức các API lớn | [../routing/01-groups-params.md](../routing/01-groups-params.md) |
| Phần mềm trung gian | Khi bạn cần ghi nhật ký, xác thực hoặc yêu cầu chặn | Trình xử lý bao bọc phần mềm trung gian - hiểu Luồng ngữ cảnh là điều kiện tiên quyết | [../middleware/01-builtin-custom.md](../middleware/01-builtin-custom.md) |