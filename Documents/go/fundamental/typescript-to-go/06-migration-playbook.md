<!-- tags: golang, typescript, migration --> # 🚚 Playbook di chuyển - Chuyển đổi dịch vụ từ TypeScript sang Go mà không tạo ra sự cố của riêng bạn.

> Cách di chuyển có chủ ý: chọn đúng strategy , giữ hợp đồng ổn định, đo đường cơ sở trước khi viết lại và đào tạo đội ngũ theo lộ trình 30/60/90 ngày.

📅 Đã tạo: 2026-04-06 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 18 phút đọc

| Khía cạnh | Chi tiết |
| --- | --- |
| **Tập trung** | Di chuyển strategy , triển khai theo hợp đồng đầu tiên, hỗ trợ nhóm |
| **Trường hợp sử dụng** | Viết lại dịch vụ, phân chia đường dẫn quan trọng, đưa Go vào tổ chức nặng về JS/TS |
| **Khác biệt về phím** | Di chuyển tốt là ranh giới + hoạt động + vấn đề học tập nhóm, không chỉ là dịch mã |
| ** Go stdlib** | `context` , `encoding/json` , `net/http` , `sync/atomic` |

## 1. ĐỊNH NGHĨA

Sự cám dỗ lớn nhất khi nhóm quyết định "viết lại trong Go " là bắt đầu từ một repo mới. Điều đó hầu như luôn mang lại cảm giác di chuyển rất nhanh trong 2 tuần đầu tiên, sau đó chững lại khi sự phức tạp của thế giới thực ập đến.

Tại sao? Bởi vì việc di chuyển không chỉ là về mã:

- Hệ thống hiện tại có các hợp đồng any hoàn toàn phụ thuộc vào khách hàng không?
- Bạn đã đo độ trễ, bộ nhớ, tỷ lệ lỗi cơ bản chưa?
- Team có đủ hiểu Go để giữ nguyên hành vi cũ mà không đưa ra lỗi mới không?
- Kế hoạch khôi phục ở đâu nếu phiên bản Go đi vào sản xuất và gặp sự cố?

Di chuyển tốt không bắt đầu bằng việc viết lại. Nó bắt đầu với những ranh giới rõ ràng, đo lường đầy đủ và triển khai phù hợp strategy .

Repo mới là phần dễ dàng.

Rollback là phần khó khăn.

### 1.1 3 chiến lược thực dụng nhất.

**Kẻ bóp cổ** 
Giữ dịch vụ TypeScript cũ, định tuyến dần một số điểm cuối/trường hợp sử dụng tới Go . Đây là mặc định an toàn nhất khi hệ thống có lưu lượng truy cập thực.

** Khai thác xe sidecar / công nhân ** 
Trước tiên hãy chia phần concurrency -heavy, CPU-heavy, batch-heavy hoặc infra-heavy thành Go . Thích hợp khi bạn không muốn chạm vào một hợp đồng API lớn.

**Viết lại đầy đủ** 
Chỉ hợp lý khi dịch vụ nhỏ, hợp đồng đơn giản, hoặc code cũ đã mục nát đến mức không thể cứu được nữa. Ngay cả khi viết lại toàn bộ, bạn vẫn nên thu gọn lại trước và đo đường cơ sở.

### 1.2 Lộ trình 30/60/90 ngày dành cho nhóm đầu tiên về TypeScript.

**Ngày 0-30** 
Khóa mô hình tinh thần, mô hình dữ liệu, lỗi/ concurrency /bối cảnh, chuỗi công cụ và viết 1-2 dịch vụ nhỏ không quan trọng.

**Ngày 31-60** 
Bắt đầu tách công nhân, sidecar, công cụ nội bộ hoặc người tiêu dùng một chiều thành Go . Thiết lập danh sách kiểm tra đánh giá riêng cho pointer /value/context/errors.

**Ngày 61-90** 
Chạm vào một đường dẫn quan trọng hơn: một tuyến API nhỏ, phân phát dịch vụ xuôi dòng lớn hoặc một công việc xử lý thông lượng cao. Chỉ làm điều này nếu bạn có kế hoạch cơ bản và khôi phục rõ ràng.

### 1.3 Các kiểu bất biến và lỗi

- Nếu không lưu hợp đồng kiểm tra thì viết lại sẽ “đúng theo mã mới” nhưng sai theo hành vi cũ mà khách hàng đang sử dụng.
- Nếu bạn không đo lường đường cơ sở trước, bạn sẽ không biết liệu việc viết lại có thực sự cải thiện được điều gì khác ngoài cảm giác hay không.
- Nếu nhóm không có kỷ luật xem xét đối với Go , lỗi pointer /context/ goroutine rò rỉ sẽ được đưa vào sản xuất rất nhanh.

## 2. HÌNH ẢNH

Di chuyển là một vấn đề triển khai nhiều giai đoạn, vì vậy nội dung trực quan tĩnh giúp bạn thấy chu trình xác thực và khoảng 30/60/90 rõ ràng hơn nhiều so với sơ đồ dưới dạng mã. ![Migration Playbook Rollout](./images/migration-playbook-rollout.png) *Hình: Bảng bên trên là vòng triển khai an toàn từ đường cơ sở đến mở rộng hoặc khôi phục; Bảng bên dưới là nhịp độ học tập và phạm vi can thiệp phù hợp cho nhóm ưu tiên TypeScript trong 30/60/90 ngày đầu tiên.*.

## 3. MÃ

Di chuyển tốt thường thắng trong thiết kế ranh giới hơn là thuật toán. Ba ví dụ dưới đây minh họa tinh thần đó.

### Ví dụ 1: Cơ bản — khóa hợp đồng với interface trước khi thay đổi cách triển khai.

> **Mục tiêu**: Tránh khiến việc triển khai strategy phụ thuộc trực tiếp vào ứng dụng khách cụ thể cũ.
> **Phương pháp**: Xác định interface tại thời điểm sử dụng, sau đó hoán đổi dần bộ chuyển đổi.
> **Ví dụ**: Dịch vụ đọc hóa đơn từ hệ thống TS cũ hôm nay, từ bộ chuyển đổi Go ​​ngày mai.

Phiên bản TypeScript dành cho nhiều nhóm có sẵn:```typescript
type Invoice = {
  id: string;
  amount: number;
};

interface InvoiceReader {
  findById(id: string): Promise<Invoice>;
}

class LegacyTsClient implements InvoiceReader {
  async findById(id: string): Promise<Invoice> {
    return { id, amount: 1500 };
  }
}

class BillingService {
  constructor(private readonly reader: InvoiceReader) {}

  async printInvoice(id: string): Promise<void> {
    const invoice = await this.reader.findById(id);
    console.log(`invoice=${invoice.id} amount=${invoice.amount}`);
  }
}
```Phiên bản Go tương ứng:```go
package main

import (
	"context"
	"fmt"
)

type Invoice struct {
	ID     string
	Amount int64
}

type InvoiceReader interface {
	FindByID(ctx context.Context, id string) (Invoice, error)
}

type LegacyTSClient struct{}

func (LegacyTSClient) FindByID(ctx context.Context, id string) (Invoice, error) {
	return Invoice{ID: id, Amount: 1500}, nil
}

type BillingService struct {
	reader InvoiceReader
}

func NewBillingService(reader InvoiceReader) BillingService {
	return BillingService{reader: reader}
}

func (s BillingService) PrintInvoice(ctx context.Context, id string) error {
	invoice, err := s.reader.FindByID(ctx, id)
	if err != nil {
		return fmt.Errorf("print invoice %s: %w", id, err)
	}
	fmt.Printf("invoice=%s amount=%d\n", invoice.ID, invoice.Amount)
	return nil
}

func main() {
	service := NewBillingService(LegacyTSClient{})
	_ = service.PrintInvoice(context.Background(), "inv-10")
}
```> **Bài học rút ra**: Quá trình di cư bền vững bắt đầu từ bước cuối cùng. Nếu bạn chưa có đường nối, việc viết lại sẽ rất khó để triển khai từng phần một.

Đường may có, nhưng đường may thôi chưa đủ. Nếu hợp đồng cũ vẫn tràn sang miền mới, bạn chỉ thay đổi ngôn ngữ chứ không gặp rủi ro.

### Ví dụ 2: Trung cấp - dịch DTO ở ranh giới thay vì để miền ôm lấy hợp đồng kế thừa.

> **Mục tiêu**: Cho phép dịch vụ Go giữ cho mô hình miền sạch sẽ trong khi vẫn giao tiếp với hình dạng JSON cũ.
> **Phương pháp tiếp cận**: Sở hữu DTO kế thừa, giữ một miền riêng và sử dụng các chức năng dịch rõ ràng.
> **Ví dụ**: Điểm cuối TS kế thừa trả về `customerId` và `totalCents` ; miền Go sử dụng `Order` .

Phiên bản TypeScript ở lớp bộ điều hợp:```typescript
type LegacyOrderDTO = {
  id: string;
  customerId: string;
  totalCents: number;
};

type Order = {
  id: string;
  customerId: string;
  total: number;
};

function translateLegacyOrder(dto: LegacyOrderDTO): Order {
  if (!dto.id || !dto.customerId || dto.totalCents <= 0) {
    throw new Error("legacy order contract invalid");
  }

  return {
    id: dto.id,
    customerId: dto.customerId,
    total: dto.totalCents,
  };
}
```Phiên bản Go tương ứng:```go
package main

import (
	"encoding/json"
	"fmt"
)

type legacyOrderDTO struct {
	ID         string `json:"id"`
	CustomerID string `json:"customerId"`
	TotalCents int64  `json:"totalCents"`
}

type Order struct {
	ID         string
	CustomerID string
	Total      int64
}

func translateLegacyOrder(raw []byte) (Order, error) {
	var dto legacyOrderDTO
	if err := json.Unmarshal(raw, &dto); err != nil {
		return Order{}, fmt.Errorf("decode legacy order: %w", err)
	}
	if dto.ID == "" || dto.CustomerID == "" || dto.TotalCents <= 0 {
		return Order{}, fmt.Errorf("legacy order contract invalid")
	}
	return Order{
		ID:         dto.ID,
		CustomerID: dto.CustomerID,
		Total:      dto.TotalCents,
	}, nil
}

func main() {
	raw := []byte(`{"id":"ord-9","customerId":"u-1","totalCents":4200}`)
	order, err := translateLegacyOrder(raw)
	if err != nil {
		panic(err)
	}
	fmt.Printf("%+v\n", order)
}
```> **Tại sao?** Các nhóm thường cố gắng giữ một mô hình chung cho các hợp đồng cũ, miền mới, cơ sở dữ liệu, sự kiện và phản hồi. Đó là cách nhanh nhất để rò rỉ logic di chuyển trên cơ sở mã. Dịch ranh giới có vẻ giống như một công việc làm thêm nhưng nó mang lại hiệu quả ngay lập tức.

> **Bài học rút ra**: Hình dạng kế thừa là mối quan tâm của lớp bộ điều hợp. Tên miền mới không nên mang cú pháp cũ lâu.

Biên dịch giữ nguyên hình dạng. Vấn đề còn lại là triển khai: giao thông đi đâu, quan sát thế nào, quay đầu ra sao.

### Ví dụ 3: Nâng cao — bộ định tuyến strangler có cờ tính năng và khôi phục đơn giản.

> **Mục tiêu**: Định tuyến lưu lượng truy cập dần dần đến trình xử lý Go trong khi vẫn giữ đường dẫn quay lại.
> **Phương pháp tiếp cận**: Sử dụng cờ nguyên tử để chọn giữa trình xử lý cũ và trình xử lý mới.
> **Ví dụ**: `/invoice` có thể chạy qua đường dẫn cũ hoặc Go .

Các phiên bản TypeScript/Node thường bắt đầu như thế này:```typescript
import express from "express";

const app = express();
let goPathEnabled = false;

function legacyHandler(_req: express.Request, res: express.Response) {
  res.status(200).send("legacy-ts-response");
}

function goHandler(_req: express.Request, res: express.Response) {
  res.status(200).send("new-go-response");
}

app.get("/invoice", (req, res) => {
  if (goPathEnabled) {
    return goHandler(req, res);
  }
  return legacyHandler(req, res);
});
```Phiên bản Go tương ứng:```go
package main

import (
	"fmt"
	"net/http"
	"sync/atomic"
)

var goPathEnabled atomic.Bool

func legacyHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write([]byte("legacy-ts-response"))
}

func goHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write([]byte("new-go-response"))
}

func stranglerHandler(w http.ResponseWriter, r *http.Request) {
	if goPathEnabled.Load() {
		goHandler(w, r)
		return
	}
	legacyHandler(w, r)
}

func main() {
	goPathEnabled.Store(false) // flip when canary passes

	http.HandleFunc("/invoice", stranglerHandler)
	fmt.Println("listening on :8080")
	_ = http.ListenAndServe(":8080", nil)
}
```> **Tại sao?** Mô hình strangler thành công khi việc khôi phục rẻ hơn so với triển khai. Nếu bạn phải triển khai lại hoặc khôi phục toàn bộ dịch vụ mỗi lần time xảy ra lỗi thì bạn chưa thực sự xây dựng được quá trình di chuyển an toàn.

> **Bài học rút ra**: Di chuyển quy mô nhỏ slices với tính năng khôi phục rẻ tiền hầu như luôn đánh bại việc viết lại mạnh mẽ.

## 4. Cạm bẫy

Ba lỗi dưới đây hiếm khi xuất hiện trong các slide khởi động.

Chúng xuất hiện muộn hơn, khi dòng thời gian bị khóa và quá trình sản xuất bắt đầu có tín hiệu xấu.

| # | Mức độ nghiêm trọng | Lỗi | Hậu quả | Sửa chữa |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Gây tử vong | Viết lại đột phá mà không cần đo đường cơ sở và không cần khôi phục | Bỏng dòng thời gian, khó xác minh giá trị, dễ xảy ra sự cố trong sản xuất | Chọn người siết cổ hoặc xe sidecar trước; Đo đường cơ sở về độ trễ/lỗi/chi phí ngay từ đầu |
| 2 | 🟡 Chung | Chuyển kiến ​​trúc NestJS/Express ban đầu vào Go | Viết lại xong nhưng sự phức tạp cũ vẫn còn nguyên | Thiết kế lại ranh giới theo package , nhỏ interface , hàm tạo rõ ràng |
| 3 | 🔵 Nhỏ | Huấn luyện nhóm bằng một tài liệu duy nhất và sau đó đi sâu vào con đường quan trọng | Chất lượng đánh giá yếu, lỗi ngữ nghĩa lọt qua | Thực hiện theo lộ trình 30/60/90 ngày và sử dụng danh sách kiểm tra đánh giá riêng cho Go |

## 5. GIỚI THIỆU

| Tài nguyên | Loại | Liên kết | Lưu ý |
| --- | --- | --- | --- |
| Cẩm nang TypeScript | Chính thức | https://www.typescriptlang.org/docs/handbook/intro.html | Đường cơ sở của mô hình nguồn runtime /type trước khi di chuyển |
| Go Hướng dẫn sử dụng | Chính thức | https://go.dev/doc/ | Đường cơ sở của chuỗi công cụ, modules , thử nghiệm và quy trình làm việc phía mục tiêu |
| Go cho Dịch vụ Mạng & Đám mây | Chính thức | https://go.dev/solutions/cloud | Cơ sở đánh giá các trường hợp sử dụng phù hợp cho việc khai thác dịch vụ/xe sidecar Go |

## 6. KHUYẾN NGHỊ

Cốt lõi của **Playbook di chuyển** rất rõ ràng. Các tiện ích mở rộng bên dưới giúp bạn thực hiện quá trình di chuyển strategy của mình bằng tập bản đồ dịch thuật và giới thiệu nhóm.

Nó có một chuỗi quyết định nhỏ, có thể đo lường được và quay trở lại.

| Gia hạn | Khi nào | Cơ sở lý luận | Liên kết |
| --- | --- | --- | --- |
| Mô hình tinh thần & Runtime | Khi nhóm vẫn xem Go là "TypeScript được biên dịch thành nhị phân" | Việc di chuyển chính xác strategy trước tiên cần có một mô hình tinh thần chính xác | [→ 01-mental-model-runtime](./01-mental-model-runtime.md) |
| Khi nào nên chọn Go so với TypeScript | Khi tranh luận về việc nên di chuyển hoàn toàn hay di chuyển từng bước trước | Khung quyết định trước khi cam kết lộ trình | [→ 05-when-to-choose](./05-when-to-choose-go-vs-typescript.md) |
| Bố cục dự án, Dụng cụ, Kiểm tra | Khi kế hoạch di chuyển đã rõ ràng nhưng việc tổ chức repo và vận chuyển vẫn chưa được quyết định | Di chuyển ngôn ngữ mà không thay đổi quy trình làm việc khiến việc triển khai kém bền hơn | [→ 04-project-layout-tooling](./04-project-layout-tooling-testing.md) |
| Các loại & mô hình hóa dữ liệu | Khi hợp đồng cũ bắt đầu trở nên phức tạp | Lớp dịch đúng yêu cầu mô hình dữ liệu chính xác | [→ 02-types-data-modeling](./02-types-data-modeling.md) |
| Lỗi, Concurrency , Ngữ cảnh | Khi slice đã di chuyển bắt đầu gọi nhiều luồng xuống | Lỗi di chuyển là phổ biến nhất trong kiểm soát vòng đời | [→ 03-errors-concurrency-context](./03-errors-concurrency-context.md) |
| Bản đồ dịch thuật | Khi nhóm đang di chuyển nhưng vẫn hỏi "Thành ngữ TS/Node này trong Go ?" | Tra cứu nhanh trong khi vẫn duy trì hướng thành ngữ | [→ 07-translation-atlas](./07-translation-atlas.md) |
| Người trợ giúp — TS/JS → Go Tiện ích | Khi nhóm cần cú pháp ánh xạ nhanh trong quá trình thực hiện di chuyển | Strategy xử lý cụm strategy ; người trợ giúp xử lý công thức nấu ăn | [→ Helper README](../helper/README.md) |

**Điều hướng**: [← Previous](./05-when-to-choose-go-vs-typescript.md) · [→ Next](./07-translation-atlas.md)