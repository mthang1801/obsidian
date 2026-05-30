<!-- tags: java, spring -->
# ☕ Spring Beans — Lifecycle, Scopes & Java Config

> Sau khi hiểu container tạo dependency graph ra sao, bước tiếp theo là hiểu bean sống như thế nào trong graph đó. Scopes, lifecycle callback và Java config quyết định ứng dụng Spring có predictable hay không khi đi vào production.

📅 Ngày tạo: 2026-03-28 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 14 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Advanced |
| **Use case** | Cấu hình bean lifecycle và scope đúng cách |
| **Java focus** | `@Bean`, scopes, `@PostConstruct`, `@PreDestroy` |
| **Prerequisites** | ApplicationContext, DI basics |

## 1. DEFINE

Hình dung một bean Spring hoạt động rất bình thường cho đến ngày bạn đổi scope, thêm config hoặc inject nó vào một chỗ sống lâu hơn dự kiến. Từ đó, lifecycle không còn là kiến thức phụ. Nó trở thành thứ quyết định object nào được tạo lúc nào, sống bao lâu và bị framework quản lý theo luật gì.

Bài này đặt `Spring Beans — Lifecycle, Scopes & Java Config` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Bean lifecycle gồm những gì?

Một bean Spring thường đi qua:

- definition registration
- instantiation
- dependency injection
- initialization callback
- ready for use
- destruction callback khi context đóng

### Scope phổ biến

| Scope | Ý nghĩa |
| --- | --- |
| `singleton` | một instance cho toàn context |
| `prototype` | mỗi lần request bean tạo instance mới |
| `request` | một instance cho mỗi HTTP request |
| `session` | một instance cho mỗi HTTP session |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Dùng sai scope | state bị chia sẻ ngoài ý muốn | chọn scope theo lifecycle thật |
| Bean init quá nặng | startup chậm hoặc side effect sớm | tách lazy init hoặc bootstrap hợp lý |
| Cleanup thiếu | resource như connection/file handle không được giải phóng | dùng callback destroy rõ ràng |

Các failure mode trên nghe quen. Nhưng có trap: prototype bean inject vào singleton = stale reference, và @PostConstruct gọi dependency chưa ready = NPE. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Với Spring Beans — Lifecycle, Scopes & Java Config, phần khó không nằm ở tên annotation hay package nữa mà ở flow thật của request, bean hoặc boundary. Sơ đồ dưới đây giúp kéo flow đó ra ánh sáng.

```text
Bean definition
    │
    ▼
instantiate
    │
    ▼
inject dependencies
    │
    ▼
init callback
    │
    ▼
ready for use
    │
    ▼
destroy callback
```

## 3. CODE

Sơ đồ đã cho bạn thấy flow của Spring Beans — Lifecycle, Scopes & Java Config. Bây giờ ta chuyển nó thành code Java/Spring đủ gần production để boundary không còn là khái niệm mơ hồ.

### Basic: Java config with `@Bean`

```java
// BillingConfiguration.java — Explicit bean wiring with Java config
package com.example.springbeans;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class BillingConfiguration {
    @Bean
    public CurrencyFormatter currencyFormatter() {
        return new CurrencyFormatter("VND");
    }
}
```

Bean lifecycle đã cover. Nhưng scopes cần prototype vs singleton — hãy chọn.

### Intermediate: lifecycle callbacks

```java
// ReportBuffer.java — Initialize and clean up resource-oriented bean explicitly
package com.example.springbeans;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import org.springframework.stereotype.Component;

@Component
public class ReportBuffer {
    @PostConstruct
    public void warmUp() {
        System.out.println("report buffer warmed up");
    }

    @PreDestroy
    public void flushBeforeShutdown() {
        System.out.println("report buffer flushed");
    }
}
```

Scopes đã cover. Nhưng conditional beans cần @Profile/@Conditional — hãy filter.

### Advanced: scope with stateful bean

```java
// RequestTraceContext.java — Request-scoped bean for per-request state
package com.example.springbeans;

import java.util.UUID;
import org.springframework.stereotype.Component;
import org.springframework.web.context.annotation.RequestScope;

@Component
@RequestScope
public class RequestTraceContext {
    private final String traceId = UUID.randomUUID().toString();

    public String traceId() {
        return traceId;
    }
}
```

Bạn đã đi qua lifecycle, scopes, và conditional. Bây giờ đến phần nguy hiểm: stale prototype và premature init — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Spring Beans — Lifecycle, Scopes & Java Config` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Dùng singleton cho object giữ mutable request state | chuyển sang request scope hoặc bỏ state |
| 2 | Dồn logic network/file nặng vào init callback | giữ init nhẹ, tách bootstrap hợp lý |
| 3 | Không cleanup resource khi shutdown | dùng `@PreDestroy` hoặc lifecycle contract rõ ràng |
| 4 | Quá phụ thuộc component scan mặc định | dùng Java config nơi cần wiring tường minh |

Bạn đã đi qua Bean Lifecycle và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Spring Bean Overview | https://docs.spring.io/spring-framework/reference/core/beans/definition.html |
| Bean Scopes | https://docs.spring.io/spring-framework/reference/core/beans/factory-scopes.html |
| Lifecycle Callbacks | https://docs.spring.io/spring-framework/reference/core/beans/factory-nature.html |

## 6. RECOMMEND

Khi các bẫy chính của `Spring Beans — Lifecycle, Scopes & Java Config` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| `@ConfigurationProperties` | Bean config có nhiều field | type-safe hơn |
| Lazy initialization | Startup cost cao | hoãn creation đến khi thật sự cần |
| Profiles + conditional beans | Wiring khác nhau theo môi trường | kiểm soát behavior tốt hơn |

## 7. QUIZ

### Quick Check

1. Khi nào `request` scope phù hợp hơn `singleton`?
2. Vì sao lifecycle callback cần được dùng có chủ đích?
3. `@Bean` trong Java config có lợi gì so với chỉ dựa vào component scan?

### Answer Key

1. Khi bean giữ state riêng cho từng HTTP request.
2. Vì callback init/destroy ảnh hưởng trực tiếp tới startup, shutdown và resource handling.
3. Nó giúp wiring tường minh và kiểm soát object creation rõ hơn.

## 8. NEXT STEPS

- Đọc tiếp [DispatcherServlet & Controller Flow](../mvc/01-dispatcher-servlet-controller-flow.md)
- Hoặc sang [Spring Boot](../../spring-boot/README.md) để thấy các bean này được auto-config như thế nào
