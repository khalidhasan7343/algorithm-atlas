# Activity Selection

## 1. Algorithm Name

Activity Selection

## 2. Overview

Select as many mutually compatible activities as possible on one resource. The implementation sorts by finishing time, then makes a single pass; this is an unweighted cardinality problem.

## 3. Problem Statement

Each activity is an integer half-open interval [start,finish), with start<finish and both times in [-10^9,10^9]. At most 10000 activities are accepted. Touching endpoints are compatible. Return original zero-based indices in selection order. Sort ties by (finish,start,index). Duplicate intervals remain distinct input positions, but their positive durations prevent selecting overlapping copies together. Empty input returns []. Zero-duration and reversed intervals are rejected.

## 4. Why Do We Need This Algorithm?

Choosing the first activity to start or the shortest duration can block more useful later activities. Earliest finishing leaves at least as much remaining time as any other feasible first choice, which supplies a provable local rule.

## 5. Real-World Applications

Single-room reservation selection and choosing nonoverlapping measurement windows fit this model when every chosen activity has equal benefit. Multiple rooms, setup times, preferences or unequal rewards change the optimization problem.

## 6. Core Intuition

Among activities compatible with the last chosen finish, choose the one that finishes earliest. Afterwards only the remaining compatible suffix matters. Sorting once makes this choice available through a linear scan.

## 7. Prerequisites

Arrays, sorting with tuple keys, half-open intervals and induction. Compare [Job Sequencing](../job-sequencing-with-deadlines/README.md), where each job has a flexible slot rather than a fixed start/finish interval.

## 8. Step-by-Step Working Process

Validate the intervals, sort their indices by (finish,start,index), and begin with no previous finish. Accept an index when its start is at least the last chosen finish, then advance that finish. Rejecting an overlapping activity never invalidates an earlier choice.

Greedy-choice exchange: let g be the earliest-finishing compatible activity and let o be the first activity in an optimal remaining schedule. Since finish(g)≤finish(o), replacing o by g preserves every later activity and does not reduce count. The remainder after g has the same problem form, so optimal substructure and induction prove maximum cardinality. Equal-finish choices leave identical future availability; start/index ties make the output deterministic without altering the optimum. The scan invariant is that selected activities are compatible and the chosen prefix can extend to an optimum for the unprocessed choices.

## 9. Pseudocode

```text
order ← original indices sorted by (finish,start,index)
selected ← []; last_finish ← absent
for i in order:
    if last_finish absent OR start[i] ≥ last_finish:
        append i to selected
        last_finish ← finish[i]
return selected
```

## 10. Dry Run

Input indices and intervals: 0:[1,3), 1:[2,5), 2:[3,4), 3:[4,7), 4:[5,6).

| Sorted index | Interval | Last finish before | Decision |
| --- | --- | --- | --- |
| 0 | [1,3) | absent | choose; finish=3 |
| 2 | [3,4) | 3 | choose; finish=4 |
| 1 | [2,5) | 4 | skip overlap |
| 4 | [5,6) | 4 | choose; finish=6 |
| 3 | [4,7) | 6 | skip overlap |

Return [0,2,4], count 3. A different maximum schedule can exist, but the specified key determines this one.

## 11. Time Complexity

For n activities, validation and selection each take O(n), while sorting takes O(n log(n+1)) worst time. Total worst time is O(n log(n+1)); sorting dominates. Python adaptive sorting can make already ordered inputs O(n); C++ std::sort retains its O(n log(n+1)) comparison bound without a stronger best-case promise. Average time needs an input distribution; none is assumed. If a separately validated input is already sorted, the selection step itself is linear.

## 12. Space Complexity

O(n) auxiliary index storage plus up to O(n) output indices. Python sorting may use O(n) temporary storage; C++ sorting typically needs O(log n) stack within the O(n) total bound. Original intervals are not copied or mutated. A caller that already maintains finishing order could stream the selection with O(1) scan state plus output.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `activity_selection(activities)`. Native integer inputs exclude bool and floating point; invalid data/resource bounds raise ValueError. Inputs are read only, results own their containers, and importing the module performs no I/O. The implementation follows the strategy in sections 6–9.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) exposes `activity_selection(vector<Activity>)` in namespace `atlas_greedy`. Define `ALGORITHM_ATLAS_NO_MAIN` when including it in an API driver. C++17 and C++20 use standard containers and signed 64-bit integers. The shared [header](../common.hpp) handles validation/CLI utilities; the algorithm itself is implemented in this canonical source. Invalid data/resource bounds throw invalid_argument. Inputs are const references.

## 15. Input and Output Examples

From the repository root, input is **count n followed by n start/finish pairs**. Numeric tokens are ASCII signed decimal integers. Counts must match exactly; missing, malformed or extra tokens produce exit 2, a stderr diagnostic, and empty stdout. A successful run prints one JSON value and a newline.

```sh
printf '%s\n' '5 1 3 2 5 3 4 4 7 5 6' | .venv/bin/python dsa/greedy/activity-selection/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/greedy/activity-selection/cpp/solution.cpp -o /tmp/atlas-activity-selection
printf '%s\n' '5 1 3 2 5 3 4 4 7 5 6' | /tmp/atlas-activity-selection
```

Both print:

```text
[0,2,4]
```

Use `-std=c++20` for the other supported standard. Run `.venv/bin/python -m pytest dsa/greedy/activity-selection --require-cpp` to execute Python, C++17 and C++20 tests. Independent expected values and boundary cases are in the [test cases](tests/cases.py).

## 16. Edge Cases

Empty input returns []; one valid activity is selected. Fully overlapping input yields one activity. Touching intervals can all be selected. Negative time coordinates are supported; no special zero origin is assumed. Duplicate intervals use the earliest original index after equal finish/start. Validation rejects nonintegers, start≥finish, out-of-range coordinates and n=10001. Independent tests enumerate every positional subset, verify compatibility and maximize its count, then apply the stated deterministic order among optima.

## 17. Advantages

The exchange argument is short, output is deterministic, and selection after sorting is linear. No capacity table or exponential enumeration is needed in production.

## 18. Disadvantages and Limitations

Only one resource and equal activity rewards are modeled. Earliest finish does not generally maximize weighted reward: [0,1) and [1,2), each reward 1, beat a single count-wise choice [0,2) but lose to it if its reward is 100. The 10000-item cap is an educational resource contract. Time values are compared rather than subtracted, so no overflow-sensitive duration calculation is needed.

## 19. When to Use It

Use for maximum count of positive-duration, fixed intervals on one resource when touching endpoints may share it.

## 20. When Not to Use It

Use weighted interval scheduling DP for unequal rewards, interval partitioning for a minimum room count, or a richer scheduler for dependencies and setup times. Closed intervals would require different endpoint compatibility.

## 21. Comparison With Related Algorithms

| Problem/approach | Objective | Appropriate strategy |
| --- | --- | --- |
| Activity Selection here | maximum compatible count | earliest finish |
| Weighted interval scheduling | maximum reward | predecessor-based DP |
| Interval partitioning | minimum simultaneous resources | room allocation |
| Exhaustive subsets | same count objective | small independent oracle |

## 22. Interview Questions

Why does earliest start fail? What exactly is exchanged in the optimal schedule? Why are endpoint-touching intervals compatible? How do duplicate activities and equal finishing times affect the proof and witness?

## 23. Practice Problems

Construct counterexamples to earliest-start and shortest-duration rules. Trace the tie examples in the tests. Then formulate weighted interval scheduling separately and explain why the exchange argument no longer preserves total reward.

## 24. References

[MIT 6.046: Overview and Interval Scheduling](https://ocw.mit.edu/courses/6-046j-design-and-analysis-of-algorithms-spring-2015/resources/lecture-1-course-overview-interval-scheduling/) provides original course material on interval scheduling and greedy analysis. This implementation and its numeric/tie contracts are project-specific; no lecture code is copied.

## 25. Author Attribution

Algorithm Atlas is maintained by **MD.Khalid Hasan** ([GitHub](https://github.com/khalidhasan7343)). See the [repository](https://github.com/khalidhasan7343/algorithm-atlas), [MIT License](../../../LICENSE), and [contribution policy](../../../CONTRIBUTING.md).
