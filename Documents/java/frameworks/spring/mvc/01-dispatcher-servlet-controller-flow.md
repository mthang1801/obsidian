<!-- tags: java, spring -->
# ☕ Spring MVC — DispatcherServlet & Controller Flow

> Trước khi dùng Spring Boot để build REST API hàng loạt, nên hiểu request thật sự đi qua Spring MVC ra sao. `DispatcherServlet` là trung tâm điều phối request, mapping, binding và response rendering trong web stack cổ điển của Spring.

📅 Ngày tạo: 2026-03-28 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 15 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Advanced |
| **Use case** | Hiểu request lifecycle của Spring MVC |
| **Java focus** | `DispatcherServlet`, controller, binding, model/view |
| **Prerequisites** | DI basics, beans, HTTP fundamentals |

## 1. DEFINE

Hình dung một request vào hệ thống và trước khi chạm tới business logic, nó đã đi qua handler mapping, argument resolver, validation và exception handler. Nếu không nhìn được flow đó, bạn sẽ luôn sửa Spring MVC theo kiểu mò mẫm. Bài này mở đúng ở chỗ request lifecycle cần được kéo ra khỏi hậu trường.

Bài này đặt `Spring MVC — DispatcherServlet & Controller Flow` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### `DispatcherServlet` làm gì?

Nó là front controller của Spring MVC, chịu trách nhiệm:

- nhận HTTP request
- tìm handler/controller phù hợp
- binding request data
- invoke controller
- chọn cách render response

### Actors

| Actor | Vai trò |
| --- | --- |
| `DispatcherServlet` | front controller điều phối request |
| Handler mapping | tìm controller/method phù hợp |
| Controller | xử lý request ở web layer |
| View resolver / message converter | render HTML hoặc serialize response |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Controller ôm business logic | boundary web/app bị lẫn | giữ controller mỏng |
| Response format không nhất quán | mapping lỗi rải rác | gom exception handling |
| Binding lộ model nội bộ | dùng thẳng entity/domain object | tách request/response DTO |

Các failure mode trên nghe dễ tránh. Nhưng có trap: handler mapping order sai = wrong controller xử lý, và @ResponseBody thiếu = trả view thay JSON. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Với Spring MVC — DispatcherServlet & Controller Flow, phần khó không nằm ở tên annotation hay package nữa mà ở flow thật của request, bean hoặc boundary. Sơ đồ dưới đây giúp kéo flow đó ra ánh sáng.

```text
HTTP request
   │
   ▼
DispatcherServlet
   │
   ├── HandlerMapping
   ├── Argument binding
   ├── Controller invocation
   └── View / JSON rendering
   ▼
HTTP response
```

## 3. CODE

Sơ đồ đã cho bạn thấy flow của Spring MVC — DispatcherServlet & Controller Flow. Bây giờ ta chuyển nó thành code Java/Spring đủ gần production để boundary không còn là khái niệm mơ hồ.

### Basic: MVC controller

```java
// GreetingController.java — Simple Spring MVC controller returning a JSON response
package com.example.springmvc;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class GreetingController {
    @GetMapping("/greet")
    public GreetingResponse greet(@RequestParam(defaultValue = "world") String name) {
        return new GreetingResponse("hello " + name);
    }
}
```

```java
// GreetingResponse.java — Response DTO for MVC layer
package com.example.springmvc;

public record GreetingResponse(String message) {
}
```

DispatcherServlet flow đã cover. Nhưng handler interceptors cần chain — hãy thêm.

### Intermediate: request DTO binding

```java
// CreateTaskRequest.java — Request model bound from JSON payload
package com.example.springmvc;

import jakarta.validation.constraints.NotBlank;

public record CreateTaskRequest(@NotBlank String title) {
}
```

```java
// TaskController.java — Thin controller delegating to application service
package com.example.springmvc;

import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/tasks")
public class TaskController {
    private final TaskApplicationService taskApplicationService;

    public TaskController(TaskApplicationService taskApplicationService) {
        this.taskApplicationService = taskApplicationService;
    }

    @PostMapping
    public TaskResponse create(@Valid @RequestBody CreateTaskRequest request) {
        return taskApplicationService.create(request);
    }
}
```

Interceptors đã cover. Nhưng exception handler cần @ControllerAdvice — hãy centralize.

### Advanced: controller flow mental model

```text
request arrives
  -> DispatcherServlet selects handler
  -> request params/body get bound to method arguments
  -> controller delegates to service
  -> return value becomes JSON/view through converter or resolver
```

Bạn đã đi qua servlet, interceptors, và error handling. Bây giờ đến phần nguy hiểm: mapping order và missing annotation — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Spring MVC — DispatcherServlet & Controller Flow` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Nhét business rule trực tiếp vào controller | chuyển sang service/use case |
| 2 | Bind thẳng entity/domain object từ request | tạo request DTO riêng |
| 3 | Tự render lỗi khác nhau ở từng controller | dùng exception handler tập trung |
| 4 | Không hiểu binding/validation lifecycle | giữ request model rõ ràng và validate tại web boundary |

Bạn đã đi qua Spring MVC và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Spring Web MVC | https://docs.spring.io/spring-framework/reference/web/webmvc.html |
| DispatcherServlet Javadoc | https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/web/servlet/DispatcherServlet.html |
| Validation in Spring MVC | https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-validation.html |

## 6. RECOMMEND

Khi các bẫy chính của `Spring MVC — DispatcherServlet & Controller Flow` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| `@RestControllerAdvice` | API lớn hơn vài controller | giữ error contract nhất quán |
| Spring Boot web starter | Muốn bootstrap MVC stack nhanh | giảm config thủ công |
| OpenAPI docs | API có client team khác dùng | contract rõ và dễ tích hợp |

## 7. QUIZ

### Quick Check

1. Vai trò chính của `DispatcherServlet` là gì?
2. Vì sao controller nên mỏng?
3. Khi nào nên tách request DTO khỏi domain model?

### Answer Key

1. Nó là front controller điều phối mapping, binding, invocation và rendering response.
2. Vì controller chỉ nên xử lý web boundary, không ôm business logic.
3. Gần như luôn luôn ở public API để tránh lộ shape nội bộ và giảm coupling.

## 8. NEXT STEPS

- Đi tiếp sang [Spring Boot Web](../../spring-boot/web/01-rest-controller-validation.md)
- Hoặc nối với [Spring Security Basics](../../spring-security/basics/01-authentication-authorization-filter-chain.md)
