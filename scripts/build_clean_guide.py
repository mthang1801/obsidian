import re
import os

SOURCE_DIR = "/home/mvt/mAIvt/Documents/go/gin"
TARGET_FILE = "/home/mvt/mAIvt/Go/Fundamental/gin-guide.html"

MAPPING = [
    {"id": "engine-context", "path": "basics/01-engine-context-handlers.md", "category": "Basics", "badge": "BASICS"},
    {"id": "project-struct", "path": "basics/02-project-structure.md", "category": "Basics", "badge": "BASICS"},
    {"id": "json-validation", "path": "binding/01-json-form-validation.md", "category": "Binding", "badge": "BINDING"},
    {"id": "file-upload", "path": "binding/02-file-upload-multipart.md", "category": "Binding", "badge": "BINDING"},
    {"id": "groups-params", "path": "routing/01-groups-params.md", "category": "Routing", "badge": "ROUTING"},
    {"id": "versioning-redirect", "path": "routing/02-versioning-redirect.md", "category": "Routing", "badge": "ROUTING"},
    {"id": "builtin-custom-mw", "path": "middleware/01-builtin-custom.md", "category": "Middleware", "badge": "MIDDLEWARE"},
    {"id": "guards-interceptors", "path": "middleware/02-guards-interceptors.md", "category": "Middleware", "badge": "MIDDLEWARE"},
    {"id": "json-html-streaming", "path": "response/01-json-html-streaming.md", "category": "Response", "badge": "RESPONSE"},
    {"id": "sse-websocket", "path": "response/02-sse-websocket.md", "category": "Response", "badge": "RESPONSE"},
    {"id": "configuration", "path": "techniques/01-configuration.md", "category": "Techniques", "badge": "TECHNIQUES"},
    {"id": "database-orm", "path": "techniques/02-database-orm.md", "category": "Techniques", "badge": "TECHNIQUES"},
    {"id": "validation-dto", "path": "techniques/03-validation-dto.md", "category": "Techniques", "badge": "TECHNIQUES"},
    {"id": "caching", "path": "techniques/04-caching.md", "category": "Techniques", "badge": "TECHNIQUES"},
    {"id": "logging", "path": "techniques/05-logging.md", "category": "Techniques", "badge": "TECHNIQUES"},
    {"id": "session-cookies", "path": "techniques/06-session-cookies.md", "category": "Techniques", "badge": "TECHNIQUES"},
    {"id": "error-handling", "path": "techniques/07-error-handling.md", "category": "Techniques", "badge": "TECHNIQUES"},
    {"id": "authentication-jwt", "path": "security/01-authentication-jwt.md", "category": "Security", "badge": "SECURITY"},
    {"id": "authorization-rbac", "path": "security/02-authorization-rbac.md", "category": "Security", "badge": "SECURITY"},
    {"id": "cors-csrf-helmet", "path": "security/03-cors-csrf-helmet.md", "category": "Security", "badge": "SECURITY"},
    {"id": "rate-limiting", "path": "security/04-rate-limiting.md", "category": "Security", "badge": "SECURITY"},
    {"id": "swagger-openapi", "path": "recipes/01-swagger-openapi.md", "category": "Recipes", "badge": "RECIPES"},
    {"id": "health-check", "path": "recipes/02-health-check.md", "category": "Recipes", "badge": "RECIPES"},
    {"id": "graceful-cqrs", "path": "recipes/03-graceful-cqrs.md", "category": "Recipes", "badge": "RECIPES"},
    {"id": "testing-production", "path": "advanced/01-testing-production.md", "category": "Advanced", "badge": "ADVANCED"},
    {"id": "dependency-injection", "path": "advanced/02-dependency-injection.md", "category": "Advanced", "badge": "ADVANCED"},
    {"id": "lifecycle-hooks", "path": "advanced/03-lifecycle-hooks.md", "category": "Advanced", "badge": "ADVANCED"},
    {"id": "auth-rate-limit-production", "path": "advanced/04-auth-rate-limit-production.md", "category": "Advanced", "badge": "ADVANCED"},
    {"id": "upload-download-streaming", "path": "advanced/05-upload-download-streaming.md", "category": "Advanced", "badge": "ADVANCED"},
    {"id": "sse-websocket-realtime", "path": "advanced/06-sse-websocket-real-time.md", "category": "Advanced", "badge": "ADVANCED"}
]

TRANSLATIONS = {
    "Severity": "Mức độ",
    "Defect": "Sai sót / Lỗi",
    "Impact": "Ảnh hưởng",
    "Fix": "Giải pháp khắc phục",
    "Scope": "Phạm vi",
    "Application": "Cách áp dụng",
    "Use case": "Trường hợp sử dụng",
    "Method": "Phương thức",
    "Source": "Nguồn dữ liệu",
    "NestJS Concept": "Khái niệm NestJS",
    "Gin Equivalent": "Tương đương trong Gin",
    "NestJS": "NestJS (TypeScript)",
    "Gin / Go": "Gin / Go (Golang)",
    "Resource": "Tài liệu",
    "Link": "Liên kết",
    "Extension": "Chủ đề mở rộng",
    "When": "Khi nào áp dụng",
    "Rationale": "Lý do áp dụng",
    "Component": "Thành phần",
    "Role": "Vai trò",
    "Code": "Mã nguồn minh họa",
    "RouterGroup": "Nhóm định tuyến",
}

SEVERITY_MAP = {
    "🔴 Fatal": '<span class="badge b-expert" style="background:rgba(239,68,68,0.12);color:#f87171;border:1px solid rgba(239,68,68,0.25);">🔴 FATAL</span>',
    "🔴 Critical": '<span class="badge b-expert" style="background:rgba(239,68,68,0.12);color:#f87171;border:1px solid rgba(239,68,68,0.25);">🔴 CRITICAL</span>',
    "🟡 Common": '<span class="badge b-advanced" style="background:rgba(245,158,11,0.1);color:#fbbf24;border:1px solid rgba(245,158,11,0.25);">🟡 COMMON</span>',
    "🟡 Warning": '<span class="badge b-advanced" style="background:rgba(245,158,11,0.1);color:#fbbf24;border:1px solid rgba(245,158,11,0.25);">🟡 WARNING</span>',
}

PROSE_TRANSLATIONS = [
    # 01 Basics - Engine & Context
    ("Every Gin application starts with three primitives: the **Engine** (creates the router and holds middleware), the **Context** (carries request data, response writer, and per-request key-value storage through the middleware chain), and the **Handler** (a function with signature `func(c *gin.Context)` that processes a single request).",
     "Mọi ứng dụng Gin đều bắt đầu bằng ba thành phần nguyên tố: **Engine** (khởi tạo bộ định tuyến và chứa middleware), **Context** (mang dữ liệu request, bộ ghi response và kho lưu trữ key-value per-request xuyên suốt chuỗi middleware), và **Handler** (hàm có cấu trúc `func(c *gin.Context)` để xử lý một request đơn lẻ)."),
    ("Context is NOT goroutine-safe. Passing `*gin.Context` into a goroutine without `.Copy()` causes data races and panics.",
     "Context KHÔNG an toàn cho Goroutine (thread-safe). Truyền trực tiếp `*gin.Context` vào goroutine mà không sử dụng `.Copy()` sẽ gây lỗi Data Race và crash runtime panic."),
    ("`gin.Default()` includes Logger and Recovery middleware. Use `gin.New()` for a bare engine when you want full control.",
     "`gin.Default()` bao gồm sẵn middleware Logger và Recovery. Sử dụng `gin.New()` để có một engine sạch hoàn toàn khi bạn muốn tự kiểm soát toàn bộ."),
    ("*Figure: Gin request lifecycle — HTTP request enters the Engine's radix tree for route matching, passes through the middleware chain (Logger → Recovery → Custom Auth) before hitting the final handler.*",
     "*Hình: Vòng đời request trong Gin — HTTP request đi vào cây radix tree của Engine để so khớp route, đi qua chuỗi middleware (Logger → Recovery → Custom Auth) trước khi đến handler xử lý.*"),
    ("*Figure: Request lifecycle — incoming HTTP request → Engine route match → middleware chain → handler → response.*",
     "*Hình: Vòng đời request — HTTP request gửi đến → Engine so khớp route → chuỗi middleware → handler → response.*"),
    ("*Figure: Context boundary — each request gets its own `gin.Context` with params, query, headers, body, and a KV store.*",
     "*Hình: Ranh giới Context — mỗi request nhận được một đối tượng `gin.Context` riêng chứa tham số, query, headers, body và một kho lưu trữ Key-Value.*"),

    # 02 Basics - Project Structure
    ("NestJS (TypeScript) uses decorators and packages to organize code into dependency-injected modules. In Go, packages are directories. To avoid import cycles, you structure the project by layer (handlers, services, repositories) with explicit dependency injection during boot.",
     "NestJS (TypeScript) sử dụng các decorator và packages để tổ chức mã nguồn thành các module được tiêm phụ thuộc (dependency injection). Trong Go, các package được tổ chức dưới dạng thư mục. Để tránh lỗi import vòng tròn (import cycles), bạn cấu trúc dự án theo lớp (handlers, services, repositories) với việc tiêm phụ thuộc tường minh lúc khởi chạy."),
    ("Import cycles in Go are compile errors, not warnings. Handlers depend on Services, Services depend on Repositories, Repositories depend on the DB handle. Never import upstream (e.g., service importing handler).",
     "Lỗi Import vòng tròn trong Go sẽ gây lỗi biên dịch chứ không phải cảnh báo. Handlers phụ thuộc vào Services, Services phụ thuộc vào Repositories, Repositories phụ thuộc vào kết nối DB. Tuyệt đối không bao giờ import ngược dòng (ví dụ: service import handler)."),
    ("Avoid global state (like global DB variables). Pass database handles and dependencies explicitly via struct constructors (`NewHandler`, `NewService`).",
     "Tránh sử dụng state toàn cục (như biến DB toàn cục). Hãy truyền kết nối database và các phụ thuộc một cách tường minh thông qua hàm dựng struct constructor (`NewHandler`, `NewService`)."),
    ("*Figure: Go Gin project structure — `cmd/api/main.go` wires dependencies into domain packages (`internal/user`, `internal/product`), each following a clean layout.*",
     "*Hình: Cấu trúc dự án Go Gin — `cmd/api/main.go` liên kết các phụ thuộc vào các package domain (`internal/user`, `internal/product`), mỗi thư mục tuân theo một layout sạch sẽ.*"),
    ("*Figure: Layered architecture — `cmd/` bootstraps the app, `internal/` contains domain packages, each with handler → service → repository.*",
     "*Hình: Kiến trúc phân lớp — `cmd/` khởi động ứng dụng, `internal/` chứa các package domain, mỗi package có cấu trúc handler → service → repository.*"),

    # 03 Binding - JSON Form Validation
    ("Bind JSON/form/URI data to Go structs and validate with `binding` tags powered by go-playground/validator. NestJS uses class-validator. In Gin, `c.ShouldBind*` methods decode request data into a struct and run validation rules in one line.",
     "Liên kết dữ liệu JSON/form/URI vào các struct Go và xác thực bằng thẻ `binding` vận hành bởi go-playground/validator. NestJS sử dụng class-validator. Trong Gin, các phương thức `c.ShouldBind*` giúp decode dữ liệu request vào struct và kích hoạt các quy tắc xác thực chỉ trong một dòng code."),
    ("`c.ShouldBindJSON` reads the request body. If validation fails, it returns an error. You must handle this error and return a custom response.",
     "`c.ShouldBindJSON` đọc request body. Nếu xác thực thất bại, nó sẽ trả về lỗi. Bạn phải tự xử lý lỗi này và trả về phản hồi tùy chỉnh tương ứng."),
    ("Use pointers for fields that are optional or can be nil (e.g., in PATCH requests). Pointers + `omitempty` tag allow correct partial updates.",
     "Sử dụng con trỏ (pointers) cho các trường không bắt buộc hoặc có thể nhận giá trị nil (ví dụ: trong request PATCH). Sự kết hợp giữa con trỏ và tag `omitempty` cho phép cập nhật từng phần (partial updates) chính xác."),
    ("*Figure: Binding pipeline — raw request → ShouldBindJSON → struct hydration → validator rules → error or clean struct.*",
     "*Hình: Pipeline liên kết dữ liệu — request thô → ShouldBindJSON → làm đầy struct → các quy tắc validator → lỗi hoặc struct sạch.*"),
    ("*Figure: Decision tree — choose ShouldBindJSON (body), ShouldBindQuery (querystring), or ShouldBindUri (path).*",
     "*Hình: Cây quyết định — chọn ShouldBindJSON (cho body), ShouldBindQuery (cho querystring), hoặc ShouldBindUri (cho path).*"),

    # 04 Binding - File Upload Multipart
    ("Handle single and multiple file uploads safely with custom size limits. NestJS uses FileInterceptor. In Gin, you read form data directly from the multipart parser, limit memory usage, and save files to disk or cloud storage.",
     "Xử lý tải lên đơn tệp và đa tệp an toàn với giới hạn kích thước tùy chỉnh. NestJS sử dụng FileInterceptor. Trong Gin, bạn đọc dữ liệu form trực tiếp từ bộ phân tích multipart, giới hạn dung lượng bộ nhớ và lưu tệp vào đĩa cứng hoặc dịch vụ lưu trữ đám mây."),
    ("Gin buffers the entire multipart body into memory up to MaxMultipartMemory (default 32 MB). If files exceed this, they are temp-stored on disk. Use `c.FormFile` for single files, and `c.MultipartForm` for multiple files.",
     "Gin lưu tạm thời toàn bộ thân request multipart vào bộ nhớ tối đa là MaxMultipartMemory (mặc định 32 MB). Nếu tệp vượt quá giới hạn này, chúng sẽ được lưu tạm thời trên đĩa. Sử dụng `c.FormFile` cho đơn tệp, và `c.MultipartForm` cho đa tệp."),
    ("Never trust the filename from the client. Sanitize filenames or generate UUIDs before saving to prevent directory traversal attacks.",
     "Không bao giờ tin tưởng tên tệp từ phía client. Hãy làm sạch tên tệp (sanitize) hoặc tự sinh UUID mới trước khi lưu để ngăn chặn các cuộc tấn công directory traversal."),
    ("*Figure: File upload flow — multipart request buffered by MaxMultipartMemory → c.FormFile extracts header → validation (extension, size, content sniff) → write to storage.*",
     "*Hình: Luồng tải lên tệp — request multipart được đệm bởi MaxMultipartMemory → c.FormFile trích xuất header → xác thực (đuôi tệp, kích thước, sniff nội dung) → ghi vào kho lưu trữ.*"),
    ("*Figure: File upload flow — multipart form → extract file header → validate → save to disk or cloud storage.*",
     "*Hình: Luồng tải lên tệp — form multipart → trích xuất header của file → xác thực → lưu vào ổ đĩa hoặc cloud storage.*"),

    # 05 Middleware - Builtin Custom
    ("Chain middleware functions that run before/after every handler — logging, recovery, auth, CORS, request ID. NestJS uses global and route-specific guards/interceptors. In Gin, middleware is a function with signature `func(c *gin.Context)` that calls `c.Next()` to continue the chain.",
     "Liên kết các hàm middleware chạy trước và sau mỗi handler — logging, recovery, auth, CORS, request ID. NestJS sử dụng các guard/interceptor toàn cục hoặc theo route. Trong Gin, middleware là hàm có cấu trúc `func(c *gin.Context)` gọi `c.Next()` để tiếp tục chuỗi xử lý."),
    ("A Gin middleware is a `gin.HandlerFunc` that runs in a chain before (and optionally after) the final handler. `c.Next()` advances to the next middleware in the chain. `c.Abort()` stops downstream handlers from executing, but the current middleware will finish its execution unless you explicitly return.",
     "Middleware trong Gin là một `gin.HandlerFunc` chạy trong một chuỗi trước (và tùy chọn sau) handler cuối cùng. `c.Next()` chuyển tiếp đến middleware tiếp theo trong chuỗi. `c.Abort()` ngăn các handler phía sau thực thi, nhưng middleware hiện tại vẫn sẽ chạy hết code của nó trừ khi bạn gọi return một cách tường minh."),
    ("Always call `return` immediately after aborting a request in middleware. Failing to do so causes the remaining code inside the current middleware to execute, even though downstream handlers are blocked.",
     "Luôn gọi `return` ngay sau khi abort một request trong middleware. Nếu thiếu `return`, mã nguồn phía sau của middleware hiện tại vẫn sẽ tiếp tục thực thi, dù các handler phía sau đã bị chặn."),
    ("*Figure: Middleware chain — incoming request → Middleware 1 → Middleware 2 → Handler → response flow.*",
     "*Hình: Chuỗi Middleware — request đi vào → Middleware 1 → Middleware 2 → Handler → luồng response ngược lại.*"),
    ("*Figure: Middleware flow — request goes downstream (before c.Next) and then upstream (after c.Next) in reverse order.*",
     "*Hình: Luồng Middleware — request đi xuôi dòng (trước c.Next) và sau đó đi ngược dòng (sau c.Next) theo thứ tự đảo ngược.*"),

    # 06 Middleware - Guards Interceptors
    ("NestJS (TypeScript) has four distinct pipeline stages (Guards → Interceptors → Pipes → Filters) with dedicated decorators. Gin collapses all four into a single primitive: middleware. By custom typing the handler function, you can build structured NestJS-style components.",
     "NestJS (TypeScript) có bốn giai đoạn đường dẫn riêng biệt (Guards → Interceptors → Pipes → Filters) với các decorator chuyên biệt. Gin gộp cả bốn thành phần này vào một cơ chế duy nhất: middleware. Bằng cách tùy chỉnh kiểu dữ liệu của hàm handler, bạn có thể xây dựng các thành phần có cấu trúc kiểu NestJS."),
    ("*Figure: NestJS pipeline concepts → Gin middleware — Guard (abort before c.Next), Interceptor (wrap c.Next), Pipe (ShouldBind in handler), Exception Filter (catch errors).*",
     "*Hình: Các khái niệm đường dẫn NestJS → Middleware của Gin — Guard (hủy trước c.Next), Interceptor (bao bọc c.Next), Pipe (ShouldBind trong handler), Exception Filter (bắt các lỗi).*"),
    ("*Figure: NestJS Guards → Gin auth middleware, Interceptors → c.Next() wrappers, Pipes → ShouldBind + validation.*",
     "*Hình: NestJS Guards → Middleware xác thực của Gin, Interceptors → các wrapper bao bọc c.Next(), Pipes → ShouldBind + validation.*"),

    # 07 Recipes - Swagger
    ("Generate OpenAPI specs from Go comments with swag and serve Swagger UI. NestJS has @nestjs/swagger. In Gin, you write special comments above your handlers and run the swag tool to generate static JSON/YAML specs.",
     "Tự động sinh tài liệu đặc tả OpenAPI từ các bình luận trong mã nguồn Go với swag và hiển thị giao diện Swagger UI. NestJS có @nestjs/swagger. Trong Gin, bạn viết các comments đặc biệt ngay phía trên các handler và chạy công cụ swag để tạo tài liệu đặc tả JSON/YAML tĩnh."),
    ("Run `swag init` in your CI/CD pipeline. If you only run it locally and forget to commit the changes, your deployed Swagger UI will show outdated endpoints.",
     "Hãy chạy `swag init` trong quy trình CI/CD của bạn. Nếu bạn chỉ chạy nó dưới local rồi quên commit, giao diện Swagger UI khi deploy lên server sẽ hiển thị tài liệu cũ kỹ."),
    ("Define explicit named structs for all request bodies and responses. Avoid generic `map[string]interface{}` because Swagger cannot parse them, leaving empty schemas for your consumers.",
     "Định nghĩa các struct có tên rõ ràng cho tất cả request body và response. Tránh dùng kiểu chung chung `map[string]interface{}` vì Swagger không thể phân tích cấu trúc, dẫn đến schema trống rỗng đối với client."),
    ("*Figure: Swagger workflow — comment annotations in code → swag tool run → doc generation → served via HTTP endpoint.*",
     "*Hình: Quy trình Swagger — viết chú thích comment trong code → chạy công cụ swag → sinh tài liệu → cung cấp qua HTTP endpoint.*"),

    # 08 Recipes - Health Check
    ("Kubernetes needs two probe types: **liveness** (is the process alive?) and **readiness** (can it accept traffic?). NestJS uses Terminus. In Gin, you write handler functions that ping each dependency (DB, Redis, external APIs) and return a structured JSON response.",
     "Kubernetes cần hai loại probe: **liveness** (tiến trình còn sống không?) và **readiness** (đã sẵn sàng nhận traffic chưa?). NestJS sử dụng Terminus. Trong Gin, bạn tự viết các hàm handler để ping từng dependency (DB, Redis, các API bên ngoài) và trả về phản hồi JSON có cấu trúc."),
    ("Liveness probes must be extremely fast and return immediately. Never perform database or network calls in liveness checks, as a transient database hiccup will trigger unnecessary container restarts.",
     "Liveness probe phải cực kỳ nhanh và trả về ngay lập tức. Tuyệt đối không thực hiện truy vấn DB hoặc gọi network trong liveness probe, vì một sự cố DB tạm thời sẽ kích hoạt việc khởi động lại container không cần thiết."),
    ("Readiness probes must check all critical dependencies (database, cache, queues). If any dependency is down, return a `503 Service Unavailable` status so the load balancer stops routing traffic to this pod.",
     "Readiness probe phải kiểm tra toàn bộ dependencies quan trọng (database, cache, queues). Nếu bất kỳ dependency nào bị sập, hãy trả về mã `503 Service Unavailable` để bộ cân bằng tải ngừng định tuyến traffic tới pod này."),
    ("*Figure: Liveness (/health/live) = process alive, K8s restarts if fails. Readiness (/health/ready) = can serve traffic, checks DB/Redis/external via endpoints.*",
     "*Hình: Liveness (/health/live) = tiến trình còn sống, K8s tự khởi động lại nếu lỗi. Readiness (/health/ready) = sẵn sàng nhận traffic, kiểm tra DB/Redis/external qua các endpoint.*"),
    ("*Figure: Kubelet probes — liveness returns immediately; readiness checks all dependencies and returns 503 if any are down.*",
     "*Hình: Các đầu dò Kubelet — liveness trả về kết quả ngay lập tức; readiness kiểm tra tất cả các phụ thuộc và trả về 503 nếu có bất kỳ phụ thuộc nào bị sập.*"),

    # 09 Recipes - Graceful CQRS
    ("CQRS splits read and write operations into separate handler types. NestJS has `@nestjs/cqrs` with `CommandBus`/`QueryBus`. In Go, you implement this as plain structs with a `Handle(ctx, input)` method — no bus abstraction needed for most projects.",
     "CQRS phân tách các thao tác đọc và ghi thành các kiểu handler riêng biệt. NestJS có `@nestjs/cqrs` với `CommandBus`/`QueryBus`. Trong Go, bạn triển khai việc này bằng các struct thuần túy với phương thức `Handle(ctx, input)` — không cần trừu tượng hóa bus cho hầu hết các dự án."),
    ("Commands return minimal data. A command handler should only return an ID or an error, never the full entity. This keeps write operations lightweight and decoupled.",
     "Commands chỉ nên trả về dữ liệu tối thiểu (như ID hoặc lỗi), tuyệt đối không trả về toàn bộ entity. Điều này giúp các thao tác ghi cực kỳ gọn nhẹ và lỏng lẻo."),
    ("Queries must never mutate state. If a query handler performs database updates or writes, the foundational separation of CQRS is broken.",
     "Queries tuyệt đối không bao giờ được thay đổi trạng thái (mutate state). Nếu một query handler thực hiện cập nhật hoặc ghi dữ liệu vào database, nguyên tắc cốt lõi của CQRS đã bị phá vỡ."),
    ("*Figure: CQRS — Command path (POST/PUT/DELETE → validate → write to primary DB) separated from Query path (GET → read from optimized store/cache). Independent scaling, clear responsibility.*",
     "Hình: CQRS — Đường dẫn Command (POST/PUT/DELETE → validate → ghi vào DB chính) phân tách khỏi đường dẫn Query (GET → đọc từ store/cache tối ưu). Co giãn độc lập, phân định trách nhiệm rõ ràng.*"),
    ("*Figure: CQRS boundary — POST routes go through command handlers (write path); GET routes go through query handlers (read path). Each path can scale independently.*",
     "*Hình: Ranh giới CQRS — các route POST đi qua các handler command (đường ghi); các route GET đi qua các handler query (đường đọc). Mỗi luồng có thể co giãn độc lập.*"),

    # 10 Response - JSON HTML Streaming
    ("Gin provides typed response methods that set Content-Type and serialize data. In NestJS, you rely on interceptors or direct fastify/express handle. In Gin, you use `c.JSON` for APIs, `c.HTML` for templates, and `c.Stream` for streaming data chunk-by-chunk.",
     "Gin cung cấp các phương thức phản hồi được định kiểu giúp tự động thiết lập Content-Type và tuần tự hóa dữ liệu. Trong NestJS, bạn dựa vào các interceptor hoặc xử lý trực tiếp fastify/express. Trong Gin, bạn sử dụng `c.JSON` cho các API, `c.HTML` cho templates và `c.Stream` để truyền phát dòng dữ liệu theo từng block."),
    ("Always specify the HTTP status code before writing raw body data. Once the body is written, headers are flushed and status codes can no longer be changed.",
     "Luôn chỉ định mã trạng thái HTTP trước khi ghi dữ liệu body thô. Một khi body đã được ghi, các header sẽ được đẩy đi và mã trạng thái không thể thay đổi được nữa."),
    ("Never mix JSON responses with raw HTML output in the same request context. This violates client expectations and can lead to parsing errors or security vulnerabilities.",
     "Không bao giờ trộn lẫn phản hồi JSON với đầu ra HTML thô trong cùng một request context. Điều này vi phạm kỳ vọng của client và dễ gây lỗi phân tích cú pháp hoặc lỗ hổng bảo mật."),
    ("*Figure: Four response lanes — JSON API (c.JSON), HTML Template (c.HTML), File Download (c.File/c.FileAttachment), SSE Stream (c.Stream + c.SSEvent). Choose correct lane.*",
     "*Hình: Bốn luồng phản hồi — API JSON (c.JSON), Template HTML (c.HTML), Tải xuống tệp (c.File/c.FileAttachment), SSE Stream (c.Stream + c.SSEvent). Hãy chọn đúng luồng.*"),

    # 11 Response - SSE WebSocket
    ("SSE is one-way (server → client) over HTTP/1.1, perfect for read-only streams. WebSocket is bidirectional, full-duplex over TCP, perfect for real-time games/chat. In NestJS, you use Sse/Gateways; in Gin, you implement these as plain handlers using the standard library or gorilla/websocket.",
     "SSE là truyền dữ liệu một chiều (server → client) qua HTTP/1.1, hoàn hảo cho các luồng dữ liệu chỉ đọc. WebSocket là truyền dữ liệu hai chiều, song công qua TCP, hoàn hảo cho game/chat thời gian thực. Trong NestJS, bạn sử dụng Sse/Gateways; trong Gin, bạn triển khai các handler thuần túy bằng thư viện chuẩn hoặc gorilla/websocket."),
    ("Always handle connection closures gracefully. Leak check: if the client disconnects and the server continues running the event loop, you will quickly run out of memory or goroutines.",
     "Luôn xử lý việc đóng kết nối một cách an toàn. Kiểm tra rò rỉ: nếu client ngắt kết nối mà server vẫn tiếp tục chạy vòng lặp sự kiện, bạn sẽ sớm bị cạn kiệt bộ nhớ hoặc goroutine."),
    ("Use appropriate write deadlines for WebSockets to prevent slow-loris clients from holding connection slots indefinitely.",
     "Sử dụng write deadlines phù hợp cho WebSockets để ngăn các client kết nối chậm chạp (slow-loris) giữ các slot kết nối vô thời hạn."),
    ("*Figure: SSE vs WebSocket — SSE (one-way server-sent text stream over HTTP/1.1) vs WebSocket (two-way full-duplex TCP socket). Choose unidirectional vs bidirectional.*",
     "*Hình: SSE vs WebSocket — SSE (luồng dữ liệu chữ một chiều từ server qua HTTP/1.1) vs WebSocket (socket TCP hai chiều song công). Lựa chọn giữa truyền dữ liệu một chiều và hai chiều.*"),
    ("*Figure: SSE client-server streaming flow — client connects → server flushes headers → server enters loop writing events → client disconnects → context close detected.*",
     "*Hình: Luồng stream SSE client-server — client kết nối → server đẩy headers → server đi vào vòng lặp ghi các sự kiện → client ngắt kết nối → phát hiện đóng context.*"),

    # 12 Routing - Groups Params
    ("Gin’s `RouterGroup` lets you prefix routes, attach middleware to subsets, and nest groups for resource hierarchies. Without groups, every route repeats prefixes and middleware wiring, leading to boilerplate and errors.",
     "`RouterGroup` của Gin giúp bạn thêm tiền tố cho các route, gán middleware cho các nhóm nhỏ và lồng các nhóm cho cấu trúc phân cấp tài nguyên. Nếu không có nhóm, mọi route đều phải lặp lại tiền tố và liên kết middleware, dẫn đến mã nguồn lặp lại và dễ phát sinh lỗi."),
    ("Always register global middleware before registering any route groups. Middleware registered after route definition will not apply to those routes.",
     "Luôn đăng ký middleware toàn cục trước khi định nghĩa các nhóm route. Middleware đăng ký sau khi route được định nghĩa sẽ không có tác dụng với route đó."),
    ("Ensure wildcard routes (like `/*filepath`) do not overlap with static path definitions, as this can cause routing ambiguity and unpredictable matching.",
     "Đảm bảo các route ký tự đại diện (như `/*filepath`) không bị trùng lắp với các đường dẫn tĩnh cố định, vì điều này sẽ gây nhập nhằng định tuyến và kết quả khớp không như mong muốn."),
    ("*Figure: Route groups hierarchy — root router -> API group -> v1 sub-group (with auth) -> users / products. Shared prefix and middleware inheritance.*",
     "*Hình: Cấu trúc phân cấp Router Group — router gốc -> nhóm API -> nhóm con v1 (với xác thực auth) -> users / products. Sử dụng chung tiền tố và kế thừa middleware.*"),

    # 13 Routing - Versioning Redirect
    ("Breaking API changes destroy existing clients. Gin has no built-in versioning primitive like NestJS’s URI/Header strategies. In Gin, you build versioning manually using `RouterGroup` hierarchy or custom header routing middleware.",
     "Thay đổi lớn trên API có thể phá hỏng các client hiện tại. Gin không có sẵn cơ chế phiên bản tích hợp như chiến lược URI/Header của NestJS. Trong Gin, bạn xây dựng phiên bản thủ công bằng cách sử dụng cấu trúc phân cấp `RouterGroup` hoặc middleware định tuyến qua header tùy chỉnh."),
    ("Version your APIs explicitly in the URL path or headers from day one. Avoid ad-hoc version checks or quick patches inside handlers, as they turn your codebase into spaghetti.",
     "Đánh phiên bản API của bạn rõ ràng trên URL path hoặc headers ngay từ ngày đầu tiên. Tránh các bước kiểm tra phiên bản tùy tiện hoặc các bản vá nhanh bên trong handler, vì chúng sẽ biến code của bạn thành một đống rối rắm."),
    ("When performing permanent redirects (301), be cautious because browsers cache them aggressively. If you make a mistake, clients will be stuck redirecting to the wrong URL.",
     "Khi thực hiện chuyển hướng vĩnh viễn (301), hãy cẩn trọng vì trình duyệt cache chúng rất lâu. Nếu cấu hình sai, client sẽ bị kẹt chuyển hướng sang URL lỗi vĩnh viễn."),
    ("*Figure: API Versioning — Path versioning (GET /api/v1/users) vs Header versioning (Accept: application/vnd.company.v1+json). Tradeoffs.*",
     "*Hình: Đánh phiên bản API — Đánh phiên bản qua Path (GET /api/v1/users) vs Đánh phiên bản qua Header (Accept: application/vnd.company.v1+json). So sánh đánh đổi.*")
]

def highlight_go(code):
    keywords = {
        "package", "import", "func", "struct", "interface", "type", "return", "go", "defer",
        "if", "else", "nil", "var", "make", "chan", "select", "case", "range", "for", "switch",
        "default", "const", "map", "break", "continue"
    }
    types = {
        "Context", "Engine", "string", "int", "int64", "bool", "Time", "error", "byte",
        "HandlerFunc", "Server", "any", "float64", "float32", "uint64", "uint32", "RWMutex",
        "Mutex", "WaitGroup", "Validate", "FieldLevel", "BookingRequest", "CreateUserRequest",
        "UpdateUserRequest", "UserResponse", "ListUsersQuery", "UserURI", "H", "RouterGroup",
        "Client"
    }
    
    # Escape HTML
    code = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    comments = []
    strings = []
    
    def store_block_comment(match):
        comments.append(match.group(0))
        return f"__BLOCK_COMMENT_{len(comments)-1}__"
        
    def store_line_comment(match):
        comments.append(match.group(0))
        return f"__LINE_COMMENT_{len(comments)-1}__"
        
    def store_string(match):
        strings.append(match.group(0))
        return f"__STRING_{len(strings)-1}__"
        
    # Replace literals to protect them during syntax highlighting
    code = re.sub(r'/\*.*?\*/', store_block_comment, code, flags=re.DOTALL)
    code = re.sub(r'//.*', store_line_comment, code)
    code = re.sub(r'`[^`]*`', store_string, code)
    code = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', store_string, code)
    
    # Highlight numbers
    code = re.sub(r'\b(\d+)\b', r'<span class="num">\1</span>', code)
    
    # Highlight keywords & types
    def repl_word(match):
        word = match.group(0)
        if word in keywords:
            return f'<span class="kw">{word}</span>'
        elif word in types:
            return f'<span class="tp">{word}</span>'
        return word
        
    code = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', repl_word, code)
    code = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)(?=\()', r'<span class="fn">\1</span>', code)
    
    # Restore literals
    for i, s in enumerate(strings):
        code = code.replace(f"__STRING_{i}__", f'<span class="str">{s}</span>')
    for i, c in enumerate(comments):
        if c.startswith("//"):
            code = code.replace(f"__LINE_COMMENT_{i}__", f'<span class="cm">{c}</span>')
        else:
            code = code.replace(f"__BLOCK_COMMENT_{i}__", f'<span class="cm">{c}</span>')
            
    return code

def translate_text(text):
    for key, val in TRANSLATIONS.items():
        text = text.replace(key, val)
    for key, val in SEVERITY_MAP.items():
        text = text.replace(key, val)
    return text

def parse_markdown_table(table_text):
    lines = table_text.strip().split("\n")
    if len(lines) < 3:
        return ""
    headers = [col.strip() for col in lines[0].split("|")[1:-1]]
    rows = []
    for line in lines[2:]:
        if "|" in line:
            rows.append([col.strip() for col in line.split("|")[1:-1]])
            
    headers = [translate_text(h) for h in headers]
    html = '<table class="dtable"><thead><tr>'
    for h in headers:
        html += f'<th>{h}</th>'
    html += '</tr></thead><tbody>'
    for r in rows:
        html += '<tr>'
        for col in r:
            col_translated = translate_text(col)
            col_translated = re.sub(r'`([^`]+)`', r'<code>\1</code>', col_translated)
            html += f'<td>{col_translated}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

def parse_markdown_file(file_path):
    full_path = os.path.join(SOURCE_DIR, file_path)
    if not os.path.exists(full_path):
        return {}
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Programmatically fix merged headings (e.g. ```## 3. MÃ -> ```\n## 3. MÃ)
    content = re.sub(r'```##\s*([0-6]\.)', r'```\n## \1', content)
    
    # Programmatically fix merged subheadings (e.g. ### Ví dụ 1...```go -> ### Ví dụ 1...\n```go)
    content = re.sub(r'(### [^\n]+)```([a-zA-Z0-9_-]+)', r'\1\n```\2', content)
        
    # Strip any leading HTML comments that might prepend the title on the same line
    clean_content_for_title = re.sub(r'<!--.*?-->', '', content).strip()
    title_match = re.search(r'^#\s*(.*)', clean_content_for_title, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Chapter"
    
    # Remove emojis from title for cleaner tab name
    clean_title = re.sub(r'[^\w\s—\-\&,]', '', title).strip()
    
    # 1. DEFINE (numeric match)
    define_match = re.search(r'## 1\.[^\n]*\n(.*?)(?=## 2\.|\Z)', content, re.DOTALL)
    define_table = ""
    define_intro = ""
    define_invariants = ""
    if define_match:
        sec = define_match.group(1)
        t_match = re.search(r'(\|.*\|.*?)\n(?=\n|\S)', sec, re.DOTALL)
        if t_match:
            define_table = parse_markdown_table(t_match.group(1))
            define_intro = sec.split(t_match.group(0))[0].strip()
        else:
            define_intro = sec.strip()
        inv_match = re.search(r'### Key Invariants\s*(.*?)(?=##|\Z)', sec, re.DOTALL)
        if inv_match:
            invs = inv_match.group(1).strip()
            inv_items = re.findall(r'^- (.*)', invs, flags=re.MULTILINE)
            inv_html = "".join([f"<li>{translate_text(item)}</li>" for item in inv_items])
            define_invariants = f'''
            <div class="note n-warn" style="margin-top:16px;">
                <div class="note-icon">⚠️</div>
                <div><strong>Nguyên tắc bất biến quan trọng:</strong><ul style="margin-left:20px;margin-top:8px;">{inv_html}</ul></div>
            </div>
            '''

    # 2. VISUAL (numeric match with finditer for multiple images and diagrams)
    visual_match = re.search(r'## 2\.[^\n]*\n(.*?)(?=## 3\.|\Z)', content, re.DOTALL)
    png_tag = ""
    visual_intro = ""
    mermaid_tag = ""
    if visual_match:
        sec = visual_match.group(1).strip()
        
        # Extract all visual PNG images
        img_matches = re.finditer(r'!\[(.*?)\]\(\.(.*?)\)', sec)
        png_tags = []
        for im in img_matches:
            alt = im.group(1)
            url = im.group(2).lstrip("/")
            filename = os.path.basename(url)
            target_url = f"../../public/images/{filename}"
            png_tags.append(f'''
            <div class="concept-img-wrapper" style="margin: 28px 0; text-align: center;">
                <img src="{target_url}" alt="{alt}" loading="lazy" style="max-width:100%; border-radius:10px; border:1px solid var(--border); box-shadow:0 8px 30px rgba(0,0,0,0.4);" />
                <div class="concept-img-caption" style="font-size:12px; color:var(--text-muted); margin-top:10px; font-style:italic;">Hình: {alt}</div>
            </div>
            ''')
        png_tag = "\n".join(png_tags)
        
        # Extract all Mermaid diagrams
        mermaid_tags = []
        mermaid_matches = re.finditer(r'```mermaid(.*?)```', sec, re.DOTALL)
        for mm in mermaid_matches:
            mermaid_tags.append(f'''
            <div class="diagram-box" style="margin-top:20px; background:var(--bg-card); border:1px solid var(--border); border-radius:12px; padding:20px; overflow:hidden;">
                <div class="diagram-title" style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.1em; color:var(--text-muted); margin-bottom:16px; font-family:var(--font-mono); text-align:center;">Sơ đồ luồng hoạt động (Mermaid Workflow)</div>
                <pre class="mermaid" style="background:transparent; padding:0; text-align:center;">
{mm.group(1).strip()}
                </pre>
            </div>
            ''')
        mermaid_tag = "\n".join(mermaid_tags)
        
        # Render visual prose
        prose_sec = re.sub(r'!\[.*?\]\(.*?\)', '', sec)
        prose_sec = re.sub(r'```mermaid.*?```', '', prose_sec, flags=re.DOTALL).strip()
        visual_intro = prose_sec
        
    # 3. CODE (numeric match)
    code_match = re.search(r'## 3\.[^\n]*\n(.*?)(?=## 4\.|\Z)', content, re.DOTALL)
    examples = []
    if code_match:
        sec = code_match.group(1).strip()
        ex_matches = re.finditer(r'### (.*?)\n(.*?)(?=### |\Z)', sec, re.DOTALL)
        for m in ex_matches:
            ex_title = m.group(1).strip()
            ex_body = m.group(2).strip()
            
            block_match = re.search(r'```go(.*?)```', ex_body, re.DOTALL)
            ex_desc = re.sub(r'```go.*?```', '', ex_body, flags=re.DOTALL).strip()
            
            code_html = ""
            if block_match:
                raw_code = block_match.group(1).strip()
                filename = "main.go"
                fn_match = re.search(r'//\s*(.*?\.(?:go|json|yaml))', raw_code)
                if fn_match:
                    filename = fn_match.group(1).strip()
                highlighted = highlight_go(raw_code)
                code_html = f'''
                <div class="code-block" style="margin-top:16px;">
                    <div class="code-hdr">
                        <span class="code-lang">GO</span>
                        <span class="code-file">{filename}</span>
                        <button class="code-copy">Copy</button>
                    </div>
                    <pre><code>{highlighted}</code></pre>
                </div>
                '''
            examples.append({
                "title": ex_title,
                "description": ex_desc,
                "code_html": code_html
            })

    # 4. PITFALLS (numeric match)
    pitfalls_match = re.search(r'## 4\.[^\n]*\n(.*?)(?=## 5\.|\Z)', content, re.DOTALL)
    pitfalls_table = ""
    if pitfalls_match:
        sec = pitfalls_match.group(1).strip()
        t_match = re.search(r'(\|.*\|.*?)\n(?=\n|\S)', sec, re.DOTALL)
        if t_match:
            pitfalls_table = parse_markdown_table(t_match.group(1))

    # 5. REF (numeric match)
    ref_match = re.search(r'## 5\.[^\n]*\n(.*?)(?=## 6\.|\Z)', content, re.DOTALL)
    ref_table = ""
    if ref_match:
        sec = ref_match.group(1).strip()
        t_match = re.search(r'(\|.*\|.*?)\n(?=\n|\S)', sec, re.DOTALL)
        if t_match:
            ref_table = parse_markdown_table(t_match.group(1))

    # 6. RECOMMEND (numeric match)
    rec_match = re.search(r'## 6\.[^\n]*\n(.*?)(?=\Z)', content, re.DOTALL)
    rec_table = ""
    if rec_match:
        sec = rec_match.group(1).strip()
        t_match = re.search(r'(\|.*\|.*?)\n(?=\n|\S)', sec, re.DOTALL)
        if t_match:
            rec_table = parse_markdown_table(t_match.group(1))

    return {
        "title": title,
        "clean_title": clean_title,
        "define_intro": define_intro,
        "define_table": define_table,
        "define_invariants": define_invariants,
        "png_tag": png_tag,
        "mermaid_tag": mermaid_tag,
        "visual_intro": visual_intro,
        "examples": examples,
        "pitfalls_table": pitfalls_table,
        "ref_table": ref_table,
        "rec_table": rec_table
    }

def build():
    sidebar_items_html = ""
    topnav_items_html = ""
    sections_html = ""
    
    current_category = ""
    for idx, item in enumerate(MAPPING):
        sec_data = parse_markdown_file(item["path"])
        if not sec_data:
            print(f"Error parsing {item['path']}")
            continue
            
        if item["category"] != current_category:
            current_category = item["category"]
            sidebar_items_html += f'<div class="nav-section-title">{current_category}</div>\n'
            
        active_class = " active" if idx == 0 else ""
        sidebar_items_html += f'<button class="nav-item{active_class}" data-target="{item["id"]}">{sec_data["title"]}</button>\n'
        topnav_items_html += f'<button class="tnav{active_class}" data-target="{item["id"]}">{sec_data["clean_title"]}</button>\n'
        
        # Build Section HTML
        examples_html = ""
        for ex_idx, ex in enumerate(sec_data["examples"]):
            examples_html += f'''
            <div class="card">
                <div class="card-title" style="color:var(--accent-green); display:flex; align-items:center; gap:8px;">
                    <span class="badge b-basic" style="font-size:10px; padding:2px 8px;">VÍ DỤ {ex_idx+1}</span>
                    {ex["title"]}
                </div>
                <p class="prose" style="margin-top:8px; font-size:13.5px; line-height:1.6;">{ex["description"]}</p>
                {ex["code_html"]}
            </div>
            '''
            
        pitfalls_section = ""
        if sec_data["pitfalls_table"]:
            pitfalls_section = f'''
            <div class="divider"></div>
            <div class="card" style="border-color:rgba(255,107,107,0.2); background:rgba(255,107,107,0.01);">
                <div class="card-title" style="color:var(--accent-coral); font-family:var(--font-mono); font-size:13px; text-transform:uppercase; letter-spacing:0.08em; display:flex; align-items:center; gap:8px;">
                    <span>⚠️ Các lỗi thường gặp & Phòng tránh (Pitfalls)</span>
                </div>
                <div style="margin-top:12px;">{sec_data["pitfalls_table"]}</div>
            </div>
            '''
            
        ref_rec_section = ""
        if sec_data["ref_table"] or sec_data["rec_table"]:
            ref_rec_section = f'''
            <div class="card" style="margin-top:28px; background:rgba(255,255,255,0.01); border-style:dashed;">
                <div class="card-title" style="color:var(--text-muted); font-family:var(--font-mono); font-size:12px; text-transform:uppercase; letter-spacing:0.08em;">🔗 Tài liệu tham khảo & Bước tiếp theo (Reference & Recommend)</div>
                {f'<div style="font-size:12px; font-weight:600; margin-bottom:8px; margin-top:12px; color:var(--text-secondary);">TÀI LIỆU KHUYÊN ĐỌC:</div>{sec_data["ref_table"]}' if sec_data["ref_table"] else ''}
                {f'<div style="font-size:12px; font-weight:600; margin-bottom:8px; margin-top:16px; color:var(--text-secondary);">CHỦ ĐỀ KẾ TIẾP:</div>{sec_data["rec_table"]}' if sec_data["rec_table"] else ''}
            </div>
            '''

        sections_html += f'''
        <!-- ===== SECTION: {item["id"]} ===== -->
        <section class="page-section{active_class}" id="s-{item["id"]}">
            <div class="sec-header">
                <div class="sec-num">{idx+1:02d}</div>
                <div>
                    <div class="sec-title">{sec_data["title"]}</div>
                    <div class="sec-sub">Chủ đề {idx+1:02d} chuyên sâu trong lộ trình phát triển Gin Framework</div>
                </div>
                <span class="badge b-expert" style="margin-left:auto;">{item["badge"]}</span>
            </div>
            
            <div class="concept-box">
                <div class="label">📖 Khái niệm & Định nghĩa</div>
                <div class="ctitle">{sec_data["title"]}</div>
                <p class="prose">{sec_data["define_intro"]}</p>
                {sec_data["define_table"]}
                {sec_data["define_invariants"]}
            </div>
            
            <h3>Mã nguồn & Các ví dụ minh họa</h3>
            {examples_html}
            
            <div class="divider"></div>
            <h3>Sơ đồ trực quan & Luồng hoạt động (Visual Support)</h3>
            <p class="prose">{sec_data["visual_intro"]}</p>
            {sec_data["png_tag"]}
            {sec_data["mermaid_tag"]}
            
            {pitfalls_section}
            {ref_rec_section}
        </section>
        '''

    full_html = f'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gin Framework — Hướng dẫn chuyên sâu từ Basics đến Expert</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{{
  --bg-primary:#0d0f14;
  --bg-secondary:#131720;
  --bg-card:#1a1f2e;
  --bg-code:#0f1319;
  --accent-cyan:#00d4ff;
  --accent-green:#00ff88;
  --accent-purple:#a855f7;
  --accent-amber:#f59e0b;
  --accent-coral:#ff6b6b;
  --text-primary:#e2e8f0;
  --text-secondary:#94a3b8;
  --text-muted:#64748b;
  --border:rgba(255,255,255,0.07);
  --font-mono:'JetBrains Mono',monospace;
  --font-sans:'Inter',sans-serif;
}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{
  background:var(--bg-primary);
  color:var(--text-primary);
  font-family:var(--font-sans);
  display:flex;
  min-height:100vh;
  overflow-x:hidden;
}}
#sidebar{{
  width:270px;
  min-width:270px;
  background:var(--bg-secondary);
  border-right:1px solid var(--border);
  position:fixed;
  top:0;
  left:0;
  bottom:0;
  overflow-y:auto;
  z-index:100;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}
#sidebar::-webkit-scrollbar{{width:4px}}
#sidebar::-webkit-scrollbar-thumb{{background:var(--border);border-radius:2px}}
.sidebar-logo{{
  padding:20px;
  border-bottom:1px solid var(--border);
  display:flex;
  align-items:center;
  gap:10px;
}}
.logo-icon{{
  width:32px;
  height:32px;
  background:linear-gradient(135deg,var(--accent-cyan),var(--accent-purple));
  border-radius:8px;
  display:flex;
  align-items:center;
  justify-content:center;
  font-size:13px;
  font-weight:700;
  color:#fff;
  font-family:var(--font-mono);
}}
.logo-text{{
  font-size:14px;
  font-weight:600;
  color:var(--text-primary);
  line-height:1.2;
}}
.logo-sub{{
  font-size:11px;
  color:var(--accent-cyan);
  font-family:var(--font-mono);
}}
.nav-section{{padding:14px 12px 6px}}
.nav-section-title{{
  font-size:10px;
  font-weight:600;
  text-transform:uppercase;
  letter-spacing:.08em;
  color:var(--text-muted);
  padding:0 8px;
  margin-bottom:6px;
  margin-top:14px;
}}
.nav-item{{
  display:flex;
  align-items:center;
  padding:8px 10px;
  border-radius:6px;
  color:var(--text-secondary);
  font-size:13px;
  cursor:pointer;
  transition:all .15s;
  border:none;
  background:none;
  width:100%;
  text-align:left;
  gap:8px;
  line-height:1.4;
}}
.nav-item:hover{{background:rgba(255,255,255,.04);color:var(--text-primary)}}
.nav-item.active{{
  background:rgba(0,212,255,.08);
  color:var(--accent-cyan);
  border-left:3px solid var(--accent-cyan);
  padding-left:7px;
  font-weight:500;
}}
#topnav{{
  position:fixed;
  top:0;
  left:270px;
  right:0;
  height:52px;
  background:var(--bg-secondary);
  border-bottom:1px solid var(--border);
  display:flex;
  align-items:center;
  padding:0 24px;
  gap:6px;
  z-index:50;
  overflow-x:auto;
}}
#topnav::-webkit-scrollbar{{height:0}}
.tnav{{
  padding:5px 12px;
  border-radius:6px;
  font-size:12px;
  font-weight:500;
  color:var(--text-secondary);
  cursor:pointer;
  white-space:nowrap;
  border:none;
  background:none;
  transition:all .15s;
}}
.tnav:hover{{color:var(--text-primary);background:rgba(255,255,255,.05)}}
.tnav.active{{color:var(--accent-cyan);background:rgba(0,212,255,.1)}}

#main{{
  margin-left:270px;
  margin-top:52px;
  flex:1;
  min-width:0;
}}
.content-area{{
  padding:44px 52px;
  max-width:1000px;
  margin:0 auto;
}}
.page-section{{display:none}}
.page-section.active{{
  display:block;
  animation: fadeIn 0.25s ease-out;
}}
@keyframes fadeIn {{
  from {{ opacity: 0; transform: translateY(8px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
.sec-header{{
  display:flex;
  align-items:center;
  gap:14px;
  margin-bottom:28px;
  padding-bottom:18px;
  border-bottom:1px solid var(--border);
}}
.sec-num{{
  width:38px;
  height:38px;
  border-radius:8px;
  background:linear-gradient(135deg,var(--accent-cyan),var(--accent-purple));
  display:flex;
  align-items:center;
  justify-content:center;
  font-family:var(--font-mono);
  font-size:15px;
  font-weight:700;
  color:#fff;
  flex-shrink:0;
}}
.sec-title{{font-size:24px;font-weight:700;color:var(--text-primary)}}
.sec-sub{{font-size:13px;color:var(--text-muted);margin-top:3px}}
.badge{{
  padding:3px 9px;
  border-radius:16px;
  font-size:11px;
  font-weight:600;
  letter-spacing:.04em;
  font-family:var(--font-mono);
  display:inline-block;
}}
.b-basic{{background:rgba(0,255,136,.08);color:var(--accent-green);border:1px solid rgba(0,255,136,.2)}}
.b-advanced{{background:rgba(245,158,11,.08);color:var(--accent-amber);border:1px solid rgba(245,158,11,.2)}}
.b-expert{{background:rgba(168,85,247,.1);color:var(--accent-purple);border:1px solid rgba(168,85,247,.25)}}

.prose{{font-size:15px;line-height:1.8;color:var(--text-secondary);margin-bottom:18px}}
.prose strong{{color:var(--text-primary);font-weight:600}}
.prose code{{
  background:rgba(0,212,255,.08);
  color:var(--accent-cyan);
  padding:2px 6px;
  border-radius:4px;
  font-family:var(--font-mono);
  font-size:13.5px;
}}
h3{{font-size:18px;font-weight:600;color:var(--text-primary);margin:32px 0 14px}}
.concept-box{{
  background:linear-gradient(135deg,rgba(0,212,255,.03),rgba(168,85,247,.03));
  border:1px solid rgba(0,212,255,.15);
  border-radius:12px;
  padding:22px;
  margin-bottom:28px;
}}
.concept-box .label{{
  font-size:10px;
  font-weight:700;
  text-transform:uppercase;
  letter-spacing:.1em;
  color:var(--accent-cyan);
  margin-bottom:6px;
  font-family:var(--font-mono);
}}
.concept-box .ctitle{{font-size:19px;font-weight:700;color:var(--text-primary);margin-bottom:12px}}
.card{{
  background:var(--bg-card);
  border:1px solid var(--border);
  border-radius:10px;
  padding:22px;
  margin-bottom:20px;
  transition:border-color .2s;
}}
.card:hover{{border-color:rgba(0,212,255,.2)}}
.card-title{{font-size:15px;font-weight:600;color:var(--text-primary);margin-bottom:12px}}
.code-block{{
  background:var(--bg-code);
  border:1px solid var(--border);
  border-radius:10px;
  overflow:hidden;
  margin-top:16px;
  margin-bottom:16px;
}}
.code-hdr{{
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:10px 16px;
  border-bottom:1px solid var(--border);
  background:rgba(255,255,255,.01);
}}
.code-lang{{
  font-size:11px;
  font-weight:600;
  color:var(--accent-cyan);
  font-family:var(--font-mono);
  text-transform:uppercase;
  letter-spacing:.08em;
}}
.code-file{{font-size:11px;color:var(--text-muted);font-family:var(--font-mono)}}
.code-copy{{
  font-size:11px;
  cursor:pointer;
  background:none;
  border:1px solid var(--border);
  border-radius:4px;
  padding:3px 9px;
  color:var(--text-secondary);
  transition:all .15s;
}}
.code-copy:hover{{border-color:var(--accent-cyan);color:var(--accent-cyan)}}
pre{{
  margin:0;
  padding:20px;
  overflow-x:auto;
  font-family:var(--font-mono);
  font-size:12.5px;
  line-height:1.75;
}}
pre::-webkit-scrollbar{{height:4px}}
pre::-webkit-scrollbar-thumb{{background:var(--border);border-radius:2px}}
.kw{{color:#c084fc}}.fn{{color:#60a5fa}}.str{{color:#86efac}}.cm{{color:#4b5563;font-style:italic}}.num{{color:#fb923c}}.tp{{color:#67e8f9}}.pkg{{color:#a78bfa}}.op{{color:#f472b6}}

.note{{
  display:flex;
  gap:12px;
  padding:14px 16px;
  border-radius:8px;
  margin-bottom:16px;
  font-size:13.8px;
  line-height:1.6;
}}
.n-info{{background:rgba(0,255,136,.05);border:1px solid rgba(0,255,136,.2);color:var(--accent-green)}}
.n-warn{{background:rgba(245,158,11,.06);border:1px solid rgba(245,158,11,.2);color:#fcd34d}}
.note-icon{{font-size:16px;flex-shrink:0}}

.diagram-box{{
  background:var(--bg-card);
  border:1px solid var(--border);
  border-radius:12px;
  padding:20px;
  margin-bottom:24px;
  overflow:hidden;
}}
.diagram-title{{
  font-size:10px;
  font-weight:700;
  text-transform:uppercase;
  letter-spacing:.1em;
  color:var(--text-muted);
  margin-bottom:16px;
  font-family:var(--font-mono);
  text-align:center;
}}
table.dtable{{
  width:100%;
  border-collapse:collapse;
  margin-bottom:20px;
  margin-top:14px;
  font-size:13.5px;
}}
table.dtable th{{
  padding:10px 14px;
  text-align:left;
  background:rgba(255,255,255,.02);
  border-bottom:1px solid var(--border);
  color:var(--text-muted);
  font-size:11px;
  text-transform:uppercase;
  letter-spacing:.05em;
  font-weight:600;
}}
table.dtable td{{
  padding:10px 14px;
  border-bottom:1px solid var(--border);
  color:var(--text-secondary);
  line-height:1.6;
}}
table.dtable tr:hover td{{background:rgba(255,255,255,.015)}}
table.dtable td code{{
  background:rgba(0,212,255,.08);
  color:var(--accent-cyan);
  padding:2px 5px;
  border-radius:3px;
  font-family:var(--font-mono);
  font-size:12px;
}}

.divider{{border:none;border-top:1px solid var(--border);margin:32px 0}}

.concept-img-wrapper{{
  margin:20px 0;
  border-radius:12px;
  overflow:hidden;
  border:1px solid rgba(0,212,255,0.2);
  box-shadow:0 4px 20px rgba(0,0,0,0.35);
  background:var(--bg-card);
  padding:12px;
}}
.concept-img-wrapper img{{display:block;width:100%;height:auto;border-radius:8px}}
.concept-img-caption{{
  text-align:center;
  font-size:12.5px;
  color:var(--text-secondary);
  margin-top:10px;
  font-style:italic;
}}

/* Hamburgermenu */
#mobile-bar{{
  display:none;
  position:fixed;
  top:0;
  left:0;
  right:0;
  height:52px;
  background:var(--bg-secondary);
  border-bottom:1px solid var(--border);
  align-items:center;
  padding:0 16px;
  justify-content:space-between;
  z-index:150;
}}
.hamburger{{
  background:none;
  border:none;
  cursor:pointer;
  width:32px;
  height:32px;
  display:flex;
  flex-direction:column;
  justify-content:center;
  gap:5px;
}}
.hamburger span{{
  display:block;
  width:22px;
  height:2px;
  background:var(--text-primary);
  border-radius:1px;
  transition:all 0.25s ease;
}}
#sidebar-overlay{{
  display:none;
  position:fixed;
  top:0;
  left:0;
  right:0;
  bottom:0;
  background:rgba(0,0,0,0.5);
  z-index:90;
  backdrop-filter:blur(2px);
}}

@media (max-width:992px){{
  #sidebar{{
    transform: translateX(-100%);
  }}
  #sidebar.open{{
    transform: translateX(0);
  }}
  #sidebar-overlay.open{{
    display:block;
  }}
  #topnav{{
    left:0;
    top:52px;
    padding:0 16px;
  }}
  #main{{
    margin-left:0;
    margin-top:104px;
  }}
  .content-area{{
    padding:28px 20px;
  }}
  #mobile-bar{{
    display:flex;
  }}
}}
</style>
</head>
<body>

<!-- MOBILE BAR -->
<div id="mobile-bar">
  <button class="hamburger">
    <span></span>
    <span></span>
    <span></span>
  </button>
  <div style="display:flex; align-items:center; gap:8px;">
    <div class="logo-icon" style="width:26px; height:26px; font-size:11px;">Gin</div>
    <span class="logo-text" style="font-size:13px;">Gin Expert Guide</span>
  </div>
  <div style="width:32px;"></div>
</div>

<!-- OVERLAY -->
<div id="sidebar-overlay"></div>

<!-- SIDEBAR -->
<nav id="sidebar">
  <div class="sidebar-logo">
    <div class="logo-icon">Gin</div>
    <div>
      <div class="logo-text">Gin Expert Guide</div>
      <div class="logo-sub">// basics to expert</div>
    </div>
  </div>
  <div class="nav-section">
    {sidebar_items_html}
  </div>
</nav>

<!-- TOP NAV -->
<nav id="topnav">
  {topnav_items_html}
</nav>

<!-- MAIN -->
<main id="main">
  <div class="content-area">
    {sections_html}
  </div>
</main>

<script>
function show(targetId) {{
  // Hide all sections
  const sections = document.querySelectorAll('.page-section');
  sections.forEach(s => s.classList.remove('active'));
  
  // Show target section
  const target = document.getElementById('s-' + targetId);
  if (target) target.classList.add('active');
  
  // Update sidebar active state
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {{
    if (item.getAttribute('data-target') === targetId) {{
      item.classList.add('active');
    }} else {{
      item.classList.remove('active');
    }}
  }});
  
  // Update topnav active state
  const tnavs = document.querySelectorAll('.tnav');
  tnavs.forEach(item => {{
    if (item.getAttribute('data-target') === targetId) {{
      item.classList.add('active');
    }} else {{
      item.classList.remove('active');
    }}
  }});
  
  // Sync hash in URL
  try {{
    if (history.replaceState) {{
      history.replaceState(null, null, '#s-' + targetId);
    }} else {{
      location.hash = '#s-' + targetId;
    }}
  }} catch (e) {{}}
  
  // Auto scroll top
  window.scrollTo({{ top: 0, behavior: 'smooth' }});
  
  // Close sidebar on mobile
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  if (sidebar.classList.contains('open')) {{
    sidebar.classList.remove('open');
    overlay.classList.remove('open');
  }}
}}

function toggleSidebar() {{
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  sidebar.classList.toggle('open');
  overlay.classList.toggle('open');
}}

// Bind click events programmatically to bypass Obsidian stripping inline onclick
function bindObsidianEvents() {{
  document.querySelectorAll('[data-target]').forEach(el => {{
    el.addEventListener('click', function(e) {{
      e.preventDefault();
      const targetId = el.getAttribute('data-target');
      if (targetId) show(targetId);
    }});
  }});
  
  const hamburger = document.querySelector('.hamburger');
  if (hamburger) {{
    hamburger.addEventListener('click', toggleSidebar);
  }}
  
  const overlay = document.getElementById('sidebar-overlay');
  if (overlay) {{
    overlay.addEventListener('click', toggleSidebar);
  }}
  
  document.querySelectorAll('.code-copy').forEach(btn => {{
    btn.addEventListener('click', function() {{
      const pre = btn.parentElement.nextElementSibling;
      if (pre) {{
        navigator.clipboard.writeText(pre.innerText);
        btn.innerText = 'Copied!';
        setTimeout(() => btn.innerText = 'Copy', 2000);
      }}
    }});
  }});
}}

// On initial DOM load, automatically activate correct section if a hash is present
function initRouter() {{
  bindObsidianEvents();
  const hash = window.location.hash;
  if (hash.startsWith('#s-')) {{
    show(hash.replace('#s-', ''));
  }} else {{
    const activeSec = document.querySelector('.page-section.active');
    if (activeSec) {{
      const activeId = activeSec.id.replace('s-', '');
      show(activeId);
    }}
  }}
}}

if (document.readyState === 'loading') {{
  window.addEventListener('DOMContentLoaded', initRouter);
}} else {{
  initRouter();
}}

// Sync layout dynamically if hash changes in the URL
window.addEventListener('hashchange', () => {{
  const hash = window.location.hash;
  if (hash.startsWith('#s-')) {{
    show(hash.replace('#s-', ''));
  }}
}});
</script>
</body>
</html>
'''
    with open(TARGET_FILE, "w", encoding="utf-8") as f:
        f.write(full_html)
    print("Done! Perfectly clean & enriched HTML guide generated successfully from scratch.")

if __name__ == "__main__":
    build()
