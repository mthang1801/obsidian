<!-- tags: java, spring-boot -->
# ☕ Spring Boot Deployment — Packaging, Containers & Runtime Tuning

> Một Spring Boot app chạy local ổn chưa đủ. Bài này tập trung vào cách đóng gói và vận hành service trong container sao cho predict được hơn ở production.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 15 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Advanced |
| **Use case** | Build artifact, container deploy, runtime tuning cơ bản |
| **Java focus** | fat jar, Docker layering, env config, JVM options |
| **Prerequisites** | Spring Boot config, actuator |

## 1. DEFINE

Hình dung cùng một service Spring Boot chạy mượt ở máy dev nhưng lên container thì startup chậm, memory footprint phình ra và runtime behavior thay đổi theo image hoặc resource limit. Deployment chỉ đáng học khi bạn chấp nhận rằng “ứng dụng chạy được” và “ứng dụng vận hành đúng” là hai cột mốc khác nhau.

Bài này đặt `Spring Boot Deployment — Packaging, Containers & Runtime Tuning` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Deployment cần quan tâm gì?

Triển khai Spring Boot production thường xoay quanh 4 câu hỏi:

- artifact nào sẽ được build và chạy
- container image có đủ gọn và cache-friendly không
- config/runtime options được inject thế nào
- app có startup/shutdown và memory profile phù hợp không

### Actors

| Actor | Vai trò |
| --- | --- |
| Build artifact | JAR hoặc layered image để deploy |
| Container image | Runtime unit để đưa lên orchestration platform |
| Environment config | Giá trị thay đổi theo môi trường |
| JVM options | Ảnh hưởng startup, memory, GC, diagnostics |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Image quá nặng | Build layer không tối ưu | Tách layer và giữ base image gọn |
| OOM khó đoán | Không set runtime/memory expectation rõ | Tune JVM/container memory có chủ đích |
| Shutdown bẩn | Không xử lý signal/lifecycle | Dùng graceful shutdown + readiness |

Các failure mode trên nghe cơ bản. Nhưng có trap: fat JAR trên Alpine = glibc mismatch, và JVM heap quá lớn trong container = OOMKilled. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Với Spring Boot Deployment — Packaging, Containers & Runtime Tuning, phần khó không nằm ở tên annotation hay package nữa mà ở flow thật của request, bean hoặc boundary. Sơ đồ dưới đây giúp kéo flow đó ra ánh sáng.

```text
source code
   │
   ▼
build jar
   │
   ▼
container image
   │
   ▼
runtime env + JVM opts
   │
   ▼
orchestrated service
```

```text
build layers
   ├── dependencies
   ├── snapshot dependencies
   ├── loader
   └── application code
```

## 3. CODE

Sơ đồ đã cho bạn thấy flow của Spring Boot Deployment — Packaging, Containers & Runtime Tuning. Bây giờ ta chuyển nó thành code Java/Spring đủ gần production để boundary không còn là khái niệm mơ hồ.

### Basic: jar packaging

```xml
<!-- pom.xml — Spring Boot repackage plugin -->
<build>
  <plugins>
    <plugin>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-maven-plugin</artifactId>
    </plugin>
  </plugins>
</build>
```

Packaging đã cover. Nhưng container cần Jib/Buildpack — hãy containerize.

### Intermediate: container runtime env

```dockerfile
# Dockerfile — Simple production-oriented Spring Boot image
FROM eclipse-temurin:21-jre
WORKDIR /app
COPY target/ordering-service.jar app.jar
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

Container đã cover. Nhưng JVM tuning cần cgroup-aware flags — hãy tune.

### Advanced: runtime tuning hints

```bash
# Example runtime options
JAVA_TOOL_OPTIONS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75 -Dfile.encoding=UTF-8"
SPRING_PROFILES_ACTIVE=prod
SERVER_SHUTDOWN=graceful
```

### Expert: lifecycle hook for graceful startup and shutdown

```java
// RuntimeLifecycleLogger.java — Observe startup and shutdown phases explicitly
package com.example.ordering.runtime;

import org.springframework.context.event.ContextClosedEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

@Component
public class RuntimeLifecycleLogger {
    @EventListener
    public void onShutdown(ContextClosedEvent event) {
        System.out.println("application context is shutting down gracefully");
    }
}
```

Bạn đã đi qua packaging, containers, và JVM tuning. Bây giờ đến phần nguy hiểm: glibc mismatch và OOM — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Spring Boot Deployment — Packaging, Containers & Runtime Tuning` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Image build mỗi lần invalidate toàn bộ cache | Tách dependency/application layers |
| 2 | Không khai báo profile/runtime opts rõ | Dùng env vars nhất quán |
| 3 | Không kiểm tra graceful shutdown | Kết hợp readiness + shutdown config |
| 4 | Đẩy image nặng không cần thiết | Chọn base image gọn và runtime-only |

Bạn đã đi qua Deployment và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Spring Boot Container Images | https://docs.spring.io/spring-boot/reference/packaging/container-images/ |
| Maven Plugin | https://docs.spring.io/spring-boot/docs/current/maven-plugin/reference/htmlsingle/ |
| JVM Container Awareness | https://developers.redhat.com/articles/2023/03/07/tuning-jvm-container-environments |

## 6. RECOMMEND

Khi các bẫy chính của `Spring Boot Deployment — Packaging, Containers & Runtime Tuning` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Buildpacks | Muốn standard hóa image build | Giảm Dockerfile maintenance |
| Distroless image | Security hardening cao hơn | Giảm attack surface |
| Startup probe tuning | App khởi động chậm | Tránh restart giả |

## 7. QUIZ

### Quick Check

1. Vì sao deployment không nên chỉ dừng ở “jar build được”?
2. JVM/container runtime options ảnh hưởng gì?
3. Vì sao graceful shutdown liên quan trực tiếp đến deployment quality?

### Answer Key

1. Vì artifact chỉ là một phần; runtime behavior mới quyết định ổn định production.
2. Chúng ảnh hưởng memory, startup, GC và diagnostics.
3. Vì nếu shutdown bẩn, request dở dang và state không nhất quán dễ xảy ra khi deploy/scale.

## 8. NEXT STEPS

- Kết hợp với actuator/health để hoàn thiện readiness-liveness-deployment loop
- Batch sau có thể seed sâu hơn về Docker layering hoặc buildpacks
