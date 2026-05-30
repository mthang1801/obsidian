<!-- tags: java, collections -->
# ☕ Java Collections — List, Set & Map

> Đây là bài nền để hiểu vì sao Java backend sống dựa vào collections: request params, batch jobs, cache keys, aggregation và mọi flow business đều đi qua `List`, `Set`, `Map`.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 13 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Basic → Intermediate |
| **Use case** | Batch processing, deduplication, lookup, grouping |
| **Java focus** | `ArrayList`, `HashSet`, `HashMap`, iteration |
| **Prerequisites** | Java basics, class/record |

## 1. DEFINE

Hình dung một đoạn code chỉ thay `List` bằng `Set`, hoặc thêm một `Map` cho tiện tra cứu. Mọi thứ vẫn compile, test nhỏ vẫn pass, nhưng semantics của dữ liệu đã đổi: thứ tự, uniqueness và equality bắt đầu quan trọng hơn bạn tưởng. Collections đáng học đúng từ chỗ đổi một container có thể đổi luôn ý nghĩa của bài toán.

Bài này đặt `Java Collections — List, Set & Map` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Chọn collection theo semantics

| Collection | Bảo toàn thứ tự | Unique | Lookup by key | Use case |
| --- | --- | --- | --- | --- |
| `List` | Có | Không | Không | Danh sách items, paging result |
| `Set` | Tùy implementation | Có | Không | Deduplicate email, role, tag |
| `Map` | Tùy implementation | Key unique | Có | Index object theo id/code |

### Invariants

| Quy tắc | Ý nghĩa |
| --- | --- |
| Collection phải phản ánh đúng business semantics | Tránh dùng `List` cho dữ liệu cần unique |
| Chọn implementation phù hợp với access pattern | Không phải collection nào cũng như nhau |
| Không expose mutable collection bừa bãi | Dễ gây side effect khó trace |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Duplicate data lọt qua | Dùng `List` thay vì `Set` | Chuyển sang set hoặc dedupe trước |
| Lookup chậm | Lặp list để tìm theo id | Index bằng `Map` |
| `ConcurrentModificationException` | Vừa iterate vừa mutate sai cách | Dùng iterator/remove hợp lệ hoặc copy |

Các failure mode trên nghe dễ tránh. Nhưng có trap: List.of() trả immutable list nhưng caller gọi add = UnsupportedOperationException, và HashMap key không override equals/hashCode = lookup fail. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa mới chỉ khóa được tên của Java Collections — List, Set & Map. Để khái niệm này bớt trừu tượng, ta cần nhìn nó ở dạng flow hoặc cấu trúc đủ cụ thể trước.

```text
Order lines      ── ordered items ──▶ List
Seen emails      ── unique values ──▶ Set
Users by id      ── key lookup    ──▶ Map
```

```text
Batch import
   │
   ├── raw rows            ──▶ List<Row>
   ├── dedupe product code ──▶ Set<String>
   └── fast access by sku  ──▶ Map<String, Product>
```

## 3. CODE

Flow của Java Collections — List, Set & Map đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: use `List` for ordered data

```java
// InvoiceLineDemo.java — List keeps insertion order for invoice rendering
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

public final class InvoiceLineDemo {
    private InvoiceLineDemo() {
    }

    /**
     * Prints invoice lines in the same order users entered them.
     *
     * @param args command-line arguments
     */
    public static void main(String[] args) {
        List<InvoiceLine> lines = new ArrayList<>();
        lines.add(new InvoiceLine("BOOK", 2, new BigDecimal("12.50")));
        lines.add(new InvoiceLine("PEN", 5, new BigDecimal("1.20")));

        for (InvoiceLine line : lines) {
            System.out.printf("%s x%d = %s%n", line.sku(), line.quantity(), line.total());
        }
    }

    record InvoiceLine(String sku, int quantity, BigDecimal price) {
        BigDecimal total() {
            return price.multiply(BigDecimal.valueOf(quantity));
        }
    }
}
```

List/Set basics đã cover. Nhưng Map operations cần entry navigation — hãy iterate.

### Intermediate: use `Set` for deduplication

```java
// UniqueRoleDemo.java — Set removes duplicated role assignments
import java.util.LinkedHashSet;
import java.util.Set;

public final class UniqueRoleDemo {
    private UniqueRoleDemo() {
    }

    public static void main(String[] args) {
        Set<String> roles = new LinkedHashSet<>();
        roles.add("admin");
        roles.add("viewer");
        roles.add("admin");

        System.out.println("assigned roles = " + roles);
    }
}
```

Map operations đã cover. Nhưng concurrent collections cần thread-safety — hãy protect.

### Advanced: use `Map` as an in-memory index

```java
// ProductIndexDemo.java — Map gives fast lookup for import validation
import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;

public final class ProductIndexDemo {
    private ProductIndexDemo() {
    }

    /**
     * Builds an index for validating incoming import rows.
     *
     * @param args command-line arguments
     */
    public static void main(String[] args) {
        Map<String, Product> productsBySku = new HashMap<>();
        productsBySku.put("SKU-100", new Product("SKU-100", new BigDecimal("99.00")));
        productsBySku.put("SKU-200", new Product("SKU-200", new BigDecimal("149.00")));

        String incomingSku = "SKU-200";
        Product product = productsBySku.get(incomingSku);

        if (product == null) {
            System.out.println("unknown sku");
            return;
        }

        System.out.println("validated product = " + product.sku() + ", price = " + product.price());
    }

    record Product(String sku, BigDecimal price) {
    }
}
```

Bạn đã đi qua List, Map, và concurrent collections. Bây giờ đến phần nguy hiểm: immutable surprise và hashCode missing — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Collections — List, Set & Map` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Dùng `ArrayList` cho lookup theo id nhiều lần | Dùng `Map` để index |
| 2 | Dùng `HashSet` nhưng cần giữ insertion order | Dùng `LinkedHashSet` |
| 3 | Trả collection mutable trực tiếp ra ngoài | Bọc bằng unmodifiable view hoặc copy |
| 4 | Không rõ collection có thể chứa `null` hay không | Đặt contract rõ trong API/service |

Bạn đã đi qua Collections và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Collections Framework | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/package-summary.html |
| List API | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/List.html |
| Map API | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Map.html |

## 6. RECOMMEND

Khi các bẫy chính của `Java Collections — List, Set & Map` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Streams | Cần transform/filter/grouping | Code gọn hơn cho pipeline dữ liệu |
| `EnumMap` / `EnumSet` | Key hoặc value là enum | Nhanh và semantic hơn |
| Concurrent collections | Nhiều thread cùng truy cập | Tránh race và contention sai |

## 7. QUIZ

### Quick Check

1. Khi nào `Set` phù hợp hơn `List`?
2. Vì sao `Map` thường tốt hơn loop qua list để tìm theo id?
3. `LinkedHashSet` khác `HashSet` ở điểm nào?

### Answer Key

1. Khi cần uniqueness là semantics chính.
2. Vì lookup theo key rõ ràng và thường hiệu quả hơn lặp tuần tự.
3. `LinkedHashSet` giữ insertion order, `HashSet` thì không đảm bảo.

## 8. NEXT STEPS

- Sang `generics/` khi cần collection type-safe sâu hơn
- Hoặc chuyển sang Spring Boot web layer để thấy `List`, `Set`, `Map` xuất hiện trong request/response
