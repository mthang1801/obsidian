<!-- tags: glossary, agentic-ai, evaluation-observability -->
# LLM-as-Judge

> Using a highly capable AI model to read and grade the homework of another AI model.

| Aspect | Detail |
| --- | --- |
| **Domain** | Evaluation & Observability |
| **Used by** | ML ops engineer, AI researcher |
| **Related** | See RECOMMEND section |

📅 Created: 2026-04-28 · 🔄 Updated: 2026-05-13 · ⏱️ 5 min read

---

## 1. DEFINE

**LLM-as-Judge** is an evaluation paradigm where a powerful, highly aligned Large Language Model (like GPT-4 or Claude 3.5 Sonnet) is used to automatically evaluate and score the outputs of another model or agent. Instead of relying on rigid, deterministic metrics (like exact word match or BLEU scores), the judge model is given a grading rubric and asked to score the text on nuanced qualities like tone, factual accuracy, or helpfulness.

---

## 2. CONTEXT

**Who uses it**: ML Ops Engineers and AI Researchers.
**When**: Evaluating tasks that have high variance in acceptable answers, such as summarization, creative writing, or conversational roleplay, where traditional regex or string-matching tests fail entirely.
**Why it matters**: Human evaluation is the gold standard but is incredibly slow, expensive, and non-scalable. Traditional NLP metrics (like ROUGE) are fast but correlate poorly with actual human preference. LLM-as-Judge offers the best of both worlds: the nuance of a human reader at the speed and cost of an automated script.

---

## 3. EXAMPLES

### Example 1: The Politeness Grader

![Explainer](images/112-llm-as-judge-explainer.png)

1. The target agent generates a response: "Your password is wrong. Reset it here."
2. The eval system takes this response and feeds it to the **Judge Model** (e.g., GPT-4o).
3. The Judge Prompt: "You are an expert customer service evaluator. Rate the following response on a scale of 1-5 for politeness. Output only the number."
4. The Judge Model outputs: `2`.
5. The eval system logs the score. If the average politeness drops below 4.0 across the test suite, the build fails.

---

## 4. COMPARE

| Feature | LLM-as-Judge | Human Evaluation | Exact String Match |
|---|---|---|---|
| **Speed** | Extremely fast | Extremely slow | Instant |
| **Cost** | Moderate (API costs) | Very high | Free |
| **Nuance** | High | Maximum | Zero |

---

## 5. REF

| Resource | Type | Link | Note |
| --- | --- | --- | --- |
| Judging LLM-as-a-Judge | Research Paper | https://arxiv.org/abs/2306.05685 | Foundational paper verifying that strong LLMs correlate with human judges |
| LangSmith Evaluators | Tool | https://docs.smith.langchain.com/evaluation | Built-in LLM-as-Judge templates |

---

## 6. RECOMMEND

| Explore next | When | Why | File/Link |
| --- | --- | --- | --- |
| Evals | You want to know where the judge sits | LLM-as-Judge is just one specific type of Eval | [Evals](./111-evals.md) |
| Trace | You need to see why the model failed | If the judge gives a bad score, you use a Trace to debug | [Trace](./114-trace.md) |

**Links**: [← Previous](./111-evals.md) · [→ Next](./113-benchmark.md)
