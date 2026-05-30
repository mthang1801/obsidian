<!-- tags: java, expert -->
# ☕ Java Expert — Metrics, Logs & Trace Correlation

> Observability không phải chỉ là “đã có log”. Bài này tập trung vào ba trụ cột metrics, logs, tracing và cách nối chúng lại để backend Java debug được incident thật sự.

📅 Ngày tạo: 2026-03-28 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 15 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Expert |
| **Use case** | Production debugging, latency analysis, incident response |
| **Java focus** | metrics, structured logs, correlation IDs, tracing mindset |
| **Prerequisites** | actuator, performance profiling, resilience mindset |

## 1. DEFINE

Hình dung một request checkout vừa chậm vừa lỗi, nhưng metrics chỉ cho bạn thấy CPU và latency, logs thì không đủ correlation id, còn trace lại đứt ngay trước downstream đáng nghi nhất. Observability đáng đọc nhất ở chính lúc ba nguồn tín hiệu này không chịu nói cùng một câu chuyện.

Bài này đặt `Java Expert — Metrics, Logs & Trace Correlation` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Observability trả lời câu hỏi gì?

Một hệ thống observable giúp trả lời:

- hiện tại có gì bất thường
- request nào bị chậm hoặc fail
- dependency nào đang kéo hệ thống xuống
- incident đang lan theo flow nào

### Ba trụ cột

| Pillar | Trả lời gì | Ví dụ |
| --- | --- | --- |
| Metrics | “Có gì đang lệch khỏi baseline?” | error rate, latency, queue depth |
| Logs | “Chuyện gì đã xảy ra ở step cụ thể?” | structured event log |
| Tracing | “Một request đi qua các service thế nào?” | span timeline |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Có log nhưng không correlate được | Thiếu request/trace ID | Chuẩn hóa correlation |
| Có metrics nhưng không drill-down được | Không có logs/traces hỗ trợ | Kết nối 3 pillar |
| Noise quá nhiều | Log không structure, metrics vô nghĩa | Chọn signal có giá trị |

Các failure mode trên nghe quen. Nhưng có trap: log không có traceId = request tracing impossible, và metric cardinality explosion = monitoring cost spike. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa mới chỉ khóa được tên của Java Expert — Metrics, Logs & Trace Correlation. Để khái niệm này bớt trừu tượng, ta cần nhìn nó ở dạng flow hoặc cấu trúc đủ cụ thể trước.

```text
metric spike
   │
   ▼
find affected endpoint / dependency
   │
   ▼
inspect logs with correlation id
   │
   ▼
open trace for full request path
```

```text
request
  │
  ├── trace id
  ├── structured log fields
  └── latency/error metrics
```

## 3. CODE

Flow của Java Expert — Metrics, Logs & Trace Correlation đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: structured log shape

```java
// OrderLogShape.java — Example structured log contract
public record OrderLogShape(
        String traceId,
        String orderId,
        String step,
        String status
) {
}
```

Metrics basics đã cover. Nhưng trace correlation cần context propagation — hãy inject.

### Intermediate: correlation-first logging

```java
// CorrelationLoggingExample.java — Carry correlation id across application steps
public final class CorrelationLoggingExample {
    public void logStep(String traceId, String step) {
        System.out.printf("traceId=%s step=%s%n", traceId, step);
    }
}
```

Correlation đã cover. Nhưng structured logging cần MDC — hãy enrich.

### Advanced: observability checklist

```text
1. Define golden signals: latency, traffic, errors, saturation
2. Ensure every request has correlation metadata
3. Keep structured logs parseable
4. Sample traces intentionally, not blindly
5. Link dashboards to runbooks and alerts
```

Bạn đã đi qua metrics, traces, và logging. Bây giờ đến phần nguy hiểm: missing traceId và cardinality explosion — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Expert — Metrics, Logs & Trace Correlation` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Log string tự do không structure | Chuẩn hóa fields |
| 2 | Có metrics nhưng không action được | Chọn signal gắn với SLO/SLA |
| 3 | Mỗi service dùng request ID khác format | Chuẩn hóa propagation |
| 4 | Trace sampling vô tội vạ | Chọn strategy theo cost và incident value |

Bạn đã đi qua Observability và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| OpenTelemetry Java | https://opentelemetry.io/docs/languages/java/ |
| Micrometer | https://micrometer.io/ |
| Google SRE Observability | https://sre.google/sre-book/monitoring-distributed-systems/ |

## 6. RECOMMEND

Khi các bẫy chính của `Java Expert — Metrics, Logs & Trace Correlation` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Micrometer + Prometheus | Cần metrics scraping chuẩn | Dễ dashboard và alert |
| OpenTelemetry tracing | Có multi-service flow | Correlation tốt hơn |
| Structured JSON logging | Log volume lớn | Parse và search ổn định |

## 7. QUIZ

### Quick Check

1. Metrics, logs, tracing khác nhau ở điểm cốt lõi nào?
2. Vì sao correlation ID quan trọng?
3. Khi nào observability “có mà như không”?

### Answer Key

1. Metrics cho xu hướng, logs cho sự kiện chi tiết, tracing cho đường đi request.
2. Vì nó nối các log/signal rời rạc về cùng một flow.
3. Khi thiếu structure, thiếu correlation, hoặc signal không gắn với action thực tế.

## 8. NEXT STEPS

- Nối với `spring-boot/actuator` để đưa observability vào app thật
- Hoặc quay lại `resilience` để đo policy hoạt động ra sao khi incident xảy ra
