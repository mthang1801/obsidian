<!-- tags: glossary, agentic-ai, hooks-middleware -->
# Pre-Hook

> Custom code that runs immediately *before* a prompt is sent to the LLM, often used to inject extra context.

| Aspect | Detail |
| --- | --- |
| **Domain** | Hooks & Middleware |
| **Used by** | Backend developer |
| **Related** | See RECOMMEND section |

📅 Created: 2026-04-28 · 🔄 Updated: 2026-05-13 · ⏱️ 5 min read

---

## 1. DEFINE

A **Pre-Hook** is a specific type of lifecycle hook that executes just before a request is transmitted to the language model or before a tool is invoked. It is typically used to dynamically enrich the prompt (e.g., injecting the current date, user location, or retrieved RAG context) or to perform authorization checks to ensure the user is allowed to execute the pending action.

---

## 2. CONTEXT

**Who uses it**: Backend Developers and Security Engineers.
**When**: Managing dynamic context that changes every second, or enforcing strict access controls right before compute is spent.
**Why it matters**: If you hardcode context into a system prompt, it becomes stale. A pre-hook ensures that the exact millisecond before the LLM fires, the prompt is injected with perfectly fresh data (like the current stock price) or validated against a fast security policy.

---

## 3. EXAMPLES

### Example 1: The Timestamp Injector

![Explainer](images/76-pre-hook-explainer.png)

1. User asks the agent: "Is the supermarket open right now?"
2. The agent is about to process the prompt, but it doesn't know what time it is.
3. The **Pre-Hook** `inject_time()` intercepts the payload.
4. It dynamically appends `[System Time: Tuesday, 8:45 PM]` to the system prompt.
5. The LLM receives the enriched prompt and accurately answers the question based on the injected time.

---

## 4. COMPARE

| Feature | Pre-Hook | Post-Hook |
|---|---|---|
| **Execution Timing** | Before the LLM/Tool runs | After the LLM/Tool finishes |
| **Primary Use** | Context injection, Validation, Auth | Logging, Parsing, Data formatting |
| **Payload** | Modifies the incoming request | Modifies the outgoing response |

---

## 5. REF

| Resource | Type | Link | Note |
| --- | --- | --- | --- |
| Middleware & Hooks | Concept | https://en.wikipedia.org/wiki/Middleware | The standard software pattern applied to AI |
| LangChain before_run | Framework | https://python.langchain.com/ | Example of pre-execution callbacks |

---

## 6. RECOMMEND

| Explore next | When | Why | File/Link |
| --- | --- | --- | --- |
| Post-Hook | You need to act on the result | Post-hooks are the natural counterpart to Pre-hooks | [Post-Hook](./77-post-hook.md) |
| Input Guard | You are doing security checks | An Input Guard is a specialized, security-focused Pre-hook | [Input Guard](./84-input-guard.md) |

**Links**: [← Previous](./75-hook.md) · [→ Next](./77-post-hook.md)
