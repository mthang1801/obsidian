<!-- tags: java, backend -->
# ☕ Java Backend — REST API, Validation, Error Contracts

> Một REST API dùng được lâu không chỉ nằm ở controller trả JSON, mà ở contract rõ ràng: input validation, HTTP semantics, error response nhất quán và boundary sạch giữa web layer với service layer.

📅 Ngày tạo: 2026-03-28 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 15 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Advanced |
| **Use case** | Xây REST API cho backend Java/Spring |
| **Java focus** | DTO, Bean Validation, exception handler, response contract |
| **Prerequisites** | Spring Boot web, validation basics |

## 1. DEFINE

Hình dung một endpoint tạo đơn hàng vừa được client mobile gọi thử. Request sai một field, service trả về 400 nhưng payload lỗi mỗi nơi một kiểu, message thì nửa kỹ thuật nửa nghiệp vụ, còn log phía server không đủ để biết boundary hỏng ở đâu. Bài toán lúc này không phải chỉ là “có API chạy được”, mà là làm cho HTTP contract đủ rõ để người ngoài và người on-call cùng hiểu chuyện gì vừa xảy ra.

Bài này đặt `Java Backend — REST API, Validation, Error Contracts` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Web layer nên chịu trách nhiệm gì?

Web layer nên:

- parse request
- validate input contract
- map lỗi sang HTTP response rõ nghĩa
- gọi application/service layer

Web layer không nên:

- nhét business logic dày đặc
- tự xử lý transaction tùy tiện
- trả lỗi tùy hứng theo từng controller

### Invariants

| Quy tắc | Ý nghĩa |
| --- | --- |
| Request DTO khác domain model | tránh lộ structure nội bộ |
| Validation ở biên hệ thống | fail fast trước khi vào business flow |
| Error response nhất quán | client dễ xử lý hơn |

Các failure mode trên nghe rõ. Nhưng có trap: error response không consistent = client parsing vỡ, và validation chỉ server-side = UX lag. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa mới chỉ khóa được tên của Java Backend — REST API, Validation, Error Contracts. Để khái niệm này bớt trừu tượng, ta cần nhìn nó ở dạng flow hoặc cấu trúc đủ cụ thể trước.

```text
HTTP request
   │
   ▼
Controller + DTO validation
   │
   ▼
Application service
   │
   ▼
Domain / persistence
   │
   ▼
HTTP response or mapped error
```

## 3. CODE

Khi boundary của Java Backend — REST API, Validation, Error Contracts đã rõ trên sơ đồ, phần còn lại là đưa nó vào code sao cho những quyết định đúng không chỉ tồn tại trên slide mà tồn tại trong class và method thật.

### Basic: DTO + controller

```java
// CreateCustomerRequest.java — Request contract validated at the edge
package com.example.customer.api;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

public record CreateCustomerRequest(
        @NotBlank String name,
        @Email String email
) {
}
```

```java
// CustomerController.java — Thin controller delegating to application service
package com.example.customer.api;

import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/customers")
public class CustomerController {
    private final CustomerApplicationService service;

    public CustomerController(CustomerApplicationService service) {
        this.service = service;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public CustomerResponse create(@Valid @RequestBody CreateCustomerRequest request) {
        return service.createCustomer(request);
    }
}
```

REST basics đã cover. Nhưng validation contracts cần schema — hãy define.

### Intermediate: consistent error contract

```java
// ApiError.java — Stable error payload for client handling
package com.example.shared.api;

import java.time.Instant;
import java.util.List;

public record ApiError(
        String code,
        String message,
        List<String> details,
        Instant timestamp
) {
}
```

```java
// GlobalExceptionHandler.java — Centralized mapping from exceptions to HTTP responses
package com.example.shared.api;

import java.time.Instant;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiError> handleValidation(MethodArgumentNotValidException ex) {
        List<String> details = ex.getBindingResult().getFieldErrors().stream()
                .map(error -> error.getField() + ": " + error.getDefaultMessage())
                .toList();

        return ResponseEntity.badRequest().body(new ApiError(
                "VALIDATION_ERROR",
                "Request payload is invalid",
                details,
                Instant.now()
        ));
    }
}
```

Contracts đã cover. Nhưng error codes cần RFC 7807 — hãy standardize.

### Advanced: service boundary mindset

```text
Controller:
  - knows HTTP and request/response DTO
  - does not know repository details

Application service:
  - coordinates use case
  - returns response model or throws business exception

Exception handler:
  - converts business/validation exceptions to stable API contract
```

Bạn đã đi qua REST, validation, và error codes. Bây giờ đến phần nguy hiểm: inconsistent errors và missing validation — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Backend — REST API, Validation, Error Contracts` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Dùng entity JPA làm request/response DTO | tách DTO riêng cho API boundary |
| 2 | Mỗi controller trả lỗi một kiểu | gom về `@RestControllerAdvice` |
| 3 | Nhét business rule vào controller | đẩy sang application/service layer |
| 4 | Không version hóa hay ổn định error code | đặt `code` rõ nghĩa và dùng nhất quán |

Bạn đã đi qua REST API Contracts và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Spring Web MVC | https://docs.spring.io/spring-framework/reference/web/webmvc.html |
| Bean Validation Spec | https://beanvalidation.org/ |
| RFC 9110 HTTP Semantics | https://www.rfc-editor.org/rfc/rfc9110 |

## 6. RECOMMEND

Khi các bẫy chính của `Java Backend — REST API, Validation, Error Contracts` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Problem Details RFC 9457 | API public-facing | Chuẩn hóa error format |
| OpenAPI contract | Client teams nhiều | Đồng bộ docs và codegen |
| Request/response logging policy | Production debugging | Trace issue mà không lộ dữ liệu nhạy cảm |

## 7. QUIZ

### Quick Check

1. Vì sao không nên trả thẳng entity JPA qua API?
2. `@RestControllerAdvice` giải quyết vấn đề gì?
3. Validation nên đặt ở đâu để fail fast?

### Answer Key

1. Vì entity là model persistence, không nên ràng buộc trực tiếp với contract public.
2. Nó giúp map lỗi tập trung và giữ response nhất quán.
3. Ở biên request, ngay tại DTO/controller layer.

## 8. NEXT STEPS

- Nối với `spring-data/jpa` để thấy persistence boundary phía sau controller
- Hoặc sang `spring-security/basics` để khóa access cho các endpoint
