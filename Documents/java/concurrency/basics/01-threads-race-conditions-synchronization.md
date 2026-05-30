<!-- tags: java, concurrency -->
# ☕ Java Concurrency — Threads, Race Conditions & Synchronization

> Bài mở đầu để hiểu concurrency trong Java không phải chỉ là “chạy nhiều thread”, mà là kiểm soát shared state, lifecycle và visibility giữa các luồng thực thi.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 15 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Intermediate |
| **Use case** | Background jobs, async processing, thread-safe state |
| **Java focus** | thread, race condition, `synchronized`, `AtomicInteger` |
| **Prerequisites** | Java basics, collections |

## 1. DEFINE

Hình dung một đoạn code Java rất ngắn vừa được đưa vào worker chạy song song. Test local pass, log cũng không kêu gì, nhưng thỉnh thoảng counter sai, state cập nhật thiếu hoặc một bug chỉ xuất hiện khi tải tăng. Đó là lúc concurrency basics không còn là bài nhập môn. Nó trở thành cách gọi đúng tên thứ đang làm hệ thống của bạn mất tính quyết định.

Bài này đặt `Java Concurrency — Threads, Race Conditions & Synchronization` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Race condition là gì?

Race condition xảy ra khi nhiều thread cùng đọc/ghi shared state mà không có coordination phù hợp, dẫn đến kết quả không xác định.

### Actors

| Actor | Vai trò |
| --- | --- |
| Thread | Đơn vị thực thi độc lập |
| Shared state | Dữ liệu nhiều thread cùng truy cập |
| Lock / synchronization | Cơ chế bảo vệ critical section |
| Atomic primitive | Cơ chế cập nhật thread-safe cho một số phép toán đơn giản |

### Invariants

| Quy tắc | Ý nghĩa |
| --- | --- |
| Shared mutable state là nguồn rủi ro chính | Càng ít state dùng chung càng tốt |
| Synchronization phải bọc đúng critical section | Không chỉ “có lock” là đủ |
| Visibility giữa thread quan trọng như atomicity | Thread khác phải thấy state mới đúng lúc |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Lost update | Hai thread ghi đè nhau | Dùng lock hoặc atomic primitive |
| Data visibility bug | Thread không thấy state mới | Dùng synchronization/volatile đúng chỗ |
| Thread leak | Tạo thread thủ công thiếu lifecycle control | Ưu tiên executors ở bước sau |

Các failure mode trên nghe cơ bản. Nhưng có trap: synchronized block trên wrong monitor = data race vẫn xảy ra, và volatile không đảm bảo atomicity cho compound operations. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa của Java Concurrency — Threads, Race Conditions & Synchronization nghe có thể đã đủ rõ, nhưng concurrency chỉ thật sự lộ mặt khi bạn nhìn timing, ownership và điểm nghẽn cùng lúc. Hãy đưa nó về một sơ đồ đủ cụ thể trước.

```text
Thread A           Shared counter           Thread B
   │                     0                     │
   ├── read 0                                  ┤
   ├── +1                                      ┤
   └── write 1                                 ┤
                         ▲                     │
                         └──── read 0, write 1 ┘

Expected: 2
Actual:   1
```

```text
unsafe shared state  ──▶ race
critical section     ──▶ synchronize
single numeric state ──▶ atomic primitive
```

## 3. CODE

Khi timing của Java Concurrency — Threads, Race Conditions & Synchronization đã hiện hình, bước tiếp theo là biến nó thành code đủ nhỏ để hiểu nhưng đủ thật để nhìn ra trade-off. Ta đi từ case dễ nhất rồi tăng dần áp lực.

### Basic: race condition demo

```java
// UnsafeCounterDemo.java — Shared mutable state without synchronization
public final class UnsafeCounterDemo {
    private int counter = 0;

    public void increment() {
        counter++;
    }

    public int counter() {
        return counter;
    }

    public static void main(String[] args) throws InterruptedException {
        UnsafeCounterDemo demo = new UnsafeCounterDemo();

        Thread first = new Thread(() -> runIncrements(demo));
        Thread second = new Thread(() -> runIncrements(demo));

        first.start();
        second.start();
        first.join();
        second.join();

        System.out.println("counter = " + demo.counter());
    }

    private static void runIncrements(UnsafeCounterDemo demo) {
        for (int i = 0; i < 10_000; i++) {
            demo.increment();
        }
    }
}
```

Thread basics đã cover. Nhưng race conditions cần synchronization — hãy lock.

### Intermediate: `synchronized` critical section

```java
// SynchronizedCounterDemo.java — Synchronize writes to shared state
public final class SynchronizedCounterDemo {
    private int counter = 0;

    public synchronized void increment() {
        counter++;
    }

    public synchronized int counter() {
        return counter;
    }
}
```

Synchronized đã cover. Nhưng Lock API cần fine-grained control — hãy upgrade.

### Advanced: atomic primitive for simple counters

```java
// AtomicCounterDemo.java — AtomicInteger avoids lost updates for simple increments
import java.util.concurrent.atomic.AtomicInteger;

public final class AtomicCounterDemo {
    private final AtomicInteger counter = new AtomicInteger();

    /**
     * Increments the counter atomically.
     *
     * @return updated value
     */
    public int increment() {
        return counter.incrementAndGet();
    }

    public int counter() {
        return counter.get();
    }
}
```

Bạn đã đi qua threads, synchronization, và Lock API. Bây giờ đến phần nguy hiểm: wrong monitor và volatile misuse — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Concurrency — Threads, Race Conditions & Synchronization` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Tưởng `counter++` là atomic | Dùng `synchronized` hoặc `AtomicInteger` |
| 2 | Tạo quá nhiều thread thủ công | Chuyển sang executor trong bước tiếp |
| 3 | Lock quá rộng | Chỉ bọc critical section |
| 4 | Giữ shared mutable state không cần thiết | Ưu tiên immutable data hoặc message passing |

Bạn đã đi qua Concurrency Basics và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| Java Concurrency Tutorial | https://docs.oracle.com/javase/tutorial/essential/concurrency/ |
| AtomicInteger | https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/AtomicInteger.html |
| Synchronized Methods | https://docs.oracle.com/javase/tutorial/essential/concurrency/syncmeth.html |

## 6. RECOMMEND

Khi các bẫy chính của `Java Concurrency — Threads, Race Conditions & Synchronization` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Executors | Cần quản lý thread lifecycle | Tốt hơn tạo thread thủ công |
| Locks | Cần control chi tiết hơn `synchronized` | Hữu ích cho trường hợp phức tạp |
| Concurrent collections | Nhiều thread chia sẻ data structure | Tránh reinvent locking |

## 7. QUIZ

### Quick Check

1. Vì sao `counter++` không an toàn khi nhiều thread cùng gọi?
2. Khi nào `AtomicInteger` phù hợp hơn `synchronized`?
3. Shared mutable state gây rủi ro gì chính?

### Answer Key

1. Vì đó là chuỗi read-modify-write, không phải một thao tác atomic.
2. Khi chỉ cần thao tác đơn giản trên một giá trị số và muốn thread-safe nhẹ hơn.
3. Race condition và visibility bugs giữa các thread.

## 8. NEXT STEPS

- Đi tiếp sang `executors/` để quản lý lifecycle tốt hơn
- Sau đó học `completable-future/` nếu cần async composition
