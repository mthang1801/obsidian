<!-- tags: diagram, reference, bridge -->
# ER Diagram

> Bridge doc that keeps old links alive while routing readers to the canonical article in the new `diagram/` taxonomy.

| Aspect | Detail |
| --- | --- |
| **Concept** | Legacy bridge for `ER Diagram` |
| **Audience** | Readers arriving from old links, bookmarks, or cross-references |
| **Primary style** | Bridge router |
| **Entry point** | Open when you land on an old file and need the canonical version. |

📅 Updated: 2026-04-20 · ⏱️ 3 min read

---

## 1. DEFINE

Picture a schema review where everyone is talking about users, orders, payments, and products, but nobody is sure whether the real relationship between them is one-to-many or many-to-many. At that moment, an ER diagram is not decoration — it is the way you lock down ownership and cardinality before queries or migrations start drifting.

This file still exists to prevent broken links, but canonical content has moved to the new taxonomy. Its only job now is to route you to the article that is actively maintained.

### Canonical destination

| New file | Role |
| --- | --- |
| [ER Diagram](02-structural/01-er-diagram.md) | Current canonical article for this topic |

---

## 2. VISUAL

### Preview UI

Seeing the output first locks the diagram shape before you touch any practice work.

```mermaid
erDiagram
USER ||--o{ ORDER : places
ORDER ||--|{ ORDER_ITEM : contains
PRODUCT ||--o{ ORDER_ITEM : referenced_by
```

*Figure: Minimal Mermaid render so you see the target shape before moving to the practice section.*

The path here is simple: from the old link to the new canonical article, where narrative, visuals, and examples are kept in sync.

### Level 1

```text
legacy bookmark / old link
  -> open this bridge
  -> navigate to canonical article
  -> read the new taxonomy version
```

*Figure: A bridge doc is a transfer point, not a long-term content home.*

---

## 3. CODE

The artifact below is a short checklist for keeping old links alive without sending readers astray.

### Mermaid Practice Block

The block below holds the same shape as the preview, in raw Mermaid so you can copy it into the Mermaid Live Editor or your docs and customize.

````md
```mermaid
erDiagram
USER ||--o{ ORDER : places
ORDER ||--|{ ORDER_ITEM : contains
PRODUCT ||--o{ ORDER_ITEM : referenced_by
```
````

### Problem 1: Basic — Redirect via doc bridge

> **Goal**: Keep old bookmarks working while the new taxonomy stabilizes.
> **Approach**: State clearly that this is a bridge doc and point straight to the canonical file.
> **Example**: `ER Diagram` has been regrouped into the appropriate subfolder.
> **Complexity**: Basic

```yaml
bridge_doc:
  old_path: 03-er-diagram.md
  canonical_path: 02-structural/01-er-diagram.md
  rule: "read new content at the canonical article; do not maintain two sources in parallel"
```

---

## 4. PITFALLS

The hardest part of diagramming is not syntax — it is choosing the wrong diagram type for the wrong question. The pitfalls below cover where that mismatch usually happens.

| # | Severity | Mistake | Consequence | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🟡 Common | Treating the bridge doc as the canonical article | Reads an abridged version and misses new content | Always navigate to the canonical article |
| 2 | 🟡 Common | Maintaining both the old file and the new file in parallel | Narrative drift and structural drift | Keep the bridge as a redirect only |
| 3 | 🔵 Minor | Changing taxonomy without creating a bridge | Old links break, old bookmarks lose value | Keep the bridge short but clear about its role |

---

## 5. REF

| Resource | Type | Link | Notes |
| --- | --- | --- | --- |
| Mermaid ER diagram | Official docs | https://mermaid.js.org/syntax/entityRelationshipDiagram.html | ERD in markdown |
| PlantUML IE diagrams | Official docs | https://plantuml.com/ie-diagram | Information engineering notation |
| PostgreSQL constraints | Official docs | https://www.postgresql.org/docs/current/ddl-constraints.html | PK/FK/cardinality grounding |

## 6. RECOMMEND

Once you see where this diagram type is strong and where it breaks, the next step is to open the right adjacent lane rather than jumping randomly to another type.

| Next step | When | Reason | File/Link |
| --- | --- | --- | --- |
| ER Diagram | When you need canonical content, examples, and real pitfalls | The canonical article is maintained under the new workflow | [ER Diagram](02-structural/01-er-diagram.md) |
