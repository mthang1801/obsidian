<!-- tags: golang, generics --> # 🧬 Generics — Loại Tham số, Ràng buộc, Generic Mẫu

> Go 1.18+ generics : tham số kiểu, ràng buộc, cấu trúc dữ liệu generic 📅 Đã tạo: 2026-03-20 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 15 phút đọc

| Khía cạnh | Chi tiết |
| ----------------- | ----------------------------------------------------------------------------------- |
| **Phiên bản** | Go 1.18+ |
| **Trường hợp sử dụng** | Mã có thể tái sử dụng an toàn về loại, không có interface {} đấm bốc |
| **Thông tin chi tiết quan trọng** | Generics được giải quyết tại biên dịch- time — không có chi phí runtime |
| ** Go triết lý** | "Sao chép một chút sẽ tốt hơn là phụ thuộc một chút" — nhưng hãy sử dụng generics khi cần |

---

## 1. ĐỊNH NGHĨA

PR đầu tiên của bạn sử dụng generics : bạn viết `func Map [T any, R any](s []T, f func(T) R) []R` — người đánh giá chấp thuận nhưng hỏi: "tại sao không sử dụng `comparable` thay vì `any` ?" Bạn thay đổi nó, quá trình biên dịch không thành công vì `comparable` không đáp ứng được ràng buộc bắt buộc.

> *Bạn viết `func MinInt(a, b int) int` . Xong. Sau đó, bạn cần `MinFloat64` , `MinString` - sao chép-dán, thay đổi loại. `Contains([]int, int)` → thêm `ContainsString` , `ContainsFloat64` . Sáu chức năng, logic giống hệt nhau, chỉ khác loại - vi phạm DRY ở cấp hệ thống loại. Thêm một loại mới? Sửa sáu chỗ. Lỗi logic? Sửa sáu chỗ. Xem xét PR? Đọc sáu chức năng giống hệt nhau.*
>
> * Go 1.18 giải quyết vấn đề này bằng generics : `Min [T cmp.Ordered](a, b T) T` — một hàm, tất cả các loại được sắp xếp. Biên dịch- time kiểm tra loại, không có chi phí runtime , không có quyền anh như `interface{}` . Nhưng có một cái bẫy: over- generics biến Go thành Java — mã không thể đọc được, sự trừu tượng không cần thiết. Quy tắc: nếu bạn không thể liệt kê ít nhất 3 loại cụ thể sẽ sử dụng generic , thì đừng đặt nó generic . Cái bẫy đó sẽ xuất hiện trong PITFALS.*

### Generics Cú pháp

| Yếu tố | Cú pháp | Ví dụ |
| ---------------- | -------------- | ------------------------- |
| Nhập tham số | `[T any]` | `func Print [T any](v T) ` |
| Ràng buộc | `[T Constraint]` | `[T comparable]` |
| Nhiều thông số | `[K comparable, V any]` | Hàm Map |
| Liên minh hạn chế | `int \| float64` | Các phép toán số |
| `~int` | Loại cơ bản | Bao gồm `type MyInt int` |

### Các ràng buộc tích hợp

| Ràng buộc | Mô tả | Package |
| --------------------- | ------------------------------ | ------------------------------ |
| `any` | Any loại ( `interface{}` ) | dựng sẵn |
| `comparable` | Hỗ trợ `==` , `!=` | dựng sẵn |
| `constraints.Ordered` | Hỗ trợ `<` , `>` , `<=` , `>=` | `golang.org/x/exp/constraints` |
| `constraints.Integer` | Tất cả các loại số nguyên | `golang.org/x/exp/constraints` |
| `constraints.Float` | `float32` , `float64` | `golang.org/x/exp/constraints` |
| `cmp.Ordered` | Go 1.21+ loại được đặt hàng | `cmp` |

### Khi nào nên sử dụng Generics | Sử dụng | Không sử dụng |
| ------------------------------ | ------------------------------- |
| Vùng chứa an toàn loại ( stack , queue) | Chức năng đơn giản với 1-2 loại |
| Các hàm tiện ích ( map , lọc, giảm) | Khi interface {} ổn |
| Giảm trùng lặp mã | Khi nó ảnh hưởng đến khả năng đọc |
| Tránh phản ánh | Codebase nhỏ với vài loại |

Cú pháp, các ràng buộc, khi nào nên sử dụng - đủ lý thuyết. Chúng ta hãy xem generics so sánh trực quan với interfaces và hình ảnh phản chiếu như thế nào.

---
## 2. HÌNH ẢNH

Generics chỉ hữu ích khi chúng giải quyết được áp lực trừu tượng thực sự. Nếu không, chúng sẽ nhanh chóng rơi vào tình trạng "mã tổng quát nhưng không thể đọc được". Quyết định map bên dưới buộc bạn phải khóa câu hỏi đó trước khi viết tham số loại khác. ![Generics decision map](./images/02-generics-decision-map.png) *Hình: Quyết định generics map bắt đầu từ lựa chọn mặc định — mã cụ thể — và chỉ mở về phía trừu tượng interface hoặc generic khi áp lực đủ rõ ràng để biện minh cho điều đó.*

Khi thứ tự quyết định đã đúng, phần mã bên dưới sẽ ít mang tính lý thuyết hơn. Mỗi ví dụ thể hiện chính xác khi nào generics giảm trùng lặp và khi interface hoặc mã cụ thể vẫn là lựa chọn rõ ràng hơn.

## 3. MÃ

Với ** Generics — Tham số loại, ràng buộc, mẫu Generic **, quyết định map được thiết lập. Bây giờ chúng ta hãy map viết mã để xem mỗi quyết định - cụ thể so với generic , `any` so với ràng buộc tùy chỉnh, chức năng so với loại - thực sự thay đổi hành vi biên dịch- time và trải nghiệm xem xét mã.

### Ví dụ 1: Hàm cơ bản — Generic > **Mục tiêu**: Các hàm tiện ích an toàn loại thay thế interface {} / sao chép mã
> **Yêu cầu**: Go 1.18+
> **Kết quả**: Thư viện tiện ích an toàn, có thể tái sử dụng```go
package main

import (
    "cmp"
    "fmt"
)

// ✅ Generic function — works with any comparable type
func Contains[T comparable](slice []T, target T) bool {
    for _, v := range slice {
        if v == target {
            return true
        }
    }
    return false
}

// ✅ Generic with constraint — cmp.Ordered (Go 1.21+)
func Max[T cmp.Ordered](a, b T) T {
    if a > b {
        return a
    }
    return b
}

func Min[T cmp.Ordered](a, b T) T {
    if a < b {
        return a
    }
    return b
}

// ✅ Clamp value to range
func Clamp[T cmp.Ordered](val, min, max T) T {
    if val < min {
        return min
    }
    if val > max {
        return max
    }
    return val
}

// ✅ Map function — transform slice
func Map[T any, U any](slice []T, fn func(T) U) []U {
    result := make([]U, len(slice))
    for i, v := range slice {
        result[i] = fn(v)
    }
    return result
}

// ✅ Filter function
func Filter[T any](slice []T, fn func(T) bool) []T {
    result := make([]T, 0)
    for _, v := range slice {
        if fn(v) {
            result = append(result, v)
        }
    }
    return result
}

// ✅ Reduce function
func Reduce[T any, U any](slice []T, init U, fn func(U, T) U) U {
    acc := init
    for _, v := range slice {
        acc = fn(acc, v)
    }
    return acc
}

func main() {
    // ✅ Works with any type
    fmt.Println(Contains([]int{1, 2, 3}, 2))           // true
    fmt.Println(Contains([]string{"go", "rust"}, "go")) // true

fmt.Println(Max(10, 20))       // 20
    fmt.Println(Max("go", "rust")) // rust (lexicographic)

fmt.Println(Clamp(150, 0, 100)) // 100

// ✅ Map: []int → []string
    nums := []int{1, 2, 3, 4, 5}
    strs := Map(nums, func(n int) string {
        return fmt.Sprintf("#%d", n)
    })
    fmt.Println(strs) // [#1 #2 #3 #4 #5]

// ✅ Filter: even numbers
    evens := Filter(nums, func(n int) bool { return n%2 == 0 })
    fmt.Println(evens) // [2 4]

// ✅ Reduce: sum
    sum := Reduce(nums, 0, func(acc, n int) int { return acc + n })
    fmt.Println(sum) // 15
}
```> **Takeaway**: hàm Generic = một hàm, tất cả các loại. `cmp.Ordered` để so sánh, `comparable` cho `==` . Tự động phát hiện suy luận kiểu - không cần chỉ định thông số loại trong hầu hết các trường hợp.

 Các hàm Generic bao gồm các hoạt động tiện ích. Nhưng khi bạn cần generic **types** — Stack , Queue, Result — và **ràng buộc** tùy chỉnh** cho các loại miền như `Money` , `Temperature` thì sao? Bạn phải hiểu các mẫu `~int` (dấu ngã) và generic struct .

### Ví dụ 2: Trung cấp — Ràng buộc tùy chỉnh & loại Generic > **Mục tiêu**: Xác định các ràng buộc tùy chỉnh và cấu trúc dữ liệu generic > **Yêu cầu**: Nhập cú pháp tham số
> **Kết quả**: Vùng chứa an toàn về loại, các ràng buộc theo miền cụ thể```go
package main

import (
    "encoding/json"
    "fmt"
)

// ✅ Custom constraint — Numeric types
type Number interface {
    ~int | ~int8 | ~int16 | ~int32 | ~int64 |
    ~uint | ~uint8 | ~uint16 | ~uint32 | ~uint64 |
    ~float32 | ~float64
}

// ✅ ~ (tilde) = underlying type — includes type aliases
type Money int64         // underlying type is int64
type Temperature float64 // underlying type is float64

func Sum[T Number](nums []T) T {
    var total T
    for _, n := range nums {
        total += n
    }
    return total
}

// ✅ Generic Stack
type Stack[T any] struct {
    items []T
}

func NewStack[T any]() *Stack[T] {
    return &Stack[T]{items: make([]T, 0)}
}

func (s *Stack[T]) Push(item T) {
    s.items = append(s.items, item)
}

func (s *Stack[T]) Pop() (T, bool) {
    if len(s.items) == 0 {
        var zero T  // ✅ Zero value of any type
        return zero, false
    }
    item := s.items[len(s.items)-1]
    s.items = s.items[:len(s.items)-1]
    return item, true
}

func (s *Stack[T]) Peek() (T, bool) {
    if len(s.items) == 0 {
        var zero T
        return zero, false
    }
    return s.items[len(s.items)-1], true
}

func (s *Stack[T]) Len() int { return len(s.items) }

// ✅ Generic Pair
type Pair[A, B any] struct {
    First  A
    Second B
}

func NewPair[A, B any](a A, b B) Pair[A, B] {
    return Pair[A, B]{First: a, Second: b}
}

// ✅ Generic Result (like Rust's Result<T, E>)
type Result[T any] struct {
    value T
    err   error
}

func Ok[T any](val T) Result[T]     { return Result[T]{value: val} }
func Err[T any](err error) Result[T] { return Result[T]{err: err} }

func (r Result[T]) Unwrap() (T, error) { return r.value, r.err }
func (r Result[T]) IsOk() bool         { return r.err == nil }

func main() {
    // ✅ Custom Money type works with Sum
    prices := []Money{1990, 2990, 599}
    fmt.Println("Total:", Sum(prices)) // 5579

temps := []Temperature{36.5, 37.2, 38.1}
    fmt.Println("Avg:", Sum(temps)/Temperature(len(temps)))

// ✅ Generic Stack
    stack := NewStack[string]()
    stack.Push("hello")
    stack.Push("world")
    val, _ := stack.Pop()
    fmt.Println(val) // "world"

// ✅ Integer stack
    intStack := NewStack[int]()
    intStack.Push(1)
    intStack.Push(2)

// ✅ Pair
    p := NewPair("user-123", 42)
    fmt.Println(p.First, p.Second)

// ✅ Result
    result := Ok(42)
    if result.IsOk() {
        val, _ := result.Unwrap()
        fmt.Println("Value:", val)
    }
}
```> **Tại sao `~int` thay vì `int` trong một ràng buộc?**
> `int` chỉ khớp với loại chính xác `int` . `~int` khớp với loại any có loại cơ bản là `int` - bao gồm `type Money int64` , `type UserID int` . Dấu ngã ( `~` ) có nghĩa là "khớp loại cơ bản" - điều này là bắt buộc để generics hoạt động với các loại miền tùy chỉnh.

> **Takeaway**: Ràng buộc tùy chỉnh ( `Number` , `Entity` ) bật tính năng dành riêng cho miền generics . Mẫu `var zero T` mang lại giá trị 0 một cách an toàn. Generic các loại ( `Stack[T]` , `Result[T]` ) thiết lập các thùng chứa loại an toàn.

 Các hàm và kiểu Generic bao gồm mã cấp thư viện. Nhưng trong DDD - khi bạn đặc biệt cần CRUD kho lưu trữ generic cho tất cả các thực thể - generics trở thành vũ khí DRY chính ở cấp độ kiến ​​​​trúc.

### Ví dụ 3: Nâng cao — Generic Mẫu kho lưu trữ

> **Mục tiêu**: Generic Kho lưu trữ CRUD cho thực thể any > **Yêu cầu**: Database khái niệm, generics > **Kết quả**: Lớp kho lưu trữ DRY```go
package main

import (
    "context"
    "encoding/json"
    "errors"
    "fmt"
    "sync"
    "time"
)

// ✅ Entity constraint — all entities must have ID
type Entity interface {
    GetID() string
}

// ✅ Generic Repository interface
type Repository[T Entity] interface {
    FindByID(ctx context.Context, id string) (T, error)
    FindAll(ctx context.Context) ([]T, error)
    Create(ctx context.Context, entity T) error
    Update(ctx context.Context, entity T) error
    Delete(ctx context.Context, id string) error
}

// ✅ In-memory implementation (for demo/testing)
type InMemoryRepo[T Entity] struct {
    mu    sync.RWMutex
    store map[string]T
}

func NewInMemoryRepo[T Entity]() *InMemoryRepo[T] {
    return &InMemoryRepo[T]{
        store: make(map[string]T),
    }
}

func (r *InMemoryRepo[T]) FindByID(_ context.Context, id string) (T, error) {
    r.mu.RLock()
    defer r.mu.RUnlock()

entity, ok := r.store[id]
    if !ok {
        var zero T
        return zero, fmt.Errorf("entity %s not found", id)
    }
    return entity, nil
}

func (r *InMemoryRepo[T]) FindAll(_ context.Context) ([]T, error) {
    r.mu.RLock()
    defer r.mu.RUnlock()

items := make([]T, 0, len(r.store))
    for _, v := range r.store {
        items = append(items, v)
    }
    return items, nil
}

func (r *InMemoryRepo[T]) Create(_ context.Context, entity T) error {
    r.mu.Lock()
    defer r.mu.Unlock()

if _, exists := r.store[entity.GetID()]; exists {
        return errors.New("entity already exists")
    }
    r.store[entity.GetID()] = entity
    return nil
}

func (r *InMemoryRepo[T]) Update(_ context.Context, entity T) error {
    r.mu.Lock()
    defer r.mu.Unlock()

if _, exists := r.store[entity.GetID()]; !exists {
        return errors.New("entity not found")
    }
    r.store[entity.GetID()] = entity
    return nil
}

func (r *InMemoryRepo[T]) Delete(_ context.Context, id string) error {
    r.mu.Lock()
    defer r.mu.Unlock()

delete(r.store, id)
    return nil
}

// ✅ Concrete entities
type User struct {
    ID    string `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

func (u User) GetID() string { return u.ID }

type Product struct {
    ID    string  `json:"id"`
    Name  string  `json:"name"`
    Price float64 `json:"price"`
}

func (p Product) GetID() string { return p.ID }

// ✅ Generic service — reusable business logic
type CRUDService[T Entity] struct {
    repo Repository[T]
}

func NewCRUDService[T Entity](repo Repository[T]) *CRUDService[T] {
    return &CRUDService[T]{repo: repo}
}

func (s *CRUDService[T]) GetAll(ctx context.Context) ([]T, error) {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()
    return s.repo.FindAll(ctx)
}

func main() {
    ctx := context.Background()

// ✅ Same repository code works for User AND Product
    userRepo := NewInMemoryRepo[User]()
    userSvc := NewCRUDService[User](userRepo)

productRepo := NewInMemoryRepo[Product]()
    productSvc := NewCRUDService[Product](productRepo)

// Create users
    userRepo.Create(ctx, User{ID: "u1", Name: "Alice", Email: "alice@go.dev"})
    userRepo.Create(ctx, User{ID: "u2", Name: "Bob", Email: "bob@go.dev"})

// Create products
    productRepo.Create(ctx, Product{ID: "p1", Name: "Go Book", Price: 29.99})

users, _ := userSvc.GetAll(ctx)
    products, _ := productSvc.GetAll(ctx)

usersJSON, _ := json.MarshalIndent(users, "", "  ")
    productsJSON, _ := json.MarshalIndent(products, "", "  ")
    fmt.Println("Users:", string(usersJSON))
    fmt.Println("Products:", string(productsJSON))
}
```> **Tại sao lại có ràng buộc `Entity` interface thay vì `any` ?**
> A `Repository[T any]` không biết liệu thực thể có phương thức `GetID()` hay không → nó không thể tra cứu theo ID. Ràng buộc `Entity` đảm bảo `GetID() string` tồn tại → kho lưu trữ vừa là generic vừa an toàn về kiểu. Trong quá trình sản xuất: thay thế `InMemoryRepo` bằng `PostgresRepo[T Entity]` được hỗ trợ bởi `sqlx` / `pgx` .

> **Takeaway**: Generic kho lưu trữ = 1 cơ sở mã, N loại thực thể. Ràng buộc `Entity` thực thi hợp đồng. `sync.RWMutex` đảm bảo an toàn đồng thời. Trong quá trình sản xuất, hãy hoán đổi kho lưu trữ trong bộ nhớ lấy phần phụ trợ RDBMS.

Bây giờ bạn đã tìm hiểu các hàm generic , các ràng buộc tùy chỉnh, các loại generic và mẫu kho lưu trữ generic . Bây giờ đến phần nguy hiểm: over- generics - cái bẫy được thiết lập ở đầu bài viết này biến Go trực tiếp thành Java.

---

## 4. Cạm bẫy

Cơ chế của ** Generics — Tham số loại, ràng buộc, Generic Mẫu** rất rõ ràng. Điều còn lại là nhận ra những điểm mà mã _gần như đúng_ vô tình biến Go thành Java.

| # | Mức độ nghiêm trọng | Lỗi | Hậu quả | Sửa chữa |
|---|----------|-------|-------------|------|
| 1 | 🟡 Chung | Over- generics (kiểu Java) | Mã không thể đọc được, độ phức tạp không cần thiết | Ưu tiên các loại bê tông trước; chỉ sử dụng generics khi chứng minh được sự trùng lặp |
| 2 | 🟡 Chung | `~int` so với `int` nhầm lẫn | Các loại tùy chỉnh ( `type Money int` ) không khớp với ràng buộc `int` | Sử dụng `~int` để bao gồm tất cả các loại cơ bản |
| 3 | 🟡 Chung | Kiểu suy luận không thành công | Biên dịch lỗi với thông báo không rõ ràng | Chỉ định rõ ràng các thông số loại: `Fn [int](...) ` |
| 4 | 🔵 Nhỏ | Trả về giá trị bằng 0 | `return T{}` không biên dịch cho generics | Sử dụng `var zero T; return zero` |
| 5 | 🔵 Nhỏ | Không thể thêm phương thức nhập thông số | `T.Method()` không biên dịch | Xác định ràng buộc interface bằng các phương thức được yêu cầu |

### 🟡 Cạm bẫy #1 — Over- generics = Hội chứng Java

 Văn hóa Go yêu cầu loại cụ thể trước tiên. Generics chỉ nhập khi mã **có thể được sao chép** trên hơn 3 loại. Viết `Filter[T]` cho các tiện ích thu thập là hợp lý. Viết `UserService[T UserRepo]` khi chỉ tồn tại một triển khai là sự trừu tượng không cần thiết.

**Quy tắc**: Nếu bạn không thể liệt kê ít nhất 3 loại cụ thể sẽ sử dụng hàm generic của mình — đừng viết chung chung.

Bạn đã điều hướng các hàm, loại, kho lưu trữ generic và bẫy quá mức generics . Các tài nguyên dưới đây cung cấp nội dung sâu sắc.

---

## 5. GIỚI THIỆU

| Tài nguyên | Loại | Liên kết | Ghi chú |
| ------------------------ | -------- | ------------------------------------------------------------------------------------------ | ----- |
| Go Generics Hướng dẫn | Chính thức | [go.dev/doc/tutorial/generics](https://go.dev/doc/tutorial/generics) | Hướng dẫn thân thiện với người mới bắt đầu |
| Loại Thông số Đề xuất | Chính thức | [go.dev/blog/intro-generics](https://go.dev/blog/intro-generics) | Cơ sở thiết kế kiến ​​trúc sâu sắc |
| ràng buộc package | Chính thức | [pkg.go.dev/golang.org/x/exp/constraints](https://pkg.go.dev/golang.org/x/exp/constraints) | Các ràng buộc cốt lõi được xác định trước |
| slices package | Chính thức | [pkg.go.dev/slices](https://pkg.go.dev/slices) | Generic slice hoạt động |

---

## 6. KHUYẾN NGHỊ

Cốt lõi của ** Generics — Tham số loại, ràng buộc, Generic Mẫu** rất rõ ràng. Các nhánh bên dưới cầu loại trừu tượng hóa an toàn vào sản xuất mà không trượt vào kỹ thuật quá mức.

| Gia hạn | Khi nào nên đọc tiếp | Cơ sở lý luận | Tệp/Liên kết |
| ------- | ------- | ----- | --------- |
| lo thư viện | Khi bạn cần Lodash cho Go | Map , Lọc, Giảm, GroupBy — tất cả generic | [github.com/samber/lo](https://github.com/samber/lo) |
| mẫu Iterator | Khi làm việc với Go 1.23+ | `iter.Seq[T]` — đánh giá lười biếng, các luồng có thể tổng hợp | [go.dev/blog/range-functions](https://go.dev/blog/range-functions) |
| Generic bộ sưu tập | Khi tiêu chuẩn slices / maps không còn | Hàng đợi, bộ và cây an toàn loại | [github.com/emirpasber/gods](https://github.com/emirpasber/gods) |
| Type Assertion | Khi bạn cần kiểm tra kiểu runtime | `x.(T)` , loại công tắc và nil interface bẫy | [03-type-assertion-embedding.md](./03-type-assertion-embedding.md) |

---

**Điều hướng tuần tự**: [← Slices/Maps](./01-slices-maps-strings.md) · [→ Type Assertion & Embedding](./03-type-assertion-embedding.md)