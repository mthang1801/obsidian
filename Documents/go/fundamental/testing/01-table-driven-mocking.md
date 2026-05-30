<!-- tags: golang, testing --> # 🧪 Kiểm tra — Điều khiển theo bảng, Benchmarks , Mocking > Go 's `testing` package được tích hợp vào ngôn ngữ. Các thử nghiệm dựa trên bảng xử lý các ma trận đầu vào, `testify` cung cấp các xác nhận và `testify/mock` thay thế các phần phụ thuộc bằng các giả mạo được kiểm soát.

📅 Đã tạo: 2026-03-20 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 15 phút đọc

| Khía cạnh | Chi tiết |
| --------------- | --------------------------------------------- |
| **Công cụ** | Tích hợp `testing` package — không cần khung bên ngoài |
| **Trường hợp sử dụng** | Kiểm tra đơn vị, benchmarks , phạm vi bảo hiểm, phát hiện chủng tộc |
| **Thông tin chi tiết quan trọng** | Kiểm tra dựa trên bảng mở rộng phạm vi đầu vào mà không cần sao chép mã |
| **CLI** | `go test` , `go test -bench` , `go test -cover` |

---

## 1. ĐỊNH NGHĨA

Bạn viết `TestDivide_Normal` , `TestDivide_ByZero` , `TestDivide_NegativeResult` , `TestDivide_LargeNumbers` . Bốn chức năng, cấu trúc giống hệt nhau, chỉ khác nhau ở đầu vào. Vỏ cạnh mới có nghĩa là một chức năng mới. Lỗi trong mẫu khẳng định? Sửa bốn chỗ. Kéo yêu cầu xem xét? Đọc bốn khối gần giống nhau.

> * Table-driven testing loại bỏ sự trùng lặp này. Bạn xác định một `[]struct{ name, input, expected }` slice - một hàng cho mỗi trường hợp thử nghiệm. Vòng lặp gọi `t.Run(tt.name, ...)` cho mỗi hàng. Thêm một trường hợp có nghĩa là thêm một chữ struct . Logic xác nhận tồn tại chính xác một lần. Các nhóm kết quả đầu ra thử nghiệm theo tên: `TestDivide/normal` , `TestDivide/by_zero` — có thể đọc được, có thể lọc được bằng `-run` .*
>
> *Nhưng các bài kiểm tra dựa trên bảng chỉ xác minh mã bạn kiểm soát. Khi chức năng của bạn phụ thuộc vào database , ứng dụng khách HTTP hoặc nhà môi giới tin nhắn, bạn cần thay thế sự phụ thuộc đó bằng một giả mạo được kiểm soát. Go giải quyết vấn đề này bằng interfaces : xác định sự phụ thuộc là interface , thêm mock vào các thử nghiệm. `testify/mock` tự động hóa việc thiết lập và xác minh kỳ vọng.*

### Các loại thử nghiệm Go cung cấp bốn mẫu chức năng kiểm tra. Mỗi tệp tồn tại trong các tệp `_test.go` và bị loại trừ khỏi các tệp nhị phân sản xuất:

| Loại | Hậu tố tệp | Tiền tố hàm | Mục đích |
| ------------- | ----------- | --------------- | ----------------------------------- |
| **Kiểm tra đơn vị** | `_test.go` | `TestXxx` | Xác minh tính đúng đắn của một đơn vị |
| ** Benchmark ** | `_test.go` | `BenchmarkXxx` | Đo hiệu suất (ns/op, B/op) |
| **Ví dụ** | `_test.go` | `ExampleXxx` | Tài liệu thực thi |
| **Lông tơ** | `_test.go` | `FuzzXxx` | Tìm các trường hợp cạnh thông qua đầu vào ngẫu nhiên ( Go 1.18+) |

> **Tại sao `_test.go` ?** Trình biên dịch Go loại trừ tất cả các tệp `_test.go` khỏi các tệp nhị phân sản xuất. Trình trợ giúp kiểm tra, mock structs và dữ liệu kiểm tra không bao giờ được gửi đến sản xuất - không có chi phí, không cần thẻ xây dựng.

### Lệnh kiểm tra

| Lệnh | Mục đích |
| ----------------------------- | ------------------------------------ |
| `go test ./...` | Chạy tất cả các bài kiểm tra trong tất cả packages |
| `go test -v` | Đầu ra dài dòng với tên bài kiểm tra |
| `go test -run TestName` | Chạy thử nghiệm cụ thể theo tên |
| `go test -cover` | Hiển thị tỷ lệ phủ sóng |
| `go test -coverprofile=c.out` | Ghi dữ liệu bảo hiểm vào tập tin |
| `go test -bench .` | Chạy benchmarks |
| `go test -race` | Kích hoạt tính năng phát hiện cuộc đua |
| `go test -count=1` | Tắt kiểm tra caching |

> **Tại sao `-race` ?** Truy cập bộ nhớ của thiết bị phát hiện cuộc đua tại runtime . Nó nắm bắt các cuộc chạy đua dữ liệu mà các bài kiểm tra đơn vị bỏ lỡ - goroutines đọc và ghi cùng một biến mà không đồng bộ hóa. Chạy `-race` trong CI cho mọi PR.

---

## 2. HÌNH ẢNH

Khoảng cách giữa "kiểm tra vượt qua" và "kiểm tra bắt lỗi" là ma trận đầu vào. Table-driven testing buộc bạn phải nghĩ về các trường hợp đặc biệt dưới dạng dữ liệu chứ không phải dưới dạng mã. Quy trình làm việc bên dưới cho thấy cách một hàm kiểm tra duy nhất xử lý tất cả các trường hợp thông qua một vòng lặp.

![Table driven mocking workflow](./images/01-table-driven-mocking-workflow.png) *Hình: quy trình làm việc Table-driven test . Các trường hợp đầu vào được xác định là struct slices . Một vòng lặp duy nhất lặp lại các trường hợp, gọi `t.Run` cho các thử nghiệm phụ được đặt tên và xác nhận kết quả. Thêm trường hợp có nghĩa là thêm một hàng — không có chức năng mới.*

## 3. MÃ

Với **Kiểm tra — Dựa trên bảng, Benchmarks , Mocking **, các loại và lệnh kiểm tra được thiết lập. Bây giờ, chúng tôi neo chúng trong mã: các thử nghiệm dựa trên bảng cho ma trận đầu vào, interface mocking để cách ly phần phụ thuộc và benchmarks để đo lường hiệu suất.

### Ví dụ 1: Cơ bản — Kiểm thử theo bảng

Hàm `Add` của bạn lấy hai số nguyên và trả về tổng của chúng. Hàm `Divide` của bạn nhận hai số float và trả về kết quả hoặc lỗi. Cả hai đều cần nhiều trường hợp thử nghiệm - trường hợp dương, âm, 0, cạnh.

> **Mục tiêu**: Kiểm tra `Add` và `Divide` với nhiều đầu vào bằng cách sử dụng một chức năng kiểm tra duy nhất cho mỗi mục tiêu.
> **Phương pháp tiếp cận**: Xác định các trường hợp thử nghiệm dưới dạng `[]struct` slice . Lặp lại với `t.Run` cho các thử nghiệm phụ được đặt tên.
> **Ví dụ**: `TestDivide` xử lý phép chia thông thường, kết quả thập phân và phép chia cho 0 trong một hàm.```go
// math.go
package math

func Add(a, b int) int { return a + b }

func Divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}
```

```go
// math_test.go
package math

import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

// ✅ Table-driven test (idiomatic Go)
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive", 2, 3, 5},
        {"negative", -1, -2, -3},
        {"zero", 0, 0, 0},
        {"mixed", -5, 10, 5},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := Add(tt.a, tt.b)
            assert.Equal(t, tt.expected, result)
        })
    }
}

// ✅ Test with error cases
func TestDivide(t *testing.T) {
    tests := []struct {
        name      string
        a, b      float64
        expected  float64
        wantErr   bool
    }{
        {"normal", 10, 2, 5, false},
        {"decimal", 7, 3, 2.333, false},
        {"by zero", 10, 0, 0, true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result, err := Divide(tt.a, tt.b)
            if tt.wantErr {
                require.Error(t, err)  // ✅ require = stop test if fail
                return
            }
            require.NoError(t, err)
            assert.InDelta(t, tt.expected, result, 0.01)  // Float comparison
        })
    }
}
```> **Tại sao `require` cho lỗi và `assert` cho các giá trị?**
> `require.Error` dừng kiểm tra ngay lập tức nếu lỗi là nil — không ích gì khi kiểm tra kết quả của một thao tác thất bại. `assert.Equal` báo cáo lỗi nhưng vẫn tiếp tục kiểm tra, điều này rất hữu ích khi bạn muốn xem tất cả các xác nhận không thành công cùng một lúc. Quy tắc: `require` cho các điều kiện tiên quyết, `assert` để kiểm tra giá trị.
>
> **Kết luận**: Kiểm tra dựa trên bảng tách biệt dữ liệu kiểm tra khỏi logic kiểm tra. Việc thêm trường hợp cạnh mới là một chữ struct - không có hàm mới, không có mã xác nhận được sao chép. Mẫu `wantErr` xử lý cả đường dẫn thành công và lỗi trong cùng một bảng.

Kiểm thử dựa trên bảng bao gồm các hàm thuần túy. Nhưng khi hàm của bạn gọi database , bạn cần thay thế phần phụ thuộc đó bằng một phần giả mạo được kiểm soát. Điều đó đòi hỏi interfaces .

---

### Ví dụ 2: Trung cấp — Mocking với Interfaces `UserService.GetUser` của bạn xác thực ID, sau đó gọi `repo.FindByID` . Quá trình kiểm tra phải xác minh ba đường dẫn: thành công, không tìm thấy và ID không hợp lệ. Bài kiểm tra không được chạm vào database thực.

> **Mục tiêu**: Kiểm tra một phương thức dịch vụ có ba đường dẫn (thành công, không tìm thấy, đầu vào không hợp lệ) bằng cách sử dụng kho lưu trữ mock .
> **Cách tiếp cận**: Xác định `UserRepository` dưới dạng interface . Tạo `MockUserRepo` bằng cách sử dụng `testify/mock` . Định cấu hình kỳ vọng với `.On().Return()` .
> **Ví dụ**: Kiểm tra "id không hợp lệ" vượt qua `nil` làm kho lưu trữ — dịch vụ từ chối đầu vào trước khi gọi repo.```go
// service.go
package user

type UserRepository interface {
    FindByID(id int64) (*User, error)
    Create(user *User) error
}

type UserService struct {
    repo UserRepository
}

func NewUserService(repo UserRepository) *UserService {
    return &UserService{repo: repo}
}

func (s *UserService) GetUser(id int64) (*User, error) {
    if id <= 0 {
        return nil, errors.New("invalid id")
    }
    return s.repo.FindByID(id)
}
```

```go
// service_test.go
package user

import (
    "errors"
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
)

// ✅ Mock implementation
type MockUserRepo struct {
    mock.Mock
}

func (m *MockUserRepo) FindByID(id int64) (*User, error) {
    args := m.Called(id)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*User), args.Error(1)
}

func (m *MockUserRepo) Create(user *User) error {
    args := m.Called(user)
    return args.Error(0)
}

func TestGetUser(t *testing.T) {
    t.Run("success", func(t *testing.T) {
        mockRepo := new(MockUserRepo)
        expected := &User{ID: 1, Email: "alice@test.com"}
        mockRepo.On("FindByID", int64(1)).Return(expected, nil)

        svc := NewUserService(mockRepo)
        user, err := svc.GetUser(1)

        assert.NoError(t, err)
        assert.Equal(t, expected, user)
        mockRepo.AssertExpectations(t)
    })

    t.Run("not found", func(t *testing.T) {
        mockRepo := new(MockUserRepo)
        mockRepo.On("FindByID", int64(999)).Return(nil, errors.New("not found"))

        svc := NewUserService(mockRepo)
        user, err := svc.GetUser(999)

        assert.Error(t, err)
        assert.Nil(t, user)
    })

    t.Run("invalid id", func(t *testing.T) {
        svc := NewUserService(nil)  // No repo needed
        _, err := svc.GetUser(-1)
        assert.EqualError(t, err, "invalid id")
    })
}
```> **Tại sao `mockRepo.AssertExpectations(t)` ?**
> `AssertExpectations` xác minh rằng mọi kỳ vọng `.On(...)` thực sự đã được gọi. Nếu không có nó, bạn có thể xóa lệnh gọi `repo.FindByID(id)` khỏi dịch vụ — thử nghiệm vẫn sẽ vượt qua vì không có xác nhận nào kiểm tra xem repo đã được gọi hay chưa. `AssertExpectations` bắt cuộc gọi nhỡ.
>
> **Kết luận**: Interface mocking tách các thử nghiệm khỏi cơ sở hạ tầng. mock kiểm soát chính xác những gì kho lưu trữ trả về. `AssertExpectations` đảm bảo dịch vụ thực sự gọi kho lưu trữ. Kiểm tra "id không hợp lệ" chứng minh xác thực sớm bằng cách chuyển `nil` — không cần mock để từ chối đầu vào.

Kiểm tra đơn vị và [[E24]]] bao gồm tính chính xác. Benchmarks đo lường hiệu suất: nano giây trên mỗi thao tác, số byte được phân bổ, số phân bổ trên mỗi cuộc gọi.

---

### Ví dụ 3: Nâng cao — Benchmarks & Bảo hiểm

Hàm `Add` của bạn chạy trong vài nano giây. Nối chuỗi của bạn có hai cách triển khai - toán tử `+` và `strings.Builder` . Bạn muốn biết cái nào nhanh hơn và liệu nó có phân bổ bộ nhớ hay không.

> **Mục tiêu**: Benchmark `Add` và so sánh hai chiến lược nối chuỗi với theo dõi phân bổ.
> **Cách tiếp cận**: `BenchmarkXxx(b *testing.B)` với `b.Loop()` ( Go 1.24+) hoặc `for range b.N` ( Go 1.22+). Sub- benchmarks để so sánh tham số.
> **Ví dụ**: `BenchmarkStringConcat` so sánh `+` với `strings.Builder` . `-benchmem` tiết lộ sự khác biệt về phân bổ.```go
// benchmark_test.go
package math

import "testing"

func BenchmarkAdd(b *testing.B) {
    for i := range b.N { // Go 1.22+
        Add(42, 58)
    }
}

// ✅ Benchmark with setup
func BenchmarkDivide(b *testing.B) {
    b.ReportAllocs()  // Report memory allocations
    for i := range b.N { // Go 1.22+
        Divide(100, 3)
    }
}

// ✅ Sub-benchmarks
func BenchmarkStringConcat(b *testing.B) {
    b.Run("plus", func(b *testing.B) {
        s := ""
        for i := range b.N { // Go 1.22+
            s += "a"
        }
    })
    b.Run("builder", func(b *testing.B) {
        var sb strings.Builder
        for i := range b.N { // Go 1.22+
            sb.WriteString("a")
        }
    })
}
```

```bash
# ✅ Run benchmarks
go test -bench . -benchmem
# BenchmarkAdd-8           1000000000  0.29 ns/op  0 B/op  0 allocs/op
# BenchmarkDivide-8        500000000   2.31 ns/op  0 B/op  0 allocs/op

# ✅ Coverage
go test -cover ./...
# ok  myapp/math  0.3s  coverage: 95.2% of statements

go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out  # Open browser

# ✅ Race detection
go test -race ./...
```> **Tại sao `-benchmem` ?**
> `ns/op` đo time nhưng ẩn áp lực bộ nhớ. Một hàm chạy trong 10ns nhưng phân bổ 3 lần cho mỗi lệnh gọi sẽ tạo ra áp lực GC trên quy mô lớn. `-benchmem` báo cáo `B/op` (byte trên mỗi thao tác) và `allocs/op` — cần thiết để xác định phân bổ đường dẫn nóng.
>
> **Kết luận**: Benchmarks đo lường những gì bài kiểm tra đơn vị không thể: time , bộ nhớ và chi phí phân bổ. Sub- benchmarks so sánh các chiến lược cạnh nhau. `-benchmem` tiết lộ phân bổ ẩn. `-race` nắm bắt các cuộc đua dữ liệu mà không có xác nhận nào có thể phát hiện được.

---

## 4. Cạm bẫy

Cú pháp kiểm tra Go là tối thiểu. Các lỗi ẩn trong thiết kế thử nghiệm - xác minh caching , song song và mock .

| # | Mức độ nghiêm trọng | Lỗi | Hậu quả | Sửa chữa |
|---|--------------|--------------------------------------|------------------------------------------|---------------------------------------------------|
| 1 | 🔴 Gây tử vong | Không gọi `AssertExpectations` | Mock kỳ vọng âm thầm bị bỏ qua | Luôn gọi `mockRepo.AssertExpectations(t)` |
| 2 | 🟡 Chung | Kết quả kiểm tra được lưu trong bộ nhớ đệm | `go test` bỏ qua việc chạy lại nếu mã không thay đổi | Sử dụng `go test -count=1` để tắt bộ đệm |
| 3 | 🟡 Chung | Quên `-race` trong CI | Cuộc đua dữ liệu vượt qua CI và gặp sự cố trong quá trình sản xuất | Thêm `-race` vào lệnh kiểm tra CI |
| 4 | 🟡 Chung | `assert` thay vì `require` cho các điều kiện tiên quyết | Quá trình kiểm tra tiếp tục với `nil` pointer sau lỗi → panic | Sử dụng `require` để kiểm tra lỗi/ nil |
| 5 | 🔵 Nhỏ | Không sử dụng `t.Parallel()` | Kiểm tra tuần tự chất thải CI time | Đánh dấu các bài kiểm tra độc lập bằng `t.Parallel()` |

---

## 5. GIỚI THIỆU

| Tài nguyên | Loại | Liên kết | Ghi chú |
| ------------------ | -------- | ----------------------------------------------------------------------------------- | ---------------------------------- |
| Go Kiểm tra | Chính thức | [pkg.go.dev/testing](https://pkg.go.dev/testing) | Tài liệu tham khảo API thử nghiệm tích hợp |
| Kiểm tra dựa trên bảng | Chính thức | [go.dev/wiki/TableDrivenTests](https://go.dev/wiki/TableDrivenTests) | Mẫu table-driven test chuẩn |

---

## 6. KHUYẾN NGHỊ

Các thử nghiệm dựa trên bảng, mocking , benchmarks và phạm vi bao phủ đều được đề cập. Các nhánh bên dưới mở rộng thử nghiệm sang hồ sơ hiệu suất và các phần phụ thuộc thực sự.

| Mở rộng | Khi nào | Cơ sở lý luận | Tệp/Liên kết |
| -------------- | ------------------------------------- | -------------------------------------------- | -------------------------------------- |
| Benchmarks & Lông tơ | Khi bạn cần đo lường hiệu suất và khám phá trường hợp cụ thể | `b.Loop()` ( Go 1.24+), fuzzing , `benchstat` | [02-benchmark-fuzz.md](./02-benchmark-fuzz.md) |
| Kiểm tra tích hợp | Khi mocks vẫn chưa đủ - hãy kiểm tra DB thực, Redis, Kafka | `testcontainers-go` quay các vùng chứa Docker cho mỗi lần kiểm tra | [03-integration-testcontainers.md](./03-integration-testcontainers.md) |

**Điều hướng**: [← Packages](../packages/) · [← README](../README.md)