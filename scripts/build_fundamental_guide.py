import re
import os

# Paths
SOURCE_DIR = "/home/mvt/mAIvt/Documents/go/fundamental"
TARGET_FILE = "/home/mvt/mAIvt/Go/Fundamental/go-fundamental-guide.html"

# Mapping of section ID to markdown file path, category, and badge
MAPPING = [
    # Basics
    {"id": "syntax-variables", "path": "basics/01-syntax-variables.md", "category": "Basics", "badge": "BASICS"},
    {"id": "control-flow-loops", "path": "basics/02-control-flow-loops.md", "category": "Basics", "badge": "BASICS"},
    {"id": "defer-panic-recover", "path": "basics/03-defer-panic-recover.md", "category": "Basics", "badge": "BASICS"},
    {"id": "pointers-memory", "path": "basics/04-pointers-memory.md", "category": "Basics", "badge": "BASICS"},
    
    # Types
    {"id": "slices-maps-strings-types", "path": "types/01-slices-maps-strings.md", "category": "Types", "badge": "TYPES"},
    {"id": "generics", "path": "types/02-generics.md", "category": "Types", "badge": "TYPES"},
    {"id": "type-assertion-embedding", "path": "types/03-type-assertion-embedding.md", "category": "Types", "badge": "TYPES"},
    {"id": "comparable", "path": "types/04-comparable.md", "category": "Types", "badge": "TYPES"},
    
    # Structs
    {"id": "composition-embedding-structs", "path": "structs/01-composition-embedding.md", "category": "Structs", "badge": "STRUCTS"},
    {"id": "tags-options-builder", "path": "structs/02-tags-options-builder.md", "category": "Structs", "badge": "STRUCTS"},
    
    # Functions
    {"id": "closures-methods", "path": "functions/01-closures-methods.md", "category": "Functions", "badge": "FUNCTIONS"},
    {"id": "strings-pkg", "path": "functions/02-strings.md", "category": "Functions", "badge": "FUNCTIONS"},
    {"id": "strconv-pkg", "path": "functions/03-strconv.md", "category": "Functions", "badge": "FUNCTIONS"},
    {"id": "fmt-pkg", "path": "functions/04-fmt.md", "category": "Functions", "badge": "FUNCTIONS"},
    {"id": "math-pkg", "path": "functions/05-math.md", "category": "Functions", "badge": "FUNCTIONS"},
    {"id": "slices-maps-pkg", "path": "functions/06-slices-maps.md", "category": "Functions", "badge": "FUNCTIONS"},
    
    # Interfaces
    {"id": "implicit-io-patterns", "path": "interfaces/01-implicit-io-patterns.md", "category": "Interfaces", "badge": "INTERFACES"},
    {"id": "di-mocking-patterns", "path": "interfaces/02-di-mocking-patterns.md", "category": "Interfaces", "badge": "INTERFACES"},
    
    # Errors
    {"id": "wrapping-custom", "path": "errors/01-wrapping-custom.md", "category": "Errors", "badge": "ERRORS"},
    {"id": "sentinel-wrapping-join", "path": "errors/02-sentinel-wrapping-join.md", "category": "Errors", "badge": "ERRORS"},
    
    # Packages
    {"id": "modules-layout", "path": "packages/01-modules-layout.md", "category": "Packages", "badge": "PACKAGES"},
    {"id": "workspaces-vendoring", "path": "packages/02-workspaces-vendoring.md", "category": "Packages", "badge": "PACKAGES"},
    
    # OOP
    {"id": "oop-mental-model", "path": "oop/01-oop-mental-model.md", "category": "OOP", "badge": "OOP"},
    {"id": "encapsulation-visibility", "path": "oop/02-encapsulation-visibility.md", "category": "OOP", "badge": "OOP"},
    {"id": "composition-over-inheritance", "path": "oop/03-composition-over-inheritance.md", "category": "OOP", "badge": "OOP"},
    {"id": "interfaces-polymorphism", "path": "oop/04-interfaces-polymorphism.md", "category": "OOP", "badge": "OOP"},
    {"id": "solid-in-go", "path": "oop/05-solid-in-go.md", "category": "OOP", "badge": "OOP"},
    {"id": "design-patterns-go-way", "path": "oop/06-design-patterns-go-way.md", "category": "OOP", "badge": "OOP"},
    
    # Helpers
    {"id": "data-conversion", "path": "helper/01-data-conversion.md", "category": "Helpers", "badge": "HELPERS"},
    {"id": "array-pipeline", "path": "helper/02-array-pipeline.md", "category": "Helpers", "badge": "HELPERS"},
    {"id": "object-map-utils", "path": "helper/03-object-map-utils.md", "category": "Helpers", "badge": "HELPERS"},
    {"id": "promise-async", "path": "helper/04-promise-async.md", "category": "Helpers", "badge": "HELPERS"},
    {"id": "date-time", "path": "helper/05-date-time.md", "category": "Helpers", "badge": "HELPERS"},
    {"id": "enum-union-types", "path": "helper/06-enum-union-types.md", "category": "Helpers", "badge": "HELPERS"},
    {"id": "error-handling-helper", "path": "helper/07-error-handling.md", "category": "Helpers", "badge": "HELPERS"},
    {"id": "regex-templates", "path": "helper/08-regex-templates.md", "category": "Helpers", "badge": "HELPERS"},
    {"id": "set-concurrent-map", "path": "helper/09-set-concurrent-map.md", "category": "Helpers", "badge": "HELPERS"},
    {"id": "iterator", "path": "helper/10-iterator.md", "category": "Helpers", "badge": "HELPERS"},
    {"id": "optional-nullable", "path": "helper/11-optional-nullable.md", "category": "Helpers", "badge": "HELPERS"},
    {"id": "class-struct", "path": "helper/12-class-struct.md", "category": "Helpers", "badge": "HELPERS"},
    
    # Testing
    {"id": "table-driven-mocking", "path": "testing/01-table-driven-mocking.md", "category": "Testing", "badge": "TESTING"},
    {"id": "benchmark-fuzz", "path": "testing/02-benchmark-fuzz.md", "category": "Testing", "badge": "TESTING"},
    {"id": "integration-testcontainers", "path": "testing/03-integration-testcontainers.md", "category": "Testing", "badge": "TESTING"},
    
    # TS to Go
    {"id": "ts-go-mental-model", "path": "typescript-to-go/01-mental-model-runtime.md", "category": "TS to Go", "badge": "TS TO GO"},
    {"id": "ts-go-types-modeling", "path": "typescript-to-go/02-types-data-modeling.md", "category": "TS to Go", "badge": "TS TO GO"},
    {"id": "ts-go-errors-concurrency", "path": "typescript-to-go/03-errors-concurrency-context.md", "category": "TS to Go", "badge": "TS TO GO"},
    {"id": "ts-go-layout-tooling", "path": "typescript-to-go/04-project-layout-tooling-testing.md", "category": "TS to Go", "badge": "TS TO GO"},
    {"id": "ts-go-when-to-choose", "path": "typescript-to-go/05-when-to-choose-go-vs-typescript.md", "category": "TS to Go", "badge": "TS TO GO"},
    {"id": "ts-go-migration-playbook", "path": "typescript-to-go/06-migration-playbook.md", "category": "TS to Go", "badge": "TS TO GO"},
    {"id": "ts-go-translation-atlas", "path": "typescript-to-go/07-translation-atlas.md", "category": "TS to Go", "badge": "TS TO GO"}
]

# Structural translation map for headings and badges
TRANSLATIONS = {
    "## 1. DEFINE": "## 1. KHÁI NIỆM & ĐỊNH NGHĨA",
    "## 2. VISUAL": "## 2. SƠ ĐỒ TRỰC QUAN & LUỒNG HOẠT ĐỘNG",
    "## 3. CODE": "## 3. CÁC VÍ DỤ MINH HỌA & MÃ NGUỒN",
    "## 4. PITFALLS": "## 4. CÁC LỖI THƯỜNG GẶP & CÁCH PHÒNG TRÁNH",
    "## 5. REF": "## 5. TÀI LIỆU THAM KHẢO & LIÊN KẾT",
    "## 6. RECOMMEND": "## 6. CHỦ ĐỀ KHUYÊN ĐỌC TIẾP THEO",
    
    # Badges for Severity
    "🔴 Fatal": "<span class=\"badge b-expert\" style=\"background:rgba(239,68,68,0.15);color:#f87171;border:1px solid rgba(239,68,68,0.3);\">🔴 FATAL</span>",
    "🔴 Critical": "<span class=\"badge b-expert\" style=\"background:rgba(239,68,68,0.15);color:#f87171;border:1px solid rgba(239,68,68,0.3);\">🔴 CRITICAL</span>",
    "🟡 Common": "<span class=\"badge b-advanced\" style=\"background:rgba(245,158,11,0.12);color:#fbbf24;border:1px solid rgba(245,158,11,0.3);\">🟡 COMMON</span>",
    "🟡 Warning": "<span class=\"badge b-advanced\" style=\"background:rgba(245,158,11,0.12);color:#fbbf24;border:1px solid rgba(245,158,11,0.3);\">🟡 WARNING</span>",
    "🔵 Minor": "<span class=\"badge b-basic\" style=\"background:rgba(59,130,246,0.12);color:#60a5fa;border:1px solid rgba(59,130,246,0.3);\">🔵 MINOR</span>",
}

# Single-pass vocabulary dictionary to prevent recursive collision bugs
VOCAB_DICT = {
    "variables": "các biến",
    "variable": "biến",
    "constants": "các hằng số",
    "constant": "hằng số",
    "pointers": "các con trỏ",
    "pointer": "con trỏ",
    "interfaces": "các giao diện (interface)",
    "interface": "giao diện (interface)",
    "goroutines": "các goroutine",
    "goroutine": "goroutine",
    "channels": "các kênh (channel)",
    "channel": "kênh (channel)",
    "concurrency": "đồng thời (concurrency)",
    "concurrent": "đồng thời",
    "shadowing": "hiện tượng che khuất biến (shadowing)",
    "shadowed variable": "biến bị che khuất (shadowed)",
    "shadowed": "bị che khuất",
    "zero value": "giá trị mặc định (zero value)",
    "zero values": "các giá trị mặc định (zero values)",
    "type assertion": "khẳng định kiểu (type assertion)",
    "type assertions": "các khẳng định kiểu (type assertions)",
    "type switch": "lựa chọn theo kiểu (type switch)",
    "type switches": "các type switch",
    "control flow": "luồng điều khiển",
    "implicit": "ngầm định (implicit)",
    "explicit": "tường minh (explicit)",
    "dependency injection": "tiêm phụ thuộc (Dependency Injection)",
    "mocking": "giả lập (mocking)",
    "unit testing": "kiểm thử đơn vị (unit testing)",
    "table-driven testing": "kiểm thử hướng bảng (table-driven testing)",
    "struct tags": "thẻ cấu trúc (struct tags)",
    "struct tag": "thẻ cấu trúc (struct tag)",
    "options builder": "options builder pattern",
    "composition": "sự kết hợp (composition)",
    "inheritance": "sự kế thừa (inheritance)",
    "encapsulation": "tính đóng gói (encapsulation)",
    "polymorphism": "tính đa hình (polymorphism)",
    "design patterns": "các mẫu thiết kế (design patterns)",
    "design pattern": "mẫu thiết kế (design pattern)",
    "testcontainers": "testcontainers",
    "graceful shutdown": "tắt máy an toàn (graceful shutdown)",
    "compile error": "lỗi biên dịch",
    "compile errors": "các lỗi biên dịch",
    "runtime panic": "lỗi sập runtime (runtime panic)",
    "runtime panics": "lỗi sập runtime (runtime panics)",
    "data race": "tranh chấp dữ liệu (data race)",
    "data races": "tranh chấp dữ liệu (data races)",
    "when to use": "khi nào sử dụng",
    "how to use": "cách sử dụng",
    "pros": "ưu điểm",
    "cons": "nhược điểm",
    "definition": "định nghĩa",
    "definitions": "định nghĩa",
    "explanation": "giải thích",
    "examples": "các ví dụ",
    "pitfall": "cạm bẫy",
    "pitfalls": "cạm bẫy",
    "recommendation": "khuyến nghị",
    "recommendations": "khuyến nghị",
    "key invariants": "nguyên tắc bất biến quan trọng",
    "problem statement": "bài toán thực tế (problem)",
    "solution": "giải pháp thiết kế (solution)",
    "severity": "mức độ nghiêm trọng",
    "defect": "sai sót / lỗi cạm bẫy",
    "impact": "ảnh hưởng thực tế",
    "fix": "giải pháp khắc phục",
    "scope": "phạm vi áp dụng",
    "application": "cách áp dụng thực tế",
    "use case": "trường hợp sử dụng",
    "method": "phương thức",
    "source": "nguồn dữ liệu",
    "Aspect": "Khía cạnh so sánh",
    "Detail": "Chi tiết kỹ thuật",
    "Concept": "Khái niệm cốt lõi",
    "Prerequisite": "Điều kiện tiên quyết",
    "CLI": "Công cụ CLI",
    "Syntax": "Cú pháp khai báo",
    "Description": "Mô tả chi tiết",
    "Example": "Ví dụ minh họa",
    "Type": "Kiểu dữ liệu",
    "Zero value": "Giá trị zero mặc định",
    "Statement": "Câu lệnh điều khiển",
    "Note": "Lưu ý quan trọng",
    "Error": "Lỗi biên dịch / Runtime",
    "Cause": "Nguyên nhân gốc rễ",
    "Consequence": "Hậu quả hệ thống",
    "Fix": "Giải pháp khắc phục",
    "Resource": "Tài liệu tham khảo",
    "Link": "Liên kết truy cập",
    "Notes": "Ghi chú bổ sung",
    "Expand to": "Chủ đề mở rộng",
    "When": "Bối cảnh áp dụng",
    "Reason": "Lý do khuyên đọc",
    "File": "Đường dẫn tệp",
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
        "Mutex", "WaitGroup", "Validate", "FieldLevel", "H", "Weekday", "Permission", "Client",
        "Buffer", "File", "FileMode", "Seq", "Seq2"
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
        
    code = re.sub(r'/\*.*?\*/', store_block_comment, code, flags=re.DOTALL)
    code = re.sub(r'//.*', store_line_comment, code)
    code = re.sub(r'`[^`]*`', store_string, code)
    code = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', store_string, code)
    
    code = re.sub(r'\b(\d+)\b', r'<span class="num">\1</span>', code)
    
    def repl_word(match):
        word = match.group(0)
        if word in keywords:
            return f'<span class="kw">{word}</span>'
        elif word in types:
            return f'<span class="tp">{word}</span>'
        return word
        
    code = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', repl_word, code)
    code = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)(?=\()', r'<span class="fn">\1</span>', code)
    
    for i, s in enumerate(strings):
        code = code.replace(f"__STRING_{i}__", f'<span class="str">{s}</span>')
    for i, c in enumerate(comments):
        if c.startswith("//"):
            code = code.replace(f"__LINE_COMMENT_{i}__", f'<span class="cm">{c}</span>')
        else:
            code = code.replace(f"__BLOCK_COMMENT_{i}__", f'<span class="cm">{c}</span>')
            
    return code

def single_pass_replace(text, dictionary):
    if not text:
        return ""
    sorted_keys = sorted(dictionary.keys(), key=len, reverse=True)
    pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in sorted_keys) + r')\b', re.IGNORECASE)
    
    def replace_match(match):
        word = match.group(0)
        for k, v in dictionary.items():
            if k.lower() == word.lower():
                if word.isupper():
                    return v.upper()
                elif word[0].isupper():
                    return v[0].upper() + v[1:]
                return v
        return word
        
    return pattern.sub(replace_match, text)

def translate_text(text):
    if not text:
        return ""
        
    # Structural headings and badges replacement
    for key, val in TRANSLATIONS.items():
        text = text.replace(key, val)
        
    # Large prose sentence mappings (applied first to protect from vocabulary collisions)
    prose_maps = [
        # Syntax / Basics
        ("Imagine a Go snippet that seems incredibly basic, but the moment you shift context to debugging or code review, weak assumptions are easily exposed.",
         "Hãy tưởng tượng một đoạn mã Go có vẻ cực kỳ đơn giản, nhưng ngay khi bạn chuyển sang bối cảnh gỡ lỗi hoặc đánh giá mã nguồn (code review), những giả định lỏng lẻo sẽ dễ dàng bị lộ tẩy."),
        ("You have just cloned a Go repository for the first time. Opening `main.go`, you see `:=` instead of `var`, functions returning `(int, error)` instead of throwing exceptions, and `for` being used in all three places where C/Java would use `for`, `while`, and `do-while`.",
         "Bạn vừa clone một kho lưu trữ Go lần đầu tiên. Mở tệp `main.go`, bạn thấy ký hiệu `:=` thay vì `var`, các hàm trả về cặp `(int, error)` thay vì ném ra ngoại lệ (exception), và duy nhất từ khóa `for` được dùng cho cả ba kiểu vòng lặp mà thông thường C/Java sẽ dùng `for`, `while`, và `do-while`."),
        ("Choose incorrectly and the code review gets rejected; choose correctly and the PR merges immediately.",
         "Chọn sai thì PR của bạn sẽ bị từ chối khi đánh giá mã nguồn; chọn đúng thì PR sẽ được phê duyệt và merge ngay lập tức."),
        ("This is the problem this article solves: understanding **why** Go syntax is designed the way it is, so every line of code you write is **idiomatic** — not just \"translated\" from Java or Python into Go.",
         "Đây chính là vấn đề mà chuyên đề này giải quyết: hiểu rõ **tại sao** cú pháp Go được thiết kế như vậy, để từng dòng mã bạn viết ra đều mang tính **idiomatic (chuẩn hóa Go)** — chứ không chỉ đơn thuần là \"dịch\" từ Java hay Python sang Go."),
        ("Go has **two variable declaration methods** — not due to a lack of consistency, but because they serve two distinct use cases:",
         "Go có **hai phương thức khai báo biến** — không phải do thiếu tính nhất quán, mà vì chúng phục vụ hai trường hợp sử dụng hoàn toàn khác nhau:"),
        ("Why both `var` and `:=`?", "Tại sao lại cần cả `var` và `:=`?"),
        ("var is used at the package level (outside of functions) and when explicit types are needed for documentation.",
         "var được sử dụng ở cấp độ package (ngoài các hàm) và khi cần khai báo kiểu dữ liệu tường minh để làm tài liệu hướng dẫn."),
        ("`:=` is only available within functions — it is more concise when the compiler can infer the type from the right-hand value.",
         "`:=` chỉ được phép sử dụng bên trong các hàm — nó ngắn gọn hơn khi trình biên dịch có thể tự suy luận kiểu dữ liệu từ giá trị bên phải."),
        ("Choosing the wrong one won't cause a bug, but it violates Go conventions → code reviews will request a change.",
         "Chọn sai sẽ không gây lỗi chạy ứng dụng, nhưng vi phạm quy ước chuẩn của Go và sẽ bị yêu cầu sửa đổi khi code review."),
        ("Go **does not permit uninitialized states** — every undeclared variable is assigned a zero value corresponding to its type:",
         "Go **không cho phép các trạng thái không được khởi tạo** — mọi biến chưa được gán giá trị đều tự động nhận một giá trị zero (giá trị mặc định) tương ứng với kiểu của nó:"),
        ("Why? Zero values eliminate an entire class of bugs caused by \"forgetting to initialize\" — the most common error in C/C++.",
         "Tại sao? Giá trị zero giúp loại bỏ hoàn toàn một lớp các lỗi phổ biến do \"quên khởi tạo\" — lỗi kinh điển nhất trong C/C++."),
        ("`var buf bytes.Buffer` is immediately ready for use without a constructor.",
         "`var buf bytes.Buffer` đã sẵn sàng để sử dụng ngay lập tức mà không cần gọi constructor."),
        ("But **be careful**: a `nil map` allows reads (returning the zero value), but **writing to a nil map triggers a panic**.",
         "Nhưng **hãy cẩn thận**: đọc từ một `nil map` vẫn an toàn (trả về giá trị mặc định), nhưng **ghi dữ liệu vào một nil map sẽ lập tức gây ra runtime panic (sập chương trình)**."),
        ("Go **has only a single keyword for loops** — `for` handles the roles of `while`, `do-while`, and the classic C-for loop:",
         "Go **chỉ có duy nhất một từ khóa cho các vòng lặp** — `for` đảm nhận vai trò của cả `for`, `while`, và `do-while` kiểu C cổ điển:"),
        ("Why `if err := fn(); err != nil {}`?", "Tại sao lại dùng `if err := fn(); err != nil {}`?"),
        ("The initialization statement within an `if` restricts the scope of `err` exclusively to that block — the variable does not leak outside, resulting in cleaner code.",
         "Câu lệnh khởi tạo bên trong `if` giới hạn phạm vi hoạt động của biến `err` chỉ trong khối lệnh đó — biến sẽ không bị rò rỉ ra ngoài, giúp mã nguồn sạch sẽ hơn."),
        ("This is **Go idiom #1** that every Go developer must know.", "Đây là **quy tắc chuẩn (idiom) số 1** của Go mà mọi lập trình viên đều phải thuộc lòng."),
        
        # Defer, Panic, Recover
        ("You write a function that opens a file, processes it, and returns. The function has three return paths. Each path must call `f.Close()`.",
         "Bạn viết một hàm mở tệp tin, xử lý dữ liệu và trả về kết quả. Hàm có ba lối thoát (return paths). Mỗi lối thoát đều phải gọi `f.Close()`."),
        ("Miss one and the file descriptor leaks. `defer f.Close()` placed right after `os.Open()` guarantees cleanup regardless of which path executes.",
         "Bỏ sót dù chỉ một lối thoát sẽ khiến file descriptor bị rò rỉ. Đặt câu lệnh `defer f.Close()` ngay sau khi mở tệp `os.Open()` đảm bảo tệp luôn được dọn dẹp an toàn bất kể nhánh xử lý nào được thực thi."),
        ("This example also covers `panic`/`recover` for unrecoverable errors and pointer semantics for modify-in-place operations.",
         "Ví dụ này cũng đề cập đến cơ chế `panic`/`recover` để xử lý các lỗi không thể phục hồi và ngữ nghĩa con trỏ (pointer semantics) để sửa đổi trực tiếp dữ liệu tại vùng nhớ."),
        ("Why `defer` instead of `finally`?", "Tại sao lại dùng `defer` thay vì `finally`?"),
        ("Java's `finally` lives far from the resource it cleans up — you open a file at line 10, close it at line 50. `defer` sits right next to `Open()`, making the intent visible: \"this resource will be cleaned up.\"",
         "Khối lệnh `finally` của Java thường nằm rất xa tài nguyên cần dọn dẹp — bạn mở tệp ở dòng 10 nhưng phải đóng nó ở dòng 50. Ngược lại, `defer` trong Go nằm ngay cạnh hàm `Open()`, giúp thể hiện rõ ràng mục đích: \"tài nguyên này chắc chắn sẽ được giải phóng.\""),
        ("`defer` also runs during a `panic`, serving as `try-finally` and exception handler in one keyword.",
         "`defer` vẫn được thực thi ngay cả khi xảy ra `panic`, đóng vai trò vừa là `try-finally` vừa là bộ xử lý ngoại lệ chỉ trong một từ khóa duy nhất."),
        ("Why pointers without pointer arithmetic?", "Tại sao lại có con trỏ nhưng không cho phép số học con trỏ?"),
        ("Pointer arithmetic (`ptr + offset`) is the root cause of buffer overflows in C. Go keeps pointers for modify-in-place and avoiding struct copies, but removes arithmetic.",
         "Phép toán số học con trỏ (`ptr + offset`) là nguyên nhân hàng đầu gây ra lỗi tràn bộ đệm (buffer overflow) trong C. Go giữ lại con trỏ để sửa đổi trực tiếp tại chỗ và tránh sao chép các struct lớn, nhưng loại bỏ hoàn toàn các phép toán số học con trỏ."),
        ("The garbage collector can track every pointer safely. Trade-off: less flexibility, guaranteed memory safety.",
         "Nhờ đó, Garbage Collector (bộ thu gom rác) có thể theo dõi mọi con trỏ một cách an toàn. Đây là sự đánh đổi cực kỳ xứng đáng: bớt đi chút linh hoạt để đổi lấy sự an toàn bộ nhớ tuyệt đối."),
        ("When should you use `panic`?", "Khi nào bạn nên sử dụng `panic`?"),
        ("Only when the program **cannot continue**: `init()` fails to load required config, a critical invariant is violated (programming bug), or `Must*` patterns like `regexp.MustCompile`.",
         "Chỉ khi chương trình **không thể tiếp tục chạy**: ví dụ hàm `init()` không tải được cấu hình hệ thống bắt buộc, một nguyên tắc bất biến bị vi phạm nghiêm trọng (lỗi lập trình), hoặc các mẫu thiết kế dạng `Must*` như `regexp.MustCompile`."),
        ("For expected errors, always `return error`.", "Đối với các lỗi thông thường có thể dự đoán trước, hãy luôn **trả về đối tượng `error`**."),
        
        # Control Flow & Loops
        ("You switch from Java to Go and reach for `while`. The compiler rejects it. You write a `switch` case and forget `break`.",
         "Bạn chuyển từ Java sang Go và theo thói quen viết vòng lặp `while`. Trình biên dịch báo lỗi từ chối. Bạn viết một câu lệnh `switch` và quên viết `break`."),
        ("The code works — because Go auto-breaks. You try `forEach` on a slice. It does not exist. `for range` does the job.",
         "Mã nguồn vẫn chạy đúng — vì Go tự động dừng (auto-break). Bạn cố gắng dùng `forEach` trên một slice nhưng nó không tồn tại. Đừng lo, `for range` sinh ra để giải quyết việc đó."),
        ("Go collapses the typical 6–8 control flow keywords found in C/Java into four: `if`, `for`, `switch`, and `select`.",
         "Go rút gọn 6-8 từ khóa điều khiển luồng thông thường trong C/Java xuống còn bốn: `if`, `for`, `switch`, và `select`."),
        ("Each keyword absorbs multiple roles. The result: less syntax to memorize, fewer opportunities for classic bugs like C's fall-through `switch` or Java's accidental infinite `while(true)`.",
         "Mỗi từ khóa đảm nhận nhiều vai trò khác nhau. Kết quả là: ít cú pháp phải ghi nhớ hơn, ít cơ hội xảy ra các lỗi kinh điển như trôi lệnh `switch` của C hay vòng lặp vô hạn `while(true)` ngoài ý muốn của Java."),
        ("Why no `while`?", "Tại sao không có `while`?"),
        ("Rob Pike: *\"If `for` can do everything, why add `while`?\"* `for condition {}` is a while loop. `for {}` is an infinite loop. One keyword. Zero ambiguity.",
         "Rob Pike chia sẻ: *\"Nếu `for` có thể làm được mọi thứ, tại sao phải thêm `while` làm gì?\"* Câu lệnh `for condition {}` chính là vòng lặp while. `for {}` chính là vòng lặp vô hạn. Một từ khóa duy nhất. Không bao giờ nhập nhằng."),
        ("Why does `range string` yield runes?", "Tại sao `range string` lại trả về các rune?"),
        ("Go strings are UTF-8 byte sequences. A single character like \"世\" occupies 3 bytes. `range` decodes each character into a rune, returning `(byteIndex, rune)` — correct Unicode handling without manual decoding.",
         "Chuỗi ký tự (string) trong Go thực chất là chuỗi byte UTF-8. Một ký tự đặc biệt như \"世\" chiếm tới 3 byte. Vòng lặp `range` sẽ tự động giải mã từng ký tự thành một rune, trả về bộ `(byteIndex, rune)` — giúp xử lý Unicode chính xác mà không cần giải mã thủ công."),
        ("Why auto-break?", "Tại sao lại tự động break?"),
        ("Forgetting `break` in C switch statements causes silent fall-through bugs. Go inverts the default: cases break automatically. Use `fallthrough` only when you genuinely need it.",
         "Việc quên viết từ khóa `break` trong các câu lệnh switch của C là nguyên nhân gây ra các lỗi trôi lệnh âm thầm rất nguy hiểm. Go đảo ngược mặc định này: các trường hợp case tự động ngắt. Bạn chỉ sử dụng `fallthrough` khi thực sự cần hành vi trôi lệnh đó."),
        ("What if two channels are ready simultaneously?", "Điều gì xảy ra nếu hai channel cùng sẵn sàng một lúc?"),
        ("Go selects one at random. This prevents starvation and guarantees fairness across channels.",
         "Go sẽ lựa chọn ngẫu nhiên một channel. Điều này giúp ngăn ngừa tình trạng nghẽn (starvation) và đảm bảo tính công bằng giữa các kênh."),
    ]
    
    for en, vi in prose_maps:
        text = text.replace(en, vi)
        text = text.replace(en.lower(), vi.lower())
        
    # Single-pass vocabulary replacements (completely immune to recursive collisions)
    text = single_pass_replace(text, VOCAB_DICT)
        
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
            
    # Headers and cells are already translated in translate_text(text) at start of render_markdown_prose
    html = '<table class="dtable"><thead><tr>'
    for h in headers:
        html += f'<th>{h}</th>'
    html += '</tr></thead><tbody>'
    for r in rows:
        html += '<tr>'
        for col in r:
            col_translated = re.sub(r'`([^`]+)`', r'<code>\1</code>', col)
            html += f'<td>{col_translated}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

def extract_and_replace_tables(text):
    lines = text.split("\n")
    output_lines = []
    current_table = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            current_table.append(line)
        else:
            if current_table:
                if len(current_table) >= 3 and any("---" in l for l in current_table[1:2]):
                    html_table = parse_markdown_table("\n".join(current_table))
                    output_lines.append(html_table)
                else:
                    output_lines.extend(current_table)
                current_table = []
            output_lines.append(line)
            
    if current_table:
        if len(current_table) >= 3 and any("---" in l for l in current_table[1:2]):
            html_table = parse_markdown_table("\n".join(current_table))
            output_lines.append(html_table)
        else:
            output_lines.extend(current_table)
            
    return "\n".join(output_lines)

def process_blockquotes(text):
    lines = text.split("\n")
    output = []
    in_quote = False
    quote_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(">"):
            in_quote = True
            content = stripped[1:].strip()
            quote_lines.append(content)
        else:
            if in_quote:
                quote_text = "\n".join(quote_lines)
                note_class = "n-tip"
                note_icon = "💡"
                if "why" in quote_text.lower() or "tại sao" in quote_text.lower():
                    note_class = "n-info"
                    note_icon = "ℹ️"
                elif "warn" in quote_text.lower() or "cẩn thận" in quote_text.lower() or "lưu ý" in quote_text.lower():
                    note_class = "n-warn"
                    note_icon = "⚠️"
                elif "conclusion" in quote_text.lower() or "kết luận" in quote_text.lower():
                    note_class = "n-info"
                    note_icon = "✅"
                
                # Already translated via translate_text(text) at start of render_markdown_prose
                quote_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', quote_text)
                quote_text = re.sub(r'`([^`]+)`', r'<code>\1</code>', quote_text)
                
                output.append(f'''
                <div class="note {note_class}" style="margin: 16px 0;">
                    <div class="note-icon">{note_icon}</div>
                    <div>{quote_text}</div>
                </div>
                ''')
                quote_lines = []
                in_quote = False
            output.append(line)
            
    if in_quote:
        quote_text = "\n".join(quote_lines)
        note_class = "n-tip"
        note_icon = "💡"
        if "why" in quote_text.lower() or "tại sao" in quote_text.lower():
            note_class = "n-info"
            note_icon = "ℹ️"
        elif "warn" in quote_text.lower() or "cẩn thận" in quote_text.lower() or "lưu ý" in quote_text.lower():
            note_class = "n-warn"
            note_icon = "⚠️"
        
        # Already translated via translate_text(text) at start of render_markdown_prose
        quote_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', quote_text)
        quote_text = re.sub(r'`([^`]+)`', r'<code>\1</code>', quote_text)
        
        output.append(f'''
        <div class="note {note_class}" style="margin: 16px 0;">
            <div class="note-icon">{note_icon}</div>
            <div>{quote_text}</div>
        </div>
        ''')
        
    return "\n".join(output)

def render_markdown_prose(text):
    if not text:
        return ""
        
    # Translate vocabulary and common paragraph patterns first
    text = translate_text(text)
    
    # Process tables and blockquotes
    text = extract_and_replace_tables(text)
    text = process_blockquotes(text)
    
    # Handle Heading 3
    text = re.sub(r'^### (.*)', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    
    # Bold and Italic markup formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)
    
    # Inline code rendering
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    # Process unordered lists
    lines = text.split("\n")
    output = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            if not in_list:
                output.append('<ul style="margin-left: 20px; margin-bottom: 16px;">')
                in_list = True
            output.append(f'<li style="margin-bottom: 6px;">{stripped[2:]}</li>')
        else:
            if in_list:
                output.append('</ul>')
                in_list = False
            output.append(line)
    if in_list:
        output.append('</ul>')
    text = "\n".join(output)
    
    # Paragraph wrapping
    blocks = text.split("\n\n")
    rendered_blocks = []
    for block in blocks:
        block_stripped = block.strip()
        if not block_stripped:
            continue
        if block_stripped.startswith("<table") or block_stripped.startswith("<div") or block_stripped.startswith("<h3") or block_stripped.startswith("<ul") or block_stripped.startswith("<pre") or block_stripped.startswith("<h3>"):
            rendered_blocks.append(block_stripped)
        else:
            rendered_blocks.append(f'<p class="prose">{block_stripped}</p>')
            
    return "\n".join(rendered_blocks)

def parse_markdown_file(file_path):
    full_path = os.path.join(SOURCE_DIR, file_path)
    if not os.path.exists(full_path):
        print(f"File not found: {full_path}")
        return {}
        
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Programmatically fix merged headings (e.g. ```## 3. MÃ -> ```\n## 3. MÃ)
    content = re.sub(r'```##\s*([0-6]\.)', r'```\n## \1', content)
    
    # Programmatically fix merged subheadings (e.g. ### Ví dụ...```go -> ### Ví dụ...\n```go)
    content = re.sub(r'(### [^\n]+)```([a-zA-Z0-9_-]+)', r'\1\n```\2', content)
    
    # Programmatically fix accidentally prepended backticks before image tags (e.g. ```![alt] -> ![alt])
    content = content.replace("```![", "![")
        
    # Extract Title (clean, no markdown symbols or emojis for topnav)
    # Strip any leading HTML comments that might prepend the title on the same line
    clean_content_for_title = re.sub(r'<!--.*?-->', '', content).strip()
    title_match = re.search(r'^#\s*(.*)', clean_content_for_title, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Chuyên đề Go"
    clean_title = re.sub(r'[^\w\s\-\/\(\)]', '', title).replace("Go Basics", "").replace("Go Types", "").replace("Go Helpers", "").strip()
    if not clean_title:
        clean_title = title
        
    # 1. DEFINE (numeric match)
    define_match = re.search(r'## 1\.[^\n]*\n(.*?)(?=## 2\.|\Z)', content, re.DOTALL)
    define_html = ""
    if define_match:
        sec = define_match.group(1).strip()
        define_html = render_markdown_prose(sec)
        
    # 2. VISUAL (numeric match)
    visual_match = re.search(r'## 2\.[^\n]*\n(.*?)(?=## 3\.|\Z)', content, re.DOTALL)
    visual_html = ""
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
        visual_intro = render_markdown_prose(prose_sec)
        
        visual_html = f'''
        <div style="margin-top:20px;">
            {visual_intro}
            {png_tag}
            {mermaid_tag}
        </div>
        '''
        
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
            ex_desc_raw = re.sub(r'```go.*?```', '', ex_body, flags=re.DOTALL).strip()
            ex_desc = render_markdown_prose(ex_desc_raw)
            
            ex_code_html = ""
            if block_match:
                raw_code = block_match.group(1).strip()
                filename = "example.go"
                filename_match = re.search(r'//\s*(.*?\.(?:go|json|yaml))', raw_code)
                if filename_match:
                    filename = filename_match.group(1).strip()
                    
                highlighted = highlight_go(raw_code)
                ex_code_html = f'''
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
                "title": translate_text(ex_title),
                "description": ex_desc,
                "code_html": ex_code_html
            })
            
    # 4. PITFALLS (numeric match)
    pitfalls_match = re.search(r'## 4\.[^\n]*\n(.*?)(?=## 5\.|\Z)', content, re.DOTALL)
    pitfalls_html = ""
    if pitfalls_match:
        sec = pitfalls_match.group(1).strip()
        pitfalls_html = render_markdown_prose(sec)

    # 5. REF (numeric match)
    ref_match = re.search(r'## 5\.[^\n]*\n(.*?)(?=## 6\.|\Z)', content, re.DOTALL)
    ref_html = ""
    if ref_match:
        sec = ref_match.group(1).strip()
        ref_html = render_markdown_prose(sec)
            
    # 6. RECOMMEND (numeric match)
    rec_match = re.search(r'## 6\.[^\n]*\n(.*?)(?=\Z)', content, re.DOTALL)
    rec_html = ""
    if rec_match:
        sec = rec_match.group(1).strip()
        rec_html = render_markdown_prose(sec)

    return {
        "title": title,
        "clean_title": clean_title,
        "define_html": define_html,
        "visual_html": visual_html,
        "examples": examples,
        "pitfalls_html": pitfalls_html,
        "ref_html": ref_html,
        "rec_html": rec_html
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
                <div style="margin-top:8px; font-size:13.5px; line-height:1.6;">{ex["description"]}</div>
                {ex["code_html"]}
            </div>
            '''
            
        pitfalls_section = ""
        if sec_data["pitfalls_html"]:
            pitfalls_section = f'''
            <div class="divider"></div>
            <div class="card" style="border-color:rgba(255,107,107,0.2); background:rgba(255,107,107,0.01);">
                <div class="card-title" style="color:var(--accent-coral); font-family:var(--font-mono); font-size:13px; text-transform:uppercase; letter-spacing:0.08em; display:flex; align-items:center; gap:8px;">
                    <span>⚠️ Các lỗi thường gặp & Phòng tránh (Pitfalls)</span>
                </div>
                <div style="margin-top:12px;">{sec_data["pitfalls_html"]}</div>
            </div>
            '''
            
        ref_rec_section = ""
        if sec_data["ref_html"] or sec_data["rec_html"]:
            ref_rec_section = f'''
            <div class="card" style="margin-top:28px; background:rgba(255,255,255,0.01); border-style:dashed;">
                <div class="card-title" style="color:var(--text-muted); font-family:var(--font-mono); font-size:12px; text-transform:uppercase; letter-spacing:0.08em;">🔗 Tài liệu tham khảo & Bước tiếp theo (Reference & Recommend)</div>
                {f'<div style="font-size:12px; font-weight:600; margin-bottom:8px; margin-top:12px; color:var(--text-secondary);">TÀI LIỆU KHUYÊN ĐỌC:</div>{sec_data["ref_html"]}' if sec_data["ref_html"] else ''}
                {f'<div style="font-size:12px; font-weight:600; margin-bottom:8px; margin-top:16px; color:var(--text-secondary);">CHỦ ĐỀ KẾ TIẾP:</div>{sec_data["rec_html"]}' if sec_data["rec_html"] else ''}
            </div>
            '''

        sections_html += f'''
        <!-- ===== SECTION: {item["id"]} ===== -->
        <section class="page-section{active_class}" id="s-{item["id"]}">
            <div class="sec-header">
                <div class="sec-num">{idx+1:02d}</div>
                <div>
                    <div class="sec-title">{sec_data["title"]}</div>
                    <div class="sec-sub">Chủ đề {idx+1:02d} chuyên sâu trong lộ trình phát triển Go Fundamentals</div>
                </div>
                <span class="badge b-expert" style="margin-left:auto;">{item["badge"]}</span>
            </div>
            
            <div class="concept-box">
                <div class="label">📖 Khái niệm & Định nghĩa</div>
                <div class="ctitle">{sec_data["title"]}</div>
                <div>{sec_data["define_html"]}</div>
            </div>
            
            <h3>Mã nguồn & Các ví dụ minh họa</h3>
            {examples_html}
            
            <div class="divider"></div>
            <h3>Sơ đồ trực quan & Luồng hoạt động (Visual Support)</h3>
            {sec_data["visual_html"]}
            
            {pitfalls_section}
            {ref_rec_section}
        </section>
        '''

    full_html = f'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Go Fundamentals — Cẩm nang phát triển toàn diện chuyên sâu</title>
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
.concept-box .ctitle{{
  font-size:20px;
  font-weight:700;
  color:var(--text-primary);
  margin-bottom:8px;
}}
.card{{
  background:var(--bg-card);
  border:1px solid var(--border);
  border-radius:10px;
  padding:22px;
  margin-bottom:20px;
  transition:border-color 0.2s;
}}
.card:hover{{border-color:rgba(0,212,255,0.25)}}
.card-title{{font-size:15px;font-weight:600;color:var(--text-primary);margin-bottom:10px}}

.code-block{{
  background:var(--bg-code);
  border:1px solid var(--border);
  border-radius:10px;
  overflow:hidden;
  margin-bottom:24px;
}}
.code-hdr{{
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:10px 16px;
  border-bottom:1px solid var(--border);
  background:rgba(255,255,255,0.02);
}}
.code-lang{{
  font-size:11px;
  font-weight:600;
  color:var(--accent-cyan);
  font-family:var(--font-mono);
  text-transform:uppercase;
  letter-spacing:0.08em;
}}
.code-file{{
  font-size:11px;
  color:var(--text-muted);
  font-family:var(--font-mono);
}}
.code-copy{{
  font-size:11px;
  cursor:pointer;
  background:none;
  border:1px solid var(--border);
  border-radius:4px;
  padding:3px 10px;
  color:var(--text-secondary);
  transition:all 0.15s;
  font-family:var(--font-sans);
}}
.code-copy:hover{{
  border-color:var(--accent-cyan);
  color:var(--accent-cyan);
}}
pre{{
  margin:0;
  padding:20px;
  overflow-x:auto;
  font-family:var(--font-mono);
  font-size:13px;
  line-height:1.75;
}}
pre::-webkit-scrollbar{{height:4px}}
pre::-webkit-scrollbar-thumb{{background:var(--border);border-radius:2px}}
.kw{{color:#c084fc}}
.fn{{color:#60a5fa}}
.str{{color:#86efac}}
.cm{{color:#4b5563;font-style:italic}}
.num{{color:#fb923c}}
.tp{{color:#67e8f9}}

.note{{
  display:flex;
  gap:12px;
  padding:14px 18px;
  border-radius:8px;
  margin-bottom:20px;
  font-size:14px;
  line-height:1.65;
}}
.note p{{margin:0}}
.n-info{{
  background:rgba(0,255,136,0.06);
  border:1px solid rgba(0,255,136,0.2);
  color:var(--accent-green);
}}
.n-warn{{
  background:rgba(245,158,11,0.08);
  border:1px solid rgba(245,158,11,0.2);
  color:#fcd34d;
}}
.n-danger{{
  background:rgba(255,107,107,0.08);
  border:1px solid rgba(255,107,107,0.2);
  color:var(--accent-coral);
}}
.n-tip{{
  background:rgba(0,212,255,0.06);
  border:1px solid rgba(0,212,255,0.2);
  color:var(--accent-cyan);
}}
.note-icon{{
  font-size:16px;
  flex-shrink:0;
  margin-top:2px;
}}
.diagram-box{{
  background:var(--bg-card);
  border:1px solid var(--border);
  border-radius:12px;
  padding:20px;
  margin-bottom:24px;
  overflow:hidden;
}}
.diagram-title{{
  font-size:11px;
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
  margin:20px 0;
  font-size:14px;
}}
table.dtable th{{
  padding:10px 14px;
  text-align:left;
  background:rgba(255,255,255,0.03);
  border-bottom:1px solid var(--border);
  color:var(--text-muted);
  font-size:11px;
  text-transform:uppercase;
  letter-spacing:0.05em;
  font-weight:600;
}}
table.dtable td{{
  padding:10px 14px;
  border-bottom:1px solid var(--border);
  color:var(--text-secondary);
}}
table.dtable tr:hover td{{
  background:rgba(255,255,255,0.02);
}}
table.dtable td code{{
  background:rgba(0,212,255,0.08);
  color:var(--accent-cyan);
  padding:2px 6px;
  border-radius:4px;
  font-family:var(--font-mono);
  font-size:12.5px;
}}
.divider{{
  border:none;
  border-top:1px solid var(--border);
  margin:32px 0;
}}

/* ── HAMBURGER & MOBILE RESPONSIVENESS ── */
.mobile-bar {{
  display:none;
  position:fixed;
  top:0;
  left:0;
  right:0;
  height:52px;
  background:var(--bg-secondary);
  border-bottom:1px solid var(--border);
  z-index:1000;
  align-items:center;
  padding:0 16px;
}}
.hamburger {{
  background:none;
  border:none;
  color:var(--text-primary);
  font-size:24px;
  cursor:pointer;
  display:flex;
  align-items:center;
  justify-content:center;
}}
.mobile-title {{
  font-size:14px;
  font-weight:600;
  color:var(--text-primary);
  margin-left:14px;
  font-family:var(--font-sans);
}}
#sidebar-overlay {{
  display:none;
  position:fixed;
  top:0;
  left:0;
  right:0;
  bottom:0;
  background:rgba(0,0,0,0.5);
  z-index:90;
  backdrop-filter:blur(3px);
}}
@media (max-width: 992px) {{
  #sidebar {{
    transform: translateX(-100%);
  }}
  #sidebar.open {{
    transform: translateX(0);
  }}
  #sidebar-overlay.open {{
    display:block;
  }}
  #topnav {{
    left:0;
    top:52px;
  }}
  #main {{
    margin-left:0;
    margin-top:104px;
  }}
  .mobile-bar {{
    display:flex;
  }}
  .content-area {{
    padding:24px 16px;
  }}
}}
</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script>
  mermaid.initialize({{
    theme: 'dark',
    startOnLoad: true,
    flowchart: {{ useMaxWidth: true, htmlLabels: true }}
  }});
</script>
</head>
<body>

<!-- MOBILE BAR -->
<div class="mobile-bar">
  <button class="hamburger">☰</button>
  <div class="mobile-title">Go Fundamentals — Cẩm Nang Chuyên Sâu</div>
</div>

<!-- SIDEBAR OVERLAY -->
<div id="sidebar-overlay"></div>

<!-- SIDEBAR -->
<nav id="sidebar">
  <div class="sidebar-logo">
    <div class="logo-icon">GO</div>
    <div>
      <div class="logo-text">Go Fundamentals</div>
      <div class="logo-sub">Master Manual</div>
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
  const sections = document.querySelectorAll('.page-section');
  sections.forEach(s => s.classList.remove('active'));
  
  const target = document.getElementById('s-' + targetId);
  if (target) target.classList.add('active');
  
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {{
    if (item.getAttribute('data-target') === targetId) {{
      item.classList.add('active');
    }} else {{
      item.classList.remove('active');
    }}
  }});
  
  const tnavs = document.querySelectorAll('.tnav');
  tnavs.forEach(item => {{
    if (item.getAttribute('data-target') === targetId) {{
      item.classList.add('active');
    }} else {{
      item.classList.remove('active');
    }}
  }});
  
  try {{
    if (history.replaceState) {{
      history.replaceState(null, null, '#s-' + targetId);
    }} else {{
      location.hash = '#s-' + targetId;
    }}
  }} catch (e) {{}}
  
  window.scrollTo({{ top: 0, behavior: 'smooth' }});
  
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
    hamburger.removeAttribute('onclick');
    hamburger.addEventListener('click', toggleSidebar);
  }}
  
  const overlay = document.getElementById('sidebar-overlay');
  if (overlay) {{
    overlay.removeAttribute('onclick');
    overlay.addEventListener('click', toggleSidebar);
  }}
}}

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

window.addEventListener('hashchange', () => {{
  const hash = window.location.hash;
  if (hash.startsWith('#s-')) {{
    show(hash.replace('#s-', ''));
  }}
}});

// Programmatic Code Block Copy
document.querySelectorAll('.code-copy').forEach(btn => {{
  btn.addEventListener('click', () => {{
    const code = btn.parentElement.nextElementSibling.innerText;
    navigator.clipboard.writeText(code).then(() => {{
      btn.innerText = 'Copied!';
      setTimeout(() => btn.innerText = 'Copy', 2000);
    }});
  }});
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
