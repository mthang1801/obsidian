<!-- tags: glossary, reference, agentic-ai, evaluation-observability, overview -->
# Evaluation & Observability

> Measuring, tracing, and monitoring AI systems — from automated evals and LLM-as-judge to traces, spans, and budget enforcement.

| Aspect | Detail |
| --- | --- |
| **Concept** | Frameworks for measuring AI quality, debugging agent behavior, and controlling costs in production. |
| **Audience** | AI engineer, QA engineer, ML engineer, DevOps |
| **Primary style** | Glossary hub router |
| **Entry point** | Start here when you need to answer "is the agent working?" or "why did the agent do that?" |

📅 Created: 2026-04-28 · 🔄 Updated: 2026-04-28 · ⏱️ 7 min read

---

## 1. DEFINE

Shipping an AI system without evaluation is like deploying code without tests. The system might work in demos but fail silently in production. This cluster defines the vocabulary for measuring AI quality (evals, benchmarks), debugging behavior (traces, spans), managing costs (token and latency budgets), and ensuring changes do not cause regressions.

### Coverage Map

| Entry | Role | Note |
| --- | --- | --- |
| [Evals](111-evals.md) | Term | Automated quality measurement |
| [LLM-as-Judge](112-llm-as-judge.md) | Term | Using LLMs to evaluate LLMs |
| [Benchmark](113-benchmark.md) | Term | Standardized comparison datasets |
| [Trace](114-trace.md) | Term | Full execution record |
| [Span](115-span.md) | Term | Single step in a trace |
| [Prompt Versioning](116-prompt-versioning.md) | Term | Prompt change management |
| [Latency Budget](117-latency-budget.md) | Term | Time allocation per pipeline |
| [Token Budget](118-token-budget.md) | Term | Cost control per run |
| [LLM Observability](119-llm-observability.md) | Term | Monitoring infrastructure |
| [Regression Testing for AI](120-regression-testing-for-ai.md) | Term | Preventing quality degradation |

---

## 2. CONTEXT

**Who uses it**: QA engineers designing test suites, ML engineers measuring model quality, DevOps monitoring production systems.

**When**: Before shipping to production, and continuously after deployment.

---

## 5. REF

| Resource | Type | Link | Note |
| --- | --- | --- | --- |
| LangSmith | Platform | https://smith.langchain.com/ | LLM observability and evaluation |
| Langfuse | Tool | https://langfuse.com/ | Open-source LLM observability |
| Braintrust | Platform | https://www.braintrust.dev/ | Eval and prompt management |

---

## 6. RECOMMEND

| Explore next | When | Why | File/Link |
| --- | --- | --- | --- |
| Evals | You need to measure output quality systematically | Evals are the starting point for AI quality | [Evals](./111-evals.md) |
| Trace | You need to debug a specific agent run | Traces show every step the agent took | [Trace](./114-trace.md) |
| Token Budget | Costs are unpredictable | Token budgets prevent runaway spending | [Token Budget](./118-token-budget.md) |

**Links**: [← Previous](../skills-plugins/README.md) · [→ Next](./111-evals.md)
