<!-- tags: java, spring-boot -->
# ☕ Spring Boot Config — Profiles, Properties & Secrets

> Cấu hình là nơi nhiều project Java trở nên khó kiểm soát nhất. Bài này tập trung vào cách tách config theo môi trường, bind type-safe và tránh hardcode secrets vào source code.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 14 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Intermediate |
| **Use case** | Ứng dụng có nhiều môi trường dev/staging/prod |
| **Java focus** | profiles, `application.yml`, `@ConfigurationProperties` |
| **Prerequisites** | Spring Boot basics |

## 1. DEFINE

Hình dung service của bạn chạy ổn ở local nhưng lên staging thì trỏ sai database, đọc nhầm secret hoặc trộn lẫn config giữa hai môi trường chỉ vì một profile bật thiếu chủ ý. Spring Boot config chỉ trông đơn giản cho tới ngày boundary môi trường bắt đầu bị rò rỉ qua từng property.

Bài này đặt `Spring Boot Config — Profiles, Properties & Secrets` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Mục tiêu của config tốt

Config tốt cần:

- tách dữ liệu thay đổi khỏi code
- phân biệt rõ config theo môi trường
- giúp validate sai sót sớm
- không làm lộ secrets trong repo

### Actors

| Actor | Vai trò |
| --- | --- |
| `application.yml` | Base configuration |
| Profile-specific files | Override theo môi trường |
| `@ConfigurationProperties` | Bind config sang object type-safe |
| Environment variables / secret store | Cung cấp secret runtime |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Hardcode credential | Viết trực tiếp vào code/yaml commit lên repo | Đưa sang env hoặc secret manager |
| Config key rải rác | Dùng `@Value` bừa bãi | Gom theo properties object |
| Dev/prod behavior lệch khó trace | Không dùng profile rõ ràng | Tách file config theo môi trường |

Các failure mode trên nghe quen. Nhưng có trap: secrets commit vào git = credential leak, và profile activation order sai = wrong config. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Với Spring Boot Config — Profiles, Properties & Secrets, phần khó không nằm ở tên annotation hay package nữa mà ở flow thật của request, bean hoặc boundary. Sơ đồ dưới đây giúp kéo flow đó ra ánh sáng.

```text
application.yml
   │
   ├── application-dev.yml
   ├── application-staging.yml
   └── application-prod.yml
            │
            ▼
@ConfigurationProperties
            │
            ▼
typed config object
```

```text
code           <- stable behavior
config files   <- non-secret defaults
env/secrets    <- secret values per environment
```

## 3. CODE

Sơ đồ đã cho bạn thấy flow của Spring Boot Config — Profiles, Properties & Secrets. Bây giờ ta chuyển nó thành code Java/Spring đủ gần production để boundary không còn là khái niệm mơ hồ.

### Basic: base YAML structure

```yaml
# application.yml — Base configuration shared by all environments
spring:
  application:
    name: ordering-service

app:
  storage:
    bucket: local-exports
    signed-url-ttl-seconds: 900
```

Properties đã cover. Nhưng profiles cần environment separation — hãy split.

### Intermediate: profile-specific override

```yaml
# application-prod.yml — Production overrides
spring:
  datasource:
    url: ${DB_URL}
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}

app:
  storage:
    bucket: ${EXPORT_BUCKET}
    signed-url-ttl-seconds: 300
```

Profiles đã cover. Nhưng secrets cần vault/env vars — hãy externalize.

### Advanced: typed properties binding

```java
// ExportProperties.java — Strongly typed export configuration
package com.example.ordering.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * Configuration for export file delivery.
 *
 * @param bucket object storage bucket
 * @param signedUrlTtlSeconds TTL for signed URLs in seconds
 */
@ConfigurationProperties(prefix = "app.storage")
public record ExportProperties(String bucket, long signedUrlTtlSeconds) {
    public ExportProperties {
        if (bucket == null || bucket.isBlank()) {
            throw new IllegalArgumentException("bucket must not be blank");
        }
        if (signedUrlTtlSeconds <= 0) {
            throw new IllegalArgumentException("signedUrlTtlSeconds must be positive");
        }
    }
}
```

Bạn đã đi qua properties, profiles, và secrets. Bây giờ đến phần nguy hiểm: credential leak và profile order — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Spring Boot Config — Profiles, Properties & Secrets` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Nhét secret vào git-tracked YAML | Dùng env var hoặc secret manager |
| 2 | Dùng `@Value` rải rác khắp codebase | Gom config thành properties object |
| 3 | Không validate config nhập vào | Validate ngay trong `@ConfigurationProperties` |
| 4 | Profile dev/prod khác nhau nhưng không ghi rõ | Tách file và naming nhất quán |

Bạn đã đi qua Config & Secrets và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| External Config | https://docs.spring.io/spring-boot/reference/features/external-config.html |
| Profiles | https://docs.spring.io/spring-boot/reference/features/profiles.html |
| Configuration Properties | https://docs.spring.io/spring-boot/reference/features/external-config.html#features.external-config.typesafe-configuration-properties |

## 6. RECOMMEND

Khi các bẫy chính của `Spring Boot Config — Profiles, Properties & Secrets` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Secret manager | Hệ thống production nghiêm túc | Giảm rủi ro lộ credential |
| Config validation tests | Config phức tạp, nhiều env | Bắt lỗi sớm trước deploy |
| Actuator env/info | Cần quan sát config runtime | Debug môi trường dễ hơn |

## 7. QUIZ

### Quick Check

1. Vì sao `@ConfigurationProperties` thường tốt hơn `@Value` rải rác?
2. Secret nên nằm ở đâu thay vì hardcode vào repo?
3. Profiles giúp giải quyết vấn đề gì chính?

### Answer Key

1. Vì nó gom config theo domain và bind type-safe, dễ validate hơn.
2. Ở environment variables hoặc secret manager.
3. Tách hành vi/config theo môi trường một cách rõ ràng và kiểm soát được.

## 8. NEXT STEPS

- Đi tiếp sang `actuator/` để thấy config gắn với vận hành production
- Hoặc kết hợp với testing để verify config binding
