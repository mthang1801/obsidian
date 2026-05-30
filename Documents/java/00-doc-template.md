<!-- tags: java, template, reference -->
# 🧩 Java Document Template

> Template chuẩn để viết bài Java theo workflow `create-doc.md`, có thể dùng cho Java core, JVM, backend, Spring và expert topics.

📅 Ngày tạo: 2026-03-27 · 🔄 Cập nhật: 2026-03-27 · ⏱️ 5 phút đọc

## Header

```markdown
# ☕ [Tên chủ đề]

> Mô tả ngắn 1-2 câu, nói rõ giá trị thực tế của chủ đề.

📅 Ngày tạo: YYYY-MM-DD · 🔄 Cập nhật: YYYY-MM-DD · ⏱️ XX phút đọc

| Aspect | Detail |
| --- | --- |
| **Complexity** | Basic / Intermediate / Advanced / Expert |
| **Use case** | Khi nào dùng |
| **Java focus** | API / concept / framework chính |
| **Prerequisites** | Những gì cần biết trước |
```

## Section Layout

1. `## 1. DEFINE`
2. `## 2. VISUAL`
3. `## 3. CODE`
4. `## 4. PITFALLS`
5. `## 5. REF`
6. `## 6. RECOMMEND`
7. `## 7. QUIZ` nếu bài đủ nặng
8. `## 8. NEXT STEPS`

## Java Writing Rules

- Ưu tiên Java idioms hiện đại: `record`, `sealed`, `var` khi hợp lý, `CompletableFuture`, `Stream`, `HttpClient`
- Với Spring: dùng constructor injection, DTO, validation, `@ControllerAdvice`, `@ConfigurationProperties`
- Với class public/protected quan trọng: thêm Javadoc ngắn gọn
- Example phải chia rõ `basic`, `intermediate`, `advanced`, `expert` nếu chủ đề đủ sâu

## Quiz Attachment Rule

- `Quick Check` cho bài basic/intermediate
- `Scenario Quiz` cho bài advanced/expert
- Answer key luôn ở cuối cùng
