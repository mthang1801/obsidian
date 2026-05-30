import os
import re

GLOSARIES_DIR = "/home/mvt/mAIvt/Documents/glosaries"
SQL_DIR = "/home/mvt/mAIvt/Documents/sql"
GO_DIR = "/home/mvt/mAIvt/Documents/go"
OUTPUT_FILE = "/home/mvt/mAIvt/scripts/glossary.txt"

def clean_term(term):
    # Strip prefix numbers (e.g. 01-technical-debt -> technical-debt)
    term = re.sub(r'^[0-9]+-', '', term)
    # Replace dashes and underscores with spaces
    term = term.replace("-", " ").replace("_", " ")
    # Clean whitespace
    term = " ".join(term.split())
    return term

def scan_folders():
    terms = set()
    
    # 1. Scan glosaries filenames and folder names
    if os.path.exists(GLOSARIES_DIR):
        for root, dirs, files in os.walk(GLOSARIES_DIR):
            for d in dirs:
                if d != "images":
                    terms.add(clean_term(d))
            for f in files:
                if f.endswith(".md") and f != "README.md":
                    name = f[:-3] # strip .md
                    terms.add(clean_term(name))
                    
    # 2. Add structural terms from SQL & Go docs
    for folder in [SQL_DIR, GO_DIR]:
        if os.path.exists(folder):
            for root, dirs, files in os.walk(folder):
                for d in dirs:
                    if d != "images":
                        terms.add(clean_term(d))
                for f in files:
                    if f.endswith(".md") and f != "README.md":
                        name = f[:-3]
                        terms.add(clean_term(name))
                        
    # 3. Exhaustive manually curated list of Go, GORM, DB, SQL, and System Design keywords
    custom_keywords = [
        # Severity badges with emojis
        "🔴 Fatal", "🔴 Critical", "🟡 Common", "🟡 Warning", "🔵 Minor",
        "Fatal", "Critical", "Common", "Warning", "Minor",
        
        # Concurrency & Multithreading
        "goroutine", "goroutines", "goroutine leakage", "goroutine leak", "goroutine leaks",
        "channel", "channels", "buffered channel", "unbuffered channel", "select", "select statement",
        "mutex", "mutexes", "rwmutex", "sync", "sync.Mutex", "sync.RWMutex", "sync.WaitGroup",
        "waitgroup", "waitgroups", "once", "sync.Once", "cond", "sync.Cond", "pool", "sync.Pool",
        "map", "sync.Map", "atomic", "sync/atomic", "race condition", "race conditions", "data race",
        "thread-safe", "thread safety", "concurrency", "parallelism", "context", "contexts",
        "context cancellation", "context timeout", "context deadline", "withcancel", "withtimeout",
        "withdeadline", "withvalue", "semaphore", "semaphores", "worker pool", "worker pools",
        
        # Database & GORM specific
        "orm", "gorm", "gorm.Model", "gorm.Config", "automigrate", "automigration", "migration",
        "migrations", "migrator", "migrators", "golang-migrate", "goose", "atlas", "schema",
        "schemas", "schema drift", "schema drifts", "connection pool", "connection pools",
        "maxopenconns", "maxidleconns", "connmaxlifetime", "connmaxidletime", "read splitted",
        "read-write splitting", "read splitting", "write splitting", "replica", "replicas",
        "primary database", "replica database", "dbresolver", "resolver", "resolvers",
        "soft delete", "soft deletes", "hard delete", "hard deletes", "deletedat", "unscoped",
        "preload", "preloading", "joins", "association", "associations", "has one", "has many",
        "belongs to", "many to many", "foreign key", "foreign keys", "primary key", "primary keys",
        "composite key", "composite keys", "index", "indexes", "indices", "unique index",
        "unique indexes", "composite index", "composite indexes", "transaction", "transactions",
        "nested transaction", "nested transactions", "savepoint", "savepoints", "rollback",
        "commit", "upsert", "onconflict", "clause.OnConflict", "row locking", "row locks",
        "pessimistic locking", "optimistic locking", "for update", "for share", "version column",
        "prepared statement", "prepared statements", "preparestmt", "sql injection", "sql injections",
        "raw sql", "sql builder", "dryrun", "singletable", "table per class", "table per concrete class",
        "polymorphic", "polymorphic association", "polymorphic associations",
        
        # SQL Operations & Querying
        "select clause", "where clause", "order by", "group by", "having clause", "limit", "offset",
        "pagination", "offset pagination", "keyset pagination", "cursor pagination", "full table scan",
        "index scan", "index seek", "n+1 query", "n+1 queries", "n+1 problem", "batch insert",
        "batch inserts", "bulk insert", "bulk inserts", "findinbatches", "first", "take", "last",
        "find", "pluck", "scopes", "scope", "query", "queries", "subquery", "subqueries",
        "join", "left join", "right join", "inner join", "outer join", "cross join", "self join",
        
        # Enterprise & Architecture patterns
        "multi-tenant", "multi-tenancy", "tenant", "tenants", "tenant id", "tenant filtration",
        "shared database", "database per tenant", "schema per tenant", "observability", "metrics",
        "logging", "tracing", "profiling", "pprof", "prometheus", "opentelemetry", "otel",
        "jaeger", "grafana", "structured logging", "slog", "zap", "logrus", "error budget",
        "sli", "slo", "sla", "mttr", "mtbf", "rto", "rpo", "runbook", "post-mortem",
        "singleflight", "cache aside", "write through", "write behind", "cache stampede",
        "cache eviction", "lru", "lfu", "ttl", "cdn", "hot path", "graceful shutdown",
        "health check", "liveness", "readiness", "circuit breaker", "bulkhead", "sidecar",
        "service mesh", "api gateway", "bff", "backend for frontend", "cqrs", "event sourcing",
        "outbox pattern", "saga pattern", "idempotency", "idempotency key", "eventual consistency",
        "cap theorem", "backpressure", "throttling", "rate limiting", "debounce", "throttle",
        
        # Go Language basics & syntax
        "package", "module", "workspace", "vendoring", "dependency injection", "di", "mocking",
        "mock", "mocks", "stub", "stubs", "fake", "fakes", "spy", "spies", "unit test", "unit testing",
        "integration test", "integration testing", "smoke test", "sanity test", "regression test",
        "contract test", "e2e test", "end-to-end test", "stress test", "load test", "chaos test",
        "mutation test", "fuzz test", "fuzz testing", "ab test", "canary test", "test coverage",
        "flaky test", "benchmark", "benchmarks", "testcontainers", "error wrapping", "sentinel error",
        "sentinel errors", "custom error", "custom errors", "error handling", "date time",
        "datetime", "timestamp", "timestamps", "format", "strconv", "regex", "regular expression",
        "pipeline", "iterator", "iterators", "async/await", "async", "await", "promise", "promises",
        "callback", "callbacks", "nil", "zero value", "zero values", "pointer", "pointers",
        "slice", "slices", "array", "arrays", "struct", "structs", "interface", "interfaces",
        "generic", "generics", "comparable", "any", "iota", "closure", "closures", "defer",
        "panic", "recover", "receiver", "receivers", "method", "methods", "function", "functions",
        "interface embedding", "struct embedding", "anonymous field", "anonymous fields",
        
        # Web Framework & API Specific
        "engine", "context", "handler", "handlers", "handlerfunc", "middleware", "middlewares",
        "router", "routers", "routing", "request", "requests", "response", "responses",
        "status code", "status codes", "query parameter", "query parameters", "path parameter",
        "path parameters", "form value", "form values", "multipart form", "file upload",
        "validation", "validator", "binding", "shouldbind", "shouldbindjson", "mustbind",
        "swagger", "openapi", "redoc", "sse", "server-sent events", "websocket", "websockets",
        "cors", "csrf", "helmet", "secure header", "secure headers", "rate limit", "rate limiter",
        "session", "sessions", "cookie", "cookies", "jwt", "jsonwebtoken", "oauth2", "oidc",
        "rbac", "abac", "claims", "token", "tokens", "refresh token", "access token",
        
        # General Software Architecture
        "dry", "kiss", "yagni", "solid", "single responsibility", "open closed", "liskov substitution",
        "interface segregation", "dependency inversion", "technical debt", "refactoring",
        "code smell", "code smells", "linter", "formatter", "inversion of control", "ioc",
        "hexagonal architecture", "clean architecture", "onion architecture", "domain driven design",
        "ddd", "twelve factor", "immutable infrastructure", "infrastructure as code", "iac",
        "semantic versioning", "semver"
    ]
    
    for t in custom_keywords:
        terms.add(t)
        
    return sorted(list(terms))

def main():
    print("Scanning documentation and glossary directories...")
    terms = scan_folders()
    print(f"Found {len(terms)} unique glossary terms to protect.")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for t in terms:
            if t.strip():
                f.write(t.strip() + "\n")
                
    print(f"Successfully generated clean glossary protection file: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
