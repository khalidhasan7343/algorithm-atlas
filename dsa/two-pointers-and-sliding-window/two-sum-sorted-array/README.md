# Two Sum in Sorted Array

## 1. Algorithm Name

Two Sum in Sorted Array

## 2. Overview

Move inward from both ends of a validated sorted array to find a deterministic matching index pair.

## 3. Problem Statement

Return the lexicographically smallest [i,j], i<j, whose values sum to target; return [] when no pair exists.

**API:** solve(values,target); C++ two_sum. Sorted nondecreasing signed values ±10^9, n≤10000; target ±2*10^9. Indices are zero-based and refer to the unchanged input.

[Shared contracts](../../../docs/two-pointers-sliding-window-conventions.md) specify numeric/byte domains, invalid-input behavior, resource bounds and exact CLI grammar.

## 4. Why Do We Need This Algorithm?

Sorted order lets one comparison eliminate an entire set of impossible pairs, reducing exhaustive quadratic pair enumeration to a linear scan.

## 5. Real-World Applications

Bounded pair lookup in sorted numeric data, duplicate-aware index exercises and teaching monotone search boundaries. Sorting an unsorted input is not silently performed.

## 6. Core Intuition

If the current sum is too small, even the largest remaining right value cannot rescue the left value. If it is too large, even the smallest remaining left value cannot rescue the right value.

## 7. Prerequisites

Sorted-array order, two-index bounds, lexicographic tie rules and additive comparison. Read [window contracts](../../../docs/two-pointers-sliding-window-conventions.md).

## 8. Step-by-Step Working Process

Validate type, size, numeric bounds, target and nondecreasing order. Initialize left=0,right=n-1. Increase left for a sum below target and decrease right above target. On equality, move right leftward across equal right values while keeping right>left, then return the pair. If pointers meet/cross, return [].

**Correctness:** Every discarded left value has no valid partner in the remaining interval because its largest possible sum is too small. Every discarded right value has no partner at or beyond the current left because its smallest possible sum is too large. Thus the first surviving equality has the smallest possible left index. Equal right values yield the same sum; shrinking across their suffix chooses the earliest valid right index. This proves the specified lexicographic pair while preserving all feasible candidates until found.

## 9. Pseudocode

```text
validate sorted array and target
left=0; right=n-1
while left<right:
    s=values[left]+values[right]
    if s<target: left+=1
    else if s>target: right-=1
    else:
        while right>left+1 and values[right-1]=values[right]: right-=1
        return [left,right]
return []
```

## 10. Dry Run

For [1,1,2,2] and target 3, the first equality is at [0,3]. The equal right-hand 2 at index 2 is earlier, so return [0,2]. For [2,2,2] and target 4, return [0,1]. An empty array has right=-1 and never enters the loop.

## 11. Time Complexity

The scan is O(n) worst case because left only increases and right only decreases, including duplicate shrinking. Numeric/sorted validation scans input even if the first pair matches, so the public API has O(n) valid-array work overall (O(1) for empty/minimal sizes), rather than claiming best O(1) while ignoring validation.

## 12. Space Complexity

O(1) auxiliary scan/validation state and at most two returned indices; no sort, hash table or copied input array is used by the algorithm.

## 13. Python Implementation

A generator validates adjacent sortedness without copying values. The result contains original positions, not selected values; list/tuple inputs remain unchanged. Read [`python/solution.py`](python/solution.py). Importing it runs no example.

## 14. C++ Implementation

Integer positions are signed so empty-array right=-1 is safe; array access occurs only under left<right. Values and target are validated before summing; every sum is within ±2*10^9 and safely fits int64_t. Read [`cpp/solution.cpp`](cpp/solution.cpp). Define ALGORITHM_ATLAS_NO_MAIN in an API test driver. Both C++17 and C++20 are tested.

## 15. Input and Output Examples

From the repository root:

```sh
printf '%s\n' '3 1 1 2 2' | .venv/bin/python dsa/two-pointers-and-sliding-window/two-sum-sorted-array/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/two-pointers-and-sliding-window/two-sum-sorted-array/cpp/solution.cpp -o /tmp/atlas-category-example
printf '%s\n' '3 1 1 2 2' | /tmp/atlas-category-example
```

Both print:

```json
[0,2]
```

C++20 uses -std=c++20. Decimal tokens have no array length prefix; consult the shared contract for each operation’s arity and scalar-prefix or hex-string syntax.

## 16. Edge Cases

Empty/singleton arrays, duplicates, repeated zeros, negative operands, target at either bound and impossible pairs are defined. Unsorted input is rejected instead of silently sorted. Equal-valued positions must still have distinct indices; pointer crossing produces [].

[Python tests](tests/test_python.py) and [C++ tests](tests/test_cpp.py) exercise deterministic vectors, independent references and invalid contracts. Actual seeds/counts/results are recorded in [checkpoints](../../../docs/two-pointers-sliding-window-checkpoints.md).

## 17. Advantages

Linear deterministic pair search with constant working memory and stable original-index output.

## 18. Disadvantages and Limitations

Sortedness is a real precondition and its validation cost is included. The API returns one earliest pair, not every pair or a count of duplicate pair combinations.

## 19. When to Use It

Choose for an already sorted bounded array when one deterministic index pair is needed.

## 20. When Not to Use It

Use a separately specified method for unsorted inputs or all-pair enumeration; sorting here would change original-index semantics.

## 21. Comparison With Related Algorithms

Exhaustive pair loops provide an independent O(n²) oracle. A hash-based unsorted variant has different preprocessing/memory and tie obligations; it is not added as a new canonical.

## 22. Interview Questions

Why does each pointer move safely exclude pairs? Why is shrinking equal right values needed for the tie rule? Why does sorted validation change the best-case API claim?

## 23. Practice Problems

Trace negative/duplicate arrays. Exhaustively compare all sorted small arrays and targets with nested pair loops. Construct an early equality with several possible right indices.

## 24. References

[UCSD ICPC two-pointer/sliding-window lesson](https://ucsdicpc.github.io/slides/two_pointers_lesson.pdf). The exact index tie rule and validation policy are derived here. The bounded API and output/tie rules are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
