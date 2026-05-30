<!-- tags: java, quiz, scenario, production -->
# Java Scenario Quiz — On-Call Triage for Service Incidents

> Tình huống Java backend production nơi request timeout, thread pool saturation, transaction pressure và observability gap xuất hiện cùng lúc.

📅 Ngày tạo: 2026-04-04 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 9 phút đọc

## 1. DEFINE

Bạn đang on-call cho một Spring Boot service xử lý checkout. Sau một đợt traffic tăng, P95 latency nhảy từ 180ms lên 4.2s, HTTP 500 bắt đầu tăng, active threads chạm ngưỡng pool và DB connection pool cũng gần cạn. Trong vài phút đầu tiên đó, mọi khái niệm bạn từng đọc về Java backend bị ép phải nói chung một ngôn ngữ.

Đây là kiểu sự cố khiến kiến thức rời rạc không đủ dùng. Bạn phải quyết định thứ gì cần kiểm tra trước để không biến một hệ thống đang đau thành một hệ thống vừa đau vừa mù dữ liệu.

| Variant | Mô tả |
| --- | --- |
| Thread-pool pressure | request backlog, blocking downstream, saturation |
| Transaction pressure | DB pool exhaustion, long transaction, retry storm |
| Observability gap | metrics có nhưng không đủ để chốt nguyên nhân |

Core insight:

> Trong incident Java backend, bước đầu đúng hiếm khi là bước “mạnh” nhất; nó thường là bước giúp bạn mua thêm thời gian mà không xóa dấu vết của nguyên nhân.

## 2. VISUAL

Tình huống này chỉ rõ khi bạn thấy được mối liên hệ giữa request path, thread pool và DB boundary. Nếu không nhìn ba điểm này cùng lúc, rất dễ hành động theo cảm giác.

### Level 1

```text
incoming requests
      |
      v
controller -> service -> transaction -> repository -> database
      |
      v
thread pool saturation if downstream blocks
```

*Hình: Request path chỉ có vài bước, nhưng mỗi bước đều có thể giữ thread và connection lâu hơn dự kiến.*

### Level 2

```text
Signal                          Điều cần hỏi ngay
-----------------------------  ------------------------------------------
active threads tăng mạnh       thread đang CPU-bound hay blocked?
DB pool gần cạn                transaction nào giữ connection quá lâu?
500 tăng theo latency          timeout ở đâu, fallback có hoạt động không?
```

*Hình: Level 2 biến symptom thành câu hỏi triage, không phải thành fix ngay lập tức.*

## 3. CODE

Artifact dưới đây là dạng câu trả lời tốt cho scenario này: không phô diễn kỹ thuật, mà khóa thứ tự hành động và blast radius.

### Basic: first-five-minutes triage note

```text
1. Freeze risky changes: chưa tăng thread pool, chưa restart hàng loạt.
2. Kiểm tra active request breakdown: blocked downstream hay CPU spike.
3. Kiểm tra DB pool + slow transaction evidence.
4. Xem timeout/fallback metrics của downstream clients.
5. Chọn hành động ít phá dấu vết nhất:
   - nếu downstream treo: degrade feature hoặc shed load có kiểm soát
   - nếu transaction giữ connection lâu: chặn traffic gây write storm
```

**Tại sao?** Tình huống này được dựng để xem bạn có phân biệt được “giảm đau tạm thời” với “sửa đúng” hay không. Tăng pool hoặc restart có thể làm symptom đổi hình nhưng cũng có thể xóa evidence khiến root cause khó thấy hơn.

**Kết luận**: Incident tốt không thưởng cho hành động nhanh nhất. Nó thưởng cho hành động làm hệ thống đỡ đau mà vẫn giữ được khả năng nhìn ra sự thật.

## 4. PITFALLS

Biết cách dùng `Java Scenario Quiz — On-Call Triage for Service Incidents` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Severity | Lỗi | Hậu quả | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Fatal | Tăng thread pool ngay khi chưa biết blocked ở đâu | Tăng pressure lên DB/downstream | Chốt blocked-vs-CPU evidence trước |
| 2 | 🟠 Major | Restart pod để “hết lỗi” | Mất dấu vết runtime, incident quay lại sau ít phút | Ưu tiên snapshot metrics/thread dump |
| 3 | 🟠 Major | Chỉ nhìn application metrics mà quên DB pool | Chẩn đoán lệch tầng | Kiểm app và persistence boundary cùng lúc |

## 5. REF

| Resource | Loại | Link | Ghi chú |
| --- | --- | --- | --- |
| Spring Boot Actuator | Official docs | https://docs.spring.io/spring-boot/reference/actuator/ | Metrics và health endpoints |
| HikariCP Wiki | Official docs | https://github.com/brettwooldridge/HikariCP/wiki | Connection pool behavior |
| JFR Runtime Guide | Official docs | https://docs.oracle.com/javacomponents/jmc/ | Thread/blocking evidence |

## 6. RECOMMEND

Khi các bẫy chính của `Java Scenario Quiz — On-Call Triage for Service Incidents` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do | File |
| --- | --- | --- | --- |
| [01-executors-thread-pools-shutdown.md](../../concurrency/executors/01-executors-thread-pools-shutdown.md) | Sai ở thread-pool mental model | Làm rõ saturation và shutdown behavior | Nội bộ |
| [01-transaction-boundaries-rollback-idempotency.md](../../backend/transactions/01-transaction-boundaries-rollback-idempotency.md) | Sai ở transaction boundary | Giảm connection hold time | Nội bộ |
| [01-metrics-logs-trace-correlation.md](../../expert/observability/01-metrics-logs-trace-correlation.md) | Sai ở observability reading | Củng cố evidence-based triage | Nội bộ |
