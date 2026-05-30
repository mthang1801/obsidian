<!-- tags: java, spring-security -->
# ☕ Spring Security — JWT Resource Server Basics

> JWT làm auth cho API stateless rất phổ biến, nhưng cũng rất dễ bị hiểu sai thành “chỉ cần decode token”. Bài này tập trung vào mental model đúng cho resource server.

📅 Ngày tạo: 2026-03-28 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 15 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Expert |
| **Use case** | Bảo vệ REST API bằng bearer token |
| **Java focus** | resource server, JWT claims, token validation, authority mapping |
| **Prerequisites** | Spring Security basics |

## 1. DEFINE

Hình dung token đã tới tay resource server, request thì có vẻ hợp lệ, nhưng claims không map đúng quyền, signature check không đi qua chỗ bạn nghĩ và một endpoint nhạy cảm đang được bảo vệ bằng assumption nhiều hơn là certainty. JWT đáng học khi nó không còn là buzzword của auth nữa mà là contract thật trước biên trust.

Bài này kéo resource server JWT về đúng bản chất của nó: một trust boundary cần hiểu đủ sâu trước khi chạm vào cấu hình chi tiết.

### Resource server cần làm gì?

Một JWT resource server cần:

- xác thực token hợp lệ
- kiểm tra claims quan trọng như `exp`, `iss`, `aud`
- map claims sang authority/role nội bộ
- từ chối request không hợp lệ một cách nhất quán

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Chỉ verify signature | Bỏ qua semantic claims | Validate `exp`, issuer, audience |
| Tin role từ token mù quáng | Mapping lỏng | Chuẩn hóa authority mapping |
| Dùng JWT cho mọi thứ | Không hiểu session vs token trade-off | Chọn theo architecture |

Các failure mode trên nghe cơ bản. Nhưng có trap: JWT validation thiếu issuer check = token forge, và symmetric key shared = secret compromise. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Với Spring Security — JWT Resource Server Basics, phần khó không nằm ở tên annotation hay package nữa mà ở flow thật của request, bean hoặc boundary. Sơ đồ dưới đây giúp kéo flow đó ra ánh sáng.

```text
Bearer token
   │
   ▼
decode + verify signature
   │
   ▼
validate claims
   │
   ▼
map authorities
   │
   ▼
authorize endpoint
```

## 3. CODE

Sơ đồ đã cho bạn thấy flow của Spring Security — JWT Resource Server Basics. Bây giờ ta chuyển nó thành code Java/Spring đủ gần production để boundary không còn là khái niệm mơ hồ.

### Basic: enable resource server

```java
// JwtSecurityConfiguration.java — Minimal JWT resource server configuration
package com.example.security;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class JwtSecurityConfiguration {
    @Bean
    public SecurityFilterChain jwtFilterChain(HttpSecurity http) throws Exception {
        http
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/actuator/health").permitAll()
                        .anyRequest().authenticated()
                )
                .oauth2ResourceServer(oauth -> oauth.jwt());

        return http.build();
    }
}
```

JWT basics đã cover. Nhưng resource server cần public key validation — hãy verify.

### Intermediate: explicit authority rule

```java
// JwtAdminAccessExample.java — Require a mapped authority for admin endpoints
package com.example.security;

import org.springframework.security.config.annotation.web.builders.HttpSecurity;

public final class JwtAdminAccessExample {
    private JwtAdminAccessExample() {
    }

    public static HttpSecurity apply(HttpSecurity http) throws Exception {
        return http.authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/admin/**").hasAuthority("SCOPE_admin")
                .anyRequest().authenticated()
        );
    }
}
```

Public key đã cover. Nhưng custom claim extraction cần converter — hãy map.

### Advanced: validation checklist

```text
1. Verify signature / key material
2. Check expiration
3. Check issuer and audience
4. Map claims to authorities intentionally
5. Return consistent 401/403 semantics
```

Bạn đã đi qua JWT, resource server, và claim mapping. Bây giờ đến phần nguy hiểm: missing issuer và key compromise — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Spring Security — JWT Resource Server Basics` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Decode token nhưng không verify đúng | Dùng resource server validation chuẩn |
| 2 | Không check issuer/audience | Áp semantic claim validation |
| 3 | Role mapping ad-hoc | Chuẩn hóa authority contract |
| 4 | Log token thô | Tránh lộ secret/credential material |

Bạn đã đi qua JWT Resource Server và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Spring Security JWT Resource Server | https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html |
| OAuth 2.0 Bearer Tokens | https://datatracker.ietf.org/doc/html/rfc6750 |
| JWT RFC | https://datatracker.ietf.org/doc/html/rfc7519 |

## 6. RECOMMEND

Khi các bẫy chính của `Spring Security — JWT Resource Server Basics` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Key rotation strategy | Token issuer production-grade | Giảm rủi ro key compromise |
| Audit logging | Endpoint nhạy cảm | Trace access decision tốt hơn |
| Method security | Rule sâu hơn endpoint | Tăng layer protection |

## 7. QUIZ

### Quick Check

1. Vì sao verify signature thôi là chưa đủ?
2. `401` và `403` khác nhau trong JWT API thế nào?
3. Mapping authority nên làm có chủ đích ở đâu?

### Answer Key

1. Vì token còn phải hợp lệ về `exp`, `iss`, `aud` và semantics khác.
2. `401` cho unauthenticated/invalid token, `403` cho authenticated nhưng thiếu quyền.
3. Ở security layer với contract claims rõ ràng, không map ad-hoc khắp nơi.

## 8. NEXT STEPS

- Batch sau có thể seed `oauth2/` hoặc method security
- Hoặc nối với observability để audit token-based access flow
