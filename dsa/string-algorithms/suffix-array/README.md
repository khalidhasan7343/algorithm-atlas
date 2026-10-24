# Suffix Array

## 1. Algorithm Name

Suffix Array

## 2. Overview

Sort suffix starting positions by doubling rank-pair lengths, then compute adjacent LCP values with Kasai’s scan.

## 3. Problem Statement

Build a reusable lexicographic suffix index and find every occurrence of a query pattern.

**API:** `SuffixArray(text).sa / .lcp / .find(pattern); solve(text, pattern) returns [sa,lcp,positions]. LCP[0]=0; the empty suffix is omitted.`

Inputs are byte strings of length at most 10000 unless the shared contract specifies a smaller construction budget. Indexes are zero-based bytes; intervals are half-open. UTF-8 must be encoded explicitly. See [String conventions](../../../docs/string-conventions.md) for every empty, ordering, invalid-type and resource rule.

## 4. Why Do We Need This Algorithm?

Preprocessing one fixed text allows many substring queries without rescanning every alignment. An array index also exposes adjacent repeated-prefix lengths.

## 5. Real-World Applications

Repeated substring queries on fixed byte corpora, longest-repeat analysis and compact indexing exercises. This is an in-memory demonstration, not a compressed disk search service.

## 6. Core Intuition

If ranks correctly order prefixes of width w, pairs of ranks order prefixes of width 2w. Repeating until ranks are unique orders complete suffixes without storing full suffix strings.

## 7. Prerequisites

Understand arrays, loops, byte equality and asymptotic analysis. For the reusable-state variants also understand prefix/suffix terminology and simple loop invariants. Review [complexity notation](../../../docs/complexity-cheatsheet.md).

## 8. Step-by-Step Working Process

Validate and copy or retain immutable text. Start ranks with unsigned byte values. Sort positions by (rank[i],rank[i+w] or -1), assign new equal-pair ranks and double w. Stop at distinct ranks or w≥n. Compute inverse ranks and Kasai LCP with the preceding suffix. For find, binary-search the lower/upper suffix bounds whose prefix equals the query and sort their positions numerically.

**Correctness:** Initially ranks order one-byte prefixes. Pair comparison combines two correctly ranked adjacent blocks, so induction gives the correct order for each doubled width; absent blocks rank -1 before any byte. Once ranks are distinct or width covers the text, this is suffix order. Kasai carries at least the previous common length minus one after advancing a start, checking further bytes explicitly. All suffixes sharing a pattern prefix form a contiguous lexicographic range; two binary bounds recover exactly that range.

## 9. Pseudocode

```text
rank = unsigned bytes; SA = positions; width = 1
while width < n:
    sort SA by (rank[i], rank[i+width] or -1)
    assign next ranks to equal pairs
    if all ranks distinct: break
    width *= 2
compute inverse ranks and adjacent LCP with carried length minus one
find(pattern): binary lower/upper prefix bounds; sort matching starts
```

## 10. Dry Run

For banana, suffix order is [5,3,1,0,4,2]: a, ana, anana, banana, na, nana. Adjacent LCP is [0,1,3,0,0,2]. Query ana spans suffix starts 3 and 1, returned in numeric order [1,3]. The empty suffix is excluded from SA but empty-pattern queries include boundary n.

## 11. Time Complexity

Comparison-based rank-pair sorting costs O(n log n) per doubling round and O(log n) rounds, so construction is O(n log² n), not radix-sorted O(n log n). Kasai LCP adds O(n). A query uses O(m log n+r log r): comparisons inspect up to m bytes and output is sorted numerically. Empty-pattern output costs O(n). solve constructs once and performs one query; repeated find calls reuse the index. Here n is text length, m is pattern length, and r is output count. Preprocessing and output costs are included explicitly.

## 12. Space Complexity

O(n) stored text, SA and LCP plus O(n) rank/inverse/sorting workspace during construction. Query returns O(r) positions; Python also slices an O(r) suffix interval. No full suffix copies are built or sorted.

## 13. Python Implementation

SuffixArray exposes sa and lcp inspection arrays plus find. The sorting key is a constant-size integer pair, not text[i:]. Python bytes are immutable, so retaining text is safe. See [`python/solution.py`](python/solution.py). Python APIs reject str and require bytes; call `.encode("utf-8")` explicitly for Unicode text.

## 14. C++ Implementation

SuffixArray owns its text copy and vector<int> arrays. Every rank/comparison uses unsigned byte order; -1 distinguishes an exhausted rank block. find is const and construction counters stay within the 10000-byte bound. See [`cpp/solution.cpp`](cpp/solution.cpp), namespace `atlas_string`. Define ALGORITHM_ATLAS_NO_MAIN when including it in a test driver. std::invalid_argument signals contract errors. All algorithms use unsigned byte ordering where ordering matters.

## 15. Input and Output Examples

From the repository root:

```sh
printf '62616e616e61 616e61\n' | .venv/bin/python dsa/string-algorithms/suffix-array/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/string-algorithms/suffix-array/cpp/solution.cpp -o /tmp/atlas-string-example
printf '62616e616e61 616e61\n' | /tmp/atlas-string-example
```

C++20 works with `-std=c++20`. Both print:

```json
[[5,3,1,0,4,2],[0,1,3,0,0,2],[1,3]]
```

Each token is hex bytes; - means empty. See the shared contract for exact argument count and the special multi-pattern grammar.

## 16. Edge Cases

Empty text and pattern, one byte, longer patterns, repeated bytes, overlaps, all 256 symbols, NUL/separator-like bytes, case sensitivity and UTF-8 byte offsets are covered by [independent oracles](../string_oracles.py). Invalid types, lengths, missing/extra tokens and malformed hex are rejected; CLI errors exit 2 with error: on stderr.

[Python tests](tests/test_python.py) and [C++ tests](tests/test_cpp.py) use seed 90901 (multi-pattern seed 90904), bounded exhaustive binary cases and deterministic random cases. Matching references use slicing; preprocessing and advanced structures receive separate independent checks. Actual executed counts and outcomes belong to [checkpoints](../../../docs/string-algorithms-checkpoints.md), not an assumed CI run.

## 17. Advantages

Linear structural storage, useful LCP metadata and repeated binary-search queries on one fixed text.

## 18. Disadvantages and Limitations

The implementation uses comparison sorting in each doubling round and is not the asymptotically fastest suffix-array construction. Sorting reported starts adds an output cost beyond lexicographic enumeration. This is an eager bounded educational API; output allocation and machine memory can dominate. Byte semantics do not imply Unicode normalization, grapheme indexing or linguistic ordering.

## 19. When to Use It

Choose for many exact substring queries and suffix/LCP analysis on fixed text.

## 20. When Not to Use It

For one short query use Naive or KMP; for mutable text this index must be rebuilt.

## 21. Comparison With Related Algorithms

A compressed Suffix Tree offers direct path queries but has more pointer/edge metadata and this repository’s tree builder is quadratic. Both preserve original text positions; Aho-Corasick preprocesses patterns instead of text.

## 22. Interview Questions

Why is a missing second rank -1? Why can construction stop when all ranks differ? What makes prefix-equal suffixes contiguous? Why is this implementation O(n log² n)?

## 23. Practice Problems

Derive banana ranks for widths 1,2,4. Verify SA by directly sorting suffix strings only in a small oracle. Use adjacent LCP to compute the length of the longest repeated substring.

## 24. References

[Stanford CS166 suffix-array exercises](https://web.stanford.edu/class/cs166/handouts/080%20Problem%20Set%203.pdf) and [Princeton string-indexing overview](https://algs4.cs.princeton.edu/50strings/). The repository-specific bounds, transport and output order are defined in [String conventions](../../../docs/string-conventions.md).

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
