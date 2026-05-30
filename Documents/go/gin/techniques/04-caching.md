<!-- tags: golang, memory, modules --> # 💾 Bộ nhớ đệm — NestJS CacheModule → Đi tới Redis/Trong bộ nhớ

> **Thư viện**: Phản hồi bộ nhớ đệm bằng Redis hoặc kho lưu trữ trong bộ nhớ để giảm tải và độ trễ cơ sở dữ liệu.

📅 Đã cập nhật: 19-04-2026 · ⏱️ 10 phút đọc

## 1. ĐỊNH NGHĨA

Không có bộ nhớ đệm, mọi yêu cầu GET đều truy cập vào cơ sở dữ liệu. Với Redis TTL 60 giây, cơ sở dữ liệu xử lý một truy vấn mỗi phút thay vì hàng nghìn. Gin không có mô-đun bộ đệm tích hợp - bạn triển khai nó bằng Redis hoặc trình chặn phần mềm trung gian.

| NestJS | Đi tương đương |
| ------------------------------------ | -------------------------------------- |
| `CacheModule.register()` | `redis.NewClient()` hoặc `cache.New()` |
| `@CacheKey('users')` | Khóa bộ đệm thủ công: `"users:list"` |
| `@CacheTTL(30)` | `rdb.Set(ctx, key, data, 30*time.Second)` |
| `@UseInterceptors(CacheInterceptor)` | CacheMiddleware (kiểm tra bộ đệm trước khi xử lý) |

### Bất biến chính

- **Không hợp lệ khi ghi.** `POST/PUT/DELETE` phải `rdb.Del()` các khóa bộ đệm bị ảnh hưởng.
- **Sử dụng `singleflight` để chặn bộ nhớ đệm.** Nếu không có nó, 1000 lỗi bộ nhớ đệm đồng thời sẽ kích hoạt 1000 truy vấn DB giống hệt nhau.

## 2. HÌNH ẢNH ![Cache-aside pattern — middleware checks cache before DB, with in-memory vs Redis comparison](./images/04-caching.png) *Hình: Bỏ bộ nhớ đệm — yêu cầu chạm vào phần mềm trung gian bộ nhớ đệm trước tiên. HIT = trả về phản hồi được lưu trong bộ nhớ đệm. MISS = tìm nạp từ DB, lưu vào bộ đệm bằng TTL. Trong bộ nhớ (nhanh, mỗi nhóm) so với Redis (được chia sẻ, liên tục).*```mermaid
flowchart TD
    A["GET /users"] --> B{"Cache hit?"}
    B -->|Yes| C["Return cached"]
    B -->|No| D{"singleflight\ninflight?"}
    D -->|Yes| E["Wait for result"]
    D -->|No| F["Query DB"]
    F --> G["Set cache + TTL"]
    G --> C
    E --> C
```*Hình: Dành riêng bộ nhớ đệm với singleflight — chỉ có một goroutine truy vấn DB bị bỏ lỡ; những người khác chờ đợi kết quả.*

### Luồng bộ nhớ đệm```text
GET /users
    ├── Redis hit?  → return cached JSON (source: cache)
    └── Redis miss? → query DB → serialize → SET in Redis (TTL 60s) → return JSON (source: db)
```## 3. MÃ

### Ví dụ 1: Cơ bản — Redis Client Cache```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Cache-aside: check Redis → miss → query DB → SET cache.
    // createUser invalidates cache to avoid stale data.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package main

    import (
        "encoding/json"
        "net/http"
        "time"
        "github.com/gin-gonic/gin"
        "github.com/redis/go-redis/v9"
    )

    var rdb *redis.Client

    func init() {
        rdb = redis.NewClient(&redis.Options{Addr: "localhost:6379"})
    }

    func fetchUsersFromDB() []map[string]any {
        return []map[string]any{
            {"id": 1, "name": "Alice"},
        }
    }

    func listUsers(c *gin.Context) {
        ctx := c.Request.Context()

        cached, err := rdb.Get(ctx, "users:list").Result()
        if err == nil {
            var users []map[string]any
            json.Unmarshal([]byte(cached), &users)
            c.JSON(http.StatusOK, gin.H{"data": users, "source": "cache"})
            return
        }

        users := fetchUsersFromDB()

        data, _ := json.Marshal(users)
        rdb.Set(ctx, "users:list", data, 60*time.Second)

        c.JSON(http.StatusOK, gin.H{"data": users, "source": "db"})
    }

    func createUser(c *gin.Context) {
        rdb.Del(c.Request.Context(), "users:list") 
        c.JSON(http.StatusCreated, gin.H{"message": "created"})
    }
```### Ví dụ 2: Trung cấp — Bộ chặn phản hồi```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // CacheMiddleware: intercepts GET requests, returns cached
    // response or captures handler output to cache.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package middleware

    import (
        "crypto/sha256"
        "encoding/hex"
        "encoding/json"
        "net/http"
        "time"
        "github.com/gin-gonic/gin"
        "github.com/redis/go-redis/v9"
    )

    func CacheMiddleware(rdb *redis.Client, ttl time.Duration) gin.HandlerFunc {
        return func(c *gin.Context) {
            if c.Request.Method != http.MethodGet {
                c.Next()
                return
            }

            hash := sha256.Sum256([]byte(c.Request.URL.RequestURI()))
            key := "cache:" + hex.EncodeToString(hash[:])
            ctx := c.Request.Context()

            cached, err := rdb.Get(ctx, key).Result()
            if err == nil {
                var response map[string]any
                json.Unmarshal([]byte(cached), &response)
                c.JSON(http.StatusOK, response)
                c.Abort()
                return
            }

            w := &responseCapture{ResponseWriter: c.Writer}
            c.Writer = w

            c.Next()

            if c.Writer.Status() == http.StatusOK && len(w.body) > 0 {
                rdb.Set(ctx, key, w.body, ttl)
            }
        }
    }

    type responseCapture struct {
        gin.ResponseWriter
        body []byte
    }

    func (w *responseCapture) Write(b []byte) (int, error) {
        w.body = append(w.body, b...)
        return w.ResponseWriter.Write(b)
    }
```---

## 4. Cạm bẫy

| # | Mức độ nghiêm trọng | Khiếm khuyết | Tác động | Sửa chữa |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Gây tử vong | Không có hiệu lực bộ đệm khi ghi | Khách hàng thấy dữ liệu cũ sau khi tạo/cập nhật | `rdb.Del()` các khóa bị ảnh hưởng trong mọi trình xử lý ghi |
| 2 | 🔴 Gây tử vong | Bộ nhớ đệm bị xáo trộn: 1000 truy vấn DB đồng thời bị trượt đồng thời | Nhóm kết nối cơ sở dữ liệu đã cạn kiệt | Sử dụng `golang.org/x/sync/singleflight` để loại bỏ trùng lặp |

---

## 5. GIỚI THIỆU

| Tài nguyên | Liên kết |
| --- | --- |
| Redis Đi | [redis.io/docs/latest/develop/clients/go/](https://redis.io/docs/latest/develop/clients/go/) |

---

## 6. KHUYẾN NGHỊ

| Gia hạn | Khi nào | Cơ sở lý luận | Tài nguyên |
| --- | --- | --- | --- |
| Ghi nhật ký | Khi gỡ lỗi lần truy cập/lỗi bộ đệm trong quá trình sản xuất | Nhật ký có cấu trúc với ID yêu cầu giúp theo dõi hành vi bộ đệm | [./05-logging.md](./05-logging.md) |