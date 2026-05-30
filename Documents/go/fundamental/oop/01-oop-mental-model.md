<!-- tags: golang, oop, mental-model --> # 🧠 Mô hình tinh thần OOP — Chuyển đổi từ Java/TypeScript

> Go có OOP không? Có - nhưng là một biến thể tối giản. Không có lớp, phần mở rộng hoặc công cụ sửa đổi trừu tượng. Structs + interfaces + composition thay thế tất cả chúng. Hướng dẫn này điều chỉnh lại mô hình tinh thần của bạn.

📅 Đã tạo: 2026-04-10 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 18 phút đọc

| Khía cạnh | Chi tiết |
| ----------------- | -------------------------------------------- |
| **Khái niệm** | Các khái niệm OOP được ánh xạ tới tương đương Go |
| **Trường hợp sử dụng** | Các nhà phát triển đang chuyển từ Java/TS/C++ sang Go |
| **Thông tin chi tiết quan trọng** | Go là OOP — không phải là OOP bạn đã học |
| ** Go triết lý** | Đơn giản, có khả năng kết hợp, rõ ràng > ngầm định|

---

## 1. ĐỊNH NGHĨA

Ngày đầu tiên viết Go . Bạn khởi chạy IDE, tạo `user.go` và gõ ngay `class User` — lỗi. Bạn thử `abstract class BaseEntity` — lỗi. `User extends BaseEntity implements Serializable` - cú pháp về cơ bản không tồn tại.

Bạn tìm kiếm: " Go có hỗ trợ OOP không?" Stack Overflow nói: " Go không phải là ngôn ngữ hướng đối tượng." Bạn đọc thêm: " Go hỗ trợ encapsulation , polymorphism , và composition ." Những câu lệnh này mâu thuẫn với nhau - đó là sự nhầm lẫn cốt lõi khi đến từ Java hoặc TypeScript.

Sự thật: ** Go có OOP, nhưng là một biến thể rút gọn.** Không có từ khóa `class` , không có phân cấp inheritance , không có ràng buộc `abstract` , không có phạm vi `protected` . Thay vào đó, Go sử dụng:

| OOP truyền thống | Go Tương đương | Sự khác biệt cốt lõi |
| --- | --- | --- |
| `class` | `struct` | Dữ liệu + phương pháp; không phân cấp |
| `extends` | Embedding | Composition (has-a), không phải inheritance (is-a) |
| `implements` | Sự hài lòng tiềm ẩn | Không có tuyên bố rõ ràng; phương pháp phù hợp đủ |
| `abstract` | Interface | Tối giản, do người tiêu dùng xác định |
| `private/public` | chữ thường/chữ hoa | Package -phạm vi cấp độ |
| `new()` | Hàm Factory | Xác thực rõ ràng |
| `this` | Receiver `(u *User)` | Rõ ràng, không có trạng thái ngầm định |

### Tại sao Go lại thiết kế cấu trúc chính xác này? Go có nguồn gốc từ Google — điều hướng các cơ sở mã với hàng tỷ dòng và hàng nghìn kỹ sư cam kết hàng ngày. Pike, Thompson và Griesemer đã cố tình loại bỏ:

- ** Inheritance **: Bởi vì hệ thống phân cấp cấp 5+ trên thực tế đảm bảo các lớp cơ sở dễ vỡ, vấn đề kim cương và khớp nối chặt chẽ.
- **Từ khóa lớp**: Bởi vì struct + phương thức cung cấp đủ khả năng — lớp thêm lễ không cần thiết.
- **Ngụ ý `this` **: Bởi vì receivers rõ ràng giúp việc theo dõi mã dễ dàng hơn nhiều trên quy mô lớn.

Kết quả: OOP của Go giữ lại những gì quan trọng - encapsulation , polymorphism , composition - trong khi loại bỏ inheritance mong manh, các lớp trạng thái trừu tượng và hệ thống phân cấp phức tạp.

### Chế độ lỗi

| Lỗi Tâm Thần | Triệu chứng | Hậu quả |
| --- | --- | --- |
| " Go thiếu OOP" | Viết spaghetti thủ tục phẳng | Logic miền chảy máu khắp nơi, không encapsulation |
| " Go OOP = Java OOP" | Dịch các mẫu doanh nghiệp Java 1:1 | Dài dòng, không thành ngữ, khó ôn lại |
| "Mọi struct cần một interface " | Chất béo interfaces được xác định tại ranh giới nhà sản xuất | Khớp nối, mock chết tiệt, vi phạm ISP |

Thiếu mô hình theo một trong hai hướng đều phải trả giá thực sự. Dưới đây cho thấy mô hình tinh thần thực sự hoạt động như thế nào - lập bản đồ dòng suy nghĩ, không chỉ cú pháp.

---

## 2. HÌNH ẢNH

Mâu thuẫn không nằm ở cú pháp - mà là ở dòng suy nghĩ. Khi bạn nghĩ "Tôi cần polymorphism ", Java sẽ thúc đẩy bạn hướng tới `extends` → `override` . Go hướng bạn tới `interface` → sự hài lòng tiềm ẩn. Cùng một đích đến, những con đường ngược nhau.

### Java OOP Stack so với Go OOP Stack```mermaid
flowchart LR
    subgraph Java["Java / TypeScript OOP"]
        direction TB
        A1[class] --> A2[extends / implements]
        A2 --> A3[abstract class]
        A3 --> A4[interface]
        A4 --> A5[polymorphism via vtable]
    end

    subgraph Go["Go OOP"]
        direction TB
        B1[struct] --> B2[embedding]
        B2 --> B3[no abstract — just interface]
        B3 --> B4[implicit interface satisfaction]
        B4 --> B5[polymorphism via interface dispatch]
    end

    Java -.->|"reframe"| Go
```![OOP mental model compare card](./images/01-oop-mental-model-compare.png) *Hình: Cùng 5 cấp mục tiêu — nhưng Go loại bỏ cấp 2 bên trong (phân cấp lớp + lớp trừu tượng). Kết quả: phẳng, khớp nối thấp.*

### Quyết định Map : Khi nào triển khai nghiêm ngặt cái gì?```mermaid
flowchart TD
    A[Require grouping data + behavior?] --> B{Complex behavior?}
    B -->|No — pure rigid data| C[simple struct]
    B -->|Yes — active methods necessary| D[struct + methods]
    D --> E{Require reusing active behavior?}
    E -->|No| F[Terminal — struct + methods purely suffice]
    E -->|Yes| G{Is-a or practically Has-a?}
    G -->|Has-a| H[Embedding / Fast Composition]
    G -->|Is-a... genuinely?| I[Interface — silent implicit satisfaction]
    I --> J{Total explicit methods?}
    J -->|1-3| K[✅ Small modular interface — Go standard]
    J -->|4+| L[⚠️ Heavily split — Enforce ISP]
```*Hình: Luồng quyết định của nhà phát triển Go — hầu hết các đường dẫn đều kết thúc ở struct + phương thức đơn giản hoặc [[E4]]] nhỏ. Embedding chỉ xuất hiện khi cần nâng cấp phương thức.*

Mô hình tinh thần là rõ ràng. Đoạn mã bên dưới maps biến nó thành các tạo phẩm đang hoạt động — bắt đầu từ bản dịch "lớp sang struct " đơn giản nhất.

---

## 3. MÃ

### Ví dụ 1: Cơ bản — Lớp → Struct + Phương thức

Bạn xử lý một lớp Java tiêu chuẩn: `User` bao gồm các trường riêng tư, hàm tạo, getters và phương thức nghiệp vụ. Điều này di chuyển mạnh đến mức nào vào Go ?

> **Mục tiêu**: Map một lớp Java thành một Go struct + các phương thức + factory .
> **Phương pháp tiếp cận**: Struct giữ dữ liệu, các phương thức liên kết với dữ liệu đó, `NewXxx()` xử lý việc xác thực cấu trúc.
> **Ví dụ**: `User` Lớp Java → `User` Go struct .```go
// mental_model.go — Java class → Go struct

// Java:
// public class User {
//     private String email;
//     private String name;
//     public User(String email, String name) { this.email = email; this.name = name; }
//     public String getEmail() { return email; }
//     public String greet() { return "Hello, " + name; }
// }

// Go equivalent:
type User struct {
	email string // lowercase = unexported (strictly private to the declared package)
	name  string
}

// NewUser acts as the constructor proxy. Go inherently lacks an explicit constructor keyword.
// Execute validation here — the factory function strictly guarantees the resulting object is logically valid.
func NewUser(email, name string) (*User, error) {
	if email == "" {
		return nil, fmt.Errorf("email strictly required")
	}
	return &User{email: email, name: name}, nil
}

// Method bound to User — utilizing an explicit receiver bypassing the implicit Java `this` pointer
// (u *User) defines a pointer receiver — safely mutating the core origin struct while massively avoiding memory copy overhead
func (u *User) Email() string { return u.email }

func (u *User) Greet() string {
	return "Hello, " + u.name
}
```> **Takeaway**: Không `class` , không `this` , không có bản tóm tắt get/set. Structs + phương thức + chức năng factory = hoàn thành. receiver `(u *User)` rõ ràng làm rõ những gì Java ẩn đằng sau ẩn `this` . Struct + các phương thức xử lý một thực thể duy nhất. Khi bạn cần polymorphism — làm cho các loại khác nhau có chung một hợp đồng hành vi — Java sử dụng `implements` . Go xử lý nó như thế nào?

---

### Ví dụ 2: Trung cấp — Interface dụng cụ → Sự hài lòng ngầm

Java: `class EmailNotifier implements Notifier {}` . Go : loại bỏ hoàn toàn từ khóa `implements` - nếu struct có các phương thức khớp, nó đáp ứng hợp đồng.

> **Mục tiêu**: Dịch sự hài lòng của Java `implements` sang Go của implicit interface .
> **Phương pháp tiếp cận**: Xác định interface ở ranh giới người tiêu dùng. Any struct đáp ứng nó bằng cách cung cấp các phương thức khớp.
> **Ví dụ**: `Notifier` interface — `EmailNotifier` và `SlackNotifier` ngầm thỏa mãn điều đó.```go
// implicit_interface.go — Java implements → Go implicit satisfaction

// Java:
// interface Notifier { void send(String to, String msg); }
// class EmailNotifier implements Notifier {
//     public void send(String to, String msg) { /* SMTP implementation */ }
// }

// Go: Interface rigorously defined WHERE IT IS ACTIVELY CONSUMED — entirely ignoring the upstream producer origin
type Notifier interface {
	Send(to, msg string) error
}

// EmailNotifier — EXPLICITLY NO "implements Notifier" hard declaration
// If this root struct functionally ships the `Send(to, msg string) error` method → it automatically structurally satisfies the `Notifier` constraint
type EmailNotifier struct {
	SMTPHost string
}

func (e *EmailNotifier) Send(to, msg string) error {
	// execute internal SMTP dispatch
	fmt.Printf("[Email] to=%s msg=%s via %s\n", to, msg, e.SMTPHost)
	return nil
}

type SlackNotifier struct {
	WebhookURL string
}

func (s *SlackNotifier) Send(to, msg string) error {
	// execute internal Slack webhook payload transit
	fmt.Printf("[Slack] channel=%s msg=%s\n", to, msg)
	return nil
}

// ✅ Consumer processes strictly generic interfaces — completely oblivious tracking concrete nested types
type OrderService struct {
	notifier Notifier // structurally injected dependency — dynamically accepting Email, Slack, or any compatible future architectural entity
}

func (os *OrderService) Complete(orderID string) error {
	// ... sequentially finalize root order transition parameters ...
	return os.notifier.Send("ops-channel", "Order "+orderID+" completed successfully")
}
```> **Tại sao lại ngầm hiểu sự hài lòng thay vì rõ ràng `implements` ?**
> Rõ ràng `implements` tạo ra sự liên kết chặt chẽ: nhà sản xuất PHẢI biết interface tồn tại. Go đảo ngược điều này: người tiêu dùng xác định mức interface tối thiểu mà nó cần. Nhà sản xuất thực hiện các phương thức mà không biết interface nào sẽ sử dụng chúng. Kết quả: không có nhập khẩu từ nhà sản xuất đến người tiêu dùng. Tách rời sạch sẽ.
>
> **Bẫy**: Không tạo " interface cho mọi struct " — nếu chỉ tồn tại 1 triển khai cụ thể và bạn không cần kiểm tra mock , hãy bỏ qua interface . Interfaces xuất hiện khi tồn tại ≥2 lần triển khai HOẶC khi thử nghiệm yêu cầu ranh giới mock .

> **Takeaway**: Go sử dụng kiểu gõ cấu trúc (gõ vịt) thay vì kiểu gõ danh nghĩa. Nếu struct có các phương thức khớp, nó đáp ứng interface - không cần khai báo. Do người tiêu dùng xác định, không phải do nhà sản xuất xác định.

Ẩn interfaces bìa polymorphism . Nhưng khi bạn cần sử dụng lại mã kiểu chéo - Java sử dụng `extends` . Go xử lý việc đó như thế nào?

---

### Ví dụ 3: Nâng cao — Inheritance Phân cấp → Flat Composition Trong Java, `AdminUser extends User extends BaseEntity` thúc đẩy việc tái sử dụng mã. Go thiếu `extends` . Nó thay thế bằng embedding + interface composition phẳng - tạo ra các cấu trúc phẳng, không dễ vỡ.

> **Mục tiêu**: Map hệ thống phân cấp Java 3 cấp tới Go phẳng composition .
> **Phương pháp tiếp cận**: Embedding để tái sử dụng trường/phương thức, interfaces để tái sử dụng hợp đồng.
> **Ví dụ**: BaseEntity + User + AdminUser — 3 cấp độ Java → 2 cấp độ Go (được nhúng).```go
// flat_composition.go — Java 3-level hierarchy → Go flat embedding

// Java:
// abstract class BaseEntity { Long id; LocalDateTime createdAt; }
// class User extends BaseEntity { String email; }
// class AdminUser extends User { String role; boolean canDelete(); }

// Go: NO explicit hierarchy. Embedding strictly = composition, entirely excluding inheritance.

// ✅ Reusable "base" fields — fundamentally NOT a parent class
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

// ✅ User simply embeds Timestamps — explicitly "has timestamps", strictly not "is a timestamp"
type User struct {
	Timestamps        // embedded element — implicitly promotes nested fields/methods
	ID         int64
	Email      string
}

// ✅ Admin cleanly embeds User — explicitly "has user data", strictly not "is a user"
type Admin struct {
	User              // embedded element — silently promotes User fields/methods upward
	Role   string
	Perms  []string
}

func (a *Admin) CanDelete() bool {
	for _, p := range a.Perms {
		if p == "delete" {
			return true
		}
	}
	return false
}

// ⚠️ CRITICAL DIFFERENCE from Java:
// var u User = admin  ← FATAL COMPILE ERROR in Go!
// Admin variables strictly ARE NOT statically assignable targeting User allocations.
// An Admin physically HAS a User. Construct a dynamic interface dictating polymorphism:

type Authenticatable interface {
	GetEmail() string
}

func (u *User) GetEmail() string { return u.Email }

// ✅ Both structured User and Admin completely satisfy Authenticatable — executing via the natively promoted method
// func authenticate(a Authenticatable) { ... }
```> **Tại sao phẳng lại đánh bại hệ thống phân cấp 3 cấp độ sâu?**
> Trong Java: việc thay đổi kiểu `BaseEntity.createdAt` gợn sóng thông qua `User` , `AdminUser` và mọi lớp con. Đó là vấn đề Lớp cơ sở mong manh. Với Go embedding : thay đổi `Timestamps.CreatedAt` chỉ ảnh hưởng đến các loại nhúng `Timestamps` . Không có vtables, không có xung đột thứ tự giải quyết phương pháp. Và quan trọng là: `Admin` KHÔNG phải là `User` - bạn cần một interface rõ ràng cho polymorphism . Điều này nghe có vẻ hạn chế nhưng tỏ ra an toàn hơn: nó buộc phải suy nghĩ có chủ ý về polymorphism thay vì mặc định là inheritance .

> **Takeaway**: Go composition bằng Java inheritance trừ đi tính dễ vỡ. Embedding thúc đẩy việc tái sử dụng mã. Interfaces ổ đĩa polymorphism . Hai mối quan tâm riêng biệt - hoàn toàn tách biệt khỏi bẫy `extends` .

Những ví dụ này map cho 3 trụ cột OOP. Tiếp theo: các bẫy phổ biến trong đó tư duy Java kích hoạt lỗi Go .

---

## 4. Cạm bẫy

| # | Mức độ nghiêm trọng | Lỗi | Hậu quả | Sửa chữa |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Gây tử vong | Dịch 1:1 Java design patterns | Một `AbstractFactoryBuilder` dài 200 dòng mà không ai có thể xem lại | Rút gọn: struct + factory + nhỏ interface |
| 2 | 🔴 Gây tử vong | Giả sử embedding = inheritance ( `admin = user` ) | Biên dịch lỗi; hoặc tệ hơn là lỗi logic runtime im lặng | Embedding là có-a. Sử dụng interfaces cho polymorphism |
| 3 | 🟡 Chung | Tạo fat interfaces trước khi cần 2 lần triển khai | Interface ranh giới có giá trị bằng 0 | YAGNI: tạo interfaces khi tồn tại ≥2 biến thể |
| 4 | 🟡 Chung | Thêm getter/setter cho mọi trường | Bộ nhớ cơ Java dư thừa | Go tiêu chuẩn: xuất trực tiếp các trường khi thích hợp |
| 5 | 🔵 Nhỏ | Sử dụng `this.field` bằng bộ nhớ cơ | Không thành ngữ | Sử dụng ngắn receivers (ví dụ: `u *User` ) |

### 🔴 Cạm bẫy #1 — Java-to- Go dịch = quái vật nghi lễ

Nhà phát triển Java viết Go tự nhiên tạo ra:```go
// ❌ Java-translated Go — structurally excessively complex
type UserFactory interface {
    CreateUser(email string) (*User, error)
}
type UserFactoryImpl struct{}
func (f *UserFactoryImpl) CreateUser(email string) (*User, error) { /* ... */ }
```Sự cần thiết quan trọng hoàn toàn:```go
// ✅ Idiomatic Go — clean robust simple factory function
func NewUser(email string) (*User, error) { /* ... */ }
```Các ranh giới interface `UserFactory` về mặt logic chỉ tồn tại một cách chính xác khi vận hành nhiều ranh giới triển khai một cách rõ ràng hoặc an toàn mocking .

---

## 5. GIỚI THIỆU

| Tài nguyên | Loại | Liên kết | Ghi chú |
| --- | --- | --- | --- |
| Go Câu hỏi thường gặp — Go OOP? | Chính thức | https://go.dev/doc/faq#Is_Go_an_object-orient_lingu | Câu trả lời dứt khoát của Rob Pike |
| Có hiệu lực Go | Chính thức | https://go.dev/doc/effect_go | Thành ngữ cấu trúc kinh điển |
| Go Blog — Composition | Chính thức | https://go.dev/blog/ embedding | Embedding được giải thích thuần túy về mặt khái niệm |

---

## 6. KHUYẾN NGHỊ

Cốt lõi của **Mô hình tinh thần OOP - Điều chỉnh lại cho Go ** rất rõ ràng. Các nhánh bên dưới điều hướng theo chiều sâu từng trụ cột OOP.

| Gia hạn | Khi nào | Cơ sở lý luận | Tệp/Liên kết |
| --- | --- | --- | --- |
| [Encapsulation & Visibility](./02-encapsulation-visibility.md) | Khi điều hướng mức độ hiển thị package -level nguyên bản | Chữ hoa/chữ thường có vẻ đơn giản - độ phức tạp thực sự nằm bên trong packages chính xác | Tiếp theo theo thứ tự |
| [Composition over Inheritance](./03-composition-over-inheritance.md) | Khi mẫu cấu trúc embedding cho DDD | Embedding + ủy quyền = Go thay thế cho kéo dài | Logic OOP cốt lõi |
| [Interfaces & Polymorphism](./04-interfaces-polymorphism.md) | Khi yêu cầu thiết kế polymorphism sạch sẽ | Giới hạn mô-đun ngầm định, do người tiêu dùng xác định — tìm hiểu sâu | Logic OOP cốt lõi |
| [Structs & Composition](../structs/01-composition-embedding.md) | Khi thực thi chi tiết cấu trúc cụ thể struct một cách hiệu quả | Thẻ Struct , ngữ nghĩa bản sao gốc, đường dẫn mẫu hàm tạo rõ ràng | Liên kết chéo |

---

**Điều hướng**: [← OOP in Go](./README.md) · [→ Encapsulation](./02-encapsulation-visibility.md)