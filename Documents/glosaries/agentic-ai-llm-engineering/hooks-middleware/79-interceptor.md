<!-- tags: glossary, agentic-ai, hooks-middleware -->
# Interceptor

> A strict checkpoint that can completely block or redirect a request if it violates a rule.

| Aspect | Detail |
| --- | --- |
| **Domain** | Hooks & Middleware |
| **Used by** | Security engineer, backend developer |
| **Related** | See RECOMMEND section |

📅 Created: 2026-04-28 · 🔄 Updated: 2026-05-13 · ⏱️ 5 min read

---

## 1. DEFINE

An **Interceptor** is an aggressive piece of middleware or hook designed specifically to halt execution if certain conditions are not met. While standard middleware usually transforms data and passes it along, an interceptor analyzes the payload (or the context) and can short-circuit the entire process, returning an immediate error or fallback response to the user without ever querying the LLM.

---

## 2. CONTEXT

**Who uses it**: Security Engineers and Backend API Developers.
**When**: Enforcing hard boundaries, such as blocking toxic content, denying unauthorized tool usage, or preventing execution when the user has run out of account credits.
**Why it matters**: Calling an LLM is slow and expensive. If a user asks a highly offensive question, there is no reason to spend money evaluating it. An interceptor catches the violation instantly and blocks it, saving compute and protecting the system.

---

## 3. EXAMPLES

### Example 1: The Semantic Cache Interceptor

![Explainer](images/79-interceptor-explainer.png)

1. User asks: "What is the capital of France?"
2. The **Cache Interceptor** catches the prompt.
3. It checks the semantic cache database and sees this exact question was answered 5 seconds ago by another user.
4. The interceptor **short-circuits** the request. It returns "Paris" immediately.
5. The LLM is never invoked, saving time and money.

---

## 4. COMPARE

| Feature | Interceptor | Standard Middleware |
|---|---|---|
| **Primary Action** | Blocking, Short-circuiting, Redirecting | Filtering, Modifying, Enriching |
| **Execution Flow** | Can stop the pipeline completely | Usually passes data to the next step |
| **Common Use Case** | Caching, Authentication, Hard Guardrails | Logging, Data formatting |

---

## 5. REF

| Resource | Type | Link | Note |
| --- | --- | --- | --- |
| gRPC Interceptors | Framework | https://grpc.io/docs/guides/interceptors/ | The technical pattern used in high-performance backends |
| Semantic Caching | Concept | https://github.com/zilliztech/GPTCache | A common implementation of an AI interceptor |

---

## 6. RECOMMEND

| Explore next | When | Why | File/Link |
| --- | --- | --- | --- |
| Guardrail | You want to intercept bad behavior | Guardrails are interceptors specifically for safety | [Guardrail](./82-guardrail.md) |
| Input Guard | You are intercepting malicious prompts | Input Guards intercept at the very beginning of the pipeline | [Input Guard](./84-input-guard.md) |

**Links**: [← Previous](./78-middleware.md) · [→ Next](./80-callback.md)
