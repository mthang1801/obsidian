
#### **LEVEL 1: Core Patterns & Data Structures (Section 1)**

Nền tảng thuật toán thiết yếu, tập trung vào tối ưu hóa con trỏ mảng, cấu trúc dữ liệu tuyến tính và duyệt cây cơ bản:

1. [**Two Pointers & Sliding Window**](./section-1.html#s01) - Tối ưu hóa mảng/chuỗi con liên tục từ $O(N^2)$ về $O(N)$ bằng con trỏ trái-phải và cửa sổ trượt.
2. [**Binary Search (Tìm kiếm nhị phân)**](./section-1.html#s02) - Chia đôi không gian tìm kiếm $O(\log N)$ trên mảng đã sắp xếp và tìm kiếm điểm xoay.
3. [**Stack, Queue & Monotonic Structures**](./section-1.html#s03) - Ứng dụng cấu trúc LIFO/FIFO và Ngăn xếp/Hàng đợi đơn điệu tìm kiếm "phần tử tiếp theo lớn hơn".
4. [**Linked List (Danh sách liên kết)**](./section-1.html#s04) - Đảo ngược danh sách, tìm điểm giao nhau, và kỹ thuật hai con trỏ nhanh-chậm phát hiện chu trình.
5. [**Tree Traversal & BFS/DFS**](./section-1.html#s05) - Duyệt cây nhị phân (Pre, In, Post, Level-order) và các cấu trúc cây tự cân bằng.

---

#### **LEVEL 2: Intermediate Strategies & Graph Theory (Section 2)**

Chinh phục các cấu trúc đồ thị cơ bản, quy hoạch động sơ khởi, thuật toán tham lam và quay lui:

6. [**Graph BFS / DFS & Traversal**](./section-2.html#s01) - Duyệt đồ thị, tìm kiếm đường đi ngắn nhất trên đồ thị không trọng số, và tô màu đồ thị.
7. [**Dynamic Programming (Quy hoạch động cơ bản)**](./section-2.html#s02) - Tư duy phân rã bài toán con, tiếp cận Bottom-Up (Tabulation) vs Top-Down (Memoization).
8. [**Greedy Algorithms & Intervals**](./section-2.html#s03) - Lựa chọn tối ưu cục bộ để đạt tối ưu toàn cục và xử lý các bài toán khoảng thời gian trùng lặp.
9. [**Backtracking (Quay lui)**](./section-2.html#s04) - Duyệt vét cạn không gian trạng thái một cách thông minh (N-Queens, Sinh tập hợp, Sinh hoán vị).
10. [**Bit Manipulation & Binary Math**](./section-2.html#s05) - Sử dụng các phép toán bitwise (AND, OR, XOR, Shift) để giải quyết các bài toán tối ưu hóa bộ nhớ và tính toán nhanh.

---

#### **LEVEL 3: Advanced Structures & State Machine DP (Section 3)**

Làm chủ các cấu trúc dữ liệu nâng cao tự xây dựng và các dạng bài toán quy hoạch động chuyên sâu:

11. [**Heap & Priority Queue**](./section-3.html#s01) - Cấu trúc cây hoàn chỉnh quản lý phần tử lớn nhất/nhỏ nhất hiệu quả (tận dụng gói `container/heap` của Go).
12. [**Trie (Prefix Tree)**](./section-3.html#s02) - Tối ưu hóa lưu trữ và tìm kiếm từ điển, tự động hoàn thành từ (autocomplete) và tìm kiếm tiền tố.
13. [**HashMap & Prefix Sum**](./section-3.html#s03) - Kết hợp bảng băm và mảng cộng dồn giải quyết các bài toán tính tổng đoạn trong thời gian $O(1)$.
14. [**Matrix Optimization**](./section-3.html#s04) - Xử lý mảng hai chiều, duyệt đồ thị trên lưới tọa độ, xoay ma trận và tối ưu không gian.
15. [**State Machine DP (Quy hoạch động trạng thái)**](./section-3.html#s05) - Tư duy hữu hạn trạng thái giải quyết các bài toán giao dịch cổ phiếu phức tạp (Buy & Sell Stock).

---

#### **LEVEL 4: Expert-level Algorithms & Hard Patterns (Section 4)**

Chinh phục các đỉnh cao thuật toán và cấu trúc dữ liệu quy mô lớn đòi hỏi tư duy phân tích toán học vượt trội:

16. [**Advanced Dynamic Programming**](./section-4.html#s-dp-advanced) - Bitmask DP, Digit DP, Interval DP, Tree DP, và DP trên đồ thị có hướng không chu trình (DAG).
17. [**Advanced Graph Theory**](./section-4.html#s-advanced-graph) - Các thuật toán Dijkstra, Bellman-Ford, Floyd-Warshall, Tarjan SCC (tìm thành phần liên thông mạnh), và Kruskal MST.
18. [**Sorting & Searching Variants**](./section-4.html#s-sorting-searching) - QuickSort 3-Way Partition, MergeSort, Radix/Counting Sort, và các biến thể tìm nhị phân nâng cao.
19. [**Array Window Optimization**](./section-4.html#s-array-techniques) - Các kỹ thuật mảng cực hạn, Sliding Window nâng cao, Monotonic Stack tối ưu.
20. [**Advanced Trees & Query Structures**](./section-4.html#s-advanced-trees) - Segment Tree (Point/Range Query & Lazy Propagation), Fenwick Tree (BIT), và XOR Trie.
21. [**Sequence & Alignment DP**](./section-4.html#s-dp-sequences) - Quy hoạch động chuỗi và so khớp dãy số kinh điển: LCS, LIS $O(N \log N)$, Edit Distance, Palindrome, Wildcard Matching.

---

### 💡 So Sánh Go vs JS/TS Khi Giải Thuật Toán trên LeetCode

Việc chuyển dịch từ JavaScript/TypeScript sang Go để code giải thuật có một số thay đổi lớn về cú pháp và tối ưu hóa bộ nhớ:

| JS / TS | Go Equivalent | Đặc thù kỹ thuật & Tối ưu |
| :--- | :--- | :--- |
| `Array.push()` / `pop()` | `append()` / Slicing | Slices trong Go là cửa sổ trỏ vào mảng tĩnh bên dưới. Cắt mảng `slice[:len(slice)-1]` tốn $O(1)$ thời gian và không cần copy. |
| `new Map()` | `make(map[K]V)` | Map trong Go khởi tạo bằng `make`. Cực kỳ nhanh nhưng hãy lưu ý: thứ tự duyệt map là **ngẫu nhiên** ở mỗi lần chạy. |
| `Array.sort()` | `sort.Slice()` | Hàm sort trong Go dùng `sort.Slice(slice, func(i, j int) bool)` nhận vào hàm so sánh chỉ mục, tối ưu hóa in-place. |
| Custom Heap Class | `container/heap` | Go không có lớp Heap mặc định. Bạn cần định nghĩa một struct cài đặt đủ 5 phương thức của `heap.Interface` (`Len`, `Less`, `Swap`, `Push`, `Pop`). |
| `null` check | `nil` check | Trong các bài toán Linked List/Tree, luôn kiểm tra `if node == nil` trước khi truy cập con trỏ con để tránh lỗi Panic runtime. |
| Recursion Stack | Goroutine Dynamic Stack | JS có call stack giới hạn. Go goroutine stack ban đầu cực kỳ nhẹ (2KB) và tự mở rộng linh hoạt, rất lý tưởng cho đệ quy sâu (DFS). |

#### 🛠️ Cách cài đặt Min/Max Heap chuẩn trong Go:
Để dùng Heap trong Go, hãy nhớ mẫu khai báo sau:
```go
import "container/heap"

type IntHeap []int
func (h IntHeap) Len() int           { return len(h) }
func (h IntHeap) Less(i, j int) bool { return h[i] < h[j] } // < là MinHeap, > là MaxHeap
func (h IntHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *IntHeap) Push(x any)        { *h = append(*h, x.(int)) }
func (h *IntHeap) Pop() any {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

// Cách dùng:
h := &IntHeap{2, 1, 5}
heap.Init(h)
heap.Push(h, 3)
minVal := heap.Pop(h).(int) // Phải ép kiểu (type assertion) vì Pop trả về type 'any'
```

---

### 🚀 Gợi Ý Lộ Trình Luyện Tập

1. **Tuần 1**: Foundation (Section 1) - Giải 15 bài Easy/Medium về Two Pointers, Sliding Window và duyệt Tree để làm quen với syntax con trỏ và slices của Go.
2. **Tuần 2**: Graphs & Recursion (Section 2) - Thực hành 10 bài về DFS/BFS trên đồ thị, tập viết các hàm đệ quy Backtracking sinh hoán vị bằng Go.
3. **Tuần 3**: Advanced DSA (Section 3) - Cài đặt cấu trúc Heap tùy chỉnh và Trie tiền tố, giải quyết các bài toán về ma trận và chuỗi.
4. **Tuần 4**: Expert Peak (Section 4) - Thử sức với các bài toán Hard quy hoạch động nâng cao (Bitmask DP), cài đặt Segment Tree xử lý Range Query, và giải quyết triệt để các bài toán Sequence DP kinh điển.
