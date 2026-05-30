<!-- tags: golang, structs --> # 🧱 Structs & Composition > Structs , embedding , composition trên inheritance — cách tiếp cận cốt lõi của Go đối với OOP

📅 Đã tạo: 20-03-2026 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 17 phút đọc

| Khía cạnh | Chi tiết |
| ----------------- | ------------------------------------- |
| **Khái niệm** | Struct loại, embedding ( composition ) |
| **Trường hợp sử dụng** | Lập mô hình dữ liệu, thực thể DDD |
| **Thông tin chi tiết quan trọng** | Go KHÔNG có lớp nào, KHÔNG inheritance |
| ** Go triết lý** | Composition > Inheritance |

---

## 1. ĐỊNH NGHĨA

Bạn nhúng `sync.Mutex` trực tiếp vào struct và chuyển struct đó theo giá trị. Bản sao mutex — hai goroutines hiện khóa hai mutex khác nhau và cuộc đua dữ liệu bắt đầu. Đây là lỗi phổ biến nhất khi nhà phát triển sử dụng embedding mà không hiểu ngữ nghĩa giá trị.

> *Bạn lập mô hình một hệ thống với `User` , `AdminUser` , `Product` và `AuditLog` . Mọi loại đều cần `ID` , `CreatedAt` và `UpdatedAt` . Trong Java hoặc C#, bạn tạo `BaseEntity` và `extends` . Hai năm sau: hệ thống phân cấp sâu 5 lớp, `BaseEntity` có 20 phương pháp, các kỹ sư mới không thể biết nên ghi đè phương pháp nào và `AdminUser extends User extends BaseEntity extends Auditable` — một vấn đề kim cương. Tái cấu trúc chạm tới 200 tệp. Kỳ thi được nghỉ trong 3 ngày.*
>
> * Go không có lớp và không có inheritance . Thay vào đó: ** embedding ** — đặt `BaseModel` bên trong `User` thúc đẩy tất cả các trường và phương thức. `user.ID` , `user.CreatedAt` và `user.Touch()` hoạt động như thể chúng thuộc về `User` . Nhưng đây **không phải** "is-a" - đây là "has-a" với phương pháp quảng bá. Nó nhẹ, linh hoạt và loại bỏ vấn đề về kim cương.*

Điều này nghe có vẻ rõ ràng - nhưng [[E44]]] thô ẩn giấu một cái bẫy: `c2 := c1` sao chép struct , nhưng các trường slice và map chỉ sao chép tiêu đề của chúng. Cả structs hiện chia sẻ cùng một dữ liệu cơ bản. Lỗi này chỉ phát sinh trong quá trình sản xuất khi hai goroutines sửa đổi bản sao được chia sẻ đồng thời. Chúng tôi mổ xẻ cái bẫy đó trong CÂU HỎI.

### 1.1 Struct Tính năng

| Tính năng | Mô tả | Ví dụ |
| ---------------- | -------------- | ---------------------------- |
| Lĩnh vực | Thành viên dữ liệu nội bộ | `Name string` |
| Thẻ | Siêu dữ liệu rõ ràng (JSON, DB) | ` ` ` json:"name" ` ` ` |
| Embedding | Native Composition (has-a) | ` gõ Quản trị viên struct { Người dùng } ` |
| Anonymous struct | Ephemeral Inline struct | ` struct { X, Y int }{1, 2} ` |
| Constructor | Idiomatic Factory function | ` func Người dùng mới(...) *Người dùng ` |

### 1.2 Struct Tags — Reference Table

| Tag | Package | Description |
| --------------------- | ------------- | ------------------ |
| ` json:"name" ` | encoding/json | Binds JSON field name |
| ` json:"-" ` | encoding/json | Forces field skip |
| ` json:",omitempty" ` | encoding/json | Skips whenever zero value |
| ` db:"column" ` | sqlx/pgx | Maps DB column name |
| ` xác thực:"required" ` | validator | Applies Validation rules |
| ` gorm :"primaryKey" ` | gorm | Installs ORM configuration |

### 1.3 Failure Modes

| Error | Root Cause | Consequence | Fix |
| --- | ------------ | ------ | --- |
| Shallow copy struct containing slices | ` c2 := c1 ` copies the slice header but shares the underlying array | Mutating ` c2.Tags[0] ` also mutates ` c1.Tags[0] ` | Deep copy: ` copy(dst, src) ` for slices, manual clone for maps |
| Embedding ≠ inheritance | Developer assumes ` Quản trị viên ` "is-a" ` Người dùng ` | ` Quản trị viên ` is not assignable to a ` Người dùng ` variable | Use embedding for composition (has-a) and interfaces for polymorphism |
| Comparing struct with embedded slices | ` c1 == c2 ` when fields include a slice | Compile error — slices are not comparable | Use ` phản ánh.DeepEqual()` hoặc viết so sánh thủ công |

Struct tính năng, thẻ, chế độ lỗi - lý thuyết đã được đề cập. Bây giờ chúng ta hãy xem embedding hoạt động trực quan như thế nào và nó khác với inheritance như thế nào.

---

Các mẫu ở trên nghe có vẻ rõ ràng - nhưng có một cái bẫy nghiêm trọng: quảng cáo struct được nhúng có thể gây ra xung đột tên phương thức im lặng và sự hài lòng của interface được nhúng có thể trở nên mờ đục. Cái bẫy đó xuất hiện trong PITFALS.

## 2. HÌNH ẢNH

Ma sát tốn kém nhất với structs xuất phát từ việc coi embedding là inheritance . Quyết định map bên dưới buộc phải kiểm tra mạnh mẽ hơn: bạn có cần quảng bá phương thức hay bạn cần một phụ thuộc được đặt tên có quyền truy cập rõ ràng? ![Composition and embedding decision map](./images/01-composition-embedding-decision-map.png) *Hình: Một quyết định map phân chia bốn đường dẫn: các trường được đặt tên làm mặc định, embedding làm công cụ quảng bá có điều kiện, inheritance -suy nghĩ như một bẫy logic và sao chép ngữ nghĩa làm rủi ro sản xuất.*

Khi cây quyết định được định tuyến, phần mã bên dưới sẽ có thể thực hiện được. Đọc hàm tạo, nội dung nhúng và ví dụ sao chép sâu dưới dạng ba lần xác thực cho mô hình quyền sở hữu — chứ không phải dưới dạng bản trình diễn cú pháp bị ngắt kết nối.

## 3. MÃ

Với ** Structs & Composition **, chúng ta có một mô hình tinh thần cho embedding và phương pháp quảng bá. Bây giờ chúng tôi neo nó trong mã: các trường được đặt tên so với embedding , giá trị receivers so với pointer receivers , quảng cáo so với theo dõi - mỗi lựa chọn sẽ thay đổi hành vi runtime và sự hài lòng của interface .

### Ví dụ 1: Cơ bản — Structs & Hàm tạo

> **Mục tiêu**: Xác định struct bằng thẻ, xây dựng hàm tạo thành ngữ và sử dụng các tùy chọn chức năng để tạo linh hoạt.
> **Phương pháp tiếp cận**: `User` struct với các thẻ JSON, hàm tạo `NewUser()` và `NewUserWithOptions()` cho các tham số tùy chọn.
> **Ví dụ**: `json:"-"` ẩn trường `Password` khỏi đầu ra JSON. `WithAge(30)` chèn một tham số tùy chọn.```go
package main

import (
    "encoding/json"
    "fmt"
    "time"
)

// ✅ Struct definition — fields + tags
type User struct {
    ID        int64     `json:"id"`
    Email     string    `json:"email" validate:"required,email"`
    FullName  string    `json:"full_name"`
    Age       int       `json:"age,omitempty"`
    Password  string    `json:"-"`                // ✅ Never serialize
    CreatedAt time.Time `json:"created_at"`
    UpdatedAt time.Time `json:"updated_at"`
}

// ✅ Constructor pattern — idiomatic Go
func NewUser(email, name, password string) *User {
    now := time.Now()
    return &User{
        Email:     email,
        FullName:  name,
        Password:  password,
        CreatedAt: now,
        UpdatedAt: now,
    }
}

// ✅ Functional options — flexible constructor
type UserOption func(*User)

func WithAge(age int) UserOption {
    return func(u *User) { u.Age = age }
}

func WithID(id int64) UserOption {
    return func(u *User) { u.ID = id }
}

func NewUserWithOptions(email, name string, opts ...UserOption) *User {
    u := &User{
        Email:     email,
        FullName:  name,
        CreatedAt: time.Now(),
    }
    for _, opt := range opts {
        opt(u)
    }
    return u
}

func main() {
    u1 := NewUser("alice@example.com", "Alice", "secret123")

u2 := NewUserWithOptions("bob@example.com", "Bob",
        WithAge(30),
        WithID(42),
    )

// ✅ JSON marshal — Password excluded by json:"-"
    data, _ := json.MarshalIndent(u1, "", "  ")
    fmt.Println(string(data))
    fmt.Println(u2)
}
```> **Takeaway**: Struct + constructor = Go sự thay thế thành ngữ cho một lớp. `json:"-"` ẩn các trường nhạy cảm khỏi đầu ra JSON. Các tùy chọn chức năng cung cấp khả năng xây dựng linh hoạt mà không làm quá tải phương thức.

Một hàm tạo duy nhất xử lý một struct . Nhưng điều gì xảy ra khi 5 loại đều cần các trường `ID` giống nhau, `CreatedAt` và `UpdatedAt` - bạn có sao chép-dán chúng vào mọi struct không? Không. Embedding giải quyết vấn đề này: khai báo `BaseModel` một lần, nhúng nó ở mọi nơi.

---

Cơ bản composition là rõ ràng. Nhưng embedding có các quy tắc quảng cáo phức tạp - phương thức nào sẽ hiển thị và trường nào bị ẩn?

### Ví dụ 2: Trung cấp — Embedding & Composition > **Mục tiêu**: Nhúng `BaseModel` để sử dụng lại các trường và phương thức trên nhiều loại.
> **Phương pháp tiếp cận**: `User` nhúng `BaseModel` → `user.ID` và `user.SetTimestamps()` được thăng cấp.
> **Ví dụ**: Việc gọi `u.SetTimestamps()` đặt cả `CreatedAt` và `UpdatedAt` — sử dụng lại mã mà không cần inheritance .```go
package main

import (
    "fmt"
    "time"
)

// ✅ Base model — reusable fields + methods
type BaseModel struct {
    ID        int64     `json:"id"`
    CreatedAt time.Time `json:"created_at"`
    UpdatedAt time.Time `json:"updated_at"`
}

func (b *BaseModel) SetTimestamps() {
    now := time.Now()
    if b.CreatedAt.IsZero() {
        b.CreatedAt = now
    }
    b.UpdatedAt = now
}

// ✅ Embedding = composition (NOT inheritance!)
type User struct {
    BaseModel                // Embedded — fields/methods promoted
    Email    string `json:"email"`
    FullName string `json:"full_name"`
}

type Product struct {
    BaseModel
    Name  string  `json:"name"`
    Price float64 `json:"price"`
}

type AuditLog struct {
    BaseModel
    Action    string `json:"action"`
    UserID    int64  `json:"user_id"`
    TableName string `json:"table_name"`
}

func main() {
    u := User{
        Email:    "alice@example.com",
        FullName: "Alice",
    }

// ✅ Promoted methods — call directly on User
    u.SetTimestamps()

// ✅ Promoted fields — access directly
    u.ID = 1  // Same as u.BaseModel.ID = 1
    fmt.Println(u.ID, u.CreatedAt)

// ✅ Composition: User IS NOT a BaseModel
    // User HAS a BaseModel — no "is-a" relationship
}
```> **Tại sao lại nhúng thay vì sử dụng trường được đặt tên?**
> Trường được đặt tên `base BaseModel` yêu cầu `u.base.ID` và `u.base.SetTimestamps()` — dài dòng. Embedding ( `BaseModel` không có tên trường) thúc đẩy các trường và phương thức: `u.ID` và `u.SetTimestamps()` hoạt động trực tiếp. Cú pháp trông giống như inheritance , nhưng cơ chế hoàn toàn là composition .
>
> **Tại sao Go từ chối inheritance ?**
> Inheritance tạo ra sự liên kết chặt chẽ (con cái phụ thuộc vào phần bên trong của cha mẹ), vấn đề về lớp cơ sở dễ vỡ (sửa đổi cha mẹ làm hỏng con cái) và sự mơ hồ kim cương (nhiều xung đột inheritance ). Composition giữ cho khớp nối lỏng lẻo, độ phân giải phương thức đơn giản (tra cứu theo chiều rộng, không có vtable) và chỉ rõ ràng khi cần.

> **Takeaway**: Embedding = composition với khuyến mãi ngầm. A `User` "has-a" `BaseModel` , không bao giờ "is-a". Tái sử dụng các trường và phương thức mà không cần ghép nối inheritance . Embedding bao gồm việc sử dụng lại mã. Nhưng một điểm bất thường nguy hiểm ẩn bên dưới bề mặt: `c2 := c1` có vẻ giống như một bản sao an toàn, nhưng khi struct chứa các trường slice hoặc map , cả hai structs đều chia sẻ cùng một dữ liệu cơ bản. Lỗi này đã được gieo vào trong các định nghĩa ở trên - bây giờ hãy xem nó bị hỏng ở runtime .

--- Embedding quy tắc được bao gồm. Chuyển sang lãnh thổ Nâng cao: khả năng so sánh struct , bản sao nông và sâu và mẫu `Clone()` .

### Ví dụ 3: Nâng cao — So sánh & Sao chép sâu

> **Mục tiêu**: Hiểu các quy tắc so sánh struct , chẩn đoán bẫy sao chép nông và thiết lập mẫu `Clone()` .
> **Phương pháp tiếp cận**: Structs chỉ hỗ trợ các trường comparable `==` . Structs với slices hoặc maps yêu cầu sao chép sâu thủ công.
> **Ví dụ**: `p1 == p2` hoạt động (tất cả các trường comparable ). `c2 := c1` chia sẻ dữ liệu slice (bẫy sao chép nông). `c1.Clone()` tạo ra một bản sao độc lập an toàn.```go
package main

import "fmt"

// ✅ Comparable struct — all fields are comparable types
type Point struct {
    X, Y int
}

// ❌ NOT comparable — has slice field
type Config struct {
    Name  string
    Tags  []string  // slices are not comparable!
}

// ✅ Deep copy — manually copy reference types
func (c Config) Clone() Config {
    tagsCopy := make([]string, len(c.Tags))
    copy(tagsCopy, c.Tags)
    return Config{
        Name: c.Name,
        Tags: tagsCopy,
    }
}

func main() {
    p1 := Point{1, 2}
    p2 := Point{1, 2}
    fmt.Println(p1 == p2)  // true — struct comparison works

c1 := Config{Name: "app", Tags: []string{"go", "api"}}
    c2 := c1               // ⚠️ Shallow copy — Tags shares underlying array!
    c2.Tags[0] = "rust"
    fmt.Println(c1.Tags)   // [rust api] — c1 modified!

c3 := c1.Clone()       // ✅ Deep copy
    c3.Tags[0] = "python"
    fmt.Println(c1.Tags)   // [rust api] — c1 NOT modified
}
```> **Tại sao `c2 := c1` lại gây ra lỗi?**
> Phép gán Go struct sao chép tất cả các trường theo giá trị. Nhưng tiêu đề slice là `{pointer, len, cap}` - sao chép tiêu đề có nghĩa là chia sẻ array cơ bản. Sửa đổi `c2.Tags[0]` sửa đổi chia sẻ array , điều này cũng thay đổi `c1.Tags[0]` . Maps hoạt động theo cách tương tự. Cách khắc phục: luôn sao chép sâu các trường loại tham chiếu ( slices , maps , pointers ).
>
> **Khi nào nên sử dụng `reflect.DeepEqual` so với so sánh thủ công?**
> `reflect.DeepEqual` : thuận tiện, đệ quy, hoạt động với mọi loại. Sự cân bằng: chậm (chi phí phản ánh) và mù quáng về sự bình đẳng về ngữ nghĩa (hai dấu thời gian ở các múi giờ khác nhau biểu thị cùng một thời điểm). So sánh thủ công: nhanh chóng, cung cấp toàn quyền kiểm soát ngữ nghĩa. Trong mã sản xuất: sử dụng so sánh thủ công. Trong các thử nghiệm: `reflect.DeepEqual` hoặc `assert.Equal` đều được chấp nhận.

> **Takeaway**: Struct `==` chỉ hoạt động khi tất cả các trường là comparable (không có slices , maps hoặc hàm). Bẫy sao chép nông: các trường loại tham chiếu tiếp tục chia sẻ dữ liệu cơ bản sau khi gán. Triển khai `Clone()` cho any struct với các trường tham chiếu.

Bây giờ bạn đã biết cách xác định, xây dựng, nhúng và sao chép sâu structs . Cái bẫy nguy hiểm nhất vẫn còn: lỗi sao chép nông cạn chỉ xuất hiện trong quá trình sản xuất khi hai goroutines chia sẻ một bản sao struct .

---

## 4. Cạm bẫy

Cơ chế của ** Structs & Composition ** rất rõ ràng. Mục tiêu còn lại là nhận ra nơi mã gần như chính xác kéo theo lỗi composition hoặc xung đột phương thức im lặng vào sản xuất.

| # | Mức độ nghiêm trọng | Lỗi | Hậu quả | Sửa chữa |
|---|----------|-------|-------------|------|
| 1 | 🔴 Gây tử vong | Bản sao nông của structs với slices / maps | Dữ liệu cơ bản được chia sẻ → lỗi đột biến | Sao chép sâu qua phương thức `Clone()` |
| 2 | 🟡 Chung | Xử lý embedding là inheritance | Kỳ vọng sai về polymorphism ; `Admin` không thể gán cho `User` | Sử dụng embedding cho composition (has-a) và interfaces cho polymorphism |
| 3 | 🟡 Chung | Thiếu thẻ JSON | Tên trường xuất ra dưới dạng `FullName` thay vì `full_name` | Thêm `json:"snake_case"` vào mọi trường được xuất |
| 4 | 🟡 Chung | Xung đột tên phương thức từ nhiều lần nhúng | Lỗi biên dịch khi 2 kiểu nhúng xác định cùng tên phương thức | Sử dụng đường dẫn rõ ràng: `s.TypeA.Method()` |
| 5 | 🔵 Nhỏ | Xuất khẩu sự nhầm lẫn về khả năng hiển thị | Chữ thường `id` không được xuất → không thể truy cập được từ packages khác | Viết hoa cho công khai, viết thường cho riêng tư |

### 🔴 Cạm bẫy #1 — Bản sao nông âm thầm chia sẻ dữ liệu cơ bản `user2 := user1` sao chép các trường struct — nhưng các trường slice / map chỉ sao chép tiêu đề của chúng ( pointer + len + cap). Sửa đổi `user2.Tags[0]` làm hỏng `user1.Tags[0]` . Lỗi này ẩn trong thử nghiệm vì các thử nghiệm sử dụng dữ liệu mới - quá trình sản xuất kích hoạt lỗi này khi hai goroutines chia sẻ bản sao chép không chính xác struct .```go
// ❌ Shallow copy — shared slice
u2 := u1
u2.Tags[0] = "changed" // u1.Tags[0] was also changed!

// ✅ Deep copy
u2 := u1
u2.Tags = slices.Clone(u1.Tags)
```Bây giờ bạn đã biết thiết kế struct , embedding , sao chép sâu và cạm bẫy nguy hiểm nhất. Các tài nguyên bên dưới đi sâu hơn vào bên trong bộ nhớ struct .

---

## 5. GIỚI THIỆU

| Tài nguyên | Loại | Liên kết | Ghi chú |
| ------------ | -------- | ------------------------------------------------------------------------------ | ----- |
| Go Structs | Chính thức | [go.dev/tour/moretypes/2](https://go.dev/tour/moretypes/2) | Struct hướng dẫn cơ bản |
| Struct Thẻ | Chính thức | [pkg.go.dev/reflect#StructTag](https://pkg.go.dev/reflect#StructTag) | Phân tích cú pháp thẻ Runtime và thông số format |
| Có hiệu lực Go | Chính thức | [go.dev/doc/effective_go#embedding](https://go.dev/doc/effective_go#embedding) | mẫu Composition và embedding |

---

## 6. KHUYẾN NGHỊ

Cơ chế cốt lõi của ** Structs & Composition ** được đề cập. Các tài nguyên bên dưới mở rộng thiết kế struct vào sản xuất: thẻ khai báo, hàm tạo linh hoạt và interface dựa trên polymorphism .

| Gia hạn | Khi nào nên đọc tiếp | Cơ sở lý luận | Tệp/Liên kết |
| ------- | ------- | ----- | --------- |
| Thẻ, Tùy chọn & Builder | Các hàm tạo linh hoạt, nội bộ thẻ struct | Tùy chọn chức năng, mẫu builder , hệ thống thẻ dựa trên phản ánh | [02-tags-options-builder.md](./02-tags-options-builder.md) |
| Interfaces | Polymorphism trong Go | Interfaces là cách tiếp cận của Go đối với polymorphism — thay thế inheritance | [../interfaces/01-implicit-io-patterns.md](../interfaces/01-implicit-io-patterns.md) |
| Pointers & Bộ nhớ | Căn chỉnh bố cục, đệm | `unsafe.Sizeof` , căn chỉnh trường, thiết kế thân thiện với bộ đệm struct | [../basics/04-pointers-memory.md](../basics/04-pointers-memory.md) |

---

**Điều hướng tuần tự**: [← Functions](../functions/) · [→ Tags & Options](./02-tags-options-builder.md)