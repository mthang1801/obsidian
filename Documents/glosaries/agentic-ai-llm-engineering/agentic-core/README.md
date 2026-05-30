<!-- tags: glossary, reference, agentic-ai, agentic-core, overview -->
# Agentic Core

> The foundational concepts that transform an LLM from a text generator into an autonomous agent — loops, planning, reflection, and human oversight.

| Aspect | Detail |
| --- | --- |
| **Concept** | Core patterns for building AI agents that plan, act, and self-correct with varying degrees of autonomy. |
| **Audience** | AI engineer, backend developer, architect designing agentic systems |
| **Primary style** | Glossary hub router |
| **Entry point** | Start here when the system needs to go beyond prompt-response into autonomous multi-step execution. |

📅 Created: 2026-04-28 · 🔄 Updated: 2026-04-28 · ⏱️ 7 min read

---

## 1. DEFINE

A prompt-response system answers questions. An agent solves problems. The difference is the loop: an agent observes the result of its action, decides whether the goal is met, and continues acting until it succeeds or escalates. This cluster defines the vocabulary for that transition — from a stateless text generator to a goal-directed system that plans, decomposes tasks, reflects on its work, and knows when to ask a human for help.

### Coverage Map

| Entry | Role | Note |
| --- | --- | --- |
| [AI Agent](34-ai-agent.md) | Term | The core definition |
| [Agentic Loop](35-agentic-loop.md) | Term | Observe → Think → Act cycle |
| [ReAct Loop](36-react-loop.md) | Term | Reason + Act pattern |
| [Autonomy Level](37-autonomy-level.md) | Term | L1 suggest to L3 autonomous |
| [Agency](38-agency.md) | Term | Capacity for independent action |
| [Goal-Directed Behavior](39-goal-directed-behavior.md) | Term | Acting toward objectives |
| [Task Decomposition](40-task-decomposition.md) | Term | Breaking tasks into sub-tasks |
| [Planning](41-planning.md) | Term | Creating execution plans |
| [Self-Reflection](42-self-reflection.md) | Term | Evaluating own output |
| [Self-Critique](43-self-critique.md) | Term | Criticizing own reasoning |
| [Human-in-the-Loop](44-human-in-the-loop.md) | Term | Human review checkpoints |
| [Interrupt / Escalation](45-interrupt-escalation.md) | Term | Transferring control to humans |

---

## 2. CONTEXT

**Who uses it**: Engineers building autonomous AI features, architects designing agentic pipelines, product managers defining autonomy boundaries.

**When**: After mastering [Prompt Engineering](../prompt-engineering/README.md), when the system needs to act, not just respond.

---

## 3. EXAMPLES

```yaml
agentic_router:
  - symptom: "System needs to take multi-step actions autonomously"
    open_first: ./34-ai-agent.md
  - symptom: "Agent gets stuck or loops forever"
    open_first: ./35-agentic-loop.md
  - symptom: "Need to control how much the agent can do on its own"
    open_first: ./37-autonomy-level.md
  - symptom: "Agent makes mistakes that a human could catch"
    open_first: ./44-human-in-the-loop.md
```

---

## 4. COMPARE

| | Agentic System | Workflow Automation | Chat Bot |
|--|---|---|---|
| **Decision making** | Autonomous, goal-directed | Predefined paths | Reactive, per-message |
| **Error handling** | Self-reflection, retry | Retry policies, fallbacks | Show error message |
| **Human involvement** | Configurable (L1–L3) | Minimal | Every interaction |

---

## 5. REF

| Resource | Type | Link | Note |
| --- | --- | --- | --- |
| Anthropic — Building Effective Agents | Guide | https://www.anthropic.com/engineering/building-effective-agents | Production agent patterns |
| LangGraph — Agent architectures | Docs | https://langchain-ai.github.io/langgraph/ | Framework for agentic systems |

---

## 6. RECOMMEND

| Explore next | When | Why | File/Link |
| --- | --- | --- | --- |
| AI Agent | You need to understand what makes an LLM an agent | This is the foundational definition | [AI Agent](./34-ai-agent.md) |
| Agentic Loop | You need to design the core execution cycle | The loop is the heartbeat of every agent | [Agentic Loop](./35-agentic-loop.md) |
| Human-in-the-Loop | You need safety boundaries for autonomous action | HITL is essential for production agents | [Human-in-the-Loop](./44-human-in-the-loop.md) |

**Links**: [← Previous](../prompt-engineering/README.md) · [→ Next](./34-ai-agent.md)
