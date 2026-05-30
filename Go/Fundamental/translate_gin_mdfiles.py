import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from deep_translator import app

SOURCE_DIR = "/home/mvt/mAIvt/Documents/go/gin"

def get_translator():
    return GoogleTranslator(source='en', target='vi')

def translate_chunk(text, translator):
    if not text or not text.strip():
        return text
        
    # If purely symbols/markdown structure, return unchanged
    if re.match(r'^[\|\-\s\d\.\:\#\🔀🟢🟠🔴🔵🟡ℹ️⚠️💡✅\(\)\[\]\`]+$', text):
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
    
    # Translate
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
            
    # Restore placeholders
    for idx in range(len(placeholders) - 1, -1, -1):
        token_img = f"[[[A{idx}]]]"
        token_link = f"[[[B{idx}]]]"
        token_inline = f"[[[C{idx}]]]"
        token_html = f"[[[D{idx}]]]"
        
        translated = re.sub(rf'\s*\[\[\[\s*A{idx}\s*\]\]\]\s*', f' {placeholders[idx]} ', translated, flags=re.IGNORECASE)
        translated = re.sub(rf'\s*\[\[\[\s*B{idx}\s*\]\]\]\s*', f' {placeholders[idx]} ', translated, flags=re.IGNORECASE)
        translated = re.sub(rf'\s*\[\[\[\s*C{idx}\s*\]\]\]\s*', f' {placeholders[idx]} ', translated, flags=re.IGNORECASE)
        translated = re.sub(rf'\s*\[\[\[\s*D{idx}\s*\]\]\]\s*', f' {placeholders[idx]} ', translated, flags=re.IGNORECASE)
        
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
        
    # Check if already translated
    if "Trình điều khiển" in content or "Vòng đời request" in content or "Bản ghi lỗi" in content:
        print(f"Skipping already translated file: {os.path.basename(filepath)}")
        return
        
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
    print("Reverting files in go/gin for fresh translation...")
    os.system("git checkout -- /home/mvt/mAIvt/Documents/go/gin/")
    
    all_files = []
    for root, dirs, files in os.walk(SOURCE_DIR):
        if "images" in root:
            continue
        for file in files:
            if file.endswith(".md") and file != "README.md":
                all_files.append(os.path.join(root, file))
                
    all_files.sort()
    total = len(all_files)
    print(f"Found {total} Gin markdown files to translate in parallel.")
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(translate_markdown_file, all_files)
        
    print("ALL GIN TRANSLATIONS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
