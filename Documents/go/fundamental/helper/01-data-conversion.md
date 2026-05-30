<!-- tags: golang, conversion, bytes, encoding --> # 🔄 Chuyển đổi dữ liệu - Chuỗi, Byte, Base64, Hex, JSON

> Go tách biệt `string` bất biến khỏi `[]byte` có thể thay đổi. Mọi tải trọng mạng, hàm băm mật mã và nội dung JSON đều bắt đầu dưới dạng byte. Bỏ qua chuyển đổi rõ ràng gây ra hỏng dữ liệu thầm lặng.

📅 Đã tạo: 23-03-2026 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 15 phút đọc

## 1. ĐỊNH NGHĨA

Trình xử lý webhook của bạn nhận được HMAC signature dưới dạng chuỗi hex trong tiêu đề `X-Hub-Signature` . Phần phụ trợ của bạn tính toán thông báo và nhận được `[]byte` thô. Bạn so sánh chúng với `==` - việc kiểm tra đều thất bại time . Chuỗi hex `"a1b2c3"` và byte slice `[]byte{0xa1, 0xb2, 0xc3}` trông có vẻ liên quan nhưng chúng chiếm các bố cục bộ nhớ khác nhau. Bạn cần `hex.EncodeToString` để đưa chúng vào cùng một biểu diễn trước khi so sánh.

Các nhà phát triển JavaScript mong đợi sự ép buộc ngầm giữa chuỗi và dữ liệu nhị phân. Go từ chối. `string(bytes)` và `[]byte(str)` tạo các bản sao rõ ràng - chuỗi không thay đổi, byte slice vẫn có thể thay đổi. Việc trộn lẫn chúng sẽ làm hỏng các so sánh mật mã và rò rỉ bộ nhớ trong các tình huống phát trực tuyến.

### 1.1 Các kiểu bất biến và lỗi

| Ranh giới | Trách nhiệm cốt lõi |
| --- | --- |
| ** `[]byte` ** | Phổ quát format . Bộ mã hóa mật mã, I/O và JSON chỉ sử dụng byte slices . |
| **Mã hóa** | Base64 và hex là các trình bao bọc vận chuyển - chúng chuyển đổi byte slices thành các chuỗi có thể in được để truyền mạng. |

| Quy tắc | Cơ sở lý luận |
| --- | --- |
| **Bản sao rõ ràng** | `string(buf)` cấp phát một chuỗi mới. Việc thay đổi `buf` sau khi truyền không ảnh hưởng đến chuỗi. |
| **Quy trình đọc** | Tránh `io.ReadAll` trên đầu vào không đáng tin cậy. Truyền tải trọng lớn qua `json.NewDecoder` để giới hạn mức sử dụng bộ nhớ. |

### 1.2 Chuỗi thất bại

- **Sai lệch Base64:** Bạn giải mã tải trọng JWT bằng `base64.StdEncoding` thay vì `base64.URLEncoding` . Base64 tiêu chuẩn sử dụng `+` và `/` ; Base64 an toàn cho URL sử dụng `-` và `_` . Bộ giải mã âm thầm tạo ra các byte sai.
- **Bộ giải mã OOM:** Một khách hàng tải lên nội dung JSON 2 GB. Bạn gọi `io.ReadAll(request.Body)` và tải toàn bộ tải trọng vào bộ nhớ. Nhóm Kubernetes đạt đến giới hạn bộ nhớ và bị hủy.

## 2. HÌNH ẢNH

Bối cảnh chuyển đổi có một trung tâm trung tâm: `[]byte` . Mọi format — chuỗi, Base64, hex, JSON — chuyển đổi thành và từ byte. Hình ảnh neo giữ hệ thống phân cấp này. ![Data Conversion Map](./images/01-data-conversion-api-map.png) *Hình: `[]byte` nằm ở trung tâm. Các chuỗi, Base64, hex và JSON đều chuyển đổi thông qua byte slices . Tải trọng mạng đến dưới dạng byte; định dạng hiển thị để lại dưới dạng chuỗi.*

## 3. MÃ

Với hệ thống phân cấp chuyển đổi được thiết lập, mã bên dưới thể hiện bốn mẫu tăng dần: chuyển đổi chuỗi/byte cơ bản, xác minh hex signature , giải mã JSON trực tuyến và tập hợp nhiều phần.

### Ví dụ 1: Cơ bản — Chuyển đổi chuỗi và byte

> **Mục tiêu**: Chuyển đổi giữa `string` và `[]byte` cho tải trọng mạng và mật mã.
> **Phương pháp tiếp cận**: Sử dụng các phôi `[]byte()` gốc và `encoding/base64` để mã hóa truyền tải.
> **Độ phức tạp**: O(N) — mỗi chuyển đổi sẽ sao chép toàn bộ bộ đệm.```go
// basic_coercion.go
package helper

import (
	"encoding/base64"
	"fmt"
)

func ExecuteConversions(payload string) error {
	// ✅ string → []byte creates a mutable copy
	buffer := []byte(payload)
	
	// ✅ []byte → string creates an immutable copy
	reverted := string(buffer)

	standardEncoded := base64.StdEncoding.EncodeToString(buffer)
	urlEncoded := base64.URLEncoding.EncodeToString(buffer)
	
	fmt.Printf("Reverted: %s | Std: %s | URL: %s\n", reverted, standardEncoded, urlEncoded)
	return nil
}
```> **Takeaway**: `string(buf)` và `[]byte(str)` là những bản sao rõ ràng. Việc thay đổi byte slice sau khi chuyển đổi không ảnh hưởng đến chuỗi. Sử dụng `URLEncoding` cho mã thông báo JWT và tham số URL; sử dụng `StdEncoding` cho mọi thứ khác.

---

### Ví dụ 2: Trung cấp — Xác minh Hex signature > **Mục tiêu**: So sánh thông báo HMAC thô với tiêu đề signature được mã hóa hex.
> **Phương pháp tiếp cận**: Mã hóa thông báo thô bằng `hex.EncodeToString` và so sánh các chuỗi.
> **Độ phức tạp**: O(N) — một lần mã hóa, một lần so sánh.```go
// crypto_mapping.go
package helper

import (
	"encoding/hex"
	"fmt"
)

func VerifyHexadecimalSignatures(rawHash []byte, providedSignature string) error {
	// ✅ Encode the raw bytes to a hex string for comparison
	generatedHex := hex.EncodeToString(rawHash)

	if generatedHex != providedSignature {
		return fmt.Errorf("signature mismatch: expected %s, got %s", generatedHex, providedSignature)
	}
	return nil
}
```> **Takeaway**: Không bao giờ so sánh trực tiếp byte thô với chuỗi hex. `hex.EncodeToString` chuyển đổi `[]byte{0xa1}` thành `"a1"` — cả hai bên phải có cùng cách biểu diễn.

---

### Ví dụ 3: Nâng cao — Giải mã JSON trực tuyến

> **Mục tiêu**: Giải mã nội dung yêu cầu JSON lớn mà không tải toàn bộ tải trọng vào bộ nhớ.
> **Phương pháp tiếp cận**: Sử dụng `json.NewDecoder(reader)` để phân tích cú pháp trực tiếp từ `io.ReadCloser` .
> **Độ phức tạp**: O(1) chi phí bộ nhớ — bộ giải mã đọc mã thông báo theo mã thông báo.```go
// streaming_json.go
package helper

import (
	"encoding/json"
	"net/http"
)

type VerificationPayload struct {
	EntityIdentifier string `json:"entity_identifier"`
	Action           string `json:"action"`
}

func StreamIncomingPayload(request *http.Request) (VerificationPayload, error) {
	defer request.Body.Close()

	var payload VerificationPayload
	// ✅ Stream-parse: reads from the body without buffering the entire content
	decoder := json.NewDecoder(request.Body)
	decoder.DisallowUnknownFields()
	
	if err := decoder.Decode(&payload); err != nil {
		return VerificationPayload{}, err
	}
	
	return payload, nil
}
```> **Takeaway**: `io.ReadAll` trên đầu vào không đáng tin cậy là một vectơ OOM. `json.NewDecoder` đọc phần thân HTTP dưới dạng luồng - bộ nhớ không đổi bất kể kích thước tải trọng.

---

### Ví dụ 4: Expert — Lắp ráp biểu mẫu nhiều phần

> **Mục tiêu**: Xây dựng nội dung nhiều phần HTTP chứa cả siêu dữ liệu JSON và tệp nhị phân.
> **Phương pháp tiếp cận**: Sử dụng `multipart.Writer` để ghi các trường và phần tệp vào bộ đệm dùng chung.
> **Độ phức tạp**: Logic đệm O(1) — ghi luồng trực tiếp.```go
// multipart_assembly.go
package helper

import (
	"bytes"
	"mime/multipart"
)

func BuildMultipartTransmission(metadata string, binary []byte) (*bytes.Buffer, string, error) {
	buffer := new(bytes.Buffer)
	writer := multipart.NewWriter(buffer)

	_ = writer.WriteField("diagnostic_metadata", metadata)

	if len(binary) > 0 {
		part, _ := writer.CreateFormFile("diagnostic_binary", "payload.bin")
		// ✅ Write binary data directly to the multipart stream
		part.Write(binary)
	}

	// Close writes the multipart termination boundary
	writer.Close()
	
	return buffer, writer.FormDataContentType(), nil
}
```> **Takeaway**: `multipart.Writer` tự động xử lý các điểm đánh dấu ranh giới. Gọi `Close()` trước khi đọc bộ đệm - nó ghi ranh giới cuối cùng.

## 4. Cạm bẫy

| # | Khiếm khuyết | Sửa chữa |
| --- | --- | --- |
| 1 | Sử dụng `StdEncoding` cho tải trọng URL/ JWT | Sử dụng `base64.URLEncoding` — mã hóa tiêu chuẩn chứa `+` và `/` phá vỡ các tham số URL |
| 2 | Gọi `io.ReadAll` trên các phần thân HTTP không đáng tin cậy | Sử dụng `json.NewDecoder` để phân tích cú pháp luồng; thêm `http.MaxBytesReader` làm bộ bảo vệ kích thước |
| 3 | So sánh byte thô với chuỗi hex/Base64 | Mã hóa cả hai bên thành cùng một format trước khi so sánh |
| 4 | Giả sử `string(buf)` chia sẻ bộ nhớ với `buf` | Nó tạo ra một bản sao. Đột biến `buf` sau khi truyền là an toàn nhưng phân bổ thêm bộ nhớ |

## 5. GIỚI THIỆU

| Tài nguyên | Liên kết |
| --- | --- |
| `encoding/base64` | [pkg.go.dev/encoding/base64](https://pkg.go.dev/encoding/base64) |
| `encoding/json` | [pkg.go.dev/encoding/json](https://pkg.go.dev/encoding/json) |

## 6. KHUYẾN NGHỊ

| Gia hạn | Khi nào | Cơ sở lý luận |
| --- | --- | --- |
| [Array Pipeline](./02-array-pipeline.md) | Khi xử lý bộ sưu tập các bản ghi được chuyển đổi | Generic `Map` , `Filter` , `Reduce` trên đã gõ slices |
| [Promise & Async](./04-promise-async.md) | Khi gọi đồng thời nhiều API bên ngoài | Các mẫu `errgroup` và channel cho I/O song song |

**Điều hướng**: [← Bridge Router](./README.md) · [→ Array Pipeline](./02-array-pipeline.md)