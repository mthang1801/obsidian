<!-- tags: java, spring-boot, web -->
# ☕ Spring Boot Web — REST Controller & Validation

> Đây là bài nền cho web layer: nhận request bằng DTO, validate ở boundary, chuyển vào service và trả response ổn định thay vì để controller ôm hết logic.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 14 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Intermediate |
| **Use case** | Build JSON API với Spring Boot |
| **Java focus** | `@RestController`, DTO, `@Valid`, `@ControllerAdvice` |
| **Prerequisites** | Spring Boot basics |

## 1. DEFINE

Hình dung một controller trông rất gọn cho tới lúc bạn phải thêm validation, error handling và mapping response nhất quán cho nhiều client khác nhau. Từ khoảnh khắc đó, web layer không còn là chỗ gắn annotation cho đủ. Nó là boundary đầu tiên quyết định service của bạn nói chuyện với bên ngoài ra sao.

Bài này đặt `Spring Boot Web — REST Controller & Validation` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Web layer nên làm gì?

Web layer nên:

- parse request
- validate input ở boundary
- map sang command/use case
- trả response contract nhất quán

Web layer không nên:

- nhúng SQL
- viết business rule phức tạp
- expose entity persistence trực tiếp ra ngoài

### Actors

| Actor | Vai trò |
| --- | --- |
| Controller | Nhận HTTP request và gọi use case |
| Request DTO | Validate input |
| Service / Use case | Chứa business logic |
| Exception handler | Chuẩn hóa error response |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Controller quá béo | Chứa cả validation thủ công + rule nghiệp vụ | Đẩy nghiệp vụ sang service |
| Error response mỗi endpoint mỗi kiểu | Không có global handler | Dùng `@ControllerAdvice` |
| Entity bị lộ ra API | Trả trực tiếp JPA entity | Dùng DTO/response model |

Các failure mode trên nghe rõ. Nhưng có trap: @Valid thiếu trên nested object = validation bypass, và MethodArgumentNotValidException không handle = 500 error. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Với Spring Boot Web — REST Controller & Validation, phần khó không nằm ở tên annotation hay package nữa mà ở flow thật của request, bean hoặc boundary. Sơ đồ dưới đây giúp kéo flow đó ra ánh sáng.

```text
HTTP Request
   │
   ▼
Controller
   │  @Valid DTO
   ▼
Application Service
   │
   ▼
Response DTO
   │
   ▼
HTTP Response
```

```text
Validation failure
   │
   ▼
MethodArgumentNotValidException
   │
   ▼
@ControllerAdvice
   │
   ▼
{ code, message, fieldErrors[] }
```

## 3. CODE

Sơ đồ đã cho bạn thấy flow của Spring Boot Web — REST Controller & Validation. Bây giờ ta chuyển nó thành code Java/Spring đủ gần production để boundary không còn là khái niệm mơ hồ.

### Basic: request DTO with bean validation

```java
// CreateCustomerRequest.java — Request DTO with validation constraints
package com.example.customer.api;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * Request payload for customer creation.
 *
 * @param email customer email
 * @param fullName display name
 */
public record CreateCustomerRequest(
        @NotBlank @Email String email,
        @NotBlank @Size(min = 2, max = 100) String fullName
) {
}
```

REST controller đã cover. Nhưng validation cần @Valid + BindingResult — hãy validate.

### Intermediate: lean controller

```java
// CustomerController.java — Controller delegates business logic to service
package com.example.customer.api;

import com.example.customer.application.CustomerApplicationService;
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
    private final CustomerApplicationService customerApplicationService;

    public CustomerController(CustomerApplicationService customerApplicationService) {
        this.customerApplicationService = customerApplicationService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public CustomerResponse create(@Valid @RequestBody CreateCustomerRequest request) {
        return customerApplicationService.create(request.email(), request.fullName());
    }
}
```

Validation đã cover. Nhưng custom validator cần ConstraintValidator — hãy extend.

### Advanced: global exception handler

```java
// ApiExceptionHandler.java — Global handler for validation and domain errors
package com.example.customer.api;

import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class ApiExceptionHandler {
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleValidation(MethodArgumentNotValidException exception) {
        List<String> fieldErrors = exception.getBindingResult()
                .getFieldErrors()
                .stream()
                .map(error -> error.getField() + ": " + error.getDefaultMessage())
                .toList();

        return new ErrorResponse("validation_error", "Invalid request payload", fieldErrors);
    }

    public record ErrorResponse(String code, String message, List<String> details) {
    }
}
```

Bạn đã đi qua controller, validation, và custom validators. Bây giờ đến phần nguy hiểm: nested validation miss và unhandled exceptions — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Spring Boot Web — REST Controller & Validation` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Validate thủ công bằng `if` trong controller | Dùng Bean Validation |
| 2 | Trả stack trace thô ra client | Chuẩn hóa error response |
| 3 | Controller gọi repository trực tiếp | Qua application service |
| 4 | DTO/request/response đặt lẫn với domain entity | Tách package `api` rõ ràng |

Bạn đã đi qua REST Validation và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Validation in Spring | https://docs.spring.io/spring-framework/reference/core/validation/beanvalidation.html |
| Building REST services | https://spring.io/guides/gs/rest-service/ |
| Exception Handling | https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-exceptionhandler.html |

## 6. RECOMMEND

Khi các bẫy chính của `Spring Boot Web — REST Controller & Validation` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| `@ControllerAdvice` chuẩn hóa nhiều lỗi hơn | API public hoặc nhiều team cùng dùng | Contract ổn định |
| Problem Details | Cần error format chuẩn RFC | Dễ integrate client |
| OpenAPI | Cần tài liệu API | Hỗ trợ FE/QA |

## 7. QUIZ

### Quick Check

1. Vì sao controller không nên chứa business logic phức tạp?
2. `@Valid` giúp giải quyết phần nào của request lifecycle?
3. `@ControllerAdvice` có lợi gì cho API lớn?

### Answer Key

1. Vì controller chỉ nên là boundary adapter, giữ code mỏng và dễ test.
2. Nó validate input ở boundary trước khi vào use case.
3. Nó chuẩn hóa error response và giảm duplicated handling.

## 8. NEXT STEPS

- Mở rộng sang security hoặc persistence khi service đã có web contract rõ ràng
- Bổ sung test với `@WebMvcTest` ở nhịp tiếp theo
