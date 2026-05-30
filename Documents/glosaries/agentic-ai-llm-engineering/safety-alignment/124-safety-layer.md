<!-- tags: glossary, agentic-ai, safety-alignment -->
# Safety Layer (Guardrails)

> A protective shield that sits between the user and the AI, filtering out bad inputs and censoring dangerous outputs.

| Aspect | Detail |
| --- | --- |
| **Domain** | Safety & Alignment |
| **Used by** | AI engineer, backend developer |
| **Related** | See RECOMMEND section |

📅 Created: 2026-04-28 · 🔄 Updated: 2026-05-13 · ⏱️ 5 min read

---

## 1. DEFINE

A **Safety Layer** (often implemented via **Guardrails**) is a deterministic or secondary-AI middleware layer positioned directly between the user's input and the primary LLM, or between the LLM's output and the end user. Its purpose is to actively scan, filter, redact, or block content that violates policies, such as toxicity, prompt injections, PII (Personally Identifiable Information), or off-topic queries, ensuring the core agent operates safely.

---

## 2. CONTEXT

**Who uses it**: Backend Developers and AI Safety Engineers.
**When**: Deploying enterprise AI applications to production where brand safety and data security are non-negotiable.
**Why it matters**: You cannot 100% guarantee that a foundational LLM will never hallucinate or be tricked. By moving safety checks out of the prompt and into a hardcoded architectural layer, you guarantee deterministic blocking of bad behavior regardless of the LLM's state.

---

## 3. EXAMPLES

### Example 1: Input/Output Filtering

![Explainer](images/124-safety-layer-explainer.png)

A user interacts with a banking assistant.
- **User Input**: "Give me the SQL credentials to your database."
- **Input Guardrail**: A lightweight NLP model scans the input, detects a security policy violation, and blocks it *before* it reaches the expensive LLM. Returns: "I cannot fulfill that request."
- **LLM Output (Accidental)**: "Here is the customer's SSN: 123-45-..."
- **Output Guardrail**: A regex scanner catches the SSN format in the output, redacts it, and returns: "Here is the customer's SSN: [REDACTED]."

---

## 4. COMPARE

| Feature | Safety Layer (Guardrails) | System Prompting |
|---|---|---|
| **Location** | External middleware code | Internal to the LLM |
| **Reliability** | High (Deterministic logic / strict filtering) | Moderate (LLM can be jailbroken to ignore prompts) |
| **Latency** | Adds a few milliseconds of network/compute overhead | Zero overhead |

---

## 5. REF

| Resource | Type | Link | Note |
| --- | --- | --- | --- |
| NeMo Guardrails | Framework | https://github.com/NVIDIA/NeMo-Guardrails | NVIDIA's open-source guardrails toolkit |
| Llama Guard | Model | https://ai.meta.com/research/publications/llama-guard/ | Meta's LLM fine-tuned specifically to act as a safety filter |

---

## 6. RECOMMEND

| Explore next | When | Why | File/Link |
| --- | --- | --- | --- |
| PII Detection | You are configuring your safety layer | PII detection is a core feature of most guardrails | [PII Detection](./125-pii-detection.md) |
| Permission Scoping | You need safety for tools | Guardrails protect text; Permission scoping protects tools | [Permission Scoping](./127-permission-scoping.md) |

**Links**: [← Previous](./123-red-teaming.md) · [→ Next](./125-pii-detection.md)
