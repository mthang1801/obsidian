<!-- tags: java, spring-security -->
# ☕ Spring Security — OAuth2 Login & SSO Mental Model

> OAuth2 login thường bị hiểu sai thành “JWT nhưng redirect nhiều hơn”. Bài này tập trung vào mental model SSO, identity provider và điểm khác nhau giữa login flow với resource server validation.

📅 Ngày tạo: 2026-03-28 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 15 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Expert |
| **Use case** | SSO, social login, enterprise identity integration |
| **Java focus** | OAuth2 login, identity provider, redirect flow, session after login |
| **Prerequisites** | Spring Security basics, JWT basics |

## 1. DEFINE

Hình dung lần đầu bạn nối SSO vào ứng dụng Spring và mọi thứ có vẻ chỉ là vài redirect, vài config property. Rồi callback hỏng ở một môi trường, principal mang shape khác bạn tưởng, và cả flow login bắt đầu giống một mê cung hơn là một feature. OAuth2 chỉ bớt đáng sợ khi mental model của flow đủ sáng.

Bài này đặt `Spring Security — OAuth2 Login & SSO Mental Model` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### OAuth2 login khác JWT resource server thế nào?

| Topic | OAuth2 Login | JWT Resource Server |
| --- | --- | --- |
| Mục tiêu | Người dùng đăng nhập qua IdP | API xác thực bearer token |
| Flow | Redirect-based | Token presented directly |
| State | Thường tạo session sau login | Thường stateless |
| Actor chính | Browser + IdP + app | Client + API + token issuer |

### Actors

| Actor | Vai trò |
| --- | --- |
| Browser | Thực hiện redirect flow |
| Identity Provider | Xác thực người dùng |
| Application | Nhận callback và tạo security context/session |
| User | Chủ thể đăng nhập |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Trộn login flow với API token validation | Mental model lẫn | Tách rõ OAuth2 login vs resource server |
| Redirect URI sai | Config không đồng bộ | Chuẩn hóa callback contract |
| Không kiểm soát post-login mapping | User principal khó dùng | Chuẩn hóa user mapping sau login |

Các failure mode trên nghe quen. Nhưng có trap: redirect URI mismatch = OAuth error, và access token stored in localStorage = XSS steal. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Với Spring Security — OAuth2 Login & SSO Mental Model, phần khó không nằm ở tên annotation hay package nữa mà ở flow thật của request, bean hoặc boundary. Sơ đồ dưới đây giúp kéo flow đó ra ánh sáng.

```text
user -> app -> redirect to IdP
               │
               ▼
         user authenticates
               │
               ▼
        IdP redirects back
               │
               ▼
      app establishes session/context
```

```text
OAuth2 login = user interactive flow
JWT resource server = API token verification flow
```

## 3. CODE

Sơ đồ đã cho bạn thấy flow của Spring Security — OAuth2 Login & SSO Mental Model. Bây giờ ta chuyển nó thành code Java/Spring đủ gần production để boundary không còn là khái niệm mơ hồ.

### Basic: enable OAuth2 login

```java
// OAuth2LoginConfiguration.java — Minimal OAuth2 login setup
package com.example.security;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class OAuth2LoginConfiguration {
    @Bean
    public SecurityFilterChain oauth2LoginChain(HttpSecurity http) throws Exception {
        http
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/login", "/error").permitAll()
                        .anyRequest().authenticated()
                )
                .oauth2Login();

        return http.build();
    }
}
```

OAuth2 login đã cover. Nhưng SSO cần session management — hãy integrate.

### Intermediate: map login success outcome

```java
// OAuth2UserView.java — Simplified view after successful login
package com.example.security;

public record OAuth2UserView(String email, String displayName, String provider) {
}
```

SSO đã cover. Nhưng custom OAuth2UserService cần attribute mapping — hãy extend.

### Advanced: post-login checklist

```text
1. Verify redirect URI contract
2. Map external identity to internal user record
3. Define session / token strategy after login
4. Handle login failure path consistently
5. Audit sensitive login events
```

Bạn đã đi qua OAuth2, SSO, và user mapping. Bây giờ đến phần nguy hiểm: redirect URI và token storage — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Spring Security — OAuth2 Login & SSO Mental Model` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Tưởng OAuth2 login thay luôn API auth model | Tách interactive login với API security |
| 2 | Callback URI config lệch | Đồng bộ IdP và app config |
| 3 | Không map identity về internal user model | Chuẩn hóa user provisioning/linking |
| 4 | Bỏ qua failure/audit path | Ghi nhận event đăng nhập quan trọng |

Bạn đã đi qua OAuth2 SSO và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Spring Security OAuth2 Login | https://docs.spring.io/spring-security/reference/servlet/oauth2/login/index.html |
| OAuth 2.0 Overview | https://datatracker.ietf.org/doc/html/rfc6749 |
| OpenID Connect Core | https://openid.net/specs/openid-connect-core-1_0.html |

## 6. RECOMMEND

Khi các bẫy chính của `Spring Security — OAuth2 Login & SSO Mental Model` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| OIDC user mapping | SSO production-grade | Chuẩn hóa claim-to-user mapping |
| Logout strategy | Có nhiều apps/session | Tránh session leak/confusion |
| Security event audit | Compliance hoặc incident response | Trace login issue rõ hơn |

## 7. QUIZ

### Quick Check

1. OAuth2 login khác resource server ở điểm cốt lõi nào?
2. Vì sao redirect URI là điểm nhạy cảm?
3. Sau login thành công, app thường cần làm gì thêm?

### Answer Key

1. OAuth2 login là interactive user login flow, còn resource server là API token validation flow.
2. Vì sai callback contract dễ làm flow lỗi hoặc mở rủi ro redirect/config mismatch.
3. Map external identity về internal user/session strategy một cách rõ ràng.

## 8. NEXT STEPS

- Có thể nối tiếp bằng bài thực chiến OIDC/JWT hybrid architecture
- Hoặc quay lại Spring Boot web/security để hoàn thiện full auth flow
