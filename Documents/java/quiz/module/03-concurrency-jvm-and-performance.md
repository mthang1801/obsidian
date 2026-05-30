<!-- tags: java, quiz, concurrency, jvm -->
# Java Module Quiz — Concurrency, JVM & Performance

> Quiz cho concurrency, GC, profiling, JMH và runtime behavior: thread model, virtual threads, executors, allocation, tuning mindset.

📅 Ngày tạo: 2026-04-04 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 8 phút đọc

## 1. DEFINE

Hình dung bạn đã đọc về thread pool, GC, profiling và nghĩ mình đã có đủ nguyên tắc để xử lý incident runtime. Nhưng chỉ khi các dấu hiệu đó xuất hiện cùng lúc trong một tình huống cụ thể, bạn mới biết mình đang hiểu bằng cơ chế hay chỉ bằng khẩu hiệu. Đây là chỗ module quiz thử lửa điều đó.

Quiz này kiểm tra xem bạn có thật sự đọc được tín hiệu runtime hay không. Nó tập trung vào mental model: bottleneck nằm ở scheduling, allocation, lock contention hay phương pháp đo lường sai.

| Variant | Mô tả |
| --- | --- |
| Concurrency quiz | threads, executors, futures, virtual threads |
| JVM quiz | GC, memory, hotspot, profiling signals |
| Performance quiz | benchmarking, latency, throughput, false optimization |

Core insight:

> Ở vùng runtime, đáp án đúng thường là đáp án đọc tín hiệu đúng trước, không phải đáp án “nghe tối ưu” nhất.

## 2. VISUAL

Điều khó nhất của quiz runtime là thấy được câu hỏi đang hỏi về tín hiệu nào. Sơ đồ dưới đây giúp tách ba nhóm tín hiệu thường bị trộn vào nhau.

### Level 1

```text
scheduler pressure --> memory pressure --> measurement quality
```

*Hình: Phần lớn câu hỏi runtime nằm ở một trong ba lớp tín hiệu này, dù bề mặt có thể trông giống nhau.*

### Level 2

```text
Symptom                        Hỏi lại lớp nào?
----------------------------  -------------------------------------
queue dài / tasks chậm        executors, blocking, scheduling
GC spike / RSS tăng           allocation, retention, collector fit
benchmark đẹp nhưng app tệ    methodology, warmup, realism
```

*Hình: Quiz runtime tốt buộc bạn map symptom về đúng lớp tín hiệu trước khi phán đoán.*

## 3. CODE

Flow của Java Module Quiz — Concurrency, JVM & Performance đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: benchmark skepticism trigger

```java
@Benchmark
public String concatLoop() {
    String result = "";
    for (int i = 0; i < 100; i++) {
        result += i;
    }
    return result;
}
```

**Tại sao?** Một snippet đơn giản như vậy đủ để hỏi xem bạn đang đánh giá API, allocation pattern hay chính benchmark setup. Nếu không phân biệt được ba thứ đó, mọi kết luận performance đều lung lay.

**Kết luận**: Runtime quiz luôn nên bắt đầu bằng câu hỏi “mình đang đo cái gì thật ra?”.

## 4. PITFALLS

Biết cách dùng `Java Module Quiz — Concurrency, JVM & Performance` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Severity | Lỗi | Hậu quả | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🟠 Major | Trả lời theo từ khóa hot như virtual threads hay ZGC | Chọn giải pháp lệch vấn đề | Hỏi lại symptom gốc và tín hiệu đo |
| 2 | 🟡 Common | Đồng nhất benchmark với production truth | Tối ưu sai chỗ | Kiểm tra workload realism |
| 3 | 🟠 Major | Bỏ qua lock/scheduling để chỉ nhìn CPU | Chẩn đoán sai bottleneck | Đọc thêm thread state và wait profile |

## 5. REF

| Resource | Loại | Link | Ghi chú |
| --- | --- | --- | --- |
| JMH samples | Official docs | https://openjdk.org/projects/code-tools/jmh/ | Verify benchmark methodology |
| JEP 444 | Official docs | https://openjdk.org/jeps/444 | Verify virtual threads mental model |
| Java Flight Recorder docs | Official docs | https://docs.oracle.com/javacomponents/jmc/ | Verify profiling/runtime signals |

## 6. RECOMMEND

Khi các bẫy chính của `Java Module Quiz — Concurrency, JVM & Performance` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do | File |
| --- | --- | --- | --- |
| [01-executors-thread-pools-shutdown.md](../../concurrency/executors/01-executors-thread-pools-shutdown.md) | Sai scheduling mental model | Khóa executor semantics | Nội bộ |
| [01-virtual-threads-for-io-bound-workloads.md](../../concurrency/virtual-threads/01-virtual-threads-for-io-bound-workloads.md) | Sai virtual threads trade-off | Chọn workload phù hợp hơn | Nội bộ |
| [01-jmh-basics-benchmarking-without-self-deception.md](../../performance/benchmarking/01-jmh-basics-benchmarking-without-self-deception.md) | Sai cách đo | Sửa methodology trước khi tối ưu | Nội bộ |
