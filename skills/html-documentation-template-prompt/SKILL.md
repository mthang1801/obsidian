---
name: html-documentation-template-prompt
title: HTML Documentation Template — Design System & Prompt Guide
description: >
  Mô tả chính xác design system (dark theme, CSS tokens, component library, syntax highlighting)
  cho self-contained HTML technical documentation. Dùng để prompt AI agent tạo artifact đồng nhất.
tags: [design-system, html, documentation, prompt-template, dark-theme, css]
---

# Prompt Template: HTML Technical Documentation Artifact

> **Mục đích**: Template này mô tả chính xác design system của documentation HTML trong Obsidian vault,
> để khi prompt với AI agent (Claude, Gemini, GPT, Copilot...) sẽ tạo ra artifact đồng nhất về UI/UX.

---

## 🔑 Nguyên tắc cốt lõi khi prompt

### 1. Mô tả Layout Architecture (PHẢI CÓ)
```
Layout: Single-page application style với 3 vùng chính:
- Sidebar cố định bên trái (270px), chứa navigation phân nhóm theo mức độ
- Top navigation bar nằm ngang (fixed, horizontal scroll), mirror các sections  
- Main content area (scrollable), chỉ hiện 1 section tại một thời điểm (tab-based)

Khi click sidebar item hoặc topnav → section tương ứng hiện, các section khác ẩn.
- CSS bắt buộc: `.topic { display: none; } .topic.active { display: block !important; }`
- Tránh lỗi đè tiêu đề: Thiết lập `.shell { padding-top: 74px; }` hoặc khoảng đệm phù hợp để fixed topbar không che khuất phần đầu nội dung của tab hoạt động.
- Javascript Router bắt buộc tương thích Obsidian Sandbox:
  1. Sử dụng addEventListener động (không dùng inline onclick).
  2. Bọc history.pushState trong try-catch phòng lỗi SecurityError, fallback về window.location.hash.
  3. Cuộn mượt về đầu trang (window.scrollTo(0, 0)) và hỗ trợ deep-linking dựa trên hash khi tải trang.
```

### 2. Mô tả Design System (PHẢI CÓ)
```
Dark theme premium với design tokens:
- Backgrounds: #0d0f14 (primary), #131720 (secondary), #1a1f2e (card), #0f1319 (code)
- Accents: cyan #00d4ff (primary), green #00ff88 (success), purple #a855f7 (expert),
  amber #f59e0b (warning), coral #ff6b6b (danger), blue #3b82f6 (info)
- Text: #e2e8f0 (primary), #94a3b8 (secondary), #64748b (muted)
- Borders: rgba(255,255,255,0.07), accent border rgba(0,212,255,0.3)
- Fonts: Inter (body text), JetBrains Mono (code + labels)
- Border-radius: 12px cards, 10px code blocks, 8px buttons, 6px inputs, 4px inline-code
```

### 3. Mô tả Component Library (CHỌN components cần dùng)

| Component | Khi nào dùng | Mô tả ngắn |
|-----------|-------------|-------------|
| `section-header` | Đầu mỗi section | Số thứ tự gradient + title + subtitle + badge level |
| `concept-box` | Định nghĩa quan trọng | Box gradient cyan→purple, có label + title + prose |
| `card` / `card-grid` | Liệt kê use-cases | Grid 2 cột, cards với icon title + description |
| `code-block` | Code examples | Header (lang + filename + copy button) + pre highlighted |
| `note` | Cảnh báo / tips | 4 variants: `note-info`, `note-warn`, `note-danger`, `note-success` |
| `data-table` | So sánh / API ref | Thead uppercase, hover rows, inline code support |
| `diagram-container` | Kiến trúc / flows | SVG inline với font JetBrains Mono, title uppercase centered |
| `compare-grid` | So sánh 2 options | 2 columns, mỗi cột có colored header + tags good/bad |
| `badge` | Level indicator | 3 levels: `badge-basic` (cyan), `badge-advanced` (amber), `badge-expert` (purple) |
| `ref-card` | External references | Icon + title + description + URL + stars/label |
| `concept-img-wrapper` | Hình minh họa | Image with cyan border glow + italic caption |
| `tag` | Feature labels | `tag-good` (green ✅) / `tag-bad` (red ❌) |
| `prose` | Body text | 15px, line-height 1.8, inline code cyan highlighted |
| `divider` | Section separator | `<hr>` styled, margin 36px |
| `demo-container` | Interactive demos | Header with colored dots + body + controls + log output |

### 4. Syntax Highlighting Convention (cho code blocks)
```
Wrap code tokens trong <span> classes:
- .kw  = keywords (purple #c084fc): package, func, if, for, return, defer, go, type, var...
- .fn  = function names (blue #60a5fa): Printf, Acquire, Release, NewWeighted...
- .str = strings (green #86efac): "hello", 'path'
- .cm  = comments (gray #4b5563, italic): // comment
- .num = numbers (orange #fb923c): 1, 100, 3.14
- .tp  = types (cyan #67e8f9): int, string, error, Context, Weighted...
- .pkg = package names (lavender #a78bfa): main, fmt, sync
- .op  = operators (pink #f472b6): :=, <-, &&
```

### 5. SVG Diagram Convention
```
- ViewBox thường 820×280-380, width="100%"
- Background colors dùng rgba() với low opacity (0.08-0.15)
- Text dùng font-family="JetBrains Mono"
- Arrow markers defined trong <defs>
- Color code: green=running, amber=blocked/waiting, cyan=active, purple=stages
- Legend ở bottom, font-size 11px
```

---

## 📋 Ready-to-Use Prompt Skeleton

Dưới đây là prompt bạn có thể copy và điền vào `[...]`:

---

````markdown
Tạo một trang HTML documentation chuyên sâu về [CHỦ ĐỀ], sử dụng CHÍNH XÁC
design system sau. File HTML phải self-contained (CSS + JS inline), không dùng
framework, không có external dependencies ngoài Google Fonts.

## Yêu cầu kỹ thuật

**Layout & Điều hướng SPA**:
- Fixed sidebar trái (270px) chứa navigation phân nhóm
- Fixed top navigation bar (horizontal scrollable) mirror sidebar items
- Main content area hiển thị CHỈ 1 section/tab tại một thời điểm. Mặc định ẩn tất cả các section khác.
- CSS bắt buộc: `.topic { display: none; padding: 46px 0; border-bottom: 1px solid var(--line-soft); scroll-margin-top: 84px; } .topic.active { display: block !important; }`
- Tránh lỗi đè tiêu đề: Thiết lập `.shell { padding-top: 74px; }` hoặc một khoảng đệm hợp lý để thanh topbar cố định không che khuất phần đầu nội dung của tab hoạt động.
- JavaScript SPA Router bắt buộc (tương thích Obsidian Sandboxed environment):
  1. KHÔNG dùng thuộc tính inline `onclick` trên HTML. Toàn bộ các sự kiện chuyển đổi menu phải được lắng nghe động thông qua `addEventListener` trong thẻ `<script>`.
  2. Hàm `show(id)` thực hiện: ẩn toàn bộ các thẻ `.topic`, thêm class `active` vào phần tử mục tiêu, đồng bộ trạng thái class `active` trên toàn bộ thẻ liên kết `.toc a` và `.topnav a`, sau đó gọi `window.scrollTo(0, 0)` để cuộn trang lên đầu.
  3. Quản lý trạng thái bằng URL hash: Hàm `handleHash()` đọc `window.location.hash`, tự động kích hoạt `show(id)` tương ứng, mặc định là `show('intro')`. Lắng nghe sự kiện hash qua `window.addEventListener('hashchange', handleHash);`.
  4. Cập nhật hash an toàn trong Obsidian: Khi click liên kết, bọc hàm `history.pushState` trong một khối `try...catch`. Nếu có lỗi `SecurityError` xảy ra do sandbox restrictions, tự động fallback về việc cập nhật trực tiếp `window.location.hash`.

**Design System (Dark Theme)**:
- CSS Variables cho colors, fonts — dùng :root {}
- Backgrounds: #0d0f14 → #131720 → #1a1f2e → #0f1319
- Accent colors: cyan #00d4ff, green #00ff88, purple #a855f7, amber #f59e0b, coral #ff6b6b
- Text: #e2e8f0 / #94a3b8 / #64748b
- Fonts: Inter (sans-serif body), JetBrains Mono (code + labels)
- Borders: rgba(255,255,255,0.07), border-radius 12px cards / 10px code

**Components bắt buộc**:
1. Section headers: số thứ tự gradient (cyan→purple) + title + subtitle + badge level
2. Concept boxes: gradient background, label uppercase + title + prose explanation
3. Code blocks: header (language label + filename + copy button) + <pre> với syntax highlighting
   bằng <span> classes: .kw (purple keywords), .fn (blue functions), .str (green strings),
   .cm (gray italic comments), .num (orange numbers), .tp (cyan types), .pkg (lavender packages)
4. Note boxes: 4 variants — info (cyan), warn (amber), danger (coral), success (green) —
   mỗi box có icon + text
5. Card grids: 2 columns, hover border-accent effect
6. Data tables: uppercase thead, hover rows, inline code styling
7. Compare grids: 2 columns side-by-side, colored headers, tags good/bad
8. SVG diagrams inline: viewBox 820xN, font JetBrains Mono, rgba colors, arrow markers
9. Reference cards: icon + title + description + URL + stars/badge
10. Copy button: JavaScript copy code to clipboard với feedback "Copied!"

**Responsive**:
- @media max-width 768px: sidebar hidden, hamburger menu toggle, grids → single column
- @media max-width 480px: smaller font sizes, tighter padding

**Cấu trúc Sections** (chia thành [N] sections):

| # | Section ID | Tên | Badge Level | Nội dung |
|---|-----------|-----|-------------|----------|
| 01 | intro | [Giới thiệu] | BASIC | [Định nghĩa, tại sao cần, use-cases 4 cards] |
| 02 | [concept] | [Khái niệm] | BASIC | [Nguyên lý hoạt động, SVG diagram, internal struct] |
| 03 | [basic] | [Ví dụ cơ bản] | BASIC | [Hello world, code examples cơ bản] |
| 04 | [pattern-1] | [Pattern 1] | ADVANCED | [Code + diagram + explanation] |
| 05 | [pattern-2] | [Pattern 2] | ADVANCED | [Code + diagram + explanation] |
| ... | ... | ... | ... | ... |
| N-1 | [pitfalls] | [Pitfalls] | EXPERT | [Common mistakes: ❌ WRONG vs ✅ CORRECT] |
| N | [refs] | [References] | — | [Official docs, books, tools, videos — ref-cards] |

**Sidebar Navigation Groups**:
- Cơ bản: sections 01-03
- Patterns: sections 04-07
- Nâng cao: sections 08-10
- Expert: sections 11-N

**Nội dung chuyên môn**:
[MÔ TẢ CHI TIẾT NỘI DUNG KỸ THUẬT CỦA TỪNG SECTION Ở ĐÂY]

**Phong cách viết**:
- Tiếng Việt cho prose, comments trong code
- Tiếng Anh cho code, API names, technical terms
- Giải thích từ cơ bản → nâng cao → expert (Diátaxis-inspired)
- Mỗi code example phải có filename thực tế và runnable
- SVG diagrams cho mỗi concept quan trọng
- Pitfalls section luôn có pattern ❌ WRONG → ✅ CORRECT

**CHÚ Ý QUAN TRỌNG**:
- File phải self-contained, KHÔNG dùng external CSS/JS libraries
- Toàn bộ CSS trong <style>, JS trong <script> cuối body
- KHÔNG dùng Tailwind, Bootstrap, hay bất kỳ framework nào
- Code highlight bằng <span class="kw/fn/str/cm/num/tp/pkg/op">
- lang="vi" cho HTML tag
````

---

## 🎯 Ví dụ prompt hoàn chỉnh (ngắn gọn)

```
Tạo HTML documentation chuyên sâu về "Go Context Pattern" theo đúng
design system dark theme premium đã mô tả ở file
skills/html-documentation-template-prompt.md.

Sections:
01. Giới thiệu Context (BASIC)
02. context.Background vs context.TODO (BASIC)
03. WithCancel pattern (BASIC)
04. WithTimeout & WithDeadline (ADVANCED)
05. WithValue — truyền data (ADVANCED)
06. Context propagation trong HTTP servers (ADVANCED)
07. Context trong database queries (ADVANCED)
08. Pitfalls & Anti-patterns (EXPERT)
09. Production patterns (EXPERT)
10. References

Mỗi section cần: prose giải thích → SVG diagram (nếu concept phức tạp)
→ code block với syntax highlighting → note boxes cho cảnh báo.

Sidebar groups: Cơ bản (01-03), Patterns (04-07), Expert (08-10).
```

---

## 📁 Reference Files

Các file HTML hiện tại sử dụng design system này:

| File | Chủ đề | Size |
|------|--------|------|
| `references/01-goroutines-guide.html` | Goroutines | ~159KB |/02-buffered-unbuffered-channels.html` | Channels | ~131KB |
| `references/19-semaphore-guide.html` | Semaphore | ~133KB |

> [!TIP]
> Khi prompt, có thể attach 1 file reference:
> `@[Go/Concurrency/19-semaphore-guide.html] — Tạo file mới GIỐNG CHÍNH XÁC design system này nhưng cho chủ đề [X]`

---

## ⚡ Quick Prompt (Phiên bản tối giản)

Nếu agent đã biết design system (đã có context từ file trước), chỉ cần:

```
Tạo HTML documentation cho [CHỦ ĐỀ] theo đúng template của
19-semaphore-guide.html:
- Dark theme, sidebar+topnav, tab-based sections
- [N] sections: [liệt kê tên sections]
- Components: concept-box, code-blocks (syntax highlighted),
  SVG diagrams, note boxes, compare-grids, data-tables, ref-cards
- Tiếng Việt, self-contained HTML
```
