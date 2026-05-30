<!-- tags: java, quiz, fundamentals -->
# Java Module Quiz — Core Libraries & Language Shape

> Quiz cho Java fundamentals và core libraries: syntax, records, collections, generics, time API, HTTP client, streams.

📅 Ngày tạo: 2026-04-04 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 8 phút đọc

## 1. DEFINE

Hình dung bạn vừa đọc xong fundamentals và core libraries, cảm giác mọi thứ đã khá quen thuộc. Rồi một câu hỏi rất ngắn về `equals/hashCode`, wildcard hay timezone xuất hiện và bạn nhận ra mình đang nhớ mặt khái niệm nhiều hơn là nhớ lực kéo của nó trong code thật. Đây là dạng quiz dành cho khoảnh khắc đó.

Quiz này tồn tại để kéo bạn ra khỏi cảm giác quen tay đó. Nó buộc bạn chứng minh rằng bạn không chỉ nhớ cú pháp Java, mà còn hiểu các quy tắc đang giữ chương trình đúng.

| Variant | Mô tả |
| --- | --- |
| Language semantics | records, enums, control flow, type system |
| Collections & generics | variance, bounds, collection contracts |
| Core library reasoning | time API, streams, HTTP client |

Core insight:

> Ở tầng Java core, sai nhỏ thường là sai nền. Một mental model lệch ở đây sẽ bị nhân lên ở tất cả tầng phía trên.

## 2. VISUAL

Điều quan trọng nhất của quiz này là thấy được nó đang chạm vào lớp hiểu biết nào. Sơ đồ dưới đây biến các câu hỏi thành những vùng mental model cụ thể.

### Level 1

```text
language shape --> collections contracts --> core libraries --> everyday bugs
```

*Hình: Từ ngôn ngữ đến thư viện lõi là một chuỗi liên tục; lỗi ở đầu chuỗi thường phát nổ ở cuối chuỗi.*

### Level 2

```text
Symptom                         Hỏi lại mental model nào?
-----------------------------  --------------------------------------
List/Set hoạt động lạ          equals/hashCode + collection contract
Generic API khó gọi            bounds + producer/consumer variance
Date/time lệch múi giờ         Instant vs LocalDateTime vs ZoneId
Stream code chạy nhưng khó đọc pipeline shape + side effects
```

*Hình: Quiz tốt buộc bạn map symptom về đúng lớp hiểu biết gốc.*

## 3. CODE

Quiz không cần code dài, nhưng nó cần artifact đủ cụ thể để bạn tự kiểm chứng. Snippet dưới đây cho thấy kiểu câu hỏi nên ép bạn suy nghĩ như thế nào.

### Basic: contract before convenience

```java
record User(String email) {}

Set<User> users = new HashSet<>();
users.add(new User("a@example.com"));
users.add(new User("a@example.com"));

System.out.println(users.size());
```

**Tại sao?** Một câu hỏi kiểu này không kiểm tra trí nhớ về `HashSet`, mà kiểm tra xem bạn có nối record semantics với contract của collection hay không.

**Kết luận**: Nếu bạn trả lời đúng nhưng không giải thích được vì sao, mental model vẫn chưa đủ chắc.

## 4. PITFALLS

Biết cách dùng `Java Module Quiz — Core Libraries & Language Shape` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Severity | Lỗi | Hậu quả | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🟡 Common | Chọn đáp án theo “nhớ mang máng” | Dễ nhầm API giống nhau nhưng semantics khác | Giải thích lại cơ chế trước khi chốt |
| 2 | 🟠 Major | Bỏ qua câu sai vì tưởng chi tiết nhỏ | Lỗ hổng core lặp lại ở nhiều tầng khác | Quay lại bài nguồn ngay sau quiz |
| 3 | 🟡 Common | Học mẹo stream/generics rời rạc | Code khó đọc và khó maintain | Gắn mỗi câu sai với một invariant cụ thể |

## 5. REF

| Resource | Loại | Link | Ghi chú |
| --- | --- | --- | --- |
| Java Language Specification | Official docs | https://docs.oracle.com/javase/specs/ | Verify semantics ngôn ngữ |
| Java Collections Framework | Official docs | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/package-summary.html | Verify collection contracts |
| java.time API | Official docs | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/time/package-summary.html | Verify time model |

## 6. RECOMMEND

Khi các bẫy chính của `Java Module Quiz — Core Libraries & Language Shape` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do | File |
| --- | --- | --- | --- |
| [01-list-set-map.md](../../fundamental/collections/01-list-set-map.md) | Sai ở collection contract | Củng cố hành vi container | Nội bộ |
| [01-type-parameters-bounds-wildcards.md](../../fundamental/generics/01-type-parameters-bounds-wildcards.md) | Sai ở generics | Làm rõ variance và bounds | Nội bộ |
| [01-instant-localdatetime-zoneid-duration.md](../../core-libraries/time/01-instant-localdatetime-zoneid-duration.md) | Sai ở time API | Tránh bug thời gian production | Nội bộ |
