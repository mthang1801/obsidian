<!-- tags: golang, oop, solid, principles --> # ⚖️ SOLID trong Go — Tên giống nhau, biểu thức khác biệt

> Các nguyên tắc SOLID vẫn có hiệu lực trong Go — nhưng cách thể hiện của chúng hoàn toàn khác nhau. Không có lớp, không có phần mở rộng và không có khai báo trừu tượng. Hướng dẫn này maps từng nguyên tắc cốt lõi cho các thành ngữ Go bản địa.

📅 Đã tạo: 2026-04-10 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 16 phút đọc

| Khía cạnh | Chi tiết |
| ----------------- | ---------------------------------------------- |
| **Khái niệm** | Nguyên tắc SOLID được ánh xạ trực tiếp tới cấu trúc Go |
| **Trường hợp sử dụng** | Cấu trúc xem xét mã, quyết định kiến ​​trúc |
| **Thông tin chi tiết quan trọng** | SOLID ≠ Java SOLID . Ý tưởng giống hệt nhau, biểu thức Go |
| ** Go triết lý** | Các nguyên tắc hoạt động chính xác, việc thực hiện lại khác nhau |

---

## 1. ĐỊNH NGHĨA

Hãy xem xét đánh giá mã vào thứ Ba. Bạn nhận xét về `OrderProcessor` struct bên trong PR:

> " struct này vi phạm SRP — nó xác thực, duy trì và thông báo đồng thời."

Một nhà phát triển cấp dưới trả lời: "Nhưng Go không có lớp. SRP có áp dụng cho struct không? Và OCP — Mở/Đóng — 'mở để mở rộng' nghĩa là gì khi ngôn ngữ thiếu `extends` ?"

Đây là một câu hỏi hay. ** Các nguyên tắc SOLID vẫn hợp lệ trong Go ** — nhưng biểu thức thay đổi:

| Nguyên tắc | Biểu thức Java | Go Biểu thức |
| --- | --- | --- |
| **S** — Trách nhiệm duy nhất | Một lớp học, một lý do cụ thể để thay đổi | Một struct / package , một trách nhiệm công việc riêng biệt |
| **O** — Mở/Đóng | Định nghĩa lớp trừu tượng + ghi đè chính thức | hợp đồng Interface + triển khai cấu trúc mới |
| **L** — Thay thế Liskov | Lớp con hoạt động có thể thay thế trực tiếp cho lớp cha | Interface người triển khai vẫn có thể thay thế một cách an toàn |
| **I** — Interface Phân chia | Tách mỡ khổng lồ interfaces | interfaces tập trung nhỏ được mô hình hóa ngay từ đầu |
| **D** — Đảo ngược phụ thuộc | Lớp trừu tượng/ interface cứng nhắc DI | Nội dung dựa trên hàm tạo + cụ thể do người tiêu dùng xác định interface |

Nếu bạn cho rằng " SOLID trong Go là quá dễ dàng vì Go thực thi thuần composition " — điều đó đúng... liên quan đến O, L và I. Nhưng S (SRP) và D (DIP) vẫn yêu cầu kỷ luật cấu trúc nghiêm ngặt — Go không tự động thực thi chúng.

### Chế độ lỗi

| Khiếm khuyết cấu trúc | Nguyên nhân gốc rễ | Hiệu ứng gợn sóng |
| --- | --- | --- |
| " SOLID = ủy quyền một interface cho mỗi struct " | Hiểu sai logic cơ bản của ISP | Lễ vô nghĩa, vi phạm nghiêm ngặt YAGNI |
| " Go structs thiếu lớp nên SRP không thành công" | Phạm vi cấu trúc SRP khó hiểu | Tạo Thần 500 dòng structs |
| "DIP = nhập generic interface packages " | Duy trì các ràng buộc kiểu Java DI lỗi thời | Khớp nối phụ thuộc interface được chia sẻ nghiêm trọng |

SRP xếp hạng đầu tiên vì nó tác động đến kiến ​​trúc nhiều nhất — nhưng nó tạo ra sự nhầm lẫn nặng nề khi đến từ nền tảng Java. Chúng ta hãy xem xét từng nguyên tắc riêng biệt.

---

## 2. HÌNH ẢNH

### SOLID Ánh xạ quyết định: Java → Go```mermaid
flowchart TD
    subgraph S["S — Single Responsibility"]
        S1["Java: 1 class = 1 formal reason"]
        S2["Go: 1 struct/package = 1 exact job"]
    end
    subgraph O["O — Open/Closed"]
        O1["Java: abstract class framework + override logic"]
        O2["Go: modular interface + strict new implementation"]
    end
    subgraph L["L — Liskov Substitution"]
        L1["Java: concrete subclass replaces abstract parent"]
        L2["Go: matching implementer replaces interface usage"]
    end
    subgraph I["I — Interface Segregation"]
        I1["Java: painfully split fat legacy interface"]
        I2["Go: maintain small limits from start — 1-3 methods"]
    end
    subgraph D["D — Dependency Inversion"]
        D1["Java: @Autowired mapping + global interface"]
        D2["Go: constructor injection wiring + consumer interface parameters"]
    end
```![SOLID in Go taxonomy card](./images/05-solid-in-go-taxonomy.png) *Hình: 5 nguyên tắc hình thức, thuật ngữ giống nhau, phương tiện hoạt động riêng biệt. Go thiếu các khung `abstract` , `extends` và `@Autowired` — nhưng các phần tử SOLID vẫn tồn tại nhờ sử dụng structs , interfaces và các hàm tạo rõ ràng.*

### SOLID Logic phát hiện vi phạm```mermaid
flowchart TD
    A[Review specific struct/package definition] --> B{Can you describe it utilizing 1 short sentence?}
    B -->|No — requiring the word 'and'| C["⚠️ Major SRP violation"]
    B -->|Yes| D{Does adding behavior = modifying the existing code layer?}
    D -->|Yes| E["⚠️ Major OCP violation"]
    D -->|No — adding new type parameters| F{Does the interface exceed 3 distinct methods?}
    F -->|Yes| G["⚠️ Definite ISP concern"]
    F -->|No| H{Does the struct depend upon a specific concrete type?}
    H -->|Yes| I["⚠️ Major DIP violation"]
    H -->|No — depends purely upon interface| J["✅ SOLID operations validated OK"]
```*Hình: 4 câu hỏi đánh giá tuần tự nhắm mục tiêu phát hiện vi phạm. Hoàn hảo để triển khai trong quá trình đánh giá mã — mỗi câu hỏi cụ thể kiểm tra chính xác 1 nguyên tắc.*

Bây giờ chúng ta sẽ triển khai từng nguyên tắc - bắt đầu với SRP, nguyên tắc thường bị vi phạm nhất.

---

### Ví dụ 1: Cơ bản — SRP: Một Struct , Một công việc

Một vị thần struct làm quá nhiều việc. Phân chia trách nhiệm.

> **Mục tiêu**: Khắc phục các vi phạm SRP.
> **Cách tiếp cận**: Mô tả struct . Nếu bạn sử dụng "và", hãy chia nó ra.
> **Ví dụ**: `OrderProcessor` trở thành `OrderValidator` cộng `OrderRepository` cộng `OrderNotifier` .```go
// ❌ SRP violation — God struct
type OrderProcessor struct {
	db       *sql.DB
	smtp     *smtp.Client
	rules    []ValidationRule
}

func (op *OrderProcessor) Process(o *Order) error {
	// validation (reason 1)
	for _, r := range op.rules { /* validate */ }
	// persistence (reason 2)
	_, err := op.db.Exec("INSERT INTO orders") 
	// notification (reason 3)
	op.smtp.Send(o.CustomerEmail, "Order confirmed")
	return nil
}

// ✅ SRP fixed — 1 job per struct
type OrderValidator struct {
	rules []ValidationRule
}
func (v *OrderValidator) Validate(o *Order) error {
	for _, r := range v.rules {
		if err := r.Check(o); err != nil {
			return err
		}
	}
	return nil
}

type OrderRepository struct {
	db *sql.DB
}
func (r *OrderRepository) Save(ctx context.Context, o *Order) error {
	_, err := r.db.ExecContext(ctx, "INSERT INTO orders")
	return err
}

type OrderNotifier struct {
	smtp *smtp.Client
}
func (n *OrderNotifier) Notify(ctx context.Context, o *Order) error {
	return n.smtp.Send(o.CustomerEmail, "Order confirmed")
}

// Orchestrator — thin coordinator
type OrderService struct {
	validator *OrderValidator
	repo      *OrderRepository
	notifier  *OrderNotifier
}
func (s *OrderService) Process(ctx context.Context, o *Order) error {
	if err := s.validator.Validate(o); err != nil { return err }
	if err := s.repo.Save(ctx, o); err != nil       { return err }
	_ = s.notifier.Notify(ctx, o) // non-critical
	return nil
}
```> **Takeaway**: SRP trong Go có nghĩa là struct có một công việc. Không sử dụng "và" trong mô tả của nó. Tọa độ dịch vụ struct , nó không giữ logic.

---

### Ví dụ 2: Trung cấp — OCP + DIP: Thêm hành vi mà không sửa đổi

Thêm giá strategy bằng cách tạo struct mới, không sửa đổi dịch vụ. Việc tiêm Interface đáp ứng OCP và DIP.

> **Mục tiêu**: OCP — mở để mở rộng, đóng để sửa đổi. DIP - phụ thuộc vào sự trừu tượng.
> **Cách tiếp cận**: Sử dụng `PricingStrategy` interface . Triển khai cụ thể.
> **Ví dụ**: Thêm `WeekendPricing` mà không sửa đổi `CheckoutService` .```go
// ocp_dip.go — Open/Closed + Dependency Inversion
package checkout

import "time"

// Interface — abstraction (DIP)
type PricingStrategy interface {
	Calculate(entry, exit time.Time) int64 // cents
}

// ✅ Implementation 1
type HourlyPricing struct {
	RatePerHour int64
}
func (h *HourlyPricing) Calculate(entry, exit time.Time) int64 {
	hours := int64(exit.Sub(entry).Hours()) + 1
	return hours * h.RatePerHour
}

// ✅ Implementation 2 — added LATER, NO code modified
type BlockPricing struct {
	RatePerBlock int64
	BlockHours   int64
}
func (b *BlockPricing) Calculate(entry, exit time.Time) int64 {
	hours := int64(exit.Sub(entry).Hours())
	blocks := (hours / b.BlockHours) + 1
	return blocks * b.RatePerBlock
}

// ✅ Implementation 3 — added EVEN LATER. CheckoutService remains unmodified.
type WeekendPricing struct {
	Weekday PricingStrategy // composition!
	Weekend PricingStrategy
}
func (w *WeekendPricing) Calculate(entry, exit time.Time) int64 {
	if entry.Weekday() == time.Saturday || entry.Weekday() == time.Sunday {
		return w.Weekend.Calculate(entry, exit)
	}
	return w.Weekday.Calculate(entry, exit)
}

// CheckoutService — NEVER MODIFIED when new pricing added
// Depends on interface (DIP)
type CheckoutService struct {
	pricing PricingStrategy // injected at construction
}

func NewCheckoutService(p PricingStrategy) *CheckoutService {
	return &CheckoutService{pricing: p}
}

func (cs *CheckoutService) Checkout(entry, exit time.Time) int64 {
	return cs.pricing.Calculate(entry, exit)
}
```> **Tại sao lại là OCP và DIP?**
> **OCP**: `CheckoutService` không thể sửa đổi. Để thêm `WeekendPricing` , hãy viết một struct mới . Mã dịch vụ không có thay đổi. 
> **DIP**: `CheckoutService` phụ thuộc vào `PricingStrategy` (trừu tượng), không phải `HourlyPricing` (cụ thể). 

> **Bài học rút ra**: OCP cộng với DIP trong Go là hệ thống dây dẫn và bộ tạo interface . Trình xây dựng cộng với interface là tất cả những gì bạn cần. Không cần khuôn khổ.

\n### Ví dụ 3: Nâng cao — ISP + LSP: Tách Interface & Đảm bảo khả năng thay thế

Quy tắc ISP: người gọi cần một phương thức sẽ nhận được interface với một phương thức. Quy tắc LSP: mọi triển khai đều hoạt động chính xác khi được thay thế.

> **Mục tiêu**: ISP — chia mỡ interfaces . LSP - đảm bảo khả năng thay thế an toàn.
> **Phương pháp tiếp cận**: Xây dựng nhỏ interfaces . Cấm hoảng loạn hoặc giá trị trả về không mong muốn trong quá trình triển khai.
> **Ví dụ**: Kho lưu trữ chia thành Reader và Writer. Phát hiện vi phạm LSP.```go
// isp_lsp.go — Interface Segregation plus Liskov Substitution
package repository

import "context"

// ✅ ISP — split by caller requirements, not by domain
type UserReader interface {
	FindByID(ctx context.Context, id int64) (*User, error)
	FindByEmail(ctx context.Context, email string) (*User, error)
}

type UserWriter interface {
	Save(ctx context.Context, u *User) error
	Delete(ctx context.Context, id int64) error
}

// Composed interface if both are required
type UserRepository interface {
	UserReader
	UserWriter
}

// ✅ Query handler requires Reader only — Writer methods are ignored
func GetUserHandler(reader UserReader) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		user, err := reader.FindByID(r.Context(), parseID(r))
		// handler logic
	}
}

// ✅ Command handler requires Writer only
func DeleteUserHandler(writer UserWriter) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		err := writer.Delete(r.Context(), parseID(r))
		// handler logic
	}
}

// --- LSP — Substitutability Rules ---

// ✅ Correct: PostgresRepo implements the full contract
type PostgresRepo struct{ db *sql.DB }
func (r *PostgresRepo) FindByID(ctx context.Context, id int64) (*User, error) {
	// Proper implementation
	return nil, sql.ErrNoRows // allow caller checking via errors.Is
}

// ❌ LSP VIOLATION: CacheRepo.Delete() panics
type BrokenCacheRepo struct{}
func (r *BrokenCacheRepo) Delete(ctx context.Context, id int64) error {
	panic("cache does not support delete") // 🔴 LSP VIOLATION
	// The caller expects an error return. A panic breaks substitution.
}

// ✅ LSP CORRECT: CacheRepo returns explicit errors
type CacheRepo struct{}
func (r *CacheRepo) Delete(ctx context.Context, id int64) error {
	return fmt.Errorf("cache repository does not support delete") // ✅ safe handling
}
```> **Tại sao panic lại tương đương với vi phạm LSP?**
> Hợp đồng interface quy định `Delete() error` . Người gọi mong đợi một lỗi trả về và xử lý nó. `panic` làm hỏng quá trình thực thi. Việc thay thế `BrokenCacheRepo` cho `PostgresRepo` gây ra sự cố runtime . LSP bị hỏng.
>
> **Quy tắc ISP**: Nếu quá trình triển khai phải để trống các phương thức hoặc gây hoảng loạn thì mục tiêu interface quá béo. Chia nó ra.

> **Takeaway**: ISP trong Go tương đương với việc soạn thảo interfaces nhỏ theo yêu cầu. LSP ra lệnh cho tất cả các triển khai hoạt động hợp lý khi được thay thế mà không gây hoảng loạn hoặc thất bại thầm lặng.

---

## 4. Cạm bẫy

| # | Mức độ nghiêm trọng | Khiếm khuyết | Hậu quả | Sửa chữa |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Gây tử vong | Hoảng loạn bên trong quá trình triển khai interface | Vi phạm LSP và sự cố ứng dụng | Trả về lỗi tiêu chuẩn. Đừng panic . |
| 2 | 🔴 Gây tử vong | Chúa structs với vô số phụ thuộc | ISP và SRP bị vi phạm, kiểm tra thất bại | Chia thành các định nghĩa struct tập trung. |
| 3 | 🟡 Chung | Ưu tiên interface cho mọi struct | Lễ và sự gián tiếp vô ích | Xác định một loại cụ thể đầu tiên. Chỉ sử dụng interfaces khi cần mocks . |
| 4 | 🟡 Chung | Đã chia sẻ interface packages | Khớp nối chặt chẽ đánh bại DIP | Người tiêu dùng xác định interfaces nguyên bản khi được sử dụng. |
| 5 | 🔵 Nhỏ | Đặt tên structs như `XxxImpl` | Định dạng kế thừa Java | Đặt tên mang tính mô tả như `PostgresRepo` . |

---

## 5. GIỚI THIỆU

| Tài nguyên | Loại | Liên kết | Ghi chú |
| --- | --- | --- | --- |
| SOLID Go Thiết kế | Trình bày | https://dave.cheney.net/2016/08/20/ solid -go-design | Buổi nói chuyện của Dave Cheney |
| Go Châm ngôn | Triết học | https://go-proverbs.github.io/ | Báo giá kiến ​​trúc |
| Có hiệu lực Go | Tài liệu | https://go.dev/doc/effect_go | Mẫu mã gốc |

---

## 6. KHUYẾN NGHỊ

Các hoạt động cốt lõi của ** SOLID trong Go ** rất rõ ràng. Các phần mở rộng bên dưới chuyển đổi các nguyên tắc SOLID thành các mẫu và kiến ​​trúc thực tế.

| Gia hạn | Khi nào | Cơ sở lý luận | Liên kết tập tin |
| --- | --- | --- | --- |
| [Design Patterns Formats](./06-design-patterns-go-way.md) | Khi triển khai các mẫu cấu trúc | Factory , Strategy , Observer | Trình tự tiếp theo |
| [OOP Mental Model Configs](./01-oop-mental-model.md) | Rà soát các quy tắc cơ bản | Đánh giá cấu trúc rộng rãi | Go quay lại |
| [Interfaces structure deep dive](../interfaces/02-di-mocking-patterns.md) | Khi cần logic mock | DI cấu trúc nối dây | Module băng qua |

---

**Điều hướng thư mục**: [← Interfaces module](./04-interfaces-polymorphism.md) · [→ Design Patterns logic](./06-design-patterns-go-way.md)