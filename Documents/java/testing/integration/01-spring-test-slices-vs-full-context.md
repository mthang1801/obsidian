<!-- tags: java, testing -->
# ☕ Java Testing — Spring Test Slices vs Full Context

> Không phải integration test nào cũng nên boot toàn bộ ứng dụng. Bài này giúp chọn đúng độ rộng test để giữ feedback loop nhanh mà vẫn bắt được bug quan trọng.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 15 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Intermediate |
| **Use case** | Test controller, repository, app wiring |
| **Java focus** | `@WebMvcTest`, `@DataJpaTest`, `@SpringBootTest` |
| **Prerequisites** | JUnit, Mockito, Spring Boot web |

## 1. DEFINE

Hình dung một bug chỉ xuất hiện khi application context thật được dựng lên, trong khi unit test và vài mock-based test đều xanh rất đẹp. Bạn biết mình cần integration test, nhưng không biết nên dùng test slice đủ nhẹ hay full context đủ thật. Bài này mở đúng ở lựa chọn cân não đó.

Bài này đặt `Java Testing — Spring Test Slices vs Full Context` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Vì sao phải chọn đúng mức test?

Nếu mọi test đều là `@SpringBootTest`:

- feedback loop chậm
- setup nặng
- khó biết bug nằm ở layer nào

Nếu mọi test đều chỉ unit test:

- có thể bỏ sót wiring bug
- configuration bug lộ muộn
- contract web/persistence không được verify đủ

### Actors

| Actor | Vai trò |
| --- | --- |
| `@WebMvcTest` | Test web layer cắt mỏng |
| `@DataJpaTest` | Test persistence/repository |
| `@SpringBootTest` | Test full context/app wiring |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Test quá chậm | Dùng full context cho mọi case | Ưu tiên slice test trước |
| Không bắt được wiring bug | Chỉ có unit test | Bổ sung integration test có mục tiêu |
| Assertion lẫn nhiều layer | Test scope không rõ | Chọn annotation đúng theo mục tiêu |

Các failure mode trên nghe quen. Nhưng có trap: @SpringBootTest load toàn bộ context = test chậm, và @WebMvcTest thiếu mock service = NPE. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa mới chỉ khóa được tên của Java Testing — Spring Test Slices vs Full Context. Để khái niệm này bớt trừu tượng, ta cần nhìn nó ở dạng flow hoặc cấu trúc đủ cụ thể trước.

```text
Unit Test
   │
   ├── Web Slice      -> @WebMvcTest
   ├── Data Slice     -> @DataJpaTest
   └── Full Context   -> @SpringBootTest
```

```text
faster + narrower  ----------------------> slower + broader
unit -> slice -> full context
```

## 3. CODE

Flow của Java Testing — Spring Test Slices vs Full Context đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: web slice

```java
// CustomerControllerWebTest.java — Focused test for controller contract
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(CustomerController.class)
class CustomerControllerWebTest {
    @Autowired
    private MockMvc mockMvc;

    @Test
    void shouldReturnOk() throws Exception {
        mockMvc.perform(get("/api/customers/1"))
                .andExpect(status().isOk());
    }
}
```

Test slices đã cover. Nhưng custom context cần @TestConfiguration — hãy giới hạn.

### Intermediate: data slice

```java
// CustomerRepositoryDataTest.java — Repository-focused persistence test
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

@DataJpaTest
class CustomerRepositoryDataTest {
    @Autowired
    private CustomerRepository customerRepository;

    @Test
    void shouldFindCustomerByEmail() {
        boolean exists = customerRepository.findByEmail("alice@example.com").isPresent();
        assertTrue(exists);
    }
}
```

Custom context đã cover. Nhưng test containers cần real DB — hãy integrate.

### Advanced: full context smoke test

```java
// OrderingApplicationSmokeTest.java — Full context boot verification
import static org.junit.jupiter.api.Assertions.assertNotNull;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class OrderingApplicationSmokeTest {
    @Autowired
    private OrderApplicationService orderApplicationService;

    @Test
    void shouldBootApplicationContext() {
        assertNotNull(orderApplicationService);
    }
}
```

Bạn đã đi qua slices, custom context, và containers. Bây giờ đến phần nguy hiểm: full context overhead và missing mocks — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Testing — Spring Test Slices vs Full Context` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Lạm dụng `@SpringBootTest` | Chỉ dùng cho wiring/integration thật cần thiết |
| 2 | Dùng web slice nhưng vẫn mong DB thật chạy | Chọn `@DataJpaTest` hoặc full context phù hợp |
| 3 | Không phân biệt mục tiêu mỗi test | Đặt tên/scope test rõ |
| 4 | Chạy full context quá nhiều trong CI | Giữ số lượng ít nhưng giá trị cao |

Bạn đã đi qua Spring Testing và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Spring Boot Testing | https://docs.spring.io/spring-boot/reference/testing/index.html |
| WebMvcTest | https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html#testing.spring-boot-applications.autoconfigured-spring-mvc-tests |
| DataJpaTest | https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html#testing.spring-boot-applications.autoconfigured-data-jpa-tests |

## 6. RECOMMEND

Khi các bẫy chính của `Java Testing — Spring Test Slices vs Full Context` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Testcontainers | Cần DB/broker thật | Integration gần production hơn |
| Contract tests | API/consumer critical | Giảm mismatch liên service |
| Performance tests | Endpoint/query nặng | Bắt bottleneck sớm |

## 7. QUIZ

### Quick Check

1. Khi nào `@WebMvcTest` phù hợp hơn `@SpringBootTest`?
2. `@DataJpaTest` nên tập trung kiểm tra điều gì?
3. Vì sao cần giữ số lượng full-context test có chọn lọc?

### Answer Key

1. Khi chỉ cần verify web contract/controller behavior mà không cần boot toàn app.
2. Repository mapping, query behavior và persistence contract.
3. Vì chúng chậm hơn và nên dành cho wiring/integration bug thực sự quan trọng.

## 8. NEXT STEPS

- Sang `testcontainers/` khi cần integration gần production hơn
- Hoặc nối với `spring-boot/actuator` để test operational endpoints
