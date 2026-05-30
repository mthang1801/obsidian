<!-- tags: glossary, reference, agentic-ai, llm-engineering, overview -->
# Agentic AI & LLM Engineering

> A glossary hub for the vocabulary of large language models, agentic systems, prompt engineering, and the infrastructure that makes autonomous AI work in production.

| Aspect | Detail |
| --- | --- |
| **Concept** | A comprehensive vocabulary map covering LLM fundamentals, prompt engineering, agentic patterns, tooling, orchestration, memory, evaluation, and safety. |
| **Audience** | AI engineer, ML engineer, backend developer building AI-powered systems, tech lead evaluating agentic architectures |
| **Primary style** | Glossary hub router |
| **Entry point** | Start here when you encounter an AI/LLM term you cannot place, or when your team uses the same word to mean different things across the agentic stack. |

📅 Created: 2026-04-28 · 🔄 Updated: 2026-04-28 · ⏱️ 10 min read

---

## 1. DEFINE

Your team is building an AI-powered feature. The product manager says "agent." The backend engineer thinks "function calling." The ML engineer means "ReAct loop with tool use." The DevOps lead asks about "guardrails" while the security team wants to discuss "sandboxing." Everyone is talking about the same system, but each person is anchored to a different layer of the stack. If the vocabulary is not aligned before the first design review, every architectural decision that follows will solve the wrong problem at the wrong layer.

**Agentic AI & LLM Engineering** is the discipline that spans from how a large language model generates tokens to how autonomous agents plan, act, use tools, collaborate, remember, and stay safe in production environments.

| Variant | Description |
| --- | --- |
| Foundation & inference | Core LLM mechanics — tokens, context windows, temperature, embeddings, fine-tuning. |
| Prompt craft | The art and science of shaping LLM behavior through input design — from zero-shot to chain-of-thought to constrained decoding. |
| Agentic architecture | How LLMs become agents — loops, planning, tool use, orchestration, memory, and multi-agent collaboration. |
| Production guardrails | Evaluation, observability, safety, alignment, and permission scoping that keep agentic systems trustworthy. |

| Approach | Time | Space | Choose it when |
| --- | --- | --- | --- |
| Route by layer | O(1) route | O(1) | You know which stack layer the confusion sits in. |
| Route by symptom | O(1) route | O(1) | You have a production problem and need the right term to search for solutions. |
| Route by role | O(1) route | O(1) | Different team members need different entry points into the same system. |

Core insight:

> Agentic AI is not one concept — it is a stack. Misrouting a question to the wrong layer wastes more time than not knowing the answer at all.

### 1.1 Signals & Boundaries

- If the question is about how a model generates text, tokenization, or training — route to **Core LLM Concepts**.
- If the pain is about getting better output from the model — route to **Prompt Engineering**.
- If the system needs to plan, act, and loop autonomously — route to **Agentic Core**.
- If the agent needs to interact with external systems — route to **Tools & Capabilities**.
- If the concern is about the infrastructure wrapping the agent — route to **Scaffolding & Harness**.
- If multiple steps need coordination — route to **Workflow & Orchestration**.
- If you need to intercept, validate, or transform LLM I/O — route to **Hooks & Middleware**.
- If multiple agents must collaborate — route to **Multi-Agent Systems**.
- If the agent needs to remember across sessions — route to **Memory Systems**.
- If you are packaging reusable capabilities — route to **Skills & Plugins**.
- If you need to measure quality or debug behavior — route to **Evaluation & Observability**.
- If the concern is about safety, permissions, or alignment — route to **Safety & Alignment**.

### Coverage Map

| Entry | Role | Entries | Note |
| --- | --- | --- | --- |
| [Core LLM Concepts](core-llm-concepts/README.md) | Subtopic hub | 12 docs | LLM, tokens, context, temperature, embeddings, fine-tuning |
| [Prompt Engineering](prompt-engineering/README.md) | Subtopic hub | 21 docs | Zero-shot to constrained decoding |
| [Agentic Core](agentic-core/README.md) | Subtopic hub | 12 docs | Agent loops, planning, autonomy, reflection |
| [Tools & Capabilities](tools-capabilities/README.md) | Subtopic hub | 11 docs | Function calling, RAG, browser use, search |
| [Scaffolding & Harness](scaffolding-harness/README.md) | Subtopic hub | 6 docs | Runtime, sandbox, execution environment |
| [Workflow & Orchestration](workflow-orchestration/README.md) | Subtopic hub | 12 docs | DAGs, pipelines, checkpoints, handoffs |
| [Hooks & Middleware](hooks-middleware/README.md) | Subtopic hub | 10 docs | Pre/post hooks, guardrails, parsers |
| [Multi-Agent Systems](multi-agent-systems/README.md) | Subtopic hub | 10 docs | Supervisor, critic, swarm, communication |
| [Memory Systems](memory-systems/README.md) | Subtopic hub | 8 docs | Short-term to external memory |
| [Skills & Plugins](skills-plugins/README.md) | Subtopic hub | 8 docs | Skill routing, MCP, composability |
| [Evaluation & Observability](evaluation-observability/README.md) | Subtopic hub | 10 docs | Evals, traces, spans, budgets |
| [Safety & Alignment](safety-alignment/README.md) | Subtopic hub | 8 docs | Alignment, red teaming, sandboxing, audit |

---

## 2. CONTEXT

**Who uses it**: AI engineers, ML engineers, backend developers integrating LLMs, tech leads evaluating agentic architectures, DevOps teams deploying AI systems, security teams auditing AI behavior.

**When**: Use this hub when your team is building, evaluating, or debugging any system that involves LLMs — from a simple chat completion endpoint to a multi-agent orchestration pipeline.

**Why it matters**: The agentic AI stack moves faster than most teams can absorb. A shared vocabulary prevents the most expensive mistake in AI engineering: solving the right problem at the wrong layer.

**In this ecosystem**:
- Start with **Core LLM Concepts** if your team is new to LLMs and needs baseline mechanics.
- Start with **Prompt Engineering** if output quality is the bottleneck.
- Start with **Agentic Core** if you are designing autonomous workflows.
- Start with **Safety & Alignment** if you are shipping to production and need guardrails.

The vocabulary is mapped. The harder question is which lane to enter first based on where your system is failing right now.

---

## 3. EXAMPLES

The hub becomes useful when a team can route a live production question to the right glossary entry without debating terminology first.

### Example 1: Basic — Route the right symptom to the right cluster

> **Goal**: Stop a planning meeting from collapsing into "we need AI" without specifying which layer.
> **Approach**: Start from the symptom, not the buzzword.
> **Complexity**: Basic

```yaml
agentic_router:
  - symptom: "The model keeps making things up"
    open_first: ./core-llm-concepts/08-hallucination.md
    also_check: ./core-llm-concepts/09-grounding.md

  - symptom: "The output format is unpredictable"
    open_first: ./prompt-engineering/32-structured-output.md
    also_check: ./prompt-engineering/33-constrained-decoding.md

  - symptom: "The agent gets stuck in a loop"
    open_first: ./agentic-core/35-agentic-loop.md
    also_check: ./workflow-orchestration/70-retry-policy.md

  - symptom: "We need the agent to call our APIs"
    open_first: ./tools-capabilities/46-tool-use-function-calling.md
    also_check: ./tools-capabilities/47-tool-schema.md

  - symptom: "The agent forgets what happened earlier"
    open_first: ./memory-systems/95-short-term-memory.md
    also_check: ./memory-systems/96-long-term-memory.md
```

**Conclusion**: The first value of this hub is reducing the cost of misrouting a question to the wrong layer of the agentic stack.

### Example 2: Intermediate — Build a learning path across clusters

> **Goal**: Read the glossary in a sequence that builds understanding layer by layer.
> **Approach**: Follow the stack from bottom (LLM mechanics) to top (safety).
> **Complexity**: Intermediate

```yaml
learning_path:
  foundation:
    - Core LLM Concepts
    - Prompt Engineering
  agentic_layer:
    - Agentic Core
    - Tools & Capabilities
    - Scaffolding & Harness
  orchestration_layer:
    - Workflow & Orchestration
    - Hooks & Middleware
    - Multi-Agent Systems
  production_layer:
    - Memory Systems
    - Skills & Plugins
    - Evaluation & Observability
    - Safety & Alignment
```

**Conclusion**: At the intermediate level, the hub becomes a curriculum that prevents teams from jumping to multi-agent systems before understanding the agentic loop.

### Example 3: Advanced — Use the hub as a design review vocabulary

> **Goal**: Keep architecture reviews, ADRs, and incident postmortems using the same AI vocabulary.
> **Approach**: Map each design decision to the glossary entry that governs it.
> **Complexity**: Advanced

```yaml
design_review_vocabulary:
  model_selection: Core LLM Concepts
  prompt_design: Prompt Engineering
  agent_architecture: Agentic Core
  external_integration: Tools & Capabilities
  infrastructure: Scaffolding & Harness
  pipeline_design: Workflow & Orchestration
  request_lifecycle: Hooks & Middleware
  multi_agent_design: Multi-Agent Systems
  state_management: Memory Systems
  extensibility: Skills & Plugins
  quality_assurance: Evaluation & Observability
  compliance: Safety & Alignment
```

**Conclusion**: At the advanced level, this hub is a governance map that ensures every AI design decision references the right layer of the stack.

---

## 4. COMPARE

| | Traditional Software Glossary | Agentic AI Glossary |
|--|------|------|
| **Scope** | Deterministic systems with predictable I/O | Probabilistic systems with emergent behavior |
| **Key tension** | Correctness and performance | Alignment, hallucination, and controllability |
| **Failure mode** | Bug — code does wrong thing | Drift — model does plausible but wrong thing |
| **Governance** | Code review and tests | Evals, guardrails, and red teaming |

### Easy-to-miss Boundary Drift

| # | Severity | Mistake | Consequence | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Fatal | Treating prompt engineering as the solution to an architecture problem | The team optimizes prompts when they need agent planning or tool use | Route the symptom to the correct cluster first |
| 2 | 🟡 Common | Mixing "agent" and "workflow" as if they are the same | Deterministic pipelines get agentic complexity they do not need | Separate agentic-core from workflow-orchestration |
| 3 | 🟡 Common | Skipping evaluation before shipping | The system works in demos but fails on edge cases in production | Read evaluation-observability before deploying |
| 4 | 🔵 Minor | Using "RAG" as a catch-all for any retrieval | Semantic search, hybrid search, and vector DB are distinct capabilities | Check tools-capabilities for the precise term |

---

## 5. REF

| Resource | Type | Link | Note |
| --- | --- | --- | --- |
| Anthropic — Building Effective Agents | Guide | https://www.anthropic.com/engineering/building-effective-agents | Practical patterns for agentic systems |
| OpenAI — Function Calling Guide | Official | https://platform.openai.com/docs/guides/function-calling | Foundation for tool use patterns |
| LangChain Conceptual Guide | Reference | https://python.langchain.com/docs/concepts/ | Comprehensive framework vocabulary |
| Google — Agents white paper | Research | https://cloud.google.com/discover/what-are-ai-agents | Agent architecture overview |
| Model Context Protocol (MCP) | Specification | https://modelcontextprotocol.io/ | Standard for tool and data integration |

---

## 6. RECOMMEND

You have identified the landscape. Now pick the entry point that matches where your system is failing or where your next design decision sits.

| Explore next | When | Why | File/Link |
| --- | --- | --- | --- |
| Core LLM Concepts first | Your team is new to LLMs or mixing up inference, tokens, and context | These mechanics constrain every decision above them | [Core LLM Concepts](./core-llm-concepts/README.md) |
| Prompt Engineering next | The model works but output quality is inconsistent | Prompt craft is the highest-leverage intervention before architecture changes | [Prompt Engineering](./prompt-engineering/README.md) |
| Agentic Core when ready | You need the system to plan, act, and loop without human intervention | This is where LLMs become agents | [Agentic Core](./agentic-core/README.md) |
| Safety & Alignment before shipping | The system is going to production | Every other layer is wasted if the agent is unsafe | [Safety & Alignment](./safety-alignment/README.md) |

---

## 7. QUICK REF

| If you encounter | Open first |
| --- | --- |
| Model generates incorrect facts | [Hallucination](./core-llm-concepts/08-hallucination.md), [Grounding](./core-llm-concepts/09-grounding.md) |
| Output format is unpredictable | [Structured Output](./prompt-engineering/32-structured-output.md) |
| Need the model to call external APIs | [Tool Use / Function Calling](./tools-capabilities/46-tool-use-function-calling.md) |
| Agent stuck in infinite loop | [Agentic Loop](./agentic-core/35-agentic-loop.md), [Retry Policy](./workflow-orchestration/70-retry-policy.md) |
| Agent forgets previous context | [Memory Systems](./memory-systems/README.md) |
| Need multiple agents to collaborate | [Multi-Agent Systems](./multi-agent-systems/README.md) |
| Shipping to production — what could go wrong? | [Safety & Alignment](./safety-alignment/README.md) |
| How to measure if the agent is working | [Evaluation & Observability](./evaluation-observability/README.md) |

**Links**: [← Previous](../README.md) · [→ Next](./core-llm-concepts/README.md)
