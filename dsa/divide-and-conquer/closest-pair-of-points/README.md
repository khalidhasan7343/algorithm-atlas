# Closest Pair of Points

## 1. Algorithm Name

Closest Pair of Points

## 2. Overview

Find the nearest pair among planar integer points using an x-ordered split, recursive half solutions, and a narrow y-ordered strip. Sorting helpers support the decomposition; the closest-pair logic itself is implemented directly.

## 3. Problem Statement

Input is a finite sequence of coordinate pairs, each a native integer (x,y) in [-10^9,10^9]. Return `(squared_distance,i,j)` with original indices i<j, minimizing that full tuple lexicographically. Fewer than two points return None/nullopt (CLI null). Identical coordinates at different positions are valid distinct points and can have distance zero. Output uses squared Euclidean distance exactly; it does not return a rounded square root. Caller order and coordinates remain unchanged.

## 4. Why Do We Need This Algorithm?

A brute-force pair scan examines Θ(n²) pairs. Spatial partitioning can restrict cross-half candidates while retaining every pair capable of beating or tying the best half answer.

## 5. Real-World Applications

- Find nearby object-coordinate pairs in small integer spatial datasets.
- Detect coincident measurement positions while retaining original record identities.
- Build an exact nearest-pair baseline for geometry experiments. Applications needing floating coordinates, geographic distances, or different dimensions require a separately specified model.

## 6. Core Intuition

After solving both x-halves, a better crossing pair must be close to the dividing line. Merge the halves by y, then compare only strip successors whose vertical gap is at most the current best distance. Separation inside each half bounds that neighborhood by a constant.

## 7. Prerequisites

Understand Euclidean squared distance, lexicographic sorting, balanced recursion, stable merging, and geometric packing. [Merge Sort](../../sorting/merge-sort/README.md) explains why returning sorted child results allows a linear combine instead of sorting anew at every level.

## 8. Step-by-Step Working Process

1. Validate every point, retain its original index, and sort by (x,y,index).
2. Scan adjacent equal coordinates. If any exist, return the lexicographically smallest original-index pair at distance zero; this also removes the zero-separation degeneracy from the strip proof.
3. For ranges of at most three points, check all pairs and return a y-sorted list. Larger ranges split by x rank, so even a vertical line halves by count.
4. Solve each half and merge returned lists by (y,x,index) in linear time.
5. Include strip points with squared x-gap <= best distance squared. For each point, inspect successors while squared y-gap <= current best; compare full distance/index tuples. Inclusive boundaries preserve equal-distance ties.
6. Return the best pair and merged y-list. A global optimum is in one half or crosses the split; any crossing optimum no worse than the half best lies in the strip and passes the y-gap test, proving completeness. The tuple comparison proves deterministic tie selection.

## 9. Pseudocode

```text
sort by (x,y,index); handle duplicate coordinates
solve(lo,hi):
  if size<=3: brute pairs; return best, y-sorted points
  mid=lo+(hi-lo)//2; split_x=points[mid].x
  left,ly=solve(lo,mid); right,ry=solve(mid,hi)
  best=min(left,right); merged=merge_by_y(ly,ry)
  strip=[p in merged where (p.x-split_x)^2<=best.d2]
  for p in strip:
    for later q while (q.y-p.y)^2<=best.d2:
      best=min(best,(distance_squared(p,q),min_index,max_index))
  return best,merged
```

## 10. Dry Run

For original points `[(0,0),(3,4),(0,1),(3,5)]`, x-sort gives indices 0,2,1,3. The left half has pair (0,2) at squared distance 1; right has (1,3), also distance 1. The tuple rule chooses (1,0,2). Merge by y as indices 0,2,1,3; the strip around split_x=3 includes only the right x=3 points, so no cross pair improves it. A duplicate example `[(8,8),(9,9),(8,8),(0,0),(0,0)]` must return (0,0,2), even though the (0,0) coordinate group sorts first: original indices, not coordinate order, break ties.

## 11. Time Complexity

Initial sorting is O(n log n). Nonduplicate recursion satisfies T(n)=T(floor(n/2))+T(ceil(n/2))+Θ(n), yielding O(n log n): y-merging and strip filtering are linear, and geometric separation bounds successor comparisons by a constant. The implementation does not re-sort full strips/subproblems, avoiding O(n log² n). Its while loop uses an inclusive y-gap rather than a fragile hard-coded seven-successor tie cutoff; the same packing bound stays constant including boundaries. Duplicate detection may return after sorting; Python Timsort can be linear on already ordered/all-equal data. Best cost is at least Ω(n) validation; no distributional average is asserted, and O(n log n) remains the worst-case bound.

## 12. Space Complexity

Auxiliary storage is O(n): the indexed x-order, returned/merged y-lists, strip, and live recursive child data form a geometric sum along an active branch. Recursion depth is O(log n). Only one pair is returned. CLI tokens add O(n) input storage; no n×n distance matrix is allocated.

## 13. Python Implementation

[Complete runnable Python source](python/solution.py). API: `closest_pair(points) -> tuple[int,int,int] | None`. Integer fields require native int; bools, floats, strings, None, and int subclasses are invalid integer fields (TypeError). Domain/shape/range errors raise ValueError. Sequence inputs must be finite and indexable. Inputs are read only; outputs own their storage. The main guard prevents import-time demonstrations. No third-party runtime dependency is needed.

## 14. C++ Implementation

[Complete runnable C++ source](cpp/solution.cpp). API in namespace `algorithm_atlas`: `closest_pair(const vector<pair<long long,long long>>&) -> optional<ClosestPair>`. Define `ALGORITHM_ATLAS_NO_MAIN` before including it in a driver. Supported standards are C++17 and C++20; only standard headers are used. Invalid input raises std::invalid_argument. Resource failures remain errors. Exact numeric representation and bounds are part of the contract above; there is no silent overflow or approximate-success fallback.

## 15. Input and Output Examples

Run from this algorithm directory:

```sh
printf '4 0 0 3 4 0 1 3 5\n' | python3 python/solution.py
g++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-closest-pair-of-points
printf '4 0 0 3 4 0 1 3 5\n' | /tmp/atlas-closest-pair-of-points
```

Both commands print:

```json
[1,0,2]
```

CLI grammar: n followed by exactly n x/y pairs; n may be zero. Whitespace-separated ASCII signed decimal tokens only.
Output is one compact JSON value and newline. Invalid input exits nonzero,
writes stderr, and produces no result. Decimal strings in JSON preserve exact
integers without relying on a consumer's floating-point numeric precision.

From the repository root, run both language suites:

```sh
.venv/bin/python -m pytest -q --require-cpp dsa/divide-and-conquer/closest-pair-of-points/tests
```


## 16. Edge Cases

Empty/singleton, horizontal/vertical/collinear, lattice ties, identical points, duplicate groups, negative and ±10^9 coordinates, and seeded random sets are tested. Independent brute-force tuples check exact distance and original-index ties, including exhaustive repeated small point sequences. Invalid shape/types/ranges and malformed count-prefix CLIs are rejected. Tests compare inputs before/after.

## 17. Advantages

Worst-case subquadratic pair selection with exact integer comparisons, deterministic record identity, and no floating tolerance choices. Rank splits remain balanced even when x values repeat.

## 18. Disadvantages and Limitations

Only 2D integer coordinates within ±10^9 are supported. C++ differences fit ±2·10^9; each squared difference is ≤4·10^18 and their sum ≤8·10^18, fitting signed 64-bit. These limits are validated before arithmetic and match Python. JSON distance numbers can exceed 2^53; consumers must preserve integer precision. The API supplies squared distance, not an approximate length. No streaming updates, nearest-k, higher-dimensional or geographic metric mode is provided; very large inputs can exhaust memory.

## 19. When to Use It

Use it for exact static planar nearest-pair queries under the documented integer coordinate bounds.

## 20. When Not to Use It

Avoid it when points are dynamic, dimensions/metrics differ, floating-point noise is part of the model, or n is tiny enough that a direct pair scan is simpler.

## 21. Comparison With Related Algorithms

| Method | Worst time | Main tradeoff |
| --- | --- | --- |
| This divide/conquer | O(n log n) | O(n) memory and y-merge bookkeeping |
| Brute force | Θ(n²) | Very simple small-case oracle |
| Spatial indexing | Dataset/update dependent | Useful for repeated queries; separate data structure |

## 22. Interview Questions

1. Why split by rank instead of by the number of points strictly left of an x coordinate?
2. Why must equality be included in the strip and y-gap tests?
3. Why handle duplicate coordinates before the packing argument?
4. Where would sorting each strip change the recurrence?

## 23. Practice Problems

1. Trace a vertical line with equal adjacent distances.
2. Construct tied closest pairs that cross the split.
3. Instrument strip comparisons on a large integer grid and explain why they remain linear per level.

## 24. References

- [University of Hawaii ICS311: divide/conquer, maximum subarray, and recurrences](https://courses.ics.hawaii.edu/ics311_f26/Notes/Topic-07.html).
- [Carnegie Mellon: deterministic closest-pair lecture and strip analysis](https://www.cs.cmu.edu/~15451-f18/lectures/lec23-closest-pair.pdf).
- [Carnegie Mellon algorithm notes](https://www.cs.cmu.edu/~avrim/451f11/lectures/lects1-10.pdf), including Karatsuba and Strassen algebra. Code and contract-specific proofs in this lesson are original educational implementations.

## 25. Author Attribution

Algorithm Atlas is maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). See the [MIT license](../../../LICENSE), [contribution policy](../../../CONTRIBUTING.md), and [development standards](../../../docs/development.md). This canonical A4 topic does not authorize implementing any other category. Passing tests does not imply owner review or phase approval.
