<!-- tags: glossary, reference, agentic-ai, multi-agent-systems, overview -->
# Multi-Agent Systems

> Architectures where multiple specialized agents collaborate to solve problems beyond the capability of any single agent.

| Aspect | Detail |
| --- | --- |
| **Concept** | Patterns for composing, coordinating, and communicating between multiple AI agents working toward a shared goal. |
| **Audience** | AI architect, senior engineer, tech lead |
| **Primary style** | Glossary hub router |
| **Entry point** | Start here when one agent is not enough — when the problem requires specialized roles, debate, or parallel exploration. |

📅 Created: 2026-04-28 · 🔄 Updated: 2026-04-28 · ⏱️ 7 min read

---

## 1. DEFINE

One agent writes code. Another reviews it. A third runs the tests. A supervisor decides when the code is ready to ship. This is not one smart agent — it is a system of specialized agents, each with a defined role, communicating through a shared protocol. Multi-agent systems trade the simplicity of a single agent for the power of specialization and parallel execution.

### Coverage Map

| Entry | Role | Note |
| --- | --- | --- |
| [Multi-Agent System](85-multi-agent-system.md) | Term | The architecture pattern |
| [Agent Role](86-agent-role.md) | Term | Specialized responsibilities |
| [Supervisor Agent](87-supervisor-agent.md) | Term | Coordination and delegation |
| [Sub-Agent / Worker Agent](88-sub-agent-worker-agent.md) | Term | Task executors |
| [Critic Agent](89-critic-agent.md) | Term | Quality review agent |
| [Debate Pattern](90-debate-pattern.md) | Term | Adversarial improvement |
| [Swarm Intelligence](91-swarm-intelligence.md) | Term | Emergent collective behavior |
| [Agent Communication Protocol](92-agent-communication-protocol.md) | Term | Inter-agent messaging |
| [Shared Memory](93-shared-memory.md) | Term | State sharing between agents |
| [Agent Registry](94-agent-registry.md) | Term | Available agent catalogue |

---

## 2. CONTEXT

**Who uses it**: Architects designing complex AI systems, teams building AI-powered workflows that require specialization.

**When**: After single-agent patterns ([Agentic Core](../agentic-core/README.md)) hit their limits.

---

## 5. REF

| Resource | Type | Link | Note |
| --- | --- | --- | --- |
| CrewAI | Framework | https://www.crewai.com/ | Multi-agent orchestration |
| AutoGen | Framework | https://microsoft.github.io/autogen/ | Microsoft's multi-agent framework |
| OpenAI Swarm | Reference | https://github.com/openai/swarm | Lightweight multi-agent patterns |

---

## 6. RECOMMEND

| Explore next | When | Why | File/Link |
| --- | --- | --- | --- |
| Multi-Agent System | You need the foundational definition | Start here before diving into roles | [Multi-Agent System](./85-multi-agent-system.md) |
| Supervisor Agent | You need a coordination pattern | Supervisor is the most common orchestration approach | [Supervisor Agent](./87-supervisor-agent.md) |
| Debate Pattern | You need higher quality through adversarial review | Debate reduces hallucination through multi-perspective critique | [Debate Pattern](./90-debate-pattern.md) |

**Links**: [← Previous](../hooks-middleware/README.md) · [→ Next](./85-multi-agent-system.md)
