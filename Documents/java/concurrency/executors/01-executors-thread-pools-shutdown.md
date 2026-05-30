<!-- tags: java, concurrency -->
# ☕ Java Concurrency — Executors, Thread Pools & Shutdown

> Sau khi hiểu race condition, bước tiếp theo là quản lý concurrency bằng executor thay vì tự tạo thread bừa bãi. Bài này tập trung vào pool sizing, task submission và shutdown an toàn.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 15 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Intermediate |
| **Use case** | Background task, bounded concurrency, scheduled jobs |
| **Java focus** | `ExecutorService`, fixed pool, scheduled executor, shutdown |
| **Prerequisites** | Concurrency basics |

## 1. DEFINE

Hình dung một service Java chạy ổn nhiều tuần, rồi dưới tải thật queue bắt đầu dài ra, active thread chạm trần và shutdown thì treo lơ lửng mỗi lần deploy. Executor lúc đó không còn là utility class để “quăng việc vào”. Nó là nơi throughput, latency và khả năng dừng hệ thống va vào nhau trực diện.

Bài này đặt `Java Concurrency — Executors, Thread Pools & Shutdown` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Vì sao nên dùng executor?

Tạo `new Thread(...)` thủ công cho từng task có 3 vấn đề:

- không có chiến lược giới hạn concurrency rõ ràng
- lifecycle shutdown khó kiểm soát
- khó đo và tối ưu khi load tăng

`ExecutorService` giải quyết bằng cách:

- tái sử dụng worker threads
- giới hạn số task chạy song song
- tách phần submit task khỏi phần quản lý execution

### Actors

| Actor | Vai trò |
| --- | --- |
| `ExecutorService` | Chạy và quản lý task pool |
| Worker thread | Thực thi task bên trong pool |
| Task | `Runnable` hoặc `Callable` |
| Shutdown policy | Đảm bảo app dừng gọn, không bỏ dở state |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Thread explosion | Tạo thread thủ công theo mỗi request/job | Dùng pool có giới hạn |
| App không thoát | Quên shutdown executor | Gọi `shutdown()` và `awaitTermination()` |
| Queue phình không kiểm soát | Submit quá nhiều task | Bounded queue hoặc policy rõ ràng |

Các failure mode trên nghe quen. Nhưng có trap: fixed pool quá nhỏ = task starvation, và không call shutdown = JVM treo. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa của Java Concurrency — Executors, Thread Pools & Shutdown nghe có thể đã đủ rõ, nhưng concurrency chỉ thật sự lộ mặt khi bạn nhìn timing, ownership và điểm nghẽn cùng lúc. Hãy đưa nó về một sơ đồ đủ cụ thể trước.

```text
incoming tasks
    │
    ▼
ExecutorService
    │
    ├── worker-1 ──▶ task
    ├── worker-2 ──▶ task
    └── worker-3 ──▶ task
```

```text
submit tasks
   │
   ▼
queue / pool
   │
   ▼
shutdown requested
   │
   ├── stop accepting new tasks
   ├── finish running tasks
   └── terminate cleanly
```

## 3. CODE

Khi timing của Java Concurrency — Executors, Thread Pools & Shutdown đã hiện hình, bước tiếp theo là biến nó thành code đủ nhỏ để hiểu nhưng đủ thật để nhìn ra trade-off. Ta đi từ case dễ nhất rồi tăng dần áp lực.

### Basic: fixed thread pool

```java
// ReportJobExecutor.java — Fixed pool for bounded background jobs
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public final class ReportJobExecutor {
    private final ExecutorService executorService = Executors.newFixedThreadPool(4);

    public void submit(String reportId) {
        executorService.submit(() -> {
            System.out.println("processing report " + reportId);
        });
    }
}
```

Basic executors đã cover. Nhưng custom pool cần ThreadPoolExecutor — hãy tune.

### Intermediate: scheduled executor

```java
// MetricsPublisher.java — Periodic publishing with scheduled executor
import java.time.Instant;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public final class MetricsPublisher {
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);

    public void start() {
        scheduler.scheduleAtFixedRate(() -> {
            System.out.println("publishing metrics at " + Instant.now());
        }, 0, 30, TimeUnit.SECONDS);
    }
}
```

Custom pool đã cover. Nhưng scheduled executor cần cron-like — hãy schedule.

### Advanced: graceful shutdown

```java
// ExecutorShutdownSupport.java — Graceful executor shutdown helper
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;

public final class ExecutorShutdownSupport {
    private ExecutorShutdownSupport() {
    }

    /**
     * Shuts down an executor gracefully and escalates when timeout is exceeded.
     *
     * @param executorService target executor
     * @throws InterruptedException when current thread is interrupted
     */
    public static void shutdownGracefully(ExecutorService executorService) throws InterruptedException {
        executorService.shutdown();
        if (!executorService.awaitTermination(10, TimeUnit.SECONDS)) {
            executorService.shutdownNow();
        }
    }
}
```

Bạn đã đi qua executors, pools, và scheduling. Bây giờ đến phần nguy hiểm: pool starvation và missing shutdown — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Concurrency — Executors, Thread Pools & Shutdown` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | `new Thread()` cho mọi task | Dùng `ExecutorService` |
| 2 | Không shutdown pool khi app dừng | Thêm shutdown hook/lifecycle callback |
| 3 | Pool size chọn tùy hứng | Cân theo workload CPU-bound hay IO-bound |
| 4 | Submit task vô hạn không backpressure | Dùng queue/policy có giới hạn |

Bạn đã đi qua Executors và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| ExecutorService | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ExecutorService.html |
| ScheduledExecutorService | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ScheduledExecutorService.html |
| Concurrency Tutorial | https://docs.oracle.com/javase/tutorial/essential/concurrency/executors.html |

## 6. RECOMMEND

Khi các bẫy chính của `Java Concurrency — Executors, Thread Pools & Shutdown` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| `CompletableFuture` | Cần compose async flows | Phù hợp orchestration tốt hơn |
| Virtual threads | IO-heavy workloads | Scale đồng thời tốt hơn với Java mới |
| Micrometer metrics | Cần đo queue/pool utilization | Quan sát production rõ hơn |

## 7. QUIZ

### Quick Check

1. Vì sao `ExecutorService` tốt hơn `new Thread()` cho task lặp lại?
2. Khi nào `shutdownNow()` mới nên được cân nhắc?
3. Pool size nên dựa vào điều gì?

### Answer Key

1. Vì nó quản lý lifecycle, reuse worker và bounded concurrency tốt hơn.
2. Khi graceful shutdown vượt timeout hoặc cần dừng khẩn cấp.
3. Dựa vào loại workload và năng lực tài nguyên, không chọn ngẫu nhiên.

## 8. NEXT STEPS

- Đi tiếp sang `completable-future/` để học orchestration async
- Hoặc qua `spring-boot/actuator` để quan sát runtime health tốt hơn
