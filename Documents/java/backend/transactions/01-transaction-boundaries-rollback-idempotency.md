<!-- tags: java, backend -->
# ☕ Java Backend — Transaction Boundaries, Rollback, Idempotency

> Một transaction tốt không phải transaction dài nhất, mà là transaction đúng boundary nhất. Khi kết hợp database write với HTTP call, queue publish hoặc retry từ client, việc hiểu rollback semantics và idempotency trở nên rất quan trọng.

📅 Ngày tạo: 2026-03-28 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 15 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Expert |
| **Use case** | Business flow có DB write, retry và side effects |
| **Java focus** | `@Transactional`, rollback rule, remote call boundary |
| **Prerequisites** | Spring Boot basics, JPA basics |

## 1. DEFINE

Hình dung một lệnh thanh toán chạy gần xong thì downstream timeout. Bạn không chắc database đã commit tới đâu, không chắc retry có tạo double charge hay không, và càng không chắc rollback hiện tại có thực sự bảo vệ được business invariant. Transaction boundary chỉ trở nên đáng học ở chính khoảnh khắc mơ hồ đó.

Bài này được viết cho chính khoảnh khắc biên đó bắt đầu mờ đi.

### Transaction boundary nên bao gì?

Nó nên bao tập các DB operations phải thành công hoặc thất bại cùng nhau. Không nên ôm các remote operation dài hoặc không thể rollback bằng DB transaction.

### Invariants

| Quy tắc | Ý nghĩa |
| --- | --- |
| DB transaction chỉ bảo vệ resource manager mà nó kiểm soát | không tự rollback HTTP call hay email |
| Retry từ client là thực tế bình thường | flow quan trọng cần idempotent |
| Rollback rules phải rõ | tránh nghĩ sai exception nào rollback |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Publish event rồi DB rollback | side effect ngoài transaction | dùng outbox hoặc publish sau commit |
| Remote call treo trong transaction | giữ connection/lock quá lâu | tách remote boundary |
| Retry tạo duplicate data | thiếu idempotency key/business constraint | thêm uniqueness hoặc request key |

Các failure mode trên nghe dễ tránh. Nhưng có trap: @Transactional trên private method = no proxy = no rollback, và checked exception không rollback by default. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa mới chỉ khóa được tên của Java Backend — Transaction Boundaries, Rollback, Idempotency. Để khái niệm này bớt trừu tượng, ta cần nhìn nó ở dạng flow hoặc cấu trúc đủ cụ thể trước.

```text
request
   │
   ▼
open DB transaction
   │
   ├── read/write database
   ├── commit
   └── after commit -> publish event / call external system
```

## 3. CODE

Khi boundary của Java Backend — Transaction Boundaries, Rollback, Idempotency đã rõ trên sơ đồ, phần còn lại là đưa nó vào code sao cho những quyết định đúng không chỉ tồn tại trên slide mà tồn tại trong class và method thật.

### Basic: transaction quanh DB work

```java
// TransferService.java — Keep database updates inside one transaction boundary
package com.example.payment.application;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class TransferService {
    private final AccountRepository accountRepository;

    public TransferService(AccountRepository accountRepository) {
        this.accountRepository = accountRepository;
    }

    @Transactional
    public void transfer(long fromId, long toId, long amount) {
        Account from = accountRepository.load(fromId);
        Account to = accountRepository.load(toId);

        from.debit(amount);
        to.credit(amount);
    }
}
```

Transaction basics đã cover. Nhưng rollback rules cần exception mapping — hãy config.

### Intermediate: remote call should stay outside DB transaction

```java
// OrderApplicationService.java — Commit DB state before notifying external systems
package com.example.order.application;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class OrderApplicationService {
    private final OrderRepository orderRepository;
    private final ShippingGateway shippingGateway;

    public OrderApplicationService(OrderRepository orderRepository, ShippingGateway shippingGateway) {
        this.orderRepository = orderRepository;
        this.shippingGateway = shippingGateway;
    }

    @Transactional
    public Long createOrder(CreateOrderCommand command) {
        Order order = Order.create(command.customerId(), command.items());
        orderRepository.save(order);
        return order.getId();
    }

    public void requestShipping(Long orderId) {
        shippingGateway.reserveSlot(orderId);
    }
}
```

Rollback đã cover. Nhưng idempotency cần unique key — hãy guarantee.

### Advanced: idempotency checklist

```text
for retry-safe write APIs:
  1. accept idempotency key or business-unique identifier
  2. check existing successful operation first
  3. keep uniqueness at database level if possible
  4. separate "already processed" from real failure
```

Bạn đã đi qua transactions, rollback, và idempotency. Bây giờ đến phần nguy hiểm: private method proxy miss và checked exception — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Backend — Transaction Boundaries, Rollback, Idempotency` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Gọi HTTP/payment gateway trong DB transaction | tách external call khỏi DB boundary |
| 2 | Tin rằng mọi exception đều rollback như nhau | hiểu rollback rule của framework |
| 3 | Không có uniqueness/idempotency khi client retry | thêm key hoặc constraint |
| 4 | Publish event trước commit | dùng outbox hoặc after-commit hook |

Bạn đã đi qua Transactions và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Spring Transaction Management | https://docs.spring.io/spring-framework/reference/data-access/transaction.html |
| Spring Declarative Transactions | https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative.html |
| Enterprise Integration Patterns | https://www.enterpriseintegrationpatterns.com/ |

## 6. RECOMMEND

Khi các bẫy chính của `Java Backend — Transaction Boundaries, Rollback, Idempotency` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Outbox pattern | Có DB + message broker | giữ consistency tốt hơn |
| Retry policy + backoff | service gọi nhau qua network | giảm blast radius |
| Idempotency table | Public write APIs | xử lý retry rõ ràng hơn |

## 7. QUIZ

### Quick Check

1. Vì sao DB transaction không rollback được HTTP call?
2. Khi nào nên tách side effect sang sau commit?
3. Idempotency khác uniqueness ở điểm nào?

### Answer Key

1. Vì HTTP call là resource bên ngoài DB transaction manager.
2. Khi side effect không thể tham gia cùng DB transaction một cách an toàn.
3. Idempotency xử lý retry ở cấp workflow; uniqueness chỉ chặn trùng ở một constraint cụ thể.

## 8. NEXT STEPS

- Nối với `spring-data/jpa` để thấy transaction gắn với repository/service thế nào
- Hoặc sang `expert/resilience` để xử lý retry, timeout, circuit breaker tốt hơn
