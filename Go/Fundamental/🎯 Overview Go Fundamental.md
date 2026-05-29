#### **LEVEL 1: Core Basics (Basics Guide — Modules 1-6)**

Học viên cần làm quen với tư duy lập trình hệ thống, hiểu cách Go tối ưu hóa bộ nhớ tĩnh:

1. [**Syntax & Variables**](./go-basics-guide.html#s-syntax) - Khai báo biến, các kiểu dữ liệu cơ bản, kiểu tĩnh tĩnh học và hành vi mặc định của Zero Values.
2. [**Control Flow & Loops**](./go-basics-guide.html#s-control) - Tại sao Go chỉ có duy nhất từ khóa `for` để lặp và cách dùng `switch` không cần `break`.
3. [**Defer, Panic, Recover**](./go-basics-guide.html#s-defer) - Quản lý giải phóng tài nguyên ngược LIFO và xử lý phục hồi lỗi nghiêm trọng trong runtime.
4. [**Pointers & Memory**](./go-basics-guide.html#s-pointers) - Bản chất truyền giá trị (Value Semantics), sử dụng con trỏ (Pointer Semantics) và cơ chế Escape Analysis.
5. [**Errors — Wrapping & Custom**](./go-basics-guide.html#s-errors) - Tư duy xử lý lỗi tường minh thông qua interface `error` thay vì khối `try-catch`.
6. [**Slices & Maps**](./go-basics-guide.html#s-slices) - Cơ chế hoạt động của Slices (trỏ vào mảng tĩnh bên dưới) và các thao tác map cơ bản.

🔥 **So sánh nhanh**: Slices trong Go truyền tham chiếu đến mảng cơ sở nhưng bản thân struct header của Slice được sao chép theo giá trị (Value Copy).

---

#### **LEVEL 2: Functions, Standard Packages & Multi-Errors (Modules 7-12)**

Làm chủ các thư viện tiêu chuẩn thông dụng nhất của Go để thao tác dữ liệu:

7. [**Closures & Methods**](./go-basics-guide.html#s-closures) - Thiết kế hàm bậc cao (First-class functions), hàm bao đóng closure và bộ nhận phương thức `Value/Pointer Receivers`.
8. [**Package strings**](./go-basics-guide.html#s-strings) - Xử lý chuỗi UTF-8 bất biến và tối ưu hóa cấp phát chuỗi với `strings.Builder`.
9. [**Package strconv**](./go-basics-guide.html#s-strconv) - Chuyển đổi qua lại giữa kiểu chuỗi văn bản và các kiểu dữ liệu nguyên thủy một cách an toàn.
10. [**Package fmt**](./go-basics-guide.html#s-fmt) - Định dạng chuỗi nâng cao, in vết dữ liệu và interface `Stringer`.
11. [**Package math**](./go-basics-guide.html#s-math) - Xử lý số học chính xác, hàm lượng giác, sinh số ngẫu nhiên an toàn và xử lý số cực lớn `big.Int`.
12. [**Sentinel, Wrapping & Join**](./go-basics-guide.html#s-sentinel) - Định nghĩa sentinel errors, bọc chuỗi lỗi tĩnh `%w`, và kỹ thuật gộp đa lỗi `errors.Join` từ Go 1.20+.

---

#### **LEVEL 3: Advanced Data & Pipeline Control (Advanced Guide — Modules 1-6)**

Chuyển đổi tư duy lập trình từ JS/TS sang các mô hình nâng cao tối ưu hiệu năng của Go:

13. [**Data Conversion**](./go-advanced-guide.html#s-dataconv) - Ép kiểu an toàn, chuyển đổi JSON/encoding, cấu trúc generic converters và xử lý coerce types.
14. [**Array Pipeline**](./go-advanced-guide.html#s-arrpipeline) - Thiết kế pipeline xử lý mảng kiểu functional (Map/Filter/Reduce), lazy evaluation và tối ưu hóa luồng qua channels.
15. [**Object Map Utils**](./go-advanced-guide.html#s-maputils) - Các hàm tiện ích: Deep merge, object diff, deep cloning, map flattening và truy cập động qua struct path.
16. [**Promise / Async**](./go-advanced-guide.html#s-async) - Mô phỏng cơ chế Future/Promise, quản lý tập tác vụ song song thông qua `errgroup` kết hợp timeout & retry.
17. [**Date & Time**](./go-advanced-guide.html#s-datetime) - Làm chủ múi giờ (timezone), các bài toán số học lịch biểu phức tạp, parsing và formatting thông qua hằng số layout đặc biệt của Go.
18. [**Enum & Union Types**](./go-advanced-guide.html#s-enums) - Triển khai hằng số tự tăng `iota`, thiết kế kiểu Enum kiểu an toàn (Sealed Interfaces) và mô hình hóa Union Types.

---

#### **LEVEL 4: Advanced Patterns & Idioms (Advanced Guide — Modules 7-12)**

Nâng tầm lập trình lên cấp độ kiến trúc sư phần mềm chuyên nghiệp bằng Go:

19. [**Error Handling (Advanced)**](./go-advanced-guide.html#s-errhandling) - Cấu trúc lỗi phân lớp, lưu trữ vết lời gọi (Stack Trace), phục hồi panic cấp middleware và triển khai `Result Monad` kiểu functional.
20. [**Regex & Templates**](./go-advanced-guide.html#s-regex) - Sử dụng biểu thức chính quy tối ưu (compile-once) và cơ chế sinh mã HTML/Text an toàn qua template engines.
21. [**Set & Concurrent Map**](./go-advanced-guide.html#s-concurrentmap) - Triển khai cấu trúc Set generic, sử dụng `sync.Map` và thiết kế Sharded Map hiệu năng cực cao tránh lock contention.
22. [**Iterator (Go 1.23+)**](./go-advanced-guide.html#s-iterators) - Làm chủ tính năng lặp `range-over-func` thế hệ mới, viết hàm lặp tùy chỉnh và xây dựng luồng Sequence lười biếng (Lazy Sequences).
23. [**Optional / Nullable**](./go-advanced-guide.html#s-optional) - Triển khai `Option[T]` generic triệt tiêu hoàn toàn lỗi `nil pointer dereference`, giải tuần tự JSON nullable và xử lý trường Null của Database.
24. [**Class & Struct Patterns**](./go-advanced-guide.html#s-oop) - Tư duy hướng đối tượng không cần Class: Encapsulation, Struct Embedding (thay thế kế thừa), đa hình qua Interfaces, các mẫu thiết kế Builder và Decorator thực tiễn.

---

#### **LEVEL 5: Go Optimization &amp; Runtime (Optimization Guide — Modules 1-9)**

Chinh phục đỉnh cao hiệu năng, làm chủ hoàn toàn runtime và cơ chế tối ưu hóa hệ thống của Go:

25. [**Tri-color Garbage Collector**](./go-optimization-guide.html#s-gc-concept) - Bản chất cơ chế GC Concurrent Tri-color Mark-Sweep, Dijkstra write barriers, GOGC và GOMEMLIMIT.
26. [**Go Runtime Scheduler**](./go-optimization-guide.html#s-sched-concept) - Kiến trúc M:N Scheduler (GMP model), cơ chế Work Stealing và Cooperative / Non-cooperative Preemption.
27. [**Go Memory Model**](./go-optimization-guide.html#s-mem-concept) - Hiểu rõ Happens-before guarantees để thiết kế mã nguồn đồng thời chính xác không bị data races.
28. [**Go 1.24 Runtime Enhancements**](./go-optimization-guide.html#s-go124) - generic type aliases, weak pointers, runtime.AddCleanup và cải tiến map.
29. [**pprof Profiling**](./go-optimization-guide.html#s-pprof-intro) - Đo đạc chuyên sâu CPU, Heap, Goroutines, Mutex và Block profiles xác định điểm nghẽn hiệu năng.
30. [**Iterator &amp; Generator Patterns**](./go-optimization-guide.html#s-gen-concept) - Xây dựng lazy collection generators hiệu năng cực cao bằng `iter.Seq` range-over-func.
31. [**Execution Tracer**](./go-optimization-guide.html#s-trace-concept) - Sử dụng `go tool trace` phân tích microsecond timeline của goroutines, scheduler latency và GC.
32. [**Benchmark &amp; Benchstat**](./go-optimization-guide.html#s-bench-concept) - Viết benchmarks chuẩn xác, tránh loop optimization, và dùng thống kê `benchstat` so sánh hiệu năng.
33. [**Goroutine Leak Detection**](./go-optimization-guide.html#s-leak-concept) - Nhận diện các leaks phổ biến (blocked channels, slow timer) và phát hiện bằng thư viện `goleak` của Uber.

---

### 💡 So Sánh Cú Pháp Nền Tảng (JS/TS vs Go)

| JS / TS | Go Equivalent | Giải thích kỹ thuật |
| :--- | :--- | :--- |
| `let x = 10;` | `x := 10` | Cú pháp khai báo nhanh, Go tự suy luận kiểu dữ liệu động tại thời điểm biên dịch. |
| `try { ... } catch (e) { ... }` | `val, err := action()` | Go xử lý lỗi như một giá trị trả về thông thường (explicit error propagation). |
| `class User { ... }` | `type User struct { ... }` | Sử dụng cấu trúc dữ liệu thuần túy (struct) thay vì mô hình hướng đối tượng class-based. |
| `const x = ...` | `const x = ...` | Hằng số trong Go chỉ chấp nhận các giá trị nguyên thủy tính toán được tại compile time. |
| `interface User { ... }` | `type User interface { ... }` | Interface trong Go được thỏa mãn một cách ngầm định (Implicit Interfaces / Duck Typing). |
| `JSON.stringify(obj)` | `json.Marshal(obj)` | Sử dụng thẻ gán `json:"field_name"` trên struct để điều khiển quá trình chuyển đổi. |

---

### 🚀 Gợi Ý Học Tập Bản Đồ Go Fundamental

1. **Tuần 1 (Cơ bản tinh gọn)**: Nắm chắc Syntax, Pointers và cách vận hành mảng động Slices trong [Go Basics Guide](./go-basics-guide.html).
2. **Tuần 2 (Xử lý chuỗi & Lỗi)**: Nâng cao kỹ năng thao tác thư viện `strings`, `strconv` và thực hành bọc lỗi / gộp đa lỗi an toàn.
3. **Tuần 3 (Chuyển đổi dữ liệu nâng cao)**: Chuyển dịch từ JS sang Go các cấu trúc Map/Filter/Reduce thông qua [Go Advanced Guide](./go-advanced-guide.html).
4. **Tuần 4 (Idiomatic Go)**: Thực hành lập trình không lớp học (OOP via Embedding &amp; Interfaces), cài đặt Iterator của Go 1.23+ và áp dụng `Option[T]` để triệt tiêu bug runtime trong [Go Advanced Guide](./go-advanced-guide.html).
5. **Tuần 5 (Tối ưu hóa &amp; Runtime)**: Tiến sâu vào hệ thống nội tại của Go Runtime trong [Go Optimization &amp; Runtime](./go-optimization-guide.html). Nắm vững Tri-color GC, GMP scheduler, đo đạc với `pprof` và `go tool trace`, thống kê đo lường bằng `benchstat`, và chặn rò rỉ goroutine bằng `goleak`.
