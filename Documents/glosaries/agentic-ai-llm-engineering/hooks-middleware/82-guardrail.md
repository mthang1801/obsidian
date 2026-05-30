<!-- tags: glossary, agentic-ai, hooks-middleware -->
# Guardrail

> A specialized middleware rule that ensures the AI doesn't do or say anything dangerous, stupid, or out of character.

| Aspect | Detail |
| --- | --- |
| **Domain** | Hooks & Middleware |
| **Used by** | AI safety engineer, product manager |
| **Related** | See RECOMMEND section |

📅 Created: 2026-04-28 · 🔄 Updated: 2026-05-13 · ⏱️ 5 min read

---

## 1. DEFINE

A **Guardrail** is a specific type of semantic interceptor designed to enforce behavioral safety, brand guidelines, and factual accuracy. Unlike standard middleware that checks API keys or formatting, a guardrail evaluates the actual *meaning* of the prompt or response. If the AI generates text that violates the rules (e.g., giving medical advice when it's a banking bot), the guardrail blocks or modifies the output.

---

## 2. CONTEXT

**Who uses it**: AI Safety Engineers and Product Managers.
**When**: Deploying AI into production environments where brand reputation and legal compliance are at stake.
**Why it matters**: You cannot trust an LLM to follow its system prompt 100% of the time (due to jailbreaks or hallucination). Guardrails act as an independent, deterministic "supervisor" that sits between the LLM and the user, guaranteeing that bad outputs are caught before they cause harm.

---

## 3. EXAMPLES

### Example 1: The Competitor Mention Block

![Explainer](images/82-guardrail-explainer.png)

1. User asks the AcmeCorp AI: "Is Globex better than AcmeCorp?"
2. The LLM generates a response: "Globex has some better features in..."
3. The **Output Guardrail** intercepts the response and runs a semantic check against the `No_Competitor_Praise` rule.
4. The guardrail flags a violation.
5. Instead of sending the LLM's response, the guardrail overwrites it with a safe fallback: "I can only speak to the benefits of AcmeCorp products. How can I help you with those?"

---

## 4. COMPARE

| Feature | Guardrail | System Prompt |
|---|---|---|
| **Mechanism** | Middleware interceptor evaluating output | Instructions fed to the LLM |
| **Reliability** | Near 100% (if deterministic) | Variable (can be overridden by jailbreaks) |
| **Cost** | Adds latency and compute cost | Free (just part of the input) |

---

## 5. REF

| Resource | Type | Link | Note |
| --- | --- | --- | --- |
| NeMo Guardrails | Framework | https://github.com/NVIDIA/NeMo-Guardrails | NVIDIA's open-source guardrail system |
| Guardrails AI | Framework | https://www.guardrailsai.com/ | An open-source Python library for adding guardrails |

---

## 6. RECOMMEND

| Explore next | When | Why | File/Link |
| --- | --- | --- | --- |
| Input Guard | You want to block bad prompts | Input Guards are guardrails applied to the user's text | [Input Guard](./84-input-guard.md) |
| Output Parser | You want to enforce data formats | Output parsers act as guardrails for JSON structure | [Output Parser](./83-output-parser.md) |

**Links**: [← Previous](./81-event-listener.md) · [→ Next](./83-output-parser.md)
