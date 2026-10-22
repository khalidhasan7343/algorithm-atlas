# Red-Black Tree Operations

## 1. Algorithm Name

Red-Black Tree Operations

## 2. Overview

Maintain a genuine left-leaning Red-Black search tree with complete top-down deletion and color repair.

## 3. Problem Statement

Maintain an ordered set of integer keys with search, insertion, deletion, sorted enumeration and half-open range queries. Duplicate insertion and absent deletion return false; successful mutations return true.

**API:** `RedBlackTree().contains(key) / .insert(key) / .erase(key) / .keys() / .range_query(low,high)`. Unique integer keys in [-10^9,10^9], at most 1000 keys; bool is rejected as a Python integer. Empty keys/ranges return []; low≤high and range is [low,high). solve accepts at most 1000 operations: [0,key] insert, [1,key] erase, [2,key] contains, [3] keys, [4,low,high] range. Resource/type/range errors are validated before mutation; duplicate insert at capacity remains a valid false result.

## 4. Why Do We Need This Algorithm?

An ordinary binary search tree becomes a chain under sorted insertions. Structural balance gives logarithmic path lengths for both search and mutation.

## 5. Real-World Applications

In-memory ordered indexes, event dictionaries and bounded symbol tables requiring stable worst-case path lengths.

## 6. Core Intuition

Red links encode a logical 3-node in a 2–3 tree. Left-leaning links, no adjacent reds and equal black height keep all search paths within a constant factor of one another.

## 7. Prerequisites

Know BST ordering, recursive subtree ownership and rotations. Understand red/black links and the equivalence to balanced 2–3 trees. Read the [shared conventions](../../../docs/tree-conventions.md).

## 8. Step-by-Step Working Process

Insert recursively as red, rotate a right-only red link left, rotate consecutive left reds right and split a temporary 4-node by flipping colors. Force the root black. Before descending during deletion, move a red link toward a minimal child using color flips and rotations. Replace an internal deleted key with its successor and delete the minimum in its right subtree; fix links while unwinding and restore a black root.

**Correctness and invariants:** The left-leaning representation encodes a balanced 2–3 tree. Rotations preserve inorder order and transfer the old parent color; flips redistribute a 4-node without changing path black height. move_red helpers prevent descending into a 2-node that cannot safely lose a record. Successor replacement preserves ordering, and fix restores lean/red adjacency/black-height invariants on return. Restoring a black root completes the red-black conditions; null leaves count as black.

## 9. Pseudocode

```text
NIL=null, always black
insert: BST red leaf; rotate/flip on return; root.black=true
erase:
    if both root children black: color root red temporarily
    before entering a black 2-node: move_red_left/right
    remove leaf or replace with successor and delete_min
    fix right red links, consecutive left reds and 4-nodes
    if root exists: color it black
```

## 10. Dry Run

Inserting 3,1,2 rotates the red links and flips a temporary 4-node, leaving black root 2. Deleting 2 uses its successor and top-down color repair; keys 1 and 3 remain. A duplicate 2 inserted earlier changed nothing.

## 11. Time Complexity

O(log n) contains, insert and erase; a red-black path has at most twice its black height, and equal black height implies h≤2 log2(n+1). keys() costs O(n); pruned range_query costs O(log n+k) for k returned keys.

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

Empty transitions, root deletion, successor deletion, duplicates, numeric extremes, sorted and reverse insertions, capacity rejection and complete draining are covered. Deterministic capacity/drain tests assert both rotations, color flips and both move-red deletion repairs occur.

[Independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py) execute empty/minimal, invalid, duplicate, balanced/skewed and bounded stress inputs. 219 exhaustive/small/random streams (seed 8404) use independent Python set/sorted expectations, with every actual node inspected after each operation in Python and both C++ standards. Capacity/drain tests validate every mutation over 1000 keys. Inspectors verify strict BST bounds, black root, no red-red edge, equal black height and the stronger left-leaning condition. Tests compare both languages with the same independent expectations, rather than relying only on agreement.

## 17. Advantages

Worst-case logarithmic operations with a compact color-based balance representation.

## 18. Disadvantages and Limitations

This is the left-leaning variant, with null black leaves, not a parent-pointer CLRS sentinel implementation. Its deletion helpers depend on the documented leaning invariants. The implementation is a bounded in-memory set, not a concurrent, persistent or disk-backed index.

## 19. When to Use It

Use when ordered operations need predictable logarithmic search paths.

## 20. When Not to Use It

Use a hash set for exact-only lookup, or a multiway tree for block-oriented storage.

## 21. Comparison With Related Algorithms

AVL stores heights and constrains local height differences. Red-Black stores colors and constrains black height; both implement identical key-set semantics and are compared with an independent set. B-Trees use wider nodes rather than binary links.

[avl-tree-rotations](../avl-tree-rotations/README.md), [b-tree-operations](../b-tree-operations/README.md)

## 22. Interview Questions

Why are null leaves black? How do color flips preserve black height? Why must deletion avoid entering a minimal 2-node?

## 23. Practice Problems

Trace root deletion, insert sorted keys and erase alternating extremes; inspect the actual node structure after every mutation and compare keys with an independent ordered reference.

## 24. References

[Princeton RedBlackBST documentation](https://algs4.cs.princeton.edu/code/javadoc/edu/princeton/cs/algs4/RedBlackBST.html), left-leaning insertion and deletion. The exact bounded API, tie rules and serialization grammar are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
