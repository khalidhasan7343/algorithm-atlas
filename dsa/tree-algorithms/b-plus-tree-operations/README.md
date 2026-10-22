# B+ Tree Operations

## 1. Algorithm Name

B+ Tree Operations

## 2. Overview

Maintain a genuine B+ Tree with leaf-only records, cached internal separators and linked-leaf range iteration.

## 3. Problem Statement

Maintain a unique ordered integer-key set with contains, insert, erase, keys and half-open range_query. Minimum degree t is configurable from 2 through 8; no built-in ordered map implements the tree.

**API:** `BPlusTree(degree=2).contains(key) / .insert(key) / .erase(key) / .keys() / .range_query(low,high)`. t∈[2,8], at most 1000 unique keys in [-10^9,10^9]; duplicates/absent deletions return false. Empty tree is an empty root leaf. Leaf records: maximum 2t−1, minimum nonroot t−1. Internal children: maximum 2t, minimum nonroot t, root at least two; separator count=children−1. Internal separators duplicate leaf records and are not extra members. solve takes degree and q≤1000 operations: 0 insert, 1 erase, 2 contains, 3 keys, 4 low high range [low,high). Invalid key/degree/range and capacity requests reject before mutation.

## 4. Why Do We Need This Algorithm?

Binary trees use one key per node. A multiway tree reduces height by storing several sorted keys and many children per node while preserving balanced leaf depth.

## 5. Real-World Applications

Educational block-oriented index design, database search-tree foundations and bounded ordered dictionaries. This in-memory implementation does not claim real disk pages, persistence or transactions.

## 6. Core Intuition

Only leaves store records. An internal separator is exactly the minimum record in its right-hand child, so equal keys descend right. Leaves link in increasing order for range scans.

## 7. Prerequisites

Know sorted-node binary search, child interval bounds, recursive ownership, split/borrow/merge operations and the distinction between records and separators. See [shared conventions](../../../docs/tree-conventions.md).

## 8. Step-by-Step Working Process

For insertion descend by upper_bound on separators; split an overflowing leaf into t/t records and splice its link. Split an overflowing internal node with 2t+1 children into t and t+1 children; propagate the new sibling upward and grow the root if necessary. For deletion remove a record only in its leaf, then repair underflow upward: borrow from a spare adjacent sibling, otherwise merge. Recompute cached minima and separator arrays after every changed child, splice merged leaf links and contract a one-child root.

**Correctness and invariants:** Upper-bound routing sends each record to its unique half-open child interval. Splits preserve record order and equal leaf depth; internal keys are rebuilt solely from cached minima of right children. Borrowing moves one edge record or child without changing global order; merging adjacent siblings preserves capacity because underflow plus a minimal sibling fits a node. Refreshing minima on every return handles separator changes even without underflow. Splicing leaf next pointers on split/merge keeps the link chain identical to structural leaf order. Root growth/contraction changes all leaf depths equally.

## 9. Pseudocode

```text
insert(node,key):
    leaf: insert record; overflow at 2t -> split t/t, update next
    internal: insert returned sibling; refresh separators
    overflow at 2t+1 children -> split t/(t+1)
erase(node,key):
    leaf: remove record
    internal: recurse; if child underfull borrow left/right or merge
    refresh cached minima/separators
root with one child -> replace by that child
range(low,high): seek leaf(low); follow next links until key>=high
```

## 10. Dry Run

At t=2, inserting 1..4 overflows the root leaf and creates leaves [1,2] and [3,4], separator 3. Range [2,4) follows the leaf link and returns [2,3]. Deleting 2 leaves [1]; deleting 1 causes repair/merge, eventually contracting the root back into one leaf.

## 11. Time Complexity

For variable t and height h=O(log_t(n+1)), search uses O(h log t) comparisons; insertion/deletion cost O(t h) because node-vector shifts, cached separator rebuilds and splits/merges cost O(t). With the documented t∈[2,8], these are O(log(n+1)). keys() costs O(n). A linked-leaf range scan costs O(h log t+k+1), visiting only the initial search path and leaves containing k output records (nonroot leaves are nonempty).

## 12. Space Complexity

O(n) records/nodes plus O(n) cached duplicate separators and non-owning leaf links. Recursive mutation/inspection stacks use O(log_t(n+1)); output occupies O(k). No flattened collection replaces the node hierarchy.

## 13. Python Implementation

Read the canonical [`python/solution.py`](python/solution.py). Each node owns distinct child-node references and local sorted keys. A cached subtree minimum makes separator refresh O(t); next references are non-owning traversal links. `solve` is the executable adapter. Invalid types (including bool as integer), dimensions and references raise ValueError; CLI input failures exit 2.

## 14. C++ Implementation

Read [`cpp/solution.cpp`](cpp/solution.cpp) in namespace `atlas_tree`. Compile with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-tree-example`, or C++20. Define ALGORITHM_ATLAS_NO_MAIN in API drivers. Node children use unique_ptr ownership; local vectors move owned subtrees during splits, redistribution and merges. Raw next pointers never own leaves; leaf merging splices around the deleted right leaf before it is destroyed. Public const root() enables independent topology inspection. Failed contracts throw invalid_argument; the executable prints an error on stderr and exits 2.

## 15. Input and Output Examples

Python JSON input:
```json
{"degree":2,"operations":[[0,1],[0,2],[0,3],[0,4],[3],[4,2,4],[1,2],[2,2],[1,1],[1,3],[1,4],[3]]}
```
C++ text input:
```text
2 12 0 1 0 2 0 3 0 4 3 4 2 4 1 2 2 2 1 1 1 3 1 4 3
```
Grammar: degree, q, then q variable-width opcode operations. keys/ranges return JSON arrays, mutations and contains return booleans.

Both output:
```json
[true,true,true,true,[1,2,3,4],[2,3],true,false,true,true,true,[]]
```
Keys are only compared and copied, never added or multiplied. C++ signed 64-bit keys cover ±10^9. Bounded degree controls per-node vector sizes, and n≤1000 bounds height, recursion and ownership cleanup. Separator caching stores optional minimum; an empty root leaf has no minimum rather than reserving a key value.

## 16. Edge Cases

Empty root, numeric extremes, duplicate at capacity, internal/root deletion, ordered/reverse insertion, randomized removal, all degrees 2..8, root splits/contraction and complete drain are covered. Inspections compare separators with actual right-subtree minima and verify every next pointer agrees with structural leaf order.

[Independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py) execute empty/minimal, invalid, duplicate, balanced/skewed and bounded stress inputs. 876 streams (219 each at degrees 2,3,4,8, seed 8505) compare exact results against Python set/sorted oracles and inspect every actual node after every operation in both languages. Separate mutation-by-mutation 600-key randomized insert/drain tests cover every degree 2..8 and assert split/borrow-left/borrow-right/merge/root-contraction counters; B-Tree also asserts predecessor/successor deletion. A 1000-key capacity test drains in reverse with every mutation inspected. Tests compare both languages with the same independent expectations, rather than relying only on agreement.

## 17. Advantages

Leaf-only records and sequential leaf scans; internal separators contain only routing information.

## 18. Disadvantages and Limitations

Separator minima and leaf links must be updated on every structural change. This is a set of keys, not a key/value or multiset database engine. No persistence, concurrency, page-size model or crash recovery is implemented.

## 19. When to Use It

Use to study complete multiway balanced operations and the invariants underlying block indexes.

## 20. When Not to Use It

Use a production storage engine when durable or concurrent indexing is required; choose a simpler binary tree for a small in-memory API without page concerns.

## 21. Comparison With Related Algorithms

B-Tree stores records in all nodes and promotes/removes records during splits. B+ Tree stores records only in linked leaves and copies minimum-of-right separators into internal nodes. Their Python/C++ key-set outputs agree, but their occupancy, deletion and structural inspections are separate.

[b-tree-operations](../b-tree-operations/README.md), [red-black-tree-operations](../red-black-tree-operations/README.md)

## 22. Interview Questions

Why must equality route right? How does deleting a child minimum affect a separator even without underflow? How are next pointers repaired after a merge?

## 23. Practice Problems

For each degree, build multiple levels and erase all keys in several orders; draw borrow/merge cases and verify every occupancy boundary. Compare range queries with a sorted independent reference.

## 24. References

[Virginia Tech OpenDSA, B-Trees and B+ Trees](https://opendsa-server.cs.vt.edu/ODSA/Books/CS3/html/BTree.html). The exact minimum-degree and separator conventions above define this implementation. The exact bounded API, tie rules and serialization grammar are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
