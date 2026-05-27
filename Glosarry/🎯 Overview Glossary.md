#### **LEVEL 1: System Design & Distributed Patterns (System Design Guide)**

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

#### **LEVEL 2: Security Architecture & Infrastructure Protection (Security Guide)**

Kiến thức nền tảng bắt buộc để bảo vệ hệ thống doanh nghiệp, quản lý danh tính và bảo mật kênh truyền:

10. [**mTLS (Mutual TLS)**](./security-architecture-guide.html#s-mtls-concept) - Xác thực hai chiều giữa các máy chủ (Service-to-Service Authentication) loại bỏ hoàn toàn rủi ro giả mạo.
11. [**Zero Trust Architecture**](./security-architecture-guide.html#s-zt-concept) - Nguyên tắc an ninh mạng hiện đại: "Không bao giờ tin tưởng, luôn luôn xác thực", kiểm tra liên tục mọi truy cập ở mọi vị trí địa lý.
12. [**RBAC & ABAC Access Control**](./security-architecture-guide.html#s-rbac-concept) - Thiết kế hệ thống phân quyền dựa trên vai trò (Role-Based) và thuộc tính động môi trường (Attribute-Based).
13. [**OAuth2 & OIDC Identity**](./security-architecture-guide.html#s-oauth-concept) - Làm chủ quy trình ủy quyền (Authorization) và xác thực danh tính (Authentication) chuẩn thế giới cho API & Web Apps.
14. [**JWT Best Practices**](./security-architecture-guide.html#s-jwt-concept) - Sử dụng và quản lý JSON Web Tokens an toàn, hạn chế tối đa rủi ro lộ khóa ký hay tấn công replay attack.
15. [**Secrets Manager & Vault**](./security-architecture-guide.html#s-secret-concept) - Quản lý an toàn khóa cấu hình, database credentials, xoay vòng tự động API keys tránh mã hóa cứng trong code.
16. [**CORS & Secure Headers**](./security-architecture-guide.html#s-cors-concept) - Cấu hình Cross-Origin Resource Sharing an toàn, chặn đứng tấn công CSRF, XSS và clickjacking bằng security headers.

---

#### **LEVEL 3: AI & Machine Learning Glossary (AI Glossary)**

Thuật ngữ và nền tảng của kỷ nguyên Trí tuệ Nhân tạo cùng Mô hình ngôn ngữ lớn (LLM):

17. [**AI & Machine Learning Core**](./AI%20glossary.md#ai-foundations) - Khái quát về Học máy có giám sát (Supervised), không giám sát (Unsupervised), Mạng nơ-ron (Neural Networks) và Học sâu (Deep Learning).
18. [**Transformer Architecture**](./AI%20glossary.md#transformer) - Tìm hiểu kiến trúc Transformer đột phá, cơ chế tự chú ý (Self-Attention) làm thay đổi hoàn toàn xử lý ngôn ngữ tự nhiên (NLP).
19. [**LLMs & Generative AI**](./AI%20glossary.md#llms) - Cách vận hành của các mô hình ngôn ngữ lớn (GPT-4, Claude, Gemini), quy trình Pre-training, Fine-tuning và kỹ thuật RAG (Retrieval-Augmented Generation).
20. [**Vector Databases & Embeddings**](./AI%20glossary.md#vectors) - Cơ chế biến đổi văn bản thành không gian vector đa chiều (Embeddings) để tìm kiếm ngữ nghĩa siêu tốc trên các cơ sở dữ liệu Vector chuyên dụng.

---

### 💡 So Sánh Mô Hình Bảo Mật & Hệ Thống (Truyền Thống vs Hiện Đại)

| Khái niệm cũ | Mô hình bảo mật / Hệ thống mới | Giải thích bản chất |
| :--- | :--- | :--- |
| **Bảo mật tường lửa (Perimeter Security)** | **Zero Trust / mTLS** | Tường lửa không còn an toàn. Mọi request dù ở mạng nội bộ hay ngoài internet đều bắt buộc phải mã hóa và xác thực độc lập. |
| **Database phân tán (Synchronous)** | **Eventual Consistency / Saga** | Không thể đồng bộ tức thời trên hệ thống lớn vì nghẽn mạng. Phải chấp nhận độ trễ dữ liệu và tự động rollback bằng transaction bù đắp. |
| **Monolithic Gateway** | **BFF (Backend For Frontend)** | API Gateway duy nhất cho mọi thiết bị sẽ bị phình to. Tách riêng gateway cho Web, Mobile để phục vụ payload tối ưu nhất. |
| **Hardcoded Secrets** | **Secrets Manager (Vault / KMS)** | Không bao giờ lưu trữ mật khẩu hay API key trong mã nguồn (`.env`). Nạp tự động từ dịch vụ quản lý khóa và xoay vòng định kỳ. |

---

### 🚀 Gợi Ý Học Tập Bản Đồ Glossary

1. **Tuần 1-2**: Chinh phục [System Design Guide](./system-design-guide.html). Tập trung sâu vào các khái niệm lũy đẳng (Idempotency), Saga và CQRS vì đây là các câu hỏi phỏng vấn System Design kinh điển nhất.
2. **Tuần 3**: Đi sâu vào [Security Architecture Guide](./security-architecture-guide.html). Thực hành cấu hình OAuth2 Flow, nắm rõ cơ chế mTLS và Zero Trust để có tư duy DevSecOps chuyên nghiệp.
3. **Tuần 4**: Nghiên cứu [AI Glossary](./AI%20glossary.md) để cập nhật nhanh toàn bộ thuật ngữ công nghệ AI thời đại mới, hiểu cách hoạt động thực sự của LLMs dưới góc độ kỹ thuật.
