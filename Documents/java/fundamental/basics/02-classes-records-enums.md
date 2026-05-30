<!-- tags: java, fundamentals, oop -->
# ☕ Java Basics — Classes, Records & Enums

> Bài này giúp phân biệt ba khối xây dựng rất hay gặp trong Java backend: class truyền thống, `record` cho immutable data, và `enum` cho domain state hữu hạn.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 12 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Basic → Intermediate |
| **Use case** | Model request, response, config, workflow state |
| **Java focus** | class, constructor, `record`, `enum` |
| **Prerequisites** | `01-syntax-control-flow.md` |

## 1. DEFINE

Hình dung bạn đang quyết định một kiểu dữ liệu mới trong Java: nên là class, record hay enum. Quyết định trông rất nhỏ, cho tới khi serialization, equality, domain meaning và khả năng mở rộng bắt đầu phụ thuộc vào nó. Bài này mở ở đúng lúc kiểu dữ liệu không còn là chuyện cú pháp.

Bài này đặt `Java Basics — Classes, Records & Enums` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Phân biệt nhanh

| Type | Khi dùng | Điểm mạnh |
| --- | --- | --- |
| `class` | Object có state + behavior thay đổi được | Linh hoạt nhất |
| `record` | DTO, event, value object bất biến | Gọn, rõ, auto `equals/hashCode` |
| `enum` | Trạng thái hoặc tập giá trị cố định | Type-safe hơn string |

### Invariants

| Quy tắc | Ý nghĩa |
| --- | --- |
| `record` nên đại diện dữ liệu bất biến | Tránh lạm dụng cho object nhiều behavior |
| `enum` chỉ dùng cho tập giá trị hữu hạn ổn định | Không dùng thay table config động |
| Constructor nên bảo vệ object khỏi invalid state | Fail fast từ đầu |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Class có quá nhiều setter | Mutable state lan rộng | Dùng constructor/record |
| Dùng string cho status | Dễ typo, khó refactor | Chuyển sang enum |
| Record chứa business logic phức tạp | Sai abstraction | Tách sang service/value object phù hợp |

Các failure mode trên nghe rõ. Nhưng có trap: record component mutable = immutability vỡ, và enum comparator dùng equals thay == = style inconsistent. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa mới chỉ khóa được tên của Java Basics — Classes, Records & Enums. Để khái niệm này bớt trừu tượng, ta cần nhìn nó ở dạng flow hoặc cấu trúc đủ cụ thể trước.

```text
Domain model choices

mutable behavior-heavy object    ──▶ class
immutable transport/value data   ──▶ record
finite workflow states           ──▶ enum
```

```text
OrderStatus
PENDING ──▶ PAID ──▶ PACKING ──▶ SHIPPED
   │
   └────────────▶ CANCELLED
```

## 3. CODE

Flow của Java Basics — Classes, Records & Enums đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: class with constructor guards

```java
// CustomerAccount.java — Class with constructor validation and behavior
public final class CustomerAccount {
    private final String email;
    private int loyaltyPoints;

    /**
     * Creates an account with a validated email.
     *
     * @param email customer email
     */
    public CustomerAccount(String email) {
        if (email == null || email.isBlank()) {
            throw new IllegalArgumentException("email must not be blank");
        }
        this.email = email;
        this.loyaltyPoints = 0;
    }

    public String email() {
        return email;
    }

    public int loyaltyPoints() {
        return loyaltyPoints;
    }

    public void reward(int points) {
        if (points <= 0) {
            throw new IllegalArgumentException("points must be positive");
        }
        this.loyaltyPoints += points;
    }
}
```

Class basics đã cover. Nhưng records cần immutability — hãy dùng.

### Intermediate: record for request/value data

```java
// CreateOrderCommand.java — Record for immutable request data
import java.math.BigDecimal;

/**
 * Immutable command object for order creation.
 *
 * @param customerId customer identifier
 * @param sku product SKU
 * @param amount order amount
 */
public record CreateOrderCommand(long customerId, String sku, BigDecimal amount) {
    public CreateOrderCommand {
        if (customerId <= 0) {
            throw new IllegalArgumentException("customerId must be positive");
        }
        if (sku == null || sku.isBlank()) {
            throw new IllegalArgumentException("sku must not be blank");
        }
        if (amount == null || amount.signum() <= 0) {
            throw new IllegalArgumentException("amount must be positive");
        }
    }
}
```

Records đã cover. Nhưng sealed types cần hierarchy control — hãy seal.

### Advanced: enum with transition logic

```java
// OrderStatus.java — Enum with domain transition rules
public enum OrderStatus {
    PENDING,
    PAID,
    PACKING,
    SHIPPED,
    CANCELLED;

    /**
     * Validates if current status can move to the target status.
     *
     * @param target target status
     * @return true when transition is allowed
     */
    public boolean canMoveTo(OrderStatus target) {
        return switch (this) {
            case PENDING -> target == PAID || target == CANCELLED;
            case PAID -> target == PACKING || target == CANCELLED;
            case PACKING -> target == SHIPPED;
            case SHIPPED, CANCELLED -> false;
        };
    }
}
```

Bạn đã đi qua classes, records, và sealed types. Bây giờ đến phần nguy hiểm: mutable records và enum comparison — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Basics — Classes, Records & Enums` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Dùng `record` cho entity mutable | Chỉ dùng record cho immutable DTO/value object |
| 2 | Enum chỉ giữ name nhưng không có behavior | Đẩy rule transition vào enum khi hợp lý |
| 3 | Constructor không validate input | Chặn invalid state ngay khi khởi tạo |
| 4 | Expose setter cho mọi field | Giảm mutability, chỉ mở hành vi cần thiết |

Bạn đã đi qua Classes & Records và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Records | https://docs.oracle.com/en/java/javase/21/language/records.html |
| Enums | https://docs.oracle.com/javase/tutorial/java/javaOO/enum.html |
| Classes and Objects | https://docs.oracle.com/javase/tutorial/java/javaOO/classes.html |

## 6. RECOMMEND

Khi các bẫy chính của `Java Basics — Classes, Records & Enums` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Sealed classes | Có hierarchy giới hạn | Model state rõ hơn |
| Bean Validation | Validate DTO ở web layer | Tách validation khỏi controller |
| Jackson | Serialize record/class thành JSON | Phục vụ API |

## 7. QUIZ

### Quick Check

1. Khi nào `record` phù hợp hơn `class`?
2. Vì sao `enum` tốt hơn `String` cho status?
3. Validation nên nằm ở đâu để object khó rơi vào invalid state?

### Answer Key

1. Khi dữ liệu immutable, chủ yếu là DTO hoặc value object.
2. Vì enum type-safe, ít typo, dễ refactor và có thể chứa behavior.
3. Ở constructor hoặc canonical constructor của record.

## 8. NEXT STEPS

- Tiếp tục với [List, Set & Map](../collections/01-list-set-map.md)
- Sau đó chuyển qua Spring Boot để thấy các type này xuất hiện trong web/backend
