<!-- tags: java, architecture -->
# ☕ Java Architecture — Ports, Adapters, Service Boundaries

> Hexagonal architecture hữu ích khi project Java bắt đầu phình to vì framework, ORM và integration code lấn át business logic. Mục tiêu không phải “vẽ hình đẹp”, mà là giữ core use case đủ độc lập để thay adapter mà không đập cả hệ thống.

📅 Ngày tạo: 2026-03-28 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 15 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Expert |
| **Use case** | Java backend có nhiều integration và muốn giữ core ổn định |
| **Java focus** | ports, adapters, application service, dependency direction |
| **Prerequisites** | backend basics, JPA basics |

## 1. DEFINE

Hình dung bạn đang cố gắng thay gateway thanh toán trong một service Java đã sống vài năm. Business rule thì vẫn phải giữ nguyên, nhưng chỉ một thay đổi ở adapter ngoài cũng đủ kéo theo controller, service và test vỡ dây chuyền. Chính lúc đó câu hỏi về ports và adapters mới trở nên thật: làm sao để boundary ứng dụng giữ được hình dạng của nó khi thế giới bên ngoài đổi ý liên tục?

Bài này đặt `Java Architecture — Ports, Adapters, Service Boundaries` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Hexagonal architecture là gì?

Hexagonal architecture tách hệ thống thành:

- core business/use cases
- inbound adapters nhận request
- outbound adapters gọi DB, queue, HTTP service khác

Dependency direction luôn hướng vào core qua abstractions.

### Actors

| Actor | Vai trò |
| --- | --- |
| Inbound adapter | controller, message consumer, CLI entrypoint |
| Application service | điều phối use case |
| Port | abstraction giữa core với bên ngoài |
| Outbound adapter | JPA repository adapter, HTTP client adapter |

### Invariants

| Quy tắc | Ý nghĩa |
| --- | --- |
| Core không phụ thuộc framework chi tiết | dễ test và dễ thay adapter |
| Port phản ánh nhu cầu use case | tránh abstraction quá chung chung |
| Adapter chịu trách nhiệm translate data | không đẩy chi tiết infra vào core |

Các failure mode trên nghe quen. Nhưng có trap: adapter leak vào domain = dependency rule vỡ, và port interface quá fat = violation ISP. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa mới chỉ khóa được tên của Java Architecture — Ports, Adapters, Service Boundaries. Để khái niệm này bớt trừu tượng, ta cần nhìn nó ở dạng flow hoặc cấu trúc đủ cụ thể trước.

```text
HTTP Controller / Consumer
          │
          ▼
   Application Service
      │          │
      │ uses     │ uses
      ▼          ▼
  CustomerPort  MailPort
      │            │
      ▼            ▼
 JPA Adapter   SMTP/HTTP Adapter
```

## 3. CODE

Flow của Java Architecture — Ports, Adapters, Service Boundaries đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: define a port

```java
// CustomerStore.java — Outbound port owned by the application core
package com.example.customer.application.port;

import java.util.Optional;

public interface CustomerStore {
    Optional<CustomerRecord> findByEmail(String email);

    CustomerRecord save(CustomerRecord record);
}
```

```java
// CustomerRecord.java — Data shape the core actually needs
package com.example.customer.application.port;

public record CustomerRecord(Long id, String name, String email) {
}
```

Ports & adapters đã cover. Nhưng service boundaries cần module isolation — hãy chia.

### Intermediate: application service depends on port

```java
// RegisterCustomerUseCase.java — Core flow independent from JPA details
package com.example.customer.application;

import com.example.customer.application.port.CustomerRecord;
import com.example.customer.application.port.CustomerStore;

public class RegisterCustomerUseCase {
    private final CustomerStore customerStore;

    public RegisterCustomerUseCase(CustomerStore customerStore) {
        this.customerStore = customerStore;
    }

    public Long execute(String name, String email) {
        customerStore.findByEmail(email).ifPresent(existing -> {
            throw new IllegalArgumentException("email already exists");
        });

        CustomerRecord saved = customerStore.save(new CustomerRecord(null, name, email));
        return saved.id();
    }
}
```

Service boundaries đã cover. Nhưng test doubles cần port mocking — hãy inject.

### Advanced: outbound adapter implements the port

```java
// JpaCustomerStore.java — Adapter translating between JPA entity and application port
package com.example.customer.infrastructure.persistence;

import com.example.customer.application.port.CustomerRecord;
import com.example.customer.application.port.CustomerStore;
import java.util.Optional;
import org.springframework.stereotype.Component;

@Component
public class JpaCustomerStore implements CustomerStore {
    private final SpringDataCustomerRepository repository;

    public JpaCustomerStore(SpringDataCustomerRepository repository) {
        this.repository = repository;
    }

    @Override
    public Optional<CustomerRecord> findByEmail(String email) {
        return repository.findByEmail(email)
                .map(entity -> new CustomerRecord(entity.getId(), entity.getName(), entity.getEmail()));
    }

    @Override
    public CustomerRecord save(CustomerRecord record) {
        CustomerEntity saved = repository.save(new CustomerEntity(record.name(), record.email()));
        return new CustomerRecord(saved.getId(), saved.getName(), saved.getEmail());
    }
}
```

Bạn đã đi qua ports, boundaries, và test doubles. Bây giờ đến phần nguy hiểm: adapter leak và fat port — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Architecture — Ports, Adapters, Service Boundaries` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Tạo quá nhiều port generic kiểu CRUD toàn cục | để port bám sát use case cụ thể |
| 2 | Core vẫn import annotation framework | giữ framework ở adapter/config layer |
| 3 | Adapter leak entity vào core | translate data shape tại biên adapter |
| 4 | Áp hexagonal quá hình thức | chỉ dùng nơi boundary và dependency direction thực sự có giá trị |

Bạn đã đi qua Hexagonal Architecture và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Hexagonal Architecture overview | https://alistair.cockburn.us/hexagonal-architecture/ |
| Spring documentation | https://docs.spring.io/spring-framework/reference/ |
| Domain-Driven Design Reference | https://www.domainlanguage.com/ddd/reference/ |

## 6. RECOMMEND

Khi các bẫy chính của `Java Architecture — Ports, Adapters, Service Boundaries` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Package-by-feature | Module business bắt đầu nhiều flow | boundary rõ hơn package-by-layer |
| Integration tests per adapter | Có DB, broker, HTTP client | verify adapter contract thực tế |
| Outbox / anti-corruption layer | Hệ thống tích hợp ngoài nhiều | cô lập coupling tốt hơn |

## 7. QUIZ

### Quick Check

1. Port nên do core hay adapter sở hữu?
2. Vì sao hexagonal không đồng nghĩa với tạo vô số interface?
3. Adapter nên làm gì với entity/DTO/framework model?

### Answer Key

1. Port nên phản ánh nhu cầu của core/use case.
2. Vì abstraction chỉ có giá trị khi nó phục vụ boundary thật, không phải vì hình thức.
3. Adapter nên translate chúng sang shape mà core cần.

## 8. NEXT STEPS

- Nối với `spring-data/jpa` để xem adapter persistence cụ thể hơn
- Hoặc sang `expert/observability` để bổ sung tracing qua các boundary
