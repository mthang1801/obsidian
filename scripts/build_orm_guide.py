import re
import os

# Paths
SOURCE_DIR = "/home/mvt/mAIvt/Documents/go/orm"
TARGET_FILE = "/home/mvt/mAIvt/Go/Fundamental/go-orm-guide.html"

# Mapping of section ID to markdown file path, category, and badge
MAPPING = [
    {"id": "models-and-connection", "path": "01-models-and-connection.md", "category": "Connection & Initialization", "badge": "CONNECTION"},
    {"id": "crud", "path": "02-crud.md", "category": "Core CRUD Operations", "badge": "CRUD"},
    {"id": "querying", "path": "03-querying.md", "category": "Core CRUD Operations", "badge": "QUERYING"},
    {"id": "associations", "path": "04-associations.md", "category": "Data Relationships", "badge": "ASSOCIATIONS"},
    {"id": "transactions-and-hooks", "path": "05-transactions-and-hooks.md", "category": "Transactions & Logic", "badge": "TRANSACTIONS"},
    {"id": "migration-and-advanced", "path": "06-migration-and-advanced.md", "category": "Database Migrations", "badge": "MIGRATIONS"},
    {"id": "transaction-patterns", "path": "07-transaction-patterns.md", "category": "Transactions & Logic", "badge": "TRANSACTIONS"},
    {"id": "row-locking-and-concurrency-control", "path": "08-row-locking-and-concurrency-control.md", "category": "Concurrency & Locking", "badge": "LOCKING"},
    {"id": "large-pagination-and-batch-processing", "path": "09-large-pagination-and-batch-processing.md", "category": "High Performance Patterns", "badge": "PERFORMANCE"},
    {"id": "multi-tenant-patterns", "path": "10-multi-tenant-patterns.md", "category": "Enterprise Scale", "badge": "ENTERPRISE"},
    {"id": "read-write-splitting-replicas", "path": "11-read-write-splitting-replicas.md", "category": "Enterprise Scale", "badge": "ENTERPRISE"},
    {"id": "performance-tuning-and-query-observability", "path": "12-performance-tuning-and-query-observability.md", "category": "High Performance Patterns", "badge": "PERFORMANCE"}
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
        "Buffer", "File", "FileMode", "Seq", "Seq2", "DB", "Config", "Dialector"
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

def translate_text(text):
    if not text:
        return ""
        
    # Structural headings and badges replacement
    for key, val in TRANSLATIONS.items():
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
        
    text = translate_text(text)
    
    text = extract_and_replace_tables(text)
    text = process_blockquotes(text)
    
    text = re.sub(r'^### (.*)', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)
    
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
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
        
    content = re.sub(r'```##\s*([0-6]\.)', r'```\n## \1', content)
    content = re.sub(r'(### [^\n]+)```([a-zA-Z0-9_-]+)', r'\1\n```\2', content)
    content = content.replace("```![", "![")
        
    clean_content_for_title = re.sub(r'<!--.*?-->', '', content).strip()
    title_match = re.search(r'^#\s*(.*)', clean_content_for_title, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Chuyên đề ORM"
    
    # Strip numbers at front (e.g. 01 — Models & Connection -> Models & Connection)
    clean_title = re.sub(r'^[0-9\s—\-#]*', '', title).strip()
    if not clean_title:
        clean_title = title
        
    # 1. DEFINE
    define_match = re.search(r'## 1\.[^\n]*\n(.*?)(?=## 2\.|\Z)', content, re.DOTALL)
    define_html = ""
    if define_match:
        sec = define_match.group(1).strip()
        define_html = render_markdown_prose(sec)
        
    # 2. VISUAL
    visual_match = re.search(r'## 2\.[^\n]*\n(.*?)(?=## 3\.|\Z)', content, re.DOTALL)
    visual_html = ""
    if visual_match:
        sec = visual_match.group(1).strip()
        
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
        
    # 3. CODE
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
            
    # 4. PITFALLS
    pitfalls_match = re.search(r'## 4\.[^\n]*\n(.*?)(?=## 5\.|\Z)', content, re.DOTALL)
    pitfalls_html = ""
    if pitfalls_match:
        sec = pitfalls_match.group(1).strip()
        pitfalls_html = render_markdown_prose(sec)

    # 5. REF
    ref_match = re.search(r'## 5\.[^\n]*\n(.*?)(?=## 6\.|\Z)', content, re.DOTALL)
    ref_html = ""
    if ref_match:
        sec = ref_match.group(1).strip()
        ref_html = render_markdown_prose(sec)
            
    # 6. RECOMMEND
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
                    <div class="sec-sub">Chủ đề {idx+1:02d} chuyên sâu trong lộ trình phát triển Go ORM & GORM</div>
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
<title>Go ORM — Cẩm nang GORM & Database Patterns chuyên sâu</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{{
  --bg-primary:#0d0f14;
  --bg-secondary:#131720;
  --bg-card:#1a1f2e;
  --border:#262f45;
  --text-primary:#f3f4f6;
  --text-secondary:#b7c1d7;
  --text-muted:#6b7280;
  --accent-cyan:#00d4ff;
  --accent-green:#10b981;
  --accent-coral:#ff6b6b;
  --accent-orange:#f59e0b;
  --accent-purple:#a855f7;
  --font-sans:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;
  --font-mono:'JetBrains Mono',monospace;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{
  background:var(--bg-primary);
  color:var(--text-primary);
  font-family:var(--font-sans);
  font-size:14.5px;
  line-height:1.6;
  overflow:hidden;
  display:flex;
  height:100vh;
}}
a{{color:var(--accent-cyan);text-decoration:none}}
a:hover{{text-decoration:underline}}
#sidebar{{
  width:270px;
  background:var(--bg-secondary);
  border-right:1px solid var(--border);
  display:flex;
  flex-direction:column;
  height:100%;
  flex-shrink:0;
  z-index:100;
  transition:transform .3s cubic-bezier(0.4, 0, 0.2, 1);
}}
.sidebar-hdr{{
  padding:20px 24px;
  border-bottom:1px solid var(--border);
  display:flex;
  align-items:center;
  gap:12px;
}}
.logo-box{{
  width:36px;
  height:36px;
  border-radius:8px;
  background:linear-gradient(135deg, #00d4ff 0%, #a855f7 100%);
  display:flex;
  align-items:center;
  justify-content:center;
  color:#fff;
  font-weight:700;
  font-size:18px;
  font-family:var(--font-mono);
}}
.logo-title{{
  font-size:15px;
  font-weight:700;
  color:var(--text-primary);
  line-height:1.2;
}}
.logo-sub{{
  font-size:9px;
  color:var(--accent-cyan);
  font-family:var(--font-mono);
  letter-spacing:.05em;
}}
.nav-section{{padding:14px 12px 6px; overflow-y:auto; flex-grow:1}}
.nav-section::-webkit-scrollbar{{width:4px}}
.nav-section::-webkit-scrollbar-thumb{{background:var(--border);border-radius:4px}}
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
  background:none;
  border:none;
  color:var(--text-secondary);
  font-size:12px;
  font-weight:500;
  padding:6px 12px;
  border-radius:20px;
  cursor:pointer;
  transition:all .15s;
  white-space:nowrap;
}}
.tnav:hover{{background:rgba(255,255,255,.03);color:var(--text-primary)}}
.tnav.active{{
  background:var(--accent-cyan);
  color:#0d0f14;
  font-weight:600;
}}
#main-content{{
  flex-grow:1;
  padding-top:52px;
  height:100%;
  overflow-y:auto;
  position:relative;
}}
#main-content::-webkit-scrollbar{{width:6px}}
#main-content::-webkit-scrollbar-thumb{{background:var(--border);border-radius:4px}}
.page-section{{
  display:none;
  max-width:960px;
  margin:0 auto;
  padding:40px 24px 80px;
}}
.page-section.active{{display:block}}
.sec-header{{
  display:flex;
  align-items:center;
  gap:16px;
  margin-bottom:32px;
  border-bottom:1px solid var(--border);
  padding-bottom:20px;
}}
.sec-num{{
  width:44px;
  height:44px;
  border-radius:8px;
  background:rgba(0,212,255,.08);
  border:1px solid rgba(0,212,255,.2);
  color:var(--accent-cyan);
  display:flex;
  align-items:center;
  justify-content:center;
  font-family:var(--font-mono);
  font-weight:700;
  font-size:20px;
}}
.sec-title{{font-size:22px;font-weight:700;color:var(--text-primary)}}
.sec-sub{{font-size:12.5px;color:var(--text-muted);margin-top:2px}}
.concept-box{{
  background:var(--bg-card);
  border:1px solid var(--border);
  border-radius:12px;
  padding:24px;
  margin-bottom:32px;
}}
.concept-box .label{{
  font-family:var(--font-mono);
  font-size:11px;
  font-weight:700;
  text-transform:uppercase;
  letter-spacing:.08em;
  color:var(--accent-cyan);
  margin-bottom:12px;
}}
.concept-box .ctitle{{
  font-size:18px;
  font-weight:700;
  color:var(--text-primary);
  margin-bottom:16px;
}}
.prose{{margin-bottom:16px;color:var(--text-secondary);line-height:1.7}}
h3{{
  font-size:16px;
  font-weight:700;
  margin-top:36px;
  margin-bottom:16px;
  color:var(--text-primary);
  display:flex;
  align-items:center;
  gap:8px;
}}
.card{{
  background:var(--bg-card);
  border:1px solid var(--border);
  border-radius:12px;
  padding:20px;
  margin-bottom:20px;
}}
.card-title{{
  font-size:14.5px;
  font-weight:700;
  margin-bottom:12px;
}}
.badge{{
  font-size:10px;
  font-weight:700;
  padding:3px 10px;
  border-radius:12px;
  font-family:var(--font-mono);
}}
.b-basic{{background:rgba(16,185,129,.12);color:var(--accent-green);border:1px solid rgba(16,185,129,.2)}}
.b-advanced{{background:rgba(245,158,11,.12);color:var(--accent-orange);border:1px solid rgba(245,158,11,.2)}}
.b-expert{{background:rgba(0,212,255,.08);color:var(--accent-cyan);border:1px solid rgba(0,212,255,.2)}}
.dtable{{
  width:100%;
  border-collapse:collapse;
  margin:16px 0 24px;
  font-size:13.5px;
}}
.dtable th, .dtable td{{
  padding:12px 14px;
  text-align:left;
  border-bottom:1px solid var(--border);
}}
.dtable th{{
  background:rgba(255,255,255,.02);
  color:var(--text-primary);
  font-weight:600;
}}
.dtable td{{color:var(--text-secondary)}}
.note{{
  display:flex;
  gap:12px;
  padding:14px 16px;
  border-radius:8px;
  font-size:13px;
  line-height:1.5;
  margin:16px 0;
}}
.note-icon{{font-size:16px;flex-shrink:0}}
.n-info{{background:rgba(0,212,255,.04);border-left:4px solid var(--accent-cyan);color:var(--text-secondary)}}
.n-tip{{background:rgba(16,185,129,.04);border-left:4px solid var(--accent-green);color:var(--text-secondary)}}
.n-warn{{background:rgba(255,107,107,.04);border-left:4px solid var(--accent-coral);color:var(--text-secondary)}}
.divider{{
  height:1px;
  background:var(--border);
  margin:40px 0;
}}
.code-block{{
  background:#090b10;
  border:1px solid var(--border);
  border-radius:8px;
  overflow:hidden;
  font-family:var(--font-mono);
  font-size:13px;
  margin-top:16px;
}}
.code-hdr{{
  background:rgba(255,255,255,.02);
  padding:8px 16px;
  display:flex;
  align-items:center;
  border-bottom:1px solid var(--border);
}}
.code-lang{{color:var(--text-muted);font-weight:700;font-size:11px}}
.code-file{{color:var(--text-secondary);font-size:11px;margin-left:12px;font-weight:500}}
.code-copy{{
  margin-left:auto;
  background:rgba(255,255,255,.04);
  border:1px solid var(--border);
  color:var(--text-secondary);
  font-size:11px;
  padding:3px 8px;
  border-radius:4px;
  cursor:pointer;
  transition:all .15s;
}}
.code-copy:hover{{background:rgba(255,255,255,.08);color:var(--text-primary)}}
.code-block pre{{padding:16px;overflow-x:auto;margin:0}}
.code-block code{{font-family:inherit;color:inherit;padding:0;background:none;border-radius:0;font-size:inherit}}
code{{
  background:rgba(255,255,255,.06);
  color:var(--accent-cyan);
  padding:2px 6px;
  border-radius:4px;
  font-family:var(--font-mono);
  font-size:12.5px;
}}
.kw{{color:#ff7b72;font-weight:500}}
.tp{{color:#79c0ff}}
.str{{color:#a5d6ff}}
.fn{{color:#d2a8ff}}
.cm{{color:#8b949e;font-style:italic}}
.num{{color:#f0883e}}
.hamburger{{
  display:none;
  background:none;
  border:none;
  color:var(--text-primary);
  font-size:20px;
  cursor:pointer;
  padding:8px;
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
}}
@media (max-width:1024px){{
  #sidebar{{
    position:fixed;
    top:0;
    bottom:0;
    left:0;
    transform:translateX(-100%);
  }}
  #sidebar.open{{
    transform:translateX(0);
  }}
  #topnav{{
    left:0;
    padding-left:12px;
  }}
  .hamburger{{
    display:block;
  }}
  #sidebar-overlay.open{{
    display:block;
  }}
}}
</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script>
mermaid.initialize({{
  startOnLoad:true,
  theme:'dark',
  themeVariables:{{
    background:'#131720',
    primaryColor:'#1a1f2e',
    primaryTextColor:'#f3f4f6',
    lineColor:'#262f45'
  }}
}});
</script>
</head>
<body>
<div id="sidebar-overlay"></div>
<aside id="sidebar">
  <div class="sidebar-hdr">
    <div class="logo-box">G</div>
    <div>
      <div class="logo-title">Go ORM</div>
      <div class="logo-sub">GORM & DATABASE PATTERNS</div>
    </div>
  </div>
  <nav class="nav-section">
    {sidebar_items_html}
  </nav>
</aside>

<div id="main-content">
  <header id="topnav">
    <button class="hamburger">☰</button>
    {topnav_items_html}
  </header>
  
  {sections_html}
</div>

<script>
function show(id) {{
  document.querySelectorAll('.page-section').forEach(sec => sec.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
  document.querySelectorAll('.tnav').forEach(item => item.classList.remove('active'));
  
  const targetSec = document.getElementById('s-' + id);
  if (targetSec) targetSec.classList.add('active');
  
  const sidebarItem = document.querySelector(`.nav-item[data-target="${{id}}"]`);
  if (sidebarItem) sidebarItem.classList.add('active');
  
  const topnavItem = document.querySelector(`.tnav[data-target="${{id}}"]`);
  if (topnavItem) {{
    topnavItem.classList.add('active');
    topnavItem.scrollIntoView({{ behavior: 'smooth', block: 'nearest', inline: 'center' }});
  }}
  
  const main = document.getElementById('main-content');
  if (main) main.scrollTop = 0;
}}

function toggleSidebar() {{
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  if (sidebar && overlay) {{
    sidebar.classList.toggle('open');
    overlay.classList.toggle('open');
  }}
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
    print("Done! Perfectly clean & enriched HTML ORM guide generated successfully from scratch.")

if __name__ == "__main__":
    build()
