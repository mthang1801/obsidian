<!-- tags: golang, oop, design-patterns --> # 🏗️ Design Patterns , Cách Go — Đơn giản hơn mong đợi

> Nhiều design patterns đơn giản hóa đáng kể trong Go . Các nhà máy trở thành chức năng. Chiến lược trở thành interfaces . Người quan sát chạy qua channels . Singletons bọc trong `sync.Once` . Hướng dẫn này hiển thị các cách triển khai Go thành ngữ.

📅 Đã tạo: 2026-04-10 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 18 phút đọc

| Khía cạnh | Chi tiết |
| ----------------- | --------------------------------------------------- |
| **Khái niệm** | GoF design patterns được triển khai lại trong thành ngữ Go |
| **Trường hợp sử dụng** | Thiết kế mã, quyết định kiến ​​trúc |
| **Thông tin chi tiết quan trọng** | Nhiều mẫu đơn giản hóa. Một số biến mất. Không yêu cầu phân cấp lớp. |
| ** Go triết lý** | Đừng triển khai một mẫu cho đến khi bạn cần nó |

---

## 1. ĐỊNH NGHĨA

Một nhóm phát triển mới bắt đầu viết Go . Bạn xem xét một PR tạo `AbstractPaymentProcessorFactory` — chứa 4 tệp, 3 interfaces , 2 cơ sở trừu tượng structs , trải dài 150 dòng.

Người đánh giá mã cấp cao nhận xét: "Bạn chỉ yêu cầu `NewStripeProcessor()` . Một hàm. Tổng cộng có 8 dòng."```go
func NewStripeProcessor(apiKey string) *StripeProcessor {
    return &StripeProcessor{apiKey: apiKey}
}
```Bạn so sánh `AbstractPaymentProcessorFactory` và nhận ra: Java cần 150 dòng vì `new` bỏ qua xác thực, các hàm tạo không thể trả về lỗi và hệ thống phân cấp lớp cần một lớp trừu tượng cho polymorphism . Go : Các hàm `NewXxx()` xác thực, trả về lỗi và các loại cụ thể yield . Mẫu Factory giảm xuống còn 1 hàm.

**Không phải mọi mẫu đều đơn giản hóa như nhau** — Strategy , Observer và Middleware vẫn cần cấu trúc. Nhưng cấu trúc đó nhẹ hơn cấu trúc tương đương của Java.

### Ma trận chuyển đổi mẫu

| Mẫu kế thừa | Triển khai Java Format | Go Format Thực hiện | Kết quả đơn giản hóa |
| --- | --- | --- | --- |
| ** Factory ** | Các lớp kế thừa factory + cụ thể factory | `NewXxx()` chức năng chính xác | Lớp học → 1 hàm gốc |
| ** Builder ** | Builder lớp logic + Giám đốc chính thức | Tùy chọn chức năng format `With...()` | Phần tử lớp → hàm thuần túy |
| ** Singleton ** | Khóa kiểm tra hai lần + trường tĩnh cứng nhắc | `sync.Once` + target package -biến cấp độ | Giảm 20 dòng → 5 dòng |
| ** Strategy ** | Interface + định nghĩa trừu tượng + lớp cụ thể | Bản địa interface + cấu trúc thô struct | Không cần định dạng lớp cơ sở trừu tượng |
| ** Observer ** | Ánh xạ EventListener + Điều phối EventManager | Channels tham số + thực thi goroutines | Không có danh sách đăng ký, không có chuỗi callback riêng biệt |
| ** Decorator ** | Các lớp bao bọc sâu chính thức mở rộng cơ sở | Mẫu hàm phần mềm trung gian `func(H) H` | Không cần lớp cơ sở |
| ** Iterator ** | Iterator format interface + vòng bê tông | Đích `range` logic + cấu trúc channels | Được xây dựng chính thức trực tiếp vào các thành phần ngôn ngữ trình biên dịch |
| **Phương pháp mẫu** | Lớp trừu tượng inheritance + ghi đè bắt buộc | Giao thức interface cơ bản + chức năng mặc định gốc | Không có lớp trừu tượng |

### Chế độ lỗi

| Khiếm khuyết cấu trúc | Nguyên nhân gốc rễ | Hiệu ứng gợn sóng |
| --- | --- | --- |
| Dịch các mẫu Java 1:1 | "Phải có nhà máy trừu tượng" | Kỹ thuật quá mức, không thành ngữ |
| Bỏ qua hoàn toàn các mẫu | " Go rất đơn giản, không cần mẫu" | Mã spaghetti ở quy mô |
| Xây dựng mô hình sớm | Triển khai trước 3 trường hợp sử dụng cụ thể | Trừu tượng không cần thiết |

Mẫu map rõ ràng. Hãy triển khai 3 mẫu quan trọng - bắt đầu bằng Factory .

---

## 2. HÌNH ẢNH

### Java so với Go Độ phức tạp về cấu trúc```mermaid
flowchart LR
    subgraph Java["Java Native Patterns"]
        direction TB
        J1["Factory logic\n4 files, 150 code lines"]
        J2["Strategy logic\n3 rigid classes + base abstract"]
        J3["Observer logic\nEventListener struct + formal Manager logic"]
        J4["Singleton structure\nExplicit DCL + strict volatile parameter"]
    end

    subgraph Go["Go Logical Idiomatic Patterns"]
        direction TB
        G1["Factory format\n1 clean function, 8 code lines"]
        G2["Strategy format\nbare interface + fundamental struct"]
        G3["Observer target\nprimitive channel parameter + pure goroutine parameter"]
        G4["Singleton\nsync.Once variable flag, 5 isolated code lines"]
    end

    J1 -.->|"-95% lines"| G1
    J2 -.->|"-60% lines"| G2
    J3 -.->|"-70% lines"| G3
    J4 -.->|"-75% lines"| G4
```![Design patterns Go way taxonomy card](./images/06-design-patterns-go-way-taxonomy.png) *Hình: Mục tiêu giảm độ phức tạp khi vận hành: Factory –95%, Singleton –75%, Observer –70%, Strategy –60%. Các tính năng ngôn ngữ tích hợp sẽ loại bỏ hoàn toàn bản mẫu soạn sẵn cũ.*

### Mô hình cây quyết định mẫu cấu trúc```mermaid
flowchart TD
    A[Require dynamically generating new memory objects?] -->|Executing validation at pure construction stage| B["Factory pattern: NewXxx() target execution"]
    A -->|Configuring numerous distinct optional specific initialization parameters| C["Builder pattern logic: Functional Options variables"]
    D[Require natively swapping execution behavior methods?] -->|Executing pure runtime algorithmic procedural swaps| E["Strategy logic mapping: Explicit interface targeted parameter injection"]
    D -->|Targeting HTTP networking Request execution pipeline elements| F["Decorator execution model: Functional middleware func(H)H mapping"]
    G[Require broadcasting fundamental system events functionally?] -->|Targeting distinct async decoupled operations| H["Observer architectural format: Pure native channels operations"]
    G -->|Execution via tight synchronous execution callback requirements| I["Event callback handling logic: Simple formal func structure slice"]
    J[Require rigid global exact strict native singleton instance definition?] --> K["Singleton structural parameter definition: Native sync.Once variables"]
```*Hình: 7 mẫu phổ biến được dịch sang thành ngữ Go . Không có lớp trừu tượng ở bất cứ đâu.*

---
### Ví dụ 1: Cơ bản — Factory + Tùy chọn chức năng.

 Mẫu Factory trong Java: abstractFactory → ConcreteFactory → Product. Hàm Go : `NewXxx()` . Khi cần nhiều thông số tùy chọn: các tùy chọn chức năng.

> **Mục tiêu**: mẫu Factory + Builder thay thế (tùy chọn chức năng).
> **Phương pháp tiếp cận**: `NewServer()` thông số bắt buộc + `WithXxx()` thông số tùy chọn.
> **Ví dụ**: Máy chủ HTTP có thời gian chờ, trình ghi nhật ký, TLS có thể định cấu hình.```go
// factory.go — Factory + Functional Options pattern
package server

import (
	"log"
	"time"
	"crypto/tls"
)

// Server — the "product"
type Server struct {
	host         string
	port         int
	timeout      time.Duration
	logger       *log.Logger
	tlsConfig    *tls.Config
	maxBodyBytes int64
}

// Option — functional option type
type Option func(*Server)

// WithXxx — each option is a function returning Option
func WithTimeout(d time.Duration) Option {
	return func(s *Server) { s.timeout = d }
}

func WithLogger(l *log.Logger) Option {
	return func(s *Server) { s.logger = l }
}

func WithTLS(config *tls.Config) Option {
	return func(s *Server) { s.tlsConfig = config }
}

func WithMaxBody(bytes int64) Option {
	return func(s *Server) { s.maxBodyBytes = bytes }
}

// NewServer — factory function: required params + optional options
// ✅ Replace: AbstractServerFactory + ConcreteServerFactory + ServerBuilder + Director
func NewServer(host string, port int, opts ...Option) (*Server, error) {
	if host == "" {
		return nil, fmt.Errorf("host required")
	}
	if port <= 0 || port > 65535 {
		return nil, fmt.Errorf("invalid port: %d", port)
	}

	// Defaults — sane, overridable
	s := &Server{
		host:         host,
		port:         port,
		timeout:      30 * time.Second,
		maxBodyBytes: 1 << 20, // 1MB
	}

	// Apply options
	for _, opt := range opts {
		opt(s)
	}

	return s, nil
}

// Usage:
// s, err := NewServer("localhost", 8080,
//     WithTimeout(5 * time.Second),
//     WithTLS(tlsConfig),
//     WithLogger(customLogger),
// )
```> **Tại sao có lớp Tùy chọn chức năng thay vì lớp Builder ?**
> Lớp Builder : `ServerBuilder.SetHost().SetPort().Build()` — đối tượng builder có thể thay đổi, các phương thức xâu chuỗi, bước Build() riêng biệt. Tùy chọn chức năng: hàm bất biến, có thể kết hợp, không có trạng thái trung gian. Dave Cheney ( nhóm cốt lõi Go ): "Các tùy chọn chức năng là cách giống Go nhất để xây dựng các đối tượng phức tạp." Cần một lựa chọn khác sau này? Thêm 1 chức năng - mã hiện tại không thay đổi.

> **Takeaway**: hàm Factory = `NewXxx()` . Builder = Tùy chọn chức năng `WithXxx()` . Cả hai mẫu Java đều thu gọn thành một mẫu Go - đơn giản hơn, thành ngữ hơn. Factory bao gồm việc tạo đối tượng. Strategy hoán đổi hành vi bìa - mẫu quan trọng nhất đối với OCP.

---

### Ví dụ 2: Trung cấp — Strategy + Middleware ( Decorator ). Strategy : thuật toán hoán đổi tại runtime thông qua interface tiêm. Phần mềm trung gian: mẫu decorator cho đường dẫn HTTP.

> **Mục tiêu**: mẫu Strategy + Decorator làm phần mềm trung gian.
> **Cách tiếp cận**: `Compressor` interface ( strategy ). `Middleware func(http.Handler) http.Handler` ( decorator ).
> **Ví dụ**: Trình nén tệp hoán đổi gzip/zstd. Chuỗi phần mềm trung gian HTTP.```go
// strategy.go — Strategy pattern
package compress

import (
	"bytes"
	"compress/gzip"
	"io"
)

// Compressor — strategy interface
type Compressor interface {
	Compress(data []byte) ([]byte, error)
	Extension() string
}

// GzipCompressor — concrete strategy
type GzipCompressor struct {
	Level int
}

func (g *GzipCompressor) Compress(data []byte) ([]byte, error) {
	var buf bytes.Buffer
	w, err := gzip.NewWriterLevel(&buf, g.Level)
	if err != nil {
		return nil, err
	}
	if _, err := w.Write(data); err != nil {
		return nil, err
	}
	if err := w.Close(); err != nil {
		return nil, err
	}
	return buf.Bytes(), nil
}

func (g *GzipCompressor) Extension() string { return ".gz" }

// ZstdCompressor — another strategy (added later, 0 changes to FileExporter)
type ZstdCompressor struct{}

func (z *ZstdCompressor) Compress(data []byte) ([]byte, error) {
	// ... zstd compression ...
	return data, nil
}
func (z *ZstdCompressor) Extension() string { return ".zst" }

// FileExporter — uses strategy, doesn't know which compressor
type FileExporter struct {
	compressor Compressor // injected
}

func NewFileExporter(c Compressor) *FileExporter {
	return &FileExporter{compressor: c}
}

func (fe *FileExporter) Export(filename string, data []byte) error {
	compressed, err := fe.compressor.Compress(data)
	if err != nil {
		return fmt.Errorf("compress: %w", err)
	}
	outFile := filename + fe.compressor.Extension()
	return os.WriteFile(outFile, compressed, 0644)
}
```

```go
// middleware.go — Decorator pattern as HTTP middleware
package middleware

import (
	"log"
	"net/http"
	"time"
)

// Middleware type — decorator pattern in 1 line
// func(http.Handler) http.Handler = wraps handler, returns new handler
type Middleware func(http.Handler) http.Handler

// Logging middleware
func Logging(logger *log.Logger) Middleware {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()
			next.ServeHTTP(w, r) // ← delegate to wrapped handler
			logger.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
		})
	}
}

// Auth middleware
func RequireAuth(tokenValidator func(string) bool) Middleware {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			token := r.Header.Get("Authorization")
			if !tokenValidator(token) {
				http.Error(w, "unauthorized", http.StatusUnauthorized)
				return // ← short circuit: don't call next
			}
			next.ServeHTTP(w, r)
		})
	}
}

// Chain — compose middleware
func Chain(handler http.Handler, middlewares ...Middleware) http.Handler {
	// Apply in reverse order — outermost middleware wraps first
	for i := len(middlewares) - 1; i >= 0; i-- {
		handler = middlewares[i](handler)
	}
	return handler
}

// Usage:
// handler := Chain(myHandler,
//     Logging(logger),
//     RequireAuth(validateToken),
//     RateLimit(100),
// )
```> **Tại sao lại là phần mềm trung gian thay vì lớp Decorator ?**
> Java Decorator : `class LoggingHandler extends HandlerWrapper { ... }` — lớp trên decorator , mở rộng base. Go : `func(http.Handler) http.Handler` — 1 hàm = 1 decorator . Không có lớp, không mở rộng, không có cơ sở. Soạn với `Chain()` . Cùng một mẫu.

> **Takeaway**: Strategy = interface + tiêm — giống như Java, trừ lớp trừu tượng. Middleware = decorator thông qua hàm composition - Go Mặt chức năng của Go tỏa sáng ở đây. Factory , Strategy , Decorator bao gồm các mẫu "cấu trúc + hành vi". Observer - mẫu dành cho hướng sự kiện - Go có một công cụ tích hợp: channels .

---

### Ví dụ 3: Nâng cao — Observer qua Channels + Singleton qua sync.Once. Observer trong Go không cần EventListener interface — channels LÀ cơ chế. Singleton : `sync.Once` thay vì khóa được kiểm tra hai lần.

> **Mục tiêu**: mẫu Observer qua channels . Singleton qua sync.Once.
> **Phương pháp tiếp cận**: Sự kiện channel + người đăng ký goroutines . Package -level var + sync.Once.
> **Ví dụ**: Xuất bản/đăng ký xe buýt sự kiện. Cấu hình singleton .```go
// observer.go — Observer pattern via channels
package eventbus

import (
	"context"
	"sync"
)

// Event — domain event
type Event struct {
	Type    string
	Payload any
}

// EventBus — publisher
type EventBus struct {
	mu          sync.RWMutex
	subscribers map[string][]chan Event
}

func NewEventBus() *EventBus {
	return &EventBus{
		subscribers: make(map[string][]chan Event),
	}
}

// Subscribe — returns channel for events of given type
// ✅ No EventListener interface needed — channel IS the listener
func (eb *EventBus) Subscribe(eventType string, bufSize int) <-chan Event {
	ch := make(chan Event, bufSize)
	eb.mu.Lock()
	eb.subscribers[eventType] = append(eb.subscribers[eventType], ch)
	eb.mu.Unlock()
	return ch
}

// Publish — fan-out to all subscribers
func (eb *EventBus) Publish(ctx context.Context, evt Event) {
	eb.mu.RLock()
	subs := eb.subscribers[evt.Type]
	eb.mu.RUnlock()

	for _, ch := range subs {
		select {
		case ch <- evt: // non-blocking if buffer available
		case <-ctx.Done():
			return
		default:
			// ⚠️ Subscriber slow — drop event (or log, or buffer)
			// Decision: drop vs block vs buffer depends on your SLA
		}
	}
}

// Close — clean up all channels
func (eb *EventBus) Close() {
	eb.mu.Lock()
	defer eb.mu.Unlock()
	for _, subs := range eb.subscribers {
		for _, ch := range subs {
			close(ch)
		}
	}
}

// Usage:
// bus := NewEventBus()
// orderEvents := bus.Subscribe("order.placed", 100)
// go func() {
//     for evt := range orderEvents {
//         log.Printf("Order placed: %v", evt.Payload)
//     }
// }()
// bus.Publish(ctx, Event{Type: "order.placed", Payload: order})
```

```go
// singleton.go — Singleton via sync.Once
package config

import (
	"os"
	"sync"
)

// config — unexported type, cannot be instantiated externally
type config struct {
	DatabaseURL string
	Port        string
	Debug       bool
}

var (
	instance *config
	once     sync.Once
)

// Get — returns singleton config
// ✅ sync.Once guarantees exactly 1 initialization, thread-safe
// No double-checked locking, no volatile, no synchronized
func Get() *config {
	once.Do(func() {
		instance = &config{
			DatabaseURL: os.Getenv("DATABASE_URL"),
			Port:        getEnvOr("PORT", "8080"),
			Debug:       os.Getenv("DEBUG") == "true",
		}
	})
	return instance
}

func getEnvOr(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

// Usage: cfg := config.Get()
// First call: initializes. All subsequent calls: returns same instance.
// Thread-safe. No mutex needed after initialization.
```> **Tại sao channel thay vì callback /EventListener?**.
> Java Observer : `listener.onEvent(event)` — đồng bộ callback , người nghe phải triển khai interface , hủy đăng ký phức tạp. Go channels : async theo mặc định, được lưu vào bộ đệm để tách rời, `range` để lặp lại, `close()` để phân tách. Channel tích hợp áp suất ngược (bộ đệm đầy = nhà xuất bản bị chặn hoặc bị rớt). Không có EventListener, không có điệu nhảy hủy đăng ký.
>
> **đồng bộ hóa.Một lần so với khóa được kiểm tra hai lần?**
> Java DCL: 10 dòng, `volatile` + `synchronized` + kiểm tra null × 2. Dễ mắc lỗi. Go `sync.Once` : được đảm bảo bởi runtime , không có cơ hội chạy đua. Tổng cộng 5 dòng. Xong.

> **Takeaway**: Observer = channels + goroutines — Go ’s concurrency nguyên thủy LÀ mẫu. Singleton = `sync.Once` — 5 dòng, thread -an toàn, xong. Nhiều mẫu GoF được đơn giản hóa hoặc hấp thụ bởi các tính năng tích hợp của Go .

---

## 4. Cạm bẫy

| # | Mức độ nghiêm trọng | Lỗi | Hậu quả | Sửa chữa |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Gây tử vong | Dịch các mẫu Java 1:1 (lớp AbstractFactory, Builder ) | Kỹ thuật quá mức, không thành ngữ | `NewXxx()` + tùy chọn chức năng |
| 2 | 🔴 Gây tử vong | Observer bị rò rỉ goroutine — người đăng ký không bao giờ đóng | Rò rỉ bộ nhớ, số lượng goroutine tăng mãi mãi | Hủy bối cảnh + dọn dẹp `Close()` + defer |
| 3 | 🟡 Chung | Singleton lạm dụng (sử dụng cho mọi thứ) | Sự phụ thuộc ẩn giấu, thử nghiệm địa ngục | Thích tiêm rõ ràng. Singleton chỉ dành cho cấu hình, logger |
| 4 | 🟡 Chung | Channel Observer không có áp suất ngược | Nhà xuất bản chặn khi người đăng ký chậm | Đã lưu vào bộ đệm channel + `select default` hoặc ghi |
| 5 | 🔵 Nhỏ | Mẫu sớm - áp dụng trước trường hợp sử dụng thứ 3 | Trừu tượng không cần thiết | Đợi 3 trường hợp cụ thể rồi trích xuất mẫu |

---

## 5. GIỚI THIỆU

| Tài nguyên | Loại | Liên kết | Lưu ý |
| --- | --- | --- | --- |
| Go Design Patterns | Sách | https://www.packtpub.com/product/go-design-potypes/9781786466204 | Toàn diện |
| Dave Cheney — SOLID Go | Nói chuyện | https://dave.cheney.net/2016/08/20/ solid -go-design | Mẫu + SOLID |
| Tùy chọn chức năng | Blog | https://dave.cheney.net/2014/10/17/function-options-for-friend-apis | Đề xuất ban đầu |

---

## 6. KHUYẾN NGHỊ

Cốt lõi của ** Design Patterns — Go Cách** rất rõ ràng. Các nhánh tiện ích mở rộng bên dưới giúp bạn đưa design patterns vào sản xuất với DDD, kiến ​​trúc sạch và các mẫu vi dịch vụ.

| Gia hạn | Khi nào | Lý do | Tệp/Liên kết |
| --- | --- | --- | --- |
| [Go Concurrency](../../concurrency/) | Khi bạn cần goroutines , channels , hãy đồng bộ hóa các mẫu | mẫu Observer → concurrency lặn sâu | Go bài hát |
| [Go Design Patterns](../../design-patterns/) | Khi bạn cần một danh mục mẫu đầy đủ | Tất cả các mẫu GoF đều thành ngữ | Go bài hát |
| [Clean Architecture](../../../architecture/go/) | Khi bạn cần cấu trúc ứng dụng | DDD + Kiến trúc sạch trong Go | Kiến trúc |
| [OOP Mental Model](./01-oop-mental-model.md) | Khi bạn cần xem lại khung hình | Toàn bộ Java map → Go | Thư mục này |

---

**Điều hướng**: [← SOLID in Go](./05-solid-in-go.md) · [→ OOP in Go Hub](./README.md)