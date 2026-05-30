<!-- tags: golang -->
# 11 — Singleflight

> **Package**: `golang.org/x/sync/singleflight` — Deduplicate concurrent calls for the same key.

📅 Created: 2026-03-20 · 🔄 Updated: 2026-04-19 · ⏱️ 15 min read

| Aspect         | Detail                                                          |
| -------------- | --------------------------------------------------------------- |
| **Concept**    | Singleflight — N callers, 1 execution, shared result           |
| **Use case**   | Cache miss thundering herd, hot key dedup, API coalesce         |
| **Go stdlib**  | `golang.org/x/sync/singleflight`                                |
| **Key insight**| Reduces N concurrent calls to 1 — prevents thundering herd     |

---

## 1. DEFINE

Cache expires. 500 goroutines hit the same key at the same instant. All 500 fire the same database query. The DB buckles under duplicate load, latency spikes, and the cache stampede cascades into a full outage. `singleflight` collapses those 500 identical in-flight calls into one: only the first goroutine executes; the rest wait and share the result.

Your Redis cache TTL expires. 1,000 requests simultaneously call key "popular-product" → all cache miss → 1,000 identical DB queries running concurrently. DB stutters, latency increases 10x — that is a **cache stampede** (thundering herd). Singleflight solves it: 1,000 callers with the same key, only 1 goroutine actually queries DB, 999 others wait and receive the shared result. But there is a trap: singleflight caches errors too = all callers receive the same error, even after the backend has recovered. `Forget()` solves it — but wrong timing = cache stampede returns. That trap will surface in PITFALLS.

### Definition

**Singleflight** ensures that for 1 key, only **1 function execution** happens at a time. If N goroutines call with the same key → only 1 goroutine executes, N-1 remaining goroutines **wait and receive the same result**.

### Use cases

| Use case              | Problem                                    | Solution                           |
| --------------------- | ------------------------------------------ | ---------------------------------- |
| **Cache stampede**    | Cache expires → 1000 requests query DB     | Singleflight: 1 query, 999 wait   |
| **API deduplication** | Client spams the same API endpoint         | 1 execution, rest share result     |
| **Config reload**     | Multiple goroutines trigger reload         | 1 reload, rest wait                |

### Singleflight vs Cache vs Mutex

| Mechanism        | Purpose                      | Scope                        |
| ---------------- | ---------------------------- | ---------------------------- |
| **Cache**        | Store results for reuse      | Across requests (time-based) |
| **Singleflight** | Deduplicate concurrent calls | Only concurrent (in-flight)  |
| **Mutex**        | Exclusive access to resource | Block all except 1           |

### API

| Method            | Description                                                  |
| ----------------- | ----------------------------------------------------------- |
| `Do(key, fn)`     | Execute fn, deduplicate by key. Return `(val, err, shared)` |
| `DoChan(key, fn)` | Same as Do but returns channel (non-blocking caller)        |
| `Forget(key)`     | Remove key from in-flight → next call will execute fresh     |

### Failure Modes

| Failure               | Cause                                 | Prevention                   |
| --------------------- | ------------------------------------- | ---------------------------- |
| **Error propagation** | 1 goroutine errors → ALL get error    | Retry logic at caller        |
| **Slow function**     | Slow function → ALL wait              | Combine with timeout/context |
| **Stale result**      | Old result shared for new requests    | `Forget(key)` or short TTL   |

Singleflight, deduplication, thundering herd — theory is covered. Let us see what request deduplication looks like visually.

---
## 2. VISUAL

`singleflight` only becomes truly clear when you look at two worlds side by side: duplicate calls and duplicate suppression.

![Duplicate calls vs singleflight](./images/11-singleflight-duplicate-suppression.png)

*This PNG holds the core focus of the article: `singleflight` does not magically make requests faster, it collapses duplicate downstream work to a single in-flight owner.*

### Singleflight — Cache Stampede Prevention

```
  Before (without singleflight):

Cache MISS!
  Request 1 ──▶ Query DB ──────────▶ Result
  Request 2 ──▶ Query DB ──────────▶ Result   ← 1000 queries!
  Request 3 ──▶ Query DB ──────────▶ Result
  ...
  Request 1000 ──▶ Query DB ───────▶ Result

After (with singleflight):

Cache MISS!
  Request 1 ──▶ Query DB ──────────▶ Result ──▶ Share
  Request 2 ──▶ WAIT ─────────────────────────▶ Same Result ← shared!
  Request 3 ──▶ WAIT ─────────────────────────▶ Same Result
  ...
  Request 1000 ──▶ WAIT ──────────────────────▶ Same Result

1 DB query instead of 1000!
```

The diagram gives an overview of the deduplication flow. Now let us implement — starting from cache stampede prevention, then singleflight + cache, then DoChan non-blocking, then 3-layer cache.

---

## 3. CODE

The visual of **Singleflight** gave you the big picture. Code is where decisions about cancellation, ownership, or sequencing turn into real behavior.

---

### Example 1: Basic — Cache Stampede Prevention
> **Goal**: Demonstrate basic cache stampede prevention in the right context so the reader understands why this technique exists.
> **Approach**: Start from a basic example then attach necessary technical decisions instead of jumping straight into hard code.
> **Example**: A job or request passes through multiple goroutines while preserving cancellation, concurrency limits, and clear error handling.
> **Complexity**: O(1) orchestration in application code; real cost depends on data, goroutines, or I/O being demonstrated.

**Goal**: 100 concurrent requests for the same user data. Without singleflight → 100 DB queries. With singleflight → 1 DB query, 99 wait and receive the same result.

**Requirements**: `golang.org/x/sync/singleflight`.

```go
package main

import (
    "fmt"
    "sync"
    "sync/atomic"
    "time"

"golang.org/x/sync/singleflight"
)

var (
    dbQueryCount atomic.Int64 // counts actual DB queries
    group        singleflight.Group
)

// getUserFromDB: simulate DB query (expensive)
func getUserFromDB(userID string) (string, error) {
    dbQueryCount.Add(1)
    fmt.Printf("  📊 [DB] Querying user %s (query #%d)\n", userID, dbQueryCount.Load())
    time.Sleep(200 * time.Millisecond) // simulate DB latency
    return fmt.Sprintf("User{id: %s, name: 'Alice'}", userID), nil
}

// getUser: wrapper with singleflight
func getUser(userID string) (string, error) {
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Do(key, fn):
    // - Key: "user:123" — deduplicate by this key
    // - If a goroutine is already running fn for this key → wait + share result
    // - If not → run fn, result shared with all waiters
    //
    // Return:
    // - val: result from fn
    // - err: error from fn
    // - shared: true if result was shared (not the executor)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    val, err, shared := group.Do("user:"+userID, func() (interface{}, error) {
        return getUserFromDB(userID)
    })
    if err != nil {
        return "", err
    }

if shared {
        fmt.Printf("  ♻️  [Cache] Result shared (not from DB)\n")
    }

return val.(string), nil
}

func main() {
    fmt.Println("=== 100 concurrent requests for same user ===\n")

var wg sync.WaitGroup
    for i := range 100 { // Go 1.22+
        wg.Add(1)
        go func(requestID int) {
            defer wg.Done()
            user, err := getUser("123")
            if err != nil {
                fmt.Printf("Request %d: ❌ %v\n", requestID, err)
                return
            }
            _ = user // use result
        }(i)
    }

wg.Wait()
    fmt.Printf("\n📊 Total DB queries: %d (saved %d queries!)\n",
        dbQueryCount.Load(), 100-dbQueryCount.Load())
}
```

This example is appropriate for grasping the baseline of cache stampede prevention. When you need to handle more edge cases or coordinate additional abstractions, move to the next example.

**Achieved**:

- 100 concurrent requests → only 1-2 DB queries (instead of 100).
- 98-99 requests receive a **shared result** — zero DB load.
- `shared=true` indicates the result was shared from another goroutine.

**Caveats**:

- Singleflight **only deduplicates concurrent calls** — it does NOT cache results.
- After the first goroutine finishes → the key is removed → the next request will execute fresh.
- Combine with cache: `check cache → miss → singleflight → set cache → return`.

Basic singleflight covers deduplication. But production needs singleflight + local cache — a double-check pattern to avoid querying DB when cache already has the data.

---

### Example 2: Intermediate — Singleflight + Cache — Production Pattern
> **Goal**: Demonstrate singleflight + cache — production pattern in the right context so the reader understands why this technique exists.
> **Approach**: Start from an intermediate example then attach necessary technical decisions instead of jumping straight into hard code.
> **Example**: A job or request passes through multiple goroutines while preserving cancellation, concurrency limits, and clear error handling.
> **Complexity**: O(1) orchestration; total complexity depends on the number of coordination steps and related data structures.

**Goal**: The most common pattern: L1 cache → singleflight → DB. Prevents both cache stampede and duplicate queries.

**Requirements**: `singleflight` + simple in-memory cache.

```go
package main

import (
    "fmt"
    "sync"
    "sync/atomic"
    "time"

"golang.org/x/sync/singleflight"
)

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// SimpleCache: in-memory cache with TTL
// Production: use Redis, Memcached, or go-cache
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
type CacheEntry struct {
    Value     string
    ExpiresAt time.Time
}

type Cache struct {
    mu      sync.RWMutex
    entries map[string]CacheEntry
}

func NewCache() *Cache {
    return &Cache{entries: make(map[string]CacheEntry)}
}

func (c *Cache) Get(key string) (string, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    entry, ok := c.entries[key]
    if !ok || time.Now().After(entry.ExpiresAt) {
        return "", false // miss or expired
    }
    return entry.Value, true
}

func (c *Cache) Set(key, value string, ttl time.Duration) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.entries[key] = CacheEntry{Value: value, ExpiresAt: time.Now().Add(ttl)}
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// UserService: cache → singleflight → DB
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
type UserService struct {
    cache *Cache
    group singleflight.Group
    dbHit atomic.Int64
}

func NewUserService() *UserService {
    return &UserService{cache: NewCache()}
}

func (s *UserService) GetUser(userID string) (string, error) {
    cacheKey := "user:" + userID

// ━━━ Layer 1: Check cache ━━━
    if val, ok := s.cache.Get(cacheKey); ok {
        return val, nil // cache HIT — fastest
    }

// ━━━ Layer 2: Singleflight — deduplicate DB queries ━━━
    val, err, _ := s.group.Do(cacheKey, func() (interface{}, error) {
        // Double-check cache (another goroutine may have already set it)
        if val, ok := s.cache.Get(cacheKey); ok {
            return val, nil
        }

// ━━━ Layer 3: Query DB ━━━
        s.dbHit.Add(1)
        time.Sleep(100 * time.Millisecond) // simulate DB
        result := fmt.Sprintf("User{id:%s, name:'Alice'}", userID)

// Set cache for subsequent requests
        s.cache.Set(cacheKey, result, 5*time.Second)

return result, nil
    })
    if err != nil {
        return "", err
    }

return val.(string), nil
}

func main() {
    svc := NewUserService()

fmt.Println("=== Wave 1: 50 concurrent requests (cold cache) ===")
    var wg sync.WaitGroup
    for range 50 { // Go 1.22+
        wg.Add(1)
        go func() {
            defer wg.Done()
            svc.GetUser("123")
        }()
    }
    wg.Wait()
    fmt.Printf("DB hits: %d (singleflight saved %d queries)\n\n", svc.dbHit.Load(), 50-svc.dbHit.Load())

fmt.Println("=== Wave 2: 50 more requests (warm cache) ===")
    for range 50 { // Go 1.22+
        wg.Add(1)
        go func() {
            defer wg.Done()
            svc.GetUser("123")
        }()
    }
    wg.Wait()
    fmt.Printf("DB hits: %d (cache hit for wave 2)\n", svc.dbHit.Load())
}
```

This level starts being useful for real code because it coordinates multiple techniques. The caveat is to keep the API compact so the reader does not lose track of reasoning.

**Achieved**:

- Wave 1 (cold cache): 50 requests → 1 DB query → set cache.
- Wave 2 (warm cache): 50 requests → 0 DB queries (cache hit).
- 100 total requests → only 1 DB query.

**Caveats**:

- **Double-check cache** inside the singleflight fn — avoids querying DB if another goroutine already set the cache.
- Pattern: `cache.Get → singleflight.Do → cache.Get (double-check) → DB → cache.Set`.
- TTL should be **short** (5-30s) for frequently changing data.

> **Why double-check cache inside singleflight.Do?**
> Between the caller checking cache (miss) and singleflight.Do starting to run, another goroutine may have already populated the cache. Double-check avoids redundant DB queries. This is the double-checked locking pattern — familiar in Java/C++, in Go implemented via singleflight.

Singleflight + cache covers production. But when you need per-caller timeout (each caller has its own deadline) — DoChan non-blocking + select is the solution.

---

### Example 3: Advanced — DoChan — Non-blocking with timeout
> **Goal**: Demonstrate DoChan — non-blocking with timeout in the right context so the reader understands why this technique exists.
> **Approach**: Start from an advanced example then attach necessary technical decisions instead of jumping straight into hard code.
> **Example**: A job or request passes through multiple goroutines while preserving cancellation, concurrency limits, and clear error handling.
> **Complexity**: O(1) orchestration at the example layer; real complexity lies in concurrency, memory, and integration underneath.

**Goal**: `DoChan` returns a channel instead of blocking — combine with `select` for timeout control.

```go
package main

import (
    "fmt"
    "time"

"golang.org/x/sync/singleflight"
)

func main() {
    var group singleflight.Group

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // DoChan: returns <-chan Result instead of blocking
    // Combine with select for timeout
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ch := group.DoChan("slow-query", func() (interface{}, error) {
        time.Sleep(2 * time.Second) // simulate slow query
        return "result from DB", nil
    })

// ━━━ Select: result vs timeout ━━━
    select {
    case result := <-ch:
        if result.Err != nil {
            fmt.Println("❌ Error:", result.Err)
        } else {
            fmt.Printf("✅ Got: %v (shared: %v)\n", result.Val, result.Shared)
        }
    case <-time.After(1 * time.Second):
        fmt.Println("⏱️ Timeout! Falling back to default value")
        // Forget key so the next request can execute fresh
        group.Forget("slow-query")
    }
}
```

This is the closest to production level in this article. Only keep this complexity when the trade-off yields clear benefits in correctness, throughput, or maintainability.

**Achieved**:

- Slow query (2s) but timeout is 1s → fallback.
- `Forget("slow-query")` removes the key → next request can retry.

**Caveats**:

- `DoChan` + `select` = timeout control for singleflight.
- `Forget(key)` is important: without forget, subsequent requests still wait for the old goroutine.
- The old goroutine **still runs** after timeout — only the result is discarded (similar to context cancel).

> **Why DoChan instead of Do when timeout is needed?**
> `Do()` is blocking — the caller cannot timeout independently. `DoChan()` returns a channel → the caller uses `select` with `time.After` or `ctx.Done()`. If timeout: the caller walks away, but the executing goroutine still runs and populates cache — the next request benefits.

DoChan covers per-caller timeout. Combining memory → Redis → DB 3-layer cache = production-grade caching system.

---

### Example 4: Expert — Singleflight + Redis + GORM — Production 3-Layer Cache
> **Goal**: Demonstrate singleflight + Redis + GORM — production 3-layer cache in the right context so the reader understands why this technique exists.
> **Approach**: Start from an expert example then attach necessary technical decisions instead of jumping straight into hard code.
> **Example**: A job or request passes through multiple goroutines while preserving cancellation, concurrency limits, and clear error handling.
> **Complexity**: O(1) orchestration at the application layer; the hard parts lie in reliability, scale, and operations.

**Goal**: Complete production pattern: Redis cache (L1) → singleflight (dedup) → GORM query (DB). Combining 3 techniques: caching, deduplication, and ORM. Common in high-traffic API servers.

**Requirements**: `golang.org/x/sync/singleflight`, `github.com/redis/go-redis/v9`, `gorm.io/gorm`.

**Components**: Product API — GET `/products/:id` receiving thousands of requests/second. Redis cache with 30s TTL, singleflight deduplicate, GORM query PostgreSQL.

```go
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "log"
    "time"

"github.com/redis/go-redis/v9"
    "golang.org/x/sync/singleflight"
    "gorm.io/driver/postgres"
    "gorm.io/gorm"
)

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// GORM Model
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
type Product struct {
    ID          uint      `gorm:"primarykey" json:"id"`
    Name        string    `gorm:"column:name" json:"name"`
    Price       float64   `gorm:"column:price" json:"price"`
    Category    string    `gorm:"column:category;index" json:"category"`
    Stock       int       `gorm:"column:stock" json:"stock"`
    UpdatedAt   time.Time `json:"updated_at"`
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// ProductService: 3-layer lookup
//   Layer 1: Redis cache (fast, 30s TTL)
//   Layer 2: Singleflight (dedup concurrent DB calls)
//   Layer 3: GORM → PostgreSQL (source of truth)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
type ProductService struct {
    db    *gorm.DB
    rdb   *redis.Client
    group singleflight.Group
}

func NewProductService(db *gorm.DB, rdb *redis.Client) *ProductService {
    return &ProductService{db: db, rdb: rdb}
}

func (s *ProductService) GetProduct(ctx context.Context, productID uint) (*Product, error) {
    cacheKey := fmt.Sprintf("product:%d", productID)

// ━━━ Layer 1: Redis Cache ━━━
    // Redis GET: ~0.5ms vs DB query ~5-50ms
    cached, err := s.rdb.Get(ctx, cacheKey).Bytes()
    if err == nil {
        var product Product
        if json.Unmarshal(cached, &product) == nil {
            log.Printf("[Redis HIT] product:%d", productID)
            return &product, nil
        }
    }
    // Redis MISS or unmarshal fail → continue

// ━━━ Layer 2: Singleflight — deduplicate concurrent DB queries ━━━
    // 1000 requests for the same product → only 1 DB query
    val, err, shared := s.group.Do(cacheKey, func() (interface{}, error) {
        // Double-check Redis (another goroutine may have already set it)
        if cached, err := s.rdb.Get(ctx, cacheKey).Bytes(); err == nil {
            var product Product
            if json.Unmarshal(cached, &product) == nil {
                return &product, nil
            }
        }

// ━━━ Layer 3: GORM → PostgreSQL ━━━
        var product Product
        if err := s.db.WithContext(ctx).First(&product, productID).Error; err != nil {
            return nil, fmt.Errorf("product %d not found: %w", productID, err)
        }
        log.Printf("[DB QUERY] product:%d (name=%s, price=%.2f)", productID, product.Name, product.Price)

// Set Redis cache — async (does not block response)
        go func() {
            data, _ := json.Marshal(product)
            if err := s.rdb.Set(context.Background(), cacheKey, data, 30*time.Second).Err(); err != nil {
                log.Printf("[Redis SET Error] %v", err)
            }
        }()

return &product, nil
    })

if err != nil {
        return nil, err
    }

if shared {
        log.Printf("[Singleflight SHARED] product:%d — result from another goroutine", productID)
    }

return val.(*Product), nil
}

// InvalidateCache: called when product is updated
func (s *ProductService) InvalidateCache(ctx context.Context, productID uint) {
    cacheKey := fmt.Sprintf("product:%d", productID)
    s.rdb.Del(ctx, cacheKey)
    s.group.Forget(cacheKey) // ← clear singleflight so a fresh query runs
}

func main() {
    // Setup GORM
    dsn := "host=localhost user=app dbname=shop port=5432 sslmode=disable"
    db, _ := gorm.Open(postgres.Open(dsn), &gorm.Config{})
    db.AutoMigrate(&Product{})

// Setup Redis
    rdb := redis.NewClient(&redis.Options{Addr: "localhost:6379"})

svc := NewProductService(db, rdb)

ctx := context.Background()

// Simulate: 100 concurrent requests for product #42
    // Expected: 1 DB query, 1 Redis SET, 99 singleflight shares, then cache hit
    for range 100 { // Go 1.22+
        go func() {
            product, err := svc.GetProduct(ctx, 42)
            if err != nil {
                log.Printf("❌ %v", err)
                return
            }
            _ = product
        }()
    }

time.Sleep(2 * time.Second)
}
```

This level is only appropriate when the team is already comfortable with the abstractions and related libraries. If there is no corresponding operational need, a simpler version is usually better.

**Achieved**:

- **3 layers**: Redis (~0.5ms) → singleflight (0ms, shared) → DB (~5-50ms).
- **100 concurrent requests → 1 DB query**, 1 Redis SET, 99 shared results.
- After cache warm: all requests served from Redis (~0.5ms).
- **Cache invalidation**: `InvalidateCache()` clears both Redis + singleflight.

**Caveats**:

- **Async Redis SET**: `go func()` sets cache — does not block response. If it fails → next request queries DB again.
- **Double-check** inside singleflight — avoids DB query if another goroutine already set Redis.
- **`Forget(key)`** is critical when invalidating — without it, subsequent requests wait for the old (now stale) goroutine.
- **Redis TTL 30s** is a trade-off. Shorter → fresher data. Longer → fewer DB queries. Tune per use case.
- Comparison: `patrickmn/go-cache` for in-process cache (single instance), Redis for multi-instance.

> **Why 3-layer (memory → Redis → DB) instead of just Redis → DB?**
> Redis roundtrip ~0.5-1ms. In-memory ~10ns. For hot keys (10K+ reads/s), memory cache reduces 99% of Redis calls. Singleflight at the Redis layer prevents thundering herd when memory cache misses. 3 layers = optimal latency + DB protection + cache coherency.

You now know stampede prevention, cache pattern, DoChan, and 3-layer cache. Here comes the dangerous part: cached errors and Forget timing — traps set up from the beginning of this article.

---

## 4. PITFALLS

From here on, with **Singleflight**, the focus is no longer making it work, but avoiding the kinds of runs that seem fine but silently create operational debt.

| # | Severity | Mistake | Consequence | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Fatal | **Error shared** | 1 goroutine errors → all get error | Retry at caller |
| 2 | 🟡 Common | **Not caching result** | Singleflight only deduplicates, does NOT cache | Combine with cache |
| 3 | 🟡 Common | **Slow fn blocks all** | Slow function → N goroutines wait | DoChan + timeout |
| 4 | 🔵 Minor | **Stale after Forget** | Forget called but goroutines still waiting | Use DoChan + select |

You have covered stampede, cache, DoChan, 3-layer, and the error-cache/Forget traps. The resources below help you go deeper.

---

## 5. REF

| Resource | Type | Link | Notes |
| --- | --- | --- | --- |
| singleflight package | Official docs | [pkg.go.dev/golang.org/x/sync/singleflight](https://pkg.go.dev/golang.org/x/sync/singleflight) | Core API |
| Preventing thundering herds | Blog | [calhoun.io](https://www.calhoun.io/using-singleflight-to-deduplicate-requests/) | Practical guide |

---

## 6. RECOMMEND

The most important point of **Singleflight** is clear. The extensions below are for when you need to turn this understanding into a more complete investigation or operations workflow.

| Next step | When | Reason | File/Link |
| --- | --- | --- | --- |
| **patrickmn/go-cache / Redis** | L1 Cache | Time-based cache — combine with singleflight | `patrickmn/go-cache` |
| **Singleflight + GORM** | GORM cache | Deduplicate concurrent DB reads | [orm/03](../orm/03-querying.md) |
| **Singleflight + gRPC** | gRPC | Deduplicate concurrent RPC calls | Pattern |
| **singleflight + ResponseWriter** | HTTP cache | Cache HTTP responses for same-key requests | Pattern |
| **Redis SETNX + channel** | Distributed | Cross-process singleflight | External stores |
| **Prometheus counter** | Monitoring | Measure deduplication effectiveness | `shared_results` metric |
