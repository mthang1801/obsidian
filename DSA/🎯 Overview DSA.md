
#### **LEVEL 1: Foundation & Core Patterns (1-5)**

Những viên gạch đầu tiên cần nắm chắc trước khi giải quyết mọi bài toán thuật toán:

1. [**Arrays & Strings Cơ Bản**](string.html) - Cách Go quản lý mảng tĩnh, slices linh hoạt, và bản chất read-only UTF-8 của String.
2. [**Two Pointers Pattern**](dsa-patterns-go.html#s-twoptr) - Kỹ thuật dùng hai con trỏ tối ưu hóa tìm kiếm từ $O(N^2)$ về $O(N)$.
3. [**Sliding Window Pattern**](dsa-patterns-go.html#s-sliding) - Quản lý cửa sổ trượt (Cố định & Khả biến) xử lý mảng/chuỗi con liên tục.
4. [**Singly & Doubly Linked Lists**](linked-lists.html#s01) - Trực quan hóa cấu trúc danh sách liên kết, đảo ngược và phát hiện chu trình.
5. [**HashMap & Prefix Sum**](dsa-patterns-go.html#s-hashmap) - Sử dụng mảng cộng dồn `Prefix Sum` để truy vấn đoạn $O(1)$ và bảng băm lưu trữ trạng thái.

🔥 **So sánh nhanh**: JS Array (thực chất là object, dynamic) vs Go Slice (cửa sổ trỏ vào mảng tĩnh bên dưới, cực kỳ tối ưu bộ nhớ).

---

#### **LEVEL 2: Non-Linear Data Structures & Greedy (6-10)**

Nâng cao tư duy cấu trúc dữ liệu và các kỹ thuật lựa chọn tối ưu cục bộ:

6. [**Stack & Queue Cơ Bản**](dsa-patterns-go.html#s-stack) - Cấu trúc LIFO/FIFO tự xây dựng trong Go và ứng dụng duyệt DFS/BFS.
7. [**Binary Search & Array Division**](searching.html#binary) - Chia đôi không gian tìm kiếm, tìm kiếm trên mảng đã sắp xếp và mảng xoay vòng.
8. [**Greedy Algorithms & Kadane's**](greedy-algorithms.html#s-kadane-intro) - Thuật toán tham lam lựa chọn tối ưu cục bộ và tìm mảng con có tổng lớn nhất trong $O(N)$.
9. [**Monotonic Stack & Deque**](dsa-patterns-go.html#s-monostack) - Ngăn xếp/Hàng đợi đơn điệu giải quyết các bài toán "phần tử tiếp theo lớn hơn".
10. [**Union-Find (Disjoint Set Union)**](important-algorithms.html#uf-concept) - Cấu trúc quản lý tập hợp rời rạc, tối ưu Path Compression và phát hiện chu trình.

---

#### **LEVEL 3: Graphs & Advanced Structures (11-15)**

Chinh phục các cấu trúc dữ liệu đồ thị phức tạp và thuật toán nâng cao:

11. [**Graph Algorithms (DFS & BFS)**](graph-algorithms.html) - Biểu diễn đồ thị bằng Adjacency List/Matrix, duyệt đồ thị, kiểm tra liên thông.
12. [**Shortest Paths & Spanning Trees**](graph-algorithms.html) - Các thuật toán Dijkstra, Bellman-Ford, Kruskal & Prim tìm cây khung nhỏ nhất.
13. [**Advanced Tree & BST Traversal**](tree.html#traversal) - Duyệt cây nhị phân, AVL, Red-Black Tree và cấu trúc tự cân bằng.
14. [**Trie (Cây tiền tố)**](string.html#trie) - Cấu trúc dữ liệu tối ưu hóa lưu trữ từ điển, autocomplete và tìm kiếm tiền tố.
15. [**String Matching (KMP & Rabin-Karp)**](important-algorithms.html#kmp-concept) - Tìm kiếm chuỗi con trong thời gian tuyến tính thay vì vét cạn $O(N \times M)$.

---

#### **LEVEL 4: Dynamic Programming (DP) & Expert Patterns (16-20)**

Làm chủ quy hoạch động và các kỹ thuật tối ưu hóa đỉnh cao:

16. [**Quy hoạch động (Concepts)**](dynamic-programing.html#concepts) - Tư duy phân rã bài toán con, tiếp cận Top-Down (Memoization) vs Bottom-Up (Tabulation).
17. [**LCS & LIS Patterns**](dynamic-programing.html#lcs) - Tìm chuỗi con chung dài nhất và chuỗi con tăng dần dài nhất.
18. [**Knapsack Problem**](dynamic-programing.html#knapsack) - Bài toán cái túi kinh điển (0/1 Knapsack, Bounded & Unbounded).
19. [**Coin Change & House Robber**](dynamic-programing.html#coin) - Ứng dụng thực tế của Quy hoạch động trong việc ra quyết định tối ưu.
20. [**Manacher's & Palindrome DP**](string.html#palindrome) - Xử lý chuỗi đối xứng cực hạn $O(N)$ bằng thuật toán Manacher.

---

#### **BONUS: Advanced Search & Backtracking (21-22)**

21. [**A\* Pathfinding**](important-algorithms.html#astar-concept) - Tìm kiếm đường đi thông minh nhất sử dụng hàm Heuristic ước lượng.
22. [**Backtracking Pattern**](important-algorithms.html#bt-concept) - Tư duy quay lui vét cạn không gian trạng thái (bài toán N-Queens, Sinh hoán vị).

---

### 💡 Best Practices Từ Background JS/TS Của Bạn

#### So Sánh Cú Pháp & Cách Dùng:

| JS / TS | Go Equivalent | Giải thích kỹ thuật |
| :--- | :--- | :--- |
| `Array.prototype.push()` | `append(slice, val)` | Go Slice tăng kích thước tự động bằng cách nhân đôi capacity khi vượt ngưỡng. |
| `new Map()` | `make(map[K]V)` | Map trong Go không thread-safe mặc định (cần `sync.RWMutex` nếu concurrent). |
| `new Set()` | `map[K]struct{}` | Go không có Set mặc định, dùng map với value là `struct{}` (tốn 0 byte memory). |
| `null` | `nil` | Đại diện cho con trỏ không trỏ đi đâu cả, cần kiểm tra `nil` trước khi truy cập tree/linked list node. |
| `class Node { ... }` | `type Node struct { ... }` | Sử dụng struct để biểu diễn Node của Trees/Linked Lists thay vì hướng đối tượng class. |
| Generics `class Stack<T>` | Generics `type Stack[T any]` | Go 1.18+ hỗ trợ Generic giúp viết cấu trúc dữ liệu dùng chung cực kỳ type-safe. |

#### Lưu Ý Quan Trọng Về Bộ Nhớ (Memory Management):

1. **Escape Analysis**: V8 thu gom rác tự động bằng tracing GC. Go có trình biên dịch thông minh tự phân tích xem biến của bạn nằm ở **Stack** hay **Heap** (Escape to Heap). Khởi tạo quá nhiều con trỏ ngắn hạn trong Tree/Linked List sẽ làm tăng áp lực lên Garbage Collector của Go.
2. **Slice Memory Leak**: Khi cắt một slice lớn `slice[10:12]`, Go vẫn giữ nguyên mảng tĩnh khổng lồ bên dưới trong bộ nhớ. Để tránh rò rỉ bộ nhớ, hãy dùng `copy()` sang slice mới nếu chỉ cần một phần dữ liệu nhỏ.
3. **Struct với struct{}**: Khi implement các bài toán đồ thị cần tập hợp các node đã duyệt (`visitedSet`), hãy luôn dùng `map[int]struct{}` thay vì `map[int]bool`. Việc này giúp Go tối ưu kích thước bản đồ xuống mức tối thiểu vì `struct{}` không tốn dung lượng bộ nhớ.
4. **Tránh recursion quá sâu**: Khác với JS có call stack linh hoạt (nhưng giới hạn bởi engine), Go goroutine stack ban đầu rất nhỏ (chỉ 2KB) và tự co giãn. Tuy nhiên, đệ quy quá sâu trong DFS/DP vẫn có thể gây overhead. Hãy chuyển sang dạng vòng lặp dùng Stack tự xây dựng khi xử lý cây/đồ thị khổng lồ.

---

### 🚀 Gợi Ý Học Tập

1. **Tuần 1-2**: Foundation (1-5) - Nắm vững cơ chế Slice, quản lý bộ nhớ của Go và các kỹ thuật con trỏ/cửa sổ trượt.
2. **Tuần 3**: Intermediate (6-10) - Rèn luyện các cấu trúc Stack, Queue tự chế, tập giải các bài toán trung cấp bằng Go Generics.
3. **Tuần 4**: Graphs & advanced (11-15) - Luyện tập duyệt đồ thị BFS/DFS, KMP và cài đặt cây tiền tố Trie.
4. **Tuần 5**: Chinh phục DP & Expert (16-22) - Tập trung giải quyết các mẫu bài toán quy hoạch động kinh điển, vẽ bảng Tabulation trực quan để hiểu luồng tối ưu hóa.
