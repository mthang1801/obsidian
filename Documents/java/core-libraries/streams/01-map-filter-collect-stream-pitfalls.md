<!-- tags: java, jdk -->
# ☕ Java Core Libraries — Map, Filter, Collect & Stream Pitfalls

> Stream API giúp code collection transformation gọn hơn, nhưng chỉ khi dùng có chủ đích. Bài này tập trung vào mental model đủ thực dụng để stream phục vụ readability thay vì chống lại nó.

📅 Ngày tạo: 2026-03-28 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 14 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Intermediate |
| **Use case** | Filter list, transform DTO, grouping/reporting |
| **Java focus** | `map`, `filter`, `collect`, `toList`, collector mindset |
| **Prerequisites** | Collections, generics |

## 1. DEFINE

Hình dung bạn mở một PR và thấy một chain stream rất đẹp: `map`, `filter`, `collect` nối nhau mượt mà tới mức không ai muốn phá vỡ. Nhưng khi bug xuất hiện hoặc performance bắt đầu giảm, cả nhóm lại phải dừng lại để giải mã xem dữ liệu đã đổi hình dạng ở bước nào. Streams đáng học nhất ở chính khoảnh khắc vẻ đẹp cú pháp bắt đầu che mất flow thật.

Bài này đặt `Java Core Libraries — Map, Filter, Collect & Stream Pitfalls` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Stream API nên dùng khi nào?

Stream hợp khi:

- cần mô tả pipeline dữ liệu rõ ràng
- logic là transform/filter/group/aggregate
- code imperative bắt đầu lặp lại mẫu chung

Không nên cố dùng stream khi:

- stateful logic phức tạp hơn pipeline
- side effect là trọng tâm
- đọc imperative rõ hơn hẳn

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Stream khó đọc | Nhồi quá nhiều lambda | Tách method nhỏ |
| Side effects ẩn | Dùng `peek` hoặc mutate state ngoài | Giữ stream pure hơn |
| Parallel stream dùng bừa | Không hiểu workload | Chỉ dùng sau khi đo |

Các failure mode trên nghe quen. Nhưng có trap: stream reuse = IllegalStateException, và parallel stream trên small dataset = overhead > gain. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa mới chỉ khóa được tên của Java Core Libraries — Map, Filter, Collect & Stream Pitfalls. Để khái niệm này bớt trừu tượng, ta cần nhìn nó ở dạng flow hoặc cấu trúc đủ cụ thể trước.

```text
source list
   │
   ├── filter
   ├── map
   └── collect
```

```text
data pipeline
  raw orders -> paid orders -> order summaries -> list/map
```

## 3. CODE

Flow của Java Core Libraries — Map, Filter, Collect & Stream Pitfalls đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: filter and map

```java
// OrderSummaryStreamDemo.java — Filter and map a list of orders
import java.util.List;

public final class OrderSummaryStreamDemo {
    public List<String> paidOrderCodes(List<Order> orders) {
        return orders.stream()
                .filter(Order::paid)
                .map(Order::code)
                .toList();
    }

    public record Order(String code, boolean paid) {
    }
}
```

Map/filter/collect basics đã cover. Nhưng collectors cần grouping — hãy aggregate.

### Intermediate: collect to map

```java
// ProductIndexStreamDemo.java — Build an index from a product list
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

public final class ProductIndexStreamDemo {
    public Map<String, Product> indexBySku(List<Product> products) {
        return products.stream()
                .collect(Collectors.toMap(Product::sku, Function.identity()));
    }

    public record Product(String sku, String name) {
    }
}
```

Collectors đã cover. Nhưng custom collector cần Collector.of — hãy build.

### Advanced: grouping and aggregation

```java
// RevenueByStatusDemo.java — Aggregate order totals by status
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public final class RevenueByStatusDemo {
    public Map<String, BigDecimal> revenueByStatus(List<Order> orders) {
        return orders.stream()
                .collect(Collectors.groupingBy(
                        Order::status,
                        Collectors.reducing(BigDecimal.ZERO, Order::amount, BigDecimal::add)
                ));
    }

    public record Order(String status, BigDecimal amount) {
    }
}
```

Bạn đã đi qua streams, collectors, và custom. Bây giờ đến phần nguy hiểm: stream reuse và parallel overhead — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Core Libraries — Map, Filter, Collect & Stream Pitfalls` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Dùng stream cho mọi bài toán | Ưu tiên readability trước |
| 2 | Nhét side effect vào pipeline | Giữ transform thuần khi có thể |
| 3 | Lambda quá dài | Tách method đặt tên rõ |
| 4 | Dùng parallel stream không đo | Benchmark/profiling trước |

Bạn đã đi qua Streams và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Stream API | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/package-summary.html |
| Collectors | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/Collectors.html |
| Stream interface | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/Stream.html |

## 6. RECOMMEND

Khi các bẫy chính của `Java Core Libraries — Map, Filter, Collect & Stream Pitfalls` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Collector custom | Aggregate logic đặc thù | Giữ pipeline nhất quán |
| Benchmark stream vs loop | Hot path nhạy performance | Chọn implementation có dữ liệu |
| Optional + stream combo | Data transformation nhiều nhánh | Tăng expressiveness có kiểm soát |

## 7. QUIZ

### Quick Check

1. Khi nào stream phù hợp hơn imperative loop?
2. Vì sao `peek` dễ bị lạm dụng?
3. Parallel stream có nên bật mặc định không?

### Answer Key

1. Khi bài toán là pipeline transform/filter/group rõ ràng.
2. Vì nó dễ kéo side effect ẩn vào pipeline và làm code khó reasoning.
3. Không, chỉ nên cân nhắc sau khi đo workload thật.

## 8. NEXT STEPS

- Nối với `performance/profiling` nếu stream xuất hiện trên hot path
- Hoặc quay lại `spring-data` trong batch sau để thấy stream ở repository/service layer
