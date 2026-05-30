<!-- tags: glossary, agentic-ai, memory-systems -->
# Working Memory

> A temporary digital scratchpad where an AI holds variables, intermediate math, and task steps while it works.

| Aspect | Detail |
| --- | --- |
| **Domain** | Memory Systems |
| **Used by** | AI engineer, prompt engineer |
| **Related** | See RECOMMEND section |

📅 Created: 2026-04-28 · 🔄 Updated: 2026-05-13 · ⏱️ 5 min read

---

## 1. DEFINE

**Working Memory** is the highly dynamic, immediate processing space an AI agent uses *during* the execution of a complex task. It functions like a cognitive scratchpad. While short-term memory holds the conversational history, working memory holds the intermediate state—such as tool outputs, parsed variables, pending sub-tasks, and unverified hypotheses—before the final answer is synthesized and delivered to the user.

---

## 2. CONTEXT

**Who uses it**: AI Engineers building multi-step reasoning loops (like ReAct).
**When**: Designing agents that execute complex workflows requiring multiple sequential API calls where step 3 depends on the output of step 2.
**Why it matters**: Without a structured working memory (often implemented as a JSON state object in the orchestration layer), an LLM has to cram all its intermediate reasoning into its output text, which can confuse the user. Working memory keeps the messy "thinking" hidden while preserving the data for the next step.

---

## 3. EXAMPLES

### Example 1: The Hidden State Object

![Explainer](images/99-working-memory-explainer.png)

An agent is asked: "Find my latest invoice and email it to accounting."
1. **Step 1**: Agent calls `search_invoices()` tool.
2. **Working Memory Update**: The system saves `invoice_url: "s3://invoices/123.pdf"` into the agent's invisible state dictionary.
3. **Step 2**: Agent calls `email_attachment(url)` tool. It pulls the URL directly from Working Memory.
4. **Final Output**: The agent tells the user, "Email sent," without ever needing to print the raw S3 URL into the chat interface. The Working Memory is then cleared.

---

## 4. COMPARE

| Feature | Working Memory | Short-Term Memory |
|---|---|---|
| **Primary Use** | Holding intermediate variables and task state | Holding conversational dialogue |
| **Format** | Structured JSON / State dictionaries | Raw text strings / Message arrays |
| **Visibility** | Hidden from the user (internal scratchpad) | Visible to the user (chat history) |

---

## 5. REF

| Resource | Type | Link | Note |
| --- | --- | --- | --- |
| LangGraph State | Framework Docs | https://python.langchain.com/docs/langgraph | How LangGraph passes working memory between nodes |
| Scratchpad Prompting | Concept | https://arxiv.org/abs/2112.00114 | Using explicit `<scratchpad>` XML tags for LLM working memory |

---

## 6. RECOMMEND

| Explore next | When | Why | File/Link |
| --- | --- | --- | --- |
| Chain of Thought | You want the LLM to write out its memory | CoT is a way of forcing working memory into text | [Chain of Thought](../prompt-engineering/19-chain-of-thought.md) |
| Shared Memory | You have multiple agents | Shared memory is just a global working memory for swarms | [Shared Memory](../multi-agent-systems/93-shared-memory.md) |

**Links**: [← Previous](./98-semantic-memory.md) · [→ Next](./100-memory-compression.md)
