<!-- tags: java, testing, junit -->
# ☕ Java Testing — JUnit 5 Essentials

> Đây là điểm vào của testing trong Java. Mục tiêu là viết unit test gọn, đọc được, kiểm tra hành vi rõ ràng thay vì tạo test dài và mong manh.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 14 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Intermediate |
| **Use case** | Unit test service, utility, value object |
| **Java focus** | JUnit 5, assertions, lifecycle, parameterized tests |
| **Prerequisites** | Java basics, class/record |

## 1. DEFINE

Hình dung bạn đang sửa một bug nhỏ nhưng test hiện tại hoặc quá ít để giữ hành vi, hoặc quá rối để nói rõ mình đang bảo vệ điều gì. JUnit 5 chỉ thật sự đáng học khi test không còn là nghi thức bắt buộc, mà là công cụ để làm feedback loop sắc và nhanh hơn.

Bài này đặt `Java Testing — JUnit 5 Essentials` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### JUnit 5 dùng để làm gì?

JUnit 5 là test platform phổ biến cho Java hiện đại. Nó cho phép:

- tổ chức test theo method/nested class
- chạy assertion rõ nghĩa
- dùng parameterized tests để giảm duplication
- giữ unit test nhỏ, nhanh, và tập trung vào hành vi

### Actors

| Actor | Vai trò |
| --- | --- |
| `@Test` | Đánh dấu test case chuẩn |
| `Assertions` | Kiểm tra expected behavior |
| `@BeforeEach` | Setup state trước từng test |
| `@ParameterizedTest` | Chạy cùng logic với nhiều input |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Test khó đọc | Setup lẫn với assert | Tách arrange / act / assert |
| Một test ôm quá nhiều scenario | Muốn “tiện” | Dùng nested test hoặc parameterized test |
| Assertion mơ hồ | Chỉ check boolean chung chung | Dùng assertion cụ thể, message rõ |

Các failure mode trên nghe dễ tránh. Nhưng có trap: test method order dependency = flaky tests, và @BeforeAll non-static = extension error. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa mới chỉ khóa được tên của Java Testing — JUnit 5 Essentials. Để khái niệm này bớt trừu tượng, ta cần nhìn nó ở dạng flow hoặc cấu trúc đủ cụ thể trước.

```text
Arrange
  │
  ▼
Act
  │
  ▼
Assert
```

```text
JUnit 5 test class
   ├── @BeforeEach
   ├── @Test
   ├── @Nested
   └── @ParameterizedTest
```

## 3. CODE

Flow của Java Testing — JUnit 5 Essentials đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: simple assertion

```java
// PriceCalculatorTest.java — Basic JUnit 5 assertion example
import java.math.BigDecimal;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class PriceCalculatorTest {
    @Test
    void shouldCalculateDiscountedPrice() {
        BigDecimal result = PriceCalculator.discounted(
                new BigDecimal("100.00"),
                new BigDecimal("0.10")
        );

        Assertions.assertEquals(new BigDecimal("90.00"), result);
    }
}
```

Basic assertions đã cover. Nhưng parameterized tests cần @MethodSource — hãy data-drive.

### Intermediate: lifecycle + nested test

```java
// LoyaltyServiceTest.java — Nested tests make scenarios easier to scan
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class LoyaltyServiceTest {
    private LoyaltyService loyaltyService;

    @BeforeEach
    void setUp() {
        loyaltyService = new LoyaltyService();
    }

    @Nested
    class RewardPoints {
        @Test
        void shouldAddPointsForPositivePurchase() {
            int points = loyaltyService.reward(250_000);
            Assertions.assertEquals(25, points);
        }

        @Test
        void shouldRejectNegativePurchase() {
            IllegalArgumentException error = Assertions.assertThrows(
                    IllegalArgumentException.class,
                    () -> loyaltyService.reward(-1)
            );
            Assertions.assertEquals("purchaseAmount must be non-negative", error.getMessage());
        }
    }
}
```

Parameterized đã cover. Nhưng extensions cần lifecycle callbacks — hãy customize.

### Advanced: parameterized test

```java
// PasswordPolicyTest.java — Parameterized test for validation matrix
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class PasswordPolicyTest {
    @ParameterizedTest
    @CsvSource({
            "abc, false",
            "password123, true",
            "'', false",
            "StrongPass99, true"
    })
    void shouldValidatePasswordStrength(String input, boolean expected) {
        boolean result = PasswordPolicy.isAcceptable(input);
        Assertions.assertEquals(expected, result);
    }
}
```

Bạn đã đi qua assertions, parameterized, và extensions. Bây giờ đến phần nguy hiểm: order dependency và lifecycle misuse — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Testing — JUnit 5 Essentials` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Một test assert quá nhiều thứ không liên quan | Chia nhỏ theo behavior |
| 2 | Reuse mutable shared state giữa test cases | Setup lại bằng `@BeforeEach` |
| 3 | Không test exception message/contract khi cần | Dùng `assertThrows` rồi check tiếp |
| 4 | Copy-paste cùng một test cho nhiều input | Dùng `@ParameterizedTest` |

Bạn đã đi qua JUnit 5 và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| JUnit 5 User Guide | https://junit.org/junit5/docs/current/user-guide/ |
| Assertions API | https://junit.org/junit5/docs/current/api/org.junit.jupiter.api/org/junit/jupiter/api/Assertions.html |
| Parameterized Tests | https://junit.org/junit5/docs/current/user-guide/#writing-tests-parameterized-tests |

## 6. RECOMMEND

Khi các bẫy chính của `Java Testing — JUnit 5 Essentials` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Mockito | Có dependency cần stub/verify | Unit test service dễ hơn |
| Testcontainers | Cần integration test thật | Gần production hơn |
| `@WebMvcTest` | Test web layer | Không cần boot full app |

## 7. QUIZ

### Quick Check

1. Khi nào `@ParameterizedTest` tốt hơn nhiều `@Test` gần giống nhau?
2. Vì sao `@BeforeEach` an toàn hơn shared mutable fixture?
3. `assertThrows` giúp kiểm tra được gì ngoài việc “có lỗi”?

### Answer Key

1. Khi cùng một hành vi cần được verify trên nhiều input khác nhau.
2. Vì mỗi test chạy trên state sạch, giảm coupling và flaky test.
3. Nó cho phép kiểm tra loại exception và cả message/contract chi tiết.

## 8. NEXT STEPS

- Seed tiếp `mockito/` nếu cần test service có dependency
- Hoặc sang Spring Boot test slices để test controller/repository
