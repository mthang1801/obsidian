<!-- tags: golang, interfaces --> # 💉 DI qua Interfaces & Mocking Mẫu

> Go bỏ qua các khung DI — interfaces + nội dung hàm tạo là đủ. Tạo mocks với mockgen/mockery.

📅 Đã tạo: 23-03-2026 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 12 phút đọc

| Khía cạnh | Chi tiết |
| --- | --- |
| **Khái niệm** | Nội dung xây dựng thông qua interfaces , được tạo mocks |
| **Trường hợp sử dụng** | Đơn vị kiểm tra logic nghiệp vụ không có cơ sở dữ liệu hoặc HTTP |
| **Thông tin chi tiết quan trọng** | Không có vùng chứa DI - hàm tạo rõ ràng, không có phép thuật |
| ** Go stdlib** | `testing` , `context` , `net/http` |

| TS/NestJS | Go |
| ----------------------------- | ----------------------------------------- |
| `@Injectable()` + `@Inject()` | Hàm tạo: `func NewService(repo Repo)` |
| `interface UserRepo {}` | `type UserRepo interface{}` |
| `jest.mock()` | `mockgen` / `mockery` |
| `useClass: MockRepo` | Truyền trực tiếp mock tới hàm tạo |

---

## 1. ĐỊNH NGHĨA

Trình xử lý của bạn gọi database , bộ đệm và API bên ngoài. Việc kiểm tra nó yêu cầu Postgres, Redis và máy chủ HTTP mock đang chạy. CI mất 5 phút mỗi lần chạy. Cách khắc phục: xác định interfaces cho từng phần phụ thuộc, đưa chúng vào thông qua hàm tạo và hoán đổi các triển khai thực tế cho mocks trong bộ nhớ trong quá trình kiểm tra.

> *Kiểm tra đơn vị cho `GetUser` đạt database . Mỗi bản ghi hạt giống thử nghiệm, chạy truy vấn và dọn dẹp. CI tạo ra các thùng chứa Postgres cho mọi bộ phần mềm. Chạy 200 bài kiểm tra mất 4 phút. Thay thế loại bê tông `UserRepository` bằng interface , thêm map được hỗ trợ mock và các thử nghiệm sẽ chạy trong micro giây.*
>
> *Đây là Dependency Injection trong Go : không khung, không trang trí, không phản chiếu. Xác định một interface ở người tiêu dùng, chấp nhận nó trong hàm tạo và chuyển phần triển khai thực sự trong `main()` và mock trong `_test.go` .*

### DI Nguyên tắc trong Go | Nguyên tắc | Mô tả | Tại sao |
| --- | --- | --- |
| **Do người tiêu dùng xác định interfaces ** | Người tiêu dùng (dịch vụ) xác định interface , không phải nhà sản xuất (repo) | Loại bỏ khớp nối nhập khẩu |
| **Tiêm hàm tạo** | Các phần phụ thuộc được truyền dưới dạng đối số của hàm tạo | Rõ ràng, có thể theo dõi trong IDE |
| **Nhỏ interfaces ** | 1–3 phương thức cho mỗi interface | Dễ mock , dễ soạn |
| **Không có khung DI ** | Không có thùng chứa, không có sự phản ánh | Biên dịch- time an toàn, không có ma thuật |

### Chế độ lỗi

| Khiếm khuyết | Nguyên nhân | Hậu quả | Sửa chữa |
| --- | ------------ | ------ | --- |
| Chất béo interfaces (hơn 10 phương pháp) | interface đơn cho tất cả các hoạt động repo | Mỗi mock phải triển khai hơn 10 phương thức | Chia theo trường hợp sử dụng (Trình đọc, Trình ghi, Trình xóa) |
| Phía nhà sản xuất interfaces | Interface được xác định bên cạnh phần triển khai | Người tiêu dùng buộc phải nhập khẩu nhà sản xuất package | Xác định interface tại người tiêu dùng |
| Phụ thuộc cụ thể | Trường Struct là `*PostgresRepo` không phải `UserRepo` | Không thể thay thế mocks | Sử dụng các loại interface trong các trường struct |

---

## 2. HÌNH ẢNH DI trong Go là ba bước: xác định interface → tiêm qua hàm tạo → trao đổi thực cho mock trong các thử nghiệm. Hình ảnh bên dưới maps luồng này. ![DI and mocking workflow](./images/02-di-mocking-patterns-workflow.png) *Hình: quy trình công việc DI — định nghĩa interface , nội dung hàm tạo và thay thế mock trong các thử nghiệm.*

## 3. MÃ

Ba cấp độ tiến triển: interface cơ bản + hàm tạo DI , thủ công mock và được tạo mock với sự nhạo báng.

### Ví dụ 1: Cơ bản — Interface + Hàm tạo DI Dịch vụ phụ thuộc vào `UserRepository` (một interface ), không phải `*PostgresUserRepo` (một loại cụ thể). Hàm tạo chấp nhận interface - quá trình sản xuất vượt qua repo thực, các thử nghiệm vượt qua mock .```go
// ✅ Define interface at consumer (UserService package)
type UserRepository interface {
	FindByID(ctx context.Context, id string) (*User, error)
	Create(ctx context.Context, user *User) error
	Delete(ctx context.Context, id string) error
}

// ✅ Service depends on interface, not concrete type
type UserService struct {
	repo UserRepository // interface field
}

// ✅ Constructor injection — explicit, no magic
func NewUserService(repo UserRepository) *UserService {
	return &UserService{repo: repo}
}

func (s *UserService) GetUser(ctx context.Context, id string) (*User, error) {
	return s.repo.FindByID(ctx, id)
}
```> **Takeaway**: Dịch vụ không bao giờ nhập kho lưu trữ package . Nó chỉ biết interface . Đây là cách Go đạt được DI mà không cần khung.

---

### Ví dụ 2: Trung cấp — Thủ công Mock Hướng dẫn sử dụng mock triển khai interface với bộ nhớ trong map . Không database ​​, không có mạng — các bài kiểm tra chạy trong vài phần triệu giây.```go
// ✅ Mock implementation — in-memory, no DB dependency
type MockUserRepo struct {
	users map[string]*User
}

func NewMockUserRepo() *MockUserRepo {
	return &MockUserRepo{users: make(map[string]*User)}
}

func (m *MockUserRepo) FindByID(_ context.Context, id string) (*User, error) {
	user, ok := m.users[id]
	if !ok {
		return nil, apperror.ErrNotFound
	}
	return user, nil
}

func (m *MockUserRepo) Create(_ context.Context, user *User) error {
	m.users[user.ID] = user
	return nil
}

func (m *MockUserRepo) Delete(_ context.Context, id string) error {
	delete(m.users, id)
	return nil
}

// ✅ Test — inject mock, no DB, microsecond execution
func TestGetUser(t *testing.T) {
	mockRepo := NewMockUserRepo()
	mockRepo.users["1"] = &User{ID: "1", Name: "Alice"}

service := NewUserService(mockRepo) // inject mock

user, err := service.GetUser(context.Background(), "1")
	assert.NoError(t, err)
	assert.Equal(t, "Alice", user.Name)
}
```> **Khi thủ công mocks ?** Khi bạn cần hành vi tùy chỉnh (lỗi mô phỏng, theo dõi cuộc gọi, trả về dữ liệu động). Hướng dẫn sử dụng mocks cung cấp toàn quyền kiểm soát.
>
> **Tại sao `_` cho `context.Context` ?** Các trường hợp thử nghiệm sử dụng `context.Background()` — không cần hết thời gian chờ hoặc hủy. Dấu gạch dưới báo hiệu rằng tham số này không được sử dụng có chủ ý.

> **Takeaway**: Thủ công mocks là tốt nhất cho interfaces nhỏ (phương pháp 1–3). Đối với interfaces lớn hơn, việc tạo mã sẽ tránh được bản soạn sẵn.

---

### Ví dụ 3: Nâng cao — Đã tạo Mock (nhạo báng) `mockery` tạo ra các triển khai mock từ các định nghĩa interface . Thiết lập kỳ vọng một cách khai báo và tự động xác minh cuộc gọi.```bash
# Install mockery
go install github.com/vektra/mockery/v2@latest

# Generate mock from interface
mockery --name=UserRepository --dir=./internal/domain --output=./internal/domain/mocks
```

```go
// Generated: internal/domain/mocks/UserRepository.go
// ✅ No manual mock code — all auto-generated

func TestGetUser_WithMockery(t *testing.T) {
	mockRepo := mocks.NewUserRepository(t)

// ✅ Setup expectations — declarative
	mockRepo.EXPECT().
		FindByID(mock.Anything, "1").
		Return(&User{ID: "1", Name: "Alice"}, nil)

service := NewUserService(mockRepo)
	user, err := service.GetUser(context.Background(), "1")

assert.NoError(t, err)
	assert.Equal(t, "Alice", user.Name)
	mockRepo.AssertExpectations(t) // ✅ Verify all expectations met
}
```> **Tại sao `mock.Anything` lại dành cho ngữ cảnh?** Giá trị ngữ cảnh khác nhau giữa các thử nghiệm. `mock.Anything` khớp với giá trị any , giữ kỳ vọng tập trung vào tham số kinh doanh ( `"1"` ).
>
> **Tại sao `AssertExpectations` ?** Không có nó, bài kiểm tra sẽ vượt qua ngay cả khi mock chưa bao giờ được gọi. `AssertExpectations` xác minh rằng mọi kỳ vọng được khai báo đều thực sự được viện dẫn.

> **Takeaway**: `mockery` loại bỏ bản soạn sẵn cho interfaces lớn. Kết hợp với `AssertExpectations` để ngăn chặn kết quả dương tính giả.

---

## 4. Cạm bẫy

Cơ chế của ** DI & Mocking ** rất rõ ràng. Những gì còn lại là nhận ra các mẫu gây ra độ tin cậy của bài kiểm tra sai.

| # | Mức độ nghiêm trọng | Khiếm khuyết | Hậu quả | Sửa chữa |
|---|----------|------|----------|------|
| 1 | 🔴 Gây tử vong | Thiếu `AssertExpectations` trên mocks | Kiểm thử đạt ngay cả khi các phương thức dự kiến ​​không bao giờ được gọi | Luôn gọi `mockRepo.AssertExpectations(t)` |
| 2 | 🟡 Chung | Chất béo interfaces (hơn 10 phương pháp) | Mọi mock phải triển khai tất cả các phương thức | Tách interfaces theo trường hợp sử dụng |
| 3 | 🟡 Chung | Interface được xác định tại nhà sản xuất, không phải người tiêu dùng | Người tiêu dùng nhập nhà sản xuất package | Xác định interface tại người tiêu dùng |
| 4 | 🟡 Chung | Các loại struct được mã hóa cứng trong hàm signatures | Không thể thay thế mocks | Chấp nhận interfaces , không phải loại cụ thể |
| 5 | 🔵 Nhỏ | mocks được thiết kế quá mức với logic phức tạp | Mock kiểm tra mock , không phải mã | Giữ mocks đơn giản: trả về các giá trị cố định |

### 🔴 Cạm bẫy số 1 — Thiếu xác minh khẳng định

Đã tạo mocks ghi lại các kỳ vọng nhưng không tự động thực thi chúng. Nếu không có `AssertExpectations(t)` , thử nghiệm sẽ vượt qua ngay cả khi phương thức mock không bao giờ được gọi — một kết quả dương tính giả che giấu các lỗi thực sự.

---

---

## 5. GIỚI THIỆU

| Tài nguyên | Loại | Liên kết | Mô tả |
| ----------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------- | ------- |
| chế nhạo | Công cụ | [github.com/vektra/mockery](https://github.com/vektra/mockery) | Tự động tạo mocks từ interfaces |
| Go Interface Các phương pháp hay nhất | Chính thức | [go.dev/wiki/CodeReviewComments#interfaces](https://github.com/golang/go/wiki/CodeReviewComments#interfaces) | Interface hướng dẫn đặt tên và thiết kế |
| google/dây | Công cụ | [github.com/google/wire](https://github.com/google/wire) | Biên dịch- time dependency injection |

---

## 6. KHUYẾN NGHỊ

Nền tảng của ** DI & Mocking ** đã được giải quyết. Các tiện ích mở rộng bên dưới kết nối các mẫu DI để kiểm tra quy trình làm việc và nối dây sản xuất.

| Gia hạn | Khi nào | Tại sao | Tệp/Liên kết |
| ------- | ------- | ----- | --------- |
| Ẩn Interfaces | Hiểu cơ học interface | Nền tảng cho các hợp đồng do người tiêu dùng xác định | [01-implicit-io-patterns.md](./01-implicit-io-patterns.md) |
| Kiểm tra theo hướng bảng | Cấu trúc các ca kiểm thử một cách có hệ thống | Kết hợp với DI mocks để có phạm vi phủ sóng toàn diện | [../../testing/01-table-driven-mocking.md](../testing/01-table-driven-mocking.md) |
| google/dây | Đồ thị phụ thuộc phức tạp | Biên dịch- tạo mã time DI cho các ứng dụng lớn | [github.com/google/wire](https://github.com/google/wire) |

---

**Điều hướng**: [← Implicit Interfaces](./01-implicit-io-patterns.md) · [→ Structs](../structs/01-composition-embedding.md)