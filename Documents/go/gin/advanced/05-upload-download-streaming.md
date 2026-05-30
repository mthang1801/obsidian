<!-- tags: golang --> # 📤 Tải lên và tải xuống trực tuyến — Tệp lớn trong Gin

> **Thư viện**: Truyền phát các nội dung tải lên có dung lượng lớn qua `io.Copy` , phân phát các nội dung tải xuống có tiêu đề phù hợp, giảm tải cho các URL được ký trước của S3.

📅 Đã cập nhật: 2026-04-19 · ⏱️ 16 phút đọc

## 1. ĐỊNH NGHĨA

Đang tải tệp 500 MB vào bộ nhớ bằng `ioutil.ReadAll` sẽ giết chết quá trình. Thay vào đó: hãy sử dụng `http.MaxBytesReader` để giới hạn kích thước nội dung, phát trực tiếp bằng `io.Copy` để tránh bị giật và đặt tiêu đề `Content-Disposition` + `Content-Length` để tải xuống. Để sản xuất, hãy chuyển sang các URL được ký trước S3/GCS.

| Mối quan tâm | Giải pháp |
| --------------- | ----------------------------------------- |
| Tổng kích thước | `http.MaxBytesReader(w, body, maxBytes)` |
| Xác thực | Kiểm tra tiện ích mở rộng + MIME trước khi lưu |
| Truyền phát an toàn | `io.Copy(dst, file)` — không có bộ đệm đầy đủ |
| Tiêu đề đúng | `Content-Disposition: attachment` |

### Bất biến chính

- **Luôn đặt `MaxBytesReader` trước nội dung đọc.** Nếu không có nó, tải lên 10 GB sẽ tiêu tốn toàn bộ RAM.
- **Sử dụng `filepath.Base()` trên tên tệp người dùng.** Ngăn chặn các cuộc tấn công truyền tải đường dẫn ( `../../etc/passwd` ).

## 2. HÌNH ẢNH ![Upload and download streaming — buffered vs io.Copy streaming with S3 pre-signed URLs](./images/05-upload-streaming.png) *Hình: Tải lên — bộ đệm các tệp nhỏ trong bộ nhớ (c.FormFile), luồng tệp lớn qua io.Copy. Tải xuống — c.File (tĩnh), c.FileAttachment (bắt buộc tải xuống), io.Copy (luồng từ S3/DB).*```mermaid
flowchart LR
    subgraph Upload
        A["multipart/form-data"] -->|"MaxBytesReader"| B["FormFile"]
        B -->|"io.Copy"| C["disk / S3"]
    end
    subgraph Download
        D["GET /report"] --> E["os.Open"]
        E -->|"io.Copy"| F["Response writer"]
    end
    subgraph Pre-signed
        G["GET /download"] --> H["S3.CreateDownloadURL"]
        H --> I["302 redirect"]
    end
```*Hình: Ba mẫu — tải luồng lên qua io.Copy, tải luồng xuống với tiêu đề phù hợp, giảm tải qua URL được ký trước.*

### Quyết định mẫu```text
Small file (≤10MB):  c.SaveUploadedFile (Gin built-in)
Large file (≥10MB):  MaxBytesReader + io.Copy (streamed)
Production:          Pre-signed S3/GCS URL (no server bandwidth)
```## 3. MÃ

### Ví dụ 1: Cơ bản — Luồng ghi nhiều phần```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Streamed upload: cap body with MaxBytesReader,
    // extract file, validate name, stream via io.Copy.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package advanced

    import (
        "io"
        "net/http"
        "os"
        "path/filepath"
        "github.com/gin-gonic/gin"
    )

    func UploadDocument(c *gin.Context) {
        c.Request.Body = http.MaxBytesReader(c.Writer, c.Request.Body, 20<<20)

        file, header, err := c.Request.FormFile("file")
        if err != nil {
            c.JSON(http.StatusBadRequest, gin.H{"error": "invalid multipart file"})
            return
        }
        defer file.Close()

        safeName := filepath.Base(header.Filename)
        dst, err := os.Create(filepath.Join("/tmp/uploads", safeName))
        if err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": "create destination failed"})
            return
        }
        defer dst.Close()

        if _, err := io.Copy(dst, file); err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": "stream upload failed"})
            return
        }

        c.JSON(http.StatusCreated, gin.H{"file": safeName})
    }
```### Ví dụ 2: Trung cấp — Tiêu đề truyền phát phản hồi```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Streamed download: open file, set Content-Disposition
    // + Content-Length headers, stream via io.Copy.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package advanced

    import (
        "io"
        "net/http"
        "os"
        "strconv"
        "github.com/gin-gonic/gin"
    )

    func DownloadReport(c *gin.Context) {
        file, err := os.Open("/tmp/reports/report-2026-03.csv")
        if err != nil {
            c.JSON(http.StatusNotFound, gin.H{"error": "report not found"})
            return
        }
        defer file.Close()

        stat, err := file.Stat()
        if err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": "stat failed"})
            return
        }

        c.Header("Content-Type", "text/csv")
        c.Header("Content-Disposition", `attachment; filename="report-2026-03.csv"`)
        c.Header("Content-Length", strconv.FormatInt(stat.Size(), 10))
        c.Status(http.StatusOK)
        _, _ = io.Copy(c.Writer, file)
    }
```### Ví dụ 3: Nâng cao — URL đối tượng được ký trước```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Pre-signed URL: generate time-limited S3 download URL.
    // Client downloads directly from S3, no server bandwidth.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package advanced

    import (
        "net/http"
        "time"
        "github.com/gin-gonic/gin"
    )

    type SignedURLProvider interface {
        CreateDownloadURL(objectKey string, expiresIn time.Duration) (string, error)
    }

    func RequestReportDownload(provider SignedURLProvider) gin.HandlerFunc {
        return func(c *gin.Context) {
            url, err := provider.CreateDownloadURL("reports/report-2026-03.csv", 15*time.Minute)
            if err != nil {
                c.JSON(http.StatusInternalServerError, gin.H{"error": "signed url generation failed"})
                return
            }

            c.JSON(http.StatusAccepted, gin.H{
                "delivery": "signed_url",
                "url":      url,
                "expires":  "15m",
            })
        }
    }
```---

## 4. Cạm bẫy

| # | Mức độ nghiêm trọng | Khiếm khuyết | Tác động | Sửa chữa |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Gây tử vong | Không sử dụng `MaxBytesReader` trên điểm cuối tải lên | Tải lên 10GB sẽ tiêu tốn hết RAM; xử lý OOM-kill | `http.MaxBytesReader(c.Writer, c.Request.Body, 20<<20)` |
| 2 | 🔴 Gây tử vong | Sử dụng tên tệp do người dùng cung cấp trực tiếp trong `os.Create` | Truyền tải đường dẫn: `../../etc/passwd` ghi đè các tệp hệ thống | `filepath.Base(header.Filename)` để loại bỏ các thành phần đường dẫn |

---

## 5. GIỚI THIỆU

| Tài nguyên | Liên kết |
| --- | --- |
| Kịch câm/Đa phần | [pkg.go.dev/mime/multipart](https://pkg.go.dev/mime/multipart) |

---

## 6. KHUYẾN NGHỊ

| Gia hạn | Khi nào | Cơ sở lý luận | Tài nguyên |
| --- | --- | --- | --- |
| SSE & WebSocket | Khi bạn cần đẩy thời gian thực tới khách hàng | SSE cho nguồn cấp dữ liệu một chiều, WebSocket cho thông báo/trò chuyện hai chiều | [./06-sse-websocket-real-time.md](./06-sse-websocket-real-time.md) |