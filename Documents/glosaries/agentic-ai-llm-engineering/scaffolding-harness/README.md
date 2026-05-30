<!-- tags: glossary, reference, agentic-ai, scaffolding-harness, overview -->
# Scaffolding & Harness

> The framework infrastructure that wraps an LLM to make it operational — prompt management, tool routing, retry logic, and execution environments.

| Aspect | Detail |
| --- | --- |
| **Concept** | Infrastructure patterns that turn a raw LLM into a deployable, testable, manageable agent. |
| **Audience** | AI engineer, platform engineer, DevOps |
| **Primary style** | Glossary hub router |
| **Entry point** | Start here when the question is not "what can the agent do?" but "where does the agent run and how is it managed?" |

📅 Created: 2026-04-28 · 🔄 Updated: 2026-04-28 · ⏱️ 6 min read

---

## 1. DEFINE

An LLM alone is like an engine without a car. It generates text, but it cannot manage prompts, route tools, retry on failure, log its decisions, or run in a controlled environment. Scaffolding is the car — the framework that makes the engine useful. This cluster defines the infrastructure layer between the raw model and the production system.

### Coverage Map

| Entry | Role | Note |
| --- | --- | --- |
| [Scaffolding](57-scaffolding.md) | Term | Framework wrapping the LLM |
| [Harness](58-harness.md) | Term | Test infrastructure for agents |
| [Agent Runtime](59-agent-runtime.md) | Term | Execution lifecycle manager |
| [Agent Sandbox](60-agent-sandbox.md) | Term | Isolated execution environment |
| [Execution Environment](61-execution-environment.md) | Term | Where the agent runs |
| [Agent Shell](62-agent-shell.md) | Term | CLI/API wrapper for agents |

---

## 2. CONTEXT

**Who uses it**: Platform engineers building agent infrastructure, DevOps deploying agents, QA engineers testing agent behavior.

**When**: After defining what the agent does ([Agentic Core](../agentic-core/README.md)) and what tools it uses ([Tools & Capabilities](../tools-capabilities/README.md)).

---

## 5. REF

| Resource | Type | Link | Note |
| --- | --- | --- | --- |
| LangChain — Agent infrastructure | Docs | https://python.langchain.com/docs/concepts/ | Framework for agent scaffolding |
| CrewAI | Tool | https://www.crewai.com/ | Multi-agent scaffolding platform |

---

## 6. RECOMMEND

| Explore next | When | Why | File/Link |
| --- | --- | --- | --- |
| Scaffolding | You need to understand the framework layer | Scaffolding is the first concept in this cluster | [Scaffolding](./57-scaffolding.md) |
| Agent Sandbox | You need safe execution for agent actions | Sandboxing prevents production damage | [Agent Sandbox](./60-agent-sandbox.md) |

**Links**: [← Previous](../tools-capabilities/README.md) · [→ Next](./57-scaffolding.md)
