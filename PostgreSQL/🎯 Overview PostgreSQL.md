#### **LEVEL 1: Procedural Logic & Correlated Queries (PL/pgSQL & CTEs)**

Xây dựng tư duy xử lý logic nghiệp vụ hiệu quả ngay trong cơ sở dữ liệu và truy vấn phân cấp phức tạp:

1. [**PL/pgSQL Block & Architecture**](plpgsql-cte-mvcc.html#s-pl-intro) - Tìm hiểu cấu trúc khối PL/pgSQL, cơ chế biên dịch và tối ưu hóa thực thi của PostgreSQL.
2. [**Stored Functions & Procedures**](plpgsql-cte-mvcc.html#s-pl-basics) - Phân biệt Function (chạy trong transaction) vs Procedure (quản lý transaction độc lập với `COMMIT/ROLLBACK`).
3. [**Dynamic SQL & Cursors**](plpgsql-cte-mvcc.html#s-pl-control) - Thực thi SQL động an toàn chống SQL Injection qua `EXECUTE ... USING`, và quản lý tập dữ liệu lớn thông qua Cursors.
4. [**Recursive CTE (Truy vấn đệ quy)**](plpgsql-cte-mvcc.html#s-cte-recursive) - Chinh phục cấu trúc dữ liệu dạng cây/đồ thị, bài toán phân cấp nhân sự, và cấu trúc định giá sản phẩm (BOM).
5. [**LATERAL Join (Correlated Subquery)**](plpgsql-cte-mvcc.html#s-lateral-intro) - Kỹ thuật tối ưu hóa truy vấn Top-N per group, duyệt qua các dòng của bảng cha như vòng lặp `foreach`.

---

#### **LEVEL 2: Core Storage Internals & Data Security (MVCC & RLS)**

Hiểu sâu về cấu trúc lưu trữ vật lý của PostgreSQL, cơ chế đồng thời, và bảo mật dữ liệu cấp dòng:

6. [**MVCC Internals (xmin/xmax & Tuple Headers)**](plpgsql-cte-mvcc.html#s-mvcc-internals) - Cơ chế đa phiên bản đồng thời, cách PostgreSQL ẩn/hiện dữ liệu qua transaction state mà không cần khóa bảng (Read Committed vs Serializable).
7. [**Row-Level Security (RLS) & Multi-Tenant**](plpgsql-cte-mvcc.html#s-rls-intro) - Xây dựng kiến trúc bảo mật đa người thuê (Multi-tenant SaaS) cấp cơ sở dữ liệu bằng các chính sách RLS lọc dòng tự động.
8. [**VACUUM, Autovacuum & Bloat Management**](plpgsql-cte-mvcc.html#s-vacuum) - Cơ chế dọn dẹp các phiên bản dòng đã chết (Dead Tuples), ngăn ngừa tình trạng cạn kiệt Transaction ID (XID wraparound), và tối ưu hóa Autovacuum trong môi trường ghi tải cao.

---

#### **LEVEL 3: Indexing Strategies & Partitioning (Performance at Scale)**

Tối ưu hóa khả năng truy cập dữ liệu nhanh chóng và chiến lược quản lý bảng siêu lớn (nhiều tỷ dòng):

9. [**8 Index Types (B-Tree, GIN, BRIN, GiST, SP-GiST, Bloom)**](indexes-partitioning-replication.html#s-idx-types) - Chọn đúng cấu trúc chỉ mục cho từng loại dữ liệu: B-Tree cho sort/range, GIN cho JSONB/Mảng, BRIN cho dữ liệu sắp xếp liên tục (Time-series).
10. [**Partial, Expression & Covering Indexes (INCLUDE)**](indexes-partitioning-replication.html#s-idx-partial) - Thiết kế các index thông minh: chỉ index subset dòng cần thiết (Partial), index kết quả của hàm (Expression), và thực hiện Index-Only Scan không cần truy cập bộ nhớ Heap (Covering).
11. [**Declarative Table Partitioning (RANGE, LIST, HASH)**](indexes-partitioning-replication.html#s-part-intro) - Phân chia các bảng khổng lồ thành nhiều phân vùng vật lý nhỏ hơn để tăng tốc truy vấn và đơn giản hóa việc dọn dẹp dữ liệu lịch sử.
12. [**Partition Pruning & Maintenance (pg_partman)**](indexes-partitioning-replication.html#s-part-expert) - Cơ chế loại bỏ các phân vùng không liên quan trong quá trình lập kế hoạch truy vấn, và tự động hóa vòng đời phân vùng bằng `pg_partman`.

---

#### **LEVEL 4: Modern Semi-Structured & FTS Patterns (JSONB & Search)**

Xây dựng hệ thống linh hoạt lai ghép giữa SQL truyền thống và tài liệu NoSQL hiệu năng cao:

13. [**JSONB Storage, Operators & path queries**](indexes-partitioning-replication.html#s-json-intro) - Biểu diễn tài liệu bán cấu trúc trong PostgreSQL, các toán tử truy vấn nhanh `@>` và `?`, cách Postgres nén và lưu trữ JSONB nhị phân.
14. [**GIN Indexing for JSONB (jsonb_ops vs jsonb_path_ops)**](indexes-partitioning-replication.html#s-json-index) - Tối ưu hóa hiệu suất tìm kiếm tài liệu JSONB, so sánh các chiến lược đánh chỉ mục để tiết kiệm tài nguyên đĩa.
15. [**Full-Text Search (FTS) & Vector Lexemes**](indexes-partitioning-replication.html#s-fts-intro) - Xây dựng công cụ tìm kiếm tiếng Anh/tiếng Việt không dấu thông minh tích hợp sẵn bằng `tsvector`, `tsquery`, và các trọng số xếp hạng kết quả (`ts_rank`).

---

#### **LEVEL 5: Query Optimization, Replication & HA**

Đỉnh cao của quản trị hiệu năng cơ sở dữ liệu và vận hành hệ thống bền bỉ, không có điểm lỗi duy nhất:

16. [**EXPLAIN ANALYZE & Query Planner Cost Model**](optimize-performance.html#s-query) - Cách đọc hiểu bản kế hoạch thực thi truy vấn, so sánh chi phí các giải thuật quét (Seq Scan, Index Scan) và giải thuật khớp nối (Nested Loop, Hash Join, Merge Join).
17. [**Planner Statistics & Extended Statistics**](indexes-partitioning-replication.html#s-qopt-stats) - Cách PostgreSQL thu thập thông tin thống kê qua các biểu đồ phân bố tần suất (Histograms), và giải quyết vấn đề tương quan đa cột bằng Extended Statistics.
18. [**SQL Tuning & Keyset Pagination**](optimize-performance.html#s-pagination) - Kỹ thuật tối ưu hóa SQL, loại bỏ anti-patterns, sử dụng Keyset Pagination (Cursor-based) thay thế cho OFFSET chậm chạp trên tập dữ liệu lớn.
19. [**Streaming Replication & High Availability**](indexes-partitioning-replication.html#s-repl-intro) - Cài đặt cơ chế nhân bản vật lý liên tục (WAL logs streaming), cơ chế chuyển đổi dự phòng (failover) tự động điều phối bởi Patroni/HAProxy.
20. [**Logical Replication & Change Data Capture (CDC)**](indexes-partitioning-replication.html#s-repl-logical) - Nhân bản logic cấp bảng để tích hợp đồng bộ dữ liệu đa hệ thống, tạo luồng sự kiện thời gian thực (CDC) với Debezium.

---

### 💡 Best Practices Từ Background JavaScript / Application Developer Của Bạn

Khi phát triển ứng dụng bằng Node.js (NestJS, Express) kết hợp với các ORM như Prisma, TypeORM hoặc Sequelize, nhà phát triển thường bỏ qua các internals của PostgreSQL. Dưới đây là các ánh xạ tư duy quan trọng để tối ưu hóa hiệu năng hệ thống:

#### So Sánh Tư Duy Ứng Dụng vs Cơ Sở Dữ Liệu:

| Tư duy Application Layer | Tư duy Database Internals (PostgreSQL) | Giải thích kỹ thuật |
| :--- | :--- | :--- |
| **Giao dịch phân tán trong Node.js** | **PL/pgSQL Triggers & Procedures** | Thay vì gọi nhiều truy vấn SQL qua lại giữa API Server và DB (gây trễ mạng - Network Roundtrip), hãy đóng gói logic nghiệp vụ vào PL/pgSQL Procedure để thực thi trực tiếp trên DB trong một Transaction đơn lẻ. |
| **Truy vấn lấy quan hệ lồng nhau (include/relation)** | **LATERAL Joins & CTEs** | ORM thường sinh ra các truy vấn join phức tạp hoặc chạy n+1 query. Việc viết CTE thủ công giúp tối ưu hóa luồng kế hoạch thực thi và giúp Postgres lập chỉ mục chính xác hơn. |
| **OFFSET & LIMIT để phân trang** | **Keyset Pagination (Cursor)** | `OFFSET 100000 LIMIT 20` bắt buộc Postgres phải đọc và loại bỏ 100.000 dòng đầu tiên (Disk I/O khổng lồ). Dùng Keyset `WHERE id > last_seen_id ORDER BY id LIMIT 20` để tận dụng B-Tree index scan nhanh gấp hàng ngàn lần. |
| **Lưu trữ JSON bán cấu trúc tùy tiện** | **JSONB + Partial Indexes** | `JSON` dạng text trong Postgres chỉ lưu chuỗi thông thường. Hãy luôn dùng `JSONB` (đã được parse nhị phân) và kết hợp đánh index biểu thức cụ thể trên key/value cần truy vấn để tránh Sequential Scan. |
| **Khóa dòng lạc quan (Optimistic Locking)** | **MVCC & Row-Level Lock (SELECT FOR UPDATE)** | Postgres sử dụng MVCC giúp tác vụ Đọc không bao giờ block tác vụ Ghi. Tuy nhiên, khi cần cập nhật số dư tài khoản hoặc số lượng tồn kho, hãy dùng `SELECT ... FOR UPDATE` để ngăn chặn tình trạng Race Condition đáng tiếc. |

#### Quy Tắc Vàng Tối Ưu Hóa PostgreSQL Cho API Production:

1. **Giám sát chặt chẽ Connection Pool**: Node.js là đơn luồng xử lý I/O không đồng bộ, có thể gửi hàng ngàn query đồng thời. Nhưng PostgreSQL cấp phát 1 process riêng cho mỗi connection (rất nặng). Hãy thiết lập **PgBouncer** làm middleware gom nhóm kết nối để tránh cạn kiệt RAM và CPU của DB Server.
2. **Không bao giờ chạy SELECT \***: Trong ORM, việc lấy toàn bộ cột là mặc định. Việc này phá hỏng cơ hội thực hiện **Index-Only Scan** và làm tăng băng thông truyền tải dữ liệu. Luôn chỉ định rõ ràng các cột cần lấy trong câu lệnh SELECT.
3. **Cấu hình Autovacuum đúng cách**: Mặc định, Autovacuum chỉ chạy khi 20% số dòng của bảng bị thay đổi. Với bảng 10M dòng, cần 2M dòng chết thì vacuum mới chạy, gây bloat đĩa nghiêm trọng và làm chậm index scan. Hãy giảm ngưỡng `autovacuum_vacuum_scale_factor` xuống `0.05` (5%) cho các bảng có tần suất cập nhật cao.
4. **Luôn đo lường hiệu năng bằng BUFFERS**: Khi tối ưu hóa, đừng chỉ nhìn vào thời gian chạy (Execution Time) vì nó bị ảnh hưởng bởi cache hệ thống. Hãy chạy `EXPLAIN (ANALYZE, BUFFERS)` và tập trung giảm thiểu số lượng **Shared Read** (đọc từ đĩa) và **Shared Hit** (đọc từ RAM). Truy vấn đọc càng ít block bộ nhớ thì hệ thống càng chịu tải tốt.

---

### 🚀 Lộ Trình Học Tập Đề Xuất

1. **Tuần 1**: Internals & Lưu Trữ (Level 1-2) - Hiểu sâu về cấu trúc khối PL/pgSQL, cách tối ưu hóa các hàm đệ quy CTE, cơ chế hoạt động của MVCC và cách thiết lập hệ thống SaaS đa người thuê an toàn với RLS.
2. **Tuần 2**: Chiến Lược Đánh Chỉ Mục & Phân Vùng (Level 3) - Phân tích đặc trưng của 8 loại index, học cách tự động hóa tạo phân vùng bảng cho dữ liệu lớn bằng `pg_partman`.
3. **Tuần 3**: JSONB Lai Ghép & Tối Ưu Hóa Truy Vấn (Level 4-5) - Tích hợp cấu trúc document linh hoạt, tối ưu hóa câu lệnh SQL phức tạp bằng cách đọc hiểu chi tiết bản kế hoạch EXPLAIN ANALYZE và khắc phục các điểm nghẽn bộ nhớ.
4. **Tuần 4**: Vận Hành Đỉnh Cao (Level 5) - Thực hành thiết lập cụm cơ sở dữ liệu có tính sẵn sàng cao (High Availability), thực hiện mô phỏng sự cố để kích hoạt cơ chế tự động chuyển đổi dự phòng Failover của Patroni.
