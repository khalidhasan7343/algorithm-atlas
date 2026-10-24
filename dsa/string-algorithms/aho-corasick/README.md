# Aho–Corasick

## 1. Algorithm Name

Aho–Corasick

## 2. Overview

Build a byte-pattern trie, BFS failure links and terminal output links, then scan text through completed transitions.

## 3. Problem Statement

Return all occurrences of an ordered pattern collection, retaining duplicate pattern identities and overlapping matches.

**API:** `AhoCorasick(patterns).find(text); solve(text, patterns) returns [end,pattern_id,start] triples, ordered by end, decreasing pattern length, then ID. The executable takes text_hex count pattern_hex... .`

Inputs are byte strings of length at most 10000 unless the shared contract specifies a smaller construction budget. Indexes are zero-based bytes; intervals are half-open. UTF-8 must be encoded explicitly. See [String conventions](../../../docs/string-conventions.md) for every empty, ordering, invalid-type and resource rule.

## 4. Why Do We Need This Algorithm?

Scanning text separately for every pattern repeats work. Shared prefixes and failure transitions combine the scans into one automaton.

## 5. Real-World Applications

Bounded multi-signature scans, dictionary keyword detection and motif collections where exact byte patterns share prefixes or suffixes.

## 6. Core Intuition

A state is the longest processed-text suffix that is also a pattern prefix. Its failure link points to the longest proper suffix with that property; output links enumerate terminal suffix states.

## 7. Prerequisites

Understand arrays, loops, byte equality and asymptotic analysis. For the reusable-state variants also understand prefix/suffix terminology and simple loop invariants. Review [complexity notation](../../../docs/complexity-cheatsheet.md).

## 8. Step-by-Step Working Process

Validate at most 256 patterns and 4096 aggregate bytes. Insert each pattern ID into its terminal trie node, including empty patterns at root. Initialize root transitions and BFS the trie: failure targets use already completed shallower transitions; missing transitions inherit from failure. Keep only local terminal IDs and a link to the nearest nonroot terminal suffix. Scan each byte with one transition and emit state outputs followed by progressively shorter terminal suffixes, then root empty outputs.

**Correctness:** Trie paths identify pattern prefixes. BFS processes a node’s failure state first, so inherited transitions lead to the longest suffix remaining in the trie after the new byte. Induction on scanned bytes proves the state invariant. The output-link chain enumerates exactly the terminal suffixes of that state without omitting shorter patterns or copying their output lists. Every pattern ID appears once at its own terminal, retaining duplicates. Longer suffixes are emitted before shorter ones; local IDs remain in insertion order, and root empties are last at each end boundary.

## 9. Pseudocode

```text
insert patterns, preserving terminal identity lists
complete root transitions; queue nonroot root children
BFS node:
    output_link = nearest nonroot terminal on failure chain
    for each byte:
        missing transition = failure transition
        real child failure = failure transition; enqueue child
emit empty IDs at boundary 0
for each text byte with exclusive end:
    state = completed_transition(state,byte)
    emit terminal IDs along output links, then root empty IDs
```

## 10. Dry Run

Text aaaa with patterns [a,aa,empty,aa]: at end 1 output a(id0), then empty(id2). At end 2 output aa(id1), aa(id3), a(id0), then empty(id2). The duplicate aa patterns remain separate identities. Empty text still reports every empty-pattern ID at boundary zero.

## 11. Time Complexity

Let P be total pattern bytes, k pattern count, V trie nodes≤P+1 and σ=256. Insertion costs O(P+k). Dense transition completion and BFS cost O(σV); scanning/reporting costs O(n+z), where z is the number of triples (including empties). A state with no local output incurs at most one extra link step per byte; every subsequent link visits a terminal. solve includes construction; repeated find calls reuse it. Dense construction is explicitly O(256V), not a sparse-trie O(P) claim independent of alphabet. Here n is text length, m is pattern length, and r is output count. Preprocessing and output costs are included explicitly.

## 12. Space Complexity

O(σV+P+k) automaton/text-pattern storage and O(V) BFS queue during construction, plus O(z) eager output. Inherited terminal lists are not duplicated: each pattern ID is stored only at its own terminal, with one output link per state. n≤10000, k≤256, P≤4096; worst-case eager output can still be (n+1)k triples.

## 13. Python Implementation

AhoCorasick snapshots patterns as an immutable tuple and keeps dense lists for goto, failure, output_link, terminal and depth inspection. find uses enumerate(text,1) for exclusive end positions. See [`python/solution.py`](python/solution.py). Python APIs reject str and require bytes; call `.encode("utf-8")` explicitly for Unicode text.

## 14. C++ Implementation

Node stores a 256-entry transition array, failure/output IDs, depth and local terminal IDs. The automaton owns copies of pattern bytes. Integer node IDs remain valid across vector growth, and unsigned byte conversion indexes transitions safely. See [`cpp/solution.cpp`](cpp/solution.cpp), namespace `atlas_string`. Define ALGORITHM_ATLAS_NO_MAIN when including it in a test driver. std::invalid_argument signals contract errors. All algorithms use unsigned byte ordering where ordering matters.

## 15. Input and Output Examples

From the repository root:

```sh
printf '6161 3 61 6161 -\n' | .venv/bin/python dsa/string-algorithms/aho-corasick/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/string-algorithms/aho-corasick/cpp/solution.cpp -o /tmp/atlas-string-example
printf '6161 3 61 6161 -\n' | /tmp/atlas-string-example
```

C++20 works with `-std=c++20`. Both print:

```json
[[0,2,0],[1,0,0],[1,2,1],[2,1,0],[2,0,1],[2,2,2]]
```

Each token is hex bytes; - means empty. See the shared contract for exact argument count and the special multi-pattern grammar.

## 16. Edge Cases

Empty text and pattern, one byte, longer patterns, repeated bytes, overlaps, all 256 symbols, NUL/separator-like bytes, case sensitivity and UTF-8 byte offsets are covered by [independent oracles](../string_oracles.py). Invalid types, lengths, missing/extra tokens and malformed hex are rejected; CLI errors exit 2 with error: on stderr.

[Python tests](tests/test_python.py) and [C++ tests](tests/test_cpp.py) use seed 90901 (multi-pattern seed 90904), bounded exhaustive binary cases and deterministic random cases. Matching references use slicing; preprocessing and advanced structures receive separate independent checks. Actual executed counts and outcomes belong to [checkpoints](../../../docs/string-algorithms-checkpoints.md), not an assumed CI run.

## 17. Advantages

One deterministic output-sensitive scan for many patterns, shared prefix work and exact duplicate/empty policies.

## 18. Disadvantages and Limitations

Dense byte transition tables use substantial memory even when branching is sparse. Empty/duplicate patterns can create very large eager output. Construction is batch-only; adding patterns requires rebuilding. This is an eager bounded educational API; output allocation and machine memory can dominate. Byte semantics do not imply Unicode normalization, grapheme indexing or linguistic ordering.

## 19. When to Use It

Choose for multiple fixed patterns scanned against many bounded byte texts.

## 20. When Not to Use It

Use KMP for one pattern or a suffix index when one text receives many unrelated later queries. Reconsider output streaming for massive match counts.

## 21. Comparison With Related Algorithms

KMP failure links operate on one pattern; Aho-Corasick generalizes prefix/failure state to a trie. A suffix tree indexes suffixes of text, while this automaton indexes pattern prefixes.

## 22. Interview Questions

Why must failure links be built breadth first? Why can inherited output-list copying inflate memory? How do duplicates differ from repeated occurrences? Where must empty patterns be emitted?

## 23. Practice Problems

Draw the he/she/his/hers automaton and trace ushers. Verify each failure target by direct longest-suffix enumeration. Add duplicate and empty patterns and derive the exact deterministic output order.

## 24. References

[Stanford CS166 Aho-Corasick lecture](https://web.stanford.edu/class/archive/cs/cs166/cs166.1186/lectures/02/Slides02.pdf). The repository-specific bounds, transport and output order are defined in [String conventions](../../../docs/string-conventions.md).

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
