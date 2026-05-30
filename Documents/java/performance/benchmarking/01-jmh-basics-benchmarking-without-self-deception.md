<!-- tags: java, performance -->
# ☕ Java Performance — JMH Basics Without Self-Deception

> Benchmark Java rất dễ sai vì JIT, warmup, dead-code elimination và allocation noise. Nếu chỉ lấy `System.nanoTime()` bao quanh một đoạn code, bạn thường đang đo thứ khác chứ không phải logic muốn tối ưu. JMH tồn tại để tránh điều đó.

📅 Ngày tạo: 2026-03-28 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 15 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Expert |
| **Use case** | Đo performance của function/data structure trong JVM |
| **Java focus** | JMH, warmup, measurement, benchmark mode |
| **Prerequisites** | Profiling basics, JVM basics |

## 1. DEFINE

Hình dung bạn vừa viết xong một benchmark nhỏ, con số mới đẹp hơn hẳn, cả team bắt đầu tin rằng bottleneck đã được xử lý. Rồi production không đổi gì mấy. Benchmarking đáng học nhất ở đúng chỗ những con số đẹp bắt đầu giống lời an ủi hơn là sự thật.

Bài này đặt `Java Performance — JMH Basics Without Self-Deception` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Vì sao benchmark Java khó?

JVM tối ưu runtime theo thời gian. Kết quả chạy đầu và chạy sau có thể rất khác vì:

- JIT compilation
- warmup
- GC noise
- dead-code elimination
- constant folding

### Invariants

| Quy tắc | Ý nghĩa |
| --- | --- |
| Benchmark phải cô lập thứ cần đo | tránh đo setup không liên quan |
| Warmup rất quan trọng | JVM cần thời gian ổn định |
| Kết quả benchmark không thay profiling production | benchmark dùng cho câu hỏi hẹp |

Các failure mode trên nghe dễ tránh. Nhưng có trap: benchmark không warmup = JIT chưa optimize = kết quả sai, và dead code elimination = benchmark vô nghĩa. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa của Java Performance — JMH Basics Without Self-Deception mới chỉ cho bạn vocabulary. Điều người đọc cần tiếp theo là một bức tranh về nơi chi phí thực sự xuất hiện và cách nó di chuyển khi workload tăng.

```text
wrong benchmark:
  one main() + nanoTime()

better benchmark:
  JMH state
    -> warmup
    -> measurement
    -> forks
    -> report
```

## 3. CODE

Flow của Java Performance — JMH Basics Without Self-Deception đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: minimal JMH benchmark

```java
// StringJoinBenchmark.java — Measure two string-building strategies with JMH
package com.example.benchmark;

import java.util.concurrent.TimeUnit;
import org.openjdk.jmh.annotations.Benchmark;
import org.openjdk.jmh.annotations.BenchmarkMode;
import org.openjdk.jmh.annotations.Mode;
import org.openjdk.jmh.annotations.OutputTimeUnit;

@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.NANOSECONDS)
public class StringJoinBenchmark {
    @Benchmark
    public String plusOperator() {
        return "order-" + 42 + "-paid";
    }

    @Benchmark
    public String stringBuilder() {
        return new StringBuilder()
                .append("order-")
                .append(42)
                .append("-paid")
                .toString();
    }
}
```

JMH basics đã cover. Nhưng blackhole cần consume — hãy prevent DCE.

### Intermediate: state and input size

```java
// ArraySearchState.java — Parameterize benchmark inputs instead of hardcoding one path
package com.example.benchmark;

import org.openjdk.jmh.annotations.Param;
import org.openjdk.jmh.annotations.Scope;
import org.openjdk.jmh.annotations.State;

@State(Scope.Thread)
public class ArraySearchState {
    @Param({"100", "1000", "10000"})
    public int size;
}
```

Blackhole đã cover. Nhưng parameterized benchmarks cần @Param — hãy sweep.

### Advanced: benchmark reading guide

```text
AverageTime:
  one operation takes bao lâu

Throughput:
  một đơn vị thời gian xử lý được bao nhiêu operation

Always inspect:
  - warmup iterations
  - forks
  - variance/error
  - allocation rate if relevant
```

Bạn đã đi qua JMH, blackhole, và params. Bây giờ đến phần nguy hiểm: no warmup và dead code — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Performance — JMH Basics Without Self-Deception` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Dùng `nanoTime()` trong `main()` rồi kết luận performance | dùng JMH |
| 2 | Không warmup | để JVM ổn định trước measurement |
| 3 | Benchmark code bị tối ưu mất | dùng JMH pattern đúng |
| 4 | Tối ưu micro-benchmark khi bottleneck thật ở DB/network | profiling production trước |

Bạn đã đi qua JMH Benchmarking và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| JMH project | https://openjdk.org/projects/code-tools/jmh/ |
| JMH samples | https://hg.openjdk.org/code-tools/jmh/file/tip/jmh-samples |
| JMH GitHub mirror | https://github.com/openjdk/jmh |

## 6. RECOMMEND

Khi các bẫy chính của `Java Performance — JMH Basics Without Self-Deception` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Allocation profiling | Benchmark object-heavy code | thấy GC pressure rõ hơn |
| Throughput mode | Queue/processing workloads | phù hợp kiểu load khác |
| Realistic fixture setup | So sánh algorithm/use case thật | tránh benchmark toy quá xa production |

## 7. QUIZ

### Quick Check

1. Vì sao `System.nanoTime()` benchmark thường sai với JVM?
2. Warmup giúp gì?
3. Khi nào benchmark không đủ để kết luận tối ưu production?

### Answer Key

1. Vì JIT, dead-code elimination và runtime optimization làm kết quả nhiễu.
2. Nó cho JVM thời gian tối ưu và ổn định execution path.
3. Khi bottleneck thực nằm ở DB, network hoặc workload production phức tạp hơn benchmark.

## 8. NEXT STEPS

- Nối với `performance/profiling` để phối hợp benchmark với profiler
- Hoặc sang `jvm/gc` nếu bottleneck liên quan allocation pressure
