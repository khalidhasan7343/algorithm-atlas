# B-Tree Operations

## 1. Algorithm Name

B-Tree Operations

## 2. Overview

Maintain a genuine B-Tree with records in both internal nodes and leaves, including full top-down deletion.

## 3. Problem Statement

Maintain a unique ordered integer-key set with contains, insert, erase, keys and half-open range_query. Minimum degree t is configurable from 2 through 8; no built-in ordered map implements the tree.

**API:** `BTree(degree=2).contains(key) / .insert(key) / .erase(key) / .keys() / .range_query(low,high)`. t∈[2,8], at most 1000 unique keys in [-10^9,10^9]; duplicates/absent deletions return false. Empty tree is an empty root leaf. Every node has at most 2t−1 records; nonroots have at least t−1. Internal nodes have records+1 children; a nonleaf root has at least one record and two children. solve takes degree and q≤1000 operations: 0 insert, 1 erase, 2 contains, 3 keys, 4 low high range [low,high). Invalid key/degree/range and capacity requests reject before mutation.

## 4. Why Do We Need This Algorithm?

Binary trees use one key per node. A multiway tree reduces height by storing several sorted keys and many children per node while preserving balanced leaf depth.

## 5. Real-World Applications

Educational block-oriented index design, database search-tree foundations and bounded ordered dictionaries. This in-memory implementation does not claim real disk pages, persistence or transactions.

## 6. Core Intuition

A node with k sorted records separates k+1 child intervals. Full nodes split around a promoted median; deletion preserves occupancy by borrowing or merging before descent.

## 7. Prerequisites

Know sorted-node binary search, child interval bounds, recursive ownership, split/borrow/merge operations and the distinction between records and separators. See [shared conventions](../../../docs/tree-conventions.md).

## 8. Step-by-Step Working Process

Search with lower_bound in each sorted node. Before insertion descend only into a non-full child, splitting a full child and promoting its median. Split a full root first. For deletion, remove a leaf record; for an internal record use a predecessor/successor from a child with at least t records, otherwise merge the two minimal children with the record. Before descending toward an absent-in-node target, strengthen a t−1-key child by borrowing from a spare sibling or merging. Contract an empty internal root.

**Correctness and invariants:** A split partitions a full child into two valid t−1-key nodes around a promoted median, preserving sorted interval ownership and leaf depth. Insertion therefore enters a node with room. During deletion a child is strengthened to at least t keys before descent, so one removed key cannot underfill it. Internal successor/predecessor replacement preserves strict BST intervals, while merging two minimal children with their parent record yields exactly 2t−1 keys. Borrowing preserves child counts and order. Root contraction removes a level uniformly; induction establishes occupancy and equal-depth invariants after every mutation.

## 9. Pseudocode

```text
insert: split full root; descend, splitting full child before entry
split: retain t−1 keys left/right, promote median to parent
erase internal record:
    replace by predecessor if left has ≥t keys
    else successor if right has ≥t keys
    else merge both children and parent record, then recurse
erase down a path: strengthen t−1-key child before descent
borrow: rotate sibling key through parent
merge: combine t−1 + parent + t−1 keys
empty internal root -> replace by only child
```

## 10. Dry Run

At t=2, inserting 1,2,3 fills the root. Before inserting 4, promote median 2 into a new root with children [1] and [3]; right becomes [3,4]. Deleting internal 2 uses successor 3 from its spare right child. Later deletions merge minimal children and contract the root.

## 11. Time Complexity

For variable t and height h=O(log_t(n+1)), search uses O(h log t) comparisons; insertion/deletion cost O(t h) because node-vector shifts, splits/borrows/merges cost O(t). With the documented t∈[2,8], these are O(log(n+1)). keys() costs O(n). A pruned range traversal costs O(t h+k) including boundary-node work, O(log(n+1)+k) for bounded t.

## 12. Space Complexity

O(n) records/nodes plus child ownership links. Recursive mutation/inspection stacks use O(log_t(n+1)); output occupies O(k). No flattened collection replaces the node hierarchy.

## 13. Python Implementation

Read the canonical [`python/solution.py`](python/solution.py). Each node owns distinct child-node references and local sorted keys. Recursive top-down methods split and strengthen actual children; no built-in collection substitutes for tree operations. `solve` is the executable adapter. Invalid types (including bool as integer), dimensions and references raise ValueError; CLI input failures exit 2.

## 14. C++ Implementation

Read [`cpp/solution.cpp`](cpp/solution.cpp) in namespace `atlas_tree`. Compile with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-tree-example`, or C++20. Define ALGORITHM_ATLAS_NO_MAIN in API drivers. Node children use unique_ptr ownership; local vectors move owned subtrees during splits, redistribution and merges. Moving a root into its sole child uses a temporary owner so the old root stays alive until transfer completes. Public const root() enables independent topology inspection. Failed contracts throw invalid_argument; the executable prints an error on stderr and exits 2.

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

Empty root, numeric extremes, duplicate at capacity, internal/root deletion, ordered/reverse insertion, randomized removal, all degrees 2..8, root splits/contraction and complete drain are covered. Inspections count records across both internal and leaf nodes, with strict child interval bounds.

[Independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py) execute empty/minimal, invalid, duplicate, balanced/skewed and bounded stress inputs. 876 streams (219 each at degrees 2,3,4,8, seed 8505) compare exact results against Python set/sorted oracles and inspect every actual node after every operation in both languages. Separate mutation-by-mutation 600-key randomized insert/drain tests cover every degree 2..8 and assert split/borrow-left/borrow-right/merge/root-contraction counters; B-Tree also asserts predecessor/successor deletion. A 1000-key capacity test drains in reverse with every mutation inspected. Tests compare both languages with the same independent expectations, rather than relying only on agreement.

## 17. Advantages

High fanout reduces height and stores each record once, including internal records.

## 18. Disadvantages and Limitations

In-node vector movement costs O(t); internal record deletion is more involved than deleting only from leaves. No persistence, concurrency, page-size model or crash recovery is implemented.

## 19. When to Use It

Use to study complete multiway balanced operations and the invariants underlying block indexes.

## 20. When Not to Use It

Use a production storage engine when durable or concurrent indexing is required; choose a simpler binary tree for a small in-memory API without page concerns.

## 21. Comparison With Related Algorithms

B-Tree stores records in all nodes and promotes/removes records during splits. B+ Tree stores records only in linked leaves and copies minimum-of-right separators into internal nodes. Their Python/C++ key-set outputs agree, but their occupancy, deletion and structural inspections are separate.

[b-plus-tree-operations](../b-plus-tree-operations/README.md), [red-black-tree-operations](../red-black-tree-operations/README.md)

## 22. Interview Questions

Why strengthen a minimal child before descent? When may an internal key use predecessor versus successor? Why does merging fit exactly 2t−1 keys?

## 23. Practice Problems

For each degree, build multiple levels and erase all keys in several orders; draw borrow/merge cases and verify every occupancy boundary. Compare range queries with a sorted independent reference.

## 24. References

[Virginia Tech OpenDSA, B-Trees and B+ Trees](https://opendsa-server.cs.vt.edu/ODSA/Books/CS3/html/BTree.html). The exact minimum-degree and separator conventions above define this implementation. The exact bounded API, tie rules and serialization grammar are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
