<!-- tags: java, performance -->
# ☕ Java Performance — Profiling Hotspots Before Tuning

> Tối ưu không bắt đầu bằng chỉnh cờ JVM hay rewrite code. Nó bắt đầu bằng việc biết chính xác đâu là hotspot. Bài này tập trung vào tư duy profiling trước tuning.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 14 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Advanced |
| **Use case** | CPU spike, latency regression, allocation pressure |
| **Java focus** | profiling mindset, hotspot, flamegraph, allocation analysis |
| **Prerequisites** | GC basics, deployment awareness |

## 1. DEFINE

Hình dung service chậm đi và cả nhóm đã có năm giả thuyết khác nhau: GC, SQL, lock contention, serialization hay một helper vô danh nào đó. Nếu không có profiler, mọi cuộc tranh luận đều nghe hợp lý. Profiling chỉ thật sự có giá trị khi nó cắt đôi đám giả thuyết đẹp đẽ đó bằng evidence.

Bài này đặt `Java Performance — Profiling Hotspots Before Tuning` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Profiling dùng để trả lời gì?

Profiling giúp xác định:

- CPU đang cháy ở method nào
- allocation hotspot nằm ở đâu
- thread nào bị block hoặc contention
- tối ưu nào đáng làm nhất

### Actors

| Actor | Vai trò |
| --- | --- |
| CPU profiler | Tìm method tiêu tốn CPU |
| Allocation profiler | Tìm nơi tạo object nhiều |
| Thread dump | Cho biết block/deadlock/contention |
| Flamegraph | Cách nhìn hotspot theo stack |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Tối ưu sai chỗ | Không có measurement | Profile trước mọi thay đổi lớn |
| Chỉ nhìn average latency | Bỏ sót tail latency | Kết hợp profile với percentiles |
| So sánh local vs prod lệch | Workload không giống | Profile gần workload thật hơn |

Các failure mode trên nghe cơ bản. Nhưng có trap: profiling production với overhead cao = cascade failure, và premature optimization = wasted effort. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa của Java Performance — Profiling Hotspots Before Tuning mới chỉ cho bạn vocabulary. Điều người đọc cần tiếp theo là một bức tranh về nơi chi phí thực sự xuất hiện và cách nó di chuyển khi workload tăng.

```text
symptom
  │
  ├── high CPU      -> CPU profiler
  ├── high GC       -> allocation profiler
  └── stuck thread  -> thread dump
```

```text
flamegraph
  wide bar = expensive path
  tall stack = deep call chain
  start wide-first, not intuition-first
```

## 3. CODE

Flow của Java Performance — Profiling Hotspots Before Tuning đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: micro hotspot example

```java
// NaiveSearchService.java — CPU-heavy repeated string normalization
import java.util.List;

public final class NaiveSearchService {
    public int countMatches(List<String> values, String query) {
        int matches = 0;
        for (String value : values) {
            if (value.toLowerCase().contains(query.toLowerCase())) {
                matches++;
            }
        }
        return matches;
    }
}
```

CPU profiling đã cover. Nhưng heap analysis cần MAT — hãy dump.

### Intermediate: allocation hotspot example

```java
// ReportRenderer.java — Repeated temporary object creation
public final class ReportRenderer {
    public String renderLine(String orderId, long amount) {
        return new StringBuilder()
                .append("order=")
                .append(orderId)
                .append(",amount=")
                .append(amount)
                .toString();
    }
}
```

Heap đã cover. Nhưng async profiling cần low-overhead — hãy dùng async-profiler.

### Advanced: profiling checklist

```text
1. Reproduce symptom under representative load
2. Capture CPU profile or thread dump
3. Confirm hotspot path
4. Change one thing
5. Measure again
```

Bạn đã đi qua profiling, heap, và async. Bây giờ đến phần nguy hiểm: high-overhead profiling và premature optimization — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Performance — Profiling Hotspots Before Tuning` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Tối ưu theo cảm giác | Profile trước |
| 2 | Thấy một hotspot rồi rewrite toàn module | Chỉ sửa path chứng minh được |
| 3 | Không đo lại sau fix | Benchmark/profile lại |
| 4 | Chỉ nhìn local laptop | Cố lấy workload gần production hơn |

Bạn đã đi qua Profiling và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Java Flight Recorder | https://docs.oracle.com/en/java/javase/21/jfapi/ |
| JDK Mission Control | https://www.oracle.com/java/technologies/jdk-mission-control.html |
| async-profiler | https://github.com/async-profiler/async-profiler |

## 6. RECOMMEND

Khi các bẫy chính của `Java Performance — Profiling Hotspots Before Tuning` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Benchmarking | Có candidate optimization rõ | So trước/sau |
| GC log analysis | Nghi allocation pressure | Gắn symptom với memory path |
| Tracing + profiling | Distributed latency cao | Kết nối request path với hotspot |

## 7. QUIZ

### Quick Check

1. Vì sao profiling nên đi trước tuning?
2. Flamegraph giúp thấy điều gì?
3. Khi nào thread dump quan trọng hơn CPU profiler?

### Answer Key

1. Vì nếu không đo, rất dễ tối ưu sai chỗ.
2. Hot path nào đang tốn tài nguyên nhiều nhất theo call stack.
3. Khi symptom là block, deadlock hoặc contention thay vì CPU burn.

## 8. NEXT STEPS

- Nối với `jvm/gc` nếu thấy allocation pressure
- Hoặc qua `expert/resilience` để nhìn performance trong bối cảnh production failure
