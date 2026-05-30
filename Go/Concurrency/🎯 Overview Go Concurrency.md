#### **LEVEL 1: Foundation (1-5)**

Học trước khi code bất kỳ concurrent system nào:

1. [**Goroutines cơ bản**](./01-goroutines-guide.html) - Hiểu cách Go spawn lightweight threads
2. [**Buffered - Unbuffered- Channels**](./02-buffered-unbuffered-channels.html) - Synchronous communication (blocking) - Asynchronous với capacity
3. [**Race Conditions**](./03-race-conditions.html) - Tại sao cần synchronization (chạy với `-race` flag)
4. [**Mutex & RWMutex**](./04-mutex-and-confinement.html) - Bảo vệ shared memory

🔥 **So sánh với Node.js**: Goroutines ≈ async/await nhưng truly concurrent, channels ≈ EventEmitter nhưng type-safe

#### **LEVEL 2: Intermediate Patterns (6-10)**

Patterns thực tế cho production:

6. [**WaitGroup**](./06-wait-group.html) - Chờ nhóm goroutines (như `Promise.all()`)
7. [**Context**](./07-context.html) - Cancellation, timeout, request-scoped values (giống AbortController)
8. [**Select Statement**](./08-select-statement.html) - Multiplexing channels (unique trong Go)
9. [**Or-Done Pattern**](./09-or-done-pattern.html) - Kết hợp context với channel cleanup
10. [**Pipeline Pattern**](./10-pipeline-pattern.html) - Chain processing stages (như Stream API)

#### **LEVEL 3: Advanced Patterns (11-15)**

Scale và optimize:

11. [**Fan-Out/Fan-In**](./11-fan-out-fan-in-go.html) - Distribute work + merge results
12. [**Worker Pool**](./12-worker-pool.html) - Fixed workers cho load balancing (như BullMQ trong Node)
13. [**Tunny Worker Pool**](./13-tunny-worker-pool.html) - Production-ready pool với library
14. [**Tee Channel**](./14-tee-channel-go-pattern.html) - Duplicate stream cho nhiều consumers
15. [**ErrorGroup**](./15-errgroup-guide.html) - Coordinated error handling (`golang.org/x/sync/errgroup`)

#### **LEVEL 4: Optimization & Resource Management (16-24)**

Performance tuning:

16. [**sync.Pool & Buffer Pool**](./16-sync-pool.html) - Object reuse, giảm GC pressure
17. [**Resource Manager**](./17-resource-manager.html) - Quản lý connections, file handles
18. [**Rate Limiting**](./18-rate-limiting-go.html) - Token bucket, leaky bucket patterns
19. [**Semaphore**](./19-semaphore-guide.html) - Limit concurrent operations (`golang.org/x/sync/semaphore`)
20. [**Bounded Parallelism**](./20-bounded-parallelism-errgroup.html) - Control parallelism level với errgroup
21. [**Asynq**](./21-asynq.html) - Background job queue với Redis
22. [**Singleflight**](./22-singleflight-guide.html) - Gộp các in-flight requests trùng lặp, chống thundering herd
23. [**Ants Goroutine Pool**](./23-ants-pool-guide.html) - Bể chứa goroutine hiệu năng cao, giảm GC allocations
24. [**Structured Concurrency với Conc**](./24-conc-structured-concurrency.html) - Lập trình song song an toàn kiểu tĩnh (Generics) và an toàn lỗi (Panic safety)

#### **BONUS: Production Patterns (25-26)**

25. **Circuit Breaker** - Fail fast cho external services
26. **Retry with Backoff** - Exponential backoff cho failed operations

---

### 💡 Best Practices Từ Background Node.js Của Bạn

#### So Sánh Patterns:

| Node.js/NestJS     | Go Equivalent          |
| ------------------ | ---------------------- |
| `Promise.all()`    | `sync.WaitGroup`       |
| `Promise.race()`   | `select` statement     |
| `AbortController`  | `context.Context`      |
| BullMQ/Redis Queue | Worker Pool + Channels |
| EventEmitter       | Channels               |
| Clustering         | Goroutines (built-in)  |

#### Lưu Ý Quan Trọng:

1. **Không có shared memory mặc định**: Dùng channels hoặc mutex, tránh shared state
2. **"Share memory by communicating"**: Prefer channels over locks khi có thể
3. **Context propagation**: Pass context qua tất cả I/O operations
4. **Buffer size matters**: Unbuffered = blocking, buffered = performance vs memory tradeoff
5. **`defer` is your friend**: Cleanup với `defer mu.Unlock()`, `defer cancel()`

---

### 🚀 Gợi Ý Học Tập

1. **Tuần 1-2**: Foundation (1-5) - Chạy code với `-race` flag
2. **Tuần 3**: Intermediate (6-10) - Build mini pipeline processor
3. **Tuần 4**: Advanced (11-15) - Implement worker pool cho CPU-intensive tasks
4. **Tuần 5**: Optimization (16-21) - Profile với `pprof`, optimize allocations
5. **Bonus**: Áp dụng vào refactor NestJS service → Go service
