<!-- tags: glossary, reference, agentic-ai, prompt-engineering, overview -->
# Prompt Engineering

> The discipline of designing LLM inputs to shape output — from basic instructions to sophisticated reasoning chains and attack-resistant patterns.

| Aspect | Detail |
| --- | --- |
| **Concept** | Techniques for crafting LLM inputs that reliably produce desired outputs. |
| **Audience** | AI engineer, prompt engineer, backend developer, product manager |
| **Primary style** | Glossary hub router |
| **Entry point** | Start here when the model is capable but the output quality is inconsistent or unpredictable. |

📅 Created: 2026-04-28 · 🔄 Updated: 2026-04-28 · ⏱️ 8 min read

---

## 1. DEFINE

The model can write code, analyze documents, and answer questions — but it keeps formatting the output wrong, missing edge cases, or ignoring constraints. The team tries adding more instructions. Sometimes it helps, sometimes it makes things worse. The real issue is that nobody on the team has a vocabulary for the different prompting techniques, when to use each one, and which ones compose well together.

**Prompt Engineering** covers the full spectrum of input design techniques — from basic prompts and role assignments to sophisticated chains of thought, adversarial defenses, and output constraint mechanisms.

| Variant | Description |
| --- | --- |
| Basic prompting | System prompts, user prompts, role prompting — the building blocks. |
| Reasoning techniques | Chain-of-thought, tree of thought, self-consistency — improving model reasoning. |
| Meta techniques | Prompt templates, chaining, meta-prompts — scaling prompt design. |
| Safety & control | Prompt injection defense, structured output, constrained decoding — hardening outputs. |

### Coverage Map

| Entry | Role | Note |
| --- | --- | --- |
| [Prompt](13-prompt.md) | Term | The basic input unit |
| [System Prompt](14-system-prompt.md) | Term | Fixed instruction header |
| [User Prompt](15-user-prompt.md) | Term | Dynamic user input |
| [Zero-Shot Prompting](16-zero-shot-prompting.md) | Term | Instruction without examples |
| [Few-Shot Prompting](17-few-shot-prompting.md) | Term | Learning from examples |
| [One-Shot Prompting](18-one-shot-prompting.md) | Term | Single example variant |
| [Chain-of-Thought](19-chain-of-thought.md) | Term | Step-by-step reasoning |
| [Zero-Shot CoT](20-zero-shot-cot.md) | Term | CoT without examples |
| [Tree of Thought](21-tree-of-thought.md) | Term | Parallel reasoning paths |
| [Self-Consistency](22-self-consistency.md) | Term | Majority vote over CoT |
| [ReAct](23-react.md) | Term | Reason + Act interleaving |
| [Prompt Injection](24-prompt-injection.md) | Term | Attack via input |
| [Jailbreak](25-jailbreak.md) | Term | Bypass safety guardrails |
| [Role Prompting](26-role-prompting.md) | Term | Persona assignment |
| [Instruction Tuning](27-instruction-tuning.md) | Term | Training to follow instructions |
| [Prompt Template](28-prompt-template.md) | Term | Parameterized prompt skeletons |
| [Prompt Chaining](29-prompt-chaining.md) | Term | Sequential prompt pipelines |
| [Meta-Prompt](30-meta-prompt.md) | Term | Prompts that generate prompts |
| [Negative Prompting](31-negative-prompting.md) | Term | Explicit exclusion instructions |
| [Structured Output](32-structured-output.md) | Term | Format-constrained responses |
| [Constrained Decoding](33-constrained-decoding.md) | Term | Grammar-enforced token generation |

---

## 2. CONTEXT

**Who uses it**: Anyone designing LLM inputs — from developers writing system prompts to researchers exploring reasoning techniques.

**When**: After understanding [Core LLM Concepts](../core-llm-concepts/README.md), before designing [Agentic Core](../agentic-core/README.md) architectures.

**In this ecosystem**:
- Prompt engineering operates within the [Context Window](../core-llm-concepts/05-context-window.md).
- [Temperature](../core-llm-concepts/06-temperature.md) and sampling parameters affect prompt effectiveness.
- [Prompt Injection](24-prompt-injection.md) and [Jailbreak](25-jailbreak.md) connect to [Safety & Alignment](../safety-alignment/README.md).

---

## 3. EXAMPLES

```yaml
prompt_engineering_router:
  - symptom: "Output is unpredictable or ignores instructions"
    open_first: ./14-system-prompt.md
  - symptom: "Model cannot reason through complex problems"
    open_first: ./19-chain-of-thought.md
  - symptom: "Output format keeps changing"
    open_first: ./32-structured-output.md
  - symptom: "Users are manipulating the model"
    open_first: ./24-prompt-injection.md
```

---

## 4. COMPARE

| | Prompt Engineering | Fine-tuning | RAG |
|--|---|---|---|
| **What changes** | Input text only | Model weights | Retrieved context |
| **Cost** | Free (text editing) | High (compute) | Medium (infrastructure) |
| **Speed to iterate** | Seconds | Hours to days | Minutes |
| **Best for** | Behavior shaping, format control | Deep domain adaptation | Factual grounding |

---

## 5. REF

| Resource | Type | Link | Note |
| --- | --- | --- | --- |
| Prompt Engineering Guide | Community | https://www.promptingguide.ai/ | Comprehensive prompt engineering reference |
| Anthropic — Prompt Engineering | Official | https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering | Claude-specific best practices |
| OpenAI — Prompt Engineering | Official | https://platform.openai.com/docs/guides/prompt-engineering | GPT-specific techniques |

---

## 6. RECOMMEND

| Explore next | When | Why | File/Link |
| --- | --- | --- | --- |
| System Prompt | You need a stable instruction header for your application | System prompts are the foundation of prompt design | [System Prompt](./14-system-prompt.md) |
| Chain-of-Thought | The model struggles with multi-step reasoning | CoT dramatically improves reasoning quality | [Chain-of-Thought](./19-chain-of-thought.md) |
| Structured Output | You need machine-parseable responses | Structured output is essential for agentic systems | [Structured Output](./32-structured-output.md) |

**Links**: [← Previous](../core-llm-concepts/README.md) · [→ Next](./13-prompt.md)
