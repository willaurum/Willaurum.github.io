# Week 3: Deque

**Deque in Python (`collections.deque`)**
- **Deque** = *double-ended queue* → allows O(1) insert/remove from **both ends**.
- Faster than lists for operations at the front (`popleft`, `appendleft`).
- Perfect for problems with **sliding windows**, **reversals**, or **queue simulation**.

## Key Operations

```python
from collections import deque

dq = deque([1, 2, 3])

dq.append(4)      # add to the right → [1, 2, 3, 4]
dq.appendleft(0)  # add to the left  → [0, 1, 2, 3, 4]

dq.pop()          # remove from the right → returns 4, dq = [0, 1, 2, 3]
dq.popleft()      # remove from the left  → returns 0, dq = [1, 2, 3]
```

## Append & Pop Basics

- `append(x)` → add `x` to the right end.
- `appendleft(x)` → add `x` to the left end.
- `pop()` → remove and return the rightmost element.
- `popleft()` → remove and return the leftmost element.

## Competitive Programming Uses

- **Reversals** → toggle a flag, pop from correct end.
- **Sliding window min/max** (O(n) vs O(n²)).
- **AC problem (Baekjoon 5430)** → efficiently remove front/back elements.

## Rule of thumb

If you need frequent pops from both ends, use `deque`.

> *Note: This could be used in this week's medium problem*

## Performance Benefits

While regular Python lists are great for most operations, they become slow when you need to add or remove items from the front. A deque solves this problem:

- List operations at the front: O(n) time complexity
- Deque operations at both ends: O(1) time complexity

This makes deque essential for algorithms that need efficient access to both ends of a sequence.