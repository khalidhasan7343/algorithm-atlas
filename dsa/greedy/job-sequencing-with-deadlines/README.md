# Job Sequencing with Deadlines

## 1. Algorithm Name

Job Sequencing with Deadlines

## 2. Overview

Choose and schedule unit-duration jobs on one machine to maximize earned profit before their deadlines. Greedy processes the most profitable jobs first and puts each at its latest available feasible slot.

## 3. Problem Statement

All jobs are independent, available from time zero and take exactly one unit. Slot s is [s-1,s), so a job in slot s meets deadline d when s≤d. Deadlines are integers 0..10^9; deadline zero is valid but unschedulable, negative deadlines are invalid. Profits are integers in [-10^9,10^9]; nonpositive-profit jobs are omitted. Equal positive profits prefer lower original index. Accept n≤10000 with equal deadline/profit lengths. Return (total profit,slots), where each slot is an original job index or None/null. The fixed returned horizon is H=min(n,max(deadlines,default=0)); even unused trailing slots remain represented.

## 4. Why Do We Need This Algorithm?

Taking an early-deadline job first can waste a slot on low profit. Profit order protects high-value choices; putting each chosen job as late as possible keeps earlier slots open for tighter deadlines.

## 5. Real-World Applications

Selecting profitable, independent unit-length tasks before due times fits this model. Real production jobs with variable durations, release times, precedence or multiple machines need a different scheduler; this is not general weighted job scheduling.

## 6. Core Intuition

Consider jobs by decreasing profit and original index. Query the last free slot at or before the job deadline, clamped to H. Occupy it if positive; otherwise skip. Slot zero is a permanent “no available slot” sentinel. A disjoint-set structure merges each occupied free boundary with its preceding component.

## 7. Prerequisites

Sorting, unit-slot schedules, greedy exchange, disjoint-set union, path compression and union by rank. Compare [Activity Selection](../activity-selection/README.md): its intervals have fixed endpoints, whereas these jobs may choose any feasible unit slot.

## 8. Step-by-Step Working Process

Validate domains and allocate slots/parent/rank/available arrays for 0..H. Each initial component has available[s]=s. A component represents an occupied consecutive block plus its left free boundary; store that boundary independently of the representative chosen by union rank. Query available[find(min(deadline,H))]. If nonzero, write the job index to that slot and union its component with find(slot-1), keeping the smaller available boundary. Path compression and rank keep queries efficient without changing the boundary meaning.

Correctness of feasibility: latest placement preserves earlier capacity. If no slot is free before d, expanding the saturated prefix to cover the capped deadlines of its occupants yields a saturated prefix ending T whose T occupants must all finish by T. Adding the candidate would require T+1 completions by T, impossible. Thus the slot structure accepts exactly feasible additions.

Greedy-choice/exchange: feasible unit-job subsets obey the nested capacity constraints count(deadline≤t)≤t for every t. This family is hereditary. For feasible A,B with |A|<|B|, if no b in B\A can augment A, each such b lies in an A-tight prefix. Their largest tight prefix contains all B\A; feasibility of B then forces |B\A|≤|A\B|, a contradiction. This is the exchange property of a matroid. Its weighted greedy exchange lets the next highest-profit feasible job replace a no-more-profitable unchosen job in an optimum; previously chosen jobs stay fixed. Induction proves maximum profit. Omitting nonpositive profits cannot decrease it. Clamping deadlines to n is safe because at most n jobs can be scheduled.

## 9. Pseudocode

```text
H ← min(n, maximum deadline or 0)
initialize disjoint sets 0..H, each with its own free boundary
slots[1..H] ← empty; total ← 0
for i in positive-profit, positive-deadline jobs sorted by (-profit,index):
    s ← available[find(min(deadline[i],H))]
    if s>0:
        slots[s] ← i; total ← total+profit[i]
        union components of s and s-1 using rank/path compression
        new component available ← minimum of their available boundaries
return total,slots
```

## 10. Dry Run

Jobs 0:(d=2,p=100), 1:(1,19), 2:(2,27), 3:(1,25), 4:(3,15), H=3:

| Profit-order job | Latest free ≤ deadline | Slots after | Profit |
| --- | --- | --- | --- |
| 0 | 2 | [empty,0,empty] | 100 |
| 2 | 1 | [2,0,empty] | 127 |
| 3 | none | [2,0,empty] | 127 |
| 1 | none | [2,0,empty] | 127 |
| 4 | 3 | [2,0,4] | 142 |

All selected completion slots meet their deadlines and each original position appears once. Return profit 142 and slots [2,0,4].

## 11. Time Complexity

Let n be input jobs, q eligible positive jobs and H≤n the horizon. Validation and initialization cost O(n+H); sorting costs O(q log(q+1)). Union by rank with path compression gives O(q·α(H+1)) amortized slot operations, where α is the inverse Ackermann function. Total worst upper bound is O(n log(n+1)), independent of the numerical magnitude of deadlines. When q=0, the work is O(n+H); sorting can adapt to order in Python. No probability distribution is assumed for an average-case number. A backwards linear slot scan would instead take O(nH) worst time.

## 12. Space Complexity

O(n+H) auxiliary indices/disjoint-set arrays plus O(H) returned optional indices; H≤n. No recursion is used in find, so long chains do not consume the Python call stack. Keeping available separately from the representative allows rank balancing while preserving the latest-free-slot meaning. Input profits/deadlines are not mutated.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `job_sequencing(deadlines, profits)`. Native integer inputs exclude bool and floating point; invalid data/resource bounds raise ValueError. Inputs are read only, results own their containers, and importing the module performs no I/O. The implementation follows the strategy in sections 6–9.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) exposes `job_sequencing(deadlines, profits)` in namespace `atlas_greedy`. Define `ALGORITHM_ATLAS_NO_MAIN` when including it in an API driver. C++17 and C++20 use standard containers and signed 64-bit integers. The shared [header](../common.hpp) handles validation/CLI utilities; the algorithm itself is implemented in this canonical source. Invalid data/resource bounds throw invalid_argument. Inputs are const references.

## 15. Input and Output Examples

From the repository root, input is **count n followed by n deadline/profit pairs**. Numeric tokens are ASCII signed decimal integers. Counts must match exactly; missing, malformed or extra tokens produce exit 2, a stderr diagnostic, and empty stdout. A successful run prints one JSON value and a newline.

```sh
printf '%s\n' '5 2 100 1 19 2 27 1 25 3 15' | .venv/bin/python dsa/greedy/job-sequencing-with-deadlines/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/greedy/job-sequencing-with-deadlines/cpp/solution.cpp -o /tmp/atlas-job-sequencing-with-deadlines
printf '%s\n' '5 2 100 1 19 2 27 1 25 3 15' | /tmp/atlas-job-sequencing-with-deadlines
```

Both print:

```text
{"profit":142,"slots":[2,0,4]}
```

Use `-std=c++20` for the other supported standard. Run `.venv/bin/python -m pytest dsa/greedy/job-sequencing-with-deadlines --require-cpp` to execute Python, C++17 and C++20 tests. Independent expected values and boundary cases are in the [test cases](tests/cases.py).

## 16. Edge Cases

Empty input gives (0,[]). All zero deadlines produce an empty horizon. Nonpositive jobs are omitted; their deadlines can still contribute to the documented fixed horizon. Duplicate deadlines compete for slots and equal profits prefer lower original index. With deadlines [2,2], profits [5,5], slots are [1,0] because job 0 takes the latest slot first. Huge sparse deadlines are clamped before allocation. Independent tests enumerate every small job subset and use sorted-deadline feasibility, then compare optimal profit and verify each returned witness.

## 17. Advantages

The strategy is optimal for the specified unit-job model. It returns a checkable schedule and handles large sparse deadlines with O(n), rather than O(max deadline), storage.

## 18. Disadvantages and Limitations

The exchange proof relies on unit duration, one machine, no release times and independent jobs. It does not solve arbitrary-duration weighted interval scheduling. Nonpositive profits are intentionally not used to fill idle slots. Total positive profit is at most 10000·10^9=10^13, safely within signed-64; deadlines are clamped before conversion to slot sizes. The 10000-job cap is explicit. Different equal-profit rules could return different optimal schedules.

## 19. When to Use It

Use for independent unit-duration jobs when only completed-on-time jobs earn their stated profit and leaving slots empty is allowed.

## 20. When Not to Use It

Use other scheduling models for variable processing times, multiple machines, precedence or fixed intervals. Do not infer a general weighted scheduling solution from this unit-task greedy rule.

## 21. Comparison With Related Algorithms

| Model/data structure | Main approach | Worst work |
| --- | --- | --- |
| This unit-job model | profit greedy + ranked disjoint slots | O(n log n) total |
| Same greedy with backwards scan | search empty slot directly | O(nH) after sort |
| Activity Selection | fixed equal-reward intervals | earliest finish |
| Weighted interval scheduling | fixed intervals/rewards | DP, different contract |

## 22. Interview Questions

Why place a chosen job as late as possible? Why does clamping deadlines to n preserve feasibility? Why must available be separate from a rank-selected representative? Which assumption fails for variable-duration jobs? What certifies that rejecting a job is safe?

## 23. Practice Problems

Trace disjoint-set free boundaries for the worked example. Compare the ranked structure with a simple backwards scan on small cases. Then change job durations and construct a counterexample showing why the unit-job proof cannot be reused.

## 24. References

[CLRS-Lean: A Task-Scheduling Problem as a Matroid](https://tanktechnology.github.io/CLRS-Lean/CLRSLean/Chapter_16/Section_16_5_Task_Scheduling/) is original formalization work on unit-task deadlines and the scheduling matroid. This profit-maximizing API and ranked latest-slot implementation are independently specified and proved above; no external implementation is copied.

## 25. Author Attribution

Algorithm Atlas is maintained by **MD.Khalid Hasan** ([GitHub](https://github.com/khalidhasan7343)). See the [repository](https://github.com/khalidhasan7343/algorithm-atlas), [MIT License](../../../LICENSE), and [contribution policy](../../../CONTRIBUTING.md).
