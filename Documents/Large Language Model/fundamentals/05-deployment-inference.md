<!-- tags: llm, deployment, inference, quantization, ollama, vllm -->
# 🚀 LLM Deployment & Inference — Production-Ready AI

> Từ model weights đến production API — quantization, serving frameworks, cost optimization, và monitoring.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-03-27 · ⏱️ 18 phút đọc

| Aspect         | Detail                                                      |
| -------------- | ----------------------------------------------------------- |
| **Complexity** | ⭐⭐⭐⭐                                                      |
| **Use case**   | Self-hosted LLM, API gateway, edge inference                |
| **Keywords**   | Quantization, vLLM, Ollama, API Gateway, Cost Optimization  |

---

## 1. DEFINE

### Deployment Strategies

| Strategy         | Mô tả                          | Cost      | Latency | Control | Use case              |
| ---------------- | ------------------------------- | --------- | ------- | ------- | --------------------- |
| **API (Cloud)**  | OpenAI, Anthropic, Google APIs  | Pay/token | Low     | Low     | General purpose       |
| **Self-hosted**  | Chạy model trên own infra      | GPU rent  | Medium  | High    | Data privacy, custom  |
| **Edge/Local**   | Ollama, llama.cpp trên laptop  | Free      | Varies  | Full    | Dev/testing, offline  |
| **Serverless**   | Modal, Replicate, Together AI  | Pay/call  | Medium  | Medium  | Burst workloads       |

### Quantization — Giảm model size

| Method   | Bits  | Size Reduction | Quality Loss | GPU Memory (7B) | Speed   |
| -------- | ----- | -------------- | ------------ | ---------------- | ------- |
| **FP16** | 16    | 2×             | None         | ~14 GB           | Fast    |
| **INT8** | 8     | 4×             | Minimal      | ~7 GB            | Fast    |
| **INT4** | 4     | 8×             | Small        | ~4 GB            | Fastest |
| **GGUF Q4** | 4  | 8×             | Small        | ~4 GB (CPU!)     | Medium  |
| **AWQ**  | 4     | 8×             | Minimal      | ~4 GB            | Fast    |
| **GPTQ** | 4     | 8×             | Minimal      | ~4 GB            | Fast    |

Quantization đã cover. Nhưng serving cần framework selection — hãy chọn.

### Serving Frameworks

| Framework      | GPU  | CPU | Features                              | Best for              |
| -------------- | ---- | --- | ------------------------------------- | --------------------- |
| **vLLM**       | ✅   | ❌  | PagedAttention, continuous batching   | High-throughput GPU   |
| **Ollama**     | ✅   | ✅  | Simple CLI, auto quantization         | Local dev, prototyping |
| **llama.cpp**  | ✅   | ✅  | GGUF format, minimal deps             | Edge, embedded        |
| **TGI**        | ✅   | ❌  | HuggingFace native, production-ready  | HF ecosystem          |
| **SGLang**     | ✅   | ❌  | RadixAttention, structured gen        | Complex prompts       |

---

Các failure mode trên nghe quen. Nhưng có trap: quantization quá aggressive = quality degradation, và batch size sai = GPU utilization thấp. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

A production LLM system is not just a model — it is a layered stack where clients hit an API gateway, which routes queries to the optimal model based on complexity, while observability tracks every token and dollar spent.

![LLM Deployment Production Stack — Clients (Web/Mobile/Bot/API) → API Gateway (Rate Limiting, Auth, Load Balancing, Caching) → LLM Router (Simple→GPT-4o-mini, Complex→GPT-4o, Code→CodeLlama, Fallback→Ollama) → Observability (Metrics, Logging, Cost, Eval). Quantization chart: FP16 14GB → INT8 7GB → INT4 4GB](./images/05-deployment-production-stack.png)

*The model is one component. The production system includes routing, caching, monitoring, and cost optimization around it.*

### LLM Deployment Architecture

```text
┌───────────────────────────────────────────────────────────────┐
│                     Production LLM Stack                      │
│                                                               │
│  ┌─ Clients ──────────────────────────────────────────────┐   │
│  │  🌐 Web App    📱 Mobile    🤖 Bot    ⚡ Internal API  │   │
│  └────────────────────────┬───────────────────────────────┘   │
│                           ↓                                   │
│  ┌─ API Gateway ──────────────────────────────────────────┐   │
│  │  Rate Limiting │ Auth │ Load Balancing │ Caching       │   │
│  └────────────────────────┬───────────────────────────────┘   │
│                           ↓                                   │
│  ┌─ LLM Router ──────────────────────────────────────────┐   │
│  │                                                        │   │
│  │  Simple queries ──→ 🟢 Small Model (GPT-4o-mini)      │   │
│  │  Complex queries ──→ 🔴 Large Model (GPT-4o)          │   │
│  │  Code tasks ───────→ 🟡 Specialized (CodeLlama)       │   │
│  │  Fallback ─────────→ ⚪ Self-hosted (Ollama)           │   │
│  └────────────────────────┬───────────────────────────────┘   │
│                           ↓                                   │
│  ┌─ Observability ────────────────────────────────────────┐   │
│  │  📊 Metrics │ 📝 Logging │ 💰 Cost Tracking │ 🎯 Eval │   │
│  └────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

---

## 3. CODE

### 3.1 Ollama — Local LLM

```bash
# ━━━ ✅ Install & Run Ollama ━━━

# Install
curl -fsSL https://ollama.ai/install.sh | sh

# Pull models
ollama pull llama3.1:8b          # 4.7 GB
ollama pull llama3.1:70b-q4_0    # 40 GB (quantized)
ollama pull codellama:13b        # Code generation
ollama pull nomic-embed-text     # Embedding model

# Run interactive
ollama run llama3.1:8b

# List models
ollama list

# ━━━ ✅ API Usage (OpenAI-compatible!) ━━━
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:8b",
    "messages": [{"role": "user", "content": "Explain Docker in 3 sentences"}],
    "temperature": 0.7
  }'
```

```python
# ollama_client.py — Dùng Ollama với OpenAI SDK
from openai import OpenAI

# ✅ Ollama exposes OpenAI-compatible API
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # Required but unused
)

response = client.chat.completions.create(
    model="llama3.1:8b",
    messages=[
        {"role": "system", "content": "You are a Go expert."},
        {"role": "user", "content": "Explain goroutines vs threads"},
    ],
    temperature=0.7,
)
print(response.choices[0].message.content)

# ✅ Embeddings
embedding = client.embeddings.create(
    model="nomic-embed-text",
    input="Docker containerizes applications",
)
print(f"Embedding dimensions: {len(embedding.data[0].embedding)}")
```

### 3.2 vLLM — High-Performance Serving

```bash
# ━━━ ✅ Install & Run vLLM ━━━

pip install vllm

# Start OpenAI-compatible server
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --port 8000 \
    --tensor-parallel-size 1 \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.9

# With quantization (AWQ)
python -m vllm.entrypoints.openai.api_server \
    --model TheBloke/Llama-3.1-8B-Instruct-AWQ \
    --quantization awq \
    --port 8000
```

```python
# vllm_batch.py — Batch inference with vLLM
from vllm import LLM, SamplingParams

# ✅ Batch processing (much faster than sequential)
llm = LLM(
    model="meta-llama/Llama-3.1-8B-Instruct",
    tensor_parallel_size=1,
    gpu_memory_utilization=0.9,
)

sampling_params = SamplingParams(
    temperature=0.7,
    max_tokens=512,
    top_p=0.9,
)

# ✅ Process multiple prompts in one batch
prompts = [
    "Explain Docker in 3 sentences",
    "What is Kubernetes?",
    "Compare PostgreSQL vs MySQL",
    "How does Go garbage collection work?",
]

outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    print(f"Prompt: {output.prompt[:50]}...")
    print(f"Output: {output.outputs[0].text[:200]}")
    print("---")
```

### 3.3 LLM API Gateway (Go)

```go
// gateway.go — LLM API Gateway with routing, caching, rate limiting
package gateway

import (
    "context"
    "crypto/sha256"
    "encoding/hex"
    "encoding/json"
    "fmt"
    "log/slog"
    "net/http"
    "sync"
    "time"
)

type ModelConfig struct {
    Name     string  `json:"name"`
    Endpoint string  `json:"endpoint"`
    APIKey   string  `json:"api_key"`
    MaxRPS   int     `json:"max_rps"`
    CostPer1K float64 `json:"cost_per_1k_tokens"`
}

type Gateway struct {
    models   map[string]ModelConfig
    cache    sync.Map          // Simple in-memory cache
    metrics  *Metrics
}

type Metrics struct {
    mu            sync.Mutex
    TotalRequests int64
    TotalTokens   int64
    TotalCost     float64
    ByModel       map[string]int64
}

func NewGateway(models []ModelConfig) *Gateway {
    m := make(map[string]ModelConfig)
    for _, model := range models {
        m[model.Name] = model
    }
    return &Gateway{
        models:  m,
        metrics: &Metrics{ByModel: make(map[string]int64)},
    }
}

// Route selects the best model based on query complexity
func (g *Gateway) Route(prompt string) string {
    tokenCount := len(prompt) / 4 // rough estimate

    switch {
    case tokenCount < 100:
        return "gpt-4o-mini"    // Simple queries → cheap model
    case tokenCount < 1000:
        return "gpt-4o"         // Medium → standard model
    default:
        return "claude-3.5-sonnet" // Complex → best model
    }
}

// CacheKey generates a deterministic key for caching
func CacheKey(model, prompt string, temperature float64) string {
    h := sha256.Sum256([]byte(fmt.Sprintf("%s:%s:%.1f", model, prompt, temperature)))
    return hex.EncodeToString(h[:16])
}

// Chat handles a chat request with caching and metrics
func (g *Gateway) Chat(ctx context.Context, model, prompt string) (string, error) {
    // Check cache (only for temperature=0)
    cacheKey := CacheKey(model, prompt, 0)
    if cached, ok := g.cache.Load(cacheKey); ok {
        slog.Info("cache hit", "model", model)
        return cached.(string), nil
    }

    // Route to appropriate model
    if model == "" {
        model = g.Route(prompt)
    }

    config, ok := g.models[model]
    if !ok {
        return "", fmt.Errorf("unknown model: %s", model)
    }

    // Call LLM API
    start := time.Now()
    response, tokens, err := callLLMAPI(ctx, config, prompt)
    if err != nil {
        return "", fmt.Errorf("llm call: %w", err)
    }
    duration := time.Since(start)

    // Track metrics
    g.metrics.mu.Lock()
    g.metrics.TotalRequests++
    g.metrics.TotalTokens += int64(tokens)
    g.metrics.TotalCost += float64(tokens) / 1000 * config.CostPer1K
    g.metrics.ByModel[model]++
    g.metrics.mu.Unlock()

    slog.Info("llm response",
        "model", model,
        "tokens", tokens,
        "duration", duration,
        "cost", fmt.Sprintf("$%.6f", float64(tokens)/1000*config.CostPer1K),
    )

    // Cache response
    g.cache.Store(cacheKey, response)

    return response, nil
}

func callLLMAPI(ctx context.Context, config ModelConfig, prompt string) (string, int, error) {
    // Implementation similar to 01-llm-fundamentals LLM client
    // Returns: response text, total tokens, error
    return "", 0, nil // placeholder
}
```

### 3.4 Docker Compose — Self-Hosted Stack

```yaml
# docker-compose.yml — Complete self-hosted LLM stack
version: "3.9"

services:
  # ━━━ ✅ Ollama — LLM Server ━━━
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # ━━━ ✅ Open WebUI — Chat Interface ━━━
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    volumes:
      - webui_data:/app/backend/data
    depends_on:
      - ollama

  # ━━━ ✅ PostgreSQL + pgvector — Vector Store ━━━
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: rag_db
      POSTGRES_USER: ai
      POSTGRES_PASSWORD: ai_password
    ports:
      - "5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data

volumes:
  ollama_data:
  webui_data:
  pg_data:
```

### 3.5 Cost Optimization Strategies

```python
# cost_optimization.py — Các chiến lược giảm chi phí LLM

# ━━━ ✅ Strategy 1: Model routing ━━━
def smart_route(query: str, complexity_threshold: int = 50) -> str:
    """Route simple queries to cheaper models."""
    word_count = len(query.split())
    has_code = "```" in query or "def " in query or "func " in query

    if word_count < 20 and not has_code:
        return "gpt-4o-mini"       # $0.15/1M input
    elif has_code:
        return "gpt-4o"            # $2.50/1M input
    else:
        return "gpt-4o-mini"       # Default to cheap

# ━━━ ✅ Strategy 2: Prompt caching ━━━
# Anthropic: Automatic for repeated system prompts
# OpenAI: Cache common prefixes

CACHED_SYSTEM = """
You are a senior Go developer...
[Long system prompt - 2000 tokens]
"""
# First call: Full price
# Subsequent calls: 50% discount on cached prefix

# ━━━ ✅ Strategy 3: Batch API ━━━
# OpenAI Batch API: 50% discount, 24h turnaround
def batch_process(requests: list[dict]) -> str:
    """Use Batch API for non-urgent tasks."""
    batch_file = create_batch_file(requests)
    batch = client.batches.create(
        input_file_id=batch_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )
    return batch.id

# ━━━ ✅ Strategy 4: Response length control ━━━
#   max_tokens=100 thay vì default (4096)
#   Shorter system prompts
#   "Be concise. Max 3 sentences."

# ━━━ Cost comparison ━━━
MONTHLY_COST_ESTIMATE = """
10K requests/day × 30 days = 300K requests/month

| Model          | Avg tokens | Monthly cost |
|----------------|-----------|--------------|
| GPT-4o         | 1000      | $3,750       |
| GPT-4o-mini    | 1000      | $225         |
| Claude Haiku   | 1000      | $450         |
| Self-hosted 8B | 1000      | $300 (GPU)   |
| Ollama local   | 1000      | $0 (own HW)  |
"""
```

---

Bạn đã đi qua deployment & inference. Bây giờ đến phần nguy hiểm: over-quantization và batch inefficiency — trap đã được setup từ đầu bài.

## 4. PITFALLS

| # | Lỗi | Hậu quả | Fix |
| - | --- | ------- | --- |
| 1 | Không monitor token usage | Cost vượt budget | Track tokens/cost per request, set alerts |
| 2 | Không set max_tokens | Responses quá dài, cost cao | Luôn set max_tokens phù hợp task |
| 3 | Single model cho mọi task | Over-paying 10-50x | Model routing: simple→cheap, complex→powerful |
| 4 | Không cache responses | Redundant API calls | Cache deterministic queries (temp=0) |
| 5 | Self-host model quá lớn | OOM, slow, unstable | Quantize (INT4/AWQ) hoặc dùng model nhỏ hơn |
| 6 | Không có fallback | Service down = app down | Multi-provider fallback: OpenAI → Anthropic → local |
| 7 | Log chứa user data | Privacy/compliance violation | Redact PII trước khi log |

---

Bạn đã đi qua LLM Deployment và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource | Link |
| -------- | ---- |
| vLLM | [docs.vllm.ai](https://docs.vllm.ai/en/latest/) |
| Ollama | [ollama.com](https://ollama.com/) |
| llama.cpp | [github.com/ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp) |
| GGUF Format | [huggingface.co/docs/hub/gguf](https://huggingface.co/docs/hub/gguf) |
| LiteLLM (Gateway) | [github.com/BerriAI/litellm](https://github.com/BerriAI/litellm) |

---

## 6. RECOMMEND

| Mở rộng | Khi nào | Lý do |
| ------- | ------- | ----- |
| **LiteLLM** | Multi-provider routing | Unified API cho 100+ LLM providers |
| **Guardrails** | Safety-critical apps | Input/output validation |
| **LangFuse** | Observability | Trace, evaluate, monitor LLM apps |
| **Speculative Decoding** | Reduce latency | Draft model + verify = 2-3x speedup |
| **KV Cache Optimization** | Long conversations | Reduce memory usage cho multi-turn |

---

← Previous: [Fine-Tuning](./04-fine-tuning.md) · → Quay về [LLM Documentation](./README.md)
