<!-- tags: golang --> # 🏥 Kiểm tra sức khỏe — Điểm cuối NestJS → Điểm cuối sức khỏe Gin

> **Thư viện**: Thăm dò hoạt động và mức độ sẵn sàng thông qua trình xử lý Gin tùy chỉnh kiểm tra DB, Redis và các dịch vụ bên ngoài.

📅 Đã cập nhật: 19-04-2026 · ⏱️ 8 phút đọc

## 1. ĐỊNH NGHĨA

Kubernetes cần hai loại thăm dò: **sự sống động** (quy trình có hoạt động không?) và **sẵn sàng** (nó có thể chấp nhận lưu lượng truy cập không?). NestJS sử dụng Terminus. Trong Gin, bạn viết các hàm xử lý ping từng phần phụ thuộc và trả về phản hồi JSON có cấu trúc.

| NestJS | Gin / Đi |
| ------------------------------------ | --------------------------------- |
| `TerminusModule` | Chức năng xử lý tùy chỉnh |
| `@HealthCheck()` trang trí | `r.GET("/health", healthHandler)` |
| `HealthCheckService.check([])` | Kiểm tra từng phần phụ thuộc theo cách thủ công |
| `TypeOrmHealthIndicator.pingCheck()` | `db.Ping()` |
| `HttpHealthIndicator.pingCheck()` | `http.Get(url)` |

### Bất biến chính

- **Tính năng hoạt động phải ngay lập tức.** Không bao giờ đưa các bước kiểm tra DB vào tính năng hoạt động — DB chậm sẽ khiến nhóm khởi động lại không cần thiết.
- **Tính sẵn sàng kiểm tra tất cả các phần phụ thuộc.** Trả về 503 nếu không thể truy cập được bất kỳ phần phụ thuộc quan trọng nào (DB, Redis, hàng đợi).

## 2. HÌNH ẢNH ![Health check probes — liveness vs readiness with parallel dependency checks](./images/02-health-check.png) *Hình: Liveness (/health/live) = quá trình đang hoạt động, K8 sẽ khởi động lại nếu thất bại. Sẵn sàng (/health/ready) = có thể phục vụ lưu lượng truy cập, kiểm tra DB/Redis/external thông qua errgroup, K8 sẽ xóa khỏi LB nếu thất bại.*```mermaid
flowchart TD
    K["Kubelet"] -->|"GET /livez"| A["Liveness Handler"]
    A --> B["200 alive"]
    K -->|"GET /readyz"| C["Readiness Handler"]
    C --> D{"DB.Ping()\nRedis.Ping()"}
    D -->|"all ok"| E["200 ok + checks"]
    D -->|"any fail"| F["503 degraded"]
```*Hình: Đầu dò Kubelet — hoạt động trở lại ngay lập tức; mức độ sẵn sàng kiểm tra tất cả các phần phụ thuộc và trả về 503 nếu có phần phụ thuộc nào bị hỏng.*

### Các loại đầu dò```text
/livez    → always 200 (process is alive)
/readyz   → 200 if DB + Redis + queue reachable, 503 otherwise
/health   → comprehensive status with per-dependency results
```## 3. MÃ

### Ví dụ 1: Cơ bản — Kiểm tra sức khỏe đơn giản```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Simple health check: return 200 with uptime.
    // Mount at /health or /livez.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package main

    import (
        "net/http"
        "time"
        "github.com/gin-gonic/gin"
    )

    var startTime = time.Now()

    func main() {
        r := gin.Default()

        r.GET("/health", func(c *gin.Context) {
            c.JSON(http.StatusOK, gin.H{
                "status": "ok",
                "uptime": time.Since(startTime).String(),
            })
        })

        r.Run(":8080")
    }
```### Ví dụ 2: Trung cấp — Kiểm tra sức khỏe toàn diện```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Comprehensive health checker: checks DB + Redis.
    // Returns per-dependency status with duration.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package health

    import (
        "context"
        "net/http"
        "time"
        "github.com/gin-gonic/gin"
        "github.com/redis/go-redis/v9"
        "gorm.io/gorm"
    )

    type Checker struct {
        db    *gorm.DB
        redis *redis.Client
    }

    type Status struct {
        Status    string            `json:"status"`
        Uptime    string            `json:"uptime"`
        Timestamp string            `json:"timestamp"`
        Checks    map[string]Check  `json:"checks"`
    }

    type Check struct {
        Status   string `json:"status"`
        Duration string `json:"duration,omitempty"`
        Error    string `json:"error,omitempty"`
    }

    func NewChecker(db *gorm.DB, rdb *redis.Client) *Checker {
        return &Checker{db: db, redis: rdb}
    }

    func (h *Checker) Handler(startTime time.Time) gin.HandlerFunc {
        return func(c *gin.Context) {
            ctx, cancel := context.WithTimeout(c.Request.Context(), 5*time.Second)
            defer cancel()

            checks := map[string]Check{
                "database": h.checkDB(ctx),
                "redis":    h.checkRedis(ctx),
            }

            overall := "ok"
            statusCode := http.StatusOK
            for _, check := range checks {
                if check.Status != "ok" {
                    overall = "degraded"
                    statusCode = http.StatusServiceUnavailable
                }
            }

            c.JSON(statusCode, Status{
                Status:    overall,
                Uptime:    time.Since(startTime).String(),
                Timestamp: time.Now().Format(time.RFC3339),
                Checks:    checks,
            })
        }
    }

    func (h *Checker) checkDB(ctx context.Context) Check {
        start := time.Now()
        sqlDB, err := h.db.DB()
        if err != nil {
            return Check{Status: "error", Error: err.Error()}
        }
        if err := sqlDB.PingContext(ctx); err != nil {
            return Check{Status: "error", Error: err.Error()}
        }
        return Check{Status: "ok", Duration: time.Since(start).String()}
    }

    func (h *Checker) checkRedis(ctx context.Context) Check {
        start := time.Now()
        if err := h.redis.Ping(ctx).Err(); err != nil {
            return Check{Status: "error", Error: err.Error()}
        }
        return Check{Status: "ok", Duration: time.Since(start).String()}
    }

    func (h *Checker) LivenessHandler() gin.HandlerFunc {
        return func(c *gin.Context) {
            c.JSON(http.StatusOK, gin.H{"status": "alive"})
        }
    }

    func (h *Checker) ReadinessHandler() gin.HandlerFunc {
        return h.Handler(time.Now()) 
    }
```---

## 4. Cạm bẫy

| # | Mức độ nghiêm trọng | Khiếm khuyết | Tác động | Sửa chữa |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Gây tử vong | Đưa kiểm tra DB vào thăm dò độ sống | Truy vấn DB chậm khiến Kubelet khởi động lại các nhóm khỏe mạnh | Sử dụng sự sống động ngay lập tức; chỉ đặt kiểm tra phụ thuộc ở trạng thái sẵn sàng |
| 2 | 🟡 Chung | Kiểm tra tình trạng mà không hết thời gian chờ trên ping phụ thuộc | Một sự phụ thuộc chậm sẽ chặn toàn bộ phản ứng về sức khỏe | Sử dụng `context.WithTimeout(ctx, 5*time.Second)` |

---

## 5. GIỚI THIỆU

| Tài nguyên | Liên kết |
| --- | --- |
| Đầu dò Kubernetes | [kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) |

---

## 6. KHUYẾN NGHỊ

| Gia hạn | Khi nào | Cơ sở lý luận | Tài nguyên |
| --- | --- | --- | --- |
| Mẫu CQRS | Khi đọc và ghi tải phân kỳ | Các mô hình đọc/ghi riêng biệt cho phép chia tỷ lệ độc lập | [./03-graceful-cqrs.md](./03-graceful-cqrs.md) |