<!-- tags: java, jvm -->
# ☕ JVM Internals — Garbage Collection Basics & Tuning Mindset

> GC không phải thứ nên “tune vì nghe nói cần tune”. Bài này tập trung vào việc hiểu symptom, allocation pressure và trade-off trước khi đụng tới JVM options.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 15 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Advanced |
| **Use case** | Diagnose memory pressure, long pauses, unstable latency |
| **Java focus** | heap, allocation, pause, throughput, GC logs |
| **Prerequisites** | Java basics, deployment/runtime awareness |

## 1. DEFINE

Hình dung p95 latency vừa tăng, CPU bắt đầu dành nhiều thời gian cho GC hơn bình thường, và mỗi lần nhìn dashboard bạn đều có cảm giác service đang chậm đi vì một thứ rất sâu nhưng chưa thấy rõ hình. Đây là khoảnh khắc GC bước ra khỏi hậu trường và buộc bạn phải nhìn runtime như một phần của thiết kế.

Bài này đặt `JVM Internals — Garbage Collection Basics & Tuning Mindset` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### GC giải quyết gì?

GC tự động reclaim object không còn reachable. Nhưng trong production, điều quan trọng hơn là:

- allocation rate cao đến mức nào
- pause time có ảnh hưởng SLA không
- heap sizing có hợp lý không

### Actors

| Actor | Vai trò |
| --- | --- |
| Heap | Vùng nhớ cho object |
| Allocating code | Nơi tạo object gây pressure |
| GC cycle | Chu kỳ thu gom |
| GC logs / metrics | Tín hiệu để phân tích symptom |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Pause dài | Heap pressure hoặc object churn cao | Giảm allocation, đo đúng symptom |
| OOM dù heap lớn | Leak hoặc workload không kiểm soát | Tìm retention root thay vì chỉ tăng RAM |
| Tune mù | Chưa có measurement | Bắt đầu từ metrics và GC log |

Các failure mode trên nghe rõ. Nhưng có trap: GC tuning theo blog = mismatch workload, và heap quá lớn = long GC pause. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

JVM Internals — Garbage Collection Basics & Tuning Mindset chỉ dễ hiểu trên giấy khi chưa có runtime thật. Một lát cắt trực quan sẽ cho thấy tín hiệu nào đang được runtime giữ và tín hiệu nào chỉ là ảo giác bề mặt.

```text
code allocates objects
        │
        ▼
heap pressure rises
        │
        ▼
GC runs
   ├── frees dead objects
   └── may introduce pause
```

```text
high allocation rate -> frequent GC
high retention       -> heap growth / OOM
long pause           -> latency spikes
```

## 3. CODE

Flow của JVM Internals — Garbage Collection Basics & Tuning Mindset đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: allocation-heavy loop

```java
// AllocationPressureDemo.java — Simple object churn example
import java.util.ArrayList;
import java.util.List;

public final class AllocationPressureDemo {
    public static void main(String[] args) {
        for (int round = 0; round < 1_000; round++) {
            List<String> batch = new ArrayList<>();
            for (int i = 0; i < 10_000; i++) {
                batch.add("item-" + i);
            }
        }
    }
}
```

GC basics đã cover. Nhưng collector selection cần workload analysis — hãy profile.

### Intermediate: capture heap pressure symptom

```java
// MemorySnapshotPrinter.java — Print coarse heap usage for observation
public final class MemorySnapshotPrinter {
    public static void main(String[] args) {
        Runtime runtime = Runtime.getRuntime();
        long used = runtime.totalMemory() - runtime.freeMemory();
        System.out.println("used bytes = " + used);
        System.out.println("max bytes  = " + runtime.maxMemory());
    }
}
```

Collector đã cover. Nhưng GC logs cần parsing — hãy analyze.

### Advanced: enable GC logs

```bash
# Example JVM flags for GC logging
JAVA_TOOL_OPTIONS="-Xlog:gc*:stdout:time,level,tags"
```

Bạn đã đi qua GC, collectors, và log analysis. Bây giờ đến phần nguy hiểm: cargo cult tuning và oversized heap — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `JVM Internals — Garbage Collection Basics & Tuning Mindset` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Thấy CPU tăng là vội tune GC | Đo allocation, heap và pause trước |
| 2 | Chỉ tăng heap để che symptom | Tìm root cause allocation/retention |
| 3 | Không bật GC log hoặc metrics | Thiếu dữ liệu để reasoning |
| 4 | Tối ưu JVM trước khi tối ưu code | Giảm object churn từ code trước |

Bạn đã đi qua GC Tuning và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Java GC Tuning Guide | https://docs.oracle.com/en/java/javase/21/gctuning/ |
| JVM Logging | https://docs.oracle.com/en/java/javase/21/docs/specs/man/java.html |
| G1 GC Overview | https://docs.oracle.com/en/java/javase/21/gctuning/garbage-first-g1-garbage-collector1.html |

## 6. RECOMMEND

Khi các bẫy chính của `JVM Internals — Garbage Collection Basics & Tuning Mindset` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Heap dump analysis | Nghi memory leak | Tìm retained objects |
| Profiling allocation | Latency/CPU bất thường | Thấy hot allocation sites |
| Metrics dashboard | Cần quan sát liên tục | Tránh chẩn đoán bằng cảm giác |

## 7. QUIZ

### Quick Check

1. Vì sao tăng heap không luôn giải quyết vấn đề GC?
2. GC log hữu ích nhất ở điểm nào?
3. Khi nào nên nhìn vào allocation rate?

### Answer Key

1. Vì root cause có thể là leak hoặc object churn cao, không chỉ thiếu RAM.
2. Khi cần hiểu tần suất, pause và pattern GC thực tế.
3. Khi latency/CPU/GC frequency bất thường và nghi object churn.

## 8. NEXT STEPS

- Nối với `performance/profiling` để tìm allocation hotspot
- Hoặc đi sâu hơn vào JIT/class loading ở các batch sau
