<!-- tags: java, spring -->
# ☕ Spring Core — ApplicationContext & Dependency Injection

> Điểm mạnh thật sự của Spring không nằm ở annotation nhiều hay ít, mà ở việc container quản lý object graph một cách nhất quán. Bài này tập trung vào mental model của `ApplicationContext` và dependency injection trước khi đi sâu sang Boot hay Security.

📅 Ngày tạo: 2026-03-28 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 14 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Intermediate |
| **Use case** | Hiểu cách Spring tạo và wire dependency |
| **Java focus** | `ApplicationContext`, constructor injection, bean lookup |
| **Prerequisites** | Java basics, OOP |

## 1. DEFINE

Hình dung bạn đang debug một service Spring mà bean cứ xuất hiện, biến mất hoặc bị inject bằng một đường nào đó không ai mô tả rõ được. ApplicationContext chỉ đáng học khi cảm giác “Spring tự làm phép màu” bắt đầu cản trở khả năng reasoning của bạn.

Bài này đặt `Spring Core — ApplicationContext & Dependency Injection` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### `ApplicationContext` là gì?

`ApplicationContext` là container trung tâm của Spring. Nó chịu trách nhiệm:

- tạo bean
- resolve dependency
- quản lý lifecycle
- cung cấp infrastructure services như events, profiles, environment

### Invariants

| Quy tắc | Ý nghĩa |
| --- | --- |
| Dependency nên đi qua constructor | dependency explicit và dễ test |
| Business code không nên tự `new` toàn bộ graph | để container chịu trách nhiệm wiring |
| Bean lookup thủ công chỉ nên dùng ở tình huống đặc biệt | tránh service locator disguised |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Bean graph rối và khó đoán | field injection / config tản mát | ưu tiên constructor injection |
| Circular dependency | thiết kế service boundary chưa tốt | tách responsibility hoặc redesign flow |
| Code khó test | class tự tạo dependency bằng `new` | inject qua constructor/interface |

Các failure mode trên nghe rõ. Nhưng có trap: circular dependency = BeanCurrentlyInCreationException, và field injection khó test = tight coupling. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Với Spring Core — ApplicationContext & Dependency Injection, phần khó không nằm ở tên annotation hay package nữa mà ở flow thật của request, bean hoặc boundary. Sơ đồ dưới đây giúp kéo flow đó ra ánh sáng.

```text
ApplicationContext
      │
      ├── create bean A
      ├── create bean B
      ├── resolve dependency A -> B
      └── expose ready-to-use object graph
```

```text
Controller
   │
   ▼
Service
   │
   ▼
Repository
```

## 3. CODE

Sơ đồ đã cho bạn thấy flow của Spring Core — ApplicationContext & Dependency Injection. Bây giờ ta chuyển nó thành code Java/Spring đủ gần production để boundary không còn là khái niệm mơ hồ.

### Basic: declare a component

```java
// ClockProvider.java — Simple dependency managed by Spring container
package com.example.springcore;

import java.time.Clock;
import org.springframework.stereotype.Component;

@Component
public class ClockProvider {
    public Clock systemClock() {
        return Clock.systemUTC();
    }
}
```

ApplicationContext đã cover. Nhưng DI strategies cần constructor injection — hãy refactor.

### Intermediate: constructor injection

```java
// GreetingService.java — Explicit dependency injected through constructor
package com.example.springcore;

import org.springframework.stereotype.Service;

@Service
public class GreetingService {
    private final MessageTemplateRepository messageTemplateRepository;

    public GreetingService(MessageTemplateRepository messageTemplateRepository) {
        this.messageTemplateRepository = messageTemplateRepository;
    }

    public String greet(String name) {
        String template = messageTemplateRepository.loadTemplate("welcome");
        return template.formatted(name);
    }
}
```

Constructor DI đã cover. Nhưng custom BeanPostProcessor cần meta-programming — hãy extend.

### Advanced: inspect container behavior intentionally

```java
// AppContextInspector.java — Controlled lookup for diagnostics or bootstrap logic
package com.example.springcore;

import org.springframework.context.ApplicationContext;
import org.springframework.stereotype.Component;

@Component
public class AppContextInspector {
    private final ApplicationContext applicationContext;

    public AppContextInspector(ApplicationContext applicationContext) {
        this.applicationContext = applicationContext;
    }

    public boolean hasBean(String beanName) {
        return applicationContext.containsBean(beanName);
    }
}
```

Bạn đã đi qua context, DI strategies, và post-processors. Bây giờ đến phần nguy hiểm: circular deps và field injection — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Spring Core — ApplicationContext & Dependency Injection` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Dùng field injection khắp nơi | chuyển sang constructor injection |
| 2 | Lạm dụng `ApplicationContext.getBean()` như service locator | inject dependency trực tiếp thay vì lookup thủ công |
| 3 | Circular dependency giữa services | xem lại boundary và trách nhiệm từng bean |
| 4 | Tự `new` dependency trong business code | để Spring container wire object graph |

Bạn đã đi qua Spring DI và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Spring IoC Container | https://docs.spring.io/spring-framework/reference/core/beans.html |
| Dependency Injection | https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html |
| ApplicationContext Javadoc | https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/context/ApplicationContext.html |

## 6. RECOMMEND

Khi các bẫy chính của `Spring Core — ApplicationContext & Dependency Injection` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Java config | Cần wiring tường minh hơn annotation scan | kiểm soát bean creation rõ hơn |
| Profiles | Bean thay đổi theo environment | tách dev/test/prod behavior |
| Spring Boot auto-config | Muốn dựng app production nhanh hơn | giảm boilerplate configuration |

## 7. QUIZ

### Quick Check

1. Vì sao constructor injection được ưu tiên hơn field injection?
2. `ApplicationContext` quản lý những gì ngoài dependency graph?
3. Khi nào `getBean()` thủ công là dấu hiệu có mùi thiết kế?

### Answer Key

1. Vì dependency explicit, immutable hơn và test dễ hơn.
2. Nó còn quản lý lifecycle, environment, profiles và nhiều infrastructure service khác.
3. Khi business code dùng nó như service locator thay vì inject dependency rõ ràng.

## 8. NEXT STEPS

- Đọc tiếp [Bean Lifecycle & Scopes](../beans/01-bean-lifecycle-scopes-java-config.md)
- Sau đó sang [DispatcherServlet & Controller Flow](../mvc/01-dispatcher-servlet-controller-flow.md)
