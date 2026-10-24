# String Algorithms contracts

Phase 9 uses **byte strings**: Python APIs accept `bytes` (not `str`, bytearray,
integers or lists); C++ APIs accept `std::string` and convert characters to
unsigned bytes before comparisons or table indexing. All 256 byte values,
including NUL, whitespace and 255, are supported. Indexes and half-open ranges
count bytes, starting at zero. Matching is exact and case sensitive.

Unicode text is supported by explicitly encoding both inputs as UTF-8 first:
`"éé".encode("utf-8")` searched for `"é".encode("utf-8")` returns `[0,2]`.
These are byte offsets, without normalization, case folding, code-point or
grapheme guarantees. Arbitrary bytes need not be valid UTF-8. Palindromes and
lexicographic order also operate on unsigned bytes; a Unicode palindrome need
not be a byte palindrome. No implicit encoding or decoding occurs.

## Matching and indexing

Single-pattern searches return every occurrence in ascending start order,
including overlaps. Empty pattern matches all `n+1` boundaries, including both
ends. Empty text has one empty-pattern occurrence and no nonempty occurrence.
Pattern longer than text has no occurrence. Hash equality is only a candidate:
Rabin-Karp compares every candidate byte by byte before reporting it.

KMP exposes `prefix_function`, Z exposes `z_array` with Z[0]=0; their `solve`
functions return positions. Manacher exposes `radii` (odd radius includes the
center; even radius is centered before the index) and `solve` returns
`[odd, even, [start,end]]` for the earliest longest byte palindrome. Empty range
is `[0,0]`. Suffix Array returns `[suffix_order, lcp, positions]`; LCP[0]=0,
and the empty suffix is excluded from suffix_order. Suffix Tree returns
positions and exposes its compressed nodes for independent structural checks.

Aho-Corasick accepts an ordered list of patterns. Every list index is a distinct
identity, so duplicates are all reported. Each result is `[end,pattern_id,start]`
with exclusive end. Results are ordered by end, then decreasing pattern length,
then increasing pattern ID. Empty patterns occur at every boundary, after
nonempty outputs at that boundary. Output links avoid copying inherited lists.

## Bounds, memory and reuse

Default byte-length bound is 10000 per text or pattern. The intentionally
quadratic compressed Suffix Tree builder accepts text length at most 2048;
its query pattern may still have 10000 bytes. Aho-Corasick accepts at most 256
patterns and 4096 total pattern bytes. It uses a fixed 256-symbol completed
transition table, BFS failure links and terminal output links. Output is eager;
its worst bound is `(n+1)*256` triples. There is no streaming output API.

SuffixArray, SuffixTree and AhoCorasick preprocess once and support repeated
queries without rebuilding. Their public inspection data must not be mutated.
The single-pattern helpers rebuild pattern preprocessing for each call.
No timing guarantees, parallel mutation, persistence or allocation-failure
atomicity are promised. Documented bounds make quadratic demonstrations and
eager outputs finite; real memory availability can impose lower limits.

Python raises ValueError for invalid types or bounds. C++ throws
std::invalid_argument for invalid bounds. Python bytes type validation has no
C++ analogue for arguments already typed std::string. CLI parse/contract errors
write `error:` to stderr and exit 2. No partial result is printed.

## Portable executable grammar

Both languages use the same whitespace-delimited hex grammar. Each string is
an even-length hexadecimal token; `-` denotes empty. No length prefix is
needed and embedded whitespace/NUL cannot collide with token boundaries.

* Matchers, Suffix Array and Suffix Tree: `text_hex pattern_hex`.
* Manacher: `text_hex`.
* Aho-Corasick: `text_hex count pattern_hex ...` (exactly count patterns).

Extra or missing tokens, odd/non-hex strings and invalid counts are rejected.
Output is one JSON array. CLI parsing and serialization are additional linear
costs in input/output size. Z matching uses integer sentinel 256 between byte
sequences; Suffix Tree appends integer terminal 256. Neither can collide with
any input byte. Manacher uses separate odd/even arrays and no separator.

See [checkpoints](string-algorithms-checkpoints.md) for sequential evidence and
[development standards](development.md) for the required lesson structure.
