<!-- tags: java, testing -->
# ☕ Java Testing — Real Dependencies with Testcontainers

> Khi mock không còn đủ để bắt bug cấu hình hoặc behavior của database/broker thật, Testcontainers là bước tiếp theo hợp lý. Bài này tập trung vào triết lý dùng dependency thật có kiểm soát trong test.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 15 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Advanced |
| **Use case** | Integration test với Postgres, Redis, Kafka, RabbitMQ |
| **Java focus** | Testcontainers, lifecycle container, Spring integration |
| **Prerequisites** | Spring test slices, JUnit, Mockito |

## 1. DEFINE

Hình dung integration test của bạn xanh suốt ở local giả lập, rồi fail hàng loạt khi chạm database, broker hoặc môi trường gần production hơn một chút. Testcontainers chỉ trở nên đáng tiền khi team chấp nhận rằng có những niềm tin không thể mua bằng mock.

Bài này đặt `Java Testing — Real Dependencies with Testcontainers` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Vì sao cần Testcontainers?

Mock giúp unit test nhanh, nhưng không kiểm tra được:

- driver/config thực tế
- SQL dialect behavior
- startup wiring với dependency thật
- khác biệt giữa local in-memory DB và production DB

Testcontainers giải quyết bằng cách khởi tạo dependency thật trong container ngắn hạn cho test.

### Actors

| Actor | Vai trò |
| --- | --- |
| Test container | Dependency thật cho test |
| Test class | Khởi tạo và sử dụng container |
| Application context | Binding datasource/broker config từ container |
| CI runner | Chạy test trong môi trường tự động |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Test flaky | Container lifecycle không rõ | Quản lý lifecycle đúng và isolate state |
| Test quá chậm | Dùng container cho mọi unit test | Chỉ dùng ở integration layer |
| Config lệch | Không bind URL/credentials từ container | Dùng dynamic property wiring |

Các failure mode trên nghe rõ. Nhưng có trap: container port mapping sai = connection refused, và test isolation thiếu = state leak between tests. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa mới chỉ khóa được tên của Java Testing — Real Dependencies with Testcontainers. Để khái niệm này bớt trừu tượng, ta cần nhìn nó ở dạng flow hoặc cấu trúc đủ cụ thể trước.

```text
test class
   │
   ├── start postgres container
   ├── inject JDBC URL / username / password
   ├── boot repository/app slice
   └── run assertions on real DB behavior
```

```text
unit test -> mock
slice test -> partial context
testcontainers -> real dependency
```

## 3. CODE

Flow của Java Testing — Real Dependencies with Testcontainers đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: standalone Postgres container

```java
// PostgresContainerTest.java — Minimal Testcontainers setup
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

class PostgresContainerTest {
    @Test
    void shouldStartPostgresContainer() {
        try (PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16")) {
            postgres.start();
            System.out.println(postgres.getJdbcUrl());
        }
    }
}
```

Basic containers đã cover. Nhưng reusable containers cần singleton — hãy optimize.

### Intermediate: Spring property binding

```java
// CustomerRepositoryContainerTest.java — Bind datasource from Testcontainers
import org.junit.jupiter.api.Test;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

@Testcontainers
class CustomerRepositoryContainerTest {
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");

    @DynamicPropertySource
    static void registerProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Test
    void shouldWireContainerProperties() {
        // real repository assertions go here
    }
}
```

Singletons đã cover. Nhưng custom modules cần GenericContainer — hãy extend.

### Advanced: choose container scope intentionally

```java
// MessagingIntegrationTestPlan.java — Pseudo-structure for shared container strategy
/**
 * Shared static containers reduce startup cost for expensive integration suites.
 * Per-test containers give stronger isolation but increase runtime.
 */
public final class MessagingIntegrationTestPlan {
    private MessagingIntegrationTestPlan() {
    }

    public static String guidance() {
        return "Use shared containers for stable suites, isolated containers for side-effect-heavy tests.";
    }
}
```

Bạn đã đi qua containers, singletons, và custom modules. Bây giờ đến phần nguy hiểm: port mapping và state leak — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Testing — Real Dependencies with Testcontainers` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Dùng Testcontainers cho mọi test | Giữ nó cho integration tests có giá trị cao |
| 2 | Không reset state giữa tests | Isolate data hoặc recreate fixtures rõ ràng |
| 3 | Hardcode datasource test config | Bind động từ container runtime |
| 4 | Đánh giá sai runtime CI | Tách suite nhanh/chậm |

Bạn đã đi qua Testcontainers và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Testcontainers for Java | https://java.testcontainers.org/ |
| JUnit 5 Integration | https://java.testcontainers.org/test_framework_integration/junit_5/ |
| Spring Boot Integration | https://java.testcontainers.org/modules/databases/jdbc/ |

## 6. RECOMMEND

Khi các bẫy chính của `Java Testing — Real Dependencies with Testcontainers` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Reusable containers | CI/test suite lớn | Giảm startup overhead |
| Kafka/RabbitMQ containers | Messaging integration quan trọng | Kiểm tra contract thực |
| Seed fixtures migration-based | DB logic phức tạp | Test gần production hơn |

## 7. QUIZ

### Quick Check

1. Khi nào Testcontainers tốt hơn mock?
2. Vì sao không nên dùng nó cho mọi unit test?
3. `@DynamicPropertySource` giúp giải quyết gì?

### Answer Key

1. Khi cần verify behavior với dependency thật như database hoặc broker.
2. Vì chi phí runtime cao hơn và không cần thiết cho test hẹp.
3. Nó bind config runtime từ container vào Spring test context.

## 8. NEXT STEPS

- Kết hợp với `spring-boot/deployment` để nhìn cả vòng đời từ test đến runtime
- Hoặc mở rộng sang Kafka/RabbitMQ integration suites
