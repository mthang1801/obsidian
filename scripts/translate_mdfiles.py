import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from deep_translator import GoogleTranslator

SOURCE_DIR = "/home/mvt/mAIvt/Documents/go/fundamental"
GLOSSARY_FILE = "/home/mvt/mAIvt/scripts/glossary.txt"

# Thread-local translator storage to avoid resource sharing issues
import threading
thread_local = threading.local()

def get_translator():
    if not getattr(thread_local, "translator", None):
        thread_local.translator = GoogleTranslator(source="en", target="vi")
    return thread_local.translator

def load_keywords():
    if not os.path.exists(GLOSSARY_FILE):
        print(f"Glossary file not found: {GLOSSARY_FILE}")
        return []
    with open(GLOSSARY_FILE, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
        
    terms = [line.strip() for line in lines if line.strip()]
    
    # Sort terms by length in descending order to avoid sub-word overlap conflicts
    terms.sort(key=len, reverse=True)
    
    regex_patterns = []
    for t in terms:
        # Emojis/symbols or slashes like async/await don't support \b perfectly
        if not re.match(r'^[a-zA-Z0-9_\s]+$', t):
            regex_patterns.append(re.escape(t))
        else:
            # Use word boundaries case-insensitively to prevent partial sub-word matching
            regex_patterns.append(rf'\b{re.escape(t)}\b')
            
    return regex_patterns

# Pre-load patterns once globally
KEYWORDS_PATTERNS = load_keywords()

def post_process_vietnamese(text):
    # Professional developer terminology replacements
    replacements = [
        (r'chỉ cắn trong quá trình sản xuất', 'chỉ phát hiện ra khi chạy trên production'),
        (r'chỉ cắn trong sản xuất', 'chỉ phát sinh lỗi trên production'),
        (r'chỉ cắn khi chạy trên production', 'chỉ phát hiện được trên production'),
        (r'chỉ cắn', 'chỉ phát sinh lỗi'),
        (r'vượt qua một điều kiện', 'truyền vào một điều kiện'),
        (r'vượt qua tham số', 'truyền vào tham số'),
        (r'vượt qua', 'truyền vào'),
        (r'chấp nhận xung đột', 'khả năng xảy ra xung đột'),
        (r'bản đồ', 'ánh xạ'),
        (r'lập bản đồ', 'ánh xạ'),
        (r'hoảng sợ thời gian chạy', 'runtime panic'),
        (r'hoảng sợ', 'panic'),
        (r'nuốt runtime hoảng sợ', 'nuốt panic thời gian chạy (runtime panic)'),
        (r'SQL tiêm', 'SQL Injection'),
        (r'tiêm SQL', 'SQL Injection'),
        (r'đơn cách ly', 'cô lập độc lập'),
        (r'công nhân', 'worker'),
        (r'nhân viên', 'worker'),
        (r'luồng thông lượng', 'thông lượng (throughput)'),
        (r'thông lượng đọc', 'throughput đọc'),
        (r'khóa cấp độ row', 'khóa dòng (Row-level Locking)'),
        (r'khóa bi quan', 'Pessimistic Locking (Khóa bi quan)'),
        (r'khóa lạc quan', 'Optimistic Locking (Khóa lạc quan)'),
        (r'bản ghi bị xóa vật lý', 'bản ghi bị xóa vật lý (hard delete)'),
        (r'xóa mềm', 'Soft Delete (Xóa mềm)'),
        (r'xóa cứng', 'Hard Delete (Xóa cứng)'),
        (r'rò rỉ kết nối', 'Connection Leak (Rò rỉ kết nối)'),
        (r'giẫm đạp', 'Cache Stampede (Giẫm đạp cache)'),
        (r'khóa tối ưu', 'Optimistic Locking'),
        (r'khóa bình thường', 'ràng buộc duy nhất (Unique Constraint)'),
        (r'ranh giới sản xuất deadlock', 'ranh giới phát sinh deadlock'),
        (r'bỏ qua các giá trị 0', 'bỏ qua các zero-value'),
        (r'giá trị 0', 'zero value'),
        (r'lỗi hoảng sợ', 'lỗi panic'),
        (r'đối tượng map', 'map'),
        (r'cấu hình lạc quan', 'cấu hình Optimistic Locking'),
        (r'cấu hình bi quan', 'cấu hình Pessimistic Locking'),
        (r'bản cập nhật bị mất', 'Lost Update (Cập nhật bị ghi đè)'),
        (r'xử lý kép', 'double processing (xử lý trùng lặp)'),
        (r'mô hình lạc quan', 'Optimistic Locking'),
        (r'mô hình bi quan', 'Pessimistic Locking'),
        (r'chỉ định ranh giới', 'phân định ranh giới'),
        (r'vòng lặp đọc-sửa-ghi', 'vòng lặp read-modify-write'),
        (r'nhân viên trùng lặp', 'worker trùng lặp'),
        (r'mất thao tác cập nhật', 'Lost Update (Bản cập nhật bị mất)'),
        (r'thuộc tính bi quan', 'Pessimistic Locking'),
        (r'thuộc tính lạc quan', 'Optimistic Locking'),
        (r'ràng buộc của Optimistic Locking', 'ràng buộc Optimistic Locking'),
        (r'hệ thống theo dõi con trỏ', 'hệ thống theo dõi cursor'),
        (r'con trỏ phân trang', 'Keyset Pagination (Phân trang theo con trỏ)'),
        (r'ghi bình thường', 'ghi nhận bình thường'),
        (r'đọc replicas', 'Read Replicas'),
        (r'độ trễ replica', 'Replication Lag'),
        (r'kết nối limits', 'giới hạn kết nối (connection limits)'),
        (r'limits', 'giới hạn (limits)'),
        (r'độ trễ sao chép', 'Replication Lag'),
        (r'phân trang con trỏ', 'Keyset Pagination (Phân trang theo con trỏ)'),
        (r'phân trang bộ phím', 'Keyset Pagination (Phân trang theo con trỏ)'),
        (r'phân trang sâu', 'Phân trang sâu (Deep Pagination)'),
        (r'cơ sở dữ liệu chính', 'Database Primary'),
        (r'ghi chính', 'ghi vào Primary'),
        (r'thế hệ deadlock', 'phát sinh deadlock'),
        (r'deadlock thế hệ', 'phát sinh deadlock'),
        (r'khóa hàng', 'row lock'),
        (r'khóa các hàng', 'lock các row'),
        (r'con trỏ', 'cursor'),
        (r'lỗi swallowed', 'lỗi bị nuốt (swallowed error)'),
        (r'errors nuốt \(swallowed\)', 'error bị nuốt (swallowed error)'),
        (r'error bị nuốt \(swallowed\) \(swallowed error\)', 'error bị nuốt (swallowed error)'),
        (r'error bị nuốt \(swallowed error\) \(swallowed\)', 'error bị nuốt (swallowed error)'),
        (r'errors nuốt', 'error bị nuốt (swallowed error)'),
        (r'lớp bảo vệ', 'màng chắn bảo vệ'),
        
        # Post-restoration grammar / syntax adjustments
        (r'Optimistic Locking ràng buộc', 'ràng buộc Optimistic Locking'),
        (r'Pessimistic Locking ràng buộc', 'ràng buộc Pessimistic Locking'),
        (r'Optimistic Locking cấu hình', 'cấu hình Optimistic Locking'),
        (r'Pessimistic Locking cấu hình', 'cấu hình Pessimistic Locking'),
        (r'Optimistic Locking mô hình', 'mô hình Optimistic Locking'),
        (r'Pessimistic Locking mô hình', 'mô hình Pessimistic Locking'),
        (r'Pessimistic Locking cấp hàng', 'Pessimistic Locking cấp dòng'),
        (r'Optimistic Locking cấp hàng', 'Optimistic Locking cấp dòng')
    ]
    
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text

def translate_chunk(text, translator):
    if not text.strip():
        return text
        
    placeholders = []
    
    # 1. Protect Markdown Images: ![alt](url)
    def repl_img(match):
        placeholders.append(match.group(0))
        return f" [[[A{len(placeholders)-1}]]] "
    text = re.sub(r'!\[.*?\]\(.*?\)', repl_img, text)
    
    # 2. Protect Markdown Links: [text](url)
    def repl_link(match):
        placeholders.append(match.group(0))
        return f" [[[B{len(placeholders)-1}]]] "
    text = re.sub(r'\[[^\]]+\]\([^)]+\)', repl_link, text)
    
    # 3. Protect Inline Code: `code`
    def repl_inline(match):
        placeholders.append(match.group(0))
        return f" [[[C{len(placeholders)-1}]]] "
    text = re.sub(r'`[^`]+`', repl_inline, text)
    
    # 4. Protect HTML tags
    def repl_html(match):
        placeholders.append(match.group(0))
        return f" [[[D{len(placeholders)-1}]]] "
    text = re.sub(r'<[^>]+>', repl_html, text)
    
    # 5. Protect Technical Keywords dynamically from glossary.txt
    def repl_kw(match):
        placeholders.append(match.group(0))
        return f" [[[E{len(placeholders)-1}]]] "
        
    # Apply regular expression search case-insensitively for protected terms
    for pattern in KEYWORDS_PATTERNS:
        text = re.sub(pattern, repl_kw, text, flags=re.IGNORECASE)
    
    # Translate the entire chunk in a single API call
    try:
        translated = translator.translate(text)
        if not translated:
            translated = text
    except Exception as e:
        print(f"Translation error, retrying... Error: {e}")
        time.sleep(1.5)
        try:
            translated = translator.translate(text)
            if not translated:
                translated = text
        except Exception as e:
            print(f"Failed to translate chunk: {e}")
            return text
            
    # Restore placeholders in reverse order
    for idx in range(len(placeholders) - 1, -1, -1):
        translated = re.sub(rf'\[+A{idx}\]+', placeholders[idx], translated, flags=re.IGNORECASE)
        translated = re.sub(rf'\[+B{idx}\]+', placeholders[idx], translated, flags=re.IGNORECASE)
        translated = re.sub(rf'\[+C{idx}\]+', placeholders[idx], translated, flags=re.IGNORECASE)
        translated = re.sub(rf'\[+D{idx}\]+', placeholders[idx], translated, flags=re.IGNORECASE)
        translated = re.sub(rf'\[+E{idx}\]+', placeholders[idx], translated, flags=re.IGNORECASE)
        
    # Apply premium Vietnamese software engineering post-processing AFTER placeholder restoration
    translated = post_process_vietnamese(translated)
        
    translated = re.sub(r' +', ' ', translated).strip()
    return translated

def translate_prose_block(text, translator):
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = []
    current_len = 0
    
    for p in paragraphs:
        if current_len + len(p) + 2 > 4000:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [p]
            current_len = len(p)
        else:
            current_chunk.append(p)
            current_len += len(p) + 2
            
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
        
    translated_chunks = []
    for chunk in chunks:
        translated_chunks.append(translate_chunk(chunk, translator))
        
    return "\n\n".join(translated_chunks)

def translate_markdown_file(filepath):
    translator = get_translator()
    start_time = time.time()
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    parts = re.split(r'(```[a-zA-Z0-9_-]*\n.*?```)', content, flags=re.DOTALL)
    
    translated_parts = []
    for part in parts:
        if part.startswith("```"):
            translated_parts.append(part)
        else:
            translated_parts.append(translate_prose_block(part, translator))
            
    translated_content = "".join(translated_parts)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(translated_content)
    print(f"Finished: {os.path.basename(filepath)} in {time.time() - start_time:.2f}s")

def main():
    print("Reverting files for fresh translation...")
    os.system("git checkout -- /home/mvt/mAIvt/Documents/go/fundamental/")
    
    all_files = []
    for root, dirs, files in os.walk(SOURCE_DIR):
        if "images" in root:
            continue
        for file in files:
            if file.endswith(".md") and file != "README.md":
                all_files.append(os.path.join(root, file))
                
    all_files.sort()
    total = len(all_files)
    print(f"Found {total} markdown files to translate in parallel with dynamic glossary.")
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(translate_markdown_file, all_files)
        
    print("ALL TRANSLATIONS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
