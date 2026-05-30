<!-- tags: golang, export, overview -->
# CSV Export

> Stream tabular data directly to the HTTP response using `encoding/csv` — without loading the entire result set into memory.

📅 Created: 2026-04-05 · 🔄 Updated: 2026-04-14 · ⏱️ 6 min read

---

## 1. DEFINE

CSV is the simplest export format: predictable columns, plain text, and minimal overhead. The danger lies in buffering millions of rows into `[][]string` before writing. **CSV Export** teaches streaming writes that keep memory constant regardless of row count.

> *Serializing a million-row query into a `[][]string` slice before writing the response crashes the container.*

### 1.1 Signals & Boundaries

- Open this lane when the output is flat tabular data with predictable column definitions.
- CSV streams deliver directly over HTTP — no background queue required for moderate datasets.
- For datasets exceeding HTTP timeout limits, combine CSV streaming with background jobs.

### 1.2 Learning Lanes

- `CSV Stream Writer & HTTP Download` — chunked writes, `Flush()` timing, and download headers.
- `Go Programming` — `encoding/csv` internals, byte-order marks, and `io.Writer` composition.

## 2. VISUAL

![CSV Export](../images/csv-router-map.png)

*Figure: CSV export splits into three phases: set HTTP headers, fetch rows in chunks, and write + flush each chunk.*

### Level 1

```text
HTTP Request
-> Set CSV Content-Type Headers
-> Fetch Database Rows (Chunked)
-> Write CSV Row + Flush
```

*Figure: Chunked fetch-write-flush loops prevent memory accumulation.*

## 3. CODE

### Example 1: Router artifact — choosing the CSV lane

> **Goal**: Route to the CSV streaming doc by intent.
> **Approach**: Simple switch on the goal string.
> **Complexity**: O(1)

```go
func chooseLane(goal string) string {
    switch goal {
    case "csv stream writer http download":
        // Route to the streaming CSV download doc.
        return "./01-csv-stream-writer-http-download.md"
    default:
        return "./README.md"
    }
}
```

> **Why call `Flush()` manually?**
> Go's `csv.Writer` buffers output internally. Without explicit `Flush()` calls, the HTTP connection may timeout before the client receives any bytes. Flushing after each chunk keeps the TCP connection alive.

## 4. PITFALLS

| # | Severity | Defect | Fix |
|---|----------|--------|-----|
| 1 | 🔴 Fatal | Buffering all rows into `[][]string` before writing | Use `csv.Writer` with a database cursor, writing row-by-row |
| 2 | 🔴 Fatal | No `Flush()` calls during long exports | Flush after every N rows to prevent HTTP timeout |
| 3 | 🟡 Common | Missing UTF-8 BOM for non-ASCII content | Prepend `\xEF\xBB\xBF` to the output stream for Excel compatibility |

## 5. REF

| Resource | Link | Note |
| --- | --- | --- |
| encoding/csv | [https://pkg.go.dev/encoding/csv](https://pkg.go.dev/encoding/csv) | CSV writing and parsing in Go |
| net/http | [https://pkg.go.dev/net/http](https://pkg.go.dev/net/http) | HTTP download headers and response streaming basics |

## 6. RECOMMEND

| Extension | When to proceed | Rationale | File/Link |
| --- | --- | --- | --- |
| **Stream Writing** | Row count exceeds what fits in memory | Chunked write-flush loops keep memory constant | [./01-csv-stream-writer-http-download.md](./01-csv-stream-writer-http-download.md) |
| **Streaming Pipelines** | Export exceeds HTTP timeout limits | Channel-based pipelines split fetch/transform/write into goroutines | [../streaming/README.md](../streaming/README.md) |

---
