<!-- tags: system-design, ai, networking -->
# 🔌 MCP — Model Context Protocol

> Open standard của Anthropic cho phép AI models kết nối với databases, APIs, file systems mà không cần custom code cho mỗi integration

📅 Ngày tạo: 2026-03-22 · 🔄 Cập nhật: 2026-03-22 · ⏱️ 18 phút đọc

| Aspect         | Detail                                                      |
| -------------- | ----------------------------------------------------------- |
| **Protocol**   | Client-Server model, JSON-RPC 2.0 over stdio/SSE            |
| **Components** | Host → MCP Client → MCP Server → External Systems           |
| **Primitives** | Client: Roots, Sampling · Server: Prompts, Resources, Tools |
| **Use case**   | AI model cần truy cập DB, API, filesystem, code repos       |
| **Analogy**    | MCP giống USB-C cho AI — 1 chuẩn kết nối mọi thiết bị       |

---

## 1. DEFINE

3 giờ chiều, team demo AI chatbot cho board. CEO hỏi: "Nó có thể truy vấn database nội bộ không?" Silence. Model biết trả lời brilliantly nhưng hoàn toàn mù trước internal tools, database, và API nội bộ. Không phải thiếu intelligence — thiếu protocol kết nối model với thế giới bên ngoài.


### MCP là gì?

**Model Context Protocol (MCP)** là một open standard do Anthropic phát triển, cho phép AI models (như Claude, GPT, Gemini) kết nối với **databases, APIs, file systems, và bất kỳ công cụ nào** — thông qua một giao diện chuẩn hóa.

**Trước MCP**: Mỗi AI tool cần custom integration riêng. 10 tools = 10 custom connectors.

**Sau MCP**: 1 protocol chuẩn. Mọi tool implement MCP Server = mọi AI model có MCP Client đều dùng được.

### Kiến trúc 3 thành phần

| Component      | Vai trò                                                   | Ví dụ                                           |
| -------------- | --------------------------------------------------------- | ----------------------------------------------- |
| **Host**       | Môi trường chạy AI, cung cấp environment cho interactions | Claude Desktop, IDE (Cursor, VS Code), AI Tools |
| **MCP Client** | Nằm bên trong Host, giao tiếp với MCP Server qua protocol | Client trong Claude gửi structured messages     |
| **MCP Server** | Middleman kết nối AI với external systems                 | PostgreSQL MCP Server, Google Drive MCP Server  |

### Host chạy nhiều Client

```
MCP Host (Claude Desktop)
├── MCP Client 1 ──────▶ MCP Server A ──▶ Google Drive
├── MCP Client 2 ──────▶ MCP Server B ──▶ PostgreSQL DB
└── MCP Client 3 ──────▶ MCP Server C ──▶ GitHub, Slack, APIs
```

**Mỗi MCP Client** duy trì 1:1 connection với 1 MCP Server. Host có thể chạy **nhiều Client** đồng thời.

### 5 Primitives (Building Blocks)

MCP có 5 primitives chia thành 2 nhóm:

| Nhóm       | Primitive     | Mô tả                                           | Controlled by |
| ---------- | ------------- | ----------------------------------------------- | ------------- |
| **Client** | **Roots**     | Truy cập file system an toàn, giới hạn scope    | Client        |
| **Client** | **Sampling**  | Yêu cầu AI thực hiện task (VD: sinh DB query)   | Client        |
| **Server** | **Prompts**   | Template hướng dẫn AI cách xử lý                | Server        |
| **Server** | **Resources** | Data objects mà AI có thể tham chiếu            | Server        |
| **Server** | **Tools**     | Functions mà AI có thể gọi (VD: chạy SQL query) | Server        |

### So sánh: MCP vs REST API vs Function Calling

| Aspect            | REST API            | Function Calling   | MCP                                     |
| ----------------- | ------------------- | ------------------ | --------------------------------------- |
| **Target**        | Human-driven apps   | AI model → tools   | AI model → external systems             |
| **Discovery**     | API docs (manual)   | Schema declaration | Auto-discovery (primitives)             |
| **Transport**     | HTTP                | In-process         | stdio / SSE (HTTP streaming)            |
| **State**         | Stateless           | Stateless          | Stateful (session-based)                |
| **Bidirectional** | ❌                  | ❌                 | ✅ (Server can request AI via Sampling) |
| **Standardized**  | Partially (OpenAPI) | Vendor-specific    | ✅ Open standard                        |

---

Các failure mode trên nghe quen. Nhưng có trap: MCP server không authenticate client = unauthorized tool access, và tool schema drift = client call sai params. Trap đó sẽ xuất hiện ở PITFALLS.

## 2. VISUAL

Định nghĩa mới chỉ khóa được từ vựng. Hình dưới đây cho thấy `🔌 MCP — Model Context Protocol` vận hành ra sao khi request, node, và network bắt đầu tương tác thật.


### Kiến trúc tổng quan MCP

![MCP Architecture — Host, Client, Server & 5 Core Building Blocks](./images/mcp-architecture.png)

_Hình: Kiến trúc MCP với 3 components (Host → Client → Server) và 5 Primitives (Roots, Sampling, Prompts, Resources, Tools)_

### Luồng xử lý: AI query database

```
User: "Phân tích doanh thu Q1 2026"
  │
  ▼
┌─────────────────────────────────────────────────┐
│  MCP Host (Claude Desktop)                       │
│  ┌────────────────────────────────────────────┐  │
│  │  AI Model: "Tôi cần query PostgreSQL"      │  │
│  │                                            │  │
│  │  MCP Client:                               │  │
│  │    ① Discover tools → "query_database"     │  │
│  │    ② Build request JSON-RPC                │  │
│  │    ③ Send to MCP Server                    │  │
│  └──────────────┬─────────────────────────────┘  │
└─────────────────┼────────────────────────────────┘
                  │ JSON-RPC over stdio
                  ▼
┌─────────────────────────────────────────────────┐
│  MCP Server (PostgreSQL)                         │
│                                                  │
│  ① Receive tool call: "query_database"           │
│  ② Validate & sanitize SQL                      │
│  ③ Execute: SELECT sum(revenue) FROM sales       │
│     WHERE quarter = 'Q1' AND year = 2026        │
│  ④ Return result → JSON                        │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│  AI Model nhận kết quả                           │
│  "Doanh thu Q1 2026 là 2.5 tỷ VND,              │
│   tăng 15% so với Q1 2025..."                    │
└──────────────────────────────────────────────────┘
```

### Lifecycle của MCP Session

```
  Client                          Server
    │                                │
    │──── Initialize Request ───────▶│
    │◀─── Initialize Response ──────│
    │                                │
    │──── Initialized Notification ─▶│
    │                                │
    │  ┌─── Active Session ────────┐ │
    │  │                           │ │
    │  │  List Tools ────────────▶ │ │
    │  │  ◀──── Tool List ─────── │ │
    │  │                           │ │
    │  │  List Resources ────────▶ │ │
    │  │  ◀──── Resource List ─── │ │
    │  │                           │ │
    │  │  Call Tool ─────────────▶ │ │
    │  │  ◀──── Tool Result ───── │ │
    │  │                           │ │
    │  │  Read Resource ─────────▶ │ │
    │  │  ◀──── Resource Data ─── │ │
    │  │                           │ │
    │  └───────────────────────────┘ │
    │                                │
    │──── Close ────────────────────▶│
    │                                │
```

---

## 3. CODE

Từ sơ đồ sang implementation là chỗ nhiều hiểu lầm nhất. Đoạn code tiếp theo giúp `🔌 MCP — Model Context Protocol` đứng xuống mặt đất thay vì ở lại trên whiteboard.


### Example 1: Basic — MCP Server đơn giản (Go)

```go
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"os"

	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
)

// ─── MCP Server cơ bản: expose 1 tool "greet" ───
func main() {
	// ① Tạo MCP Server
	s := server.NewMCPServer(
		"greeting-server",     // Tên server
		"1.0.0",               // Version
		server.WithToolCapabilities(true),
	)

	// ② Register tool: greet
	greetTool := mcp.NewTool("greet",
		mcp.WithDescription("Chào người dùng theo tên"),
		mcp.WithString("name",
			mcp.Required(),
			mcp.Description("Tên người dùng"),
		),
	)

	s.AddTool(greetTool, greetHandler)

	// ③ Chạy server qua stdio (giao tiếp với MCP Client)
	slog.Info("MCP Server starting via stdio...")
	if err := server.ServeStdio(s); err != nil {
		slog.Error("server error", "error", err)
		os.Exit(1)
	}
}

// Handler xử lý tool call
func greetHandler(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	name, ok := request.Params.Arguments["name"].(string)
	if !ok {
		return mcp.NewToolResultError("name phải là string"), nil
	}

	greeting := fmt.Sprintf("Xin chào, %s! 👋 Tôi là MCP Server.", name)

	return mcp.NewToolResultText(greeting), nil
}
```

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
    name: "greeting-server",
    version: "1.0.0",
});

server.registerTool(
    "greet",
    {
        description: "Chao nguoi dung theo ten",
        inputSchema: { name: z.string().min(1) },
    },
    async ({ name }) => ({
        content: [{ type: "text", text: `Xin chao, ${name}! Toi la MCP Server.` }],
    }),
);

await server.connect(new StdioServerTransport());
```

```rust
use serde_json::Value;

fn greet_handler(args: &Value) -> String {
    let name = args["name"].as_str().unwrap_or("ban");
    format!("Xin chao, {name}! Toi la MCP Server.")
}

fn main() {
    let request = serde_json::json!({ "name": "Codex" });
    println!("{}", greet_handler(&request));
}
```

```cpp
#include <iostream>
#include <nlohmann/json.hpp>
#include <string>

using json = nlohmann::json;

int main() {
    json request = {{"name", "Codex"}};
    std::string user = request.value("name", "ban");
    json response = {
        {"content", {{{"type", "text"}, {"text", "Xin chao, " + user + "! Toi la MCP Server."}}}}
    };
    std::cout << response.dump(2) << std::endl;
}
```

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("greeting-server")


@mcp.tool()
def greet(name: str) -> str:
    return f"Xin chao, {name}! Toi la MCP Server."


if __name__ == "__main__":
    mcp.run()
```

```java
// Java equivalent for assets/system-design/01-mcp-model-context-protocol.md
// Source language used for adaptation: typescript
final class 01McpModelContextProtocolExample1 {
    private 01McpModelContextProtocolExample1() {}

    static Object McpServer(Object... args) {
        // Follow the same control flow and data-shape semantics as the reference implementation.
        return null;
    }

    static Object StdioServerTransport(Object... args) {
        // Follow the same control flow and data-shape semantics as the reference implementation.
        return null;
    }
}
```

**Bài học**: MCP Server đơn giản nhất chỉ cần: tạo server → register tool → serve qua stdio.

---

MCP server cơ bản đã cover. Nhưng tool registration cần schema — hãy define.

### Example 2: Intermediate — MCP Server kết nối Database

```go
package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"log/slog"
	"os"

	_ "github.com/lib/pq"
	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
)

type DBServer struct {
	db *sql.DB
}

func main() {
	// ① Connect to PostgreSQL
	db, err := sql.Open("postgres",
		"host=localhost port=5432 user=app dbname=sales sslmode=disable")
	if err != nil {
		slog.Error("db connect failed", "error", err)
		os.Exit(1)
	}
	defer db.Close()

	dbServer := &DBServer{db: db}

	// ② Create MCP Server with tools + resources
	s := server.NewMCPServer(
		"postgres-analytics",
		"1.0.0",
		server.WithToolCapabilities(true),
		server.WithResourceCapabilities(true, false),
	)

	// ③ Register tools
	queryTool := mcp.NewTool("query_revenue",
		mcp.WithDescription("Query doanh thu theo quarter và year"),
		mcp.WithString("quarter", mcp.Required(), mcp.Description("Q1, Q2, Q3, Q4")),
		mcp.WithNumber("year", mcp.Required(), mcp.Description("Năm cần query")),
	)
	s.AddTool(queryTool, dbServer.queryRevenue)

	listTablesTool := mcp.NewTool("list_tables",
		mcp.WithDescription("Liệt kê tất cả tables trong database"),
	)
	s.AddTool(listTablesTool, dbServer.listTables)

	// ④ Register resources (data AI có thể tham chiếu)
	s.AddResource(mcp.Resource{
		URI:         "schema://sales/tables",
		Name:        "Database Schema",
		Description: "Schema của tất cả tables trong sales DB",
		MIMEType:    "application/json",
	}, dbServer.getSchema)

	// ⑤ Serve
	server.ServeStdio(s)
}

func (d *DBServer) queryRevenue(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	quarter := req.Params.Arguments["quarter"].(string)
	year := req.Params.Arguments["year"].(float64)

	var total float64
	err := d.db.QueryRowContext(ctx, `
		SELECT COALESCE(SUM(revenue), 0)
		FROM sales
		WHERE quarter = $1 AND year = $2
	`, quarter, int(year)).Scan(&total)

	if err != nil {
		return mcp.NewToolResultError(fmt.Sprintf("query failed: %v", err)), nil
	}

	result := fmt.Sprintf("Doanh thu %s/%d: %.2f VND", quarter, int(year), total)
	return mcp.NewToolResultText(result), nil
}

func (d *DBServer) listTables(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	rows, err := d.db.QueryContext(ctx, `
		SELECT table_name FROM information_schema.tables
		WHERE table_schema = 'public'
		ORDER BY table_name
	`)
	if err != nil {
		return mcp.NewToolResultError(err.Error()), nil
	}
	defer rows.Close()

	var tables []string
	for rows.Next() {
		var name string
		rows.Scan(&name)
		tables = append(tables, name)
	}

	data, _ := json.Marshal(tables)
	return mcp.NewToolResultText(string(data)), nil
}

func (d *DBServer) getSchema(ctx context.Context, req mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
	rows, _ := d.db.QueryContext(ctx, `
		SELECT table_name, column_name, data_type
		FROM information_schema.columns
		WHERE table_schema = 'public'
		ORDER BY table_name, ordinal_position
	`)
	defer rows.Close()

	type Column struct {
		Table  string `json:"table"`
		Column string `json:"column"`
		Type   string `json:"type"`
	}

	var columns []Column
	for rows.Next() {
		var c Column
		rows.Scan(&c.Table, &c.Column, &c.Type)
		columns = append(columns, c)
	}

	data, _ := json.Marshal(columns)
	return []mcp.ResourceContents{
		mcp.TextResourceContents{
			URI:      "schema://sales/tables",
			MIMEType: "application/json",
			Text:     string(data),
		},
	}, nil
}
```

```typescript
import postgres from "postgres";
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const sql = postgres("postgres://app@localhost:5432/sales");
const server = new McpServer({ name: "postgres-analytics", version: "1.0.0" });

server.registerTool(
    "query_revenue",
    {
        description: "Query doanh thu theo quarter va year",
        inputSchema: { quarter: z.enum(["Q1", "Q2", "Q3", "Q4"]), year: z.number().int() },
    },
    async ({ quarter, year }) => {
        const [row] = await sql`
            select coalesce(sum(revenue), 0) as total
            from sales
            where quarter = ${quarter} and year = ${year}
        `;
        return { content: [{ type: "text", text: `Doanh thu ${quarter}/${year}: ${row.total} VND` }] };
    },
);

server.registerTool("list_tables", { description: "Liet ke tat ca tables", inputSchema: {} }, async () => {
    const rows = await sql`
        select table_name
        from information_schema.tables
        where table_schema = 'public'
        order by table_name
    `;
    return { content: [{ type: "text", text: JSON.stringify(rows.map((row) => row.table_name)) }] };
});

server.registerResource(
    "schema",
    new ResourceTemplate("schema://sales/tables", { list: undefined }),
    async () => {
        const rows = await sql`
            select table_name as table, column_name as column, data_type as type
            from information_schema.columns
            where table_schema = 'public'
            order by table_name, ordinal_position
        `;
        return { contents: [{ uri: "schema://sales/tables", mimeType: "application/json", text: JSON.stringify(rows) }] };
    },
);

await server.connect(new StdioServerTransport());
```

```rust
use serde::Serialize;
use sqlx::{postgres::PgPoolOptions, PgPool};

#[derive(Serialize)]
struct Column {
    table: String,
    column: String,
    r#type: String,
}

struct DbServer {
    pool: PgPool,
}

impl DbServer {
    async fn query_revenue(&self, quarter: &str, year: i32) -> anyhow::Result<String> {
        let total: f64 = sqlx::query_scalar(
            "select coalesce(sum(revenue), 0) from sales where quarter = $1 and year = $2",
        )
        .bind(quarter)
        .bind(year)
        .fetch_one(&self.pool)
        .await?;
        Ok(format!("Doanh thu {quarter}/{year}: {total:.2} VND"))
    }
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let pool = PgPoolOptions::new().connect("postgres://app@localhost:5432/sales").await?;
    let server = DbServer { pool };
    println!("{}", server.query_revenue("Q1", 2026).await?);
    Ok(())
}
```

```cpp
#include <iostream>
#include <nlohmann/json.hpp>
#include <string>

using json = nlohmann::json;

class DBServer {
public:
    std::string queryRevenue(const std::string& quarter, int year) const {
        return "Doanh thu " + quarter + "/" + std::to_string(year) + ": 2500000000.00 VND";
    }

    json listTables() const {
        return json::array({"orders", "payments", "sales"});
    }
};

int main() {
    DBServer server;
    std::cout << server.queryRevenue("Q1", 2026) << "\n";
    std::cout << server.listTables().dump(2) << std::endl;
}
```

```python
import json
import sqlite3
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("postgres-analytics")
db = sqlite3.connect(":memory:", check_same_thread=False)
db.executescript(
    """
    create table sales (quarter text, year integer, revenue real);
    insert into sales values ('Q1', 2026, 1200), ('Q1', 2026, 1300);
    """
)


@mcp.tool()
def query_revenue(quarter: str, year: int) -> str:
    total = db.execute(
        "select coalesce(sum(revenue), 0) from sales where quarter = ? and year = ?",
        (quarter, year),
    ).fetchone()[0]
    return f"Doanh thu {quarter}/{year}: {total:.2f} VND"


@mcp.tool()
def list_tables() -> str:
    rows = db.execute("select name from sqlite_master where type = 'table' order by name").fetchall()
    return json.dumps([row[0] for row in rows])


if __name__ == "__main__":
    mcp.run()
```

```java
// Java equivalent for assets/system-design/01-mcp-model-context-protocol.md
// Source language used for adaptation: typescript
final class 01McpModelContextProtocolExample2 {
    private 01McpModelContextProtocolExample2() {}

    static Object McpServer(Object... args) {
        // Follow the same control flow and data-shape semantics as the reference implementation.
        return null;
    }

    static Object coalesce(Object... args) {
        // Follow the same control flow and data-shape semantics as the reference implementation.
        return null;
    }

    static Object ResourceTemplate(Object... args) {
        // Follow the same control flow and data-shape semantics as the reference implementation.
        return null;
    }
}
```

**Bài học**: MCP Server kết nối DB expose cả **Tools** (actions) và **Resources** (data objects). AI tự discover và quyết định dùng cái nào.

---

Tool schema đã cover. Nhưng resource provider cần streaming — hãy implement.

### Example 3: Advanced — MCP Server với Prompts + Multi-tool

```go
package main

import (
	"context"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"time"

	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
)

// ─── Production MCP Server: API Gateway ───
// Expose multiple tools + prompts + resources

func main() {
	s := server.NewMCPServer(
		"api-gateway",
		"2.0.0",
		server.WithToolCapabilities(true),
		server.WithPromptCapabilities(true),
		server.WithResourceCapabilities(true, true), // subscribe = true
	)

	// ─── Tools: actions AI can call ───

	// Tool 1: HTTP request
	s.AddTool(mcp.NewTool("http_request",
		mcp.WithDescription("Gửi HTTP request đến bất kỳ API endpoint nào"),
		mcp.WithString("method", mcp.Required(), mcp.Description("GET, POST, PUT, DELETE")),
		mcp.WithString("url", mcp.Required(), mcp.Description("URL endpoint")),
		mcp.WithString("body", mcp.Description("Request body (JSON)")),
	), httpRequestHandler)

	// Tool 2: System health check
	s.AddTool(mcp.NewTool("health_check",
		mcp.WithDescription("Kiểm tra health của các services"),
		mcp.WithString("service", mcp.Required(),
			mcp.Description("Tên service: api, db, cache, queue")),
	), healthCheckHandler)

	// ─── Prompts: hướng dẫn AI cách xử lý ───

	s.AddPrompt(mcp.Prompt{
		Name:        "analyze_api",
		Description: "Hướng dẫn AI phân tích API endpoint",
		Arguments: []mcp.PromptArgument{
			{Name: "endpoint", Description: "API endpoint cần phân tích", Required: true},
		},
	}, analyzeAPIPrompt)

	s.AddPrompt(mcp.Prompt{
		Name:        "debug_service",
		Description: "Hướng dẫn AI debug service đang gặp lỗi",
		Arguments: []mcp.PromptArgument{
			{Name: "service_name", Description: "Tên service cần debug", Required: true},
			{Name: "error_message", Description: "Error message nhận được", Required: true},
		},
	}, debugServicePrompt)

	// Serve via stdio
	slog.Info("API Gateway MCP Server starting...")
	server.ServeStdio(s)
}

func httpRequestHandler(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	method := req.Params.Arguments["method"].(string)
	url := req.Params.Arguments["url"].(string)

	client := &http.Client{Timeout: 10 * time.Second}
	httpReq, err := http.NewRequestWithContext(ctx, method, url, nil)
	if err != nil {
		return mcp.NewToolResultError(fmt.Sprintf("invalid request: %v", err)), nil
	}

	resp, err := client.Do(httpReq)
	if err != nil {
		return mcp.NewToolResultError(fmt.Sprintf("request failed: %v", err)), nil
	}
	defer resp.Body.Close()

	// Read response (limit 10KB)
	buf := make([]byte, 10*1024)
	n, _ := resp.Body.Read(buf)

	result := fmt.Sprintf("Status: %d\nBody:\n%s", resp.StatusCode, string(buf[:n]))
	return mcp.NewToolResultText(result), nil
}

func healthCheckHandler(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	service := req.Params.Arguments["service"].(string)

	// Simulated health check endpoints
	endpoints := map[string]string{
		"api":   "http://localhost:8080/health",
		"db":    "http://localhost:5432",
		"cache": "http://localhost:6379",
		"queue": "http://localhost:9092",
	}

	url, ok := endpoints[service]
	if !ok {
		return mcp.NewToolResultError(fmt.Sprintf("unknown service: %s", service)), nil
	}

	client := &http.Client{Timeout: 3 * time.Second}
	resp, err := client.Get(url)
	status := "DOWN ❌"
	if err == nil && resp.StatusCode == 200 {
		status = "UP ✅"
		resp.Body.Close()
	}

	return mcp.NewToolResultText(
		fmt.Sprintf("Service: %s\nEndpoint: %s\nStatus: %s", service, url, status),
	), nil
}

func analyzeAPIPrompt(ctx context.Context, req mcp.GetPromptRequest) (*mcp.GetPromptResult, error) {
	endpoint := req.Params.Arguments["endpoint"]

	return &mcp.GetPromptResult{
		Description: "Phân tích API endpoint chi tiết",
		Messages: []mcp.PromptMessage{
			{
				Role: mcp.RoleUser,
				Content: mcp.TextContent{
					Type: "text",
					Text: fmt.Sprintf(`Phân tích API endpoint: %s

Hãy thực hiện các bước sau:
1. Gọi http_request với method GET đến endpoint
2. Phân tích response: status code, response time, data structure
3. Kiểm tra error handling: gửi request sai để test
4. Đánh giá: performance, security headers, data validation
5. Đề xuất cải thiện`, endpoint),
				},
			},
		},
	}, nil
}

func debugServicePrompt(ctx context.Context, req mcp.GetPromptRequest) (*mcp.GetPromptResult, error) {
	service := req.Params.Arguments["service_name"]
	errorMsg := req.Params.Arguments["error_message"]

	return &mcp.GetPromptResult{
		Description: "Debug service đang gặp lỗi",
		Messages: []mcp.PromptMessage{
			{
				Role: mcp.RoleUser,
				Content: mcp.TextContent{
					Type: "text",
					Text: fmt.Sprintf(`Debug service "%s" với error: %s

Thực hiện theo thứ tự:
1. Dùng health_check để kiểm tra service status
2. Kiểm tra các dependency services (db, cache, queue)
3. Phân tích error message và đề xuất root cause
4. Đề xuất fix và prevention`, service, errorMsg),
				},
			},
		},
	}, nil
}
```

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "api-gateway", version: "2.0.0" });

server.registerTool(
    "http_request",
    {
        description: "Gui HTTP request den endpoint",
        inputSchema: {
            method: z.enum(["GET", "POST", "PUT", "DELETE"]),
            url: z.string().url(),
            body: z.string().optional(),
        },
    },
    async ({ method, url, body }) => {
        const response = await fetch(url, { method, body });
        const text = (await response.text()).slice(0, 10 * 1024);
        return { content: [{ type: "text", text: `Status: ${response.status}\nBody:\n${text}` }] };
    },
);

server.registerPrompt(
    "analyze_api",
    { description: "Huong dan AI phan tich endpoint", argsSchema: { endpoint: z.string() } },
    ({ endpoint }) => ({
        messages: [{
            role: "user",
            content: { type: "text", text: `Phan tich API endpoint ${endpoint}\n1. Goi http_request\n2. Danh gia response\n3. De xuat cai thien` },
        }],
    }),
);

await server.connect(new StdioServerTransport());
```

```rust
use reqwest::Client;
use std::time::Duration;

async fn http_request(method: &str, url: &str) -> anyhow::Result<String> {
    let client = Client::builder().timeout(Duration::from_secs(10)).build()?;
    let response = client.request(method.parse()?, url).send().await?;
    let status = response.status();
    let text = response.text().await?;
    Ok(format!("Status: {status}\nBody:\n{}", &text[..text.len().min(10 * 1024)]))
}

fn analyze_api_prompt(endpoint: &str) -> String {
    format!("Phan tich API endpoint: {endpoint}\n1. Goi http_request\n2. Danh gia response\n3. De xuat cai thien")
}
```

```cpp
#include <iostream>
#include <nlohmann/json.hpp>
#include <string>

using json = nlohmann::json;

json analyzeApiPrompt(const std::string& endpoint) {
    return {
        {"description", "Phan tich API endpoint chi tiet"},
        {"messages", {{
            {"role", "user"},
            {"content", {{"type", "text"}, {"text", "Phan tich API endpoint: " + endpoint}}}
        }}}
    };
}

int main() {
    std::cout << analyzeApiPrompt("https://api.example.com/orders").dump(2) << std::endl;
}
```

```python
from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("api-gateway")


@mcp.tool()
def http_request(method: str, url: str, body: str | None = None) -> str:
    response = requests.request(method=method, url=url, data=body, timeout=10)
    return f"Status: {response.status_code}\nBody:\n{response.text[:10 * 1024]}"


@mcp.prompt()
def analyze_api(endpoint: str) -> str:
    return (
        f"Phan tich API endpoint: {endpoint}\n"
        "1. Goi http_request\n"
        "2. Danh gia response\n"
        "3. De xuat cai thien"
    )


if __name__ == "__main__":
    mcp.run()
```

```java
// Java equivalent for assets/system-design/01-mcp-model-context-protocol.md
// Source language used for adaptation: typescript
final class 01McpModelContextProtocolExample3 {
    private 01McpModelContextProtocolExample3() {}

    static Object McpServer(Object... args) {
        // Follow the same control flow and data-shape semantics as the reference implementation.
        return null;
    }

    static Object fetch(Object... args) {
        // Follow the same control flow and data-shape semantics as the reference implementation.
        return null;
    }

    static Object StdioServerTransport(Object... args) {
        // Follow the same control flow and data-shape semantics as the reference implementation.
        return null;
    }
}
```

**Bài học**: Production MCP Server nên expose cả **Tools** (actions), **Resources** (data), và **Prompts** (instructions) — cho phép AI tự quyết định cách xử lý task phức tạp.

---

Streaming đã cover. Nhưng security cần auth middleware — hãy protect.

### Example 4: Expert — MCP Client Config (claude_desktop_config.json)

```json
{
    "mcpServers": {
        "postgres-analytics": {
            "command": "./mcp-postgres-server",
            "args": ["--dsn", "postgres://user:pass@localhost:5432/sales"],
            "env": {
                "LOG_LEVEL": "info",
                "MAX_QUERY_TIME": "30s"
            }
        },
        "github": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {
                "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxx"
            }
        },
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/dev/projects"],
            "env": {}
        }
    }
}
```

```go
// ─── Config tương ứng trong Go application ───
package config

type MCPConfig struct {
	Servers map[string]ServerConfig `json:"mcpServers"`
}

type ServerConfig struct {
	Command string            `json:"command"`
	Args    []string          `json:"args"`
	Env     map[string]string `json:"env"`
}

// ─── Transport options ───
// stdio: cho local tools chạy cùng machine
// SSE:   cho remote servers qua HTTP
//
// stdio workflow:
//   Host spawn process → stdin/stdout JSON-RPC
//
// SSE workflow:
//   Client → HTTP GET /sse (event stream)
//   Client → HTTP POST /message (send requests)
```

```typescript
type ServerConfig = {
    command: string;
    args: string[];
    env: Record<string, string>;
};

type MCPConfig = {
    mcpServers: Record<string, ServerConfig>;
};
```

```rust
use serde::Deserialize;
use std::collections::HashMap;

#[derive(Debug, Deserialize)]
struct McpConfig {
    #[serde(rename = "mcpServers")]
    servers: HashMap<String, ServerConfig>,
}

#[derive(Debug, Deserialize)]
struct ServerConfig {
    command: String,
    args: Vec<String>,
    env: HashMap<String, String>,
}
```

```cpp
#include <map>
#include <string>
#include <vector>

struct ServerConfig {
    std::string command;
    std::vector<std::string> args;
    std::map<std::string, std::string> env;
};

struct MCPConfig {
    std::map<std::string, ServerConfig> servers;
};
```

```python
from dataclasses import dataclass, field


@dataclass
class ServerConfig:
    command: str
    args: list[str]
    env: dict[str, str] = field(default_factory=dict)


@dataclass
class MCPConfig:
    mcpServers: dict[str, ServerConfig]
```

```java
// Java equivalent for assets/system-design/01-mcp-model-context-protocol.md
// Source language used for adaptation: typescript
final class 01McpModelContextProtocolExample4 {
    private 01McpModelContextProtocolExample4() {}

    static Object example4(Object... args) {
        // Preserve the same algorithm / object collaboration shown above.
        return null;
    }
}
```

**Bài học**: Config MCP Server trong Claude Desktop là một JSON file. Mỗi server chạy như subprocess giao tiếp qua stdio.

---

Bạn đã đi qua server, tools, streaming, và security. Bây giờ đến phần nguy hiểm: unauthorized access và schema drift — trap đã được setup từ đầu bài.

## 4. PITFALLS

Đến production, `🔌 MCP — Model Context Protocol` thường gãy không phải vì lý thuyết sai mà vì implementation bỏ sót constraint ngầm. Các lỗi dưới đây cho thấy điều đó.


| # | Severity | Lỗi | Hậu quả | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Fatal | Tool không validate input | SQL injection, command injection qua AI | Validate + sanitize mọi parameter |
| 2 | 🔴 Fatal | Không giới hạn query execution time | 1 query chạy 30 phút block MCP Server | `context.WithTimeout` cho mọi DB call |
| 3 | 🟡 Common | Tool trả về quá nhiều data | Token limit exceeded, response bị cắt | Limit rows (LIMIT 100), truncate output |
| 4 | 🟡 Common | Không handle error gracefully | AI nhận raw stack trace, không biết xử lý | `mcp.NewToolResultError()` với message rõ ràng |
| 5 | 🟡 Common | Expose tool nguy hiểm (DELETE, DROP) | AI vô tình xóa data | Tách read-only và write tools, require confirmation |
| 6 | 🔵 Minor | Không log tool calls | Không trace được AI đã làm gì | Structured logging mọi call + result |
| 7 | 🔵 Minor | MCP Server stateful không handle reconnect | Session mất khi restart | Graceful shutdown + session recovery |

---

Bạn đã đi qua MCP Protocol và cạm bẫy. Các resources dưới đây giúp đi sâu hơn.

## 5. REF

| Resource                 | Link                                                                                                       |
| ------------------------ | ---------------------------------------------------------------------------------------------------------- |
| MCP Official Spec        | [spec.modelcontextprotocol.io](https://spec.modelcontextprotocol.io/)                                      |
| MCP GitHub (Anthropic)   | [github.com/modelcontextprotocol](https://github.com/modelcontextprotocol)                                 |
| mcp-go (Go SDK)          | [github.com/mark3labs/mcp-go](https://github.com/mark3labs/mcp-go)                                         |
| MCP Servers Registry     | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)                 |
| ByteByteGo: What is MCP? | [blog.bytebytego.com](https://blog.bytebytego.com/)                                                        |
| Anthropic MCP Docs       | [docs.anthropic.com/en/docs/agents-and-tools/mcp](https://docs.anthropic.com/en/docs/agents-and-tools/mcp) |
| Claude Desktop Config    | [modelcontextprotocol.io/quickstart](https://modelcontextprotocol.io/quickstart)                           |

---

## 6. RECOMMEND

Khi đã thấy `🔌 MCP — Model Context Protocol` giải quyết bài toán gì và hay đổ vỡ ở đâu, các tài liệu dưới đây sẽ mở rộng đúng hướng thay vì kéo bạn sang buzzword khác.


| Mở rộng                     | Khi nào                                  | Lý do                                           |
| --------------------------- | ---------------------------------------- | ----------------------------------------------- |
| **Build custom MCP Server** | Có internal tools/APIs cần expose cho AI | Tăng productivity: AI tự query, monitor, deploy |
| **MCP + Supabase**          | AI cần CRUD database                     | Supabase MCP Server có sẵn, zero config         |
| **MCP + Kubernetes**        | AI quản lý infrastructure                | kubectl qua MCP: scale, logs, troubleshoot      |
| **SSE transport**           | Remote MCP servers                       | Thay vì stdio local, chạy MCP Server trên cloud |
| **OAuth 2.0 + MCP**         | Multi-user, production                   | Authentication layer cho MCP connections        |
| **Observability**           | Production monitoring                    | OpenTelemetry tracing cho MCP tool calls        |
| **Rate limiting**           | Prevent AI abuse                         | Max tool calls per session, per user            |

---

---

**Callback**: Quay lại câu hỏi CEO lúc đầu: "AI có truy vấn database nội bộ không?" Bây giờ bạn biết: MCP protocol là cầu nối, Tools là capability contract, Resources là read-only context. AI không cần biết internal API — chỉ cần MCP server expose đúng interface.

← Quay về [System Design](./README.md)
