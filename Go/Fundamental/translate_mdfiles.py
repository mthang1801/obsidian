import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from deep_translator import GoogleTranslator

SOURCE_DIR = "/home/mvt/mAIvt/Documents/go/fundamental"

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
    
    # 5. Protect Technical Keywords from translation distortion (e.g. Go, slice, nil, panic, recover, defer, map, channel, goroutine, interface, struct, swagger, mocking, dependency injection)
    keywords = [
        # Concurrency & Threads
        r'\bconcurrency\b', r'\bConcurrency\b',
        r'\bgoroutine\b', r'\bgoroutines\b', r'\bGoroutine\b', r'\bGoroutines\b',
        r'\bchannel\b', r'\bchannels\b', r'\bChannel\b', r'\bChannels\b',
        r'\bselect\b', r'\bSelect\b',
        r'\bmutex\b', r'\bMutex\b',
        r'\bwaitgroup\b', r'\bWaitGroup\b',
        r'\brace condition\b', r'\brace conditions\b', r'\bRace Condition\b',
        r'\bdeadlock\b', r'\bdeadlocks\b', r'\bDeadlock\b',
        r'\bthread\b', r'\bthreads\b', r'\bThread\b', r'\bThreads\b',
        r'\bevent loop\b', r'\bEvent Loop\b',
        r'\bworker pool\b', r'\bWorker Pool\b',
        r'\bsemaphore\b', r'\bSemaphore\b',
        
        # Async & JS/TS Concepts
        r'\basync/await\b', r'\bAsync/Await\b',
        r'\basync\b', r'\bAsync\b',
        r'\bawait\b', r'\bAwait\b',
        r'\bpromise\b', r'\bpromises\b', r'\bPromise\b', r'\bPromises\b',
        r'\bcallback\b', r'\bcallbacks\b', r'\bCallback\b',
        r'\bobservable\b', r'\bObservable\b',
        r'\bgenerator\b', r'\bgenerators\b', r'\bGenerator\b',
        r'\byield\b', r'\bYield\b',
        r'\bprototype\b', r'\bPrototype\b',
        
        # Memory & Runtime
        r'\bstack\b', r'\bStack\b',
        r'\bheap\b', r'\bHeap\b',
        r'\bpointer\b', r'\bpointers\b', r'\bPointer\b', r'\bPointers\b',
        r'\bescape analysis\b', r'\bEscape Analysis\b',
        r'\bmemory allocation\b', r'\bMemory Allocation\b',
        r'\bgarbage collector\b', r'\bGarbage Collector\b', r'\bGC\b',
        r'\bruntime\b', r'\bRuntime\b',
        
        # Data Structures & Types
        r'\barray\b', r'\barrays\b', r'\bArray\b', r'\bArrays\b',
        r'\bslice\b', r'\bslices\b', r'\bSlice\b', r'\bSlices\b',
        r'\bmap\b', r'\bmaps\b', r'\bMap\b', r'\bMaps\b',
        r'\bstruct\b', r'\bstructs\b', r'\bStruct\b', r'\bStructs\b',
        r'\binterface\b', r'\binterfaces\b', r'\bInterface\b', r'\bInterfaces\b',
        r'\bgeneric\b', r'\bgenerics\b', r'\bGeneric\b', r'\bGenerics\b',
        r'\bcomparable\b', r'\bComparable\b',
        r'\bany\b', r'\bAny\b',
        r'\biota\b', r'\bIota\b',
        r'\bclosure\b', r'\bclosures\b', r'\bClosure\b', r'\bClosures\b',
        
        # Go Primitives & Language
        r'\bdefer\b', r'\bDefer\b',
        r'\bpanic\b', r'\bPanic\b',
        r'\brecover\b', r'\bRecover\b',
        r'\bnil\b', r'\bNil\b',
        r'\breceiver\b', r'\breceivers\b', r'\bReceiver\b', r'\bReceivers\b',
        r'\bvalue receiver\b', r'\bValue Receiver\b',
        r'\bpointer receiver\b', r'\bPointer Receiver\b',
        r'\bembedding\b', r'\bEmbedding\b',
        r'\btype assertion\b', r'\bType Assertion\b',
        r'\btype switch\b', r'\bType Switch\b',
        r'\bimplicit interface\b', r'\bImplicit Interface\b',
        r'\bsignature\b', r'\bsignatures\b', r'\bSignature\b',
        r'\bblank identifier\b', r'\bBlank Identifier\b',
        
        # Tooling & Packaging
        r'\bpackage\b', r'\bpackages\b', r'\bPackage\b', r'\bPackages\b',
        r'\bmodule\b', r'\bmodules\b', r'\bModule\b', r'\bModules\b',
        r'\bworkspace\b', r'\bworkspaces\b', r'\bWorkspace\b', r'\bWorkspaces\b',
        r'\bvendoring\b', r'\bVendoring\b',
        r'\bdependency injection\b', r'\bDependency Injection\b', r'\bDI\b',
        r'\bmocking\b', r'\bmock\b', r'\bmocks\b', r'\bMocking\b', r'\bMock\b',
        
        # Testing
        r'\btable-driven test\b', r'\btable-driven testing\b', r'\bTable-driven test\b', r'\bTable-driven testing\b',
        r'\bbenchmark\b', r'\bbenchmarks\b', r'\bBenchmark\b', r'\bBenchmarks\b',
        r'\bfuzzing\b', r'\bfuzz test\b', r'\bfuzz testing\b', r'\bFuzzing\b', r'\bFuzz test\b',
        r'\bintegration test\b', r'\bIntegration Test\b',
        r'\bunit test\b', r'\bUnit Test\b',
        r'\btestcontainers\b', r'\bTestcontainers\b',
        
        # Error handling
        r'\berror wrapping\b', r'\bError Wrapping\b',
        r'\bsentinel error\b', r'\bSentinel Error\b',
        r'\bcustom error\b', r'\bCustom Error\b',
        
        # Helpers & Library
        r'\bdate time\b', r'\bDate Time\b', r'\bdatetime\b', r'\bDateTime\b',
        r'\bdate\b', r'\bDate\b',
        r'\btime\b', r'\bTime\b',
        r'\bformat\b', r'\bFormat\b',
        r'\bregex\b', r'\bRegex\b', r'\bregular expression\b', r'\bRegular Expression\b',
        r'\bstrconv\b', r'\bStrconv\b',
        r'\bpipeline\b', r'\bPipeline\b',
        r'\biterator\b', r'\bIterator\b',
        
        # OOP & Patterns
        r'\bsolid\b', r'\bSOLID\b',
        r'\bcomposition\b', r'\bComposition\b',
        r'\binheritance\b', r'\bInheritance\b',
        r'\bpolymorphism\b', r'\bPolymorphism\b',
        r'\bencapsulation\b', r'\bEncapsulation\b',
        r'\bdesign pattern\b', r'\bdesign patterns\b', r'\bDesign Pattern\b', r'\bDesign Patterns\b',
        r'\bbuilder\b', r'\bBuilder\b',
        r'\bfactory\b', r'\bFactory\b',
        r'\bsingleton\b', r'\bSingleton\b',
        r'\bobserver\b', r'\bObserver\b',
        r'\bstrategy\b', r'\bStrategy\b',
        r'\bdecorator\b', r'\bDecorator\b',
        
        # Tech ecosystem
        r'\bswagger\b', r'\bSwagger\b',
        r'\bopenapi\b', r'\bOpenAPI\b',
        r'\bcors\b', r'\bCORS\b',
        r'\bcsrf\b', r'\bCSRF\b',
        r'\bjwt\b', r'\bJWT\b',
        r'\bauth\b', r'\bAuth\b',
        r'\brbac\b', r'\bRBAC\b',
        r'\bcaching\b', r'\bCaching\b',
        r'\brate limiting\b', r'\bRate Limiting\b',
        r'\bsession\b', r'\bsessions\b', r'\bSession\b',
        r'\bcookie\b', r'\bcookies\b', r'\bCookie\b',
        r'\bdatabase\b', r'\bDatabase\b',
        r'\borm\b', r'\bORM\b',
        r'\bgorm\b', r'\bGORM\b',
        r'\bGo\b',
    ]
    keywords.sort(key=len, reverse=True)
    
    def repl_kw(match):
        placeholders.append(match.group(0))
        return f" [[[E{len(placeholders)-1}]]] "
        
    for kw in keywords:
        text = re.sub(kw, repl_kw, text)
    
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
        token_img = f"[[[A{idx}]]]"
        token_link = f"[[[B{idx}]]]"
        token_inline = f"[[[C{idx}]]]"
        token_html = f"[[[D{idx}]]]"
        token_kw = f"[[[E{idx}]]]"
        
        # Use regex to restore with flexible spacing
        translated = re.sub(rf'\s*\[\[\[\s*A{idx}\s*\]\]\]\s*', f' {placeholders[idx]} ', translated, flags=re.IGNORECASE)
        translated = re.sub(rf'\s*\[\[\[\s*B{idx}\s*\]\]\]\s*', f' {placeholders[idx]} ', translated, flags=re.IGNORECASE)
        translated = re.sub(rf'\s*\[\[\[\s*C{idx}\s*\]\]\]\s*', f' {placeholders[idx]} ', translated, flags=re.IGNORECASE)
        translated = re.sub(rf'\s*\[\[\[\s*D{idx}\s*\]\]\]\s*', f' {placeholders[idx]} ', translated, flags=re.IGNORECASE)
        translated = re.sub(rf'\s*\[\[\[\s*E{idx}\s*\]\]\]\s*', f' {placeholders[idx]} ', translated, flags=re.IGNORECASE)
        
    translated = re.sub(r' +', ' ', translated).strip()
    return translated

def translate_prose_block(text, translator):
    # Split by double newlines into logical paragraphs, and group into larger chunks under 4000 characters
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
        
    # Check if already translated (disabled for fresh translation)
    # if "Trì hoãn, hoảng sợ" in content or "Diện mạo" in content or "Bài học rút ra" in content:
    #     print(f"Skipping already translated file: {os.path.basename(filepath)}")
    #     return
        
    # Split content by markdown code blocks
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
    # Revert modified files to ensure fresh, clean translation from English sources!
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
    print(f"Found {total} markdown files to translate in parallel.")
    
    # 8 parallel workers for hyper-speed
    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(translate_markdown_file, all_files)
        
    print("ALL TRANSLATIONS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
