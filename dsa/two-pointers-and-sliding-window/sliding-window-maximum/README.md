# Sliding Window Maximum

## 1. Algorithm Name

Sliding Window Maximum

## 2. Overview

Maintain a monotonic deque of candidate indices to return the maximum of every complete fixed-size window.

## 3. Problem Statement

Return maximum values for windows [i,i+k) in input order, supporting arbitrary signed values and duplicates.

**API:** solve(values,k); C++ sliding_max. Values ±10^9, n≤10000. For nonempty input require 1≤k≤n; empty input requires k=0 and returns [].

[Shared contracts](../../../docs/two-pointers-sliding-window-conventions.md) specify numeric/byte domains, invalid-input behavior, resource bounds and exact CLI grammar.

## 4. Why Do We Need This Algorithm?

Recomputing max over each k-element window costs O(nk). A deque discards candidates that cannot become a future window maximum.

## 5. Real-World Applications

Bounded rolling-peak analysis, local maximum filters and moving-window numeric exercises where all complete fixed-size windows are required.

## 6. Core Intuition

A newer value at least as large as an older one dominates it: the newer value is no worse and expires later. Retain only candidates not dominated by later values, in descending value order.

## 7. Prerequisites

Deque push/pop at both ends, indexed arrays, complete-window boundaries and amortized analysis. Negative values need no special restriction for maximum comparison.

## 8. Step-by-Step Working Process

Validate input and k before indexing. On each index, expire deque-front indices outside the window. Pop back candidates with value≤the new value, retaining the newest representative on equality. Append the new index. Once at least k values have arrived, append the front candidate value to the output.

**Correctness:** Deque indices increase, all candidates lie in the active window, and their values strictly decrease. Removing expired indices cannot affect a valid current window. Removing a dominated older candidate is safe for every future window containing it, because the newer candidate is at least as large and survives at least as long. Therefore the front is the active maximum. Every complete window is reported once after its right endpoint arrives.

## 9. Pseudocode

```text
validate array/k; handle empty input
queue=[]; result=[]
for index in increasing order:
    remove front indices outside [index-k+1,index]
    while queue nonempty and values[back]<=values[index]: pop back
    push index
    if index+1>=k: append values[front]
return result
```

## 10. Dry Run

For [1,3,-1,-3,5,3,6,7], k=3, the first deque front is value 3. Sliding drops expired candidates and the arriving 5 dominates previous smaller values. Outputs are [3,3,5,5,6,7]. Equal maxima keep the later index, but only maximum values are returned.

## 11. Time Complexity

O(n) validation plus amortized deque work: each index is appended once and removed at most once. A single arrival can pop many candidates, but the total over the scan is linear. No random-input or nonnegative-sum assumption is needed. k=1 and k=n follow the same bound.

## 12. Space Complexity

O(k) auxiliary candidate indices and O(n-k+1) returned values for nonempty input. Empty input returns [] with constant work. No copy of each window is built.

## 13. Python Implementation

collections.deque supplies the data structure; the implementation itself performs expiry and domination logic. It does not call max on every production window. Read [`python/solution.py`](python/solution.py). Importing it runs no example.

## 14. C++ Implementation

std::deque<size_t> stores original indices. Validation precedes conversion of k to size_t; expiration compares front+window≤index, avoiding unsigned subtraction underflow. With n≤10000, that addition is safely bounded. Read [`cpp/solution.cpp`](cpp/solution.cpp). Define ALGORITHM_ATLAS_NO_MAIN in an API test driver. Both C++17 and C++20 are tested.

## 15. Input and Output Examples

From the repository root:

```sh
printf '%s\n' '3 1 3 -1 -3 5 3 6 7' | .venv/bin/python dsa/two-pointers-and-sliding-window/sliding-window-maximum/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/two-pointers-and-sliding-window/sliding-window-maximum/cpp/solution.cpp -o /tmp/atlas-category-example
printf '%s\n' '3 1 3 -1 -3 5 3 6 7' | /tmp/atlas-category-example
```

Both print:

```json
[3,3,5,5,6,7]
```

C++20 uses -std=c++20. Decimal tokens have no array length prefix; consult the shared contract for each operation’s arity and scalar-prefix or hex-string syntax.

## 16. Edge Cases

Empty/k=0, one element, k=1, k=n, repeated equal values, increasing/decreasing arrays and all-negative arrays are tested. Empty with positive k, nonempty with zero k, k>n, negative k and invalid values are rejected. There are no partial windows in the output.

[Python tests](tests/test_python.py) and [C++ tests](tests/test_cpp.py) exercise deterministic vectors, independent references and invalid contracts. Actual seeds/counts/results are recorded in [checkpoints](../../../docs/two-pointers-sliding-window-checkpoints.md).

## 17. Advantages

Linear total work for every signed-value ordering with explicit candidate invariants.

## 18. Disadvantages and Limitations

This API returns values only, not argmax identities or partially filled windows. Deque memory can reach k on a decreasing array. It is a static eager scan, not a streaming object with a mutation interface.

## 19. When to Use It

Choose for all complete fixed-size rolling maxima when bounded linear work matters.

## 20. When Not to Use It

Use a different structure for arbitrary nonsequential range queries, changing window endpoints or updates outside this scan contract.

## 21. Comparison With Related Algorithms

Brute-force max over every small window is an independent O(nk) oracle. A segment tree answers arbitrary ranges with different preprocessing/query costs; this algorithm exploits monotone window movement instead.

## 22. Interview Questions

Why may a newer equal value replace an older one? Why can a single large pop loop still be amortized linear? Why do negative values not break the invariant?

## 23. Practice Problems

Trace a decreasing array and an all-equal array. Compare all valid k on bounded signed arrays with brute-force windows. Prove candidate expiry and dominance separately.

## 24. References

[UCSD two-pointer/sliding-window lesson](https://ucsdicpc.github.io/slides/two_pointers_lesson.pdf) and [Python deque documentation](https://docs.python.org/3/library/collections.html#collections.deque). The monotonic-candidate proof is derived explicitly here. The bounded API and output/tie rules are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
