# 🗺️ Bản Đồ Hệ Thống Kiến Thức Systems Architecture Suite

Chào mừng bạn đến với bộ tài liệu kỹ thuật chuyên sâu về thiết kế hệ thống, kiến trúc phần mềm, bảo mật, tích hợp dữ liệu và trí tuệ nhân tạo. Bộ tài liệu được thiết kế theo lộ trình nâng dần từ phân tán vĩ mô, mô hình hóa chi tiết, bảo mật Zero-Trust, giao thức truyền thông, tầng lưu trữ nâng cao đến hạ tầng Generative AI.

---

### 🟢 LEVEL 1: System Design & Distributed Patterns ([System Design Guide](./system-design-guide.html))

Làm chủ các mẫu thiết kế và giải pháp phân tán quan trọng nhất để xây dựng hệ thống quy mô lớn (High Availability, Scalability, Fault Tolerance):

1. [**Idempotency**](./system-design-guide.html#s-idempotency) - Cơ chế lũy đẳng bảo vệ hệ thống thanh toán và xử lý API khỏi các lỗi trùng lặp (double-charge) khi client retry.
2. [**Eventual Consistency**](./system-design-guide.html#s-eventual) - Mô hình nhất quán cuối cùng trong kiến trúc phân tán lớn, sự đánh đổi hiệu năng (stale data) để lấy tốc độ và tính sẵn sàng cao.
3. [**CAP Theorem**](./system-design-guide.html#s-cap) - Định lý CAP cốt lõi: Chọn 2 trong 3 yếu tố giữa Consistency, Availability và Partition Tolerance.
4. [**Saga Pattern**](./system-design-guide.html#s-saga) - Quản lý các giao dịch phân tán (Distributed Transactions) trên môi trường Microservices thông qua chuỗi hành động bù đắp (Compensating Actions).
5. [**CQRS & Event Sourcing**](./system-design-guide.html#s-cqrs) - Tách biệt tuyệt đối luồng ghi và đọc dữ liệu, kết hợp lưu trữ lịch sử trạng thái dưới dạng chuỗi sự kiện bất biến (Event Store).
6. [**Transactional Outbox**](./system-design-guide.html#s-outbox) - Giải pháp gửi Event/Message an toàn ra Message Broker (Kafka/RabbitMQ) mà không sợ lỗi ghi Database thành công nhưng báo thất bại.
7. [**Circuit Breaker & Bulkhead**](./system-design-guide.html#s-circuitbreaker) - Cơ chế ngắt mạch tự động chống sập lan chuyền (cascading failures) và cô lập tài nguyên cho từng luồng nghiệp vụ.
8. [**Sidecar & Service Mesh**](./system-design-guide.html#s-servicemesh) - Tách biệt hoàn toàn cross-cutting concerns (mTLS, tracing, routing) ra khỏi mã nguồn nghiệp vụ thông qua proxy phụ trợ.
9. [**Database Sharding & BFF**](./system-design-guide.html#s-apigateway) - Phân mảnh cơ sở dữ liệu theo chiều ngang để scale vô hạn và thiết kế tầng trung chuyển tối ưu hóa riêng cho từng nền tảng frontend.

---

### 🟡 LEVEL 2: Architecture Design & Modeling Principles ([Architecture Design Guide](./architecture-design-guide.html))

Phương pháp luận chuẩn hóa tài liệu, thiết kế sơ đồ hệ thống và phân rã nghiệp vụ phần mềm chuyên nghiệp:

10. [**ADR (Architecture Decision Record)**](./architecture-design-guide.html#s-adr) - Ghi chép và lưu trữ các quyết định kiến trúc cốt lõi dưới dạng lịch sử bất biến giúp tracking rationale của hệ thống.
11. [**DDD (Domain-Driven Design)**](./architecture-design-guide.html#s-ddd) - Chiến lược thiết kế hướng tên miền: Tách biệt Bounded Context, Aggregate Roots, Entities và Value Objects.
12. [**ERD (Entity-Relationship Diagram)**](./architecture-design-guide.html#s-erd) - Thiết kế sơ đồ quan hệ thực thể cơ sở dữ liệu, tối ưu khóa ngoại và chuẩn hóa bảng dữ liệu.
13. [**HLD & LLD**](./architecture-design-guide.html#s-hld) - Phân biệt Thiết kế mức cao (High-Level - topology, components) và Thiết kế mức thấp (Low-Level - class diagrams, code-level patterns).
14. [**UML Modeling**](./architecture-design-guide.html#s-uml) - Sử dụng Sequence, Component, Class, và Activity diagrams để trực quan hóa luồng xử lý và tương tác giữa các services.

---

### 🟠 LEVEL 3: Security Architecture & Infrastructure Protection ([Security Guide](./security-architecture-guide.html))

Kiến thức nền tảng bắt buộc để bảo vệ hệ thống doanh nghiệp, quản lý danh tính và bảo mật kênh truyền:

15. [**mTLS (Mutual TLS)**](./security-architecture-guide.html#s-mtls-concept) - Xác thực hai chiều giữa các máy chủ (Service-to-Service Authentication) loại bỏ hoàn toàn rủi ro giả mạo.
16. [**Zero Trust Architecture**](./security-architecture-guide.html#s-zt-concept) - Nguyên tắc an ninh mạng hiện đại: "Không bao giờ tin tưởng, luôn luôn xác thực", kiểm tra liên tục mọi truy cập ở mọi vị trí địa lý.
17. [**RBAC & ABAC Access Control**](./security-architecture-guide.html#s-rbac-concept) - Thiết kế hệ thống phân quyền dựa trên vai trò (Role-Based) và thuộc tính động môi trường (Attribute-Based).
18. [**OAuth2 & OIDC Identity**](./security-architecture-guide.html#s-oauth-concept) - Làm chủ quy trình ủy quyền (Authorization) và xác thực danh tính (Authentication) chuẩn thế giới cho API & Web Apps.
19. [**JWT Best Practices**](./security-architecture-guide.html#s-jwt-concept) - Sử dụng và quản lý JSON Web Tokens an toàn, hạn chế tối đa rủi ro lộ khóa ký hay tấn công replay attack.
20. [**Secrets Manager & Vault**](./security-architecture-guide.html#s-secret-concept) - Quản lý an toàn khóa cấu hình, database credentials, xoay vòng tự động API keys tránh mã hóa cứng trong code.
21. [**CORS & Secure Headers**](./security-architecture-guide.html#s-cors-concept) - Cấu hình Cross-Origin Resource Sharing an toàn, chặn đứng tấn công CSRF, XSS và clickjacking bằng security headers.

---

### 🔵 LEVEL 4: API Architecture & Integration Patterns ([API Patterns Guide](./api-patterns-guide.html))

Thiết kế giao thức truyền thông, tích hợp hệ thống, và các giao tiếp real-time/streaming hiện đại:

22. [**REST API**](./api-patterns-guide.html#s-rest) - Xây dựng API chuẩn RESTful, quản lý tài nguyên đồng nhất, HTTP Verbs, Caching, và Statelessness.
23. [**GraphQL**](./api-patterns-guide.html#s-graphql) - Giải quyết over-fetching/under-fetching, query linh hoạt từ client side, schema stitching và cơ chế tối ưu DataLoader.
24. [**gRPC**](./api-patterns-guide.html#s-grpc) - Kết nối Microservices hiệu năng siêu cao dựa trên HTTP/2, Protocol Buffers binary serialization và các luồng streaming dữ liệu.
25. [**Webhook**](./api-patterns-guide.html#s-webhook) - Tích hợp bất đồng bộ hướng sự kiện (Event-Driven Integration), cơ chế retry exponential backoff và bảo mật bằng chữ ký số.
26. [**Polling & Long Polling**](./api-patterns-guide.html#s-polling) - Giao tiếp near-realtime truyền thống, tối ưu hóa adapter polling và giữ kết nối server-side khi không có dữ liệu mới.
27. [**SSE (Server-Sent Events)**](./api-patterns-guide.html#s-sse) - Truyền dữ liệu một chiều từ Server đến Client liên tục (real-time streaming) như token AI, live ticker qua giao thức HTTP chuẩn.
28. [**OpenAPI / Swagger**](./api-patterns-guide.html#s-openapi) - Chuẩn hóa đặc tả API (Design-First approach), tự động tạo tài liệu tương tác, mock servers và code-generation SDKs.
29. [**API Versioning**](./api-patterns-guide.html#s-versioning) - Quản lý vòng đời API bền vững qua URI paths, Custom Headers, Query parameters và Date-based versioning.

---

### 🟣 LEVEL 5: Database Patterns & Transaction Architecture ([Database Patterns Guide](./database-patterns-guide.html))

Tổ chức dữ liệu, tối ưu hóa giao dịch dữ liệu phân tán, kiểm soát đồng thời và lưu trữ tối ưu:

30. [**ACID Properties**](./database-patterns-guide.html#acid) - Đảm bảo tính nhất quán giao dịch cơ sở dữ liệu nghiêm ngặt trong RDBMS truyền thống với isolation levels chi tiết.
31. [**BASE Model**](./database-patterns-guide.html#base) - Giải pháp nhất quán cuối cùng (Eventual Consistency) cho các NoSQL databases và hệ thống phân tán quy mô toàn cầu.
32. [**Database Sharding**](./database-patterns-guide.html#sharding) - Phân mảnh dữ liệu theo chiều ngang để phân tán tải trọng ghi, phân chia partition keys thông minh.
33. [**Replication Modes**](./database-patterns-guide.html#replication) - Kiến trúc Master-Replica, phân biệt Đồng bộ (Synchronous) và Bất đồng bộ (Asynchronous) trong bảo vệ và phân phối dữ liệu đọc.
34. [**Database Migration**](./database-patterns-guide.html#migration) - Quy trình nâng cấp schema an toàn trong môi trường Production thông qua Zero-Downtime migrations (Expand/Contract pattern).
35. [**Optimistic & Pessimistic Locking**](./database-patterns-guide.html#optimistic) - Các kỹ thuật kiểm soát concurrency, tránh write collisions khi có nhiều clients đồng thời cập nhật dòng dữ liệu.
36. [**Soft Delete & Upsert**](./database-patterns-guide.html#softdelete) - Xóa mềm bảo toàn dữ liệu lịch sử và cơ chế `INSERT ... ON CONFLICT DO UPDATE` nguyên tử.
37. [**OLTP vs OLAP**](./database-patterns-guide.html#oltp-olap) - Phân biệt cơ sở dữ liệu phục vụ giao dịch trực tuyến (Online Transaction Processing) và phân tích tổng hợp dữ liệu lớn (Online Analytical Processing).

---

### 🔴 LEVEL 6: AI & Machine Learning Foundations ([AI Glossary](./AI%20glossary.md))

Các khái niệm nền tảng của kỷ nguyên Trí tuệ Nhân tạo và kỹ thuật hạ tầng lưu trữ hỗ trợ Mô hình Ngôn ngữ Lớn (LLM):

38. [**AI & Machine Learning Core**](./AI%20glossary.md#ai-foundations) - Học máy có giám sát (Supervised), không giám sát (Unsupervised), Mạng nơ-ron (Neural Networks) và Học sâu (Deep Learning).
39. [**Transformer Architecture**](./AI%20glossary.md#transformer) - Kiến trúc Transformer đột phá, cơ chế tự chú ý (Self-Attention) nền tảng của xử lý ngôn ngữ tự nhiên hiện đại.
40. [**LLMs & Generative AI**](./AI%20glossary.md#llms) - LLMs hiện đại (GPT, Claude, Gemini), kỹ thuật Pre-training, SFT (Supervised Fine-Tuning), RLHF và RAG (Retrieval-Augmented Generation).
41. [**Vector Databases & Embeddings**](./AI%20glossary.md#vectors) - Kỹ thuật nhúng vector ngữ nghĩa đa chiều và lưu trữ trên các DB chuyên dụng (Pinecone, pgvector, Milvus) để tìm kiếm khoảng cách ngữ nghĩa.

---

### 💡 So Sánh Mô Hệ Thống (Truyền Thống vs Phân Tán Hiện Đại)

| Khái niệm truyền thống | Mô hình phân tán / Hiện đại | Giải thích bản chất lựa chọn |
| :--- | :--- | :--- |
| **Bảo mật tường lửa (Perimeter)** | **Zero Trust / mTLS** | Tường lửa không còn đủ. Mọi request bất kể trong/ngoài mạng nội bộ đều bắt buộc phải được mã hóa và xác thực độc lập. |
| **Database phân tán (Synchronous)** | **Eventual Consistency / Saga** | Không thể đồng bộ tức thời trên hệ thống lớn vì độ trễ mạng. Chấp nhận độ trễ dữ liệu ngắn và tự động rollback bằng Saga bù đắp. |
| **API REST/JSON Đơn Lẻ** | **GraphQL / gRPC / SSE** | Tối ưu hóa tối đa payload theo kênh: GraphQL cho client linh hoạt, gRPC cho microservices hiệu năng cao, SSE cho streaming AI tokens. |
| **Hardcoded Secrets** | **Secrets Manager (Vault / KMS)** | Tránh lưu trữ API keys trong file code (`.env`). Nạp động từ các hệ thống quản lý khóa trung tâm có cơ chế rotate tự động. |

---

### 🚀 Gợi Ý Học Tập Toàn Bộ Bản Đồ Glossary

1. **Giai đoạn 1 (Thiết kế vĩ mô & Mô hình hóa)**: Nghiên cứu [System Design Guide](./system-design-guide.html) và [Architecture Design Guide](./architecture-design-guide.html) để rèn luyện tư duy phân rã bài toán lớn và vẽ sơ đồ chuẩn hóa.
2. **Giai đoạn 2 (Giao tiếp & Bảo mật)**: Chinh phục [API Patterns Guide](./api-patterns-guide.html) and [Security Guide](./security-architecture-guide.html) để biết cách thiết kế API bảo mật cao và mượt mà.
3. **Giai đoạn 3 (Tối ưu hóa dữ liệu & AI)**: Đi sâu vào [Database Patterns Guide](./database-patterns-guide.html) để xử lý dữ liệu tin cậy và nghiên cứu [AI Glossary](./AI%20glossary.md) chuẩn bị cho hạ tầng công nghệ tương lai.
