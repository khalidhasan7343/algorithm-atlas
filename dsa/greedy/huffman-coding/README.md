# Huffman Coding

## 1. Algorithm Name

Huffman Coding

## 2. Overview

Build a variable-length binary prefix code from positive byte frequencies. The actual Huffman algorithm repeatedly combines the two lightest subtrees in a min-priority queue, then traverses the resulting tree to assign bit strings. Encoding and decoding use that same owned tree.

## 3. Problem Statement

The alphabet contains unique integer bytes 0..255 and frequencies in 1..10^9. Python accepts a mapping; C++ accepts unique symbol/frequency pairs and rejects duplicates. Empty alphabet produces no codes and accepts only an empty message/stream. A singleton uses code "0", not an empty codeword. Heap ties are (frequency,minimum byte in subtree,creation index), with leaves created in ascending byte order; the first popped child receives 0, the second 1. APIs expose codewords, weighted bit cost, encoding and decoding. Messages are at most 10000 bytes and bit strings at most 1000000 bits; decoded output also has the 10000-byte cap.

## 4. Why Do We Need This Algorithm?

Fixed-width coding spends the same number of bits on rare and frequent symbols. A prefix tree can give short paths to frequent symbols while keeping concatenations uniquely decodable. The optimization objective is sum(frequency·codeword length), not lexical code order or numeric bit values.

## 5. Real-World Applications

Prefix coding is a building block in lossless data compression and educational source coding. Real formats add headers, frequency/codebook transmission, bit packing and format-specific rules; this implementation deliberately exposes the tree-code step.

## 6. Core Intuition

Two smallest frequencies can be placed at sibling leaves of greatest depth in an optimum. Treat those siblings as one combined-frequency symbol, solve the smaller problem, then expand the pair. A min-heap realizes this repeated greedy choice.

## 7. Prerequisites

Binary trees, min-priority queues, recursion, byte values, bit strings and weighted sums. [Activity Selection](../activity-selection/README.md) illustrates a different exchange argument. Tree structure and prefix-free decoding should be understood before treating this as a file compressor.

## 8. Step-by-Step Working Process

Validate symbols/frequencies, create one leaf per symbol and push its heap key. Repeatedly pop the two minimum keys, append a parent node with summed weight and minimum subtree byte, and push the parent key. Continue until one root remains. Traverse left/right as 0/1 to assign leaf codes; use 0 for a singleton. Encoding concatenates known-symbol codewords after size checks. Decoding walks the tree until a leaf emits one byte and restarts at the root; nonbinary bits, invalid singleton bits, incomplete final paths and oversized outputs are rejected.

Greedy-choice proof: an optimal full binary tree has a deepest sibling-leaf pair. Exchanging the two smallest-weight symbols into those deepest positions cannot increase weighted path length. Collapse them to a leaf with their sum; expanding any collapsed solution increases cost by exactly that sum. Thus optimal substructure holds and induction proves the repeated two-minimum construction optimal. This argument applies to k≥2. The k=1 cost is frequency under the explicitly required nonempty-codeword convention. Distinct leaves cannot be ancestors of one another, proving prefix freedom; walking complete leaf paths proves round-trip correctness.

## 9. Pseudocode

```text
heap ← one (frequency,minimum_symbol,node_index) entry per leaf
while heap contains at least two entries:
    left ← pop_min(heap); right ← pop_min(heap)
    parent ← node(left,right) with summed frequency
    push(heap,parent_key)
traverse root, appending 0 on left and 1 on right
encode: concatenate code[byte] for each known message byte
decode: follow each bit; emit at a leaf and restart at root
reject if final decoder position is inside a codeword
```

## 10. Dry Run

Frequencies A(65)=5, B(66)=2, C(67)=1:

| Step | Heap weights before | Merge | Heap after |
| --- | --- | --- | --- |
| 1 | C:1, B:2, A:5 | C left + B right → CB:3 | CB:3, A:5 |
| 2 | CB:3, A:5 | CB left + A right → root:8 | root:8 |

The resulting codes are A=1, B=01, C=00. Weighted cost is 5·1+2·2+1·2=11. Message ABCA encodes as 1|01|00|1 = 101001. Following that stream reaches leaves A,B,C,A and ends at the root. With four equal symbols A..D the deterministic codes are 00,01,10,11.

## 11. Time Complexity

Let k be alphabet size, L the sum of codeword lengths, m message bytes and B encoded bits. Tree construction performs k-1 heap merges, giving O(k log(k+1)) worst time after leaf ordering. Materializing all code strings costs O(k+L), so total codebook construction is O(k log(k+1)+L); L can be O(k²) for skewed trees. Encoding in Python is O(m+B) expected dictionary work; C++ ordered-map lookup adds O(m log(k+1)). Decoding is O(B+output bytes). Empty operations take O(1). No input distribution for an average build time is assumed; the same worst bounds apply. Singleton code generation is constant-sized regardless of its frequency.

## 12. Space Complexity

The tree/heap occupy O(k) nodes/entries. Codes use O(k+L) storage; recursive traversal has depth at most k-1 (at most 255), and temporary prefixes remain within the O(k+L) bound. Encoding adds O(m+B), decoding O(output bytes), excluding input storage. Python codebook access returns an owned dictionary copy with immutable string values; C++ returns a const map reference. No bits are packed into machine-byte output.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `HuffmanCodec(frequencies), encode(bytes), decode(bits), weighted_length()`. Native integer inputs exclude bool and floating point; invalid data/resource bounds raise ValueError. Inputs are read only, results own their containers, and importing the module performs no I/O. The implementation follows the strategy in sections 6–9.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) exposes `HuffmanCodec(frequency_pairs), encode(byte_vector), decode(bits), weighted_length()` in namespace `atlas_greedy`. Define `ALGORITHM_ATLAS_NO_MAIN` when including it in an API driver. C++17 and C++20 use standard containers and signed 64-bit integers. The shared [header](../common.hpp) handles validation/CLI utilities; the algorithm itself is implemented in this canonical source. Invalid data/resource bounds throw invalid_argument. Inputs are const references.

## 15. Input and Output Examples

From the repository root, input is **alphabet size k, k byte/frequency pairs, message length m, then m byte integers**. Numeric tokens are ASCII signed decimal integers. Counts must match exactly; missing, malformed or extra tokens produce exit 2, a stderr diagnostic, and empty stdout. A successful run prints one JSON value and a newline.

```sh
printf '%s\n' '3 65 5 66 2 67 1 4 65 66 67 65' | .venv/bin/python dsa/greedy/huffman-coding/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/greedy/huffman-coding/cpp/solution.cpp -o /tmp/atlas-huffman-coding
printf '%s\n' '3 65 5 66 2 67 1 4 65 66 67 65' | /tmp/atlas-huffman-coding
```

Both print:

```text
{"codes":[[65,"1"],[66,"01"],[67,"00"]],"bits":"101001","decoded":[65,66,67,65],"cost":11}
```

Use `-std=c++20` for the other supported standard. Run `.venv/bin/python -m pytest dsa/greedy/huffman-coding --require-cpp` to execute Python, C++17 and C++20 tests. Independent expected values and boundary cases are in the [test cases](tests/cases.py).

## 16. Edge Cases

Empty alphabet/message is valid; nonempty data with no alphabet is rejected. A singleton encodes each occurrence as 0 and rejects 1. Equal frequencies, embedded byte zero, byte 255, repeated message bytes, skewed powers-of-two frequencies and the full 256-byte alphabet are tested. Frequencies must be strictly positive, finite native integers, not zero or negative. Unknown symbols, duplicates in C++/CLI, nonbinary strings and truncated codewords are errors. Tests exhaustively enumerate every pair choice in small merge trees, not just the greedy merge order, to obtain independent optimum weighted costs.

## 17. Advantages

Optimal weighted length for binary symbol-by-symbol prefix coding, deterministic cross-language trees and a direct round-trip API. Priority queues keep the tree-construction step efficient.

## 18. Disadvantages and Limitations

These are ordinary deterministic Huffman tree codes, **not canonical Huffman codes** ordered by code lengths. The frequency table/tree must be shared by encoder and decoder; raw bit strings contain no header or integrity check. Input is bytes, not Unicode characters; callers choose any text-to-byte encoding separately. Node sums are ≤256·10^9; weighted cost is conservatively ≤256·10^9·255, below signed-64. Resource caps are validated. String-bit output is educational and may be larger in memory than the original bytes; no compression-ratio claim is made for this representation.

## 19. When to Use It

Use to study or build a byte-prefix-code component when an exact frequency table and deterministic tree are appropriate.

## 20. When Not to Use It

Use a format implementation when actual compressed-file compatibility, headers and packed bits are required. Arithmetic/range coding, adaptive coding and canonical codebook serialization have different models and are outside this API.

## 21. Comparison With Related Algorithms

| Method | Code lengths | Key distinction |
| --- | --- | --- |
| Huffman tree here | variable | optimal binary symbol prefix cost |
| Fixed-width | same for every symbol | can waste bits on skewed frequency |
| Canonical Huffman | uses Huffman lengths | assigns a prescribed ordered codebook |
| Arithmetic/range coding | codes sequences | different representation/objective model |

## 22. Interview Questions

Why can the two smallest weights be siblings at maximum depth? Why does collapsing them preserve optimal substructure? What makes a code prefix-free? Why is singleton 0 a contract decision? Does deterministic tree construction imply canonical Huffman coding?

## 23. Practice Problems

Construct the tree for equal and skewed frequencies by hand. Verify prefix freedom and weighted length independently. Then design a separately specified packed-bit format with length/codebook metadata, including how it detects a truncated final message.

## 24. References

David A. Huffman, [A Method for the Construction of Minimum-Redundancy Codes (1952)](https://www.cse.iitd.ac.in/~pkalra/siv864/huffman_1952.pdf), is the original construction paper. [ETH Zürich Greedy Algorithms](https://lec.inf.ethz.ch/DA/2017/slides/daLecture15.en.handout.pdf) gives course context. The code, byte-domain limits, tie rules and singleton convention here are independently specified; no source code is copied.

## 25. Author Attribution

Algorithm Atlas is maintained by **MD.Khalid Hasan** ([GitHub](https://github.com/khalidhasan7343)). See the [repository](https://github.com/khalidhasan7343/algorithm-atlas), [MIT License](../../../LICENSE), and [contribution policy](../../../CONTRIBUTING.md).
