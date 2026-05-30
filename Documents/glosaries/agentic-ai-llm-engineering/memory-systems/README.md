<!-- tags: glossary, reference, agentic-ai, memory-systems, overview -->
# Memory Systems

> How agents remember — from the ephemeral context window to persistent long-term storage, episodic recall, and working memory management.

| Aspect | Detail |
| --- | --- |
| **Concept** | Patterns for giving agents memory that persists beyond a single conversation — retrieval, compression, and external storage. |
| **Audience** | AI engineer, backend developer, architect |
| **Primary style** | Glossary hub router |
| **Entry point** | Start here when the agent needs to remember past interactions, learn from experience, or manage information across sessions. |

📅 Created: 2026-04-28 · 🔄 Updated: 2026-04-28 · ⏱️ 6 min read

---

## 1. DEFINE

An LLM has no memory. Every inference call starts from scratch — the only "memory" is what fits in the context window. For a single-turn chatbot, that is fine. For an agent that works with you across days, manages long-running projects, or learns from past mistakes, memory is the difference between a tool and a collaborator. This cluster defines the vocabulary for how agents acquire, store, retrieve, and manage information across time.

### Coverage Map

| Entry | Role | Note |
| --- | --- | --- |
| [Short-Term Memory](95-short-term-memory.md) | Term | Current context window |
| [Long-Term Memory](96-long-term-memory.md) | Term | Persistent external storage |
| [Episodic Memory](97-episodic-memory.md) | Term | Past interaction recall |
| [Semantic Memory](98-semantic-memory.md) | Term | Knowledge base facts |
| [Working Memory](99-working-memory.md) | Term | Active reasoning scratchpad |
| [Memory Compression](100-memory-compression.md) | Term | Summarizing to free space |
| [Memory Retrieval](101-memory-retrieval.md) | Term | Querying stored memories |
| [External Memory](102-external-memory.md) | Term | Any storage outside the model |

---

## 2. CONTEXT

**Who uses it**: Engineers building agents that need persistence, architects designing stateful AI systems.

**When**: When the agent needs to remember beyond the current conversation — user preferences, task history, or accumulated knowledge.

---

## 5. REF

| Resource | Type | Link | Note |
| --- | --- | --- | --- |
| MemGPT | Research | https://memgpt.ai/ | OS-inspired LLM memory management |
| Zep | Tool | https://www.getzep.com/ | Memory layer for AI assistants |

---

## 6. RECOMMEND

| Explore next | When | Why | File/Link |
| --- | --- | --- | --- |
| Short-Term Memory | You need to understand the baseline | Context window is the default "memory" | [Short-Term Memory](./95-short-term-memory.md) |
| Long-Term Memory | You need persistence across sessions | Long-term memory is the first extension beyond context | [Long-Term Memory](./96-long-term-memory.md) |
| Memory Compression | Context window is filling up | Compression summarizes history to free space | [Memory Compression](./100-memory-compression.md) |

**Links**: [← Previous](../multi-agent-systems/README.md) · [→ Next](./95-short-term-memory.md)
