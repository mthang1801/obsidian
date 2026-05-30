<!-- tags: java, expert -->
# ☕ Java Expert — Timeouts, Retries & Circuit Breaker Mindset

> Resilience không phải là “bật retry ở khắp nơi”. Bài này tập trung vào mental model để backend Java chịu lỗi tốt hơn khi network, database, hoặc downstream services trở nên bất ổn.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 15 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Expert |
| **Use case** | External API instability, partial failure, retry storm prevention |
| **Java focus** | timeout, retry, circuit breaker, bulkhead mindset |
| **Prerequisites** | HTTP client, CompletableFuture, Spring Boot basics |

## 1. DEFINE

Hình dung downstream bắt đầu chậm đi đúng lúc traffic tăng. Mỗi request treo thêm vài giây, retry nối tiếp retry, và trước khi bạn kịp gọi tên sự cố, chính cơ chế “chống lỗi” đã góp phần khuếch đại nó. Resilience không phải danh sách pattern nghe ngầu; nó là cách hệ thống phản ứng khi sự cố đã chạm cửa.

Bài này đặt `Java Expert — Timeouts, Retries & Circuit Breaker Mindset` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Vì sao resilience quan trọng?

Trong distributed system, failure là mặc định chứ không phải ngoại lệ. Một call chậm hoặc fail có thể kéo theo:

- thread pool cạn
- retry storm
- latency lan truyền sang service khác

### Actors

| Actor | Vai trò |
| --- | --- |
| Timeout | Cắt request chậm quá mức chấp nhận |
| Retry | Thử lại có kiểm soát |
| Circuit breaker | Dừng gọi dependency đang fail hàng loạt |
| Bulkhead | Cô lập tài nguyên để một vùng lỗi không kéo sập toàn app |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Retry storm | Retry vô tội vạ ở nhiều tầng | Retry budget + jitter + idempotency |
| Thread starvation | Chờ dependency quá lâu | Timeout + bulkhead |
| Cascading failure | Không cô lập dependency | Circuit breaker + fallback |

Các failure mode trên nghe rõ. Nhưng có trap: retry without backoff = thundering herd, và circuit breaker half-open state không handle = stuck open. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa mới chỉ khóa được tên của Java Expert — Timeouts, Retries & Circuit Breaker Mindset. Để khái niệm này bớt trừu tượng, ta cần nhìn nó ở dạng flow hoặc cấu trúc đủ cụ thể trước.

```text
request
  │
  ├── timeout
  ├── retry (bounded)
  ├── circuit breaker
  └── fallback / fail fast
```

```text
dependency unstable
   │
   ├── no resilience  -> threads pile up -> service degrades
   └── resilience     -> fail fast -> protect core capacity
```

## 3. CODE

Flow của Java Expert — Timeouts, Retries & Circuit Breaker Mindset đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: timeout wrapper

```java
// TimeoutGuard.java — Guard a slow supplier with a timeout contract
import java.time.Duration;

public final class TimeoutGuard {
    private TimeoutGuard() {
    }

    public static Duration recommendation() {
        return Duration.ofSeconds(2);
    }
}
```

Timeout đã cover. Nhưng retries cần exponential backoff — hãy dampen.

### Intermediate: bounded retry policy idea

```java
// RetryPolicySketch.java — Keep retries explicit and bounded
public record RetryPolicySketch(int maxAttempts, long backoffMillis, boolean idempotentOnly) {
    public RetryPolicySketch {
        if (maxAttempts <= 0) {
            throw new IllegalArgumentException("maxAttempts must be positive");
        }
        if (backoffMillis < 0) {
            throw new IllegalArgumentException("backoffMillis must not be negative");
        }
    }
}
```

Retries đã cover. Nhưng circuit breaker cần state machine — hãy protect.

### Advanced: circuit breaker mindset checklist

```text
1. Detect error-rate or slow-call threshold
2. Open circuit when dependency becomes harmful
3. Fail fast during cool-down period
4. Probe dependency carefully in half-open state
5. Close only when health is restored
```

Bạn đã đi qua timeout, retries, và circuit breaker. Bây giờ đến phần nguy hiểm: thundering herd và stuck circuit — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Expert — Timeouts, Retries & Circuit Breaker Mindset` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Retry ở mọi tầng cùng lúc | Đặt chiến lược retry có chủ đích |
| 2 | Timeout quá dài | Fit timeout theo SLA thật |
| 3 | Dùng circuit breaker mà không có metric | Quan sát error rate/latency rõ ràng |
| 4 | Retry cho operation không idempotent | Chỉ retry khi side effect được kiểm soát |

Bạn đã đi qua Resilience Patterns và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Release It! patterns | https://pragprog.com/titles/mnee2/release-it-second-edition/ |
| Resilience4j | https://resilience4j.readme.io/ |
| Google SRE workbook | https://sre.google/workbook/ |

## 6. RECOMMEND

Khi các bẫy chính của `Java Expert — Timeouts, Retries & Circuit Breaker Mindset` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Resilience4j integration | Cần implementation thực | Chuẩn hóa policy |
| Bulkhead metrics | Thread/resource contention cao | Tránh hidden saturation |
| Idempotency strategy | Retry có side effect | Bảo vệ business correctness |

## 7. QUIZ

### Quick Check

1. Vì sao retry không nên bật bừa ở mọi tầng?
2. Circuit breaker bảo vệ điều gì quan trọng nhất?
3. Khi nào retry là nguy hiểm về business correctness?

### Answer Key

1. Vì dễ tạo retry storm và khuếch đại failure.
2. Nó bảo vệ năng lực xử lý của chính service khỏi dependency xấu.
3. Khi operation không idempotent và có side effect có thể bị lặp.

## 8. NEXT STEPS

- Nếu cần implementation thật, batch sau có thể seed bài Resilience4j
- Hoặc nối sang observability để đo resilience policy hiệu quả đến đâu
