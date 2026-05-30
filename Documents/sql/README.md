<!-- tags: sql, postgresql, database, overview -->
# 🐘 SQL & PostgreSQL — Tổng quan

> Bạn vừa nhận một hệ thống có query chậm, replica lag và schema ngày càng khó sửa. Nếu không có bản đồ học tập rõ ràng, bạn sẽ tối ưu theo cảm giác. Module này biến SQL/PostgreSQL thành một learning system có thứ tự: từ semantics, sang planner, rồi đến incident handling.

| Aspect | Detail |
| --- | --- |
| **Concept** | SQL fundamentals, PostgreSQL internals, diagnostics, replication, quiz-driven reinforcement |
| **Audience** | Backend engineer, DBA, platform engineer, on-call engineer |
| **Primary style** | Concept-First hub — điều hướng người đọc sang đúng submodule |
| **Entry point** | `postgresql/fundamental/`, `optimizer/`, `quiz/` |

📅 Ngày tạo: 2026-03-19 · 🔄 Cập nhật: 2026-04-04 · ⏱️ 6 phút đọc

---

## 1. DEFINE

SQL không khó ở syntax — SQL khó ở **khoảng cách giữa query chạy được và query chạy đúng dưới load**. Library này tổ chức kiến thức PostgreSQL theo đúng progression mà một DBA cần: fundamentals trước, performance và HA sau, quiz cuối cùng để verify mental model.

Mỗi bài không dạy syntax — nó dạy khi nào dùng gì, tại sao thay thế gì, và trap nào đang chờ ở production.

| Variant | Mô tả |
| --- | --- |
| PostgreSQL Core Track | Học schema, query, joins, JSONB, functions, transactions và batch operations trước khi tối ưu. |
| Optimizer & Operations Track | Đi vào EXPLAIN, memory, index selection, VACUUM, WAL, pooling, partitioning và triage. |
| HA & Replication Track | Tập trung vào streaming replication, logical replication, Patroni, PgBouncer, backup/PITR. |
| Quiz & Scenario Track | Dùng module quiz và incident quiz để kiểm tra mental model thay vì chỉ đọc lý thuyết. |

| Approach | Time | Space | Khi chọn |
| --- | --- | --- | --- |
| Bắt đầu từ `postgresql/fundamental` | Phụ thuộc số bài | O(1) | Dùng khi còn mơ hồ về semantics của SQL/PostgreSQL và cần baseline đúng trước. |
| Rẽ sang `optimizer` sau khi đã query được | Phụ thuộc workload | O(1) | Dùng khi query đúng logic nhưng production bắt đầu đau vì plan, lock hoặc cache miss. |
| Kết thúc mỗi track bằng `quiz` | Phụ thuộc số câu hỏi | O(1) | Dùng khi cần kiểm tra xem mình thực sự hiểu hay chỉ nhớ syntax. |
| Gắn `replication` sau performance | Phụ thuộc topology | O(1) | Dùng khi thay đổi query/index đã bắt đầu ảnh hưởng replica, failover hoặc DR. |

Core insight:

> SQL không chỉ là viết query đúng. Giá trị thật của module này nằm ở chỗ nó buộc bạn nhìn cùng một vấn đề qua ba lớp: **semantics đúng**, **planner chọn gì**, và **production chịu nổi không**.

### Module Map

| Folder | Vai trò | Điểm vào chính |
| --- | --- | --- |
| [`postgresql/`](./postgresql/README.md) | Main learning track cho PostgreSQL từ nền tảng đến replication | Nếu muốn học bài bản từ đầu |
| [`optimizer/`](./optimizer/README.md) | Diagnostic + tuning + DBA playbooks | Nếu đang xử lý query chậm, bloat, WAL, connection pressure |
| [`quiz/`](./quiz/README.md) | Quiz theo module và scenario | Nếu muốn kiểm tra mental model sau khi học |

### Decision Lens

| Nếu vấn đề là... | Hỏi trước | Vào track |
| --- | --- | --- |
| Query chưa đúng logic | Join, grouping, transaction, JSONB semantics đã đúng chưa? | [`postgresql/fundamental`](./postgresql/fundamental/README.md) |
| Query đúng nhưng chậm | Planner đang chọn plan nào, index nào, rows estimate có lệch không? | [`optimizer`](./optimizer/README.md) + [`postgresql/performance`](./postgresql/performance/README.md) |
| Production có lag / failover risk | WAL, slot, backup, cutover path đã kiểm chứng chưa? | [`postgresql/replication`](./postgresql/replication/README.md) |
| Cần biết mình hiểu đến đâu | Có trả lời được câu hỏi theo tình huống thật không? | [`quiz`](./quiz/README.md) |

---

## 2. VISUAL

Với SQL & PostgreSQL — Tổng quan, điều còn thiếu sau phần định nghĩa là bản đồ: vấn đề nào đi nhánh nào và vì sao. Sơ đồ dưới đây làm rõ đường đi đó trước khi bạn chạm vào chi tiết triển khai.

![SQL & PostgreSQL — 3 learning lanes: PostgreSQL, Query Optimizer, Quiz & Practice](./images/sql-learning-roadmap.png)

### Level 1

```text
SQL & PostgreSQL Learning Flow
------------------------------
postgresql/fundamental
        |
        v
postgresql/performance  <---->  optimizer
        |
        v
postgresql/advanced
        |
        v
postgresql/replication
        |
        v
quiz/module  --->  quiz/scenario
```

*Hình: Level 1 cho thấy order học đúng: semantics trước, tuning sau, rồi mới đến replication và incident reasoning.*

### Level 2

```text
Symptom / Goal                 Câu hỏi quyết định                  Track nên mở
----------------------------  ----------------------------------  -----------------------------------------
Schema/query chưa ổn          Semantics đã đúng chưa?             postgresql/fundamental
Query chậm bất thường         Planner/index/buffers nói gì?       optimizer + postgresql/performance
Muốn dùng SQL nâng cao        Cần procedural logic hay internals? postgresql/advanced
Replica lag / failover risk   WAL, slots, PITR đã an toàn chưa?   postgresql/replication
Muốn tự kiểm tra kiến thức    Trả lời được bằng reasoning chưa?   quiz/module + quiz/scenario
```

*Hình: Level 2 biến root README thành router — mỗi symptom được map sang đúng submodule thay vì đọc lan man.*

---
## 3. CODE

Có bản đồ của SQL & PostgreSQL — Tổng quan rồi vẫn chưa đủ nếu bạn không biến nó thành checklist hoặc lab có thể chạy thật. Phần dưới đây chuyển routing logic thành artifact dùng được ngay.

### Problem 1: Basic — Bootstrap PostgreSQL learning lab

> **Mục tiêu**: Dựng nhanh một lab local để đọc bài, chạy query, và benchmark lại các ví dụ trong module SQL.
> **Approach**: Dùng Docker + `psql` để tạo baseline thống nhất trước khi học optimizer hay replication.
> **Ví dụ**: Đầu vào là một máy local sạch; đầu ra là PostgreSQL 15 + database sandbox để chạy các bài trong `assets/sql`.
> **Độ phức tạp**: Basic — ưu tiên reproducibility trước.

```bash
# sql-lab.sh — Bootstrap PostgreSQL 15 sandbox cho assets/sql
set -euo pipefail

docker rm -f sql-handbook >/dev/null 2>&1 || true

docker run -d \
  --name sql-handbook \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=handbook \
  -p 5432:5432 \
  postgres:15

echo "Waiting for PostgreSQL..."
until docker exec sql-handbook pg_isready -U postgres >/dev/null 2>&1; do
  sleep 1
done

docker exec -i sql-handbook psql -U postgres -d handbook <<'SQL'
CREATE TABLE customers (
  customer_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE orders (
  order_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  customer_id bigint NOT NULL REFERENCES customers(customer_id),
  status text NOT NULL,
  total_amount numeric(12,2) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO customers(email)
SELECT format('user%02s@example.com', g)
FROM generate_series(1, 10) AS g;

INSERT INTO orders(customer_id, status, total_amount)
SELECT
  (random() * 9 + 1)::bigint,
  CASE WHEN random() < 0.7 THEN 'paid' ELSE 'pending' END,
  round((random() * 500)::numeric, 2)
FROM generate_series(1, 200);
SQL

echo "Lab ready: psql postgresql://postgres:postgres@localhost:5432/handbook"
```

**Tại sao?** Nếu mỗi người đọc chạy ví dụ trên một môi trường khác nhau, bạn rất khó phân biệt lỗi do PostgreSQL semantics với lỗi do môi trường. Problem này khóa cùng một baseline để những bài sau về plan, index, WAL hay replica có điểm xuất phát giống nhau.

**Kết luận**: Khi root module có một lab chuẩn, các README con không chỉ là “mục lục” mà trở thành lộ trình có thể thực hành thật. Nếu chưa có lab, đừng nhảy thẳng sang tối ưu hay HA.

### Problem 2: Intermediate — Route một symptom sang đúng submodule

> **Mục tiêu**: Biến root README thành decision router thay vì danh sách link.
> **Approach**: Dùng một checklist symptom-based để quyết định học `fundamental`, `optimizer`, `performance`, `replication` hay `quiz`.
> **Ví dụ**: Đầu vào là complaint như “query chậm” hoặc “replica lag”; đầu ra là track nên mở đầu tiên.
> **Độ phức tạp**: Intermediate — reasoning theo symptom thay vì theo folder name.

```sql
-- triage_router.sql — symptom-driven questions trước khi mở bài
WITH symptoms(symptom, first_question, target_track) AS (
  VALUES
    ('query returns wrong rows',
     'GROUP BY / JOIN / NULL semantics đã đúng chưa?',
     'postgresql/fundamental'),
    ('query slow after data growth',
     'EXPLAIN ANALYZE có cho thấy seq scan, bad estimate hoặc wrong join order không?',
     'optimizer + postgresql/performance'),
    ('replica lag keeps growing',
     'Lag đến từ slow replay, slot backlog hay WAL generation spike?',
     'postgresql/replication'),
    ('team cannot answer interview-style incidents',
     'Đã thử module quiz và scenario quiz chưa?',
     'quiz')
)
SELECT *
FROM symptoms
ORDER BY symptom;
```

**Tại sao?** Cùng một phrase “database chậm” có thể là ba vấn đề khác nhau: query viết sai, planner chọn sai, hoặc hệ thống replication đang chịu áp lực. Nếu root README không ép người đọc đặt câu hỏi đúng trước, họ sẽ vào nhầm track và tối ưu sai chỗ.

**Kết luận**: Root README phải hoạt động như một router. Khi symptom được map đúng ngay từ đầu, thời gian đọc tài liệu và thời gian triage production đều giảm mạnh.

### Problem 3: Advanced — Lập learning loop có verification

> **Mục tiêu**: Gắn docs với cơ chế kiểm tra, để việc học SQL/PostgreSQL không dừng ở đọc hiểu.
> **Approach**: Kết hợp docs + module quiz + scenario quiz theo vòng lặp lặp lại được.
> **Ví dụ**: Đầu vào là một engineer mới vào on-call rotation; đầu ra là learning path có checkpoint rõ ràng.
> **Độ phức tạp**: Advanced — phối hợp nhiều submodule và incident mindset.

```text
Week 1
  - Đọc postgresql/fundamental/01-08
  - Chạy lab local và reproduce ví dụ
  - Làm quiz/module/01-postgresql-fundamentals.md

Week 2
  - Đọc optimizer/01-07 + postgresql/performance/01-03
  - Chạy EXPLAIN ANALYZE trên dữ liệu sandbox
  - Làm quiz/module/02-query-plans-performance-and-maintenance.md

Week 3
  - Đọc postgresql/advanced/01-03
  - Đọc replication/01-05
  - Làm quiz/module/03-replication-and-ha.md
  - Làm quiz/module/04-logical-replication-and-cdc.md

Week 4
  - Làm scenario quiz 01 và 02
  - Viết lại incident notes: symptom -> evidence -> safe action -> rollback
```

**Tại sao?** SQL/PostgreSQL là miền mà hiểu biết “đọc được” không đủ. Người đọc chỉ thực sự internalize mental model khi họ phải giải thích vì sao planner đổi plan, vì sao replica lag, hoặc vì sao một failover decision là nguy hiểm. Quiz là phần bắt buộc của learning loop chứ không phải appendix.

**Kết luận**: Đọc tài liệu mà không có verification dễ tạo ảo tưởng hiểu. Root README phải đẩy người đọc sang quiz đúng lúc để biến kiến thức thành phản xạ xử lý tình huống.

---
## 4. PITFALLS

SQL & PostgreSQL — Tổng quan chỉ có ích khi nó giúp tránh đi nhầm đường. Phần dưới đây chỉ ra những cách người đọc thường tự phá learning path hoặc triage path của chính mình.

| # | Severity | Lỗi | Hậu quả | Fix |
| --- | --- | --- | --- | --- |
| 1 | 🔴 Fatal | Vào thẳng optimizer khi còn mơ hồ semantics SQL | Tối ưu sai chỗ, query có thể vẫn trả sai kết quả | Luôn đi qua `postgresql/fundamental` trước khi tune performance. |
| 2 | 🟡 Common | Dùng root README như danh sách link thay vì router symptom | Mất thời gian đọc lan man, không giải quyết được vấn đề hiện tại | Bắt đầu bằng symptom → câu hỏi quyết định → track. |
| 3 | 🟡 Common | Học replication mà chưa hiểu WAL / VACUUM / planner basics | Nhìn symptom sai, failover decision thiếu context | Hoàn thành performance/optimizer baseline trước replication. |
| 4 | 🔵 Minor | Bỏ qua quiz vì nghĩ “đọc là đủ” | Mental model không được kiểm chứng, dễ fail khi gặp incident thật | Chèn quiz vào cuối mỗi learning block. |

---
## 5. REF

| Resource | Loại | Link | Ghi chú |
| --- | --- | --- | --- |
| PostgreSQL Documentation | Official docs | https://www.postgresql.org/docs/current/index.html | Entry point để verify syntax, planner behavior, WAL, replication. |
| Neon PostgreSQL Tutorial | Tutorial | https://neon.com/postgresql/tutorial | Useful as companion material cho track `fundamental`. |
| explain.dalibo.com | Tool | https://explain.dalibo.com/ | Visualize execution plans khi học `optimizer` và `performance`. |

---

## 6. RECOMMEND

Khi đường đi của SQL & PostgreSQL — Tổng quan đã rõ, bạn có thể rẽ sang đúng module tiếp theo thay vì đọc lan man. Phần gợi ý dưới đây mở tiếp cánh cửa đó.

| Mở rộng | Khi nào | Lý do | File/Link |
| --- | --- | --- | --- |
| PostgreSQL Core Track | Khi muốn học bài bản từ đầu | Xây baseline semantics trước mọi tối ưu | [postgresql/README.md](./postgresql/README.md) |
| Optimizer & DBA Track | Khi đang bị query chậm, bloat, WAL pressure, connection pressure | Chuyển từ “query đúng” sang “query chạy đúng trên production” | [optimizer/README.md](./optimizer/README.md) |
| Quiz Track | Khi cần kiểm tra mental model sau mỗi block học | Ép reasoning thay vì chỉ nhớ syntax | [quiz/README.md](./quiz/README.md) |

---

## 7. QUICK REF

| Nếu gặp | Nghĩ ngay |
| --- | --- |
| Query sai kết quả | Quay lại `postgresql/fundamental` |
| Query chậm / seq scan / wrong estimate | Mở `optimizer` + `postgresql/performance` |
| Replica lag / failover / PITR | Mở `postgresql/replication` |
| Không chắc mình hiểu đến đâu | Làm `quiz/module` rồi `quiz/scenario` |