# Subset Generation using Bitmasking

## 1. Algorithm Name

Subset Generation using Bitmasking

## 2. Overview

Interpret every bounded mask as a positional inclusion choice and materialize its selected input values.

## 3. Problem Statement

Enumerate all positional subsets of a signed-32 sequence, preserving duplicate-valued rows, input order within each row and ascending-mask order across rows.

**API:** solve(values) accepts list/tuple in Python or vector<int64_t> in C++, with 0≤n≤16 and signed-32 values. It returns a list/vector of rows. Empty input returns [[]].

Read [fixed-width contracts](../../../docs/bit-conventions.md) for decimal grammar, two’s-complement interpretation, errors and resource limits.

## 4. Why Do We Need This Algorithm?

A subset of n positions is exactly n binary inclusion decisions. Mask enumeration provides a direct iterative technique distinct from the repository’s recursive Power Set canonical.

## 5. Real-World Applications

Small exhaustive feature/option selections, bounded combination search and checking algorithms on all position subsets. Exponential output makes this suitable only for small n.

## 6. Core Intuition

Each bit has one input-position identity, even when its value equals another position’s value. Integer masks enumerate every choice once; two different choices may legitimately yield equal value rows.

## 7. Prerequisites

Understand binary place values, arrays, loops and asymptotic analysis. Bitwise XOR/AND act independently on each bit. Two’s-complement words are a mathematical interpretation of unsigned values here; C++17 signed representation is not assumed. See [complexity notation](../../../docs/complexity-cheatsheet.md).

## 8. Step-by-Step Working Process

Validate sequence/type, value range and n≤16 before computing a limit. Compute 2^n with an unsigned one. For each mask from zero to that limit minus one, start a fresh row, test positions in increasing order and append a value when its bit is set. Store every row without deduplication.

**Correctness:** The binary representation of each mask is a unique n-position inclusion vector. Masks 0 through 2^n-1 biject with all such vectors, so no positional subset is omitted or repeated. Testing positions in ascending order preserves within-row order; iterating masks in ascending order gives deterministic row order. Duplicate values do not invalidate the bijection, so equal rows must remain present.

## 9. Pseudocode

```text
validate values and require n<=16
limit = unsigned_one << n
result = []
for mask = 0 .. limit-1:
    row = []
    for position = 0 .. n-1:
        if mask AND (unsigned_one << position): append values[position]
    append fresh row to result
return result
```

## 10. Dry Run

For [10,20], masks 00,01,10,11 select [],[10],[20],[10,20]. For [1,1], those same distinct positional masks yield [],[1],[1],[1,1], retaining both singleton rows. Empty input has one mask, 0, and thus one empty row.

## 11. Time Complexity

For n≥1 the implementation tests all n bits for every mask: Θ(n*2^n) work, plus constant validation per value. Exactly 2^n rows and n*2^(n-1) value entries are materialized, so exponential output cannot be avoided by faster loop mechanics. Empty input is Θ(1). There is no sorting, recursive generation or preprocessing table in production.

## 12. Space Complexity

O(n) auxiliary working-row storage beyond the returned result, with O(1) mask/index state. Total returned storage is Θ(2^n+n*2^(n-1)), commonly O(n*2^n) for n≥1; count row headers as well as values. At n=16 this is 65536 rows and 524288 selected entries. C++ moves each completed fresh row into the output.

## 13. Python Implementation

Each row is newly allocated and the input is untouched. Python’s arbitrary-precision shift capability does not expand the supported n: the common bound limits real output size. No itertools/recursive helper implements the production generation. Read [`python/solution.py`](python/solution.py). Importing it performs no demonstration.

## 14. C++ Implementation

Validate n≤16 before Word{1}<<n, and test Word{1}<<index only for 0≤index<n. Both counts are strictly below the 32-bit width. This avoids undefined shifts at n=32 and prevents overflow of the 2^n loop bound. Input values themselves are never shifted; they remain signed numeric payloads. Read [`cpp/solution.cpp`](cpp/solution.cpp), namespace atlas_bit. Define ALGORITHM_ATLAS_NO_MAIN when including it in an API driver. C++17 and C++20 use the same standard-library implementation.

## 15. Input and Output Examples

From the repository root:

```sh
printf '%s\n' '1 1' | .venv/bin/python dsa/bit-manipulation/subset-generation-bitmasking/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/bit-manipulation/subset-generation-bitmasking/cpp/solution.cpp -o /tmp/atlas-bit-example
printf '%s\n' '1 1' | /tmp/atlas-bit-example
```

Both output:

```json
[[],[1],[1],[1,1]]
```

Replace -std=c++17 with -std=c++20 for that build. Tokens are signed decimal values without a count prefix. CLI errors exit 2 with error: on stderr, without partial output.

## 16. Edge Cases

Empty input gives [[]], not an empty output. One zero or negative value is valid. Duplicate-valued positions retain repeated rows. Boundary payloads do not affect masks. n=16 is supported; n=17 and n=32 are rejected before any shift/output growth, as are invalid numeric types and values.

[Python tests](tests/test_python.py) and [C++ tests](tests/test_cpp.py) use [independent oracles](../bit_oracles.py), deterministic random cases and numeric boundaries. Exact vector counts, seeds and executed outcomes are recorded in [checkpoints](../../../docs/bit-manipulation-checkpoints.md).

## 17. Advantages

Straightforward iterative enumeration, exact positional semantics and deterministic mask order.

## 18. Disadvantages and Limitations

Eager output grows exponentially and is capped at 16 positions. It is not a distinct-value subset algorithm, a lazy generator or a large-dimension search strategy. Even valid maximum output consumes material memory.

## 19. When to Use It

Choose for small positional power sets where increasing-mask order is useful and complete materialization is affordable.

## 20. When Not to Use It

Use lazy/recursive branch pruning for bounded searches that need only some subsets; do not increase n without revisiting output and memory budgets.

## 21. Comparison With Related Algorithms

The existing [Power Set Generation](../../recursion-and-backtracking/power-set-generation/README.md) uses exclude/include recursion and a different row order. It remains a separate canonical technique. Tests compare row multisets to preserve duplicate counts, and use independent positional recursion to verify exact mask ordering here.

## 22. Interview Questions

Why is [1,1] allowed to produce duplicate rows? Which bit selects position zero? What happens to 1<<n at the machine width? Why is O(n) space alone misleading for this eager API?

## 23. Practice Problems

Write all masks for [a,b,c]. Count size-k rows for duplicate zeros using binomial coefficients. Compare with the existing backtracking Power Set as a multiset. Design a separate lazy contract without changing positional identities.

## 24. References

[C++17 working draft N4659](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/n4659.pdf), integral conversion and unsigned arithmetic rules; [Python integer bitwise semantics](https://docs.python.org/3/library/stdtypes.html#bitwise-operations-on-integer-types); [Sean Eron Anderson’s Bit Twiddling Hacks](https://graphics.stanford.edu/~seander/bithacks.html). The exact API and validation policy are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
