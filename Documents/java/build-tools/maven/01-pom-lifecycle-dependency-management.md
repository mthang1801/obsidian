<!-- tags: java, maven -->
# ☕ Maven — POM, Lifecycle, Dependency Management

> Maven không chỉ là công cụ “chạy `mvn package`”. Nó là nơi chuẩn hóa dependency graph, plugin execution và build lifecycle để project Java build được nhất quán giữa local, CI và production.

📅 Ngày tạo: 2026-03-28 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 14 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Intermediate |
| **Use case** | Quản lý build cho Java backend project |
| **Java focus** | `pom.xml`, scopes, lifecycle, plugin execution |
| **Prerequisites** | Java fundamentals |

## 1. DEFINE

Hình dung một dự án multi-module Java bắt đầu thêm plugin, profile và dependency nội bộ cho đủ loại nhu cầu. Mọi thứ vẫn build được, cho tới ngày lifecycle chạy lệch, transitive dependency kéo nhầm version và cả team không còn biết POM nào đang là nguồn sự thật. Bài này mở đúng ở điểm Maven bắt đầu biến từ cấu hình quen thuộc thành hệ thống cần được reasoning.

Bài này đặt `Maven — POM, Lifecycle, Dependency Management` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Maven giải quyết vấn đề gì?

Maven chuẩn hóa 4 phần:

- metadata project
- dependency graph
- build lifecycle
- plugin execution

### Actors

| Actor | Vai trò |
| --- | --- |
| `pom.xml` | nơi khai báo dependency, plugin, packaging |
| Lifecycle | chuỗi phase như `compile`, `test`, `package`, `verify` |
| Plugin | code thực thi trong từng phase |
| Dependency scope | quyết định dependency có mặt ở compile/test/runtime hay không |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Dependency conflict khó đoán | version bị kéo transitive lung tung | khóa version có chủ đích |
| Build local pass nhưng CI fail | plugin/config không ổn định | chuẩn hóa lifecycle và plugin |
| Dùng scope sai | `test` hoặc `provided` bị khai báo sai | chọn scope theo runtime thật |

Các failure mode trên nghe cơ bản. Nhưng có trap: dependency version conflict = classpath hell, và missing dependency scope = test lib in production. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa mới chỉ khóa được tên của Maven — POM, Lifecycle, Dependency Management. Để khái niệm này bớt trừu tượng, ta cần nhìn nó ở dạng flow hoặc cấu trúc đủ cụ thể trước.

```text
pom.xml
   │
   ├── project metadata
   ├── dependencies
   ├── plugins
   └── build configuration
```

```text
validate -> compile -> test -> package -> verify -> install
```

## 3. CODE

Flow của Maven — POM, Lifecycle, Dependency Management đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: minimal Spring Boot POM

```xml
<!-- pom.xml — Spring Boot project with dependency management -->
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.3.2</version>
        <relativePath/>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>inventory-service</artifactId>
    <version>1.0.0</version>
    <name>inventory-service</name>

    <properties>
        <java.version>21</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

POM basics đã cover. Nhưng lifecycle phases cần plugin binding — hãy configure.

### Intermediate: dependency management mindset

```xml
<!-- pom.xml — Manage internal dependency versions centrally -->
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>testcontainers-bom</artifactId>
            <version>1.20.1</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>postgresql</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

Lifecycle đã cover. Nhưng BOM cần dependency management — hãy centralize.

### Advanced: compiled Java code still needs build-tool conventions

```java
// OrderId.java — Simple Java type compiled and tested under Maven lifecycle
package com.example.build;

import java.util.Objects;

public record OrderId(String value) {
    public OrderId {
        Objects.requireNonNull(value, "value must not be null");
        if (value.isBlank()) {
            throw new IllegalArgumentException("value must not be blank");
        }
    }
}
```

### Expert: common lifecycle commands

```text
mvn test
  - compile main + test code
  - run unit/integration tests bound to surefire/failsafe

mvn package
  - produce jar/war artifact

mvn verify
  - run checks after packaging
  - useful in CI because quality gates thường bind tại đây
```

Bạn đã đi qua POM, lifecycle, và BOM. Bây giờ đến phần nguy hiểm: classpath hell và scope leak — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Maven — POM, Lifecycle, Dependency Management` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Nhét mọi version trực tiếp trong dependencies | dùng parent hoặc BOM để quản lý tập trung |
| 2 | Dùng `runtime` hay `test` scope sai | map scope theo nơi dependency thực sự cần |
| 3 | Chạy `package` rồi tưởng đã cover hết verify checks | dùng `verify` trong CI để chắc hơn |
| 4 | Plugin version trôi nổi theo môi trường | pin version hoặc dùng managed parent |

Bạn đã đi qua Maven và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Maven in 5 Minutes | https://maven.apache.org/guides/getting-started/maven-in-five-minutes.html |
| Introduction to the Build Lifecycle | https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html |
| Introduction to Dependency Mechanism | https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html |

## 6. RECOMMEND

Khi các bẫy chính của `Maven — POM, Lifecycle, Dependency Management` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Maven Wrapper | Mọi project team-shared | Đồng bộ Maven version giữa local và CI |
| Enforcer plugin | Team lớn hoặc multi-module | Chặn version drift và Java version mismatch |
| Surefire/Failsafe split | Có cả unit và integration test | Tách test phases rõ ràng |

## 7. QUIZ

### Quick Check

1. `dependencyManagement` khác gì `dependencies`?
2. Vì sao CI thường nên chạy `mvn verify` thay vì chỉ `mvn package`?
3. Khi nào nên dùng `test` scope?

### Answer Key

1. `dependencyManagement` quản lý version/chính sách, còn `dependencies` mới thật sự add dependency vào module.
2. Vì `verify` bao phủ thêm các quality checks sau packaging.
3. Khi dependency chỉ phục vụ test và không cần ở runtime production.

## 8. NEXT STEPS

- Nối với `testing/junit` để thấy Maven lifecycle tác động lên test run thế nào
- Hoặc đi sang `spring-boot/basics` để thấy parent POM được dùng thực chiến
