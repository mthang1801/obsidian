<!-- tags: overview -->
# Pattern-Based Diagrams

> Lane for pattern diagrams by use case: auth flow, microservices, CI/CD, database patterns.

| Aspect | Detail |
| --- | --- |
| **Concept** | Navigation hub for `Pattern-Based Diagrams` |
| **Audience** | Architect, platform engineer, reviewer |
| **Primary style** | Concept-First router |
| **Entry point** | Open when you need a familiar pattern visual to quickly explain a common architecture. |

📅 Updated: 2026-04-20 · ⏱️ 6 min read

---

## 1. DEFINE

You do not need to reinvent a new way to tell about auth flow or CI/CD pipeline every time. But you also do not want to copy a generic diagram that does not fit the system. Pattern-based diagrams sit in the middle: familiar enough to communicate fast, specific enough to still be useful.

This hub does not replace individual articles. It routes you to the correct lane before you wander into tools, syntax, or a specific diagram type.

### Signals & Boundaries

- Open this hub when you know the problem lives inside `Pattern-Based Diagrams` but are unsure which article to read first.
- Use the coverage map to route by pain point instead of file order.
- Return to this hub after each article to choose the next step with intention.

### Coverage Map

| Entry | Role |
| --- | --- |
| [Microservices Patterns Diagram](01-microservices-patterns.md) | Entry point for lane `Microservices Patterns Diagram` |
| [Auth Flow Diagram](02-auth-flow.md) | Entry point for lane `Auth Flow Diagram` |
| [CI/CD Pipeline Diagram](03-cicd-pipeline.md) | Entry point for lane `CI/CD Pipeline Diagram` |
| [Database Patterns Diagram](04-database-patterns.md) | Entry point for lane `Database Patterns Diagram` |

---

## 2. VISUAL

### Reusable Architecture Templates

Four pattern templates cover the most frequently diagrammed architecture concerns. The image below shows each pattern with a simplified flow: outbox/saga for microservices, OAuth2 token exchange for auth, linear stage gates for CI/CD, and CQRS/replication for database patterns.

![Diagram Patterns Overview — 4 reusable templates: Microservices Pattern (API → DB → Outbox → Broker → Services), Auth Flow (Client → Auth Server → Resource Server with token exchange), CI/CD Pipeline (Code → Build → Test → Deploy with gates), Database Pattern (Write DB → Event Bus → Read DB with projections)](../images/patterns-overview.png)

*Image: Pattern diagrams exist to stop teams from reinventing the same narrative frame every sprint. The trade-off: a generic pattern diagram that does not fit the actual system is worse than no diagram at all.*

### Preview UI

```mermaid
flowchart LR
Micro[Microservices Patterns] --> Auth[Auth Flow]
Auth --> CICD[CI/CD Pipeline]
CICD --> DB[Database Patterns]
```

*Figure: Pattern diagrams progress from service architecture (Microservices) through security (Auth), deployment (CI/CD), to persistence (Database).*

---

## 3. CODE

### Mermaid Practice Block

````md
```mermaid
flowchart LR
Micro[Microservices Patterns] --> Auth[Auth Flow]
Auth --> CICD[CI/CD Pipeline]
CICD --> DB[Database Patterns]
```
````

### Problem 1: Basic — Route the lane before reading deep

> **Goal**: Prevent study or review from drifting into "open whichever article looks interesting."
> **Approach**: Choose a lane by pain point.
> **Complexity**: Basic

```yaml
router:
  module: Pattern-Based Diagrams
  rule: "choose by pain point, not by familiar name"
  suggested_path:
  - 01-microservices-patterns.md
  - 02-auth-flow.md
  - 03-cicd-pipeline.md
  - 04-database-patterns.md
```

---

## 4. PITFALLS

| # | Severity | Mistake | Consequence | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Fatal | Reading by file order instead of routing by pain point | Accumulates terminology without solving the real problem | Use the coverage map first |
| 2 | 🟡 Common | Treating the README as a pure link catalog | Loses the hub's routing purpose | Always ask "which lane matches my current pain?" |
| 3 | 🔵 Minor | Finishing an article without returning to the hub | Jumps to an adjacent article by instinct | Return to the README to pick the next step |

---

## 5. REF

| Resource | Type | Link | Notes |
| --- | --- | --- | --- |
| Microservices.io | Reference site | https://microservices.io/ | Pattern catalog for service architecture |
| OAuth 2.0 | Official guidance | https://oauth.net/2/ | Auth flow background |
| Mermaid docs | Official docs | https://mermaid.js.org/ | Diagram-as-code default for repo docs |

## 6. RECOMMEND

| Next step | When | Reason | File/Link |
| --- | --- | --- | --- |
| Microservices Patterns | When your pain point matches this lane | Continue into the right cluster | [Microservices Patterns](01-microservices-patterns.md) |
| Auth Flow Diagram | When your pain point matches this lane | Continue into the right cluster | [Auth Flow](02-auth-flow.md) |
| CI/CD Pipeline | When your pain point matches this lane | Continue into the right cluster | [CI/CD Pipeline](03-cicd-pipeline.md) |
