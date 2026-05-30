<!-- tags: glossary, reference, agentic-ai, core-llm, overview -->
# Core LLM Concepts

> The foundational mechanics of large language models — how they generate text, what constrains them, and where their behavior becomes unpredictable.

| Aspect | Detail |
| --- | --- |
| **Concept** | A cluster of terms explaining how LLMs work at the inference level — tokens, context, sampling, and training techniques. |
| **Audience** | AI engineer, backend developer integrating LLMs, tech lead evaluating model capabilities |
| **Primary style** | Glossary hub router |
| **Entry point** | Start here when the team cannot agree on what the model can and cannot do, or when a production issue traces back to model mechanics. |

📅 Created: 2026-04-28 · 🔄 Updated: 2026-04-28 · ⏱️ 8 min read

---

## 1. DEFINE

A developer ships a feature that calls an LLM. It works in testing but fails unpredictably in production — sometimes the response is too long, sometimes it invents facts, sometimes the same input produces wildly different outputs. The team starts debugging the prompt, but the real issue is that nobody on the team understands what a context window is, how temperature affects sampling, or why the model hallucinates. These are not prompt problems. They are mechanics problems.

**Core LLM Concepts** covers the fundamental machinery of large language models: what they process (tokens), how much they can see (context window), how they choose outputs (temperature, top-p/top-k), where they fail (hallucination), how to anchor them (grounding, embeddings), and how to customize them (fine-tuning, RLHF).

| Variant | Description |
| --- | --- |
| Model architecture | What LLMs are and how they were trained — foundation models, inference, tokens. |
| Output control | Knobs that shape generation — temperature, top-p, top-k. |
| Failure & mitigation | Where models break and how to fix it — hallucination, grounding, embeddings. |
| Customization | How to specialize a model — fine-tuning, RLHF. |

Core insight:

> Every problem in the agentic stack ultimately bottlenecks on a core LLM mechanic. Understanding these mechanics is not optional — it is the floor.

### Coverage Map

| Entry | Role | Note |
| --- | --- | --- |
| [LLM](01-llm.md) | Term | Large Language Model — the base entity |
| [Foundation Model](02-foundation-model.md) | Term | Pretrained base for specialization |
| [Inference](03-inference.md) | Term | Running the model to produce output |
| [Token](04-token.md) | Term | The atomic unit LLMs process |
| [Context Window](05-context-window.md) | Term | How much the model can see at once |
| [Temperature](06-temperature.md) | Term | Randomness control knob |
| [Top-P / Top-K](07-top-p-top-k.md) | Term | Sampling strategies |
| [Hallucination](08-hallucination.md) | Term | Confident falsehoods |
| [Grounding](09-grounding.md) | Term | Anchoring output to facts |
| [Embedding](10-embedding.md) | Term | Semantic vector representations |
| [Fine-tuning](11-fine-tuning.md) | Term | Domain specialization |
| [RLHF](12-rlhf.md) | Term | Human feedback alignment |

---

## 2. CONTEXT

**Who uses it**: AI engineers choosing models, backend developers debugging LLM behavior, tech leads estimating capability boundaries.

**When**: Before any prompt engineering, agent design, or architecture decision — these mechanics constrain everything above them.

**In this ecosystem**:
- Master these terms before moving to [Prompt Engineering](../prompt-engineering/README.md).
- Revisit when debugging unexpected agent behavior in [Agentic Core](../agentic-core/README.md).
- These terms reappear in [Evaluation & Observability](../evaluation-observability/README.md) when measuring model performance.

---

## 3. EXAMPLES

### Example 1: Basic — Know which knob to turn

```yaml
llm_debugging_router:
  - symptom: "Output is too creative / random"
    check: Temperature, Top-P/Top-K
  - symptom: "Response got cut off mid-sentence"
    check: Token, Context Window
  - symptom: "Model says things that are not true"
    check: Hallucination, Grounding
  - symptom: "Model does not know our domain"
    check: Fine-tuning, RAG, Embedding
```

**Conclusion**: Most LLM production issues trace back to one of these twelve mechanics. Knowing which one saves hours of prompt debugging.

---

## 4. COMPARE

| | Core LLM Concepts | Prompt Engineering |
|--|---|---|
| **Scope** | Model mechanics — what the model can do | Input design — how to make the model do it |
| **Control** | Model selection, parameters, training | Prompt text, examples, structure |
| **When to focus** | When the model itself is the bottleneck | When the model is capable but underperforming |

---

## 5. REF

| Resource | Type | Link | Note |
| --- | --- | --- | --- |
| OpenAI — Models documentation | Official | https://platform.openai.com/docs/models | Model capabilities and limits |
| Anthropic — Model card | Official | https://docs.anthropic.com/en/docs/about-claude/models | Claude model specifications |
| Google — Gemini documentation | Official | https://ai.google.dev/gemini-api/docs | Gemini model details |

---

## 6. RECOMMEND

| Explore next | When | Why | File/Link |
| --- | --- | --- | --- |
| LLM | You need to understand what a large language model actually is | Everything else in this cluster assumes this baseline | [LLM](./01-llm.md) |
| Hallucination | The model is producing incorrect information | This is the most dangerous failure mode in production | [Hallucination](./08-hallucination.md) |
| Prompt Engineering | You understand the mechanics and want better outputs | Prompt craft is the next layer up | [Prompt Engineering](../prompt-engineering/README.md) |

**Links**: [← Previous](../README.md) · [→ Next](./01-llm.md)
