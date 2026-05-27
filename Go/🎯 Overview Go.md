Chào mừng bạn đến với kho lưu trữ tài nguyên chuyên sâu về ngôn ngữ lập trình **Go (Golang)**. Thư mục này được thiết kế như một lộ trình huấn luyện toàn diện từ con số 0 đến cấp độ chuyên gia, giúp bạn chuyển đổi tư duy vững chắc từ nền tảng Javascript/Typescript (Node.js/NestJS) sang mô hình lập trình hệ thống cực kỳ tối ưu của Go.

Không gian học tập được chia thành hai phân vùng chính:

---

### 📘 1. Go Fundamental (Ngôn ngữ & Cấu trúc nâng cao)
Nằm trong thư mục [**`./Fundamental/`**](./Fundamental), tập trung giúp bạn làm chủ cú pháp hệ thống, quản lý bộ nhớ và các mẫu thiết kế hướng đối tượng tối tân:

* [**🎯 Bản Đồ Chi Tiết Go Fundamental**](./Fundamental/🎯%20Overview%20Go%20Fundamental.md) - Tổng quan toàn diện lộ trình học tập nền tảng.
* [**Go Basics Guide**](./Fundamental/go-basics-guide.html) - Hướng dẫn toàn diện 12 chuyên đề cơ sở:
  * Khai báo biến, cú pháp điều khiển, zero values.
  * Bộ ba quản lý tài nguyên: `Defer, Panic, Recover`.
  * Cơ chế bộ nhớ: Con trỏ (Pointers), phân tích Stack vs Heap (Escape Analysis).
  * Xử lý lỗi tường minh: Sentinel errors, wrapping lỗi với `%w` và kỹ thuật gộp lỗi `errors.Join`.
  * Thư viện tiện ích lõi: `strings`, `strconv`, `fmt`, `math`, và cấu trúc động `Slices & Maps`.
* [**Go Advanced Patterns**](./Fundamental/go-advanced-guide.html) - Hướng dẫn lập trình chuyên sâu 12 chuyên đề thực tiễn:
  * Tái cấu trúc kiểu dữ liệu nâng cao, Generic Data Converters.
  * Đường ống xử lý dữ liệu `Array Pipeline` dạng Functional (Map/Filter/Reduce).
  * Mô phỏng mô hình bất đồng bộ: `Promise / Async` thông qua `errgroup`.
  * Làm chủ lịch biểu nâng cao (`time.Time`) và múi giờ.
  * Cài đặt kiểu Enum an toàn (Sealed Interfaces) và Concurrent Map / Sharded Map tránh xung đột luồng.
  * Ứng dụng tính năng lặp thế hệ mới **Iterator (Go 1.23 range-over-func)**.
  * Triển khai mẫu `Option[T]` triệt tiêu hoàn toàn lỗi con trỏ null.
  * Lập trình hướng đối tượng đặc sản Go (Embedding, Đa hình ngầm định, Builder & Decorator).

---

### ⚡ 2. Go Concurrency (Lập trình song song & Hệ thống)
Nằm trong thư mục [**`./Concurrency/`**](./Concurrency), tập trung vào vũ khí tối thượng của Go — concurrency mô hình CSP (Communicating Sequential Processes):

* [**🎯 Bản Đồ Chi Tiết Go Concurrency**](./Concurrency/🎯%20Overview%20Go%20Concurrency.md) - Tổng quan lộ trình chinh phục hệ thống concurrent song song.
* **Các chủ đề cốt lõi & Mẫu thiết kế (21 chuyên đề)**:
  * [**Lightweight Threads**](./Concurrency/01-goroutines-guide.html) - Cơ chế vận hành Goroutine scheduler.
  * [**Channels & Communication**](./Concurrency/02-buffered-unbuffered-channels.html) - Cơ chế đồng bộ hóa luồng dữ liệu thông qua kênh đệm (Buffered) và không đệm (Unbuffered).
  * [**Race Conditions & Mutexes**](./Concurrency/04-mutex-and-confinement.html) - Bảo vệ tài nguyên chia sẻ, tránh deadlock và xung đột luồng.
  * [**Context Control**](./Concurrency/07-context.html) - Lan truyền tín hiệu hủy (Cancellation), timeout, hạn chế rò rỉ goroutine.
  * [**Pipeline & Fan-Out/Fan-In**](./Concurrency/11-fan-out-fan-in-go-pattern.html) - Xây dựng hệ thống luồng dữ liệu song song cực mạnh.
  * [**Worker Pools**](./Concurrency/12-worker-pool.html) - Hạn chế lượng goroutine đồng thời chạy bằng cơ chế tái sử dụng luồng (như BullMQ).
  * [**Resource Tuning & Semaphores**](./Concurrency/19-semaphore-guide.html) - Tiết kiệm tài nguyên qua `sync.Pool`, điều phối giới hạn tác vụ đồng thời qua Semaphore.
  * [**Background Jobs**](./Concurrency/21-asynq.html) - Xử lý tác vụ nền bất đồng bộ hiệu năng cao sử dụng thư viện `Asynq`.

---

### 🚀 Bản Đồ So Sánh Tư Duy Nhanh (Node.js vs Go)

| Đặc tính kiến trúc | Node.js (V8 Engine) | Go (Golang Runtime) |
| :--- | :--- | :--- |
| **Mô hình thực thi** | Single-threaded Event Loop (Bất đồng bộ phi tuần tự). | Multi-threaded M:N Scheduler (Goroutines chạy thực sự song song trên CPU). |
| **Giao tiếp luồng** | Shared memory / Event Emitters / Callback queues. | **Channels** (Giao tiếp thông qua truyền nhận thông điệp an toàn). |
| **Xử lý bất đồng bộ** | `Promise`, `async/await`. | `select` multiplexing, Goroutines & Channels. |
| **Đồng bộ hóa** | Không cần lo lắng race condition trên biến (trừ I/O). | Bắt buộc phải đồng bộ hóa bằng `sync.Mutex` hoặc cô lập dữ liệu (Confinement). |
| **Quản lý tài nguyên** | Cấp phát động tự do, Garbage Collector của V8 dọn dẹp. | Tối ưu hóa tối đa thông qua tái sử dụng đối tượng (`sync.Pool`), giảm thiểu Escape to Heap. |

---

### 📅 Lộ Trình Gợi Ý Tinh Gọn Cho Bạn

1. **Giai đoạn 1 (Chắc móng)**: Đọc kỹ tài liệu [Go Basics Guide](./Fundamental/go-basics-guide.html). Thực hành viết các chức năng xử lý lỗi an toàn và bọc lỗi bằng `%w`.
2. **Giai đoạn 2 (Tư duy kiến trúc)**: Đọc tiếp [Go Advanced Patterns](./Fundamental/go-advanced-guide.html) để học cách tổ chức mã nguồn chuẩn idiomatic Go (không dùng class, dùng interface và struct embedding). Xây dựng cấu trúc dữ liệu Set và Option tùy chỉnh.
3. **Giai đoạn 3 (Song song hóa)**: Đi sâu vào thế giới [Go Concurrency](./Concurrency). Bắt đầu với Goroutines, Channels cơ bản, sau đó nâng cấp lên mô hình pipeline dữ liệu phức tạp phối hợp cùng `context` và `errgroup`.
4. **Giai đoạn 4 (Tinh chỉnh & Performance)**: Học cách phát hiện race condition bằng `-race`, phân tích hiệu năng bằng công cụ `pprof`, tối ưu hóa phân bổ bộ nhớ với `sync.Pool`.
