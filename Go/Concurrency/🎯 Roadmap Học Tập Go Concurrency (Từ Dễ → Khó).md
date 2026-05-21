

Mình đã tổ chức lại và bổ sung đầy đủ các patterns cho bạn. Đây là lộ trình học:

#### **LEVEL 1: Foundation (1-5)**

Học trước khi code bất kỳ concurrent system nào:

1. **Goroutines cơ bản** - Hiểu cách Go spawn lightweight threads
2. [**Unbuffered Channels**](./go-channels-guide.html) - Synchronous communication (blocking)
3. [**Buffered Channels**](./go-channels-guide.html) - Asynchronous với capacity
4. **Race Conditions** - Tại sao cần synchronization (chạy với `-race` flag)
5. [**Mutex & RWMutex**](./mutex-and-confinement.html) - Bảo vệ shared memory

🔥 **So sánh với Node.js**: Goroutines ≈ async/await nhưng truly concurrent, channels ≈ EventEmitter nhưng type-safe

#### **LEVEL 2: Intermediate Patterns (6-10)**

Patterns thực tế cho production:

6. [**WaitGroup**](./wait-group.html) - Chờ nhóm goroutines (như `Promise.all()`)
7. [**Context**](./context.html) - Cancellation, timeout, request-scoped values (giống AbortController)
8. [**Select Statement**](./select-statement.html) - Multiplexing channels (unique trong Go)
9. **Or-Done Pattern** - Kết hợp context với channel cleanup
10. **Pipeline Pattern** - Chain processing stages (như Stream API)

#### **LEVEL 3: Advanced Patterns (11-15)**

Scale và optimize:

11. **Fan-Out/Fan-In** - Distribute work + merge results
12. **Worker Pool** - Fixed workers cho load balancing (như BullMQ trong Node)
13. **Tunny Worker Pool** - Production-ready pool với library
14. **Tee Channel** - Duplicate stream cho nhiều consumers
15. **ErrorGroup** - Coordinated error handling (`golang.org/x/sync/errgroup`)

#### **LEVEL 4: Optimization & Resource Management (16-20)**

Performance tuning:

16. **sync.Pool & Buffer Pool** - Object reuse, giảm GC pressure
17. **Resource Manager** - Quản lý connections, file handles
18. **Rate Limiting** - Token bucket, leaky bucket patterns
19. **Semaphore** - Limit concurrent operations (`golang.org/x/sync/semaphore`)
20. **Bounded Parallelism** - Control parallelism level với errgroup

#### **BONUS: Production Patterns (21-22)**

21. **Circuit Breaker** - Fail fast cho external services
22. **Retry with Backoff** - Exponential backoff cho failed operations

---

### 💡 Best Practices Từ Background Node.js Của Bạn

#### So Sánh Patterns:

|Node.js/NestJS|Go Equivalent|
|---|---|
|`Promise.all()`|`sync.WaitGroup`|
|`Promise.race()`|`select` statement|
|`AbortController`|`context.Context`|
|BullMQ/Redis Queue|Worker Pool + Channels|
|EventEmitter|Channels|
|Clustering|Goroutines (built-in)|

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
4. **Tuần 5**: Optimization (16-20) - Profile với `pprof`, optimize allocations
5. **Bonus**: Áp dụng vào refactor NestJS service → Go service
