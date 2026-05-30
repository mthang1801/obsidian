<!-- tags: java, spring-data -->
# ☕ Spring Data JPA — Entities, Repositories, Transactions

> JPA rất mạnh nhưng cũng dễ khiến project Java trượt sang kiểu “mọi thứ là entity”. Bài này tập trung vào mental model đúng cho entity, repository và transaction boundary trong ứng dụng thật.

📅 Ngày tạo: 2026-03-28 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 16 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Advanced |
| **Use case** | CRUD + business flow dùng database quan hệ |
| **Java focus** | entity mapping, repository, transactional service |
| **Prerequisites** | Spring Boot basics, REST API basics |

## 1. DEFINE

Hình dung bạn chỉ muốn lưu một aggregate bằng JPA, nhưng rồi lazy loading, dirty checking và transaction scope bắt đầu ảnh hưởng đến cả cách bạn viết use case. JPA dễ tạo cảm giác thuận tay, và cũng vì thế rất dễ che mất cái giá thật của persistence boundary.

Bài này không cố làm JPA trông đơn giản hơn. Nó cố làm những điểm khó của nó trở nên nhìn thấy được sớm hơn.

### Entity nên là gì?

Entity JPA là model persistence có lifecycle gắn với ORM context. Nó không nhất thiết là domain model hoàn hảo, và càng không nên bị lạm dụng làm DTO cho API.

### Actors

| Actor | Vai trò |
| --- | --- |
| Entity | mapping object sang bảng DB |
| Repository | abstraction truy cập persistence |
| Transaction | boundary đảm bảo unit of work |
| Service | phối hợp business use case |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Lazy loading nổ ngoài transaction | đọc graph sai chỗ | fetch có chủ đích hoặc map DTO trong transaction |
| Entity phình thành “god object” | nhét logic web/API vào persistence model | giữ entity tập trung vào state + rules gần dữ liệu |
| Transaction quá rộng | ôm cả remote call vào một transaction DB | chỉ giữ boundary quanh database work |

Các failure mode trên nghe quen. Nhưng có trap: N+1 query với eager fetching = DB overload, và missing @Transactional = dirty read. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Với Spring Data JPA — Entities, Repositories, Transactions, phần khó không nằm ở tên annotation hay package nữa mà ở flow thật của request, bean hoặc boundary. Sơ đồ dưới đây giúp kéo flow đó ra ánh sáng.

```text
Controller
   │
   ▼
Transactional service
   │
   ├── load entity
   ├── apply business rule
   └── persist change
   ▼
Database
```

## 3. CODE

Sơ đồ đã cho bạn thấy flow của Spring Data JPA — Entities, Repositories, Transactions. Bây giờ ta chuyển nó thành code Java/Spring đủ gần production để boundary không còn là khái niệm mơ hồ.

### Basic: entity + repository

```java
// CustomerEntity.java — Persistence model for customer table
package com.example.customer.persistence;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "customers")
public class CustomerEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, unique = true)
    private String email;

    protected CustomerEntity() {
    }

    public CustomerEntity(String name, String email) {
        this.name = name;
        this.email = email;
    }

    public Long getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getEmail() {
        return email;
    }
}
```

```java
// CustomerRepository.java — Repository abstraction for aggregate persistence
package com.example.customer.persistence;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CustomerRepository extends JpaRepository<CustomerEntity, Long> {
    Optional<CustomerEntity> findByEmail(String email);
}
```

Entity basics đã cover. Nhưng repositories cần custom queries — hãy extend.

### Intermediate: transactional service

```java
// CustomerRegistrationService.java — Keep transaction at application boundary
package com.example.customer.application;

import com.example.customer.persistence.CustomerEntity;
import com.example.customer.persistence.CustomerRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class CustomerRegistrationService {
    private final CustomerRepository repository;

    public CustomerRegistrationService(CustomerRepository repository) {
        this.repository = repository;
    }

    @Transactional
    public Long register(String name, String email) {
        repository.findByEmail(email).ifPresent(existing -> {
            throw new IllegalArgumentException("email already exists");
        });

        CustomerEntity entity = repository.save(new CustomerEntity(name, email));
        return entity.getId();
    }
}
```

Repositories đã cover. Nhưng transaction propagation cần isolation levels — hãy tune.

### Advanced: transaction boundary checklist

```text
good transaction:
  - begins near use case
  - wraps DB reads/writes that belong together
  - does not include long-running remote HTTP calls

warning signs:
  - entity returned directly to controller and lazily traversed later
  - repository called from many layers without one clear owner
```

Bạn đã đi qua entities, repositories, và transactions. Bây giờ đến phần nguy hiểm: N+1 queries và missing transactions — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Spring Data JPA — Entities, Repositories, Transactions` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Expose entity trực tiếp ra API | map sang response DTO |
| 2 | Transaction bao cả remote call | tách remote orchestration khỏi DB transaction |
| 3 | Dùng repository như utility global | đặt ownership ở application/service rõ ràng |
| 4 | Ignore lazy loading boundaries | fetch có chủ đích hoặc convert trong transaction |

Bạn đã đi qua Spring Data JPA và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Spring Data JPA Reference | https://docs.spring.io/spring-data/jpa/reference/ |
| Jakarta Persistence Spec | https://jakarta.ee/specifications/persistence/ |
| Spring Transaction Management | https://docs.spring.io/spring-framework/reference/data-access/transaction.html |

## 6. RECOMMEND

Khi các bẫy chính của `Spring Data JPA — Entities, Repositories, Transactions` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Query projection | API list/read-heavy | Giảm load entity không cần thiết |
| Outbox pattern | Có side effect qua message broker | Tránh inconsistency giữa DB và messaging |
| Aggregate boundary review | Domain phức tạp | Giảm transaction bừa bãi |

## 7. QUIZ

### Quick Check

1. Vì sao entity JPA không nên làm API DTO?
2. Transaction nên bắt đầu gần đâu?
3. Lazy loading hay gây lỗi ở tình huống nào?

### Answer Key

1. Vì entity là model persistence, không phải contract public.
2. Gần application use case nơi DB work thực sự được điều phối.
3. Khi truy cập association ngoài transaction hoặc persistence context.

## 8. NEXT STEPS

- Nối với `architecture/hexagonal` để tách rõ persistence adapter và core use case
- Hoặc sang `testing/testcontainers` để test JPA flow với DB thật
