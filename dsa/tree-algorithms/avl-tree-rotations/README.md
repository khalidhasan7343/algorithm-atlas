# AVL Tree Rotations

## 1. Algorithm Name

AVL Tree Rotations

## 2. Overview

Maintain a height-balanced binary search tree using LL, RR, LR and RL rotations.

## 3. Problem Statement

Maintain an ordered set of integer keys with search, insertion, deletion, sorted enumeration and half-open range queries. Duplicate insertion and absent deletion return false; successful mutations return true.

**API:** `AVLTree().contains(key) / .insert(key) / .erase(key) / .keys() / .range_query(low,high)`. Unique integer keys in [-10^9,10^9], at most 1000 keys; bool is rejected as a Python integer. Empty keys/ranges return []; low≤high and range is [low,high). solve accepts at most 1000 operations: [0,key] insert, [1,key] erase, [2,key] contains, [3] keys, [4,low,high] range. Resource/type/range errors are validated before mutation; duplicate insert at capacity remains a valid false result.

## 4. Why Do We Need This Algorithm?

An ordinary binary search tree becomes a chain under sorted insertions. Structural balance gives logarithmic path lengths for both search and mutation.

## 5. Real-World Applications

In-memory ordered indexes, event dictionaries and bounded symbol tables requiring stable worst-case path lengths.

## 6. Core Intuition

Store each node height and constrain the difference of child heights to at most one. A local rotation changes links while preserving inorder keys.

## 7. Prerequisites

Know BST ordering, recursive subtree ownership and rotations. Understand height recurrences and balance factors. Read the [shared conventions](../../../docs/tree-conventions.md).

## 8. Step-by-Step Working Process

Search first to handle duplicate/absent operations without mutation. Insert recursively, refresh heights while unwinding and apply a single LL/RR or double LR/RL rotation at an imbalance. Delete a zero/one-child node directly; replace a two-child key with its inorder successor, remove that successor, then rebalance every ancestor, including the root.

**Correctness and invariants:** Rotations preserve the inorder sequence because the transferred middle subtree lies between the rotated keys. Refreshing the lower node before the upper node restores exact heights. Each insert/delete changes a child height by at most one; the four orientation cases restore balance, and processing every ancestor proves the invariant globally. Successor replacement preserves strict ordering and removes exactly one record.

## 9. Pseudocode

```text
height(null)=0; refresh(u)=1+max(height(left),height(right))
if balance(u)>1: rotate right (rotate left child first for LR)
if balance(u)<-1: rotate left (rotate right child first for RL)
insert: BST insert; refresh and rebalance on return
erase: BST successor deletion; refresh and rebalance on return
```

## 10. Dry Run

Inserting 3,1,2 creates LR imbalance: rotate 1 left, then 3 right, giving root 2 and children 1,3. Deleting root 2 replaces its key with successor 3 and restores stored height.

## 11. Time Complexity

O(log n) contains, insert and erase; the AVL height recurrence N(h)≥1+N(h-1)+N(h-2) bounds h=O(log n). keys() costs O(n); pruned range_query costs O(log n+k) for k returned keys.

## 12. Space Complexity

O(n) nodes and O(log n) recursive mutation/range stacks; inorder enumeration uses O(log n) explicit stack plus output. n≤1000 keeps recursive ownership destruction and Python calls bounded by balanced height.

## 13. Python Implementation

Read the canonical [`python/solution.py`](python/solution.py). Nodes hold real left/right child references; recursive functions return the repaired subtree root. The class owns its topology; no built-in ordered collection implements the search or mutation logic. `solve` is the executable adapter. Invalid types (including bool as integer), dimensions and references raise ValueError; CLI input failures exit 2.

## 14. C++ Implementation

Read [`cpp/solution.cpp`](cpp/solution.cpp) in namespace `atlas_tree`. Compile with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-tree-example`, or C++20. Define ALGORITHM_ATLAS_NO_MAIN in API drivers. Nodes own unique_ptr children. Rotations move ownership without retaining invalidated references; public read-only root() inspection supports independent invariant tests. No parent pointers or external-node handles are exposed. Failed contracts throw invalid_argument; the executable prints an error on stderr and exits 2.

## 15. Input and Output Examples

Python JSON input:
```json
{"operations":[[0,3],[0,1],[0,2],[0,2],[3],[2,1],[1,2],[4,1,3],[1,9],[3]]}
```
C++ text input:
```text
10 0 3 0 1 0 2 0 2 3 2 1 1 2 4 1 3 1 9 3
```
Grammar: q, then q operations with the opcode/arity above; booleans and arrays serialize as JSON.

Both output:
```json
[true,true,true,false,[1,2,3],true,true,[1],false,[1,3]]
```
No arithmetic combines key values. Comparisons use signed 64-bit C++ keys within ±10^9; heights, sizes and color counts are bounded by 1000 nodes. None/null is an absent child, not a sentinel key, so both key extremes are valid.

## 16. Edge Cases

Empty transitions, root deletion, successor deletion, duplicates, numeric extremes, sorted and reverse insertions, capacity rejection and complete draining are covered. Explicit triples independently trigger all four rotation orientations.

[Independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py) execute empty/minimal, invalid, duplicate, balanced/skewed and bounded stress inputs. 219 exhaustive/small/random streams (seed 8404) use independent Python set/sorted expectations, with every actual node inspected after each operation in Python and both C++ standards. Capacity/drain tests validate every mutation over 1000 keys. Inspectors verify strict BST bounds, exact heights and balance factors. Tests compare both languages with the same independent expectations, rather than relying only on agreement.

## 17. Advantages

Tight height control and explicit height metadata.

## 18. Disadvantages and Limitations

Deletion may rebalance multiple ancestors; node heights must be refreshed in the correct order. The implementation is a bounded in-memory set, not a concurrent, persistent or disk-backed index.

## 19. When to Use It

Use when ordered operations need predictable logarithmic search paths.

## 20. When Not to Use It

Use a hash set for exact-only lookup, or a multiway tree for block-oriented storage.

## 21. Comparison With Related Algorithms

AVL stores heights and constrains local height differences. Red-Black stores colors and constrains black height; both implement identical key-set semantics and are compared with an independent set. B-Trees use wider nodes rather than binary links.

[red-black-tree-operations](../red-black-tree-operations/README.md), [b-tree-operations](../b-tree-operations/README.md)

## 22. Interview Questions

How do LR and RL differ from LL and RR? Why can deletion need repairs at multiple ancestors?

## 23. Practice Problems

Trace root deletion, insert sorted keys and erase alternating extremes; inspect the actual node structure after every mutation and compare keys with an independent ordered reference.

## 24. References

[Cornell CS2112 AVL lecture](https://www.cs.cornell.edu/courses/cs2112/2021fa/lectures/avl/). The exact bounded API, tie rules and serialization grammar are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
