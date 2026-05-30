import re
import os

# Paths
SOURCE_DIR = "/home/mvt/mAIvt/Documents/go/gin"
TARGET_FILE = "/home/mvt/mAIvt/Go/Fundamental/gin-guide.html"

# Mapping of section ID to markdown file path
MAPPING = {
    "engine-context": "basics/01-engine-context-handlers.md",
    "project-struct": "basics/02-project-structure.md",
    "json-validation": "binding/01-json-form-validation.md",
    "file-upload": "binding/02-file-upload-multipart.md",
    "builtin-custom-mw": "middleware/01-builtin-custom.md",
    "guards-interceptors": "middleware/02-guards-interceptors.md",
    "swagger-openapi": "recipes/01-swagger-openapi.md",
    "health-check": "recipes/02-health-check.md",
    "graceful-cqrs": "recipes/03-graceful-cqrs.md",
    "json-html-streaming": "response/01-json-html-streaming.md",
    "sse-websocket": "response/02-sse-websocket.md",
    "groups-params": "routing/01-groups-params.md",
    "versioning-redirect": "routing/02-versioning-redirect.md"
}

# Translations for terminology
TRANSLATIONS = {
    # Table headers
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
    
    # Severity levels
    "🔴 Fatal": "<span class=\"badge badge-expert\" style=\"background:rgba(239,68,68,0.15);color:#f87171;border:1px solid rgba(239,68,68,0.3);\">🔴 FATAL</span>",
    "🔴 Critical": "<span class=\"badge badge-expert\" style=\"background:rgba(239,68,68,0.15);color:#f87171;border:1px solid rgba(239,68,68,0.3);\">🔴 CRITICAL</span>",
    "🟡 Common": "<span class=\"badge badge-advanced\" style=\"background:rgba(245,158,11,0.12);color:#fbbf24;border:1px solid rgba(245,158,11,0.3);\">🟡 COMMON</span>",
    "🟡 Warning": "<span class=\"badge badge-advanced\" style=\"background:rgba(245,158,11,0.12);color:#fbbf24;border:1px solid rgba(245,158,11,0.3);\">🟡 WARNING</span>",
    
    # Text translations
    "Key Invariants": "Nguyên tắc cốt lõi bắt buộc (Invariants)",
    "Request Flow": "Luồng Request",
    "Generation Workflow": "Luồng sinh tài liệu",
    "Execution Order": "Thứ tự thực thi",
    "Before c.Next()": "Trước c.Next()",
    "After c.Next()": "Sau c.Next()",
}

# Go code syntax highlighter
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
    
    # Helper functions to store literals in lists and return unique tokens
    def store_block_comment(match):
        comments.append(match.group(0))
        return f"__BLOCK_COMMENT_{len(comments)-1}__"
        
    def store_line_comment(match):
        comments.append(match.group(0))
        return f"__LINE_COMMENT_{len(comments)-1}__"
        
    def store_string(match):
        strings.append(match.group(0))
        return f"__STRING_{len(strings)-1}__"
        
    # Replace literals with unique tokens to prevent them from being matched as keywords/types
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
    
    # Highlight function calls: word followed by (
    code = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)(?=\()', r'<span class="fn">\1</span>', code)
    
    # Restore strings and comments with proper markup classes
    for i, s in enumerate(strings):
        code = code.replace(f"__STRING_{i}__", f'<span class="str">{s}</span>')
    for i, c in enumerate(comments):
        if c.startswith("//"):
            code = code.replace(f"__LINE_COMMENT_{i}__", f'<span class="cm">{c}</span>')
        else:
            code = code.replace(f"__BLOCK_COMMENT_{i}__", f'<span class="cm">{c}</span>')
            
    return code

def translate_text(text):
    # Perform key translations first
    for key, val in TRANSLATIONS.items():
        text = text.replace(key, val)
        
    # Standard translations using word boundaries to protect path segments and exact code keywords
    translations = [
        (r'\buses\b', 'sử dụng'),
        (r'\buse\b', 'sử dụng'),
        (r'\bpassing\b', 'Truyền'),
        (r'\bcauses\b', 'gây ra'),
        (r'\bmethods\b', 'phương thức'),
        (r'\brules\b', 'quy tắc'),
        (r'\bdecorators\b', 'chú thích (decorators)'),
    ]
    
    # Replace other exact phrases
    exact_phrases = [
        ("every Gin application starts with three primitives", "mọi ứng dụng Gin đều bắt đầu bằng ba nguyên tố cốt lõi"),
        ("creates the router and holds middleware", "khởi tạo bộ định tuyến và chứa middleware"),
        ("carries request data, response writer, and per-request key-value storage", "mang dữ liệu request, bộ ghi response và kho lưu trữ key-value per-request"),
        ("business logic entry point for a single route", "điểm xử lý logic nghiệp vụ cho một route đơn lẻ"),
        ("groups routes under a shared prefix and middleware set", "nhóm các route dưới một tiền tố và tập hợp middleware dùng chung"),
        ("shorthand for", "tên viết tắt của"),
        ("used in JSON responses", "được dùng trong các phản hồi JSON"),
        ("is NOT goroutine-safe", "KHÔNG an toàn cho Goroutine (thread-safe)"),
        ("Passing", "Truyền trực tiếp"),
        ("into a goroutine without", "vào goroutine mà không sử dụng"),
        ("causes data races and panics", "sẽ gây lỗi Data Race và crash runtime panic"),
        ("includes Logger and Recovery middleware", "bao gồm sẵn middleware Logger và Recovery"),
        ("Use", "Sử dụng"),
        ("for a bare engine when you want full control", "để có một engine sạch hoàn toàn khi bạn muốn tự kiểm soát toàn bộ"),
        ("One package per domain concept", "Mỗi khái niệm domain nằm trong một package riêng"),
        ("Import cycles in Go are compile errors, not warnings", "Lỗi Import vòng tròn trong Go sẽ gây lỗi biên dịch chứ không phải cảnh báo"),
        ("Handlers depend on Services, Services depend on Repositories", "Handler phụ thuộc vào Service, Service phụ thuộc vào Repository"),
        ("Never import handlers from services", "Tuyệt đối không import handler từ service"),
        ("Bind JSON/form/URI data to Go structs and validate with", "Bind dữ liệu JSON/form/URI vào struct của Go và xác thực bằng"),
        ("tags powered by", "struct tags vận hành bởi"),
        ("methods decode request data into a struct and run", "giúp decode dữ liệu request vào struct và kích hoạt các quy tắc"),
        ("rules from", "từ"),
        ("one line replaces manual parsing", "chỉ một dòng code thay thế hoàn toàn việc kiểm tra thủ công"),
        ("JSON request body", "Thân Request JSON"),
        ("URL query parameters", "Tham số Query trên URL"),
        ("Path parameters", "Tham số trên Path"),
        ("for custom error responses", "để tự xử lý phản hồi lỗi"),
        ("auto-writes 400", "sẽ tự động ghi HTTP 400"),
        ("Pointer fields + `omitempty` = PATCH semantics", "Các trường con trỏ (Pointer fields) + `omitempty` = ngữ nghĩa PATCH"),
        ("Non-nil means the client sent this field", "Không nil nghĩa là client thực sự gửi trường này"),
        ("Use case", "Trường hợp sử dụng"),
        ("Application", "Cách áp dụng"),
        ("Scope", "Phạm vi"),
        ("Global", "Toàn cục"),
        ("Group", "Nhóm"),
        ("Route", "Định tuyến đơn lẻ"),
        ("Logger, recovery, CORS", "Logger, recovery, CORS"),
        ("Auth for", "Xác thực cho các route"),
        ("routes", ""),
        ("Rate limit on a single endpoint", "Giới hạn tần suất trên một endpoint duy nhất"),
        ("Call `c.Next()` to continue the chain", "Hãy gọi `c.Next()` để tiếp tục chuỗi middleware"),
        ("Without it, downstream handlers never execute", "Nếu không có nó, các handler phía sau sẽ không bao giờ được chạy"),
        ("Call `return` after `c.Abort*()`", "Luôn gọi `return` ngay sau `c.Abort*()`"),
        ("Without `return`, the current middleware continues executing after the abort", "Nếu thiếu `return`, middleware hiện tại vẫn tiếp tục chạy phần code phía sau dù đã abort"),
        ("Generate OpenAPI specs from Go comments with", "Tự động sinh tài liệu OpenAPI từ Go comments bằng"),
        ("serve Swagger UI via", "và hiển thị Swagger UI thông qua"),
        ("decorators", "decorators"),
        ("to auto-generate OpenAPI specs", "để tự động tạo đặc tả OpenAPI"),
        ("reads special comments above handlers and generates", "đọc các comments đặc biệt bên trên handler và sinh ra file"),
        ("The Swagger UI is served by", "Giao diện Swagger UI được cung cấp bởi"),
        ("Run `swag init` in CI", "Chạy `swag init` trong quy trình CI/CD"),
        ("If you generate locally but forget, the deployed spec is stale", "Nếu bạn chỉ chạy ở local rồi quên, tài liệu Swagger trên server sẽ bị cũ"),
        ("Keep annotations near handler code", "Giữ các chú thích annotations ngay sát code handler"),
        ("Moving them to separate files creates drift", "Di chuyển chúng ra file khác sẽ dễ gây lệch thông tin khi thay đổi code"),
        ("Not running `swag init` in CI", "Không chạy `swag init` trong CI"),
        ("Deployed spec is stale; clients implement wrong contracts", "Tài liệu spec trên production bị cũ; client lập trình sai giao tiếp"),
        ("Add `swag init` step to CI pipeline before build", "Thêm bước `swag init` vào pipeline CI trước khi build"),
        ("Using `map[string]interface{}` as response type", "Sử dụng `map[string]interface{}` làm kiểu dữ liệu trả về"),
        ("Swagger shows empty schema; consumers can't validate", "Swagger hiển thị schema trống rỗng; client không thể biết cấu trúc dữ liệu"),
        ("Define named response structs for every endpoint", "Định nghĩa struct response rõ ràng cho từng endpoint"),
        ("Custom Middleware", "Custom Middleware"),
        ("Gin CORS", "Cấu hình CORS trong Gin"),
        ("When you need readiness/liveness probes", "Khi cần các đầu dò trạng thái sẵn sàng/sống sót"),
        ("Expose /health endpoint for orchestrators and load balancers", "Cung cấp endpoint /health cho bộ điều phối (K8s) và cân bằng tải"),
        ("When you need role-based access or structured error handling", "Khi cần phân quyền dựa trên vai trò hoặc xử lý lỗi tập trung"),
        ("Builds on middleware to implement NestJS-style Guards/Interceptors/Filters", "Xây dựng trên middleware để triển khai Guards/Interceptors/Filters kiểu NestJS"),
    ]
    
    for en, vi in exact_phrases:
        text = re.sub(re.escape(en), vi, text, flags=re.IGNORECASE)
        
    for pattern, replacement in translations:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
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
            
    # Translate headers and rows
    headers = [translate_text(h) for h in headers]
    
    html = '<table class="data-table"><thead><tr>'
    for h in headers:
        html += f'<th>{h}</th>'
    html += '</tr></thead><tbody>'
    for r in rows:
        html += '<tr>'
        for col in r:
            col_translated = translate_text(col)
            # Make code tags look beautiful
            col_translated = re.sub(r'`([^`]+)`', r'<code>\1</code>', col_translated)
            html += f'<td>{col_translated}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

def parse_markdown_file(file_path, section_id):
    full_path = os.path.join(SOURCE_DIR, file_path)
    if not os.path.exists(full_path):
        print(f"File not found: {full_path}")
        return {}
        
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Extract define table
    define_match = re.search(r'## 1\. DEFINE\s*(.*?)(?=## 2\.|\Z)', content, re.DOTALL)
    define_table_html = ""
    define_intro = ""
    define_invariants = ""
    if define_match:
        define_section = define_match.group(1)
        # Find first table
        table_match = re.search(r'(\|.*\|.*?)\n(?=\n|\S)', define_section, re.DOTALL)
        if table_match:
            define_table_html = parse_markdown_table(table_match.group(1))
            define_intro = define_section.split(table_match.group(0))[0].strip()
        else:
            define_intro = define_section.strip()
            
        # Find key invariants
        inv_match = re.search(r'### Key Invariants\s*(.*?)(?=##|\Z)', define_section, re.DOTALL)
        if inv_match:
            define_invariants = inv_match.group(1).strip()
            define_invariants = re.sub(r'^- (.*)', r'<li>\1</li>', define_invariants, flags=re.MULTILINE)
            define_invariants = f'<div class="note note-warn"><div class="note-icon">⚠️</div><div><strong>Nguyên tắc bất biến quan trọng:</strong><ul style="margin-left:20px;margin-top:8px;">{define_invariants}</ul></div></div>'
            define_invariants = translate_text(define_invariants)

    # Extract visuals
    visual_match = re.search(r'## 2\. VISUAL\s*(.*?)(?=## 3\.|\Z)', content, re.DOTALL)
    png_image_tag = ""
    visual_intro = ""
    if visual_match:
        visual_section = visual_match.group(1)
        # Look for images: ![alt](url)
        img_match = re.search(r'!\[(.*?)\]\(\.(.*?)\)', visual_section)
        if img_match:
            alt = img_match.group(1)
            url = img_match.group(2).lstrip("/")
            filename = os.path.basename(url)
            target_url = f"../../public/images/{filename}"
            png_image_tag = f'<div style="text-align:center; margin: 24px 0;"><img src="{target_url}" alt="{alt}" style="max-width:100%; border-radius:10px; border:1px solid var(--border); box-shadow: 0 4px 20px rgba(0,0,0,0.3);" /><div style="font-size:12px; color:var(--text-muted); margin-top:8px; font-style:italic;">Hình ảnh trực quan: {alt}</div></div>'
        
        visual_intro = re.sub(r'!\[.*?\]\(.*?\)', '', visual_section).strip()
        visual_intro = re.sub(r'```mermaid.*?```', '', visual_intro, flags=re.DOTALL).strip()
        visual_intro = translate_text(visual_intro)
        
    # Extract code examples
    code_match = re.search(r'## 3\. CODE\s*(.*?)(?=## 4\.|\Z)', content, re.DOTALL)
    examples = []
    if code_match:
        code_section = code_match.group(1)
        # Find all examples starting with ###
        ex_matches = re.finditer(r'### (.*?)\n(.*?)(?=### |\Z)', code_section, re.DOTALL)
        for m in ex_matches:
            ex_title = m.group(1).strip()
            ex_body = m.group(2).strip()
            
            # Extract code block inside ```go ... ```
            block_match = re.search(r'```go(.*?)```', ex_body, re.DOTALL)
            ex_desc = re.sub(r'```go.*?```', '', ex_body, flags=re.DOTALL).strip()
            ex_code_html = ""
            if block_match:
                raw_code = block_match.group(1).strip()
                # Find filename comments
                filename = "example.go"
                file_match = re.search(r'//\s*\*+\s*//\s*(.*?)\.go', raw_code, re.IGNORECASE)
                if file_match:
                    filename = file_match.group(1).strip() + ".go"
                
                # Check for other styles
                filename_match = re.search(r'//\s*(.*?\.(?:go|json|yaml))', raw_code)
                if filename_match:
                    filename = filename_match.group(1).strip()
                    
                highlighted = highlight_go(raw_code)
                ex_code_html = f'''
                <div class="code-block" style="margin-top:16px;">
                    <div class="code-header">
                        <span class="code-lang">GO</span>
                        <span class="code-filename">{filename}</span>
                        <button class="code-copy" onclick="navigator.clipboard.writeText(this.parentElement.nextElementSibling.innerText); this.innerText='Copied!'; setTimeout(() => this.innerText='Copy', 2000)">Copy</button>
                    </div>
                    <pre><code>{highlighted}</code></pre>
                </div>
                '''
            examples.append({
                "title": translate_text(ex_title),
                "description": translate_text(ex_desc),
                "code_html": ex_code_html
            })

    # Extract Pitfalls
    pitfalls_match = re.search(r'## 4\. PITFALLS\s*(.*?)(?=## 5\.|\Z)', content, re.DOTALL)
    pitfalls_table_html = ""
    if pitfalls_match:
        pitfalls_section = pitfalls_match.group(1)
        table_match = re.search(r'(\|.*\|.*?)\n(?=\n|\S)', pitfalls_section, re.DOTALL)
        if table_match:
            pitfalls_table_html = parse_markdown_table(table_match.group(1))

    # Extract References & Recommendations
    ref_match = re.search(r'## 5\. REF\s*(.*?)(?=## 6\.|\Z)', content, re.DOTALL)
    ref_table_html = ""
    if ref_match:
        ref_section = ref_match.group(1)
        table_match = re.search(r'(\|.*\|.*?)\n(?=\n|\S)', ref_section, re.DOTALL)
        if table_match:
            ref_table_html = parse_markdown_table(table_match.group(1))
            
    rec_match = re.search(r'## 6\. RECOMMEND\s*(.*?)(?=\Z)', content, re.DOTALL)
    rec_table_html = ""
    if rec_match:
        rec_section = rec_match.group(1)
        table_match = re.search(r'(\|.*\|.*?)\n(?=\n|\S)', rec_section, re.DOTALL)
        if table_match:
            rec_table_html = parse_markdown_table(table_match.group(1))

    return {
        "define_intro": translate_text(define_intro),
        "define_table_html": define_table_html,
        "define_invariants": define_invariants,
        "png_image_tag": png_image_tag,
        "visual_intro": visual_intro,
        "examples": examples,
        "pitfalls_table_html": pitfalls_table_html,
        "ref_table_html": ref_table_html,
        "rec_table_html": rec_table_html
    }

def update_html():
    with open(TARGET_FILE, "r", encoding="utf-8") as f:
        html = f.read()
        
    for sec_id, md_path in MAPPING.items():
        print(f"Processing section: {sec_id}...")
        data = parse_markdown_file(md_path, sec_id)
        if not data:
            continue
            
        # Find the section in HTML
        # A section pattern in the HTML looks like: <section class="page-section..." id="[sec_id]"> ... </section>
        pattern = r'(<section class="page-section[^"]*" id="' + sec_id + r'">)(.*?)(</section>)'
        match = re.search(pattern, html, re.DOTALL)
        if not match:
            print(f"Section {sec_id} not found in HTML!")
            continue
            
        start_tag = match.group(1)
        section_body = match.group(2)
        end_tag = match.group(3)
        
        header_match = re.search(r'<div class="section-header">.*?</div>\s*</div>\s*(?:<span class="badge.*?</span>\s*)?</div>', section_body, re.DOTALL)
        if not header_match:
            header_match = re.search(r'<div class="section-header">.*?</div>', section_body, re.DOTALL)
        
        concept_match = re.search(r'<div class="concept-box">.*?</div>\s*</div>', section_body, re.DOTALL)
        if not concept_match:
            concept_match = re.search(r'<div class="concept-box">.*?</div>', section_body, re.DOTALL)
            
        problem_match = re.search(r'<h3>Problem Statement \(Đặt vấn đề\)</h3>.*?<h3>', section_body, re.DOTALL)
        if not problem_match:
            problem_match = re.search(r'<h3>Problem Statement \(Đặt vấn đề\)</h3>.*?(?=<div class="code-block">|<h3>)', section_body, re.DOTALL)
            
        solution_match = re.search(r'<h3>Solution \(Giải pháp\)</h3>.*?<div class="code-block">', section_body, re.DOTALL)
        if not solution_match:
            solution_match = re.search(r'<h3>Solution \(Giải pháp\)</h3>.*?(?=<div class="code-block">|<h3>)', section_body, re.DOTALL)
            
        existing_code_block = re.search(r'<div class="code-block">.*?</div>\s*</pre>\s*</div>', section_body, re.DOTALL)
        if not existing_code_block:
            existing_code_block = re.search(r'<div class="code-block">.*?</div>', section_body, re.DOTALL)
            
        existing_svg = re.search(r'<div class="diagram-container">.*?</div>\s*</svg>\s*</div>', section_body, re.DOTALL)
        if not existing_svg:
            existing_svg = re.search(r'<div class="diagram-container">.*?</div>', section_body, re.DOTALL)
            
        existing_note = re.search(r'<div class="note.*?>.*?</div>\s*</p>\s*</div>', section_body, re.DOTALL)
        if not existing_note:
            existing_note = re.search(r'<div class="note.*?>.*?</div>', section_body, re.DOTALL)
            
        # Re-build body beautifully!
        new_body = ""
        if header_match:
            new_body += header_match.group(0) + "\n\n"
        if concept_match:
            new_body += concept_match.group(0) + "\n\n"
            
        # 1. Define & Concept Box
        new_body += '<div class="card" style="margin-bottom: 28px;">'
        new_body += '  <div class="card-title" style="color:var(--accent-cyan); font-family:var(--font-mono); font-size:13px; text-transform:uppercase; letter-spacing:0.08em;">📋 Khái niệm & Bảng định nghĩa</div>'
        if data.get("define_intro"):
            new_body += f'  <p class="prose">{data["define_intro"]}</p>'
        if data.get("define_table_html"):
            new_body += data["define_table_html"]
        if data.get("define_invariants"):
            new_body += data["define_invariants"]
        new_body += '</div>\n\n'
        
        # 2. Problem & Solution
        if problem_match:
            new_body += problem_match.group(0).rstrip("<h3>") + "\n"
        if solution_match:
            new_body += solution_match.group(0).rstrip("<div class=\"code-block\">") + "\n"
            
        # 3. Main code block
        if existing_code_block:
            new_body += '<h3>Mã nguồn giải pháp tối ưu (Production implementation)</h3>\n'
            new_body += existing_code_block.group(0) + "\n\n"
            
        # 4. Additional Code Examples
        if data.get("examples"):
            new_body += '<div class="divider"></div>\n'
            new_body += '<h3>Các ví dụ bổ sung (Phân tầng từ Cơ bản đến Nâng cao)</h3>\n'
            for idx, ex in enumerate(data["examples"]):
                new_body += f'''
                <div class="card" style="margin-bottom: 24px;">
                    <div class="card-title" style="color:var(--accent-green); font-family:var(--font-mono); font-size:14px; display:flex; align-items:center; gap:8px;">
                        <span class="badge badge-basic" style="padding: 2px 8px; font-size:10px;">VÍ DỤ {idx+1}</span>
                        {ex["title"]}
                    </div>
                    <p class="prose" style="margin-top:8px; font-size:13.5px; line-height:1.6;">{ex["description"]}</p>
                    {ex["code_html"]}
                </div>
                '''
                
        # 5. Visual Support
        new_body += '<div class="divider"></div>\n'
        new_body += '<h3>Minh họa luồng hoạt động & Sơ đồ (Visual Support)</h3>\n'
        if data.get("visual_intro"):
            new_body += f'<p class="prose">{data["visual_intro"]}</p>\n'
        if data.get("png_image_tag"):
            new_body += data["png_image_tag"] + "\n"
        if existing_svg:
            new_body += existing_svg.group(0) + "\n\n"
            
        # 6. Pitfalls Table
        if data.get("pitfalls_table_html"):
            new_body += '<div class="divider"></div>\n'
            new_body += '<div class="card" style="border-color: rgba(255,107,107,0.25); background: rgba(255,107,107,0.01);">'
            new_body += '  <div class="card-title" style="color:var(--accent-coral); font-family:var(--font-mono); font-size:13px; text-transform:uppercase; letter-spacing:0.08em;">⚠️ Các lỗi thường gặp & Cách phòng tránh (Pitfalls)</div>'
            new_body += data["pitfalls_table_html"]
            new_body += '</div>\n\n'
            
        # 7. Note Box
        if existing_note:
            new_body += existing_note.group(0) + "\n\n"
            
        # 8. Ref & Recommendations
        if data.get("ref_table_html") or data.get("rec_table_html"):
            new_body += '<div class="card" style="margin-top: 28px; background: rgba(255,255,255,0.01); border-style: dashed;">'
            new_body += '  <div class="card-title" style="color:var(--text-muted); font-family:var(--font-mono); font-size:12px; text-transform:uppercase; letter-spacing:0.08em;">🔗 Tài liệu tham khảo & Bước tiếp theo (Reference & Recommend)</div>'
            if data.get("ref_table_html"):
                new_body += '<div style="font-size:12px; font-weight:600; margin-bottom:8px; color:var(--text-secondary);">TÀI LIỆU KHUYÊN ĐỌC:</div>'
                new_body += data["ref_table_html"]
            if data.get("rec_table_html"):
                new_body += '<div style="font-size:12px; font-weight:600; margin-top:16px; margin-bottom:8px; color:var(--text-secondary);">CHỦ ĐỀ KẾ TIẾP:</div>'
                new_body += data["rec_table_html"]
            new_body += '</div>\n\n'
            
        # Replace in HTML
        html = html.replace(match.group(0), start_tag + new_body + end_tag)
        
    with open(TARGET_FILE, "w", encoding="utf-8") as f:
        f.write(html)
        
    print("Done! HTML guide successfully enriched.")

if __name__ == "__main__":
    update_html()
