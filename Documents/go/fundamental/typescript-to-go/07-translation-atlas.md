<!-- tags: golang, typescript, nodejs, migration --> # 🗺️ Bản đồ dịch thuật — Dịch thành ngữ Map từ TypeScript/Node.js sang Go .

> Một lối đi thực tế dành cho các lập trình viên phụ trợ TypeScript: thay vì dịch từng dòng, bài viết này maps từng "ý định" quen thuộc của TS/Node sang các nguyên hàm, packages và các quy trình làm việc đặc trưng trong Go .

📅 Đã tạo: 2026-04-06 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 15 phút đọc

| Khía cạnh | Chi tiết |
| --- | --- |
| **Tập trung** | Cú pháp qua đường, ánh xạ stdlib, runtime -bản dịch đầu tiên |
| **Trường hợp sử dụng** | Tuần đầu tiên chuyển các dịch vụ hoặc công cụ từ TypeScript/Node.js sang Go |
| **Khác biệt về phím** | TS/Node tập hợp nhiều khả năng xung quanh các đối tượng và hệ sinh thái runtime ; Go tách ý định thành packages |
| ** Go stdlib** | `os` , `io` , `bufio` , `encoding/json` , `net/http` , `flag` , `regexp` , `context` |

## 1. ĐỊNH NGHĨA

Bạn đang chuyển một phụ trợ tiện ích nhỏ từ TypeScript sang Go . Trong đầu bạn có một danh sách rất quen thuộc:

- `console.log` - `JSON.parse` - `fs.readFileSync` - `Promise.all` - `AbortController` - `class` , `constructor` , `this` - `process.argv` , `process.env` Vấn đề là khi bạn chuyển sang Go , bạn không tìm thấy "bản sao" của `process` , `fs` hoặc `Promise` . Mọi thứ dường như được chia thành nhiều nơi hơn: `fmt` , `os` , `bufio` , `encoding/json` , `net/http` , `context` , `flag` , `struct` , v.v.

Hướng dẫn từ `miguelmota/golang-for-nodejs-developers` rất hữu ích ngay tại đó: nó cung cấp cho bạn một tập bản đồ như "X trong Node.js là Y trong Go ". Nhưng nếu bạn đưa tập bản đồ đó vào Go hiện đại mà không điều chỉnh các mẫu thành ngữ, bạn có nguy cơ dịch từng dòng một mà không hiểu ý chính.

### 1.1 Không dịch dựa trên từ khóa; Hãy dịch theo ý định.

Một số ánh xạ gần như trực tiếp:

- `JSON.parse` -> `json.Unmarshal` - `JSON.stringify` -> `json.Marshal` - `process.env.FOO` -> `os.Getenv("FOO")` - `console.log` -> `fmt.Println` Nhưng nhiều ánh xạ chỉ đúng nếu nhìn từ mục đích:

- `Promise.all` không nên được ánh xạ một cách máy móc thành "một bó channels "; Với yêu cầu phân bổ ra, thành ngữ hơn là `errgroup + context` .
- `class` không map thành "lớp giả lập"; thường là `struct + constructor + methods + small interface` .
- `fs` không map đến đối tượng trung tâm; Go tách tệp I/O thành `os` , `io` , `bufio` , đôi khi thêm `filepath` .

### 1.2 Khi nào map này được sử dụng đúng?

Sử dụng tập bản đồ này khi:

- Bạn biết vấn đề mình muốn làm trong TS/Node, nhưng không biết package Go nguyên thủy nằm ở đâu.
- Bạn đang xem lại cổng mã từ TypeScript và muốn phát hiện "bản dịch nghĩa đen nhưng sai lệch về ngữ nghĩa".
- Đội cần một điểm vào nhanh trước khi tiến vào làn `helper/` .

Đừng sử dụng tập bản đồ này làm cuốn sách quy tắc cuối cùng. Khi ánh xạ bắt đầu chạm đến mô hình miền, kiểm soát vòng đời hoặc ranh giới kiến ​​trúc, bạn phải quay lại các bài học cốt lõi trong cụm này.

### 1.3 Các kiểu bất biến và lỗi

- Atlas này là một công cụ điều hướng, không phải là giấy phép để viết lại từng dòng một.
- Hướng dẫn gốc sử dụng nhiều ví dụ gốc về Node.js; Trong quá trình sản xuất Go hiện đại, một số mẫu cần được nâng cao thành `context` , `errgroup` , các hàm tạo rõ ràng và dịch ranh giới để rõ ràng hơn.
- Nếu việc ánh xạ khiến bạn thêm quá nhiều `any` , `interface{}` hoặc goroutines "trông giống như Promise ", thì đó thường là dấu hiệu cho thấy bạn đang dịch sai lớp trừu tượng.

Sự khác biệt thực sự không nằm ở việc ghi nhớ tên package . Nó nằm ở chỗ nhận ra cùng một ý định được “đóng gói” rất khác nhau giữa hai hệ thống. Sơ đồ dưới đây đưa điểm chính xác đó ra ánh sáng.

## 2. HÌNH ẢNH

### Cấp 1```text
What are you looking to do in TS/Node?

syntax + printing
    -> Go language + fmt + log

objects + classes + JSON
    -> struct + methods + encoding/json

files + streams + cli
    -> os + io + bufio + flag

HTTP + URL + request lifecycle
    -> net/http + net/url + context

Promise + async/await + cancellation
    -> goroutine + channel/select + errgroup + context

tooling + package workflow
    -> go mod + go test + gofmt + go doc
```![Translation atlas API map](./images/07-translation-atlas-api-map.png) *Hình: Cấp độ 1 cho thấy câu hỏi đúng không phải là "Có đối tượng nào giống như `fs` trong Go không?", mà là "trong đó package trong Go ý định này tồn tại?".*.

### Cấp 2```text
TS/Node runtime-shaped thinking
  -> process / fs / Buffer / Promise / class
-> find equivalent object
-> easy to translate according to the words but with different semantics.

Go intent-shaped thinking
  -> data modeling?       -> struct + constructor + json tags
  -> async orchestration? -> errgroup + context
  -> stream file?         -> os.Open + bufio.Scanner
  -> cli input?           -> flag + os.Args
  -> output/logging?      -> fmt / log / os.Stderr
```*Hình: Cấp độ 2 nhấn mạnh việc điều chỉnh lại quan trọng nhất: từ tra cứu lấy đối tượng làm trung tâm đến tra cứu lấy mục đích làm trung tâm.*.

Trực quan là đủ để xác định vị trí package . Phần còn lại là xem tập bản đồ này giúp bạn tránh khỏi việc dịch từng dòng một khi xử lý mã thực như thế nào.

## 3. MÃ

### Ví dụ 1: Cơ bản — `fs` + `JSON.parse` + mặc định phải là giải mã ranh giới rõ ràng.

> **Mục tiêu**: Map tập lệnh đọc cấu hình từ tệp JSON sang Go mà không trộn DTO tùy chọn với cấu hình miền.
> **Phương pháp tiếp cận**: Giải mã đầu vào thô ở ranh giới, sau đó áp dụng các giá trị mặc định rõ ràng khi tạo cấu hình thực tế.
> **Ví dụ**: `./config.json` → `ServiceConfig{ServiceName, Port, Debug}` .
> **Độ phức tạp**: O(n) theo kích thước tệp; phần quan trọng là thiết kế ranh giới chính xác chứ không phải hiệu suất.

Phiên bản TypeScript quen thuộc:```typescript
import { readFileSync } from "node:fs";

type ServiceConfigInput = {
  serviceName: string;
  port?: number;
  debug?: boolean;
};

type ServiceConfig = {
  serviceName: string;
  port: number;
  debug: boolean;
};

function loadConfig(path: string): ServiceConfig {
  const raw = readFileSync(path, "utf8");
  const parsed = JSON.parse(raw) as ServiceConfigInput;

  if (!parsed.serviceName) {
    throw new Error("serviceName is required");
  }

  return {
    serviceName: parsed.serviceName,
    port: parsed.port ?? 8080,
    debug: parsed.debug ?? false,
  };
}

const cfg = loadConfig("./config.json");
console.log(`service=${cfg.serviceName} port=${cfg.port} debug=${cfg.debug}`);
```Phiên bản Go tương ứng:```go
package main

import (
	"encoding/json"
	"fmt"
	"os"
)

type rawConfig struct {
	ServiceName string `json:"serviceName"`
	Port        *int   `json:"port"`
	Debug       *bool  `json:"debug"`
}

type ServiceConfig struct {
	ServiceName string
	Port        int
	Debug       bool
}

func loadConfig(path string) (ServiceConfig, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return ServiceConfig{}, fmt.Errorf("read config %s: %w", path, err)
	}

	var input rawConfig
	if err := json.Unmarshal(raw, &input); err != nil {
		return ServiceConfig{}, fmt.Errorf("decode config %s: %w", path, err)
	}
	if input.ServiceName == "" {
		return ServiceConfig{}, fmt.Errorf("serviceName is required")
	}

	cfg := ServiceConfig{
		ServiceName: input.ServiceName,
		Port:        8080,
		Debug:       false,
	}

		// Pointer only lives at the boundary to distinguish "no field" from "field with zero value"
	if input.Port != nil {
		cfg.Port = *input.Port
	}
	if input.Debug != nil {
		cfg.Debug = *input.Debug
	}

	return cfg, nil
}

func main() {
	cfg, err := loadConfig("./config.json")
	if err != nil {
		panic(err)
	}

	fmt.Printf("service=%s port=%d debug=%t\n", cfg.ServiceName, cfg.Port, cfg.Debug)
}
```> **Tại sao?** Trong Node/TypeScript, `undefined` , `null` , các trường tùy chọn và việc hợp nhất đối tượng mặc định thường đi cùng nhau khá tự nhiên. Go buộc bạn phải phân tách chúng rõ ràng hơn. Đây không phải là nghi lễ thừa - nó giúp ranh giới JSON vẫn rõ ràng và có thể sửa lỗi.

> **Takeaway**: Map `fs + JSON.parse` đến `os.ReadFile + json.Unmarshal` , nhưng giữ nguyên các giá trị mặc định và bất biến trong bước tạo đối tượng thực tế. Đừng nhét chúng vào DTO thô.

Trường hợp cơ bản là ổn. Nhưng hầu hết các nhóm không chuyển đổi ngôn ngữ chỉ để đọc tệp JSON; Họ chuyển đổi khi các yêu cầu phân chia, hết thời gian chờ và hủy bắt đầu gây ảnh hưởng. Đó là lúc tập bản đồ phải thay đổi cú pháp.

### Ví dụ 2: Trung cấp — `Promise.all` nên được dịch theo vòng đời chứ không phải theo hình thức.

> **Mục tiêu**: Map yêu cầu phân xuất bằng cách sử dụng `Promise.all` đến Go theo cách duy trì thời gian chờ và hủy toàn cầu.
> **Cách tiếp cận**: Sử dụng `fetch` + `AbortController` trong TS, sau đó `errgroup + context` trong Go .
> **Ví dụ**: Gọi song song ba điểm cuối `profile` , `billing` , `invoices` .
> **Độ phức tạp**: O(k) theo số lượng hạ lưu; chi phí thực sự nằm ở I/O mạng.

Phiên bản TypeScript với tính năng kiểm soát vòng đời quen thuộc:```typescript
type Dashboard = {
  profile: unknown;
  billing: unknown;
  invoices: unknown;
};

async function fetchJSON<T>(url: string, signal: AbortSignal): Promise<T> {
  const response = await fetch(url, { signal });
  if (!response.ok) {
    throw new Error(`request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function loadDashboard(baseURL: string): Promise<Dashboard> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 800);

  try {
    const [profile, billing, invoices] = await Promise.all([
      fetchJSON(`${baseURL}/profile`, controller.signal),
      fetchJSON(`${baseURL}/billing`, controller.signal),
      fetchJSON(`${baseURL}/invoices`, controller.signal),
    ]);

    return { profile, billing, invoices };
  } finally {
    clearTimeout(timeout);
  }
}
```Phiên bản Go tương ứng:```go
package dashboard

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"golang.org/x/sync/errgroup"
)

type Dashboard struct {
	Profile  map[string]any
	Billing  map[string]any
	Invoices map[string]any
}

func fetchJSON(ctx context.Context, client *http.Client, url string) (map[string]any, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, fmt.Errorf("build request %s: %w", url, err)
	}

	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("do request %s: %w", url, err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= http.StatusBadRequest {
		return nil, fmt.Errorf("request %s failed: %s", url, resp.Status)
	}

	var out map[string]any
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return nil, fmt.Errorf("decode %s: %w", url, err)
	}
	return out, nil
}

func LoadDashboard(ctx context.Context, baseURL string) (Dashboard, error) {
	ctx, cancel := context.WithTimeout(ctx, 800*time.Millisecond)
	defer cancel()

	client := &http.Client{}
	g, ctx := errgroup.WithContext(ctx)

	var profile map[string]any
	var billing map[string]any
	var invoices map[string]any

	g.Go(func() error {
		value, err := fetchJSON(ctx, client, baseURL+"/profile")
		if err != nil {
			return err
		}
		profile = value
		return nil
	})

	g.Go(func() error {
		value, err := fetchJSON(ctx, client, baseURL+"/billing")
		if err != nil {
			return err
		}
		billing = value
		return nil
	})

	g.Go(func() error {
		value, err := fetchJSON(ctx, client, baseURL+"/invoices")
		if err != nil {
			return err
		}
		invoices = value
		return nil
	})

	if err := g.Wait(); err != nil {
		return Dashboard{}, err
	}

	return Dashboard{
		Profile:  profile,
		Billing:  billing,
		Invoices: invoices,
	}, nil
}
```> **Tại sao?** Ánh xạ hướng dẫn ban đầu `Promise` tới channel là một điểm khởi đầu tốt để hiểu các nguyên hàm của Go 's concurrency . Nhưng với phân xuất theo phạm vi yêu cầu hiện đại, `errgroup + context` là một bản dịch gần hơn với sản xuất: nếu một nhánh không thành công, bối cảnh được chia sẻ sẽ tự động hủy bỏ các nhánh tương tự.

> **Takeaway**: Khi gặp `Promise.all` , đừng hỏi "[[E20]]] mỗi Promise thuộc về cái nào?". Hỏi "việc phân xuất này cần lỗi phân xuất, thời gian chờ và hủy ở đâu?".

Sau khi yêu cầu phân xuất đã được thông qua, cú sốc tiếp theo thường đến từ các tập lệnh và CLI nhỏ. Nút đặt `process` , `fs` , `readline` , `stdout` rất gần nhau; Go chia chúng thành nhiều packages nhỏ hơn. Đó là.

### Ví dụ 3: Nâng cao — các script dòng lệnh thường phải tách `process` thành nhiều Go packages nhỏ.

> **Mục tiêu**: Chuyển một tiện ích đếm dòng nhật ký theo regex từ Node.js sang Go trong khi vẫn giữ luồng phát trực tuyến, đối số CLI và xử lý thiết bị xuất chuẩn/thiết bị xuất chuẩn rõ ràng.
> **Cách tiếp cận**: TS sử dụng `process.argv` , `fs.createReadStream` , `readline` ; Go sử dụng `flag` , `os.Open` , `bufio.Scanner` , `regexp` .
> **Ví dụ**: `errorcount -pattern 'WARN|ERROR' ./app.log` .
> **Độ phức tạp**: O(n) theo số dòng; bộ nhớ ở gần O(1) do xử lý phát trực tuyến.

Các phiên bản TypeScript/Node thường bắt đầu như thế này:```typescript
import { createReadStream } from "node:fs";
import * as readline from "node:readline";

async function main(): Promise<void> {
  const filePath = process.argv[2];
  const pattern = process.argv[3] ?? "ERROR";

  if (!filePath) {
    throw new Error("usage: errorcount <file> [pattern]");
  }

  const re = new RegExp(pattern);
  const reader = readline.createInterface({
    input: createReadStream(filePath),
    crlfDelay: Infinity,
  });

  let count = 0;
  for await (const line of reader) {
    if (re.test(line)) {
      count++;
    }
  }

  process.stdout.write(`${count}\n`);
}

void main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
```Phiên bản Go tương ứng:```go
package main

import (
	"bufio"
	"flag"
	"fmt"
	"os"
	"regexp"
)

func main() {
	pattern := flag.String("pattern", "ERROR", "regular expression to count")
	flag.Parse()

	if flag.NArg() != 1 {
		fmt.Fprintln(os.Stderr, "usage: errorcount [-pattern REGEX] <file>")
		os.Exit(2)
	}

	re, err := regexp.Compile(*pattern)
	if err != nil {
		fmt.Fprintf(os.Stderr, "compile regex: %v\n", err)
		os.Exit(1)
	}

	file, err := os.Open(flag.Arg(0))
	if err != nil {
		fmt.Fprintf(os.Stderr, "open file: %v\n", err)
		os.Exit(1)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	count := 0
	for scanner.Scan() {
		if re.MatchString(scanner.Text()) {
			count++
		}
	}

	if err := scanner.Err(); err != nil {
		fmt.Fprintf(os.Stderr, "scan file: %v\n", err)
		os.Exit(1)
	}

	fmt.Fprintln(os.Stdout, count)
}
```> **Tại sao?** Đây là lúc tập bản đồ đặc biệt hữu ích: trong Node, nhiều khả năng nằm xung quanh `process` , `fs` và `readline` . Trong Go , không có "một đối tượng trung tâm" tương đương. Đổi lại, mỗi ý định có package rõ ràng hơn, nhỏ hơn.

> **Takeaway**: Đừng tìm Go `process` . Chấp nhận rằng các mối quan tâm về CLI/ runtime được trải rộng trên nhiều packages nhỏ - đó là cách Go giữ cho mã ít huyền diệu hơn.

Biết nơi người nguyên thủy sống là một nửa câu chuyện. Nửa còn lại dễ mắc sai sót khi sử dụng tập bản đồ làm từ điển song ngữ thay vì làm công cụ điều hướng.

## 4. Cạm bẫy

| # | Mức độ nghiêm trọng | Lỗi | Hậu quả | Sửa chữa |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Gây tử vong | Sử dụng tập bản đồ làm bảng dịch từng dòng và ánh xạ `Promise` sang thô channels | Nhìn bề ngoài, mã có vẻ "đúng Go " nhưng thiếu thời gian chờ, hủy và lỗi quạt vào | Dịch theo vòng đời: yêu cầu phân ra → `errgroup + context` , tín hiệu mức thấp sử dụng channel |
| 2 | 🔴 Gây tử vong | Đang cố gắng tìm một đối tượng Go tương đương với `process` hoặc `fs` | Cảm giác bế tắc Go rời rạc, tạo ra trợ giúp vô nghĩa packages để bắt chước Node | Phân tách theo mục đích: file → `os/io/bufio` , CLI → `flag` , đầu ra → `fmt` / `os.Stderr` |
| 3 | 🟡 Chung | Chuyển `class` sang struct và xuất tất cả các trường để "dễ sử dụng" | Mất tính bất biến, API phình bề mặt, đột biến khó kiểm soát | Giữ các trường không được xuất khi cần, sử dụng các hàm tạo và phương thức rõ ràng |
| 4 | 🔵 Nhỏ | Sử dụng tập bản đồ trong khi bỏ qua các bài học về mô hình tư duy và mô hình dữ liệu | Dịch cú pháp nhưng vẫn đưa ra quyết định thiết kế sai lầm | Sử dụng tập bản đồ để điều hướng nhanh, sau đó quay lại bài viết cốt lõi tương ứng để tìm hiểu chuyên sâu |

## 5. GIỚI THIỆU

| Tài nguyên | Loại | Liên kết | Lưu ý |
| --- | --- | --- | --- |
| Golang dành cho nhà phát triển Node.js | Cộng đồng | https://github.com/miguelmota/golang-for-nodejs-developers?tab=readme-ov-file#examples | Hướng dẫn ban đầu làm cơ sở cho tập bản đồ này; Bài viết hiện tại chọn ánh xạ |
| Go Thư viện chuẩn | Chính thức | https://pkg.go.dev/std | Chỉ mục chuẩn để tra cứu đích package thay vì đoán theo namespace như Node |
| Chuyến tham quan Go | Chính thức | https://go.dev/tour/ | Cần thiết nếu bạn vẫn chưa quen với cú pháp cơ bản của Go và mô hình package |
| Có hiệu lực Go | Chính thức | https://go.dev/doc/effect_go | Nguồn gốc của thành ngữ Go sau khi biết cú pháp |

## 6. KHUYẾN NGHỊ

Cốt lõi của **Bản đồ dịch** rất rõ ràng. Các nhánh mở rộng bên dưới giúp bạn biến tập bản đồ này thành thói quen viết Go tự nhiên thay vì dịch từ TypeScript.

Nó kết thúc bằng việc biết khi nào nên rời khỏi tập bản đồ và quay trở lại cốt lõi để đưa ra quyết định tốt hơn.

| Gia hạn | Khi nào | Cơ sở lý luận | Liên kết |
| --- | --- | --- | --- |
| Mô hình tinh thần & Runtime | Khi bạn cứ hỏi "tại sao Go không có X như Node?" | Vấn đề gốc thường là mô hình tư duy chứ không phải thiếu API | [→ 01-mental-model-runtime](./01-mental-model-runtime.md) |
| Các loại & mô hình hóa dữ liệu | Khi chuyển DTO, công đoàn, tùy chọn và lớp học bắt đầu bị ảnh hưởng | Atlas chỉ hướng; bài viết này khóa ranh giới dữ liệu và bất biến | [→ 02-types-data-modeling](./02-types-data-modeling.md) |
| Lỗi, Concurrency , Ngữ cảnh | Khi bản dịch chạm vào `Promise.all` , hết thời gian chờ, hủy bỏ hoặc thử lại | Trường hợp ánh xạ cú pháp phải nhường chỗ cho việc kiểm soát vòng đời | [→ 03-errors-concurrency-context](./03-errors-concurrency-context.md) |
| Bố cục dự án, Dụng cụ, Kiểm tra | Khi nhóm hỏi "Nếu Go thiếu khung/công cụ, chúng tôi có thể vận chuyển bằng cách nào?" | Kết nối tập bản đồ với quy trình đóng tàu thử nghiệm thực tế | [→ 04-project-layout-tooling](./04-project-layout-tooling-testing.md) |
| Promise & Async | Khi bạn cần công thức nấu ăn sâu hơn cho `Promise.all` , `Promise.race` , `AbortController` | Ánh xạ từng mẫu ở cấp độ trợ giúp | [→ 04-promise-async](../helper/04-promise-async.md) |
| Lớp → Struct | Khi codebase quá nặng về phân cấp lớp | Giúp cắt giảm thói quen sử dụng cổng OOP một-một | [→ 12-class-struct](../helper/12-class-struct.md) |
| Người trợ giúp — TS/JS → Go Tiện ích | Khi bạn cần nhiều ánh xạ cấp công thức liên tiếp | Sử dụng cụm trợ giúp để tra cứu nhanh, trong khi tập bản đồ đóng vai trò là công cụ điều hướng | [→ Helper README](../helper/README.md) |

## 7. THAM KHẢO NHANH

Bảng bên dưới là phần thưởng cuối bài: dùng để scan lại trong 20-30 giây mà không cần phải đọc lại toàn bộ cung trên.

| # | Thành ngữ TS/Node | Go tương đương | Lưu ý |
| --- | --- | --- | --- |
| 1 | `console.log` , `console.error` | `fmt.Println` , `fmt.Fprintf(os.Stderr, ...)` , `log.Println` | `fmt` cho đầu ra trực tiếp; `log` khi cần dấu thời gian/tiền tố |
| 2 | `JSON.parse` , `JSON.stringify` | `json.Unmarshal` , `json.Marshal` , `json.NewDecoder` | JSON ranh giới hầu như luôn đi qua `encoding/json` |
| 3 | `Buffer` | `[]byte` , `bytes.Buffer` , `encoding/hex` , `encoding/binary` | `[]byte` là nguyên thủy quan trọng nhất, không phải là trình bao bọc đối tượng |
| 4 | `fs.readFileSync` , `createReadStream` | `os.ReadFile` , `os.Open` , `bufio.Scanner` , `io.Reader` | Các tệp/luồng được phân chia theo mục đích thay vì được nhóm thành một không gian tên |
| 5 | `Promise.all` | `errgroup.WithContext` | Yêu cầu phân xuất riêng nên xem xét theo vòng đời thay vì thô channel |
| 6 | `AbortController` | `context.WithCancel` , `context.WithTimeout` | Việc hủy bỏ là một hợp đồng rõ ràng trong Go |
| 7 | `class` , `constructor` , `this` | `struct` , `NewXxx` , các phương thức, nhỏ interfaces | Bắt đầu từ composition , không mô phỏng inheritance |
| 8 | `process.argv` , `process.env` | `flag` , `os.Args` , `os.Getenv` | CLI args và env là riêng biệt, không đi qua một đối tượng chung |
| 9 | `EventEmitter` | rõ ràng interfaces , callbacks , đôi khi channel | Channel không phải là bản sao một-một của bộ phát |
| 10 | `npm install` , `package.json scripts` , `jest` , `bench` | `go mod` , `go test` , `go test -bench` , `go doc` | Thu thập nhiều quy trình công việc thành một chuỗi công cụ tiêu chuẩn hơn |

**Điều hướng**: [← Previous](./06-migration-playbook.md) · [→ Next](./README.md)