<!-- tags: golang --> # 📦 Ràng buộc & Xác thực - JSON, Biểu mẫu, Tải tệp lên

> **Thư viện**: Liên kết dữ liệu JSON/form/URI với cấu trúc Go và xác thực bằng thẻ `binding:` được hỗ trợ bởi `go-playground/validator` .

📅 Cập nhật: 2026-04-19 · ⏱️ 14 phút đọc

## 1. ĐỊNH NGHĨA

Các phương thức `ShouldBind*` của Gin giải mã dữ liệu yêu cầu thành một cấu trúc và chạy các quy tắc `go-playground/validator` từ các thẻ `binding:` - một dòng thay thế phân tích cú pháp thủ công.

| Phương pháp | Nguồn |
| ------------------------- | ---------------------------------- |
| `c.ShouldBindJSON(&obj)` | Nội dung yêu cầu JSON |
| `c.ShouldBindQuery(&obj)` | Tham số truy vấn URL ( `?page=2` ) |
| `c.ShouldBindUri(&obj)` | Tham số đường dẫn ( `:id` ) |

### Bất biến chính

- **Sử dụng `ShouldBind*` (không phải `Bind*` ) cho phản hồi lỗi tùy chỉnh.** `Bind*` tự động ghi 400.
- **Trường con trỏ + `omitempty` = Ngữ nghĩa PATCH.** Khác không có nghĩa là khách hàng đã gửi trường này.

## 2. HÌNH ẢNH ![Binding and validation pipeline — request sources → struct hydration → validator](./images/01-binding-validation-pipeline.png) *Hình: Đường dẫn liên kết Gin — dữ liệu yêu cầu thô từ nội dung JSON, chuỗi truy vấn hoặc đường dẫn URL chảy qua ShouldBind\* vào một cấu trúc đã nhập, sau đó go-playground/validator kiểm tra các thẻ liên kết. Đạt = cấu trúc sạch, Thất bại = 400 với lỗi cấp trường.*```mermaid
flowchart LR
    A["Raw Request"] -->|"ShouldBindJSON"| B["Struct Hydration"]
    B --> C{"Validator\nrules pass?"}
    C -->|Yes| D["Clean struct"]
    C -->|No| E["400 + field errors"]
```*Hình: Đường dẫn liên kết — yêu cầu thô → ShouldBindJSON → hydrat hóa cấu trúc → quy tắc xác thực → lỗi hoặc cấu trúc sạch.*```mermaid
flowchart TD
    A{"Where is\nthe data?"} -->|"Body (JSON)"| B["ShouldBindJSON"]
    A -->|"Query string"| C["ShouldBindQuery"]
    A -->|"URL path"| D["ShouldBindUri"]
    A -->|"Form POST"| E["ShouldBind"]
```*Hình: Cây quyết định — chọn ShouldBindJSON (nội dung), ShouldBindQuery (chuỗi truy vấn) hoặc ShouldBindUri (đường dẫn).*

### Luồng liên kết```text
POST /users  {"name":"Alice","email":"a@b.com","age":17}
    ├── ShouldBindJSON decodes into CreateUserRequest
    ├── Validator checks: age gte=18 → FAIL
    └── Handler returns 400 with validation details
```## 3. MÃ

### Ví dụ 1: Cơ bản — Ràng buộc thuộc tính JSON```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // CreateUserRequest: binding tags validate on decode.
    // UpdateUserRequest: pointer fields for PATCH (nil = not sent).
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package main

    import (
        "net/http"
        "github.com/gin-gonic/gin"
    )

    type CreateUserRequest struct {
        Name     string `json:"name"     binding:"required,min=2,max=50"`
        Email    string `json:"email"    binding:"required,email"`
        Password string `json:"password" binding:"required,min=8,max=72"`
        Age      int    `json:"age"      binding:"required,gte=18,lte=120"`
        Role     string `json:"role"     binding:"required,oneof=user admin"`
    }

    type UpdateUserRequest struct {
        Name  *string `json:"name"  binding:"omitempty,min=2,max=50"`
        Email *string `json:"email" binding:"omitempty,email"`
        Age   *int    `json:"age"   binding:"omitempty,gte=18,lte=120"`
    }

    type UserResponse struct {
        ID    int64  `json:"id"`
        Name  string `json:"name"`
        Email string `json:"email"`
        Role  string `json:"role"`
    }

    func createUser(c *gin.Context) {
        var req CreateUserRequest

        if err := c.ShouldBindJSON(&req); err != nil {
            c.JSON(http.StatusBadRequest, gin.H{
                "error":   "validation failed",
                "details": err.Error(),
            })
            return
        }

        c.JSON(http.StatusCreated, gin.H{
            "data": UserResponse{
                ID:    1,
                Name:  req.Name,
                Email: req.Email,
                Role:  req.Role,
            },
        })
    }
```### Ví dụ 2: Trung cấp — Nhắm mục tiêu truy vấn và URI```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // ShouldBindQuery: maps ?page=2&sort=name to struct.
    // ShouldBindUri: maps :id path param using uri: tags.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    type ListUsersQuery struct {
        Page    int    `form:"page"    binding:"omitempty,min=1"`
        Limit   int    `form:"limit"   binding:"omitempty,min=1,max=100"`
        Sort    string `form:"sort"    binding:"omitempty,oneof=name email"`
        Order   string `form:"order"   binding:"omitempty,oneof=asc desc"`
    }

    func listUsers(c *gin.Context) {
        query := ListUsersQuery{
            Page:  1,    
            Limit: 20,
            Sort:  "created_at",
            Order: "desc",
        }

        if err := c.ShouldBindQuery(&query); err != nil {
            c.JSON(400, gin.H{"error": err.Error()})
            return
        }

        c.JSON(200, gin.H{"query": query})
    }

    type UserURI struct {
        ID int64 `uri:"id" binding:"required,gt=0"`
    }

    func getUser(c *gin.Context) {
        var uri UserURI
        if err := c.ShouldBindUri(&uri); err != nil {
            c.JSON(400, gin.H{"error": "invalid user ID"})
            return
        }

        c.JSON(200, gin.H{"id": uri.ID})
    }
```---

## 4. Cạm bẫy

| # | Mức độ nghiêm trọng | Khiếm khuyết | Tác động | Sửa chữa |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Gây tử vong | Sử dụng `c.BindJSON` thay vì `c.ShouldBindJSON` | Tự động viết 400; không thể tùy chỉnh nội dung lỗi | Luôn sử dụng `ShouldBind*` và tự xử lý lỗi |
| 2 | 🔴 Gây tử vong | Chấp nhận `map[string]any` thô thay vì gõ struct | Không xác nhận, không an toàn về loại | Xác định cấu trúc yêu cầu bằng thẻ `binding:` |

---

## 5. GIỚI THIỆU

| Tài nguyên | Liên kết |
| --- | --- |
| Trình xác thực | [github.com/go-playground/validator](https://github.com/go-playground/validator) |
| Gin chính thức | [gin-gonic.com/en/docs](https://gin-gonic.com/en/docs/) |

---

## 6. KHUYẾN NGHỊ

| Gia hạn | Khi nào | Cơ sở lý luận | Tài nguyên |
| --- | --- | --- | --- |
| Tải lên tệp | Khi chấp nhận tải lên nhị phân (hình ảnh, tài liệu) | Phân tích cú pháp nhiều phần, giới hạn kích thước, xác thực loại nội dung | [./02-file-upload-multipart.md](./02-file-upload-multipart.md) |