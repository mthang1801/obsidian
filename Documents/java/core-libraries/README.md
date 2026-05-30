<!-- tags: java, core-libraries -->
# Java Core Libraries

> Router cho nhánh Java Core Libraries, nơi HTTP Client, IO & NIO, Serialization và các lane liên quan được ghép thành một đường học có chủ đích.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 6 phút đọc

## 1. DEFINE

Hình dung bạn chỉ đổi một đoạn code tưởng rất nhỏ: parse thời gian, bắn HTTP request hoặc ghép một stream để lọc dữ liệu. Không có gì “kiến trúc” ở đây cả, cho tới khi bug production xuất hiện đúng ở đoạn nhỏ đó. Nhánh này tồn tại để kéo các core library của Java ra khỏi cảm giác quen tay hời hợt và đặt lại chúng vào đúng trọng lượng mà chúng mang trong hệ thống thật.

Riêng với nhánh `Java Core Libraries`, mục tiêu không phải đọc cho đủ mục. Mục tiêu là biết nên vào từ đâu khi symptom, câu hỏi hoặc decision point đã xuất hiện ngay trong công việc thật.

| Variant | Mô tả |
| --- | --- |
| Router | Điều hướng người đọc vào đúng cụm Java trước khi đi sâu |
| Learning path | Giữ thứ tự từ mental model nền đến production judgment |
| Review map | Chỉ ra nhánh nào nên mở khi symptom hoặc câu hỏi thay đổi |

Core insight:

> README tốt không chỉ liệt kê file. Nó giúp người đọc biết nên mở gì trước, mở gì sau, và vì sao nhánh đó đáng đọc ngay lúc này.

### Module Map

| Điểm vào | Loại | Vai trò |
| --- | --- | --- |
| [`http-client/`](http-client/README.md) | Directory | Router cho nhánh HTTP Client |
| [`io-nio/`](io-nio/README.md) | Directory | Router cho nhánh IO & NIO |
| [`serialization/`](serialization/README.md) | Directory | Router cho nhánh Serialization |
| [`streams/`](streams/README.md) | Directory | Router cho nhánh Streams |
| [`strings/`](strings/README.md) | Directory | Router cho nhánh Strings |
| [`time/`](time/README.md) | Directory | Router cho nhánh Time API |

## 2. VISUAL

Định nghĩa đã đặt đúng người đọc vào tension của nhánh này. Tiếp theo là nhìn xem module map thực sự chia lane học ra sao sau khi đã dọn bỏ những điểm chết trong tree.

### Level 1

```text
HTTP Client -> IO & NIO -> Serialization -> Streams -> Strings -> Time API
```

*Hình: Level 1 cho thấy trục di chuyển chính của nhánh này trong hành trình Java.*

### Level 2

```text
Track / Symptom                 Điểm vào đầu tiên             Coverage
----------------------------  ----------------------------  ----------------
HTTP Client                   entry via README               1 article(s)
IO & NIO                      entry via README               0 article(s)
Serialization                 entry via README               0 article(s)
Streams                       entry via README               1 article(s)
Strings                       entry via README               0 article(s)
Time API                      entry via README               1 article(s)
```

*Hình: Level 2 biến README thành router theo cụm kiến thức và điểm vào thực tế.*

## 3. CODE

Một router chỉ thật sự có giá trị khi nó biến thành cách dùng cụ thể. Artifact dưới đây là quy trình ngắn để đọc nhánh này mà không rơi lại vào kiểu mở đại một bài rồi hi vọng tự nối được.

### Basic: reading loop for this track

```text
1. Chọn symptom hoặc câu hỏi đang gặp
2. Mở đúng README nhánh con hoặc seed article gần nhất
3. Đọc bài theo thứ tự basic -> advanced trong cùng cụm
4. Ghi lại một invariant hoặc pitfall vừa học
5. Nếu còn mơ hồ, quay sang quiz hoặc nhánh liên quan
```

**Kết luận**: Dùng nhánh này như một đường đi có checkpoint, không như một danh mục file rời rạc.

## 4. PITFALLS

README của một nhánh Java dễ bị xem nhẹ, nhưng chính ở đây người đọc thường đi sai hướng sớm nhất. Những lỗi dưới đây là các kiểu trượt phổ biến nhất.

| # | Severity | Lỗi | Hậu quả | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🟡 Common | Mở bài theo tên nghe quen thay vì theo symptom thực tế | Học lệch vấn đề đang cần | Bắt đầu từ module map và decision lens |
| 2 | 🟠 Major | Nhảy thẳng vào bài advanced khi nền chưa khóa | Hiểu lỗ mỗ nhưng không bền | Đi theo reading loop từ điểm vào gần nhất |
| 3 | 🟡 Common | Xem README như mục lục thuần túy | Bỏ lỡ logic liên kết giữa các bài | Đọc luôn DEFINE và RECOMMEND của router |

## 5. REF

| Resource | Loại | Link | Ghi chú |
| --- | --- | --- | --- |
| Java Documentation | Official docs | https://docs.oracle.com/en/java/ | Entry point chuẩn cho Java core và JVM |
| Spring Documentation | Official docs | https://docs.spring.io/ | Entry point cho các nhánh framework |
| OpenJDK JEP Index | Official docs | https://openjdk.org/jeps/0 | Hữu ích cho các chủ đề runtime và language evolution |

## 6. RECOMMEND

Khi bản đồ của nhánh này đã rõ, bước tiếp theo không phải đọc nhiều hơn ngẫu nhiên mà là rẽ đúng sang submodule hoặc seed article đang mang lực kéo lớn nhất với symptom hiện tại.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| [`http-client/`](./http-client/README.md) | Khi muốn đi sâu vào HTTP Client | Giữ learning path liền mạch |
| [`io-nio/`](./io-nio/README.md) | Khi muốn đi sâu vào IO & NIO | Giữ learning path liền mạch |
| [`serialization/`](./serialization/README.md) | Khi muốn đi sâu vào Serialization | Giữ learning path liền mạch |
| [`streams/`](./streams/README.md) | Khi muốn đi sâu vào Streams | Giữ learning path liền mạch |
| [`strings/`](./strings/README.md) | Khi muốn đi sâu vào Strings | Giữ learning path liền mạch |
| [`time/`](./time/README.md) | Khi muốn đi sâu vào Time API | Giữ learning path liền mạch |
