<!-- tags: java, spring-security -->
# ☕ Spring Security — Authentication, Authorization & Filter Chain

> Nếu không nắm filter chain và ranh giới giữa authentication với authorization, Spring Security sẽ luôn trông “ma thuật”. Bài này tập trung vào mental model trước khi đi vào JWT hay OAuth2.

📅 Ngày tạo: 2026-03-28 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 15 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Advanced |
| **Use case** | Protect API endpoints, user identity, role/permission checks |
| **Java focus** | security filter chain, authn vs authz, request security |
| **Prerequisites** | Spring Boot web, validation, config |

## 1. DEFINE

Hình dung request bị chặn trước khi vào controller nhưng không ai trong team chắc nó bị chặn ở đâu: authentication chưa chạy, authority map sai, hay filter chain đã đi nhầm nhánh. Spring Security basics chỉ đáng học khi bạn cần nhìn security flow như một hệ thống thật, không như chuỗi annotation rời.

Bài này đặt `Spring Security — Authentication, Authorization & Filter Chain` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Authentication và Authorization khác gì?

| Concept | Câu hỏi nó trả lời | Ví dụ |
| --- | --- | --- |
| Authentication | “Bạn là ai?” | user login, token validation |
| Authorization | “Bạn được phép làm gì?” | role/permission check |

### Filter chain là gì?

Spring Security chèn các filter vào request pipeline để:

- xác định identity của request
- nạp security context
- áp rule truy cập endpoint
- trả lỗi chuẩn khi request không đủ quyền

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Trộn authn và authz | Rule khó debug | Tách từng tầng rõ |
| Mở endpoint nhạy cảm ngoài ý muốn | Rule chain không explicit | Khai báo matcher rõ ràng |
| Tin payload token mù quáng | Không validate đúng | Kiểm tra signature và claims |

Các failure mode trên nghe dễ tránh. Nhưng có trap: filter chain order sai = bypass authentication, và permitAll mismatch = 403 unexpected. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Với Spring Security — Authentication, Authorization & Filter Chain, phần khó không nằm ở tên annotation hay package nữa mà ở flow thật của request, bean hoặc boundary. Sơ đồ dưới đây giúp kéo flow đó ra ánh sáng.

```text
HTTP request
   │
   ▼
security filter chain
   │
   ├── authenticate identity
   ├── populate security context
   ├── authorize request
   └── pass / reject
```

```text
authentication -> identity established
authorization  -> access decision made
```

## 3. CODE

Sơ đồ đã cho bạn thấy flow của Spring Security — Authentication, Authorization & Filter Chain. Bây giờ ta chuyển nó thành code Java/Spring đủ gần production để boundary không còn là khái niệm mơ hồ.

### Basic: declare a security filter chain

```java
// SecurityConfiguration.java — Minimal filter chain configuration
package com.example.security;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class SecurityConfiguration {
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .csrf(csrf -> csrf.disable())
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/actuator/health").permitAll()
                        .requestMatchers("/api/admin/**").hasRole("ADMIN")
                        .anyRequest().authenticated()
                )
                .httpBasic(Customizer.withDefaults());

        return http.build();
    }
}
```

Authentication đã cover. Nhưng authorization cần filter chain — hãy configure.

### Intermediate: custom principal view

```java
// CurrentUserView.java — Simplified authenticated user view
package com.example.security;

public record CurrentUserView(String username, String role) {
}
```

Filter chain đã cover. Nhưng custom filter cần OncePerRequestFilter — hãy extend.

### Advanced: security checklist for request boundary

```text
1. Decide public vs protected endpoints explicitly
2. Validate identity material correctly
3. Keep authorization rules close to resource boundaries
4. Return consistent unauthorized / forbidden responses
5. Audit sensitive actions with correlation metadata
```

Bạn đã đi qua auth, filter chain, và custom filters. Bây giờ đến phần nguy hiểm: filter order bypass và permitAll confusion — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Spring Security — Authentication, Authorization & Filter Chain` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Dùng matcher quá rộng | Khai báo endpoint scope explicit |
| 2 | Nhầm `401` với `403` | Phân biệt unauthenticated và unauthorized |
| 3 | Tắt CSRF/CORS mà không hiểu bối cảnh | Chỉ disable khi đúng architecture |
| 4 | Security rule rải rác khó trace | Tập trung config hoặc policy rõ ràng |

Bạn đã đi qua Spring Security và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Spring Security Reference | https://docs.spring.io/spring-security/reference/ |
| Authorize HTTP Requests | https://docs.spring.io/spring-security/reference/servlet/authorization/authorize-http-requests.html |
| Security Filter Chain | https://docs.spring.io/spring-security/reference/servlet/architecture.html |

## 6. RECOMMEND

Khi các bẫy chính của `Spring Security — Authentication, Authorization & Filter Chain` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| JWT resource server | API stateless | Chuẩn hóa token-based auth |
| OAuth2 login | SSO / social login | Tận dụng provider identity |
| Method security | Rule theo use case sâu hơn | Bổ sung layer protection |

## 7. QUIZ

### Quick Check

1. Authentication và authorization khác nhau thế nào?
2. Vì sao filter chain là mental model quan trọng trong Spring Security?
3. Khi nào nên phân biệt rõ `401` và `403`?

### Answer Key

1. Authentication xác định identity, authorization quyết định quyền truy cập.
2. Vì request security trong Spring đi qua chuỗi filter chứ không phải một “magic switch”.
3. Khi cần trả semantics đúng cho client và debug access issue chính xác.

## 8. NEXT STEPS

- Batch sau có thể seed `jwt/` hoặc `oauth2/`
- Hoặc nối với `expert/observability` để audit security events tốt hơn
