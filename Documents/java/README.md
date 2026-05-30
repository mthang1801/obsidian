<!-- tags: java, root -->
# Java Programming

> Bản đồ học Java từ nền tảng ngôn ngữ đến Spring, JVM, performance và incident reasoning cho backend engineer.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 6 phút đọc

## 1. DEFINE

Hình dung bạn vừa bước vào một codebase Java đang sống thật: một API mới cần ship, một service Spring Boot đang chậm dần trong dashboard, còn review queue thì đầy những câu hỏi về transaction, generics và JVM mà không ai muốn trả lời bằng linh cảm. Bạn không thiếu bài để đọc; bạn thiếu một bản đồ đủ tỉnh táo để biết nên mở nhánh nào trước khi lạc vào một rừng khái niệm rời rạc.

Riêng với nhánh `Java Programming`, mục tiêu không phải đọc cho đủ mục. Mục tiêu là biết nên vào từ đâu khi symptom, câu hỏi hoặc decision point đã xuất hiện ngay trong công việc thật.

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
| [`architecture/`](architecture/README.md) | Directory | Router cho nhánh Architecture |
| [`backend/`](backend/README.md) | Directory | Router cho nhánh Backend |
| [`build-tools/`](build-tools/README.md) | Directory | Router cho nhánh Build Tools |
| [`concurrency/`](concurrency/README.md) | Directory | Router cho nhánh Concurrency |
| [`core-libraries/`](core-libraries/README.md) | Directory | Router cho nhánh Core Libraries |
| [`expert/`](expert/README.md) | Directory | Router cho nhánh Expert Topics |
| [`frameworks/`](frameworks/README.md) | Directory | Router cho nhánh Frameworks |
| [`fundamental/`](fundamental/README.md) | Directory | Router cho nhánh Fundamentals |
| [`jvm/`](jvm/README.md) | Directory | Router cho nhánh JVM |
| [`performance/`](performance/README.md) | Directory | Router cho nhánh Performance |
| [`quiz/`](quiz/README.md) | Directory | Router cho nhánh Quiz |
| [`testing/`](testing/README.md) | Directory | Router cho nhánh Testing |

## 2. VISUAL

Định nghĩa đã đặt đúng người đọc vào tension của nhánh này. Tiếp theo là nhìn xem module map thực sự chia lane học ra sao sau khi đã dọn bỏ những điểm chết trong tree.

### Level 1

```text
Architecture -> Backend -> Build Tools -> Concurrency -> Core Libraries -> Expert Topics -> Frameworks -> Fundamentals
```

*Hình: Level 1 cho thấy trục di chuyển chính của nhánh này trong hành trình Java.*

### Level 2

```text
Track / Symptom                 Điểm vào đầu tiên             Coverage
----------------------------  ----------------------------  ----------------
Architecture                  entry via README               1 article(s)
Backend                       entry via README               2 article(s)
Build Tools                   entry via README               2 article(s)
Concurrency                   entry via README               4 article(s)
Core Libraries                entry via README               3 article(s)
Expert Topics                 entry via README               2 article(s)
Frameworks                    entry via README               13 article(s)
Fundamentals                  entry via README               4 article(s)
JVM                           entry via README               1 article(s)
Performance                   entry via README               2 article(s)
Quiz                          entry via README               4 article(s)
Testing                       entry via README               4 article(s)
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
| [`architecture/`](./architecture/README.md) | Khi muốn đi sâu vào Architecture | Giữ learning path liền mạch |
| [`backend/`](./backend/README.md) | Khi muốn đi sâu vào Backend | Giữ learning path liền mạch |
| [`build-tools/`](./build-tools/README.md) | Khi muốn đi sâu vào Build Tools | Giữ learning path liền mạch |
| [`concurrency/`](./concurrency/README.md) | Khi muốn đi sâu vào Concurrency | Giữ learning path liền mạch |
| [`core-libraries/`](./core-libraries/README.md) | Khi muốn đi sâu vào Core Libraries | Giữ learning path liền mạch |
| [`expert/`](./expert/README.md) | Khi muốn đi sâu vào Expert Topics | Giữ learning path liền mạch |
| [`frameworks/`](./frameworks/README.md) | Khi muốn đi sâu vào Frameworks | Giữ learning path liền mạch |
| [`fundamental/`](./fundamental/README.md) | Khi muốn đi sâu vào Fundamentals | Giữ learning path liền mạch |
| [`jvm/`](./jvm/README.md) | Khi muốn đi sâu vào JVM | Giữ learning path liền mạch |
| [`performance/`](./performance/README.md) | Khi muốn đi sâu vào Performance | Giữ learning path liền mạch |
| [`quiz/`](./quiz/README.md) | Khi muốn đi sâu vào Quiz | Giữ learning path liền mạch |
| [`testing/`](./testing/README.md) | Khi muốn đi sâu vào Testing | Giữ learning path liền mạch |
