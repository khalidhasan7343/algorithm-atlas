# Maximum Subarray using Divide and Conquer

## 1. Algorithm Name

Maximum Subarray using Divide and Conquer

## 2. Overview

Find a maximum-sum nonempty contiguous interval by recursively solving the left half, right half, and intervals crossing the split. This implementation demonstrates the O(n log n) divide-and-conquer formulation.

## 3. Problem Statement

Given n integer values, return `(sum,start,end)` with a zero-based half-open interval [start,end). Maximize sum; break ties by smallest start, then smallest end. Empty input returns None/nullopt (CLI null); an empty interval never competes with a nonempty answer. Python accepts arbitrary-size native ints. C++ accepts signed 64-bit values and returns an exact two-word signed-magnitude sum, exposed as `decimal(answer.sum)`. Both CLIs encode `["sum",start,end]`. No caller data is changed.

## 4. Why Do We Need This Algorithm?

A best interval may lie wholly inside either half or cross the midpoint. Treating those three exhaustive cases separately makes the recursive correctness proof explicit, even though a different linear algorithm exists.

## 5. Real-World Applications

- Identify a strongest contiguous net-gain interval in a small ordered series.
- Analyze consecutive event-score segments.
- Provide a recursive reference for comparing segment optimizers. Real financial or sensor models require their own assumptions beyond this integer objective.

## 6. Core Intuition

A crossing interval is the best suffix of the left half joined to the best prefix of the right half. Scan each outward from the split; there is no need to enumerate every crossing pair.

## 7. Prerequisites

Understand recursion, half-open ranges, induction, linear scans, lexicographic tie-breaking, and arithmetic-cost assumptions. [Merge Sort](../../sorting/merge-sort/README.md) uses the same balanced range decomposition.

## 8. Step-by-Step Working Process

1. Validate integer elements; return no result for n=0.
2. For a one-element range, that element is its only answer.
3. Split at lo+(hi-lo)//2 and recurse on both halves.
4. Scan leftward for the maximum suffix, favoring smaller starts on ties.
5. Scan rightward for the maximum prefix, favoring smaller ends.
6. Compare left, right, and crossing candidates with the same total/start/end ordering. Every nonempty interval belongs to one of those cases; induction proves each candidate is best in its case, so the chosen result is globally correct.

## 9. Pseudocode

```text
solve(lo,hi):
  if hi-lo = 1: return (values[lo],lo,hi)
  mid = lo+(hi-lo)//2
  left = solve(lo,mid); right = solve(mid,hi)
  suffix = best left suffix ending at mid
  prefix = best right prefix starting at mid
  cross = (suffix.sum+prefix.sum,suffix.start,prefix.end)
  return best(left,right,cross) using sum desc, start asc, end asc
```

## 10. Dry Run

For `[-2,1,-3,4,-1,2,1,-5,4]`, split at index 4. The left result is (4,3,4). The right result is (4,8,9). Scan left from index 3: sums 4,1,2,0; the best suffix is [3,4) with sum 4. Scan right: -1,1,2,-3,1; the best prefix is [4,7) with sum 2. Combine to (6,3,7), beating both halves. For `[0,0]`, all sums tie and [0,1) wins by earliest start/end. For `[-4,-2,-2]`, [1,2) wins; it never returns zero from an empty interval.

## 11. Time Complexity

For n≥2, T(n)=T(floor(n/2))+T(ceil(n/2))+Θ(n), with T(1)=Θ(1); therefore Θ(n log n). The algorithm scans every nontrivial range regardless of payload values, so best/average/worst bounds agree in the unit-cost model; no input distribution is required. Empty is Θ(1). Python arbitrary-size additions/comparisons introduce a factor O(B+log(n+1)) bits for B-bit inputs. C++ two-word arithmetic is fixed-cost on the documented platform.

## 12. Space Complexity

Auxiliary storage is O(log n) frames: no slices or prefix arrays are allocated, and crossing scans retain constant candidates per level. Output is one interval. Python integer temporaries use O(log(n+1)·(B+log(n+1))) bits as a safe stack bound. C++ exact magnitude fits 128 bits because at most SIZE_MAX signed 64-bit values contribute; static_assert requires size_t≤64 bits and 64-bit long long. CLI parsing stores O(n) input values separately from API workspace.

## 13. Python Implementation

[Complete runnable Python source](python/solution.py). API: `maximum_subarray(values) -> tuple[int,int,int] | None`. Integer fields require native int; bools, floats, strings, None, and int subclasses are invalid integer fields (TypeError). Domain/shape/range errors raise ValueError. Sequence inputs must be finite and indexable. Inputs are read only; outputs own their storage. The main guard prevents import-time demonstrations. No third-party runtime dependency is needed.

## 14. C++ Implementation

[Complete runnable C++ source](cpp/solution.cpp). API in namespace `algorithm_atlas`: `maximum_subarray(const vector<long long>&) -> optional<Subarray>`. Define `ALGORITHM_ATLAS_NO_MAIN` before including it in a driver. Supported standards are C++17 and C++20; only standard headers are used. Invalid input raises std::invalid_argument. Resource failures remain errors. Exact numeric representation and bounds are part of the contract above; there is no silent overflow or approximate-success fallback.

## 15. Input and Output Examples

Run from this algorithm directory:

```sh
printf '-2 1 -3 4 -1 2 1 -5 4\n' | python3 python/solution.py
g++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-maximum-subarray-divide-and-conquer
printf '-2 1 -3 4 -1 2 1 -5 4\n' | /tmp/atlas-maximum-subarray-divide-and-conquer
```

Both commands print:

```json
["6",3,7]
```

CLI grammar: zero or more values; no length prefix. Whitespace-separated ASCII signed decimal tokens only.
Output is one compact JSON value and newline. Invalid input exits nonzero,
writes stderr, and produces no result. Decimal strings in JSON preserve exact
integers without relying on a consumer's floating-point numeric precision.

From the repository root, run both language suites:

```sh
.venv/bin/python -m pytest -q --require-cpp dsa/divide-and-conquer/maximum-subarray-divide-and-conquer/tests
```


## 16. Edge Cases

Empty, singleton, all-negative, repeated zeros, equal optima, mixed signs, signed endpoints, and sums beyond signed 64-bit are covered. Invalid Python integer fields are rejected, while C++ rejects overflowing CLI tokens. Exhaustive short sequences and seeded full-range values are compared against independent enumeration of every nonempty interval. Inputs are checked unchanged.

## 17. Advantages

Balanced recursion gives a direct exhaustive-case proof. Crossing scans avoid quadratic enumeration, and deterministic ties make Python/C++ exact answers reproducible.

## 18. Disadvantages and Limitations

This O(n log n) algorithm is slower asymptotically than a linear maximum-subarray algorithm. Python big integers add bit costs; C++ input elements are 64-bit even though total sums can be wider. There is no empty-subarray, circular, streaming, or all-optima mode. Extremely large inputs can exhaust memory before arithmetic bounds become relevant.

## 19. When to Use It

Use it to study divide/conquer/combine reasoning or obtain a deterministic recursive baseline for static integer sequences.

## 20. When Not to Use It

Avoid it for streaming updates or when minimum time for one static maximum interval is the sole goal.

## 21. Comparison With Related Algorithms

| Method | Time | Distinction |
| --- | --- | --- |
| This recursive variant | Θ(n log n) | Scans crossing suffix/prefix at every split |
| [Planned Kadane](../../dynamic-programming/kadane/README.md) | O(n) classical formulation | Separate catalog topic; not implemented here |
| Exhaustive oracle | O(n²) with incremental sums | Test-only small-case reference |

## 22. Interview Questions

1. Why must a crossing interval include both sides?
2. Why does starting the best sum at zero fail for all-negative data?
3. How do suffix/prefix ties preserve the global interval tie rule?
4. Why is the stack logarithmic without array slices?

## 23. Practice Problems

1. Trace `[-5,-1,-1]` and `[0,0,0]`.
2. Derive the recurrence level by level.
3. Design an empty-interval-permitted variant and state how its contract differs; do not silently change this one.

## 24. References

- [University of Hawaii ICS311: divide/conquer, maximum subarray, and recurrences](https://courses.ics.hawaii.edu/ics311_f26/Notes/Topic-07.html).
- [Carnegie Mellon: deterministic closest-pair lecture and strip analysis](https://www.cs.cmu.edu/~15451-f18/lectures/lec23-closest-pair.pdf).
- [Carnegie Mellon algorithm notes](https://www.cs.cmu.edu/~avrim/451f11/lectures/lects1-10.pdf), including Karatsuba and Strassen algebra. Code and contract-specific proofs in this lesson are original educational implementations.

## 25. Author Attribution

Algorithm Atlas is maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). See the [MIT license](../../../LICENSE), [contribution policy](../../../CONTRIBUTING.md), and [development standards](../../../docs/development.md). This canonical A4 topic does not authorize implementing any other category. Passing tests does not imply owner review or phase approval.
