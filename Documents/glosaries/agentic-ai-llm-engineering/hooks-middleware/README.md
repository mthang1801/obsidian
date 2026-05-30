<!-- tags: glossary, reference, agentic-ai, hooks-middleware, overview -->
# Hooks & Middleware

> Interception points in the agent lifecycle — validating inputs, transforming outputs, enforcing guardrails, and observing every LLM interaction.

| Aspect | Detail |
| --- | --- |
| **Concept** | Patterns for intercepting, validating, and transforming data at every stage of the agent request lifecycle. |
| **Audience** | AI engineer, backend developer, security engineer |
| **Primary style** | Glossary hub router |
| **Entry point** | Start here when you need to add logging, validation, safety checks, or transformation without modifying core agent logic. |

📅 Created: 2026-04-28 · 🔄 Updated: 2026-04-28 · ⏱️ 7 min read

---

## 1. DEFINE

An agent calls an LLM and gets a response. Between that call and the user seeing the result, a production system needs to: log the interaction, check for PII, validate the output format, enforce rate limits, track costs, and filter harmful content. Hooks and middleware are the architectural pattern for inserting these cross-cutting concerns without coupling them to the agent's core logic.

### Coverage Map

| Entry | Role | Note |
| --- | --- | --- |
| [Hook](75-hook.md) | Term | Lifecycle insertion point |
| [Pre-hook](76-pre-hook.md) | Term | Before-action processing |
| [Post-hook](77-post-hook.md) | Term | After-action processing |
| [Middleware](78-middleware.md) | Term | Request/response layer |
| [Interceptor](79-interceptor.md) | Term | Request/response handler |
| [Callback](80-callback.md) | Term | Event-triggered function |
| [Event Listener](81-event-listener.md) | Term | Event subscription pattern |
| [Guardrail](82-guardrail.md) | Term | Output safety validation |
| [Output Parser](83-output-parser.md) | Term | Structured data extraction |
| [Input Guard](84-input-guard.md) | Term | Input sanitization |

---

## 2. CONTEXT

**Who uses it**: Security engineers adding safety layers, backend developers implementing logging and validation, platform engineers building reusable middleware.

**When**: After the agent architecture is designed, when cross-cutting concerns need to be addressed systematically.

---

## 5. REF

| Resource | Type | Link | Note |
| --- | --- | --- | --- |
| Guardrails AI | Tool | https://www.guardrailsai.com/ | Output validation framework |
| NeMo Guardrails | Tool | https://github.com/NVIDIA/NeMo-Guardrails | NVIDIA's guardrail toolkit |

---

## 6. RECOMMEND

| Explore next | When | Why | File/Link |
| --- | --- | --- | --- |
| Guardrail | You need to validate LLM output before it reaches users | Guardrails are the most critical hook in production | [Guardrail](./82-guardrail.md) |
| Middleware | You need a reusable interception layer | Middleware is the foundational pattern | [Middleware](./78-middleware.md) |
| Input Guard | You need to protect against prompt injection | Input guards sanitize before the LLM sees the input | [Input Guard](./84-input-guard.md) |

**Links**: [← Previous](../workflow-orchestration/README.md) · [→ Next](./75-hook.md)
