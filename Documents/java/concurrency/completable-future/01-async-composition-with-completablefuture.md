<!-- tags: java, concurrency -->
# ☕ Java Concurrency — Async Composition with CompletableFuture

> `CompletableFuture` là bước chuyển từ “chạy task song song” sang “orchestrate nhiều async steps có dependency”. Bài này tập trung vào cách compose flow bất đồng bộ mà không biến code thành callback spaghetti.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 15 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Advanced |
| **Use case** | Song song hóa IO, combine downstream results, async orchestration |
| **Java focus** | `CompletableFuture`, `thenCompose`, `thenCombine`, `exceptionally` |
| **Prerequisites** | Executors, concurrency basics |

## 1. DEFINE

Hình dung một request cần gọi ba downstream khác nhau. Bạn muốn giảm latency nên chuyển sang `CompletableFuture`, rồi chỉ sau vài lần deploy đã phải đối mặt với chain callback khó đọc, exception đi lạc và thread pool bị dùng theo cách không ai đoán trước. Bài này đứng ở chỗ async composition bắt đầu có giá thật.

Bài này đặt `Java Concurrency — Async Composition with CompletableFuture` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### `CompletableFuture` giải quyết gì?

Khi có nhiều async steps phụ thuộc nhau, chỉ dùng executor + callback tay sẽ nhanh chóng khó đọc. `CompletableFuture` cung cấp:

- composition theo chain
- combine nhiều kết quả song song
- propagation lỗi trong async flow
- timeout và fallback theo từng bước

### Actors

| Actor | Vai trò |
| --- | --- |
| Supplier stage | Task tạo giá trị đầu vào |
| Compose stage | Async step tiếp theo phụ thuộc kết quả trước |
| Combine stage | Gộp nhiều nhánh song song |
| Recovery stage | Xử lý exception/fallback |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Callback hell trá hình | Chain thiếu structure | Dùng `thenCompose`/`thenCombine` rõ nghĩa |
| Mất exception | Không xử lý lỗi cuối chain | Dùng `handle`, `exceptionally`, hoặc `whenComplete` |
| Block sớm bằng `.join()` | Phá lợi ích async | Chỉ join ở boundary thật cần thiết |

Các failure mode trên nghe rõ. Nhưng có trap: thenApply vs thenCompose nhầm = CompletableFuture<CompletableFuture<T>>, và exceptionally handler missing = silent failure. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa của Java Concurrency — Async Composition with CompletableFuture nghe có thể đã đủ rõ, nhưng concurrency chỉ thật sự lộ mặt khi bạn nhìn timing, ownership và điểm nghẽn cùng lúc. Hãy đưa nó về một sơ đồ đủ cụ thể trước.

```text
fetch customer ──▶ fetch orders ──▶ build summary
        │
        └─────────────▶ fetch loyalty score
                         │
                         ▼
                    thenCombine
```

```text
start async
   │
   ├── success path -> compose/combine
   └── failure path -> recover/log/fallback
```

## 3. CODE

Khi timing của Java Concurrency — Async Composition with CompletableFuture đã hiện hình, bước tiếp theo là biến nó thành code đủ nhỏ để hiểu nhưng đủ thật để nhìn ra trade-off. Ta đi từ case dễ nhất rồi tăng dần áp lực.

### Basic: async supplier

```java
// AsyncCatalogClient.java — Basic async lookup with CompletableFuture
import java.util.concurrent.CompletableFuture;

public final class AsyncCatalogClient {
    public CompletableFuture<String> fetchProductName(String sku) {
        return CompletableFuture.supplyAsync(() -> "product-" + sku);
    }
}
```

Basic future đã cover. Nhưng composition cần thenCompose — hãy chain.

### Intermediate: compose dependent async steps

```java
// CustomerOrderSummaryService.java — Compose dependent async calls
import java.util.concurrent.CompletableFuture;

public final class CustomerOrderSummaryService {
    private final CustomerGateway customerGateway;
    private final OrderGateway orderGateway;

    public CustomerOrderSummaryService(CustomerGateway customerGateway, OrderGateway orderGateway) {
        this.customerGateway = customerGateway;
        this.orderGateway = orderGateway;
    }

    public CompletableFuture<String> buildSummary(long customerId) {
        return customerGateway.fetchCustomer(customerId)
                .thenCompose(customer ->
                        orderGateway.fetchLatestOrder(customer.id())
                                .thenApply(order -> customer.name() + " -> " + order.code())
                );
    }

    public interface CustomerGateway {
        CompletableFuture<Customer> fetchCustomer(long customerId);
    }

    public interface OrderGateway {
        CompletableFuture<Order> fetchLatestOrder(long customerId);
    }

    public record Customer(long id, String name) {
    }

    public record Order(String code) {
    }
}
```

Composition đã cover. Nhưng allOf/anyOf cần fan-out — hãy parallelize.

### Advanced: combine branches with recovery

```java
// CustomerDashboardService.java — Combine async branches and recover gracefully
import java.util.concurrent.CompletableFuture;

public final class CustomerDashboardService {
    private final ProfileGateway profileGateway;
    private final LoyaltyGateway loyaltyGateway;

    public CustomerDashboardService(ProfileGateway profileGateway, LoyaltyGateway loyaltyGateway) {
        this.profileGateway = profileGateway;
        this.loyaltyGateway = loyaltyGateway;
    }

    public CompletableFuture<String> loadDashboard(long customerId) {
        CompletableFuture<String> profile = profileGateway.fetchDisplayName(customerId);
        CompletableFuture<Integer> loyalty = loyaltyGateway.fetchPoints(customerId)
                .exceptionally(error -> 0);

        return profile.thenCombine(loyalty, (displayName, points) ->
                displayName + " has " + points + " points"
        );
    }

    public interface ProfileGateway {
        CompletableFuture<String> fetchDisplayName(long customerId);
    }

    public interface LoyaltyGateway {
        CompletableFuture<Integer> fetchPoints(long customerId);
    }
}
```

Bạn đã đi qua future, composition, và fan-out. Bây giờ đến phần nguy hiểm: Apply/Compose confusion và missing error handler — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Concurrency — Async Composition with CompletableFuture` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | `.join()` ở giữa flow | Chỉ block ở boundary cuối cùng |
| 2 | Dùng `thenApply` cho async step tiếp theo | Nếu step sau trả future, dùng `thenCompose` |
| 3 | Không có strategy xử lý lỗi | Thêm `exceptionally` hoặc `handle` |
| 4 | Trộn business logic nặng vào lambda dài | Tách method nhỏ để chain dễ đọc |

Bạn đã đi qua CompletableFuture và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| CompletableFuture API | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/CompletableFuture.html |
| Concurrency Tutorial | https://docs.oracle.com/javase/tutorial/essential/concurrency/ |
| CompletionStage Guide | https://www.baeldung.com/java-completablefuture |

## 6. RECOMMEND

Khi các bẫy chính của `Java Concurrency — Async Composition with CompletableFuture` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Structured concurrency / virtual threads | Async orchestration phức tạp hơn | Mô hình mới dễ reasoning hơn |
| Timeout decorators | Downstream không ổn định | Giới hạn blast radius |
| Resilience patterns | Có retry/circuit breaker | Giữ flow async an toàn hơn |

## 7. QUIZ

### Quick Check

1. Khi nào `thenCompose` đúng hơn `thenApply`?
2. Vì sao `.join()` quá sớm làm hỏng async flow?
3. `thenCombine` phù hợp cho loại bài toán nào?

### Answer Key

1. Khi step tiếp theo trả về `CompletableFuture` khác.
2. Vì nó block thread và phá composition bất đồng bộ.
3. Khi cần gộp hai nhánh async độc lập thành một kết quả chung.

## 8. NEXT STEPS

- Đi tiếp sang `virtual-threads/` nếu muốn so mô hình async mới của Java
- Hoặc nối với `spring-boot/deployment` để nhìn từ góc vận hành production
