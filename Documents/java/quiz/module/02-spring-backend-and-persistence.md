<!-- tags: java, quiz, spring, backend -->
# Java Module Quiz — Spring, Backend & Persistence

> Quiz cho Spring, Spring Boot, Spring Data, Spring Security và backend Java: controller boundary, transaction, repository, validation, auth.

📅 Ngày tạo: 2026-04-04 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 8 phút đọc

## 1. DEFINE

Hình dung bạn vừa đi qua Spring, backend và persistence docs, rồi tự tin rằng controller, transaction và JPA boundary đã đủ rõ. Chỉ cần một câu hỏi đặt các mảnh đó cạnh nhau, nhiều vùng mơ hồ sẽ hiện ra ngay. Bài quiz này sinh ra để kéo những vùng mơ hồ đó lên mặt bàn.

Quiz này được dựng để bắt đúng các chỗ đó. Nó không hỏi bạn thuộc annotation nào, mà hỏi bạn boundary nào đang bị phá và rủi ro nào sẽ nổ ở production nếu tiếp tục như vậy.

| Variant | Mô tả |
| --- | --- |
| Web boundary quiz | DTO, validation, exception contract |
| Persistence quiz | repository, projection, transaction boundary |
| Security quiz | authentication, authorization, JWT/OAuth2 mental model |

Core insight:

> Ở hệ Spring, bug lớn thường được sinh ra từ boundary mờ chứ không phải từ thiếu annotation.

## 2. VISUAL

Sau khi hiểu mục tiêu của quiz, ta cần nhìn rõ ba lớp boundary mà nó đang bảo vệ. Nếu không thấy ba lớp này, đáp án rất dễ bị chọn theo thói quen framework.

### Level 1

```text
request contract --> use-case boundary --> persistence/security boundary
```

*Hình: Mỗi câu hỏi backend tốt đều xoay quanh một boundary bị kéo lệch.*

### Level 2

```text
Nếu câu hỏi nói về...          Boundary cần soi lại
----------------------------  --------------------------------------
request body / error payload  API contract
repository / save order       transaction + aggregate boundary
JWT / login / role mapping    authn/authz boundary
```

*Hình: Quiz backend tốt bắt người đọc xác định đúng boundary trước rồi mới nói tới framework API.*

## 3. CODE

Flow của Java Module Quiz — Spring, Backend & Persistence đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: boundary leak detection

```java
@RestController
class OrderController {
    private final OrderRepository orderRepository;

    @PostMapping("/orders")
    Order create(@RequestBody Order order) {
        return orderRepository.save(order);
    }
}
```

**Tại sao?** Câu hỏi kiểu này không kiểm tra việc bạn có biết `@RestController` hay không. Nó kiểm tra xem bạn có thấy API contract, transaction boundary và entity exposure đang bị trộn thành một hay không.

**Kết luận**: Nếu bạn chỉ sửa annotation mà không sửa boundary, đáp án vẫn sai tinh thần hệ thống.

## 4. PITFALLS

Biết cách dùng `Java Module Quiz — Spring, Backend & Persistence` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Severity | Lỗi | Hậu quả | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🟠 Major | Chọn theo “Spring thường làm vậy” | Hợp framework nhưng sai boundary | Hỏi lại lớp nào đang chịu trách nhiệm |
| 2 | 🟡 Common | Xem transaction là chi tiết implementation | Dễ đặt sai rollback boundary | Gắn transaction với use case cụ thể |
| 3 | 🟠 Major | Nhầm authn và authz | Security rule lệch nhưng khó thấy ngay | Tách riêng người dùng là ai và được làm gì |

## 5. REF

| Resource | Loại | Link | Ghi chú |
| --- | --- | --- | --- |
| Spring Framework Reference | Official docs | https://docs.spring.io/spring-framework/reference/ | Verify MVC/DI boundaries |
| Spring Data JPA Reference | Official docs | https://docs.spring.io/spring-data/jpa/reference/ | Verify repository/projection behavior |
| Spring Security Reference | Official docs | https://docs.spring.io/spring-security/reference/ | Verify filter chain và auth model |

## 6. RECOMMEND

Khi các bẫy chính của `Java Module Quiz — Spring, Backend & Persistence` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do | File |
| --- | --- | --- | --- |
| [01-rest-controller-validation.md](../../frameworks/spring-boot/web/01-rest-controller-validation.md) | Sai API contract | Khóa boundary web | Nội bộ |
| [01-entities-repositories-transactions.md](../../frameworks/spring-data/jpa/01-entities-repositories-transactions.md) | Sai persistence boundary | Làm rõ aggregate và transaction | Nội bộ |
| [01-authentication-authorization-filter-chain.md](../../frameworks/spring-security/basics/01-authentication-authorization-filter-chain.md) | Sai security mental model | Tách authn/authz rõ hơn | Nội bộ |
