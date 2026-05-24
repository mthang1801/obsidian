
#### **LEVEL 1: Structural Patterns — Concepts & Mechanics (1-6)**

Học cách ghép nối các struct, interface để tạo cấu trúc phần mềm linh hoạt, tách biệt trừu tượng khỏi cài đặt cụ thể:

1. [**Adapter Pattern**](./structural-design-patterns.html#s-adapter-concept) - Tương thích hóa các interface khác biệt thông qua struct wrapping (như bộ chuyển đổi socket).
2. [**Decorator Pattern**](./structural-design-patterns.html#s-decorator-concept) - Gắn thêm hành vi động vào đối tượng gốc đệ quy qua wrapping chain (nền tảng của Middleware).
3. [**Proxy Pattern**](./structural-design-patterns.html#s-proxy-concept) - Ủy nhiệm kiểm soát truy cập (Lazy Initialization, Virtual, Security Caching) bằng lớp gác cổng trung gian.
4. [**Facade Pattern**](./structural-design-patterns.html#s-facade-concept) - Gom nhóm và tinh giản giao diện gọi của hệ thống con phức tạp thông qua một cổng interface duy nhất.
5. [**Composite Pattern**](./structural-design-patterns.html#s-composite-concept) - Khớp nối các đối tượng dạng cây phân cấp (Tree structure), xử lý đồng nhất lá và nhánh.
6. [**Bridge Pattern**](./structural-design-patterns.html#s-bridge-concept) - Phân tách tính trừu tượng (Abstraction) và phần triển khai (Implementation) để chúng phát triển độc lập.

🔥 **So sánh nhanh**: OOP truyền thống dùng kế thừa class khắt khe (Inheritance), còn Go ưu tiên hoàn toàn **Composition over Inheritance** qua Interface và Struct Embedding.

---

#### **LEVEL 2: Behavioral Patterns — Core Logic Flows (7-11)**

Tập trung vào cơ chế giao tiếp, trao đổi dữ liệu, và phân phối trách nhiệm giữa các đối tượng:

7. [**Strategy Pattern**](./behavioral-patterns.html#s-strategy) - Định nghĩa tập hợp thuật toán độc lập và hoán đổi linh hoạt khi chạy thông qua Interface.
8. [**Observer Pattern**](./behavioral-patterns.html#s-observer) - Đăng ký-lắng nghe (Pub/Sub) một nguồn phát dữ liệu, tự động thông báo cập nhật cho danh sách Subscribers.
9. [**Command Pattern**](./behavioral-patterns.html#s-command) - Đóng gói yêu cầu xử lý thành một object riêng biệt (Request-as-an-Object) hỗ trợ undo/redo và hàng đợi.
10. [**Template Method**](./behavioral-patterns.html#s-template) - Định nghĩa bộ khung thuật toán, cho phép struct con ghi đè một số bước cụ thể qua composition.
11. [**State Pattern**](./behavioral-patterns.html#s-state) - Cho phép đối tượng thay đổi hành vi động khi trạng thái nội bộ của nó thay đổi (State Machine).

---

#### **LEVEL 3: Advanced Behavioral & Structural Decoupling (12-16)**

Tách rời logic điều phối, lặp dữ liệu, và quản lý liên kết phức tạp:

12. [**Iterator Pattern**](./behavioral-patterns.html#s-iterator) - Duyệt qua các phần tử của tập hợp mà không để lộ cấu trúc dữ liệu bên dưới (Go 1.26+ đã chuẩn hóa `iter.Seq`).
13. [**Chain of Responsibility**](./behavioral-patterns.html#s-chain) - Chuyển tiếp yêu cầu qua một chuỗi các đối tượng xử lý (Handlers) cho đến khi được giải quyết.
14. [**Mediator Pattern**](./behavioral-patterns.html#s-mediator) - Giảm liên kết trực tiếp giữa các đối tượng bằng cách ép chúng giao tiếp gián tiếp qua một đầu mối trung gian.
15. [**Memento Pattern**](./behavioral-patterns.html#s-memento) - Lưu trữ và khôi phục trạng thái bên trong của đối tượng mà không vi phạm nguyên tắc bao đóng (Capsule).
16. [**Visitor Pattern**](./behavioral-patterns.html#s-visitor) - Tách biệt thuật toán hoặc logic xử lý ra khỏi cấu trúc đối tượng chứa nó, dễ dàng thêm tính năng mới mà không sửa struct cũ.

---

### 💡 Best Practices Từ Background NestJS & Node.js Của Bạn

Trong NestJS/Node.js, OOP dựa trên nền tảng Class-based rất mạnh kết hợp cùng Dependency Injection (DI) Engine tích hợp. Khi chuyển dịch tư duy sang **Go idiomatic**, hãy chú ý các ánh xạ sau:

#### So Sánh Khái Niệm Thiết Kế:

| NestJS / TypeScript | Go Idiomatic Equivalent | Cách hoạt động / Giải thích kỹ thuật |
| :--- | :--- | :--- |
| **NestJS Interceptors & Middlewares** | Decorator Pattern | Go tận dụng interface wrapping đệ quy hoặc wrap `http.Handler` để xây dựng middleware chain cực kỳ trực quan mà không cần decorators dạng metadata `@`. |
| **NestJS Services DI Container** | Composition & Constructor Injection | Go không dùng DI container nặng nề lúc runtime (như Reflect-Metadata). Thay vào đó, inject thủ công struct cụ thể hoặc interface qua factory function (ví dụ: `NewUserService(repo UserRepository)`). |
| **TypeScript Abstract Class** | Interface & Struct Embedding | Go không có lớp trừu tượng. Thay vào đó, định nghĩa một Interface mỏng và nhúng (`embedding`) một struct chứa logic dùng chung vào struct con để tái sử dụng mã. |
| **RxJS Observables / EventEmitters** | Observer / Go Channels | Sử dụng các kênh truyền dữ liệu `channels` kết hợp cùng `goroutines` để phát và lắng nghe sự kiện đồng thời một cách type-safe mà không cần thư viện bên thứ ba. |
| **NestJS Guards & Passport Strategy** | Chain of Responsibility / Strategy | Tổ chức thành các middleware kiểm tra quyền hạn độc lập liên tiếp, hoặc hoán đổi Auth Strategy ở Runtime thông qua một Interface duy nhất. |

#### Nguyên Tắc Thiết Kế Vàng Trong Go (Go Design Idioms):

1. **"Accept Interfaces, Return Structs"**: Đây là tôn chỉ thiết kế hệ thống trong Go. Hàm nhận vào nên nhận interface để tăng khả năng mock/test, nhưng hàm trả về nên trả về cụ thể struct để tránh các chi phí cấp phát vùng nhớ không đáng có trên Heap.
2. **Interface mỏng (Small Interfaces)**: Khác với các interface cồng kềnh trong Java/TS, interface trong Go thường cực kỳ mỏng — chỉ gồm 1 đến 2 phương thức (như `io.Reader`, `io.Writer`). Sự kết hợp các interface mỏng tạo ra các hệ thống cực kỳ linh hoạt và dễ mở rộng.
3. **Implicit Interfaces**: Struct trong Go không cần khai báo từ khóa `implements`. Chỉ cần struct cài đặt đầy đủ các phương thức của Interface là trình biên dịch tự động nhận diện. Điều này giúp bạn dễ dàng viết các Adapter để tích hợp các thư viện bên thứ ba mà không cần chạm vào mã nguồn gốc của họ.
4. **Không lạm dụng Patterns**: Triết lý tối thượng của Go là **Sự đơn giản (Simplicity)**. Hãy chỉ áp dụng Design Pattern khi mã nguồn của bạn thực sự đòi hỏi độ linh hoạt đó (loose coupling, viết unit tests). Đừng áp dụng chỉ vì hệ thống trông có vẻ "thiết kế bài bản".

---

### 🚀 Gợi Ý Học Tập & Thực Hành

1. **Tuần 1-2**: Structural Patterns (1-6) - Tập trung hiểu cơ chế nhúng (embedding) struct, cách xây dựng các Middleware bằng Decorator, và cách gom nhóm subsystem bằng Facade.
2. **Tuần 3**: Core Behavioral (7-11) - Áp dụng Strategy để đổi phương thức thanh toán, xây dựng luồng State Machine cho trạng thái đơn hàng (Order Lifecycle).
3. **Tuần 4**: Advanced Control (12-16) - Cài đặt Chain of Responsibility cho hệ thống validation đầu vào, viết Iterator tùy chỉnh sử dụng tính năng `iter.Seq` của Go 1.26+.
4. **Tích hợp thực tế**: Thử refactor một dịch vụ nhỏ từ dự án NestJS hiện tại của bạn sang dịch vụ Go sử dụng kiến trúc Clean Architecture kết hợp cùng Dependency Injection thủ công.
