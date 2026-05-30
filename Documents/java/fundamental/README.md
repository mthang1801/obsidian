<!-- tags: java, fundamental -->
# Java Fundamentals

> Router cho nhánh Java Fundamentals, nơi Basics, Collections, Exceptions và các lane liên quan được ghép thành một đường học có chủ đích.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 5 phút đọc

## 1. DEFINE

Hình dung bạn đang review một PR rất “cơ bản”: vài collection, một generic type, một chút so sánh object, vài class mới. Không có gì kêu cứu. Rồi vài tuần sau, chính những lựa chọn nền đó bắt đầu tạo bug, tạo ma sát hoặc làm design méo đi. Nhánh fundamentals được viết cho đúng loại sai lầm âm thầm nhưng sống dai như vậy.

Riêng với nhánh `Java Fundamentals`, mục tiêu không phải đọc cho đủ mục. Mục tiêu là biết nên vào từ đâu khi symptom, câu hỏi hoặc decision point đã xuất hiện ngay trong công việc thật.

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
| [`basics/`](basics/README.md) | Directory | Router cho nhánh Basics |
| [`collections/`](collections/README.md) | Directory | Router cho nhánh Collections |
| [`exceptions/`](exceptions/README.md) | Directory | Router cho nhánh Exceptions |
| [`generics/`](generics/README.md) | Directory | Router cho nhánh Generics |
| [`oop/`](oop/README.md) | Directory | Router cho nhánh OOP |
| [`types/`](types/README.md) | Directory | Router cho nhánh Types |

## 2. VISUAL

Định nghĩa đã đặt đúng người đọc vào tension của nhánh này. Tiếp theo là nhìn xem module map thực sự chia lane học ra sao sau khi đã dọn bỏ những điểm chết trong tree.

### Level 1

```text
Basics -> Collections -> Exceptions -> Generics -> OOP -> Types
```

*Hình: Level 1 cho thấy trục di chuyển chính của nhánh này trong hành trình Java.*

### Level 2

```text
Track / Symptom                 Điểm vào đầu tiên             Coverage
----------------------------  ----------------------------  ----------------
Basics                        entry via README               2 article(s)
Collections                   entry via README               1 article(s)
Exceptions                    entry via README               0 article(s)
Generics                      entry via README               1 article(s)
OOP                           entry via README               0 article(s)
Types                         entry via README               0 article(s)
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
| [`basics/`](./basics/README.md) | Khi muốn đi sâu vào Basics | Giữ learning path liền mạch |
| [`collections/`](./collections/README.md) | Khi muốn đi sâu vào Collections | Giữ learning path liền mạch |
| [`exceptions/`](./exceptions/README.md) | Khi muốn đi sâu vào Exceptions | Giữ learning path liền mạch |
| [`generics/`](./generics/README.md) | Khi muốn đi sâu vào Generics | Giữ learning path liền mạch |
| [`oop/`](./oop/README.md) | Khi muốn đi sâu vào OOP | Giữ learning path liền mạch |
| [`types/`](./types/README.md) | Khi muốn đi sâu vào Types | Giữ learning path liền mạch |
