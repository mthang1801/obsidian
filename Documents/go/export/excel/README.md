<!-- tags: golang, export, overview -->
# Excel Export

> Multi-sheet workbooks with cell styling, number formatting, and binary XLSX output using Excelize.

📅 Created: 2026-04-05 · 🔄 Updated: 2026-04-14 · ⏱️ 6 min read

---

## 1. DEFINE

CSV is plain text; Excel is a ZIP archive containing XML definitions, styles, and relationships. This complexity means XLSX generation consumes 10x more memory than CSV for the same row count. **Excel Export** teaches how to use Excelize's `StreamWriter` and style caching to keep memory bounded.

> *Generating multi-sheet Excel files with string concatenation creates corrupt XLSX files. Use a proper library like Excelize.*

### 1.1 Signals & Boundaries

- Open this lane when the output requires multiple sheets, colored headers, or numeric formatting.
- Excel workbooks demand substantial RAM — plan for background processing on large datasets.
- For simple flat tabular data without styling, prefer the CSV lane instead.

### 1.2 Learning Lanes

- `Excelize Multi-Sheet Styling` — `NewFile`, `NewSheet`, `StreamWriter`, style caching, and binary output.
- `Go Programming` — `github.com/xuri/excelize/v2` API patterns and cell coordinate math.

## 2. VISUAL

![Excel Export](../images/excel-router-map.png)

*Figure: Excel export flows from workbook initialization to sheet creation, cell rendering, and binary output.*

### Level 1

```text
HTTP Request
-> Initialize Workbook (excelize.NewFile)
-> Create Specific Worksheet ("SalesReport")
-> Render Cell Arrays + Apply Styles
-> Save Binary Output buffer
```

*Figure: The workbook lifecycle — create, populate, style, and save to a binary buffer.*

## 3. CODE

### Example 1: Router artifact — choosing the Excel lane

> **Goal**: Route to the Excelize styling doc.
> **Approach**: Match on the goal string.
> **Complexity**: O(1)

```go
func chooseLane(goal string) string {
    switch goal {
    case "excelize multi sheet styling":
        // Route to the Excelize multi-sheet styling doc.
        return "./01-excelize-multi-sheet-styling.md"
    default:
        return "./README.md"
    }
}
```

> **Why is Excel slower than CSV?**
> CSV writes plain strings to a stream. Excel builds ZIP archives with XML definitions, caches styles, and renders formatting. This overhead makes memory management critical for large exports.

## 4. PITFALLS

| # | Severity | Defect | Fix |
|---|----------|--------|-----|
| 1 | 🔴 Fatal | Loading million-row datasets into memory for Excel rendering | Use `excelize.StreamWriter` for row-by-row XML generation |
| 2 | 🔴 Fatal | Synchronous generation returning `504 Gateway Timeout` | Delegate large workbooks to background job queues |
| 3 | 🟡 Common | Calling `NewStyle()` for every row with identical formatting | Cache style IDs and reuse the integer reference |

## 5. REF

| Resource | Link | Note |
| --- | --- | --- |
| Excelize docs | [https://xuri.me/excelize/en/](https://xuri.me/excelize/en/) | Workbook generation, styling, and export behavior |
| Excelize package docs | [https://pkg.go.dev/github.com/xuri/excelize/v2](https://pkg.go.dev/github.com/xuri/excelize/v2) | API reference for workbook generation |

## 6. RECOMMEND

| Extension | When to proceed | Rationale | File/Link |
| --- | --- | --- | --- |
| **Excelize Patterns** | Need multi-sheet styling and cell formatting | Covers `NewStyle` caching, row iteration, and binary output | [./01-excelize-multi-sheet-styling.md](./01-excelize-multi-sheet-styling.md) |
| **Background Jobs** | Workbook generation exceeds HTTP timeout | Queue-based processing decouples rendering from the request | [../background-jobs/README.md](../background-jobs/README.md) |

---
