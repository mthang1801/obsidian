<!-- tags: golang, datetime, formats --> # 🕐 Date & Time — TS Date /Moment/Dayjs → Go `time` > JavaScript sử dụng mã thông báo ghi nhớ format như `YYYY-MM-DD` . Go sử dụng tham chiếu ma thuật date : `2006-01-02 15:04:05` . Sử dụng mã thông báo kiểu JavaScript trong Go sẽ biên dịch không có lỗi nhưng tạo ra đầu ra rác.

📅 Đã tạo: 23-03-2026 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 16 phút đọc

## 1. ĐỊNH NGHĨA

Giao diện người dùng của bạn gửi dấu thời gian ISO 8601. Kỹ sư phụ trợ phân tích chúng bằng `time.Parse("YYYY-MM-DD", input)` — sao chép mô hình tinh thần JavaScript. Go chấp nhận chuỗi không có lỗi biên dịch. Nhưng [[E40]]] được phân tích cú pháp là vô nghĩa: năm, tháng và ngày được thay thế bằng các ký tự không liên quan vì `Y` , `M` , `D` không có ý nghĩa trong hệ thống Go 's format . Go sử dụng **tham chiếu ma thuật date **: `Mon Jan 2 15:04:05 MST 2006` . Các số tuân theo trình tự `1-2-3-4-5-6-7` : Tháng=1, Ngày=2, Giờ=15 (3 giờ chiều), Phút=04, Giây=05, Năm=2006, Độ lệch múi giờ=-0700. Ví dụ, bạn viết format — `"2006-01-02"` có nghĩa là "năm-tháng-ngày" vì đó là các giá trị tham chiếu ở các vị trí đó.

### 1.1 Các kiểu bất biến và lỗi

| Ranh giới | Trách nhiệm cốt lõi |
| --- | --- |
| **Tham khảo ma thuật date ** | Bố cục Format sử dụng các giá trị tham chiếu: Tháng=1, Ngày=2, Giờ=3/15, Phút=4, Giây=5, Năm=6, Múi giờ=7. |
| **Các loại thời lượng** | `time.Duration` lưu trữ nano giây. Sử dụng hằng số `time.Hour` , `time.Minute` cho số học. |

| Quy tắc | Cơ sở lý luận |
| --- | --- |
| **Từ chối mã thông báo `YYYY-MM-DD` ** | Họ biên dịch nhưng tạo ra kết quả sai. Chỉ sử dụng `2006-01-02` . |
| **Chỉ định rõ ràng múi giờ** | `time.Parse` giả sử UTC. Sử dụng `time.ParseInLocation` khi đầu vào ở múi giờ địa phương. |

### 1.2 Chuỗi thất bại

- **Múi giờ bị thiếu:** Bạn lưu trữ dấu thời gian bằng `t.Format(time.RFC3339)` nhưng phân tích lại chúng mà không có vị trí. Giao diện người dùng hiển thị thời gian đặt chỗ giảm 7 giờ vì UTC được giả định thay vì `Asia/Ho_Chi_Minh` .
- **Bẫy sử dụng tháng:** `time.Now().Month()` trả về `time.Month` (một loại được đặt tên), không phải `int` . So sánh nó với một số nguyên từ API không thành công khi biên dịch time . Truyền với `int(month)` .

## 2. HÌNH ẢNH

Tham chiếu format là phần khó hiểu nhất của Go 's `time` package . Mã thông báo JavaScript maps trực quan cho các giá trị tham chiếu Go . ![Date Format Reference](./images/05-date-time-compare.png) *Hình: Mã thông báo JavaScript format (YYYY, MM, DD, HH, mm, ss) được ánh xạ tới các giá trị tham chiếu Go (2006, 01, 02, 15, 04, 05). Một chữ số bị đặt sai vị trí sẽ tạo ra một lỗi âm thầm date .*

## 3. MÃ

Với tham chiếu date được ghi nhớ, đoạn mã bên dưới thể hiện khả năng phân tích cú pháp, xử lý múi giờ và kiểm tra vòng định kỳ.

### Ví dụ 1: Cơ bản — Tham chiếu ma thuật format > **Mục tiêu**: Phân tích dấu thời gian giao diện người dùng và format chúng cho phản hồi API.
> **Phương pháp tiếp cận**: Sử dụng tham chiếu của Go date `2006-01-02 15:04:05` cho bố cục. Sử dụng `time.RFC3339` cho đầu ra ISO 8601.
> **Độ phức tạp**: O(1) cho mỗi lệnh gọi phân tích cú pháp/ format .```go
// basic_parsing.go
package dates

import (
	"fmt"
	"time"
)

func ParseFrontendTimestamp(payload string) (time.Time, error) {
	// TS: dayjs(payload).format('YYYY-MM-DD HH:mm:ss')
	// ✅ Go uses the 1-2-3-4-5-6 reference sequence
	layout := "2006-01-02 15:04:05"
	
	parsed, err := time.Parse(layout, payload)
	if err != nil {
		return time.Time{}, err
	}
	
	return parsed, nil
}

func FormatStandardOutput(now time.Time) string {
	// RFC3339 = "2006-01-02T15:04:05Z07:00" (ISO 8601)
	return now.Format(time.RFC3339) 
}
```> **Bài học**: Ghi nhớ chuỗi `1-2-3-4-5-6-7` (tháng-ngày-giờ-phút-giây-năm-múi giờ). Mọi bố cục Go format là sự sắp xếp lại các giá trị tham chiếu này.

---

### Ví dụ 2: Trung cấp - Thay đổi thời lượng và múi giờ

> **Mục tiêu**: Lên lịch tác vụ trong tương lai theo múi giờ cụ thể, tương đương với `moment().add(hours, 'hour').tz("Asia/Tokyo")` .
> **Phương pháp tiếp cận**: Sử dụng `time.Duration` để bù giờ và `time.LoadLocation` để chuyển đổi múi giờ.
> **Độ phức tạp**: O(1) cho mỗi thao tác.```go
// bounded_durations.go
package dates

import (
	"time"
)

func ScheduleFutureTask(hours int, targetLocation string) (time.Time, error) {
	// TS: moment().add(hours, 'hour').tz("Asia/Tokyo")
	now := time.Now()
	
	offset := time.Duration(hours) * time.Hour
	future := now.Add(offset)

	// ✅ LoadLocation handles DST transitions automatically
	loc, err := time.LoadLocation(targetLocation)
	if err != nil {
		return time.Time{}, err
	}
	
	return future.In(loc), nil
}

func CalculateCalendarOffset() time.Time {
	now := time.Now()
	// ✅ AddDate handles calendar months (28/29/30/31 days)
	// Adding 30*24*time.Hour skips this and breaks on February
	return now.AddDate(0, 1, 0) 
}
```> **Takeaway**: Sử dụng `AddDate(0, 1, 0)` cho "một tháng sau" — nó xử lý chính xác các độ dài tháng khác nhau. `30 * 24 * time.Hour` cung cấp cho bạn chính xác 720 giờ, sai đối với tháng 2 và các tháng có 31 ngày.

---

### Ví dụ 3: Nâng cao — Mã và bỏ phiếu định kỳ

> **Mục tiêu**: Thay thế `setInterval(fn, 1000)` của JavaScript bằng Go 's `time.Ticker` .
> **Phương pháp tiếp cận**: `time.NewTicker` gửi channel đều đặn. `select` chặn trên mã đánh dấu và hủy ngữ cảnh.
> **Độ phức tạp**: O(1) mỗi tích tắc.```go
// interval_polling.go
package dates

import (
	"context"
	"fmt"
	"time"
)

func ExecutePollingInterval(ctx context.Context, duration time.Duration) {
	// TS: setInterval(fn, 1000)
	ticker := time.NewTicker(duration)
	
	// ✅ Stop the ticker to release the underlying goroutine
	defer ticker.Stop() 

	for {
		select {
		case <-ticker.C:
			fmt.Println("Polling active configurations")
		case <-ctx.Done():
			fmt.Println("Terminating interval loop")
			return
		}
	}
}
```> **Takeaway**: Luôn gọi `ticker.Stop()` qua `defer` . `time.Tick()` (không có `New` ) trả về channel mà không có cách nào để ngăn chặn goroutine cơ bản - nó rò rỉ trong suốt thời gian tồn tại của quá trình.

## 4. Cạm bẫy

| # | Khiếm khuyết | Sửa chữa |
| --- | --- | --- |
| 1 | Sử dụng mã thông báo `YYYY-MM-DD` format trong Go | Thay thế bằng `2006-01-02` . Tham chiếu của Go date là hợp lệ duy nhất format . |
| 2 | Giả sử `time.Parse` sử dụng múi giờ địa phương | `time.Parse` mặc định là UTC. Sử dụng `time.ParseInLocation` cho giờ địa phương. |
| 3 | Sử dụng `time.Sleep` để mô phỏng `setTimeout` | Sử dụng `time.AfterFunc(d, fn)` để thực hiện trì hoãn không chặn. |

## 5. GIỚI THIỆU

| Tài nguyên | Liên kết |
| --- | --- |
| `time` package | [pkg.go.dev/time](https://pkg.go.dev/time) |
| Format hằng số | [pkg.go.dev/time#pkg-constants](https://pkg.go.dev/time#pkg-constants) |

## 6. KHUYẾN NGHỊ

| Gia hạn | Khi nào | Cơ sở lý luận |
| --- | --- | --- |
| [Promise and Async](./04-promise-async.md) | Khi kết hợp các thao tác time với I/O đồng thời | Thời gian chờ theo ngữ cảnh tích hợp trực tiếp với các mẫu mã đánh dấu |
| [Enum Types](./06-enum-union-types.md) | Khi lập mô hình các trạng thái dựa trên time - (hàng ngày, hàng tuần, hàng tháng) | `iota` hằng số cho các loại khoảng thời gian lập kế hoạch |

**Điều hướng**: [← Async Contexts](./04-promise-async.md) · [→ Enum Types](./06-enum-union-types.md)