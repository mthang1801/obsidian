# 🤖 Agentic AI & Prompt Engineering — Bảng Thuật ngữ Toàn diện

> ⭐ Mức độ phổ biến: ⭐ Hiếm gặp · ⭐⭐ Ít dùng · ⭐⭐⭐ Thỉnh thoảng · ⭐⭐⭐⭐ Phổ biến · ⭐⭐⭐⭐⭐ Rất phổ biến

---

## I. 🧠 Core AI / LLM Concepts

| #   | Thuật ngữ            | Định nghĩa                                                                                          | Mức độ phổ biến |
| --- | -------------------- | --------------------------------------------------------------------------------------------------- | --------------- |
| 1   | **LLM**              | Large Language Model — mô hình ngôn ngữ lớn (GPT, Claude, Gemini) được train trên massive text data | ⭐⭐⭐⭐⭐           |
| 2   | **Foundation Model** | Model gốc được pretrain trên dữ liệu khổng lồ, dùng làm base để fine-tune cho task cụ thể           | ⭐⭐⭐⭐            |
| 3   | **Inference**        | Quá trình chạy model để sinh output từ input — khác với training                                    | ⭐⭐⭐⭐⭐           |
| 4   | **Token**            | Đơn vị nhỏ nhất LLM xử lý — ~¾ từ tiếng Anh. Giới hạn context = giới hạn token                      | ⭐⭐⭐⭐⭐           |
| 5   | **Context Window**   | Số token tối đa model có thể "nhìn thấy" trong một lần inference — memory ngắn hạn của LLM          | ⭐⭐⭐⭐⭐           |
| 6   | **Temperature**      | Độ ngẫu nhiên của output — 0 = deterministic, 1+ = sáng tạo/unpredictable                           | ⭐⭐⭐⭐⭐           |
| 7   | **Top-P / Top-K**    | Chiến lược sampling — kiểm soát diversity của token được chọn khi generate                          | ⭐⭐⭐⭐            |
| 8   | **Hallucination**    | LLM tự tin đưa ra thông tin sai — nguy hiểm nhất trong agentic context khi model tự ra quyết định   | ⭐⭐⭐⭐⭐           |
| 9   | **Grounding**        | Kỹ thuật buộc LLM bám vào dữ liệu thực (retrieved docs, facts) thay vì hallucinate                  | ⭐⭐⭐⭐            |
| 10  | **Embedding**        | Vector biểu diễn semantic của text — dùng cho semantic search, RAG, clustering                      | ⭐⭐⭐⭐⭐           |
| 11  | **Fine-tuning**      | Train thêm model trên domain-specific data để specialize behavior                                   | ⭐⭐⭐⭐            |
| 12  | **RLHF**             | Reinforcement Learning from Human Feedback — cách align model với human preference                  | ⭐⭐⭐⭐            |

---

## II. ✍️ Prompt Engineering

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|13|**Prompt**|Input text gửi đến LLM để hướng dẫn output mong muốn|⭐⭐⭐⭐⭐|
|14|**System Prompt**|Instruction cố định đặt ở đầu conversation — định nghĩa persona, rules, constraints của model|⭐⭐⭐⭐⭐|
|15|**User Prompt**|Phần input từ người dùng thực tế — dynamic, thay đổi mỗi turn|⭐⭐⭐⭐⭐|
|16|**Zero-Shot Prompting**|Yêu cầu model làm task mà không cho ví dụ — chỉ dùng instruction|⭐⭐⭐⭐⭐|
|17|**Few-Shot Prompting**|Cung cấp 2–5 ví dụ input/output trong prompt để model học pattern|⭐⭐⭐⭐⭐|
|18|**One-Shot Prompting**|Variant của Few-Shot với đúng 1 ví dụ|⭐⭐⭐⭐|
|19|**Chain-of-Thought**|CoT — yêu cầu model "think step by step" trước khi trả lời — cải thiện reasoning đáng kể|⭐⭐⭐⭐⭐|
|20|**Zero-Shot CoT**|Thêm "Let's think step by step" vào prompt mà không cần ví dụ|⭐⭐⭐⭐|
|21|**Tree of Thought**|ToT — model explore nhiều reasoning path song song như cây, chọn path tốt nhất|⭐⭐⭐|
|22|**Self-Consistency**|Generate nhiều CoT answers, chọn câu trả lời xuất hiện nhiều nhất (majority vote)|⭐⭐⭐|
|23|**ReAct**|Reason + Act — model xen kẽ reasoning và action (tool call) trong cùng output|⭐⭐⭐⭐|
|24|**Prompt Injection**|Attack vector — inject malicious instruction vào input để override system prompt|⭐⭐⭐⭐|
|25|**Jailbreak**|Kỹ thuật bypass safety guardrails của LLM thông qua prompt manipulation|⭐⭐⭐⭐|
|26|**Role Prompting**|Gán persona cụ thể cho model: "You are a senior Go engineer..."|⭐⭐⭐⭐⭐|
|27|**Instruction Tuning**|Fine-tune model đặc biệt để follow instruction tốt hơn|⭐⭐⭐⭐|
|28|**Prompt Template**|Skeleton prompt với placeholder — parameterized, reusable across inputs|⭐⭐⭐⭐⭐|
|29|**Prompt Chaining**|Output của prompt này là input của prompt tiếp theo — build complex pipeline|⭐⭐⭐⭐|
|30|**Meta-Prompt**|Prompt dùng để generate prompt khác — model viết prompt cho chính nó|⭐⭐⭐|
|31|**Negative Prompting**|Chỉ rõ model không được làm gì — thường dùng kết hợp với positive instruction|⭐⭐⭐⭐|
|32|**Structured Output**|Yêu cầu model output theo format cố định: JSON, XML, YAML — dễ parse bằng code|⭐⭐⭐⭐⭐|
|33|**Constrained Decoding**|Enforce model chỉ output token hợp lệ theo grammar/schema — mạnh hơn structured output|⭐⭐⭐|

---

## III. 🤖 Agentic AI — Core Concepts

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|34|**AI Agent**|LLM có khả năng tự lên kế hoạch, sử dụng tools, và thực thi multi-step task với minimal human intervention|⭐⭐⭐⭐⭐|
|35|**Agentic Loop**|Vòng lặp cốt lõi: Observe → Think → Act → Observe... — agent tự lặp đến khi hoàn thành task|⭐⭐⭐⭐⭐|
|36|**ReAct Loop**|Cụ thể hóa Agentic Loop: Reason → Act → Observe → Reason...|⭐⭐⭐⭐|
|37|**Autonomy Level**|Mức độ tự chủ của agent — L1: suggest only, L2: act with confirm, L3: fully autonomous|⭐⭐⭐|
|38|**Agency**|Khả năng của agent tự ra quyết định và hành động trong môi trường|⭐⭐⭐⭐|
|39|**Goal-Directed Behavior**|Agent hành động hướng đến goal cụ thể, không chỉ respond to prompt|⭐⭐⭐⭐|
|40|**Task Decomposition**|Agent tự breakdown một task lớn thành sub-tasks nhỏ có thể thực thi được|⭐⭐⭐⭐⭐|
|41|**Planning**|Agent lập kế hoạch thực thi trước khi hành động — có thể replan khi gặp obstacle|⭐⭐⭐⭐⭐|
|42|**Self-Reflection**|Agent tự đánh giá output của mình và quyết định retry hay tiếp tục|⭐⭐⭐⭐|
|43|**Self-Critique**|Agent tự criticize reasoning của mình trước khi đưa ra final answer|⭐⭐⭐|
|44|**Human-in-the-Loop**|HITL — con người review/approve ở các checkpoint quan trọng trong agentic flow|⭐⭐⭐⭐⭐|
|45|**Interrupt / Escalation**|Agent dừng và chuyển control về human khi gặp tình huống ngoài khả năng hoặc high-stakes decision|⭐⭐⭐⭐|

---

## IV. 🛠️ Tools & Capabilities

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|46|**Tool Use / Function Calling**|LLM gọi external function (search, calculator, API) để lấy thông tin thực thay vì hallucinate|⭐⭐⭐⭐⭐|
|47|**Tool Schema**|Định nghĩa JSON mô tả function signature — name, description, parameters — để LLM biết cách gọi|⭐⭐⭐⭐⭐|
|48|**Tool Registry**|Danh sách tất cả tools agent có thể sử dụng — agent query registry để chọn tool phù hợp|⭐⭐⭐⭐|
|49|**Code Interpreter**|Tool cho phép agent viết và thực thi code thực tế (Python sandbox) — giải toán, xử lý data|⭐⭐⭐⭐⭐|
|50|**Web Search Tool**|Agent tự search internet để lấy thông tin real-time vượt knowledge cutoff|⭐⭐⭐⭐⭐|
|51|**Browser Use**|Agent điều khiển browser thực — click, fill form, navigate — như Playwright nhưng AI-driven|⭐⭐⭐|
|52|**Computer Use**|Agent điều khiển cả desktop OS — mouse, keyboard, screenshot — Anthropic Claude Computer Use|⭐⭐⭐|
|53|**RAG**|Retrieval-Augmented Generation — retrieve relevant docs từ vector DB, inject vào context trước khi generate|⭐⭐⭐⭐⭐|
|54|**Vector Database**|DB lưu embeddings và hỗ trợ similarity search — Pinecone, Weaviate, pgvector, Qdrant|⭐⭐⭐⭐⭐|
|55|**Semantic Search**|Tìm kiếm theo nghĩa thay vì exact keyword — dùng embedding similarity|⭐⭐⭐⭐⭐|
|56|**Hybrid Search**|Kết hợp semantic search (embedding) và keyword search (BM25) — tốt hơn cả hai riêng lẻ|⭐⭐⭐⭐|

---

## V. 🏗️ Scaffolding & Harness

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|57|**Scaffolding**|Cấu trúc framework bao quanh LLM — quản lý prompt, memory, tool routing, retry, logging. Agent không thể hoạt động thiếu scaffolding|⭐⭐⭐⭐|
|58|**Harness**|Test harness — infrastructure để chạy agent trong controlled environment, capture input/output, assert behavior|⭐⭐⭐|
|59|**Agent Runtime**|Môi trường thực thi agent — quản lý lifecycle, resource, concurrency của nhiều agent|⭐⭐⭐⭐|
|60|**Agent Sandbox**|Môi trường isolated để agent thực thi code/action mà không ảnh hưởng production system|⭐⭐⭐⭐|
|61|**Execution Environment**|Nơi agent thực sự chạy — local, cloud function, container — với permissions được kiểm soát|⭐⭐⭐⭐|
|62|**Agent Shell**|Thin wrapper CLI/API quanh agent để dễ invoke và integrate vào CI/CD hay other tooling|⭐⭐⭐|

---

## VI. 🔄 Workflow & Orchestration

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|63|**AI Orchestrator**|Component điều phối nhiều AI agents/models làm việc cùng nhau — phân công, route, aggregate results|⭐⭐⭐⭐⭐|
|64|**Workflow**|Chuỗi steps có định nghĩa rõ ràng mà agent/pipeline thực thi — có thể linear, branching, hoặc parallel|⭐⭐⭐⭐⭐|
|65|**DAG**|Directed Acyclic Graph — cấu trúc workflow phổ biến, các node là tasks, edges là dependencies|⭐⭐⭐⭐|
|66|**Pipeline**|Chuỗi processing steps tuyến tính — input → transform → transform → output|⭐⭐⭐⭐⭐|
|67|**Step / Node**|Đơn vị nhỏ nhất trong workflow — một LLM call, một tool call, hoặc một transformation|⭐⭐⭐⭐⭐|
|68|**Parallel Execution**|Chạy nhiều steps đồng thời — fan-out tasks để giảm latency tổng thể|⭐⭐⭐⭐|
|69|**Conditional Branching**|Workflow rẽ nhánh dựa trên output của step trước — if/else trong AI pipeline|⭐⭐⭐⭐|
|70|**Retry Policy**|Số lần retry và strategy (immediate, backoff) khi một step fail|⭐⭐⭐⭐|
|71|**Checkpoint**|Lưu intermediate state của workflow — resume từ checkpoint nếu crash thay vì chạy lại từ đầu|⭐⭐⭐⭐|
|72|**Event-Driven Agent**|Agent kích hoạt bởi events (webhook, message queue) thay vì polling hoặc user input|⭐⭐⭐⭐|
|73|**Trigger**|Sự kiện khởi động workflow — schedule (cron), webhook, message, file change|⭐⭐⭐⭐⭐|
|74|**Handoff**|Chuyển giao control giữa agents — Agent A hoàn thành, pass context sang Agent B|⭐⭐⭐⭐|

---

## VII. 🪝 Hooks & Middleware

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|75|**Hook**|Điểm chèn code vào lifecycle của agent/LLM call — before/after prompt, before/after tool call|⭐⭐⭐⭐|
|76|**Pre-hook**|Chạy trước một action — validate input, transform prompt, inject context, rate limit check|⭐⭐⭐⭐|
|77|**Post-hook**|Chạy sau một action — log output, validate response, format, trigger side effects|⭐⭐⭐⭐|
|78|**Middleware**|Layer xử lý nằm giữa caller và LLM — auth, logging, caching, content filtering, cost tracking|⭐⭐⭐⭐⭐|
|79|**Interceptor**|Bắt và xử lý LLM request/response — có thể modify, block, hoặc redirect|⭐⭐⭐⭐|
|80|**Callback**|Function được gọi khi agent đạt đến lifecycle event nhất định — on_tool_start, on_agent_finish|⭐⭐⭐⭐|
|81|**Event Listener**|Subscribe vào agent events để observe, log, hay react — pattern phổ biến trong LangChain|⭐⭐⭐⭐|
|82|**Guardrail**|Kiểm tra output của LLM trước khi trả về user — content safety, format validation, PII detection|⭐⭐⭐⭐⭐|
|83|**Output Parser**|Transform raw LLM output thành structured data — parse JSON, extract fields, validate schema|⭐⭐⭐⭐⭐|
|84|**Input Guard**|Validate và sanitize input trước khi gửi đến LLM — prevent injection, enforce constraints|⭐⭐⭐⭐|

---

## VIII. 🧩 Multi-Agent Systems

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|85|**Multi-Agent System**|MAS — nhiều agents cộng tác để giải quyết task phức tạp hơn khả năng của một agent|⭐⭐⭐⭐⭐|
|86|**Agent Role**|Vai trò chuyên biệt của từng agent trong system: Planner, Executor, Critic, Researcher...|⭐⭐⭐⭐⭐|
|87|**Supervisor Agent**|Agent cấp cao điều phối các sub-agents — assign tasks, monitor, aggregate results|⭐⭐⭐⭐|
|88|**Sub-Agent / Worker Agent**|Agent thực thi task cụ thể được giao bởi Supervisor|⭐⭐⭐⭐|
|89|**Critic Agent**|Agent chuyên review và critique output của agent khác — giảm hallucination|⭐⭐⭐⭐|
|90|**Debate Pattern**|Nhiều agents tranh luận về một vấn đề, Critic/Judge agent chọn answer tốt nhất|⭐⭐⭐|
|91|**Swarm Intelligence**|Nhiều simple agents hoạt động song song, hành vi complex emerge từ interaction — không có central control|⭐⭐⭐|
|92|**Agent Communication Protocol**|Chuẩn message format giữa agents — thường là JSON với role/content/metadata|⭐⭐⭐⭐|
|93|**Shared Memory**|State/context được chia sẻ giữa nhiều agents trong cùng system|⭐⭐⭐⭐|
|94|**Agent Registry**|Catalogue của các available agents — orchestrator query để biết agent nào có capability nào|⭐⭐⭐⭐|

---

## IX. 💾 Memory Systems

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|95|**Short-Term Memory**|Context window hiện tại — mất khi conversation kết thúc|⭐⭐⭐⭐⭐|
|96|**Long-Term Memory**|Persistent storage bên ngoài context — vector DB, database — agent retrieve khi cần|⭐⭐⭐⭐⭐|
|97|**Episodic Memory**|Lưu trữ các "episodes" — past conversations, task histories — để agent học từ kinh nghiệm|⭐⭐⭐|
|98|**Semantic Memory**|Knowledge base về facts, concepts — agent retrieve để augment reasoning|⭐⭐⭐⭐|
|99|**Working Memory**|Subset của context window đang được "chú ý" — agent scratchpad trong khi reasoning|⭐⭐⭐|
|100|**Memory Compression**|Summarize conversation history khi gần đầy context — giữ gist, bỏ detail|⭐⭐⭐⭐|
|101|**Memory Retrieval**|Query long-term memory bằng semantic search để inject relevant context vào prompt|⭐⭐⭐⭐|
|102|**External Memory**|Bất kỳ storage nào bên ngoài model — files, DB, vector store — agent read/write|⭐⭐⭐⭐|

---

## X. 📐 Skills & Capabilities

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|103|**Skill**|Một capability đóng gói sẵn mà agent có thể invoke — send email, query DB, generate image|⭐⭐⭐⭐|
|104|**Skill Library**|Tập hợp skills có thể tái sử dụng — agent chọn skill phù hợp cho sub-task|⭐⭐⭐⭐|
|105|**Capability Discovery**|Agent tự khám phá capabilities available trong environment — query tool registry|⭐⭐⭐|
|106|**Composable Skills**|Skills có thể kết hợp thành complex capabilities — như Lego blocks|⭐⭐⭐|
|107|**Atomic Action**|Action nhỏ nhất không thể chia nhỏ hơn — building block của skills|⭐⭐⭐|
|108|**Skill Routing**|Quyết định skill nào phù hợp với request — dựa trên intent classification|⭐⭐⭐⭐|
|109|**Plugin**|Skill được package và distribute — OpenAI Plugin, MCP Server là examples|⭐⭐⭐⭐⭐|
|110|**MCP**|Model Context Protocol — chuẩn giao thức của Anthropic để connect LLM với external tools/data sources|⭐⭐⭐⭐⭐|

---

## XI. 🧪 Evaluation & Observability

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|111|**Evals**|Evaluation framework — tập test cases để đo chất lượng LLM/agent output tự động|⭐⭐⭐⭐⭐|
|112|**LLM-as-Judge**|Dùng một LLM để đánh giá output của LLM khác — scalable nhưng cần calibrate|⭐⭐⭐⭐|
|113|**Benchmark**|Tập dataset chuẩn để so sánh performance giữa models/agents — MMLU, HumanEval...|⭐⭐⭐⭐⭐|
|114|**Trace**|Record đầy đủ mọi LLM call, tool call, decision trong một agentic run — debug, audit|⭐⭐⭐⭐⭐|
|115|**Span**|Một bước trong agent trace — LLM call, tool call, hay retrieval đều là một span|⭐⭐⭐⭐|
|116|**Prompt Versioning**|Quản lý version của prompts như code — track changes, rollback, A/B test|⭐⭐⭐⭐|
|117|**Latency Budget**|Thời gian tối đa cho phép cho toàn bộ agentic pipeline — phân bổ cho từng step|⭐⭐⭐⭐|
|118|**Token Budget**|Giới hạn token cho một run — kiểm soát cost, tránh infinite loop|⭐⭐⭐⭐|
|119|**LLM Observability**|Logging + tracing + monitoring chuyên cho LLM — tools: LangSmith, Langfuse, Helicone|⭐⭐⭐⭐⭐|
|120|**Regression Testing for AI**|Đảm bảo prompt/model update không làm worse các cases đã pass trước đó|⭐⭐⭐⭐|

---

## XII. 🔐 Safety & Alignment

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|121|**Alignment**|Đảm bảo AI hành động đúng với human values và intentions — bài toán trung tâm của AI safety|⭐⭐⭐⭐⭐|
|122|**Constitutional AI**|Kỹ thuật của Anthropic — define principles (constitution), model tự critique và revise output theo principles|⭐⭐⭐⭐|
|123|**Red Teaming**|Cố ý tấn công/jailbreak AI system để tìm vulnerability trước khi ship|⭐⭐⭐⭐⭐|
|124|**Safety Layer**|Layer kiểm tra content trước/sau LLM — block harmful content, PII, sensitive data|⭐⭐⭐⭐⭐|
|125|**PII Detection**|Phát hiện Personally Identifiable Information trong input/output — mask hoặc block trước khi log|⭐⭐⭐⭐|
|126|**Sandboxing**|Chạy agent action trong isolated environment — giới hạn blast radius nếu agent làm sai|⭐⭐⭐⭐⭐|
|127|**Permission Scoping**|Agent chỉ được cấp đúng permissions cần thiết — principle of least privilege cho AI|⭐⭐⭐⭐|
|128|**Audit Log**|Ghi lại mọi action agent thực hiện với timestamp — accountability, forensics|⭐⭐⭐⭐⭐|

---

---

# 📄 AI Template Engineering — Bảng Thuật ngữ Toàn diện

---

## I. 🧱 Core Template Concepts

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|1|**Prompt Template**|Skeleton prompt với placeholder {variable} — parameterized, reusable, version-controlled như code|⭐⭐⭐⭐⭐|
|2|**Template Variable**|Placeholder được inject vào template lúc runtime — {user_name}, {context}, {task}|⭐⭐⭐⭐⭐|
|3|**Template Rendering**|Quá trình điền variables vào template để tạo ra final prompt gửi đến LLM|⭐⭐⭐⭐⭐|
|4|**Template Engine**|Component chịu trách nhiệm render template — Jinja2, Handlebars, f-string, Mustache|⭐⭐⭐⭐⭐|
|5|**Template Registry**|Kho lưu trữ và quản lý tất cả templates — có thể query theo name, tag, version|⭐⭐⭐⭐|
|6|**Template Inheritance**|Template con kế thừa và override một phần của template cha — giảm duplication|⭐⭐⭐|
|7|**Template Composition**|Lắp ghép nhiều template nhỏ thành một template lớn — partial templates, blocks|⭐⭐⭐⭐|
|8|**Partial Template**|Template con có thể được nhúng vào nhiều template khác — reusable fragment|⭐⭐⭐⭐|
|9|**Base Template**|Template gốc định nghĩa structure chung — các template khác extend và fill slots|⭐⭐⭐⭐|
|10|**Template Schema**|Định nghĩa formal về variables cần thiết, type, required/optional của một template|⭐⭐⭐⭐|

---

## II. 🏗️ Template Architecture & Design

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|11|**System Prompt Template**|Template cho phần system instruction — persona, rules, constraints được parameterize|⭐⭐⭐⭐⭐|
|12|**User Prompt Template**|Template cho phần user message — task description, input data được inject|⭐⭐⭐⭐⭐|
|13|**Few-Shot Template**|Template bao gồm cả phần examples — số lượng và nội dung examples có thể dynamic|⭐⭐⭐⭐|
|14|**Chat Template**|Template cấu trúc toàn bộ conversation — system + user + assistant turns theo format của model|⭐⭐⭐⭐⭐|
|15|**Instruction Template**|Template focus vào hướng dẫn task — "Given {input}, do {action} and return {output_format}"|⭐⭐⭐⭐⭐|
|16|**Context Template**|Template inject background knowledge — retrieved docs, user profile, session history|⭐⭐⭐⭐|
|17|**Output Template**|Template định nghĩa shape của output mong muốn — JSON schema, XML structure, markdown format|⭐⭐⭐⭐⭐|
|18|**Multi-Turn Template**|Template quản lý conversation history nhiều lượt — handle memory, summarization|⭐⭐⭐⭐|
|19|**Conditional Template**|Template có logic rẽ nhánh — render section A hay B tùy theo điều kiện|⭐⭐⭐⭐|
|20|**Dynamic Template**|Template được generate ở runtime dựa trên context — không hardcode cấu trúc|⭐⭐⭐⭐|

---

## III. 🔄 Template Patterns

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|21|**Role-Task-Format Pattern**|Cấu trúc 3 phần: "You are {role}. Your task is {task}. Return {format}" — baseline pattern hiệu quả nhất|⭐⭐⭐⭐⭐|
|22|**RTF Pattern**|Viết tắt của Role-Task-Format — template pattern phổ biến nhất trong production|⭐⭐⭐⭐⭐|
|23|**CRISPE Pattern**|Capacity, Role, Insight, Statement, Personality, Experiment — template framework cho complex prompts|⭐⭐⭐|
|24|**RISEN Pattern**|Role, Instructions, Steps, End goal, Narrowing — structured template cho step-by-step tasks|⭐⭐⭐|
|25|**APE Pattern**|Action, Purpose, Expectation — template ngắn gọn cho task-oriented prompts|⭐⭐⭐|
|26|**COAST Pattern**|Context, Objective, Action, Scenario, Task — template cho complex business scenarios|⭐⭐|
|27|**Chain Template**|Output của template này là input của template tiếp theo — build pipeline bằng template chaining|⭐⭐⭐⭐|
|28|**Guard Template**|Template chuyên để validate/filter — wrap quanh main template để add safety layer|⭐⭐⭐⭐|
|29|**Retry Template**|Template được modify tự động khi LLM fail — thêm clarification, thay đổi phrasing|⭐⭐⭐|
|30|**Fallback Template**|Template dự phòng khi main template không cho kết quả đủ tốt — simpler, more explicit|⭐⭐⭐|

---

## IV. 📐 Template Formatting & Structure

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|31|**Delimiter**|Ký tự phân tách sections trong prompt — ###, ---, `<tag>`, triple backtick — tránh ambiguity|⭐⭐⭐⭐⭐|
|32|**XML Tags in Prompt**|Dùng `<context>`, `<task>`, `<example>` để structure prompt — Claude đặc biệt nhạy với format này|⭐⭐⭐⭐⭐|
|33|**Markdown in Prompt**|Dùng `##`, `**bold**`, `- bullet` trong prompt để tạo visual hierarchy cho LLM|⭐⭐⭐⭐|
|34|**Slot**|Vị trí cụ thể trong template chờ được điền — tường minh hơn variable, thường có type hint|⭐⭐⭐⭐|
|35|**Anchor Text**|Đoạn text cố định trong template làm điểm tham chiếu — không thay đổi dù variable thay đổi|⭐⭐⭐|
|36|**Section Header**|Tiêu đề phân chia các phần của prompt — `## Instructions`, `## Context`, `## Output Format`|⭐⭐⭐⭐⭐|
|37|**Negative Space**|Khoảng trống, newline trong template — ảnh hưởng đến cách LLM parse và weight các sections|⭐⭐⭐|
|38|**Token Efficiency**|Tối ưu template để dùng ít token nhất có thể mà không mất thông tin — ảnh hưởng trực tiếp cost|⭐⭐⭐⭐⭐|

---

## V. 🗂️ Template Management

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|39|**Prompt Versioning**|Quản lý version của template như code — git-tracked, semantic versioning, changelog|⭐⭐⭐⭐⭐|
|40|**Template Store**|Database/repository lưu trữ templates — có thể là file system, DB, hoặc dedicated service|⭐⭐⭐⭐|
|41|**Template Tagging**|Gắn tags cho template — theo model, language, domain, task-type — để filter và discover|⭐⭐⭐⭐|
|42|**Template Deprecation**|Đánh dấu template cũ không còn dùng — có migration path sang template mới|⭐⭐⭐|
|43|**Template Diff**|So sánh hai version của template để hiểu thay đổi ảnh hưởng như thế nào đến output|⭐⭐⭐⭐|
|44|**Template Linting**|Kiểm tra template có đúng format, không thiếu variable, không có syntax lỗi — automated|⭐⭐⭐|
|45|**Template Testing**|Chạy template với test inputs để verify output đạt expectation trước khi promote to production|⭐⭐⭐⭐⭐|
|46|**Template A/B Testing**|Chạy song song hai variants của template với real traffic để chọn cái tốt hơn|⭐⭐⭐⭐|
|47|**Template Promotion**|Quy trình đưa template từ dev → staging → production — có approval, rollback plan|⭐⭐⭐⭐|
|48|**Hot Reload**|Cập nhật template ở runtime mà không cần restart service — thay đổi prompt không cần redeploy|⭐⭐⭐⭐|

---

## VI. 🔧 Template Engineering Practices

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|49|**Prompt Hardening**|Quá trình làm template robust hơn — thêm edge case handling, negative constraints, format enforcement|⭐⭐⭐⭐|
|50|**Context Stuffing**|Nhồi quá nhiều context vào template → LLM bị overwhelmed, attention bị diluted — anti-pattern|⭐⭐⭐⭐|
|51|**Context Pruning**|Loại bỏ thông tin không liên quan khỏi context trước khi inject vào template — giữ signal, bỏ noise|⭐⭐⭐⭐|
|52|**Prompt Compression**|Rút gọn template/context bằng summarization hoặc selective extraction — giảm token, giữ meaning|⭐⭐⭐⭐|
|53|**Instruction Clarity**|Nguyên tắc: instruction trong template phải đủ rõ để một người mới cũng hiểu — không dựa vào implicit assumption|⭐⭐⭐⭐⭐|
|54|**Specificity vs Generality**|Trade-off: template quá specific → rigid, quá general → inconsistent output — cần calibrate|⭐⭐⭐⭐|
|55|**Prompt Drift**|Template dần trở nên inconsistent với model mới hoặc use case mới — cần audit định kỳ|⭐⭐⭐⭐|
|56|**Template Bloat**|Template phình to theo thời gian vì thêm edge cases — làm giảm clarity và tăng cost|⭐⭐⭐|
|57|**DRY Prompting**|Không lặp instruction trong cùng một template — LLM không "học" từ repetition, chỉ tốn token|⭐⭐⭐⭐|
|58|**Prompt Sensitivity**|Mức độ output thay đổi khi template thay đổi nhỏ — model khác nhau có sensitivity khác nhau|⭐⭐⭐⭐|

---

## VII. 🤖 Agentic Template Patterns

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|59|**Agent System Prompt Template**|Template định nghĩa toàn bộ persona, capabilities, constraints của agent — core identity|⭐⭐⭐⭐⭐|
|60|**Tool Description Template**|Template mô tả một tool cho LLM — name, description, parameters, examples — ảnh hưởng lớn đến tool selection accuracy|⭐⭐⭐⭐⭐|
|61|**Planner Template**|Template cho planning step — "Given {goal}, break down into {n} subtasks with dependencies"|⭐⭐⭐⭐|
|62|**Executor Template**|Template cho execution step — "Given {subtask} and {context}, perform action and return {result}"|⭐⭐⭐⭐|
|63|**Critic Template**|Template cho review step — "Given {output}, evaluate against {criteria} and suggest improvements"|⭐⭐⭐⭐|
|64|**Summarizer Template**|Template compress conversation/result — dùng để update memory hoặc create handoff context|⭐⭐⭐⭐|
|65|**Router Template**|Template phân loại intent và quyết định agent/tool nào handle — "Given {input}, classify into {categories}"|⭐⭐⭐⭐⭐|
|66|**Reflector Template**|Template cho self-reflection — agent đánh giá chính output của mình trước khi finalize|⭐⭐⭐|
|67|**Handoff Template**|Template tạo context package khi chuyển giao giữa agents — đảm bảo không mất thông tin|⭐⭐⭐⭐|
|68|**Error Recovery Template**|Template kích hoạt khi step fail — diagnose lỗi, quyết định retry hay escalate|⭐⭐⭐⭐|

---

## VIII. 📊 RAG & Knowledge Templates

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|69|**RAG Template**|Template thiết kế cho Retrieval-Augmented Generation — có slots cho retrieved chunks, source attribution|⭐⭐⭐⭐⭐|
|70|**Retrieval Query Template**|Template transform user question thành optimal search query — khác với final answer prompt|⭐⭐⭐⭐|
|71|**Document Template**|Template format retrieved documents trước khi inject — add metadata, source, relevance score|⭐⭐⭐⭐|
|72|**Citation Template**|Template yêu cầu LLM cite source khi trả lời — "Answer based on {docs}. Cite [source] for each claim"|⭐⭐⭐⭐|
|73|**Grounding Template**|Template enforce LLM bám vào provided context — "Answer ONLY based on the following information"|⭐⭐⭐⭐⭐|
|74|**Hypothetical Document Embedding**|HyDE — generate hypothetical answer trước, dùng embedding của answer đó để search — template trick|⭐⭐⭐|
|75|**Query Expansion Template**|Template rewrite query theo nhiều cách khác nhau để cover nhiều semantic angles khi search|⭐⭐⭐⭐|
|76|**Reranking Template**|Template cho LLM đánh giá và rerank retrieved documents theo relevance trước khi use|⭐⭐⭐⭐|

---

## IX. 🌍 Localization & Persona Templates

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|77|**Persona Template**|Template định nghĩa character của LLM — tone, style, expertise level, communication style|⭐⭐⭐⭐⭐|
|78|**Tone Template**|Template điều chỉnh giọng điệu — formal, casual, empathetic, technical — inject vào system prompt|⭐⭐⭐⭐⭐|
|79|**Locale Template**|Template adapt output theo ngôn ngữ và văn hóa — date format, currency, unit, idioms|⭐⭐⭐⭐|
|80|**Audience Template**|Template calibrate độ phức tạp theo audience — expert vs beginner vs non-technical|⭐⭐⭐⭐|
|81|**Domain Template**|Template inject domain-specific vocabulary, rules, constraints — fintech, medical, legal|⭐⭐⭐⭐⭐|
|82|**Style Guide Template**|Template enforce writing style — brand voice, terminology list, forbidden words|⭐⭐⭐⭐|

---

## X. 🧪 Evaluation Templates

|#|Thuật ngữ|Định nghĩa|Mức độ phổ biến|
|---|---|---|---|
|83|**Eval Template**|Template dùng để đánh giá output của template khác — LLM-as-judge pattern|⭐⭐⭐⭐⭐|
|84|**Scoring Rubric Template**|Template định nghĩa tiêu chí chấm điểm — clarity, accuracy, completeness, format compliance|⭐⭐⭐⭐|
|85|**Red Team Template**|Template cố tình tạo adversarial inputs để test robustness của main template|⭐⭐⭐⭐|
|86|**Golden Dataset Template**|Template format cặp (input, expected output) để build test suite — ground truth|⭐⭐⭐⭐|
|87|**Regression Template**|Template so sánh output mới vs output cũ — phát hiện prompt drift sau khi update|⭐⭐⭐⭐|
|88|**Ablation Template**|Template loại bỏ từng phần để đo contribution của mỗi phần đến quality của output|⭐⭐⭐|

---

## 🗂️ Cấu trúc Tổng thể

```
Agentic AI & LLM Engineering
├── I.    Core LLM Concepts          (#1–12)
├── II.   Prompt Engineering         (#13–33)
├── III.  Agentic Core               (#34–45)
├── IV.   Tools & Capabilities       (#46–56)
├── V.    Scaffolding & Harness      (#57–62)
├── VI.   Workflow & Orchestration   (#63–74)
├── VII.  Hooks & Middleware         (#75–84)
├── VIII. Multi-Agent Systems        (#85–94)
├── IX.   Memory Systems             (#95–102)
├── X.    Skills & Plugins           (#103–110)
├── XI.   Evaluation & Observability (#111–120)
└── XII.  Safety & Alignment         (#121–128)

AI Template Engineering
├── I.    Core Template Concepts         (#1–10)
├── II.   Template Architecture          (#11–20)
├── III.  Template Patterns              (#21–30)
├── IV.   Formatting & Structure         (#31–38)
├── V.    Template Management            (#39–48)
├── VI.   Engineering Practices          (#49–58)
├── VII.  Agentic Template Patterns      (#59–68)
├── VIII. RAG & Knowledge Templates      (#69–76)
├── IX.   Localization & Persona         (#77–82)
└── X.    Evaluation Templates           (#83–88)
```

---

> 💡 **Learning path gợi ý:** Scaffolding → Agentic Loop → Tool Use → RAG → Memory Systems → Multi-Agent → Template Patterns → Agentic Templates