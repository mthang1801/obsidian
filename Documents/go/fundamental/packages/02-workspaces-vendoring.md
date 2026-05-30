<!-- tags: golang, modules -->

# 📦 Go Workspaces, Vendoring & Private Modules

> Multi-module development with `go.work`, offline builds with `vendor/`, and private registry configuration with `GOPRIVATE`.

📅 Created: 2026-03-23 · 🔄 Updated: 2026-04-19 · ⏱️ 10 min read

| Aspect | Detail |
| --- | --- |
| **Concept** | Local multi-module development, offline dependency vendoring, private module access |
| **Use case** | Monorepos, air-gapped builds, internal corporate modules |
| **Key insight** | `go.work` replaces `replace` directives for local dev — stays in `.gitignore`, never pollutes `go.mod` |
| **Go toolchain** | `go work`, `go mod vendor`, `go env`, `replace` |

| TS/Node                   | Go                                |
| ------------------------- | --------------------------------- |
| Monorepo (nx, turborepo)  | `go.work` workspaces (Go 1.18+)   |
| `node_modules/`           | `vendor/` directory               |
| `.npmrc` private registry | `GOPRIVATE`, `GONOSUMDB` env vars |
| `"file:../shared"` path   | `replace` directive in `go.mod`   |

---

## 1. DEFINE

Developing a shared library and an API service simultaneously? Without workspaces, every change to the library requires a commit, push, and `go get` update in the service. With `go.work`, both modules resolve locally — zero publish cycles.

> *Your shared library evolves daily. The API service consumes it. Without `go.work`, every library change requires: commit → push → tag → `go get` in the service. That's 4 steps per iteration. With `go.work`, changes are visible immediately — the workspace overrides module resolution locally.*
>
> *Vendoring solves a different problem: reproducible builds without network access. `go mod vendor` copies all dependencies into `vendor/`, and `go build -mod=vendor` uses them exclusively. Air-gapped environments, CI without internet, and compliance audits all benefit. `GOPRIVATE` handles the third case: internal modules that should bypass the public checksum database.*

### When to Use What

| Situation                                   | Tool              | Purpose                                       |
| -------------------------------------------- | ---------------------- | -------------------------------------------- |
| Edit multiple modules simultaneously       | `go.work`    | Local cross-module development without publishing    |
| Build without network access          | `go mod vendor`        | Archive all dependencies locally      |
| Fetch internal corporate packages       | `GOPRIVATE`    | Skip public checksum DB for private repos           |
| Temporarily use a local fork          | `replace` directive    | Point to a local path or forked repo        |

**Why `go.work` instead of `replace`?** `replace` directives modify `go.mod`, which gets committed to version control and breaks other developers' builds. `go.work` stays local (`.gitignore`d) and does not affect the module file.

---

## 2. VISUAL

The decision tree is simple: local multi-module dev → `go.work`; offline builds → `vendor/`; private repos → `GOPRIVATE`. The visual below maps these three paths.

![Workspaces vendoring decision map](./images/02-workspaces-vendoring-decision-map.png)

*Figure: Decision map routing dependency scenarios to the correct tool: `go.work` for local dev, `vendor/` for offline builds, `GOPRIVATE` for internal modules.*

## 3. CODE

Four progression levels: workspace setup, vendoring, private modules, and `replace` directives.

### Example 1: Basic — Go Workspaces (Monorepo)

A monorepo with three modules: shared library, API service, and worker. `go.work` links them for simultaneous local development.

```bash
# Project structure:
my-project/
├── go.work           # workspace root
├── services/
│   ├── api/
│   │   ├── go.mod    # module: myproject/services/api
│   │   └── main.go
│   └── worker/
│       ├── go.mod    # module: myproject/services/worker
│       └── main.go
└── pkg/
    └── shared/
        ├── go.mod    # module: myproject/pkg/shared
        └── utils.go
```

```bash
# Initialize workspace
cd my-project
go work init ./services/api ./services/worker ./pkg/shared

# go.work (auto-generated):
go 1.22

use (
    ./services/api
    ./services/worker
    ./pkg/shared
)

# Now: all modules can import each other without versioning
# services/api can `import "myproject/pkg/shared"` directly
```

> **Takeaway**: `go.work` eliminates publish cycles during local development. Add it to `.gitignore` — it is a local-only tool.

---

### Example 2: Intermediate — Vendoring

Vendoring copies all dependencies into the project tree. Builds use only vendored code — no network required.

```bash
# Create vendor directory with all dependencies
go mod vendor

# Build using vendor (offline, reproducible)
go build -mod=vendor ./...

# Verify vendor matches go.sum
go mod verify
```

```
# vendor/ structure:
vendor/
├── github.com/
│   └── gin-gonic/
│       └── gin/
├── gorm.io/
│   └── gorm/
└── modules.txt         # dependency list
```

> **When to vendor?** Air-gapped environments, strict compliance requirements, or CI systems without internet access. For most projects, the module cache (`go mod download`) is sufficient.

> **Takeaway**: `go mod vendor` + `go build -mod=vendor` gives fully reproducible, offline builds.

---

### Example 3: Advanced — Private Modules

Internal corporate modules live behind authentication and should not be verified against the public checksum database.

```bash
# Tell Go to skip checksum DB for private modules
export GOPRIVATE=github.com/mycompany/*,gitlab.com/myorg/*

# Configure Git for private repos (SSH)
git config --global url."git@github.com:mycompany/".insteadOf "https://github.com/mycompany/"

# Or use GONOSUMDB + GOFLAGS
export GONOSUMDB=github.com/mycompany/*
```

> **Takeaway**: `GOPRIVATE` tells `go get` to skip the public proxy and checksum database. Combine with SSH-based Git config for seamless authentication.

---

### Example 4: Expert — Replace Directives

`replace` directives override module resolution in `go.mod`. Use for temporary local forks — but do not commit them to shared repos.

```go
// go.mod

module myapp

go 1.22

require (
    github.com/mycompany/shared-lib v1.2.0
)

// ✅ Local development: point to local copy
replace github.com/mycompany/shared-lib => ../shared-lib

// ✅ Fork: use forked repo
replace github.com/original/lib => github.com/myfork/lib v1.0.0-patched
```

> **Why handle `replace` carefully?** Committed `replace` directives break other developers' builds — the local path does not exist on their machines. Prefer `go.work` for local development.

> **Takeaway**: Use `replace` for quick local debugging. Use `go.work` for sustained multi-module development. Never commit `replace` directives pointing to local paths.

---

## 4. PITFALLS

The tools are straightforward. The traps below catch teams who commit `replace` directives or forget to update their vendor directory.

| # | Severity | Error | Consequence | Fix |
|---|----------|-----|---------|-----|
| 1 | 🔴 Fatal | Committing `replace` directives with local paths | Breaks builds for all other developers | Use `go.work` instead; add `go.work` to `.gitignore` |
| 2 | 🟡 Common | Stale `vendor/` directory after dependency updates | Builds use old dependency versions | Run `go mod vendor` after every `go get` |

---

## 5. REF

| Resource        | Type     | Link                                                                     | Description |
| --------------- | -------- | ------------------------------------------------------------------------ | ------- |
| Go Workspaces   | Official | [go.dev/doc/tutorial/workspaces](https://go.dev/doc/tutorial/workspaces) | Multi-module workspace tutorial |
| Go Modules      | Official | [go.dev/ref/mod](https://go.dev/ref/mod)                                 | Complete module and dependency reference |

---

## 6. RECOMMEND

The foundations of **Workspaces & Vendoring** are settled. The extension below connects back to module layout fundamentals.

| Extension | When | Why | File/Link |
| ------- | ------- | ----- | --------- |
| Modules & Layout | Project structure and `internal/` boundaries | Foundation for package organization | [01-modules-layout.md](./01-modules-layout.md) |

---

**Navigation**: [← Modules Layout](./01-modules-layout.md) · [→ Basics](../basics/01-syntax-variables.md)
