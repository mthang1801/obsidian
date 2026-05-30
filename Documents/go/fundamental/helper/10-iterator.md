<!-- tags: golang, iterators, generics --> # 🔄 Iterator — TS cho...của / Generator → Go `iter.Seq` & phạm vi

> TypeScript sử dụng `function*` generators với `yield` cho các chuỗi lười biếng. Go 1.23+ giới thiệu `iter.Seq[V]` — một iterator dựa trên chức năng tích hợp với `for range` . Không channels , không goroutines , không rò rỉ.

📅 Đã tạo: 23-03-2026 · 🔄 Đã cập nhật: 19-04-2026 · ⏱️ 12 phút đọc

## 1. ĐỊNH NGHĨA

Nhà phát triển chuyển con trỏ database được phân trang từ `for await (const page of fetchPages())` generator của JavaScript. Họ triển khai nó bằng cách sử dụng Go channels - a goroutine gửi các trang tới a channel , người tiêu dùng đọc với `for page := range ch` .

Máy khách ngắt kết nối giữa vòng lặp. Không ai đọc từ channel nữa. [[E42]]] chặn vĩnh viễn `ch <- page` - nó làm rò rỉ bộ nhớ trong suốt thời gian tồn tại của quá trình. Go 1.23+ giải quyết vấn đề này với `iter.Seq[V]` : a closure -based iterator chạy đồng bộ trong goroutine của người gọi. Khi người tiêu dùng phá vỡ, iterator sẽ dừng ngay lập tức - không có goroutine bị rò rỉ.

### 1.1 Các kiểu bất biến và lỗi

| Ranh giới | Trách nhiệm cốt lõi |
| --- | --- |
| ** `iter.Seq[V]` ** | Hàm `func(yield func(V) bool)` gọi `yield` cho mỗi phần tử. Chạy trong goroutine của người gọi. |
| **Đảm bảo không rò rỉ** | Không có goroutines được sinh ra. Khi người tiêu dùng phá vỡ, `yield` trả về `false` và iterator thoát ra. |

| Quy tắc | Cơ sở lý luận |
| --- | --- |
| **Luôn kiểm tra `!yield(v)` ** | Nếu người tiêu dùng thoát ra khỏi vòng lặp `for range` , `yield` trả về `false` . Bỏ qua nó sẽ tạo ra một vòng lặp vô hạn. |
| **Thích `iter.Seq` hơn channels ** | Các trình vòng lặp dựa trên Channel yêu cầu quản lý vòng đời goroutine . `iter.Seq` không có vòng đời - đó là lệnh gọi hàm. |

### 1.2 Chuỗi thất bại

- **Vòng lặp zombie:** iterator của bạn bỏ qua giá trị trả về `yield` . Người tiêu dùng gọi `break` trong vòng lặp `for range` , nhưng iterator tiếp tục tạo ra các giá trị - mức sử dụng CPU vô hạn cho đến khi quá trình bị hủy.
- **Bẫy channel :** Bạn sử dụng goroutine và channel để triển khai phép lặp lười biếng. Người tiêu dùng từ bỏ channel . Các khối goroutine được gửi vĩnh viễn - một khối goroutine bị rò rỉ cho mỗi lần lặp bị bỏ rơi.

## 2. HÌNH ẢNH

JavaScript generators và Go `iter.Seq` đạt được cùng một mục tiêu (lặp lại lười biếng) thông qua các cơ chế khác nhau. ![Iterator Yield Mechanics](./images/10-iterator-compare.png) *Hình: JS generators sử dụng `yield` để tạm dừng thực thi. Go `iter.Seq` sử dụng closure gọi `yield(v)` - khi `yield` trả về `false` , iterator thoát ra. Không liên quan đến goroutines .*

## 3. MÃ

Với mô hình dựa trên closure - được thiết lập, mã bên dưới sẽ xây dựng ba mẫu: tạo phạm vi cơ bản, lặp lại khóa-giá trị với `iter.Seq2` và quy trình lọc lười biếng.

### Ví dụ 1: Cơ bản — Phạm vi generator > **Mục tiêu**: Tạo phạm vi tùy chỉnh iterator tương đương với `function* range(start, end)` của JavaScript.
> **Phương pháp tiếp cận**: Trả về một `iter.Seq[int]` closure gọi `yield` cho mỗi giá trị.
> **Độ phức tạp**: Mang lại phần tử O(N).```go
// basic_sequences.go
package iterators

import (
	"fmt"
	"iter"
)

// TS: function* range(start, end) { for (let i = start; i < end; i++) yield i }
func RangeBounds(start, end int) iter.Seq[int] {
	return func(yield func(int) bool) {
		for index := start; index < end; index++ {
			// ✅ Check yield return: false means the consumer called break
			if !yield(index) {
				return
			}
		}
	}
}

func ExecuteGenerators() {
	// Works directly with for-range (Go 1.23+)
	for value := range RangeBounds(1, 4) {
		fmt.Printf("Value: %d\n", value)
	}
}
```> **Takeaway**: `if !yield(v) { return }` là đường quan trọng. Không có nó, `break` trong vòng lặp của người tiêu dùng không có tác dụng gì - iterator vẫn tiếp tục chạy. Đây là Go tương đương với việc kiểm tra xem người gọi của generator có còn nghe hay không.

---

### Ví dụ 2: Trung gian — Cặp khóa-giá trị với `iter.Seq2` > **Mục tiêu**: Tạo một iterator được lập chỉ mục tương đương với `Array.entries()` hoặc `Object.entries()` của JavaScript.
> **Phương pháp tiếp cận**: `iter.Seq2[int, T]` mang lại hai giá trị cho mỗi lần lặp — chỉ mục và phần tử.
> **Độ phức tạp**: Mang lại phần tử O(N).```go
// coordinate_sequences.go
package iterators

import (
	"fmt"
	"iter"
)

// TS: Array.prototype.entries() → [index, value] pairs
func Enumerate[T any](collection []T) iter.Seq2[int, T] {
	return func(yield func(int, T) bool) {
		for index, element := range collection {
			if !yield(index, element) {
				return
			}
		}
	}
}

func MapStructures() {
	payload := []string{"Primary", "Secondary", "Tertiary"}
	
	for index, value := range Enumerate(payload) {
		fmt.Printf("Index [%d]: %s\n", index, value)
	}
}
```> **Takeaway**: `iter.Seq2[K, V]` hoạt động với `for k, v := range ...` — phá hủy hai biến. Sử dụng nó cho any iterator tạo ra các cặp (chỉ mục+giá trị, khóa+giá trị, lỗi+kết quả).

---

### Ví dụ 3: Nâng cao — Bộ lọc lười pipeline > **Mục tiêu**: Lọc một chuỗi lớn mà không phân bổ một chuỗi trung gian slice , tương đương với RxJS `pipe(filter(...))` .
> **Phương pháp tiếp cận**: Chuỗi hàm `iter.Seq` — mỗi hàm bao bọc iterator trước đó và áp dụng một phép biến đổi. Không có slices trung gian được phân bổ.
> **Độ phức tạp**: Tổng O(N) — mỗi phần tử được đánh giá một lần trong chuỗi.```go
// pipeline_streams.go
package iterators

import (
	"iter"
)

func FilterSeq[T any](stream iter.Seq[T], predicate func(T) bool) iter.Seq[T] {
	return func(yield func(T) bool) {
		for element := range stream {
			if predicate(element) {
				// ✅ Propagate the consumer's break signal through the chain
				if !yield(element) {
					return
				}
			}
		}
	}
}

func Collect[T any](stream iter.Seq[T]) []T {
	var result []T
	for element := range stream {
		result = append(result, element)
	}
	return result
}
```> **Takeaway**: Đường dẫn Iterator lười biếng — `FilterSeq` không xử lý các phần tử any cho đến khi người tiêu dùng bắt đầu lặp lại. `Collect` cụ thể hóa chuỗi thành slice . Đây là sự phân chia lười biếng/háo hức tương tự như các phương thức RxJS có thể quan sát được và array .

## 4. Cạm bẫy

| # | Khiếm khuyết | Sửa chữa |
| --- | --- | --- |
| 1 | Sử dụng channels để triển khai phép lặp lười biếng | Thay thế bằng `iter.Seq` - không goroutines , không có vòng đời channel , không rò rỉ |
| 2 | Bỏ qua giá trị trả về `yield` | Luôn kiểm tra `if !yield(v) { return }` — không có nó, `break` không có tác dụng |
| 3 | Gọi `Collect` trên các vòng lặp vô hạn | Thêm trình bao bọc `Take(n)` dừng sau N phần tử trước khi thu thập |

## 5. GIỚI THIỆU

| Tài nguyên | Liên kết |
| --- | --- |
| `iter` package | [pkg.go.dev/iter](https://pkg.go.dev/iter) |
| Blog hàm phạm vi | [go.dev/blog/range-functions](https://go.dev/blog/range-functions) |

## 6. KHUYẾN NGHỊ

| Gia hạn | Khi nào | Cơ sở lý luận |
| --- | --- | --- |
| [Array Pipelines](./02-array-pipeline.md) | Khi đầu vào vừa với bộ nhớ | Háo hức `Map` / `Filter` / `Reduce` trên bê tông slices |
| [Optional Types](./11-optional-nullable.md) | Khi các trình vòng lặp có thể tạo ra các giá trị vắng mặt | `Optional[T]` bao bọc các phần tử nullable trong chuỗi iterator |

**Điều hướng**: [← Set & Concurrent Map](./09-set-concurrent-map.md) · [→ Optional & Nullable](./11-optional-nullable.md)