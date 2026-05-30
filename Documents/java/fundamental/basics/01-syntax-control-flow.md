<!-- tags: java, fundamentals -->
# ☕ Java Basics — Syntax & Control Flow

> Bài mở đầu để nắm cú pháp Java hiện đại: variables, methods, conditionals, loops, text blocks và cách tổ chức một chương trình nhỏ nhưng rõ ràng.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 11 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Basic |
| **Use case** | Đọc và viết Java console/service code cơ bản |
| **Java focus** | primitives, `if`, `switch`, loop, method, text block |
| **Prerequisites** | Không |

## 1. DEFINE

Hình dung bạn đang đọc một đoạn Java rất cơ bản, tới mức ai cũng nghĩ không thể sai: vài điều kiện, một vòng lặp, một nhánh `switch`, vài chỗ return sớm. Nhưng chính ở những đoạn tưởng quá quen đó, lỗi logic nhỏ thường lẩn lâu nhất vì không ai cảm thấy cần phải nhìn thật kỹ.

Bài này đặt `Java Basics — Syntax & Control Flow` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Java syntax là gì?

Java là ngôn ngữ strongly-typed, compile-time checked. Điều này có nghĩa:

- kiểu dữ liệu được kiểm tra trước khi chạy
- lỗi về method signature, type mismatch, variable scope thường lộ ra sớm
- code thường verbose hơn scripting languages, nhưng đổi lại dễ bảo trì hơn ở codebase lớn

### Actors

| Actor | Vai trò |
| --- | --- |
| Variable | Lưu state tạm thời hoặc state của object |
| Method | Đóng gói logic tái sử dụng |
| Class | Đơn vị tổ chức hành vi và dữ liệu |
| JVM | Chạy bytecode sau khi compile |

### Invariants

| Quy tắc | Ý nghĩa |
| --- | --- |
| Mọi code thực thi phải nằm trong class | Java không có top-level executable statements như script |
| Kiểu dữ liệu phải tương thích | Không có implicit cast tùy tiện như JavaScript |
| Biến local phải được khởi tạo trước khi đọc | Compiler sẽ chặn |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| `cannot find symbol` | Sai tên biến / method | Đổi đúng identifier hoặc import |
| `incompatible types` | Gán sai kiểu | Cast hợp lệ hoặc đổi type |
| `NullPointerException` | Đọc object đang `null` | Guard clause, default value, constructor chặt hơn |

Các failure mode trên nghe quen. Nhưng có trap: switch expression thiếu exhaustive case = compile error, và text block indent sai = whitespace thừa. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa mới chỉ khóa được tên của Java Basics — Syntax & Control Flow. Để khái niệm này bớt trừu tượng, ta cần nhìn nó ở dạng flow hoặc cấu trúc đủ cụ thể trước.

### Java source to runtime

```text
OrderReport.java
      │
      ▼
javac OrderReport.java
      │
      ▼
OrderReport.class
      │
      ▼
java OrderReport
      │
      ▼
JVM executes bytecode
```

### Control flow mental model

```text
input
  │
  ├── valid? ── no ──▶ return error / fallback
  │
  └── yes
       │
       ├── branch with if / switch
       ├── iterate with for / while
       └── delegate to small methods
```

## 3. CODE

Flow của Java Basics — Syntax & Control Flow đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: variables, methods, text blocks

```java
// OrderSummaryApp.java — Basic Java syntax: variables, methods, text blocks
import java.math.BigDecimal;

public final class OrderSummaryApp {
    private OrderSummaryApp() {
    }

    /**
     * Starts a minimal console flow for order summary rendering.
     *
     * @param args command-line arguments
     */
    public static void main(String[] args) {
        String customer = "Alice";
        int quantity = 3;
        BigDecimal unitPrice = new BigDecimal("19.90");
        BigDecimal total = calculateTotal(quantity, unitPrice);

        String summary = """
                Order summary
                -------------
                Customer : %s
                Quantity : %d
                Total    : %s
                """.formatted(customer, quantity, total);

        System.out.println(summary);
    }

    /**
     * Calculates the order total for a single line item.
     *
     * @param quantity item quantity
     * @param unitPrice unit price
     * @return total price
     */
    public static BigDecimal calculateTotal(int quantity, BigDecimal unitPrice) {
        return unitPrice.multiply(BigDecimal.valueOf(quantity));
    }
}
```

Variables và methods đã cover. Nhưng branching cần switch expression — hãy upgrade.

### Intermediate: branching + switch expression

```java
// ShippingDecision.java — Branching and switch expression for shipping mode
import java.time.DayOfWeek;
import java.time.LocalDate;

public final class ShippingDecision {
    private ShippingDecision() {
    }

    /**
     * Decides the shipping SLA based on order flags and current day.
     *
     * @param express whether customer selected express shipping
     * @param fragile whether the package is fragile
     * @return shipping description
     */
    public static String decide(boolean express, boolean fragile) {
        if (fragile && express) {
            return "manual-review";
        }

        DayOfWeek day = LocalDate.now().getDayOfWeek();
        return switch (day) {
            case SATURDAY, SUNDAY -> "weekend-batch";
            case FRIDAY -> express ? "same-day-cutoff" : "next-business-day";
            default -> express ? "same-day" : "standard";
        };
    }

    public static void main(String[] args) {
        System.out.println(decide(true, false));
        System.out.println(decide(false, true));
    }
}
```

Switch expression đã cover. Nhưng pattern matching cần sealed types — hãy mở rộng.

### Advanced: input normalization with small focused methods

```java
// UserInputNormalizer.java — Parse and normalize command input safely
import java.util.ArrayList;
import java.util.List;

public final class UserInputNormalizer {
    private UserInputNormalizer() {
    }

    /**
     * Normalizes a comma-separated command string.
     *
     * @param raw raw user input
     * @return normalized tokens
     */
    public static List<String> normalize(String raw) {
        List<String> tokens = new ArrayList<>();
        if (raw == null || raw.isBlank()) {
            return tokens;
        }

        for (String part : raw.split(",")) {
            String normalized = part.trim().toLowerCase();
            if (!normalized.isEmpty()) {
                tokens.add(normalized);
            }
        }
        return tokens;
    }

    public static void main(String[] args) {
        List<String> commands = normalize("  CREATE , Update, , DELETE ");
        for (String command : commands) {
            System.out.println("command = " + command);
        }
    }
}
```

Bạn đã đi qua syntax, branching, và pattern matching. Bây giờ đến phần nguy hiểm: missing case và indent bugs — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Basics — Syntax & Control Flow` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Dùng `==` để so sánh `String` | Dùng `equals()` hoặc `equalsIgnoreCase()` |
| 2 | Nhồi quá nhiều logic vào `main()` | Tách thành method nhỏ theo purpose |
| 3 | Dùng `null` bừa bãi cho local flow | Trả collection rỗng, guard clause, constructor chặt |
| 4 | Viết loop nhưng không tách bước normalize/validate | Tạo method phụ để code dễ test |

Bạn đã đi qua Java Syntax và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Java Language Basics | https://docs.oracle.com/javase/tutorial/java/nutsandbolts/ |
| Switch Expressions | https://docs.oracle.com/en/java/javase/21/language/switch-expressions.html |
| Text Blocks | https://docs.oracle.com/en/java/javase/21/text-blocks/index.html |

## 6. RECOMMEND

Khi các bẫy chính của `Java Basics — Syntax & Control Flow` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| `record` | DTO/read-only data | Gọn hơn POJO |
| `List` / `Map` | Xử lý tập dữ liệu | Là nền để học collections |
| JUnit 5 | Muốn test method nhỏ | Phù hợp ngay từ bài đầu |

## 7. QUIZ

### Quick Check

1. Vì sao local variable trong Java phải được khởi tạo trước khi dùng?
2. Khi nào nên dùng `switch expression` thay vì chuỗi `if/else` dài?
3. `String` trong Java nên so sánh bằng gì?

### Answer Key

1. Vì compiler kiểm tra definite assignment trước runtime.
2. Khi logic branch rõ ràng theo enum/value hữu hạn và cần code ngắn, ít lỗi fallthrough.
3. Dùng `equals()` hoặc `equalsIgnoreCase()`, không dùng `==`.

## 8. NEXT STEPS

- Đọc tiếp [Classes, Records & Enums](./02-classes-records-enums.md)
- Sau đó chuyển sang `collections/` để làm việc với dữ liệu thực tế
