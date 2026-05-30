<!-- tags: dsa, algorithms, searching, binary-search -->
# 🎯 Binary Search

> Binary search teaches you to discard half the search space using invariants instead of checking every element. You will fail edge cases if you cannot identify the region still holding the answer.

📅 Created: 2026-03-20 · 🔄 Updated: 2026-04-10 · ⏱️ 18 min read

| Aspect | Detail |
| ------ | ------ |
| **Complexity** | O(log n) time · O(1) iterative space |
| **Use case** | Sorted array, boundary finding, insertion point |
| **Recognition** | Monotone order allows discarding half the search domain |

---

## 1. DEFINE

<!-- [Experienced layer] -->

<!-- [Beginner layer] -->
You have a sorted array and need `23`. Scanning sequentially wastes the strongest given structural advantage. Elements left of `mid` remain smaller than or equal to `arr[mid]`. Elements right of it remain larger. Each comparison can eliminate half the array.

<!-- [Experienced layer] -->
`Binary Search` maintains a `[lo, hi]` range that can still contain the answer. At each step:
- pick `mid`
- compare with target
- discard the invalid half

Core insight: **binary search is not picking the middle number, but maintaining a valid candidate region invariant**.

| Variant | Question Answered | Boundary Target | Example |
| ------- | --------------- | ---------------- | ------- |
| **Exact match** | Where is the target? | Any match | Intro binary search |
| **Lower bound** | First index `>= target` | First true | Insertion point |
| **Upper bound** | First index `> target` | First true on strict condition | Count occurrences |

| Approach | Time | Space | When to pick |
| -------- | ---- | ----- | -------- |
| Linear search | O(n) | O(1) | Unsorted data or small n |
| Binary search | O(log n) | O(1) | Sorted data with random access |

### 1.1 Quick Recognition

- Sorted data
- Random access takes O(1) time
- Each comparison discards half the remaining domain

### 1.2 Invariants & Failure Modes

<!-- [Expert layer] -->
- An exact match loop using `lo <= hi` keeps the target inside the closed `[lo, hi]` range.
- A lower or upper bound loop using `lo < hi` keeps the answer inside the half-open `[lo, hi)` range.
- The most common failure mode involves updating boundaries without respecting the chosen invariant.

---

## 2. VISUAL

This image answers the core question: **which region retains the right to hold the answer after each step?**

![Binary Search — Invariant: answer ∈ [lo, hi]](../images/binary-search-invariant.png)

These static traces ground the invariant in real data if the concept feels abstract. They prepare your mind before entering the playground.

### Level 1 — Simple
This trace answers: **which half does binary search discard at each step?**

```text
nums   = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
target = 23

lo=0 hi=9  -> mid=4 -> nums[4]=16 < 23
=> discard [0..4], keep [5..9]

lo=5 hi=9  -> mid=7 -> nums[7]=56 > 23
=> discard [7..9], keep [5..6]

lo=5 hi=6  -> mid=5 -> nums[5]=23 ✅
```
*Figure: Binary search works safely when each comparison definitively eliminates an invalid half.*

### Level 2 — Detailed
This trace answers: **how do lower bound and upper bound differ?**

```text
nums   = [1, 3, 3, 3, 5, 7]
target = 3

lower_bound(3) = first index where nums[i] >= 3 = 1
upper_bound(3) = first index where nums[i] >  3 = 4

count(target) = upper_bound - lower_bound = 3
```
*Figure: Exact match yields one valid position, while lower and upper bounds define a region.*

## 3. PLAYGROUND

The PNG above helps scan the invariant quickly. Binary search only clicks when you watch boundaries shift on real inputs. This playground respects the closed-range reasoning, allowing you to manipulate inputs and track state.

- observe which step reads `nums[mid]`
- see which half leaves the candidate region
- track which boundary update sustains the invariant

Once you internalize the flow, the code loses its rote-memorization feel. Every boundary update clearly serves a specific invariant.

::: algorithm-playground
src: ./playgrounds/02-binary-search.playground.yml
:::

## 4. CODE

The trace shows the flow. We implement the clean baseline before moving to the memorable variants.


### Problem 1: Exact Match Binary Search
> *(Basic form to lock down the `[lo, hi]` invariant first.)*
>
> **Goal**: Return the index of the target or `-1`
> **Approach**: Candidate region remains a closed `[lo, hi]` range
> **Example**: `[2,5,8,12,16,23], target=12` → `3`

```go
// binary_search.go — Searching: Exact match binary search
func BinarySearch(nums []int, target int) int {
    lo, hi := 0, len(nums)-1
    for lo <= hi {
        mid := lo + (hi-lo)/2
        if nums[mid] == target {
            return mid
        }
        if nums[mid] < target {
            lo = mid + 1
        } else {
            hi = mid - 1
        }
    }
    return -1
}
```
```typescript
// binary_search.ts — Searching: Exact match binary search
function binarySearch(nums: number[], target: number): number {
    let lo = 0;
    let hi = nums.length - 1;

    while (lo <= hi) {
        const mid = lo + Math.floor((hi - lo) / 2);
        if (nums[mid] === target) return mid;
        if (nums[mid] < target) lo = mid + 1;
        else hi = mid - 1;
    }

    return -1;
}
```
```java
// BinarySearchBasic.java — Searching: Exact match binary search
final class BinarySearchBasic {
    private BinarySearchBasic() {}

    static int binarySearch(int[] nums, int target) {
        int lo = 0;
        int hi = nums.length - 1;

        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2;
            if (nums[mid] == target) return mid;
            if (nums[mid] < target) lo = mid + 1;
            else hi = mid - 1;
        }

        return -1;
    }
}
```
```rust
// binary_search.rs — Searching: Exact match binary search
fn binary_search(nums: &[i32], target: i32) -> isize {
    let (mut lo, mut hi) = (0isize, nums.len() as isize - 1);

    while lo <= hi {
        let mid = lo + (hi - lo) / 2;
        match nums[mid as usize].cmp(&target) {
            std::cmp::Ordering::Equal => return mid,
            std::cmp::Ordering::Less => lo = mid + 1,
            std::cmp::Ordering::Greater => hi = mid - 1,
        }
    }

    -1
}
```
```cpp
// binary_search.cpp — Searching: Exact match binary search
int binarySearch(const std::vector<int>& nums, int target) {
    int lo = 0;
    int hi = static_cast<int>(nums.size()) - 1;

    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] == target) return mid;
        if (nums[mid] < target) lo = mid + 1;
        else hi = mid - 1;
    }

    return -1;
}
```
```python
# binary_search.py — Searching: Exact match binary search
def binary_search(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1

    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1

    return -1
```

> **Why?** Success hinges on the invariant rather than the midpoint formula. The invariant states the target always sits inside the closed `[lo, hi]` interval. Every boundary update must preserve this logic.

> **Conclusion**: This basic case locks the closed interval concept. Most binary search bugs originate from boundary mismanagement.

---

### Problem 2: Lower Bound / Upper Bound
> *(A more practical application because many problems demand finding boundaries instead of exact values.)*
>
> **Goal**: Find the insertion point to count target occurrences
> **Approach**: Write two tailored binary searches for boundaries
> **Example**: `[1,3,3,3,5,7], target=3` → `lower=1`, `upper=4`, `count=3`

```go
// bounds.go — Searching: Lower bound and upper bound
func LowerBound(nums []int, target int) int {
    lo, hi := 0, len(nums)
    for lo < hi {
        mid := lo + (hi-lo)/2
        if nums[mid] < target {
            lo = mid + 1
        } else {
            hi = mid
        }
    }
    return lo
}

func UpperBound(nums []int, target int) int {
    lo, hi := 0, len(nums)
    for lo < hi {
        mid := lo + (hi-lo)/2
        if nums[mid] <= target {
            lo = mid + 1
        } else {
            hi = mid
        }
    }
    return lo
}
```
```typescript
// bounds.ts — Searching: Lower bound and upper bound
function lowerBound(nums: number[], target: number): number {
    let lo = 0;
    let hi = nums.length;
    while (lo < hi) {
        const mid = lo + Math.floor((hi - lo) / 2);
        if (nums[mid] < target) lo = mid + 1;
        else hi = mid;
    }
    return lo;
}

function upperBound(nums: number[], target: number): number {
    let lo = 0;
    let hi = nums.length;
    while (lo < hi) {
        const mid = lo + Math.floor((hi - lo) / 2);
        if (nums[mid] <= target) lo = mid + 1;
        else hi = mid;
    }
    return lo;
}
```
```java
// BinarySearchIntermediate.java — Searching: Lower bound and upper bound
final class BinarySearchIntermediate {
    private BinarySearchIntermediate() {}

    static int lowerBound(int[] nums, int target) {
        int lo = 0;
        int hi = nums.length;
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if (nums[mid] < target) lo = mid + 1;
            else hi = mid;
        }
        return lo;
    }

    static int upperBound(int[] nums, int target) {
        int lo = 0;
        int hi = nums.length;
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if (nums[mid] <= target) lo = mid + 1;
            else hi = mid;
        }
        return lo;
    }
}
```
```rust
// bounds.rs — Searching: Lower bound and upper bound
fn lower_bound(nums: &[i32], target: i32) -> usize {
    let (mut lo, mut hi) = (0usize, nums.len());
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        if nums[mid] < target {
            lo = mid + 1;
        } else {
            hi = mid;
        }
    }
    lo
}

fn upper_bound(nums: &[i32], target: i32) -> usize {
    let (mut lo, mut hi) = (0usize, nums.len());
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        if nums[mid] <= target {
            lo = mid + 1;
        } else {
            hi = mid;
        }
    }
    lo
}
```
```cpp
// bounds.cpp — Searching: Lower bound and upper bound
int lowerBound(const std::vector<int>& nums, int target) {
    int lo = 0;
    int hi = static_cast<int>(nums.size());
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] < target) lo = mid + 1;
        else hi = mid;
    }
    return lo;
}

int upperBound(const std::vector<int>& nums, int target) {
    int lo = 0;
    int hi = static_cast<int>(nums.size());
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] <= target) lo = mid + 1;
        else hi = mid;
    }
    return lo;
}
```
```python
# bounds.py — Searching: Lower bound and upper bound
def lower_bound(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

def upper_bound(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

> **Why?** These bounds transform binary search from finding exact values to finding the first boundary satisfying a predicate. This behavior dominates insertion tasks and frequency counting.

> **Conclusion**: This is intermediate because it uses a boundary predicate rather than an exact match.

---

### Problem 3: Search Insert Position [LC #35]
> *(Classic practical problem: finding where a missing target should go.)*
>
> **Goal**: Return the insertion index that maintains sorted order
> **Approach**: The lower bound serves directly as the answer
> **Example**: `[1,3,5,6], target=2` → `1`

```go
// search_insert.go — Searching: Search insert position via lower bound
func SearchInsert(nums []int, target int) int {
    return LowerBound(nums, target)
}
```
```typescript
// search_insert.ts — Searching: Search insert position via lower bound
function searchInsert(nums: number[], target: number): number {
    return lowerBound(nums, target);
}
```
```java
// BinarySearchAdvanced.java — Searching: Search insert position via lower bound
final class BinarySearchAdvanced {
    private BinarySearchAdvanced() {}

    static int searchInsert(int[] nums, int target) {
        return BinarySearchIntermediate.lowerBound(nums, target);
    }
}
```
```rust
// search_insert.rs — Searching: Search insert position via lower bound
fn search_insert(nums: &[i32], target: i32) -> usize {
    lower_bound(nums, target)
}
```
```cpp
// search_insert.cpp — Searching: Search insert position via lower bound
int searchInsert(const std::vector<int>& nums, int target) {
    return lowerBound(nums, target);
}
```
```python
# search_insert.py — Searching: Search insert position via lower bound
def search_insert(nums: list[int], target: int) -> int:
    return lower_bound(nums, target)
```

> **Why?** The insertion point represents the first element `>= target`. This yields the first occurrence for existing targets or the proper slot for missing ones.

> **Conclusion**: This advanced application maps boundary search to a very common real-world API request.

---

## 5. PITFALLS

When search fails, the bug usually hides in boundaries, stop conditions, and structural assumptions rather than the main idea.


| # | Severity | Defect | Consequence | Fix |
|---|----------|-----|---------|-----|
| 1 | 🔴 Fatal | Running binary search on unsorted data | Complete result failure | Re-check the sorted precondition before use |
| 2 | 🔴 Fatal | Mixing `[lo, hi]` and `[lo, hi)` invariants | Infinite loops or off-by-one errors | Choose one invariant and strictly adhere |
| 3 | 🟡 Common | Calculating `(lo + hi) / 2` during overflow | Hidden bugs on large inputs | Use `lo + (hi-lo)/2` |
| 4 | 🟡 Common | Returning early on `nums[mid] == target` while wanting lower bound | Misses the first occurrence | Continue narrowing the domain instead of early exits |

---

## 6. REF

| Resource | Type | Link | Note |
| -------- | ---- | ---- | ------- |
| Binary search | Reference | https://en.wikipedia.org/wiki/Binary_search_algorithm | Exact match and pattern history |
| CP-Algorithms | Reference | https://cp-algorithms.com/num_methods/binary_search.html | Boundary search and predicate view |
| C++ lower_bound | Reference | https://en.cppreference.com/w/cpp/algorithm/lower_bound | Boundary search intuition |
| LeetCode 35 | Problem | https://leetcode.com/problems/search-insert-position/ | Search insert position |

---

## 7. RECOMMEND

When you master this lane, learn when to pivot to neighboring patterns instead of forcing the same template.


| Expansion | When to use | Reason | File/Link |
| ------- | ------- | ----- | --------- |
| Binary Search on Answer | Boundary predicate maps to an answer space | Explores the next layer of boundary reasoning | [../patterns/06-binary-search-on-answer.md](../patterns/06-binary-search-on-answer.md) |
| Exponential Search | Unknown range or early targets | Utilizes binary search after range discovery | [./05-exponential-search.md](./05-exponential-search.md) |

---

## 8. QUICK REF

| Problem Signal | Sub-pattern | Short Template |
| --------------- | ----------- | ------------- |
| `sorted` + exact target | exact match | `[lo, hi]` |
| `first >= x` | lower bound | `[lo, hi)` |
| `first > x` | upper bound | `[lo, hi)` |
| `insert position` | lower bound | answer = first `>= x` |

---

Binary search discards half the space using an invariant. Lower bound, upper bound, and search-on-answer share this exact core. A correct invariant eliminates off-by-one errors completely.

**Links**: [← Linear Search](./01-linear-search.md) · [→ Jump Search](./03-jump-search.md) · [↗ BS on Answer](../patterns/06-binary-search-on-answer.md)
