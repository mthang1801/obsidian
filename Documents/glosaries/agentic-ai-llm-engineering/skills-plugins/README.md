<!-- tags: glossary, reference, agentic-ai, skills-plugins, overview -->
# Skills & Plugins

> Packaged, reusable capabilities that agents can discover and invoke — from atomic actions to composable skill libraries and standardized protocols like MCP.

| Aspect | Detail |
| --- | --- |
| **Concept** | Patterns for packaging, discovering, routing, and composing agent capabilities into reusable units. |
| **Audience** | AI engineer, platform architect, developer ecosystem builder |
| **Primary style** | Glossary hub router |
| **Entry point** | Start here when you need to package agent capabilities for reuse, or when the agent needs to discover what it can do dynamically. |

📅 Created: 2026-04-28 · 🔄 Updated: 2026-04-28 · ⏱️ 6 min read

---

## 1. DEFINE

An agent that can only do what it was hard-coded to do is brittle. A plugin architecture lets agents discover new capabilities at runtime — send an email, query a database, generate an image — without redeployment. This cluster defines how capabilities are packaged, discovered, composed, and standardized.

### Coverage Map

| Entry | Role | Note |
| --- | --- | --- |
| [Skill](103-skill.md) | Term | Packaged capability unit |
| [Skill Library](104-skill-library.md) | Term | Collection of reusable skills |
| [Capability Discovery](105-capability-discovery.md) | Term | Runtime capability detection |
| [Composable Skills](106-composable-skills.md) | Term | Skills that combine like Lego |
| [Atomic Action](107-atomic-action.md) | Term | Indivisible action unit |
| [Skill Routing](108-skill-routing.md) | Term | Matching requests to skills |
| [Plugin](109-plugin.md) | Term | Distributed skill package |
| [MCP](110-mcp.md) | Term | Model Context Protocol |

---

## 2. CONTEXT

**Who uses it**: Platform architects building extensible agent systems, developers creating reusable AI capabilities.

**When**: After the agent has tools ([Tools & Capabilities](../tools-capabilities/README.md)) and needs to organize them into a discoverable, composable system.

---

## 5. REF

| Resource | Type | Link | Note |
| --- | --- | --- | --- |
| MCP Specification | Official | https://modelcontextprotocol.io/ | Standard protocol for tools and data |
| OpenAI Plugins (legacy) | Reference | https://platform.openai.com/docs/plugins | Original plugin architecture |

---

## 6. RECOMMEND

| Explore next | When | Why | File/Link |
| --- | --- | --- | --- |
| MCP | You need a standard protocol for tool integration | MCP is the emerging industry standard | [MCP](./110-mcp.md) |
| Skill | You need the basic unit of reusable capability | Skills are the atoms of the plugin system | [Skill](./103-skill.md) |
| Skill Routing | You need to match user intent to the right skill | Routing is the decision engine | [Skill Routing](./108-skill-routing.md) |

**Links**: [← Previous](../memory-systems/README.md) · [→ Next](./103-skill.md)
