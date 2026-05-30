<!-- tags: java, spring-boot -->
# ☕ Spring Boot Basics — Bootstrap & Project Structure

> Bài khởi đầu để dựng một Spring Boot service gọn, đọc được, dễ test và không rơi vào kiểu project “chạy được nhưng khó bảo trì”.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 13 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Intermediate |
| **Use case** | Tạo service backend mới bằng Spring Boot |
| **Java focus** | `@SpringBootApplication`, package-by-feature, config |
| **Prerequisites** | Java basics, collections |

## 1. DEFINE

Hình dung bạn vừa tạo một Spring Boot service mới. Mọi thứ chạy được rất nhanh, endpoint đầu tiên phản hồi chỉ sau vài phút, và cũng chính vì nhanh như vậy mà những quyết định nền đầu tiên dễ bị làm cho xong hơn là làm cho đúng. Bài này mở ở khoảnh khắc bootstrap còn đủ sớm để cứu tương lai của project.

Bài này mở ra đúng ở thời điểm đó: khi bạn cần một cách bắt đầu đủ nhanh để ship, nhưng cũng đủ sạch để không phải xin lỗi với đội tương lai của mình.

### Spring Boot giải quyết gì?

Spring Boot giúp giảm boilerplate khi dựng Java backend:

- auto-configuration cho dependency phổ biến
- embedded server để chạy web app nhanh
- starter dependencies để quản lý stack thống nhất
- actuator/config/profile giúp project đi production nhanh hơn

### Invariants

| Quy tắc | Ý nghĩa |
| --- | --- |
| Ưu tiên package-by-feature | Dễ scale theo domain |
| Constructor injection cho dependency bắt buộc | Dependency explicit, dễ test |
| Không expose entity trực tiếp ra web layer | Tách DTO và domain rõ ràng |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Project phình to theo layer cứng | Chia package `controller/service/repository` toàn cục | Chuyển sang package-by-feature |
| Hardcode config | Bỏ thẳng URL/secret vào code | Dùng `application.yml` + env |
| Constructor rỗng + field injection | Dependency ẩn | Dùng constructor injection |

Các failure mode trên nghe cơ bản. Nhưng có trap: @ComponentScan package sai = beans không được tìm thấy, và auto-configuration conflict = bean override error. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Với Spring Boot Basics — Bootstrap & Project Structure, phần khó không nằm ở tên annotation hay package nữa mà ở flow thật của request, bean hoặc boundary. Sơ đồ dưới đây giúp kéo flow đó ra ánh sáng.

```text
Spring Boot app

Application
   │
   ├── configuration
   ├── feature package
   │      ├── api
   │      ├── application
   │      └── domain
   └── infrastructure
```

```text
Request
  │
  ▼
Controller DTO
  │
  ▼
Service / Use case
  │
  ▼
Repository / External client
```

## 3. CODE

Sơ đồ đã cho bạn thấy flow của Spring Boot Basics — Bootstrap & Project Structure. Bây giờ ta chuyển nó thành code Java/Spring đủ gần production để boundary không còn là khái niệm mơ hồ.

### Basic: minimal boot application

```java
// OrderServiceApplication.java — Spring Boot application bootstrap
package com.example.ordering;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Entry point for the ordering service.
 */
@SpringBootApplication
public class OrderServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(OrderServiceApplication.class, args);
    }
}
```

Bootstrap đã cover. Nhưng project structure cần layering — hãy tổ chức.

### Intermediate: feature-oriented service with constructor injection

```java
// OrderApplicationService.java — Application service with explicit dependency
package com.example.ordering.order.application;

import com.example.ordering.order.domain.Order;
import com.example.ordering.order.domain.OrderRepository;
import org.springframework.stereotype.Service;

@Service
public class OrderApplicationService {
    private final OrderRepository orderRepository;

    public OrderApplicationService(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    /**
     * Creates and stores a new order aggregate.
     *
     * @param customerId customer identifier
     * @return created order
     */
    public Order create(long customerId) {
        Order order = Order.newDraft(customerId);
        return orderRepository.save(order);
    }
}
```

Structure đã cover. Nhưng multi-module cần parent POM — hãy chia.

### Advanced: typed configuration with `@ConfigurationProperties`

```java
// StorageProperties.java — Type-safe configuration for external storage
package com.example.ordering.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * Maps storage-related properties from application configuration.
 *
 * @param bucket bucket name
 * @param signedUrlTtlSeconds TTL for signed URLs
 */
@ConfigurationProperties(prefix = "app.storage")
public record StorageProperties(String bucket, long signedUrlTtlSeconds) {
    public StorageProperties {
        if (bucket == null || bucket.isBlank()) {
            throw new IllegalArgumentException("bucket must not be blank");
        }
        if (signedUrlTtlSeconds <= 0) {
            throw new IllegalArgumentException("signedUrlTtlSeconds must be positive");
        }
    }
}
```

Bạn đã đi qua bootstrap, structure, và multi-module. Bây giờ đến phần nguy hiểm: scan miss và auto-config conflict — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Spring Boot Basics — Bootstrap & Project Structure` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Dồn toàn bộ code vào package layer-wide | Tổ chức theo feature/domain |
| 2 | Dùng field injection | Constructor injection |
| 3 | Nhét config vào constant | Dùng `application.yml` + `@ConfigurationProperties` |
| 4 | Controller gọi repository trực tiếp | Đi qua service/use case |

Bạn đã đi qua Spring Boot Basics và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Spring Boot Reference | https://docs.spring.io/spring-boot/documentation.html |
| Configuration Properties | https://docs.spring.io/spring-boot/reference/features/external-config.html |
| Spring Initializr | https://start.spring.io |

## 6. RECOMMEND

Khi các bẫy chính của `Spring Boot Basics — Bootstrap & Project Structure` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Web starter | Cần REST API | Có MVC + validation |
| Actuator | Cần health/metrics | Hỗ trợ production ops |
| Testcontainers | Cần integration test thật | Giảm sai khác môi trường |

## 7. QUIZ

### Quick Check

1. Vì sao package-by-feature dễ scale hơn package-by-layer?
2. Khi nào nên dùng `@ConfigurationProperties`?
3. Vì sao constructor injection được ưu tiên?

### Answer Key

1. Vì code liên quan cùng feature nằm gần nhau, dễ đọc và refactor.
2. Khi cấu hình có cấu trúc và cần binding type-safe.
3. Vì dependency explicit, immutable hơn và test dễ hơn.

## 8. NEXT STEPS

- Đọc tiếp [REST Controller & Validation](../web/01-rest-controller-validation.md)
- Sau đó mở rộng sang `config/` và `actuator/`
