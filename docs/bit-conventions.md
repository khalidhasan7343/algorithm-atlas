# Bit Manipulation contracts

All public numeric inputs are **signed 32-bit values**, -2147483648 through
2147483647. Python accepts native int (excluding bool), in list/tuple sequences
for array APIs. C++ accepts int64_t values, validates the same range, then
converts to uint32_t for bit operations. These exact-width types must exist.
Results decode the unsigned word mathematically: words below 2^31 are positive;
otherwise subtract 2^32 in signed 64-bit arithmetic. This models two's complement
without relying on C++17 signed representation or out-of-range signed casts.

Python masks signed values with 0xffffffff before bit operations. C++ converts
negative input to uint32_t modulo 2^32. No signed negative shift, signed overflow,
or signed negation of INT32_MIN is used. Low-bit isolation uses unsigned
`word & uint32_t(0-word)`; wrapping subtraction is deliberate. All subset shifts
have unsigned operands and counts strictly below 32.

## Multiplicity and checked versus candidate APIs

XOR Unique requires exactly one singleton and every other distinct value exactly
twice. Two Non-Repeating requires exactly two distinct singletons and every
other value exactly twice. Input order is arbitrary, length at most 10000.
Empty input and unsupported counts (including triples, fourfold repetitions,
three singletons or no singleton) are rejected by **solve**, using a frequency
map before running the genuine XOR algorithm. Two results are sorted in signed
numeric ascending order. All inputs remain unchanged.

The explicitly named `xor_candidate` and `partition_candidates` expose the
constant-space algorithms under the caller's pair assumptions. They still
validate sequence/type/width/length and minimal length/parity; partition also
rejects a zero total XOR. Those checks cannot prove multiplicity. Candidate
results are not validated unique-element answers for arbitrary inputs.
No unchecked flag is hidden in solve or the executable interface.

The XOR core costs O(n) time and O(1) auxiliary space for fixed width. Numeric
validation also uses O(1) extra space. Default multiplicity validation uses
O(d) space for d distinct values and expected O(n) time (hash-table worst case
O(n²)). These extra validation costs are included in the lesson bounds;
constant-space claims refer only to the candidate algorithms.

## Bit counting and subsets

Kernighan counts ones in the 32-bit representation: 0 has zero, -1 has 32,
INT32_MIN has one, and INT32_MAX has 31. It clears one set bit per iteration;
the masked word is finite, so negative Python values cannot create an infinite
loop. No built-in popcount implements the production algorithm.

Bitmask subsets are **positional**, n≤16. Mask 0 comes first, then increasing
unsigned masks through 2^n-1. Bit j selects original position j; each row retains
input order. Equal values may produce repeated equal rows, which are preserved.
Empty input returns `[[]]`. At n=16 there are 65536 rows and 524288 selected
value entries. Working row space is O(n); eager returned storage is O(n*2^n)
including O(2^n) row headers. Runtime is O(n*2^n), or O(1) for empty input.
No streaming output, distinct-value deduplication or larger-n support is promised.
The existing recursive [Power Set lesson](../dsa/recursion-and-backtracking/power-set-generation/README.md)
is a different canonical technique; comparison tests preserve duplicate rows
and compare multisets because its recursion order differs from mask order.

## Portable executable grammar and failures

Both languages accept whitespace-separated signed decimal input, with optional
+/- and at most 11 characters per token. Leading zeros are allowed within that
limit; hex, underscores, exponents and non-ASCII digits are rejected. Array
algorithms consume values only, without a count prefix; Kernighan requires
exactly one token. Empty input is valid only for subsets. Output is compact JSON
(one integer, two integers, or rows of subset values).

Python raises ValueError for invalid input; C++ throws std::invalid_argument.
CLI parse and contract errors print `error:` to stderr and exit 2 without a
partial result. Larger inputs and values fail before enumeration or bit work.
Allocation failure, concurrent input mutation and externally corrupted runtime
objects are outside the educational API contract.
