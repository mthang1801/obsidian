<!-- tags: golang --> # 💉 Tiêm phụ thuộc — NestJS DI Container → Hướng dẫn sử dụng/Dây/fx

> **Thư viện**: Chèn hàm tạo thủ công hoặc tạo mã thời gian biên dịch bằng Google Wire — thay thế vùng chứa NestJS DI.

📅 Cập nhật: 2026-04-19 · ⏱️ 14 phút đọc

## 1. ĐỊNH NGHĨA

NestJS có bộ chứa IoC tích hợp với các bộ trang trí `@Injectable()` . Go không có DI thời gian chạy — bạn kết nối các phần phụ thuộc theo cách thủ công trong `main.go` hoặc sử dụng các công cụ tạo mã tại thời gian biên dịch như Google Wire. Cả hai phương pháp đều chấp nhận giao diện, cho phép chèn mô hình vào thử nghiệm.

| NestJS | Đi tương đương |
| ------------------------------------ | ----------------------------------------- |
| `@Injectable()` + `@Inject()` | Đối số hàm tạo thời gian chạy rõ ràng |
| `@Module({ providers: [...] })` | `main.go` dây hoặc tệp Google Wire |
| `useClass` , `useValue` , `useFactory` | Giao diện trả về khởi tạo trực tiếp |

### Bất biến chính

- **Chấp nhận giao diện, trả về cấu trúc.** Trình xây dựng lấy `UserRepository` (giao diện), return `*UserService` (cụ thể).
- **Dây vào `main.go` , không phải trong các gói miền.** Mã miền không nên biết nó được tập hợp như thế nào.

## 2. HÌNH ẢNH ![DI patterns — Manual constructor, Google Wire (compile-time), Uber fx (runtime)](./images/02-dependency-injection.png) *Hình: Ba cách tiếp cận Go DI — Thủ công (rõ ràng, nối dây chính()), Google Wire (codegen thời gian biên dịch, không phản chiếu), Uber fx (vùng chứa thời gian chạy như NestJS).*```mermaid
flowchart TD
    A["main.go"] -->|"NewPostgresRepo(db)"| B["UserRepository iface"]
    A -->|"NewService(repo)"| C["UserService"]
    A -->|"NewHandler(svc)"| D["UserHandler"]
    D -->|"register routes"| E["gin.Engine"]
    style B stroke-dasharray: 5 5
```*Hình: Đi dây DI trong `main.go` — loại bê tông chảy xuống, bề mặt tiếp xúc hướng lên trên. Các gói miền không bao giờ nhập `main` .*

### Phương pháp tiếp cận DI```text
Manual:  main.go creates all deps in order (simplest, ~20 deps)
Wire:    compile-time codegen from provider sets (scales to 100+ deps)
fx:      runtime container with lifecycle hooks (Uber pattern)
```## 3. MÃ

### Ví dụ 1: Cơ bản — Chèn thủ công```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Manual DI: create deps in main.go, pass via constructors.
    // Each New* function accepts interfaces, returns concrete.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package main

    import (
        "log"
        "myapp/internal/config"
        "myapp/internal/database"
        "myapp/internal/users"
        "github.com/gin-gonic/gin"
    )

    func main() {
        cfg := config.Load()
        db := database.Connect(cfg.Database)

        userRepo := users.NewPostgresRepository(db)
        userService := users.NewService(userRepo)
        userHandler := users.NewHandler(userService)

        r := gin.Default()
        api := r.Group("/api/v1")

        users.RegisterRoutes(api, userHandler)

        log.Fatal(r.Run(":" + cfg.App.Port))
    }
```### Ví dụ 2: Trung cấp — Compile-Time Wire```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Google Wire: declare provider sets, Wire generates
    // the InitializeApp() function at compile time.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    //go:build wireinject

    package main

    import (
        "myapp/internal/config"
        "myapp/internal/database"
        "myapp/internal/users"
        "github.com/google/wire"
        "github.com/gin-gonic/gin"
    )

    var infrastructureSet = wire.NewSet(
        config.Load,
        database.Connect,
    )

    var userSet = wire.NewSet(
        users.NewPostgresRepository,
        wire.Bind(new(users.Repository), new(*users.PostgresRepository)),
        users.NewService,
        users.NewHandler,
    )

    func InitializeApp() (*gin.Engine, error) {
        wire.Build(
            infrastructureSet,
            userSet,
            newRouter,
        )
        return nil, nil
    }

    func newRouter(userHandler *users.Handler) *gin.Engine {
        r := gin.Default()
        api := r.Group("/api/v1")
        users.RegisterRoutes(api, userHandler)
        return r
    }
```---

## 4. Cạm bẫy

| # | Mức độ nghiêm trọng | Khiếm khuyết | Tác động | Sửa chữa |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Gây tử vong | Chấp nhận các kiểu cụ thể trong hàm tạo thay vì giao diện | Không thể hoán đổi việc triển khai để thử nghiệm; trình xử lý được ghép nối với Postgres | `NewService(repo UserRepository)` không phải `NewService(repo *PostgresRepo)` |
| 2 | 🟡 Chung | Sự phụ thuộc vòng tròn giữa các gói | Lỗi biên dịch hoặc bế tắc ban đầu | Trích xuất các giao diện dùng chung thành gói `domain` riêng biệt |

---

## 5. GIỚI THIỆU

| Tài nguyên | Liên kết |
| --- | --- |
| Dây Google | [github.com/google/wire](https://github.com/google/wire) |

---

## 6. KHUYẾN NGHỊ

| Gia hạn | Khi nào | Cơ sở lý luận | Tài nguyên |
| --- | --- | --- | --- |
| Móc vòng đời | Khi bạn cần điều phối khởi động/tắt máy | Quản lý kết nối DB, khởi động bộ đệm và thoát nước nhẹ nhàng | [./03-lifecycle-hooks.md](./03-lifecycle-hooks.md) |