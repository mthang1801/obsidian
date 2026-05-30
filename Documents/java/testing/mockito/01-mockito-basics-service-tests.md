<!-- tags: java, testing -->
# ☕ Java Testing — Mockito Basics for Service Tests

> Mockito giúp cô lập dependency khi unit test service. Mục tiêu của bài này là mock đúng chỗ, verify đúng interaction, và tránh biến unit test thành một bản sao của implementation.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 14 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Intermediate |
| **Use case** | Test service có repository, client hoặc publisher dependency |
| **Java focus** | Mockito, stubbing, verification, interaction testing |
| **Prerequisites** | JUnit 5 essentials |

## 1. DEFINE

Hình dung một service test cần tách business decision khỏi gateway ngoài, nhưng chỉ cần mock hơi quá tay là test bắt đầu xác nhận implementation detail thay vì behavior. Mockito đáng học ở đúng ranh giới mong manh giữa kiểm soát dependency và tự nhốt mình vào test giòn gãy.

Bài này đặt `Java Testing — Mockito Basics for Service Tests` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Mockito nên dùng khi nào?

Mockito phù hợp khi:

- object đang test phụ thuộc vào collaborator bên ngoài
- collaborator đó không cần chạy thật trong unit test
- ta muốn kiểm tra contract tương tác thay vì boot nguyên context

### Actors

| Actor | Vai trò |
| --- | --- |
| Mock | Test double thay cho dependency thật |
| Stub | Định nghĩa mock sẽ trả gì khi được gọi |
| Verify | Kiểm tra dependency có được gọi đúng cách không |
| Service under test | Object chứa business logic cần kiểm tra |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Over-mocking | Mock cả những gì không cần | Chỉ mock boundary collaborator |
| Verify quá chi tiết | Test phụ thuộc implementation | Verify interaction thật sự có ý nghĩa |
| Stub dư thừa | Copy-paste setup | Chỉ stub những branch đang dùng |

Các failure mode trên nghe cơ bản. Nhưng có trap: mock final class = MockitoException, và verify order dependency = brittle tests. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa mới chỉ khóa được tên của Java Testing — Mockito Basics for Service Tests. Để khái niệm này bớt trừu tượng, ta cần nhìn nó ở dạng flow hoặc cấu trúc đủ cụ thể trước.

```text
test
  │
  ├── create mock repository
  ├── inject into service
  ├── stub repository result
  ├── call service method
  └── verify outcome + interaction
```

```text
Service under test
   │
   ├── Repository  -> mocked
   └── Event bus   -> mocked
```

## 3. CODE

Flow của Java Testing — Mockito Basics for Service Tests đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: stub a repository call

```java
// CustomerLookupServiceTest.java — Stub repository response with Mockito
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.when;

import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

class CustomerLookupServiceTest {
    @Test
    void shouldReturnCustomerName() {
        CustomerRepository repository = Mockito.mock(CustomerRepository.class);
        when(repository.findById(10L)).thenReturn(Optional.of(new Customer(10L, "Alice")));

        CustomerLookupService service = new CustomerLookupService(repository);
        String result = service.lookupName(10L);

        assertEquals("Alice", result);
    }

    interface CustomerRepository {
        Optional<Customer> findById(long id);
    }

    record Customer(long id, String name) {
    }

    static final class CustomerLookupService {
        private final CustomerRepository repository;

        CustomerLookupService(CustomerRepository repository) {
            this.repository = repository;
        }

        String lookupName(long id) {
            return repository.findById(id)
                    .map(Customer::name)
                    .orElse("unknown");
        }
    }
}
```

Mock basics đã cover. Nhưng argument matchers cần any/eq — hãy flexible.

### Intermediate: verify interaction with one collaborator

```java
// OrderApplicationServiceTest.java — Verify side effects on collaborators
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import org.junit.jupiter.api.Test;

class OrderApplicationServiceTest {
    @Test
    void shouldPublishEventAfterCreatingOrder() {
        OrderRepository repository = mock(OrderRepository.class);
        OrderEventPublisher eventPublisher = mock(OrderEventPublisher.class);

        Order draft = new Order(101L, "draft");
        when(repository.saveDraft(77L)).thenReturn(draft);

        OrderApplicationService service = new OrderApplicationService(repository, eventPublisher);
        Order result = service.create(77L);

        assertEquals(101L, result.id());
        verify(repository).saveDraft(77L);
        verify(eventPublisher).publishCreated(draft);
    }

    interface OrderRepository {
        Order saveDraft(long customerId);
    }

    interface OrderEventPublisher {
        void publishCreated(Order order);
    }

    record Order(long id, String status) {
    }

    static final class OrderApplicationService {
        private final OrderRepository repository;
        private final OrderEventPublisher eventPublisher;

        OrderApplicationService(OrderRepository repository, OrderEventPublisher eventPublisher) {
            this.repository = repository;
            this.eventPublisher = eventPublisher;
        }

        Order create(long customerId) {
            Order order = repository.saveDraft(customerId);
            eventPublisher.publishCreated(order);
            return order;
        }
    }
}
```

Matchers đã cover. Nhưng spy vs mock cần partial mocking — hãy choose.

### Advanced: avoid brittle verification

```java
// PasswordResetServiceTest.java — Verify only meaningful interaction boundaries
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.Optional;
import org.junit.jupiter.api.Test;

class PasswordResetServiceTest {
    @Test
    void shouldNotSendResetTokenWhenUserDoesNotExist() {
        UserRepository userRepository = mock(UserRepository.class);
        Mailer mailer = mock(Mailer.class);
        when(userRepository.findByEmail("nobody@example.com")).thenReturn(Optional.empty());

        PasswordResetService service = new PasswordResetService(userRepository, mailer);

        assertThrows(IllegalArgumentException.class, () -> service.reset("nobody@example.com"));
        verify(mailer, never()).send(anyString(), anyString());
    }

    interface UserRepository {
        Optional<User> findByEmail(String email);
    }

    interface Mailer {
        void send(String recipient, String body);
    }

    record User(String email) {
    }

    static final class PasswordResetService {
        private final UserRepository userRepository;
        private final Mailer mailer;

        PasswordResetService(UserRepository userRepository, Mailer mailer) {
            this.userRepository = userRepository;
            this.mailer = mailer;
        }

        void reset(String email) {
            User user = userRepository.findByEmail(email)
                    .orElseThrow(() -> new IllegalArgumentException("user not found"));
            mailer.send(user.email(), "reset-token");
        }
    }
}
```

Bạn đã đi qua mocks, matchers, và spies. Bây giờ đến phần nguy hiểm: final class mock và verify order — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Testing — Mockito Basics for Service Tests` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Mock cả value object hoặc logic thuần | Chỉ mock external collaborators |
| 2 | Verify mọi method call nhỏ | Verify behavior/side effect có ý nghĩa |
| 3 | Dùng Mockito để che thiết kế khó test | Refactor constructor injection và interface nhỏ |
| 4 | Stub quá nhiều branch không dùng | Tối giản setup theo test case |

Bạn đã đi qua Mockito và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Mockito Documentation | https://site.mockito.org/ |
| Mockito Javadoc | https://javadoc.io/doc/org.mockito/mockito-core/latest/org.mockito/org/mockito/Mockito.html |
| Mockito JUnit Jupiter | https://javadoc.io/doc/org.mockito/mockito-junit-jupiter/latest/index.html |

## 6. RECOMMEND

Khi các bẫy chính của `Java Testing — Mockito Basics for Service Tests` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Mockito extension | Muốn setup gọn hơn | Giảm boilerplate |
| Testcontainers | Dependency cần chạy thật | Chuyển sang integration test |
| Contract tests | External client quan trọng | Giảm lệ thuộc vào mock assumptions |

## 7. QUIZ

### Quick Check

1. Khi nào nên dùng Mockito thay vì dependency thật?
2. Vì sao verify quá chi tiết làm test brittle?
3. Dấu hiệu nào cho thấy bạn đang over-mocking?

### Answer Key

1. Khi dependency là boundary bên ngoài và không cần chạy thật trong unit test.
2. Vì test sẽ fail khi implementation đổi nhỏ dù behavior bên ngoài không đổi.
3. Khi cả value object hoặc logic nội bộ đơn giản cũng bị mock thay vì dùng thật.

## 8. NEXT STEPS

- Sang `integration/` nếu muốn test nhiều lớp cùng lúc
- Hoặc nối với Spring Boot web/config để test flow ứng dụng rõ hơn
