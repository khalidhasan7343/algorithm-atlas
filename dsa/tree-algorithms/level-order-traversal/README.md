# Level Order Traversal

## 1. Algorithm Name

Level Order Traversal

## 2. Overview

Visit a validated binary tree in grouped breadth-first depth order.

## 3. Problem Statement

Return node IDs grouped by depth, retaining identity even when values repeat. Empty input returns [].

**API:** `level_order(values, children, root=None)`. Single connected binary tree, n≤10000; values in [-10^9,10^9]. Children are pairs of IDs or None; root is mandatory for nonempty input. Validation rejects cycles, shared children, unreachable nodes and invalid references. Inputs are copied and never mutated.

## 4. Why Do We Need This Algorithm?

Tree-processing tasks need a specific order. Using values as identities would incorrectly merge distinct equal-valued nodes.

## 5. Real-World Applications

Tree width/depth displays, level summaries and nearest-depth exploration.

## 6. Core Intuition

A FIFO queue preserves increasing depth while node IDs refer to copied child slots, not value equality.

## 7. Prerequisites

Know parent/child relationships, node identity, stacks/queues, array indexing and asymptotic analysis. Read the [shared contracts](../../../docs/tree-conventions.md) first.

## 8. Step-by-Step Working Process

Enqueue the root. Freeze the current queue length as a level width. Pop that many nodes in FIFO order, enqueue each left child before its right child, then append the completed level.

**Correctness and invariants:** At the start of an iteration the queue contains exactly one depth, left to right. Processing that frozen width appends precisely its children in the same order, proving the next-level invariant. Unique ownership prevents repeated visits.

## 9. Pseudocode

```text
queue=[root] if present
while queue:
    width=len(queue); level=[]
    repeat width times:
        u=pop_front(); level.append(u)
        enqueue left(u), then right(u), when present
    levels.append(level)
```

## 10. Dry Run

Queue [0] yields level [0] and children [1,2]; those yield [1,2] and children [3,4]; the final level contains those leaves.

## 11. Time Complexity

O(n) end to end: validation and traversal each visit every node and child slot once.

## 12. Space Complexity

O(n) including copied input, validation visited state and output. The traversal alone uses O(w) queue space, where w is maximum width. A recursive DFS uses O(h) call frames and can exceed language limits on a chain; this implementation is iterative. A balanced tree has h=O(log n), a chain h=n.

## 13. Python Implementation

Read the canonical [`python/solution.py`](python/solution.py). The algorithm uses standard-library containers and explicit traversal state; shared support validates copied input and JSON. `solve` is the executable adapter. Invalid types (including bool as integer), dimensions and references raise ValueError; CLI input failures exit 2.

## 14. C++ Implementation

Read [`cpp/solution.cpp`](cpp/solution.cpp) in namespace `atlas_tree`. Compile with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-tree-example`, or C++20. Define ALGORITHM_ATLAS_NO_MAIN in API drivers. A validated BinaryTree owns arrays, so deep shapes do not create recursive node destruction. Core functions take const input. Failed contracts throw invalid_argument; the executable prints an error on stderr and exits 2.

## 15. Input and Output Examples

Python JSON input:
```json
{"values":[8,4,8,2,6],"children":[[1,2],[3,4],[null,null],[null,null],[null,null]],"root":0}
```
C++ text input:
```text
5 0 8 4 8 2 6 1 2 3 4 -1 -1 -1 -1 -1 -1
```
Grammar: n root, then n values, then n left/right child pairs; -1 means absent.

Both output:
```json
[[0],[1,2],[3,4]]
```
Indices, lengths and traversal counts are bounded by n≤10000. Values are preserved within ±10^9; this traversal does not sum or multiply them.

## 16. Edge Cases

Duplicate values at IDs 0 and 2 remain distinct. A left chain and a right chain yield different inorder results; a real queue is necessary for grouped levels. Empty and singleton trees are valid.

[Independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py) execute empty/minimal, invalid, duplicate, balanced/skewed and bounded stress inputs. Every binary shape through five nodes (65 shapes) and 160 seed-8101 relabeled random trees use independently recursive references. Level references group a DFS by depth rather than implementing another queue. Boundary tests construct expected 10000-node chain orders directly. Tests compare both languages with the same independent expectations, rather than relying only on agreement.

## 17. Advantages

Deterministic order, explicit node identity and safe deep-tree traversal without recursion.

## 18. Disadvantages and Limitations

A tree is required, not a graph or DAG with shared children. Shape validation and owned input copies add O(n) memory. Traversal output does not enforce BST ordering by value.

## 19. When to Use It

Use when this order matches the dependency between parent and child processing.

## 20. When Not to Use It

Use Graph DFS/BFS for arbitrary cycles or shared-node graphs. Choose a different tree traversal when its parent/child visitation order fits the task.

## 21. Comparison With Related Algorithms

Recursive traversals offer a compact definition but depend on call-stack depth. Iterative DFS stacks encode those calls; level order uses FIFO breadth-first traversal. The canonical Graph BFS remains a separate graph-input algorithm.

[preorder-traversal](../preorder-traversal/README.md), [postorder-traversal](../postorder-traversal/README.md)

## 22. Interview Questions

Why must child identity use IDs? How does stack push order affect output? Which tree shape maximizes auxiliary memory?

## 23. Practice Problems

Map returned IDs back to values; trace left/right chains; compare recursive references on small trees with the iterative implementation and explain why inorder is sorted only for a BST.

## 24. References

[Competitive Programmer’s Handbook, binary trees](https://cses.fi/book/book.pdf). The exact bounded API, tie rules and serialization grammar are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
