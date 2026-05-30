<!-- tags: java, gradle -->
# ☕ Gradle — Wrapper, Tasks, Dependency Management

> Gradle thường được chọn khi team muốn build nhanh, DSL linh hoạt và custom pipeline tốt hơn. Nhưng nếu coi nó như “script bash viết bằng Groovy/Kotlin” thì build sẽ rất khó kiểm soát. Bài này tập trung vào mental model đúng.

📅 Ngày tạo: 2026-03-28 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 14 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Intermediate |
| **Use case** | Quản lý build Java với Gradle |
| **Java focus** | wrapper, tasks, configurations, reproducible build |
| **Prerequisites** | Java fundamentals |

## 1. DEFINE

Hình dung CI vừa đỏ sau một thay đổi tưởng rất nhỏ ở `build.gradle`: task phụ thuộc chạy lệch thứ tự, dependency kéo sai version, còn local của bạn lại không tái hiện đúng lỗi trên pipeline. Đây là lúc Gradle thôi là công cụ build “cho có”. Nó trở thành nơi bạn phải hiểu workflow của project đang được lắp ghép ra sao.

Bài này đặt `Gradle — Wrapper, Tasks, Dependency Management` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Gradle nên được hiểu như thế nào?

Gradle là build system theo graph các task phụ thuộc lẫn nhau. DSL chỉ là cách mô tả graph đó.

### Actors

| Actor | Vai trò |
| --- | --- |
| Wrapper | khóa version Gradle cho project |
| Task | đơn vị công việc trong build graph |
| Configuration | nhóm dependency cho compile/test/runtime |
| Plugin | thêm task và convention cho project |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Mỗi máy dùng Gradle version khác nhau | không dùng wrapper | commit wrapper vào repo |
| Build script ngày càng khó đọc | custom logic nhồi thẳng vào root build | giữ convention rõ ràng |
| Dependency graph khó đoán | cấu hình không rõ `implementation`/`testImplementation` | chọn configuration đúng |

Các failure mode trên nghe quen. Nhưng có trap: Gradle wrapper version mismatch = build fail on CI, và implementation vs api scope sai = dependency invisible. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa mới chỉ khóa được tên của Gradle — Wrapper, Tasks, Dependency Management. Để khái niệm này bớt trừu tượng, ta cần nhìn nó ở dạng flow hoặc cấu trúc đủ cụ thể trước.

```text
gradlew
   │
   ▼
select project Gradle version
   │
   ▼
evaluate build scripts
   │
   ▼
resolve task graph
   │
   ▼
execute requested tasks
```

## 3. CODE

Flow của Gradle — Wrapper, Tasks, Dependency Management đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: minimal `build.gradle.kts`

```kotlin
// build.gradle.kts — Java project with reproducible wrapper-driven build
plugins {
    java
}

group = "com.example"
version = "1.0.0"

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(21))
    }
}

repositories {
    mavenCentral()
}

dependencies {
    testImplementation("org.junit.jupiter:junit-jupiter:5.11.0")
}

tasks.test {
    useJUnitPlatform()
}
```

Wrapper basics đã cover. Nhưng custom tasks cần Groovy/Kotlin DSL — hãy viết.

### Intermediate: Spring Boot + task mental model

```kotlin
// build.gradle.kts — Spring Boot build with dependency scopes
plugins {
    id("org.springframework.boot") version "3.3.2"
    id("io.spring.dependency-management") version "1.1.6"
    java
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-validation")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}

tasks.named("test") {
    dependsOn("classes")
}
```

Tasks đã cover. Nhưng build cache cần configuration — hãy optimize.

### Advanced: Java code the build graph is actually compiling

```java
// CustomerStatus.java — Sample Java type compiled by Gradle tasks
package com.example.gradlebuild;

public enum CustomerStatus {
    ACTIVE,
    SUSPENDED,
    DELETED
}
```

### Expert: wrapper-first workflow

```text
./gradlew test
  - always use project-defined Gradle version

./gradlew build
  - compile + test + package according to plugin conventions

./gradlew dependencies
  - inspect resolved dependency graph when conflict appears
```

Bạn đã đi qua wrapper, tasks, và cache. Bây giờ đến phần nguy hiểm: wrapper mismatch và scope confusion — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Gradle — Wrapper, Tasks, Dependency Management` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Chạy `gradle` thay vì `./gradlew` | dùng wrapper để build reproducible |
| 2 | Dồn business script vào root build file | tách convention hoặc giữ DSL gọn |
| 3 | Không phân biệt `implementation` với `testImplementation` | khai báo theo compile/runtime/test need |
| 4 | Debug dependency conflict bằng đoán mò | dùng `dependencies` hoặc `dependencyInsight` |

Bạn đã đi qua Gradle và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Gradle User Manual | https://docs.gradle.org/current/userguide/userguide.html |
| Gradle Wrapper | https://docs.gradle.org/current/userguide/gradle_wrapper.html |
| Building Java Projects | https://docs.gradle.org/current/userguide/building_java_projects.html |

## 6. RECOMMEND

Khi các bẫy chính của `Gradle — Wrapper, Tasks, Dependency Management` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Kotlin DSL | Team muốn type-safe build script | dễ maintain hơn script grow lớn |
| Build cache | CI và multi-module project | giảm thời gian build |
| Version catalog | dependency nhiều | quản lý version tập trung hơn |

## 7. QUIZ

### Quick Check

1. Vì sao luôn nên dùng `./gradlew`?
2. `task graph` giúp hiểu Gradle tốt hơn như thế nào?
3. Khi conflict dependency xảy ra, nên nhìn gì trước?

### Answer Key

1. Vì wrapper khóa đúng version Gradle cho mọi môi trường.
2. Vì Gradle thực chất chạy graph các task phụ thuộc nhau.
3. Xem resolved dependency graph bằng `dependencies` hoặc `dependencyInsight`.

## 8. NEXT STEPS

- Nối với `testing/junit` để thấy Gradle task `test` vận hành ra sao
- Hoặc sang `spring-boot/deployment` để nối build với packaging
