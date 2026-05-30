<!-- tags: java, spring-boot -->
# ☕ Spring Boot Actuator — Health, Metrics & Readiness

> Khi service đã chạy production, vấn đề không còn là “API có hoạt động không” mà là “service có khỏe, sẵn sàng và quan sát được không”. Đây là vai trò chính của Actuator.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 14 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Intermediate |
| **Use case** | Production observability, probes, basic metrics |
| **Java focus** | Actuator endpoints, health groups, readiness/liveness |
| **Prerequisites** | Spring Boot basics, config |

## 1. DEFINE

Hình dung service vừa deploy xong, pod vẫn lên nhưng readiness check chập chờn, metrics thì chưa phản ánh đúng tình trạng downstream, còn đội vận hành không biết nên tin health endpoint tới mức nào. Actuator chỉ có giá trị khi bạn dùng nó để nói sự thật về trạng thái runtime, không phải để cho dashboard đẹp hơn.

Bài này đặt `Spring Boot Actuator — Health, Metrics & Readiness` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Actuator giúp gì?

Actuator cung cấp endpoint vận hành để:

- kiểm tra service còn sống hay không
- xác định service đã sẵn sàng nhận traffic chưa
- expose metrics cơ bản cho monitoring
- hỗ trợ debug production mà không cần chọc trực tiếp vào business API

### Actors

| Actor | Vai trò |
| --- | --- |
| Liveness probe | Kiểm tra app process còn sống |
| Readiness probe | Kiểm tra app đã sẵn sàng phục vụ traffic |
| Health indicator | Đóng góp trạng thái của dependency |
| Metrics endpoint | Xuất số liệu cho monitoring system |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Probe luôn xanh dù DB chết | Health check quá nông | Thêm dependency-aware indicator |
| Expose quá nhiều endpoint | Security lỏng | Chỉ mở endpoint cần thiết |
| Readiness/liveness trộn lẫn | Semantics không rõ | Tách health group rõ ràng |

Các failure mode trên nghe dễ tránh. Nhưng có trap: health endpoint expose internal state = information leak, và liveness/readiness probe sai = pod flapping. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Với Spring Boot Actuator — Health, Metrics & Readiness, phần khó không nằm ở tên annotation hay package nữa mà ở flow thật của request, bean hoặc boundary. Sơ đồ dưới đây giúp kéo flow đó ra ánh sáng.

```text
Kubernetes / Load balancer
          │
          ├── /actuator/health/liveness   -> process alive?
          ├── /actuator/health/readiness  -> ready for traffic?
          └── /actuator/metrics           -> operational numbers
```

```text
dependency states
   │
   ├── database  -> UP
   ├── cache     -> UP
   └── broker    -> DOWN
          │
          ▼
health group result
```

## 3. CODE

Sơ đồ đã cho bạn thấy flow của Spring Boot Actuator — Health, Metrics & Readiness. Bây giờ ta chuyển nó thành code Java/Spring đủ gần production để boundary không còn là khái niệm mơ hồ.

### Basic: expose selected actuator endpoints

```yaml
# application.yml — Minimal actuator exposure
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
  endpoint:
    health:
      probes:
        enabled: true
```

Health đã cover. Nhưng custom metrics cần MeterRegistry — hãy instrument.

### Intermediate: readiness and liveness groups

```yaml
# application-prod.yml — Health groups for orchestration platform
management:
  endpoint:
    health:
      group:
        readiness:
          include: readinessState,db
        liveness:
          include: livenessState
```

Metrics đã cover. Nhưng readiness cần probe tuning — hãy deploy.

### Advanced: custom health indicator

```java
// StorageHealthIndicator.java — Custom dependency health contribution
package com.example.ordering.observability;

import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.stereotype.Component;

@Component
public class StorageHealthIndicator implements HealthIndicator {
    private final StorageClient storageClient;

    public StorageHealthIndicator(StorageClient storageClient) {
        this.storageClient = storageClient;
    }

    @Override
    public Health health() {
        if (storageClient.isAvailable()) {
            return Health.up()
                    .withDetail("provider", "object-storage")
                    .build();
        }
        return Health.down()
                .withDetail("provider", "object-storage")
                .build();
    }

    public interface StorageClient {
        boolean isAvailable();
    }
}
```

Bạn đã đi qua health, metrics, và readiness. Bây giờ đến phần nguy hiểm: info leak và probe flapping — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Spring Boot Actuator — Health, Metrics & Readiness` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Mở toàn bộ actuator endpoints công khai | Chỉ expose endpoint cần thiết |
| 2 | Readiness không check dependency chính | Thêm health indicator phù hợp |
| 3 | Dùng health endpoint như business API | Giữ actuator cho vận hành |
| 4 | Không gắn metrics vào monitoring pipeline | Tích hợp Prometheus/Micrometer ở bước sau |

Bạn đã đi qua Actuator và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Spring Boot Actuator | https://docs.spring.io/spring-boot/reference/actuator/index.html |
| Health Information | https://docs.spring.io/spring-boot/reference/actuator/endpoints.html#actuator.endpoints.health |
| Kubernetes Probes | https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/ |

## 6. RECOMMEND

Khi các bẫy chính của `Spring Boot Actuator — Health, Metrics & Readiness` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Micrometer + Prometheus | Cần metrics production thật | Dễ scrape và alert |
| Security for actuator | Service public internet | Tránh lộ endpoint nhạy cảm |
| Tracing/log correlation | Cần debug distributed flow | Quan sát sâu hơn health màu xanh/đỏ |

## 7. QUIZ

### Quick Check

1. Readiness và liveness khác nhau ở điểm cốt lõi nào?
2. Vì sao không nên mở tất cả actuator endpoint công khai?
3. Khi nào cần custom health indicator?

### Answer Key

1. Liveness hỏi app còn sống, readiness hỏi app đã sẵn sàng nhận traffic chưa.
2. Vì có thể lộ thông tin vận hành không cần thiết hoặc tăng bề mặt tấn công.
3. Khi dependency quan trọng không được phản ánh đủ bởi health mặc định.

## 8. NEXT STEPS

- Đi tiếp sang `testing/integration` để test endpoint/health contract
- Hoặc mở rộng `metrics` với Micrometer ở batch sau
