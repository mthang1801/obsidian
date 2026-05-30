<!-- tags: java, fundamentals -->
# ☕ Java Generics — Type Parameters, Bounds & Wildcards

> Generics là nền để Java giữ type safety ở compile time. Nếu không nắm phần này, đọc collections, repositories, `Comparator`, `Optional`, hay các helper API sẽ rất dễ mơ hồ.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 14 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Intermediate |
| **Use case** | Viết helper API, repository contract, collection utilities |
| **Java focus** | `<T>`, bounded type params, `? extends`, `? super` |
| **Prerequisites** | Collections, class/record |

## 1. DEFINE

Hình dung bạn mở một API Java và thấy nó compile ngon cho tới lúc một `? extends` hay `? super` xuất hiện, rồi cả team bắt đầu dùng generics theo kiểu chắp vá: chỗ thì raw type, chỗ thì cast, chỗ thì wildcard để “cho qua”. Generics chỉ thật sự sáng khi bạn nhìn nó như contract về khả năng đọc và ghi, không như bùa chú cho compiler im lặng.

Bài này đặt `Java Generics — Type Parameters, Bounds & Wildcards` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Generics giải quyết gì?

Trước generics, nhiều API phải dùng `Object`. Hệ quả:

- cần cast tay
- lỗi type mismatch lộ ra ở runtime
- IDE/autocomplete kém chính xác

Generics cho phép:

- encode type contract ngay ở compile time
- tái sử dụng logic mà vẫn type-safe
- đọc API dễ hơn nếu đặt type parameter rõ nghĩa

### Khái niệm cốt lõi

| Concept | Ý nghĩa | Ví dụ |
| --- | --- | --- |
| Type parameter | Kiểu được truyền vào generic type/method | `List<T>` |
| Upper bound | Giới hạn type phải là subtype của một base type | `<T extends Number>` |
| Wildcard extends | Đọc dữ liệu an toàn từ producer | `List<? extends Number>` |
| Wildcard super | Ghi dữ liệu an toàn vào consumer | `List<? super Integer>` |

### Invariants

| Quy tắc | Ý nghĩa |
| --- | --- |
| Dùng type parameter tên có nghĩa khi API đủ phức tạp | `T`, `ID`, `R` nên bám semantics |
| `? extends` thiên về đọc | Producer |
| `? super` thiên về ghi | Consumer |
| Tránh lạm dụng wildcard khi type parameter rõ hơn | API sẽ dễ đọc hơn |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| API quá rối với wildcard | Chọn sai abstraction | Đổi sang type parameter rõ ràng |
| Cast tay sau khi đã có generics | Chưa model type đủ tốt | Đưa generic lên interface/method |
| Dùng raw type như `List` | Mất type safety | Luôn khai báo `List<String>` hoặc tương đương |

Các failure mode trên nghe cơ bản. Nhưng có trap: type erasure gây ClassCastException tại runtime, và wildcard capture sai = compile error khó debug. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa mới chỉ khóa được tên của Java Generics — Type Parameters, Bounds & Wildcards. Để khái niệm này bớt trừu tượng, ta cần nhìn nó ở dạng flow hoặc cấu trúc đủ cụ thể trước.

```text
Without generics
List values ──▶ Object ──▶ cast at runtime ──▶ fragile

With generics
List<String> ──▶ compile-time contract ──▶ safer + clearer
```

```text
PECS mental model

Producer Extends  -> ? extends T -> mostly read
Consumer Super    -> ? super T   -> mostly write
```

## 3. CODE

Flow của Java Generics — Type Parameters, Bounds & Wildcards đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: generic box

```java
// Box.java — Simple generic type for wrapping one value safely
public final class Box<T> {
    private final T value;

    public Box(T value) {
        this.value = value;
    }

    /**
     * Returns the wrapped value.
     *
     * @return wrapped value
     */
    public T value() {
        return value;
    }

    public static void main(String[] args) {
        Box<String> nameBox = new Box<>("Alice");
        Box<Integer> ageBox = new Box<>(30);

        System.out.println(nameBox.value().toUpperCase());
        System.out.println(ageBox.value() + 1);
    }
}
```

Type parameters đã cover. Nhưng bounds cần extends/super — hãy giới hạn.

### Intermediate: bounded type parameter

```java
// NumberStats.java — Bounded type parameter for numeric calculations
import java.util.List;

public final class NumberStats {
    private NumberStats() {
    }

    /**
     * Sums a list of numeric values.
     *
     * @param values numeric values
     * @param <T> subtype of Number
     * @return sum as double
     */
    public static <T extends Number> double sum(List<T> values) {
        double total = 0.0;
        for (T value : values) {
            total += value.doubleValue();
        }
        return total;
    }

    public static void main(String[] args) {
        System.out.println(sum(List.of(1, 2, 3)));
        System.out.println(sum(List.of(1.5, 2.5, 3.5)));
    }
}
```

Bounds đã cover. Nhưng wildcards cần PECS principle — hãy apply.

### Advanced: `extends` vs `super`

```java
// GenericTransfer.java — Producer/consumer example with wildcards
import java.util.ArrayList;
import java.util.List;

public final class GenericTransfer {
    private GenericTransfer() {
    }

    /**
     * Copies values from producer to consumer using PECS rules.
     *
     * @param source producer of integers
     * @param target consumer accepting integers
     */
    public static void copyIntegers(List<? extends Integer> source, List<? super Integer> target) {
        for (Integer value : source) {
            target.add(value);
        }
    }

    public static void main(String[] args) {
        List<Integer> source = List.of(1, 2, 3);
        List<Number> target = new ArrayList<>();
        copyIntegers(source, target);
        System.out.println(target);
    }
}
```

Bạn đã đi qua generics, bounds, và wildcards. Bây giờ đến phần nguy hiểm: type erasure và capture errors — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Generics — Type Parameters, Bounds & Wildcards` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Dùng raw type `List` | Khai báo type parameter rõ ràng |
| 2 | Không phân biệt `extends` và `super` | Nhớ quy tắc PECS |
| 3 | Lạm dụng wildcard làm API khó đọc | Cân nhắc type parameter có tên |
| 4 | Tưởng generics tồn tại nguyên vẹn ở runtime | Nhớ khái niệm type erasure |

Bạn đã đi qua Generics và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Java Generics Tutorial | https://docs.oracle.com/javase/tutorial/java/generics/ |
| Wildcards | https://docs.oracle.com/javase/tutorial/java/generics/wildcards.html |
| Bounded Type Parameters | https://docs.oracle.com/javase/tutorial/java/generics/bounded.html |

## 6. RECOMMEND

Khi các bẫy chính của `Java Generics — Type Parameters, Bounds & Wildcards` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Generic repository contract | Viết data access abstraction | Tái sử dụng type-safe |
| Streams + generics | Làm collection transformations | Đọc API JDK dễ hơn |
| Sealed hierarchy | Domain model sâu hơn | Phân tách shape/type rõ |

## 7. QUIZ

### Quick Check

1. Generics giúp tránh loại lỗi nào phổ biến nhất?
2. `? extends T` phù hợp cho producer hay consumer?
3. Khi nào nên ưu tiên type parameter thay vì wildcard?

### Answer Key

1. Lỗi cast/type mismatch chỉ lộ ở runtime.
2. Producer, vì chủ yếu đọc dữ liệu ra.
3. Khi API có quan hệ type rõ và cần dễ đọc, dễ bảo trì hơn.

## 8. NEXT STEPS

- Sang `testing/junit` nếu muốn thấy generics xuất hiện trong assertion/fixture helpers
- Hoặc tiếp tục `concurrency/` khi đã vững collections + generics
