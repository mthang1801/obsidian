<!-- tags: java, jdk -->
# ☕ Java Core Libraries — Instant, LocalDateTime, ZoneId & Duration

> Thời gian là nguồn bug rất dễ bị xem nhẹ. Bài này tập trung vào mental model đúng khi dùng `java.time`, đặc biệt là phân biệt thời điểm tuyệt đối với thời gian hiển thị theo múi giờ.

📅 Ngày tạo: 2026-03-28 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 14 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Intermediate |
| **Use case** | Expiry time, scheduling, audit log, timezone-aware display |
| **Java focus** | `Instant`, `LocalDateTime`, `ZonedDateTime`, `Duration` |
| **Prerequisites** | Java basics |

## 1. DEFINE

Hình dung một tính năng lên lịch họp chạy đúng ở máy dev nhưng lệch giờ sau khi deploy sang môi trường khác. Log ghi đầy `LocalDateTime`, DB lưu timestamp theo một kiểu khác, còn client thì gửi timezone nửa vời. Java Time API chỉ trở nên sống động khi bạn nhìn thấy một sai lệch vài tiếng đồng hồ có thể làm cả flow nghiệp vụ trượt khỏi thực tế.

Bài này đặt `Java Core Libraries — Instant, LocalDateTime, ZoneId & Duration` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Phân biệt các kiểu thời gian

| Type | Ý nghĩa | Khi dùng |
| --- | --- | --- |
| `Instant` | Thời điểm tuyệt đối trên timeline | audit log, expiry, DB timestamp |
| `LocalDateTime` | Ngày giờ không gắn múi giờ | form input nội bộ, hiển thị cục bộ |
| `ZonedDateTime` | Ngày giờ kèm timezone | scheduling theo region |
| `Duration` | Khoảng thời gian | timeout, TTL, elapsed time |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Sai múi giờ | Trộn `LocalDateTime` với absolute timestamp | Dùng `Instant` cho storage |
| DST bug | Cộng trừ giờ theo local time bừa bãi | Dùng `ZoneId` và API chuẩn |
| Parse lỗi locale/format | Hardcode string format lỏng | Chuẩn hóa formatter |

Các failure mode trên nghe rõ. Nhưng có trap: LocalDateTime không có timezone = shift khi deploy cross-zone, và Duration.between sai type = UnsupportedTemporalTypeException. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa mới chỉ khóa được tên của Java Core Libraries — Instant, LocalDateTime, ZoneId & Duration. Để khái niệm này bớt trừu tượng, ta cần nhìn nó ở dạng flow hoặc cấu trúc đủ cụ thể trước.

```text
absolute moment      -> Instant
display in timezone  -> ZonedDateTime
calendar-local input -> LocalDateTime
elapsed interval     -> Duration
```

```text
store time -> UTC/Instant
display    -> user zone
business calc -> choose type explicitly
```

## 3. CODE

Flow của Java Core Libraries — Instant, LocalDateTime, ZoneId & Duration đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: capture an absolute timestamp

```java
// AuditTimestampDemo.java — Store audit events as Instant
import java.time.Instant;

public final class AuditTimestampDemo {
    public static void main(String[] args) {
        Instant createdAt = Instant.now();
        System.out.println("createdAt = " + createdAt);
    }
}
```

Instant/LocalDateTime đã cover. Nhưng ZoneId cần timezone-aware — hãy convert.

### Intermediate: convert to user timezone

```java
// UserTimezoneView.java — Convert instant to a zoned display value
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZonedDateTime;

public final class UserTimezoneView {
    public ZonedDateTime toUserTime(Instant createdAt, String zoneId) {
        return createdAt.atZone(ZoneId.of(zoneId));
    }
}
```

ZoneId đã cover. Nhưng Duration/Period cần arithmetic — hãy tính.

### Advanced: duration for timeout / expiry

```java
// SessionExpiryPolicy.java — Express expiry with Duration instead of magic numbers
import java.time.Duration;
import java.time.Instant;

public final class SessionExpiryPolicy {
    private final Duration sessionTtl = Duration.ofMinutes(30);

    public Instant expiresAt(Instant createdAt) {
        return createdAt.plus(sessionTtl);
    }
}
```

Bạn đã đi qua time, zones, và duration. Bây giờ đến phần nguy hiểm: timezone-unaware và type mismatch — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Core Libraries — Instant, LocalDateTime, ZoneId & Duration` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Dùng `LocalDateTime` cho timestamp tuyệt đối | Lưu bằng `Instant` |
| 2 | Hardcode số giây/phút rời rạc | Dùng `Duration` |
| 3 | Quên timezone khi hiển thị | Chuyển qua `ZoneId` explicit |
| 4 | Tự parse format linh tinh | Chuẩn hóa formatter và contract |

Bạn đã đi qua Java Time API và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| java.time package | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/time/package-summary.html |
| Instant | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/time/Instant.html |
| ZonedDateTime | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/time/ZonedDateTime.html |

## 6. RECOMMEND

Khi các bẫy chính của `Java Core Libraries — Instant, LocalDateTime, ZoneId & Duration` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| DateTimeFormatter | Parse/display contract ổn định | Tránh format bug |
| Clock injection | Test time-based logic | Loại bỏ `now()` hardcode |
| Timezone review | App đa region | Tránh local-time assumptions |

## 7. QUIZ

### Quick Check

1. Khi nào `Instant` tốt hơn `LocalDateTime`?
2. Vì sao `Duration` tốt hơn magic number timeout?
3. Timezone nên xử lý ở storage hay display layer?

### Answer Key

1. Khi cần timestamp tuyệt đối và không muốn lệch theo múi giờ.
2. Vì nó rõ semantics và giảm lỗi đơn vị thời gian.
3. Thường storage dùng `Instant`, display layer mới map sang timezone người dùng.

## 8. NEXT STEPS

- Nối với `streams/` nếu xử lý dữ liệu time-based theo batch
- Hoặc quay lại `spring-boot/config` nếu cần cấu hình timezone/runtime rõ hơn
