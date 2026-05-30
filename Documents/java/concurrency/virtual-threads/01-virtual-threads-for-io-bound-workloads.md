<!-- tags: java, concurrency -->
# ☕ Java Concurrency — Virtual Threads for IO-Bound Workloads

> Virtual threads thay đổi cách Java xử lý số lượng lớn tác vụ blocking I/O. Bài này tập trung vào mental model, trade-off và khi nào nên dùng chúng thay vì thread pool truyền thống.

📅 Ngày tạo: 2026-03-28 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 15 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Expert |
| **Use case** | HTTP clients, DB calls, high-concurrency blocking IO |
| **Java focus** | virtual threads, blocking style, executor per task |
| **Prerequisites** | executors, completable future, Java concurrency basics |

## 1. DEFINE

Hình dung đội ngũ của bạn vừa thấy virtual threads và nghĩ: cuối cùng cũng có thể giữ code blocking quen thuộc mà không phải trả giá về scale. Một tuần sau, code đúng là đơn giản hơn, nhưng connection pool, downstream latency và shared-state bug vẫn nguyên đó. Virtual threads chỉ có giá trị khi bạn nhìn rõ chúng giải bài nào, và không giải bài nào.

Bài này được viết cho khoảnh khắc phân vân đó. Nó không bán một tính năng mới; nó giúp bạn quyết định xem virtual threads có thực sự là câu trả lời cho hệ thống của mình hay chỉ là một cái tên mới cho kỳ vọng cũ.

### Virtual thread là gì?

Virtual thread là lightweight thread do JVM quản lý, cho phép giữ style code blocking quen thuộc nhưng scale tốt hơn ở workload I/O-bound.

### Actors

| Actor | Vai trò |
| --- | --- |
| Platform thread | OS-backed thread truyền thống |
| Virtual thread | Lightweight execution unit do JVM schedule |
| Blocking operation | I/O call có thể “đậu” virtual thread mà không giữ platform thread lâu |
| Scheduler | Thành phần JVM điều phối virtual threads |

### Invariants

| Quy tắc | Ý nghĩa |
| --- | --- |
| Virtual threads hợp nhất cho blocking IO, không phải magic cho CPU-bound work | Chọn workload đúng |
| Tránh giữ monitor/critical section quá lâu | Dễ tạo contention/pinning |
| Quan sát runtime behavior vẫn cần thiết | Không nên assume “bật lên là xong” |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Kỳ vọng virtual threads giải quyết mọi bottleneck | Dùng sai workload | Giữ CPU-bound work ở mô hình khác |
| Pinning làm mất lợi ích | Block khi đang giữ lock/monitor không phù hợp | Giảm synchronized vùng rộng |
| Thiếu observability | Khó phân tích runtime issues | Kết hợp metrics + profiling |

Các failure mode trên nghe dễ tránh. Nhưng có trap: virtual thread + synchronized block = pinning carrier thread, và ThreadLocal leak trên virtual thread = memory bloat. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa của Java Concurrency — Virtual Threads for IO-Bound Workloads nghe có thể đã đủ rõ, nhưng concurrency chỉ thật sự lộ mặt khi bạn nhìn timing, ownership và điểm nghẽn cùng lúc. Hãy đưa nó về một sơ đồ đủ cụ thể trước.

```text
many IO tasks
   │
   ├── old model -> limited platform thread pool
   └── new model -> one virtual thread per task
```

```text
virtual thread
   │
   ├── runs blocking IO
   ├── yields carrier thread when parked
   └── resumes when IO completes
```

## 3. CODE

Khi timing của Java Concurrency — Virtual Threads for IO-Bound Workloads đã hiện hình, bước tiếp theo là biến nó thành code đủ nhỏ để hiểu nhưng đủ thật để nhìn ra trade-off. Ta đi từ case dễ nhất rồi tăng dần áp lực.

### Basic: start a virtual thread

```java
// VirtualThreadDemo.java — Start one virtual thread for a blocking task
public final class VirtualThreadDemo {
    public static void main(String[] args) throws InterruptedException {
        Thread worker = Thread.ofVirtual().start(() -> {
            System.out.println("running on virtual thread");
        });
        worker.join();
    }
}
```

Virtual thread basics đã cover. Nhưng structured concurrency cần scoping — hãy structure.

### Intermediate: executor per task

```java
// VirtualThreadExecutorDemo.java — Use virtual-thread-per-task executor
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public final class VirtualThreadExecutorDemo {
    public static void main(String[] args) throws Exception {
        try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
            executor.submit(() -> System.out.println("fetch customer profile"));
            executor.submit(() -> System.out.println("fetch loyalty points"));
        }
    }
}
```

Structured concurrency đã cover. Nhưng carrier thread pinning cần detection — hãy monitor.

### Advanced: blocking style orchestration

```java
// DashboardAssembler.java — Keep blocking style while scaling IO tasks
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public final class DashboardAssembler {
    public String assemble() throws InterruptedException, ExecutionException {
        try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
            Future<String> profile = executor.submit(namedTask("profile"));
            Future<String> orders = executor.submit(namedTask("orders"));
            Future<String> loyalty = executor.submit(namedTask("loyalty"));
            return profile.get() + " | " + orders.get() + " | " + loyalty.get();
        }
    }

    private Callable<String> namedTask(String name) {
        return () -> "loaded-" + name;
    }
}
```

Bạn đã đi qua virtual threads, structured concurrency, và pinning. Bây giờ đến phần nguy hiểm: carrier pinning và ThreadLocal leak — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Concurrency — Virtual Threads for IO-Bound Workloads` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Dùng virtual threads cho CPU-bound loops | Giữ CPU-heavy work ở model phù hợp hơn |
| 2 | Tưởng không cần observability nữa | Vẫn đo thread behavior và latency |
| 3 | Giữ synchronized block rộng | Giảm pinning và contention |
| 4 | Mix lung tung với pool cũ mà không đo | Benchmark/profiling trước khi rollout rộng |

Bạn đã đi qua Virtual Threads và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Virtual Threads | https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html |
| JEP 444 | https://openjdk.org/jeps/444 |
| Structured Concurrency context | https://openjdk.org/jeps/453 |

## 6. RECOMMEND

Khi các bẫy chính của `Java Concurrency — Virtual Threads for IO-Bound Workloads` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Structured concurrency | Có nhiều task con thuộc cùng request | Quản lý lifecycle tốt hơn |
| Thread dump analysis | Nghi pinning/contention | Thấy runtime issue rõ hơn |
| HTTP/DB integration review | Service IO-heavy | Chọn nơi rollout virtual threads đúng nhất |

## 7. QUIZ

### Quick Check

1. Virtual threads phù hợp nhất với loại workload nào?
2. Vì sao pinning là vấn đề?
3. `newVirtualThreadPerTaskExecutor()` có lợi gì về mental model?

### Answer Key

1. Blocking I/O workloads nhiều concurrent tasks.
2. Vì nó làm virtual thread giữ platform thread lâu hơn cần thiết.
3. Nó cho phép nghĩ gần như “một task, một thread” mà vẫn scale tốt hơn kiểu cũ.

## 8. NEXT STEPS

- Nối với `expert/observability` để đo runtime behavior sau rollout
- Hoặc sang `spring-security` nếu muốn tiếp tục nhánh backend production
