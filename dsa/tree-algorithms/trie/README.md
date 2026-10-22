# Trie / Prefix Tree

## 1. Algorithm Name

Trie / Prefix Tree

## 2. Overview

Store a set of lowercase ASCII words using one character edge per level, with complete deletion and safe shared-prefix pruning.

## 3. Problem Statement

Support insert, contains, starts_with and erase. Empty word is valid, duplicate insertion and absent deletion return false, and empty prefix always denotes the root path.

**API:** `Trie().insert(word) / .contains(word) / .starts_with(prefix) / .erase(word)`. ASCII a..z only, length≤256; no Unicode normalization. At most 10000 words and 100000 live nodes; preflight limits before insertion. solve takes q≤1000 pairs [opcode,word], opcodes 0 insert, 1 exact, 2 prefix, 3 erase.

## 4. Why Do We Need This Algorithm?

Ordered integer trees do not directly expose character-prefix membership. A Trie shares common prefixes while distinguishing a word ending at a node from a path that merely continues.

## 5. Real-World Applications

Dictionary prefix lookup, simple autocomplete candidate filtering and lexicographic symbol indexing under an explicit alphabet contract.

## 6. Core Intuition

A path spells a prefix. A terminal flag marks complete word membership independently of children. Erasing a terminal word may remove only nodes that no longer represent any other word’s prefix.

## 7. Prerequisites

Understand rooted trees, explicit node IDs, parent arrays, depths and binary representations. See the [shared conventions](../../../docs/tree-conventions.md).

## 8. Step-by-Step Working Process

Validate every string as lowercase ASCII and length≤256. For insert, walk the existing prefix and preflight word/node budgets before creating missing nodes and setting the terminal flag. Contains requires a complete path plus terminal; starts_with requires only a path. Erase records parent edges, clears a found terminal and prunes backward until reaching a terminal or branching node.

**Correctness and invariants:** Path uniqueness follows from one edge per character. Terminal flags therefore correspond exactly to the represented set, including the root for empty word. Insert preserves existing prefixes and adds only one spelling. Erase removes membership at that spelling; deleting only childless nonterminals cannot remove another stored word, and stopping at the first used node preserves every shared prefix. Resource preflight precedes mutation, so rejected insertions preserve state.

## 9. Pseudocode

```text
insert(word): follow existing prefix; preflight missing nodes; create suffix; mark terminal
contains(word): find path and test terminal
starts_with(prefix): test path existence (empty path exists)
erase(word):
    record path; return false unless terminal
    clear terminal
    from last edge backward: delete child only if nonterminal and childless
```

## 10. Dry Run

After inserting cat and car, ca is a prefix but not a word. Reinserting cat is a no-op. Erasing cat removes its last branch while car remains accessible. Erasing the empty word clears only root terminal membership; the empty prefix still exists.

## 11. Time Complexity

O(L) per operation for key length L; the fixed 26-way child scan during C++ pruning is a constant factor. Search does not enumerate the dictionary.

## 12. Space Complexity

O(P) nodes for P distinct prefixes, bounded by 100000 nodes including root; deletion uses O(L) path storage. C++ fixed 26-child arrays use O(26P)=O(P), while Python uses child dictionaries.

## 13. Python Implementation

Read the canonical [`python/solution.py`](python/solution.py). Each node owns a child dictionary and a terminal flag. A recorded parent-edge path implements pruning; no built-in set stores or replaces the actual Trie. `solve` is the executable adapter. Invalid types (including bool as integer), dimensions and references raise ValueError; CLI input failures exit 2.

## 14. C++ Implementation

Read [`cpp/solution.cpp`](cpp/solution.cpp) in namespace `atlas_tree`. Compile with `g++ -std=c++17 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-tree-example`, or C++20. Define ALGORITHM_ATLAS_NO_MAIN in API drivers. Nodes own 26 unique_ptr children. Traversal pointers are non-owning temporary references; erasing a child occurs only after its contents are proven unused. Leaf pruning and bounded depth prevent dangling ownership or unbounded cleanup. Failed contracts throw invalid_argument; the executable prints an error on stderr and exits 2.

## 15. Input and Output Examples

Python JSON input:
```json
{"operations":[[0,""],[0,"cat"],[0,"car"],[1,"ca"],[2,"ca"],[0,"cat"],[3,"cat"],[1,"car"],[1,"cat"],[3,""],[2,""]]}
```
C++ text input:
```text
11 0 - 0 cat 0 car 1 ca 2 ca 0 cat 3 cat 1 car 1 cat 3 - 2 -
```
Grammar: q, then q opcode/word pairs; use - for the empty word. All results are JSON booleans.

Both output:
```json
[true,true,true,false,true,false,true,true,false,true,true]
```
No sum arithmetic is performed. Keys are strings, and size/node counters are bounded before growth. Maximum ownership depth is 256, keeping C++ recursive unique_ptr destruction bounded; the root remains after complete deletion.

## 16. Edge Cases

Shared prefixes, prefix words, empty word, duplicate operations, ASCII rejection, 256-character keys, 10000-word capacity and node-budget exhaustion are tested. Rejected budget operations leave prior membership unchanged.

[Independent cases](tests/cases.py), [Python tests](tests/test_python.py) and [C++17/C++20 tests](tests/test_cpp.py) execute empty/minimal, invalid, duplicate, balanced/skewed and bounded stress inputs. 100 seed-8303 streams of 180 operations plus one explicit overlapping-prefix/empty-word sequence compare against an independent set and string-prefix predicate. Capacity tests exercise both word and live-node budgets, reclamation and reinsertion. Tests compare both languages with the same independent expectations, rather than relying only on agreement.

## 17. Advantages

Direct prefix membership in time proportional to key length, with exact set semantics and reclaimed unused prefixes.

## 18. Disadvantages and Limitations

Only the documented alphabet is supported. Fixed C++ child arrays trade memory for direct indexing. This API provides membership, not ranked autocomplete, arbitrary Unicode collation or disk persistence.

## 19. When to Use It

Use for bounded lowercase dictionaries with exact/prefix queries.

## 20. When Not to Use It

Use a hash set for exact-only lookup or a Unicode-aware representation when normalization/collation is required.

## 21. Comparison With Related Algorithms

AVL/Red-Black/B-Tree index ordered integer keys; Trie structure follows characters rather than numerical comparisons. Deletion must preserve terminal ancestors and other branches.

[b-plus-tree-operations](../b-plus-tree-operations/README.md), [segment-tree](../segment-tree/README.md)

## 22. Interview Questions

Why does path existence not imply word membership? Why is an empty prefix true even in an empty Trie? When may a node be pruned?

## 23. Practice Problems

Insert a, ab and abc, then erase in each order; verify every prefix against a reference set; design a separate alphabet expansion contract.

## 24. References

[Stanford CS106B Trie lecture](https://web.stanford.edu/class/archive/cs/cs106b/cs106b.1188/lectures/Lecture21/Lecture21.pdf) and standard character-prefix tree theory. The exact bounded API, tie rules and serialization grammar are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
