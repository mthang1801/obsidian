<!-- tags: golang, oop, composition, embedding --> # 🧩 Composition trên Inheritance — Go Thiếu sót mở rộng theo thiết kế

> ** Struct Embedding **: Ủy quyền cho các thành phần riêng biệt thay vì phân cấp inheritance sâu.

📅 Đã tạo: 2026-04-10 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 17 phút đọc

| Khía cạnh | Chi tiết |
| ----------------- | ----------------------------------------------------- |
| **Khái niệm** | Struct embedding và các mẫu ủy quyền |
| **Trường hợp sử dụng** | Khả năng thành phần trộn tổng hợp miền |
| **Thông tin chi tiết quan trọng** | Phương thức xúc tiến xử lý việc ủy ​​quyền mà không cần inheritance |
| ** Go triết lý** | Dữ liệu phẳng đánh bại hệ thống phân cấp cha mẹ lồng nhau |

---

## 1. ĐỊNH NGHĨA

Hãy cân nhắc việc di chuyển các miền Java sang Go . Các hệ thống kế thừa xây dựng hệ thống phân cấp lớp rộng khắp với nhiều cấp độ gốc giúp âm thầm phá vỡ các mối phụ thuộc ở cấp dưới. Go đi theo một con đường khác. Không có từ khóa `extends` . Structs nhúng các tham chiếu được nhắm mục tiêu để sử dụng lại mã mà không tạo hệ thống phân cấp ghép nối. Composition thay thế hoàn toàn các lớp cha.

### Embedding so với Trường được đặt tên so với Interface | Kỹ thuật | Cú pháp | Vai trò |
| --- | --- | --- |
| ** Embedding ** | `type User struct { Timestamps }` | Phương pháp xúc tiến lập bản đồ các tuyến chức năng cụ thể |
| **Trường được đặt tên** | `type User struct { ts Timestamps }` | Truy cập phụ thuộc rõ ràng xác định các mục tiêu riêng biệt |
| ** Interface ** | `type Saver interface { Save() error }` | Đường dẫn hợp đồng thiết lập các ràng buộc thực thi cơ bản |

### Khi nào nên nhúng Structs ?

- Phương thức map kiểm tra hành vi rõ ràng kiểm tra giới hạn nhận dạng cấu trúc.
- Cấu trúc mục tiêu tránh các lỗi gốc chặn chồng chéo trường đệ quy runtime .
- Logic mục tiêu triển khai các cấu trúc hành vi lồng nhau interfaces rõ ràng.

### Chế độ lỗi

| Lỗi | Hậu quả | Sửa chữa |
| --- | --- | --- |
| Embedding tiện ích đơn giản | `user.Execute()` quảng bá các phương thức HTTP, gây nhầm lẫn cho API | Sử dụng các trường được đặt tên cho các tiện ích |
| Nhiều va chạm nhúng | Phương thức giống hệt signatures gây ra lỗi trình biên dịch | Xác định các phương thức bao bọc rõ ràng để giải quyết sự mơ hồ |
| Xử lý embedding là inheritance | Go từ chối việc gán loại giữa các loại được nhúng | Sử dụng interfaces cho polymorphism |

## 2. HÌNH ẢNH ![Composition over inheritance compare card](./images/03-composition-over-inheritance-compare.png) *Hình: Java duy trì các chuỗi dọc sâu. Go sử dụng các thành phần đồ thị phẳng với mục tiêu phụ thuộc chính xác.*

Độ phân giải phương thức phát hiện các xung đột khi biên dịch time , chặn các phương thức được quảng bá không rõ ràng.

## 3. MÃ

### Ví dụ 1: Cơ bản — Embedding Trường & Phương thức được Quảng cáo

> **Mục tiêu**: Chia sẻ các trường `Timestamps` trên structs mà không cần các lớp cơ sở.
> **Phương pháp**: Nhúng trực tiếp `Timestamps` ; các phương pháp được quảng bá tự động.
> **Độ phức tạp**: Cơ bản```go
package model

import "time"

type Timestamps struct {
	CreatedAt time.Time
	UpdatedAt time.Time
}

func (t *Timestamps) Touch() {
	now := time.Now()
	if t.CreatedAt.IsZero() {
		t.CreatedAt = now
	}
	t.UpdatedAt = now
}

type User struct {
	Timestamps // Anonymous field promoting inner structures
	ID    int64
	Email string
}

func main() {
	u := User{Email: "test@domain.com"}
	u.Touch() // Invokes Timestamps.Touch() resolving operations natively
	_ = u.CreatedAt
}
```> **Takeaway**: Anonymous embedding ​​quảng bá các trường và phương thức. Composition giữ nguyên các định nghĩa trong khi chia sẻ hành vi.

### Ví dụ 2: Trung cấp — Nhiều Embedding & Shadowing phương thức

> **Mục tiêu**: Giải quyết phương thức không rõ ràng signatures khi nhiều loại nhúng xung đột.
> **Phương pháp tiếp cận**: Xác định một phương thức trình bao bọc rõ ràng ủy quyền cho loại được nhúng chính xác.
> **Độ phức tạp**: Trung cấp```go
package model

import "fmt"

type User struct {
	Email string
}

func (u *User) String() string { return "User:" + u.Email }

type Logger struct {
	Level string
}

func (l *Logger) String() string { return "Logger:" + l.Level }

type Admin struct {
	User
	Logger
	Role string
}

// Map explicit functions bypassing distinct ambiguous method selections
func (a *Admin) String() string {
	return fmt.Sprintf("Admin(%s, log=%s)", a.User.String(), a.Logger.String())
}

func main() {
	a := Admin{
		User:   User{Email: "admin@domain.com"},
		Logger: Logger{Level: "info"},
	}
	fmt.Println(a.String())
}
```> **Takeaway**: Go ​​ngăn ngừa xung đột giữa các phương thức im lặng. Xác định các phương pháp rõ ràng để giải quyết sự mơ hồ giữa các loại được nhúng.

### Ví dụ 3: Nâng cao — Tổng hợp DDD với Composition > **Mục tiêu**: Xây dựng Tập hợp DDD với bộ sưu tập sự kiện được nhúng và các bất biến chuyển tiếp.
> **Phương pháp tiếp cận**: Nhúng `AggregateRoot` để theo dõi sự kiện; xác thực chuyển đổi trạng thái trong các phương thức miền.
> **Độ phức tạp**: Nâng cao```go
package domain

import (
	"fmt"
	"time"
)

type DomainEvent interface {
	EventName() string
}

type AggregateRoot struct {
	id      string
	events  []DomainEvent
}

func (ar *AggregateRoot) ID() string { return ar.id }

func (ar *AggregateRoot) AddEvent(e DomainEvent) {
	ar.events = append(ar.events, e)
}

type Order struct {
	AggregateRoot
	Status string
}

func NewOrder(id string) *Order {
	return &Order{
		AggregateRoot: AggregateRoot{id: id},
		Status:        "DRAFT",
	}
}

type ItemAddedEvent struct {
	OrderID string
}
func (e *ItemAddedEvent) EventName() string { return "item.added" }

func (o *Order) AddItem() error {
	if o.Status != "DRAFT" {
		return fmt.Errorf("invalid mapping processing state transitions")
	}

	o.AddEvent(&ItemAddedEvent{OrderID: o.ID()})
	return nil
}
```> **Takeaway**: Các gốc tổng hợp theo dõi các sự kiện miền thông qua composition được nhúng. Embedding tạo các đối tượng chức năng thực thi các bất biến kinh doanh một cách tự nhiên.

## 4. Cạm bẫy Composition thay thế hệ thống phân cấp inheritance . Những bẫy chính cần tránh:

| # | Mức độ nghiêm trọng | Khiếm khuyết | Sửa chữa |
| --- | --- | --- | --- |
| 1 | 🔴 Gây tử vong | Xử lý structs được nhúng làm kiểu cha mẹ, mong đợi sự phân công polymorphism ​​| Sử dụng interfaces cho polymorphism , không phải gõ bài tập |
| 2 | 🔴 Gây tử vong | Embedding tiện ích structs gây ô nhiễm bề mặt API miền | Sử dụng các trường được đặt tên để cách ly quyền truy cập tiện ích |
| 3 | 🟡 Chung | Xâu chuỗi các phần nhúng đa cấp che khuất nguồn gốc trường | Giới hạn độ sâu embedding ; thích các trường được đặt tên cho rõ ràng |

## 5. GIỚI THIỆU

| Tài nguyên | Liên kết | Lưu ý |
| --- | --- | --- |
| Có hiệu lực Go | [https://go.dev/doc/effective_go#embedding](https://go.dev/doc/effective_go#embedding) | Embedding ngữ nghĩa và quy tắc |
| Go Blog | [https://go.dev/blog/embedding](https://go.dev/blog/embedding) | mẫu Composition |

---