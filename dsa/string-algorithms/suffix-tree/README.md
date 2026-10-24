# Suffix Tree

## 1. Algorithm Name

Suffix Tree

## 2. Overview

Insert suffixes directly into a compressed tree whose edges store ranges of one shared symbol array.

## 3. Problem Statement

Represent every suffix endpoint and support reusable substring existence and all-occurrence queries.

**API:** `SuffixTree(text).find(pattern) returns sorted positions; .contains(pattern) returns bool. solve(text, pattern) builds once and calls find. Text≤2048 bytes; query≤10000 bytes.`

Inputs are byte strings of length at most 10000 unless the shared contract specifies a smaller construction budget. Indexes are zero-based bytes; intervals are half-open. UTF-8 must be encoded explicitly. See [String conventions](../../../docs/string-conventions.md) for every empty, ordering, invalid-type and resource rule.

## 4. Why Do We Need This Algorithm?

Sharing whole edge ranges avoids the quadratic node count of a plain suffix trie. Direct construction makes compression and splitting visible for teaching.

## 5. Real-World Applications

Fixed-text substring indexing, suffix-coverage demonstrations and repeated-substring structure exploration. No online update, storage-page or linear-time builder is claimed.

## 6. Core Intuition

Each root-to-leaf path spells one terminated suffix. When a new suffix diverges inside an edge, split only that edge and attach the unmatched remainder as one leaf.

## 7. Prerequisites

Understand arrays, loops, byte equality and asymptotic analysis. For the reusable-state variants also understand prefix/suffix terminology and simple loop invariants. Review [complexity notation](../../../docs/complexity-cheatsheet.md).

## 8. Step-by-Step Working Process

Accept at most 2048 text bytes. Append integer terminal 256, outside the entire byte alphabet. For each suffix, follow matching edge ranges. If no child exists, attach its remaining range as a leaf with the original suffix index. On an internal mismatch split the edge at the matched length and attach old/new remainders. Query bytes by walking edge symbols; a query may end in the middle of an edge. Enumerate descendant leaves and sort their suffix positions for find.

**Correctness:** Before insertion the tree spells exactly the earlier terminated suffixes. Following equal edge symbols preserves their common prefix. Attaching a new leaf adds exactly the new suffix; splitting preserves the old spelling and introduces a branch at the first difference. A unique terminal ensures no suffix is a prefix of another and every suffix has its own leaf, including the empty suffix. Every nonroot internal node branches at least twice, hence the tree is compressed and has O(n) nodes. A query path exists exactly when the query prefixes some suffix; its descendant leaves give all occurrences.

## 9. Pseudocode

```text
symbols = byte integers + [256]; nodes = root
for suffix = 0 .. n:
    walk existing compressed edges while they agree
    if missing child: attach leaf range [position,n+1) with suffix identity
    else if mismatch inside edge:
        split range at mismatch; preserve old child remainder
        attach new suffix remainder as another leaf
contains(pattern): compare edge ranges until exhausted or mismatch
find(pattern): collect descendant suffix identities; sort positions
```

## 10. Dry Run

For banana, ana shares a compressed path leading to suffixes at positions 1 and 3. Query an ends inside that path and still returns [1,3]. The terminal-only path represents suffix 6 but can never match a nonempty byte query. Empty query returns [0,1,2,3,4,5,6].

## 11. Time Complexity

Direct compressed-edge insertion uses O(n²) character comparisons in the worst case; repeated a strings realize long repeated scans. Child lookup uses a fixed alphabet of 257 symbols (C++ ordered maps add log σ with σ≤257; Python dictionaries use expected O(1) access). contains costs O(m) symbol comparisons. find costs O(m+r log r), including descendant traversal O(r) in a compressed subtree and numeric position sorting. Empty query emits n+1 boundaries. No linear construction claim is made. Here n is text length, m is pattern length, and r is output count. Preprocessing and output costs are included explicitly.

## 12. Space Complexity

O(n) symbol storage and nodes/edges: each of n+1 suffixes has one leaf and nonroot internals have at least two children. Edge labels are half-open shared-array ranges, not copied substrings. Iterative queries/destruction avoid recursive stack depth; find adds O(r) result/subtree work storage. External exhaustive structural tests deliberately use more memory than the production index.

## 13. Python Implementation

Node stores start,end,suffix and a child dictionary; nodes are kept in a flat list. find and contains reuse the completed tree without rebuilding. Public nodes and symbols are for inspection and must not be mutated. See [`python/solution.py`](python/solution.py). Python APIs reject str and require bytes; call `.encode("utf-8")` explicitly for Unicode text.

## 14. C++ Implementation

A flat vector<Node> owns map<int,int> child IDs. Construction stores indices rather than references across vector growth, preventing reallocation dangling references. symbols() and nodes() provide const inspection. No recursive pointer ownership is needed. See [`cpp/solution.cpp`](cpp/solution.cpp), namespace `atlas_string`. Define ALGORITHM_ATLAS_NO_MAIN when including it in a test driver. std::invalid_argument signals contract errors. All algorithms use unsigned byte ordering where ordering matters.

## 15. Input and Output Examples

From the repository root:

```sh
printf '62616e616e61 616e61\n' | .venv/bin/python dsa/string-algorithms/suffix-tree/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/string-algorithms/suffix-tree/cpp/solution.cpp -o /tmp/atlas-string-example
printf '62616e616e61 616e61\n' | /tmp/atlas-string-example
```

C++20 works with `-std=c++20`. Both print:

```json
[1,3]
```

Each token is hex bytes; - means empty. See the shared contract for exact argument count and the special multi-pattern grammar.

## 16. Edge Cases

Empty text and pattern, one byte, longer patterns, repeated bytes, overlaps, all 256 symbols, NUL/separator-like bytes, case sensitivity and UTF-8 byte offsets are covered by [independent oracles](../string_oracles.py). Invalid types, lengths, missing/extra tokens and malformed hex are rejected; CLI errors exit 2 with error: on stderr.

[Python tests](tests/test_python.py) and [C++ tests](tests/test_cpp.py) use seed 90901 (multi-pattern seed 90904), bounded exhaustive binary cases and deterministic random cases. Matching references use slicing; preprocessing and advanced structures receive separate independent checks. Actual executed counts and outcomes belong to [checkpoints](../../../docs/string-algorithms-checkpoints.md), not an assumed CI run.

## 17. Advantages

A genuine compressed suffix representation, explicit endpoints and collision-safe terminal. Repeated queries inspect one path rather than sorting/scanning all suffixes.

## 18. Disadvantages and Limitations

Quadratic construction is intentionally bounded at 2048 bytes. This is not Ukkonen’s online algorithm and has no suffix links or incremental append API. Child maps and explicit nodes have higher constants than arrays. This is an eager bounded educational API; output allocation and machine memory can dominate. Byte semantics do not imply Unicode normalization, grapheme indexing or linguistic ordering.

## 19. When to Use It

Choose to study compressed edges, edge splitting, suffix endpoints and substring loci on small bounded texts.

## 20. When Not to Use It

For large texts choose a proven efficient suffix-tree builder or a suffix array with a suitable construction bound. For one query use KMP.

## 21. Comparison With Related Algorithms

A plain suffix trie can have O(n²) nodes; this structure has O(n) compressed nodes but still O(n²) construction work. Ukkonen supplies a different linear-time construction under suitable alphabet assumptions. The sibling Suffix Array uses O(n log² n) construction here.

## 22. Interview Questions

Why does a terminal need to be outside all 256 byte values? Can a query finish inside an edge? Why must every nonroot internal node branch? Why do O(n) nodes not prove O(n) construction time?

## 23. Practice Problems

Insert all suffixes of abab by hand and record every edge split. Independently spell all root-to-leaf paths. Corrupt an edge range in a test snapshot and confirm structural validation rejects it.

## 24. References

[Ukkonen, On-line construction of suffix trees (1995)](https://www.cs.helsinki.fi/u/ukkonen/SuffixT1withFigs.pdf), a faster alternative construction rather than the direct insertion implemented here. The repository-specific bounds, transport and output order are defined in [String conventions](../../../docs/string-conventions.md).

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
