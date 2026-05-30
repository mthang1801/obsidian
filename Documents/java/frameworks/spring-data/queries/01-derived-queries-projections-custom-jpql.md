<!-- tags: java, spring-data -->
# ☕ Spring Data — Derived Queries, Projections, Custom JPQL

> Không phải mọi query đều nên load nguyên entity graph. Khi ứng dụng lớn dần, hiểu lúc nào dùng derived query, projection hay custom JPQL sẽ giúp API đọc nhanh hơn và persistence layer bớt mơ hồ.

📅 Ngày tạo: 2026-03-28 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 15 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Advanced |
| **Use case** | Query read model trong ứng dụng Spring Data |
| **Java focus** | repository query methods, DTO projection, JPQL |
| **Prerequisites** | JPA basics |

## 1. DEFINE

Hình dung một repository bắt đầu bằng vài derived query rất đẹp, rồi dần dần thêm projection, custom JPQL và đủ loại filter tới mức không ai còn biết abstraction đang giúp mình hay đang che đi complexity. Query layer đáng học nhất ở chỗ tốc độ ban đầu bắt đầu biến thành ambiguity về sau.

Bài này đặt `Spring Data — Derived Queries, Projections, Custom JPQL` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Chọn query strategy theo mục tiêu gì?

- cần đơn giản, ít điều kiện: derived query
- cần chỉ lấy vài field: projection
- cần logic đọc rõ ràng hơn: custom JPQL

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| API list chậm vì load nguyên entity | query không tối ưu cho read model | dùng projection |
| Method name dài khó đọc | lạm dụng derived query | chuyển sang custom query |
| JPQL bị rải lung tung | không có strategy rõ | thống nhất nơi chứa query phức tạp |

Các failure mode trên nghe rõ. Nhưng có trap: derived query dài quá = method name illegible, và JPQL injection từ user input = security risk. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Với Spring Data — Derived Queries, Projections, Custom JPQL, phần khó không nằm ở tên annotation hay package nữa mà ở flow thật của request, bean hoặc boundary. Sơ đồ dưới đây giúp kéo flow đó ra ánh sáng.

```text
simple lookup        -> derived query
read-only thin view  -> projection
complex join/filter  -> custom JPQL or native query
```

## 3. CODE

Sơ đồ đã cho bạn thấy flow của Spring Data — Derived Queries, Projections, Custom JPQL. Bây giờ ta chuyển nó thành code Java/Spring đủ gần production để boundary không còn là khái niệm mơ hồ.

### Basic: derived query

```java
// CustomerRepository.java — Derived query for straightforward lookup
package com.example.customer.persistence;

import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CustomerRepository extends JpaRepository<CustomerEntity, Long> {
    Optional<CustomerEntity> findByEmail(String email);

    List<CustomerEntity> findByStatusOrderByCreatedAtDesc(CustomerStatus status);
}
```

Derived queries đã cover. Nhưng projections cần interface proxy — hãy optimize.

### Intermediate: interface projection

```java
// CustomerSummaryView.java — Thin read model for list endpoints
package com.example.customer.readmodel;

public interface CustomerSummaryView {
    Long getId();

    String getName();

    String getEmail();
}
```

```java
// CustomerSummaryRepository.java — Projection avoids loading full entity graph
package com.example.customer.readmodel;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CustomerSummaryRepository extends JpaRepository<CustomerEntity, Long> {
    List<CustomerSummaryView> findTop20ByOrderByCreatedAtDesc();
}
```

Projections đã cover. Nhưng custom JPQL cần @Query — hãy viết.

### Advanced: custom JPQL for explicit reads

```java
// CustomerQueryRepository.java — Explicit JPQL for a more complex read use case
package com.example.customer.readmodel;

import java.util.List;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.Repository;

public interface CustomerQueryRepository extends Repository<CustomerEntity, Long> {
    @Query("""
            select new com.example.customer.readmodel.CustomerReportRow(
                c.id,
                c.name,
                count(o.id)
            )
            from CustomerEntity c
            left join OrderEntity o on o.customer.id = c.id
            group by c.id, c.name
            order by c.name asc
            """)
    List<CustomerReportRow> loadCustomerReport();
}
```

Bạn đã đi qua derived, projections, và JPQL. Bây giờ đến phần nguy hiểm: illegible methods và JPQL injection — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Spring Data — Derived Queries, Projections, Custom JPQL` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Dùng entity cho mọi read endpoint | tạo projection/read model phù hợp |
| 2 | Derived query name dài và mơ hồ | chuyển sang JPQL/custom query |
| 3 | Query logic khó tìm vì rải khắp nơi | gom read strategy theo module rõ ràng |
| 4 | Tối ưu sớm bằng native query không cần thiết | bắt đầu từ cách rõ ràng rồi đo |

Bạn đã đi qua Queries & JPQL và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Spring Data JPA Query Methods | https://docs.spring.io/spring-data/jpa/reference/jpa/query-methods.html |
| Spring Data Projections | https://docs.spring.io/spring-data/jpa/reference/repositories/projections.html |
| JPQL language reference | https://jakarta.ee/specifications/persistence/ |

## 6. RECOMMEND

Khi các bẫy chính của `Spring Data — Derived Queries, Projections, Custom JPQL` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Dedicated read repository | Read-heavy module | tách rõ read/write intent |
| Native query | Query quá nặng hoặc DB-specific optimization | kiểm soát SQL chi tiết |
| Pagination contract | List endpoint production-grade | tránh trả data quá lớn |

## 7. QUIZ

### Quick Check

1. Khi nào projection tốt hơn load full entity?
2. Derived query nên dừng ở mức nào?
3. Vì sao custom JPQL đôi khi lại dễ maintain hơn method name dài?

### Answer Key

1. Khi endpoint chỉ cần vài field và không cần entity graph đầy đủ.
2. Ở các lookup/filter đơn giản, còn logic dài thì nên chuyển strategy khác.
3. Vì intent query được viết tường minh thay vì nhét vào tên method quá dài.

## 8. NEXT STEPS

- Nối với `performance/profiling` để đo query bottleneck thực tế
- Hoặc sang `backend/http-api` để map projection thành response model
