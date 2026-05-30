<!-- tags: java, jdk -->
# ☕ Java Core Libraries — HTTP Client Basics & Async Requests

> Java 11+ đã có `HttpClient` chính thức trong JDK. Bài này tập trung vào cách gọi HTTP an toàn hơn với timeout, body handler và async request mà không phải kéo thư viện ngoài ngay từ đầu.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 14 phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Intermediate |
| **Use case** | Integrate external API, internal service call, async IO |
| **Java focus** | `HttpClient`, `HttpRequest`, `HttpResponse`, async send |
| **Prerequisites** | Java basics, CompletableFuture |

## 1. DEFINE

Hình dung một service Java vừa thêm call ra payment gateway mới. Ban đầu chỉ là một HTTP request rất bình thường, rồi timeout, retry, serialization và connection reuse bắt đầu chen vào mọi cuộc review. Từ lúc đó, `HttpClient` không còn là một API nhỏ trong JDK. Nó trở thành một boundary mạng thật sự.

Bài này đặt `Java Core Libraries — HTTP Client Basics & Async Requests` vào đúng kiểu quyết định đó: không bắt đầu bằng định nghĩa khô, mà bằng lý do tại sao người đọc lại cần khái niệm này ngay bây giờ và điều gì sẽ hỏng nếu hiểu sai nó.

### Vì sao dùng JDK HttpClient?

`HttpClient` giúp:

- tránh phụ thuộc thêm thư viện chỉ để gọi HTTP cơ bản
- hỗ trợ sync và async API
- đi kèm timeout, HTTP/2, body handlers

### Actors

| Actor | Vai trò |
| --- | --- |
| `HttpClient` | Reusable client object |
| `HttpRequest` | Mô tả request |
| `HttpResponse` | Kết quả trả về |
| Body handler | Chọn cách đọc response body |

### Failure Modes

| Failure | Nguyên nhân | Fix |
| --- | --- | --- |
| Không có timeout | Request treo vô hạn | Đặt timeout ở request/client |
| Tạo client mới mỗi lần gọi | Mất lợi ích reuse | Dùng shared client |
| Không xử lý HTTP status | Chỉ đọc body | Check status + error branch rõ |

Các failure mode trên nghe dễ tránh. Nhưng có trap: HttpClient không set timeout = blocking forever, và response body handler sai = empty body. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa mới chỉ khóa được tên của Java Core Libraries — HTTP Client Basics & Async Requests. Để khái niệm này bớt trừu tượng, ta cần nhìn nó ở dạng flow hoặc cấu trúc đủ cụ thể trước.

```text
HttpClient
   │
   ├── build request
   ├── send / sendAsync
   └── map response
```

```text
request -> network -> response
   │                     │
   ├── timeout           ├── status code
   └── headers/body      └── parse or fallback
```

## 3. CODE

Flow của Java Core Libraries — HTTP Client Basics & Async Requests đã rõ hơn. Bây giờ ta chuyển sang code để thấy quyết định nào là cơ học, quyết định nào là nơi hệ thống thật bắt đầu khác ví dụ.

### Basic: synchronous GET

```java
// CatalogHttpClient.java — Basic synchronous GET with JDK HttpClient
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

public final class CatalogHttpClient {
    private final HttpClient httpClient = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(2))
            .build();

    public String fetchCatalog() throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("https://example.com/api/catalog"))
                .timeout(Duration.ofSeconds(3))
                .GET()
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() >= 400) {
            throw new IllegalStateException("catalog request failed: " + response.statusCode());
        }
        return response.body();
    }
}
```

Sync requests đã cover. Nhưng async cần CompletableFuture — hãy non-blocking.

### Intermediate: POST with JSON body

```java
// NotificationHttpClient.java — POST JSON payload with explicit headers
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

public final class NotificationHttpClient {
    private final HttpClient httpClient = HttpClient.newHttpClient();

    public int send(String jsonPayload) throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("https://example.com/api/notifications"))
                .timeout(Duration.ofSeconds(5))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.statusCode();
    }
}
```

Async đã cover. Nhưng interceptors cần HttpClient.Builder — hãy customize.

### Advanced: async send

```java
// PricingHttpClient.java — Async HTTP call composed with CompletableFuture
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.concurrent.CompletableFuture;

public final class PricingHttpClient {
    private final HttpClient httpClient = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(2))
            .build();

    public CompletableFuture<String> fetchPriceAsync(String sku) {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("https://example.com/api/prices/" + sku))
                .timeout(Duration.ofSeconds(3))
                .GET()
                .build();

        return httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .thenApply(response -> {
                    if (response.statusCode() >= 400) {
                        throw new IllegalStateException("pricing request failed: " + response.statusCode());
                    }
                    return response.body();
                });
    }
}
```

Bạn đã đi qua sync, async, và interceptors. Bây giờ đến phần nguy hiểm: missing timeout và handler mismatch — trap đã được setup từ đầu bài.

## 4. PITFALLS

Biết cách dùng `Java Core Libraries — HTTP Client Basics & Async Requests` chưa đủ để an toàn. Phần dễ trả giá nhất luôn nằm ở những chỗ nhìn có vẻ hợp lý nhưng âm thầm bẻ cong invariant của bài.

| # | Lỗi | Fix |
| --- | --- | --- |
| 1 | Không set timeout | Đặt connect + request timeout |
| 2 | Tạo `HttpClient` cho mỗi request | Reuse client instance |
| 3 | Không check status code | Chuẩn hóa error handling |
| 4 | Async nhưng `.join()` ngay lập tức | Giữ composition async đúng chỗ |

Bạn đã đi qua HTTP Client và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| --- | --- |
| JDK HttpClient | https://docs.oracle.com/en/java/javase/21/docs/api/java.net.http/java/net/http/HttpClient.html |
| HttpRequest | https://docs.oracle.com/en/java/javase/21/docs/api/java.net.http/java/net/http/HttpRequest.html |
| HttpResponse | https://docs.oracle.com/en/java/javase/21/docs/api/java.net.http/java/net/http/HttpResponse.html |

## 6. RECOMMEND

Khi các bẫy chính của `Java Core Libraries — HTTP Client Basics & Async Requests` đã hiện ra, bước tiếp theo là nối nó sang nhánh Java lân cận để mental model không đứng yên ở một ví dụ đơn lẻ.

| Mở rộng | Khi nào | Lý do |
| --- | --- | --- |
| Retry / resilience wrapper | Downstream không ổn định | Tăng độ bền client |
| JSON mapping layer | Response body phức tạp | Tách parsing khỏi transport |
| Metrics/tracing | Client call quan trọng | Quan sát latency và error rate |

## 7. QUIZ

### Quick Check

1. Vì sao nên reuse `HttpClient` thay vì tạo mới mỗi request?
2. `sendAsync` trả về gì?
3. Khi nào cần timeout ở cả request lẫn client?

### Answer Key

1. Vì reuse tốt hơn cho resource management và connection behavior.
2. `CompletableFuture<HttpResponse<T>>`.
3. Khi cần kiểm soát cả connect phase lẫn toàn bộ request lifecycle.

## 8. NEXT STEPS

- Nối với `CompletableFuture` để orchestrate nhiều downstream calls
- Hoặc thêm resilience patterns cho external API integration
