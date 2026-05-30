<!-- tags: glossary, reference, agentic-ai, tools-capabilities, overview -->
# Tools & Capabilities

> The external functions, APIs, and data sources that give agents the ability to act in the real world — from function calling to RAG to browser automation.

| Aspect | Detail |
| --- | --- |
| **Concept** | How agents interact with external systems — calling functions, searching the web, executing code, and retrieving knowledge. |
| **Audience** | AI engineer, backend developer, platform engineer |
| **Primary style** | Glossary hub router |
| **Entry point** | Start here when the agent needs to do something beyond generating text — call an API, search a database, or browse the web. |

📅 Created: 2026-04-28 · 🔄 Updated: 2026-04-28 · ⏱️ 7 min read

---

## 1. DEFINE

An LLM alone can only generate text. It cannot check a database, call an API, execute code, or browse the web. Tools are what bridge the gap between "the model says it should check the inventory" and "the model actually checks the inventory." This cluster defines the vocabulary for everything an agent can do beyond text generation.

### Coverage Map

| Entry | Role | Note |
| --- | --- | --- |
| [Tool Use / Function Calling](46-tool-use-function-calling.md) | Term | Core mechanism for external actions |
| [Tool Schema](47-tool-schema.md) | Term | JSON definition of available tools |
| [Tool Registry](48-tool-registry.md) | Term | Catalogue of available tools |
| [Code Interpreter](49-code-interpreter.md) | Term | Execute code in sandbox |
| [Web Search Tool](50-web-search-tool.md) | Term | Real-time internet access |
| [Browser Use](51-browser-use.md) | Term | AI-driven browser automation |
| [Computer Use](52-computer-use.md) | Term | Desktop OS control |
| [RAG](53-rag.md) | Term | Retrieval-Augmented Generation |
| [Vector Database](54-vector-database.md) | Term | Embedding storage and search |
| [Semantic Search](55-semantic-search.md) | Term | Meaning-based retrieval |
| [Hybrid Search](56-hybrid-search.md) | Term | Semantic + keyword combined |

---

## 2. CONTEXT

**Who uses it**: AI engineers implementing tool integrations, backend developers exposing APIs to agents, platform engineers managing tool registries.

**When**: After understanding [Agentic Core](../agentic-core/README.md) loops — tools are what agents act with.

---

## 3. EXAMPLES

```yaml
tools_router:
  - symptom: "Agent needs to call our REST APIs"
    open_first: ./46-tool-use-function-calling.md
  - symptom: "Agent needs access to company knowledge base"
    open_first: ./53-rag.md
  - symptom: "Agent needs to run code and see results"
    open_first: ./49-code-interpreter.md
  - symptom: "Agent needs to search the internet"
    open_first: ./50-web-search-tool.md
```

---

## 5. REF

| Resource | Type | Link | Note |
| --- | --- | --- | --- |
| OpenAI — Function Calling | Official | https://platform.openai.com/docs/guides/function-calling | Core tool use API |
| MCP Specification | Spec | https://modelcontextprotocol.io/ | Standard tool protocol |

---

## 6. RECOMMEND

| Explore next | When | Why | File/Link |
| --- | --- | --- | --- |
| Tool Use / Function Calling | You need to understand how agents call external functions | This is the foundational tool mechanism | [Tool Use](./46-tool-use-function-calling.md) |
| RAG | You need to give the agent access to knowledge | RAG is the most common knowledge tool | [RAG](./53-rag.md) |
| Tool Schema | You need to define tools for an agent | Schema is the API contract for tools | [Tool Schema](./47-tool-schema.md) |

**Links**: [← Previous](../agentic-core/README.md) · [→ Next](./46-tool-use-function-calling.md)
