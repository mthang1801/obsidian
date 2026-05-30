<!-- tags: golang --> # 📡 SSE & WebSocket — Mô hình phân phối thời gian thực ở Gin

> **Thư viện**: SSE cho nguồn cấp dữ liệu đẩy máy chủ, WebSocket cho thời gian thực hai chiều thông qua `gorilla/websocket` + Hub dựa trên kênh.

📅 Cập nhật: 2026-04-19 · ⏱️ 17 phút đọc

## 1. ĐỊNH NGHĨA

SSE đẩy các sự kiện từ máy chủ đến máy khách qua một kết nối HTTP ( `text/event-stream` ). WebSocket nâng cấp HTTP lên kết nối TCP song công, liên tục. Trong Gin, SSE sử dụng `c.Writer.Flush()` với tiêu đề `text/event-stream` ; WebSocket sử dụng trình nâng cấp `gorilla/websocket` .

| Tiêu chuẩn | Lợi thế cốt lõi |
| --------- | ----------------------------------------- |
| SSE | Đơn hướng, tự động kết nối lại, HTTP/2 OK |
| WebSocket | Hai chiều, liên tục, độ trễ thấp |

### Bất biến chính

- **Luôn kiểm tra `c.Request.Context().Done()` trong vòng lặp SSE.** Không có nó, các máy khách bị ngắt kết nối sẽ rò rỉ goroutines.
- **Sử dụng mẫu Hub để phát WebSocket.** Gửi kết nối trực tiếp không mở rộng quy mô và tạo điều kiện cạnh tranh.

## 2. HÌNH ẢNH ![Advanced real-time patterns — SSE Broker fan-out and WebSocket Hub with Redis Pub/Sub scaling](./images/06-realtime-advanced.png) *Hình: SSE Broker (phân nhánh ra các kênh thuê bao) + WebSocket Hub (readPump/writePump cho mỗi khách hàng, chọn khi đăng ký/hủy đăng ký/phát sóng). Chia tỷ lệ thông qua Redis Pub/Sub trên các nhóm.*```mermaid
sequenceDiagram
    participant C as Client
    participant S as Gin Server
    rect rgb(240,248,255)
        Note over C,S: SSE (Server-Sent Events)
        C->>S: GET /events (Accept: text/event-stream)
        S-->>C: event: progress\ndata: 10
        S-->>C: event: progress\ndata: 50
        S-->>C: event: progress\ndata: 100
    end
    rect rgb(255,248,240)
        Note over C,S: WebSocket
        C->>S: GET /ws (Upgrade: websocket)
        S-->>C: 101 Switching Protocols
        C->>S: {"type":"ping"}
        S-->>C: {"type":"pong"}
    end
```*Hình: SSE = máy chủ đẩy các sự kiện qua HTTP; WebSocket = hai chiều sau khi nâng cấp giao thức.*

### Khi nào nên sử dụng cái nào```text
SSE:       Notifications, progress bars, live dashboards (one-way)
WebSocket: Chat, collaborative editing, gaming (two-way)
Polling:   Last resort when SSE/WS are blocked by infra
```## 3. MÃ

### Ví dụ 1: Cơ bản — Nguồn cấp dữ liệu SSE```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // SSE handler: set text/event-stream headers, loop with
    // ticker, flush after each write, exit on context cancel.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package advanced

    import (
        "fmt"
        "time"
        "github.com/gin-gonic/gin"
    )

    func ProgressSSE(c *gin.Context) {
        c.Writer.Header().Set("Content-Type", "text/event-stream")
        c.Writer.Header().Set("Cache-Control", "no-cache")
        c.Writer.Header().Set("Connection", "keep-alive")

        ticker := time.NewTicker(2 * time.Second)
        defer ticker.Stop()

        for progress := 10; progress <= 100; progress += 10 {
            select {
            case <-c.Request.Context().Done():
                return
            case <-ticker.C:
                _, _ = fmt.Fprintf(c.Writer, "event: progress\ndata: %d\n\n", progress)
                c.Writer.Flush()
            }
        }
    }
```### Ví dụ 2: Trung cấp — WebSocket Echo```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // WebSocket echo: upgrade HTTP, read message, write it
    // back. Exit loop on read error (client disconnected).
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package advanced

    import (
        "net/http"
        "github.com/gin-gonic/gin"
        "github.com/gorilla/websocket"
    )

    var upgrader = websocket.Upgrader{
        CheckOrigin: func(r *http.Request) bool { return true },
    }

    func EchoWebSocket(c *gin.Context) {
        conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
        if err != nil {
            c.Status(http.StatusBadRequest)
            return
        }
        defer conn.Close()

        for {
            messageType, payload, err := conn.ReadMessage()
            if err != nil {
                return
            }
            if err := conn.WriteMessage(messageType, payload); err != nil {
                return
            }
        }
    }
```### Ví dụ 3: Nâng cao — Managed Broadcast Hub```go
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // Broadcast Hub: manage client registration/unregistration
    // via channels. Non-blocking send with default close.
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    package advanced

    type Client struct {
        Send chan []byte
    }

    type Hub struct {
        Register   chan *Client
        Unregister chan *Client
        Broadcast  chan []byte
        clients    map[*Client]struct{}
    }

    func NewHub() *Hub {
        return &Hub{
            Register:   make(chan *Client),
            Unregister: make(chan *Client),
            Broadcast:  make(chan []byte, 128),
            clients:    make(map[*Client]struct{}),
        }
    }

    func (h *Hub) Run() {
        for {
            select {
            case client := <-h.Register:
                h.clients[client] = struct{}{}
            case client := <-h.Unregister:
                delete(h.clients, client)
                close(client.Send)
            case msg := <-h.Broadcast:
                for client := range h.clients {
                    select {
                    case client.Send <- msg:
                    default:
                        delete(h.clients, client)
                        close(client.Send)
                    }
                }
            }
        }
    }
```---

## 4. Cạm bẫy

| # | Mức độ nghiêm trọng | Khiếm khuyết | Tác động | Sửa chữa |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Gây tử vong | Vòng lặp SSE không có kiểm tra `ctx.Done()` | Máy khách bị ngắt kết nối sẽ rò rỉ goroutine; ngàn chồng chất | `select { case <-c.Request.Context().Done(): return }` |
| 2 | 🔴 Gây tử vong | WebSocket `CheckOrigin` trả lại `true` trong sản xuất | Mọi nguồn gốc đều có thể kết nối; kích hoạt các cuộc tấn công CSWSH | Xác thực nguồn gốc theo danh sách cho phép |

---

## 5. GIỚI THIỆU

| Tài nguyên | Liên kết |
| --- | --- |
| Khỉ đột WS | [github.com/gorilla/websocket](https://github.com/gorilla/websocket) |

---

## 6. KHUYẾN NGHỊ

| Gia hạn | Khi nào | Cơ sở lý luận | Tài nguyên |
| --- | --- | --- | --- |
| Công cụ kiểm tra | Khi bạn cần kiểm tra trình xử lý SSE/WebSocket | Sử dụng `httptest` cho SSE, `gorilla/websocket.Dial` cho các bài kiểm tra WS | [./01-testing-production.md](./01-testing-production.md) |