# Uniform Cost Search (UCS)

## 1. Algorithm Name

**Uniform Cost Search (UCS)** — best-first search of a state space ordered by accumulated path cost `g(n)`. It is the state-space counterpart of the canonical A5 [Dijkstra's Algorithm](../../../dsa/graph-algorithms/dijkstra/README.md): Dijkstra computes distances from a source to every vertex of an explicit graph, while UCS generates states lazily and stops as soon as a cheapest **goal** is removed from the frontier.

## 2. Overview

UCS always expands the frontier state with the smallest known path cost. With nonnegative step costs, the first goal state removed from the priority queue has minimum cost. Goals are tested on removal, not on generation; a goal generated early through an expensive route is kept in the frontier until any cheaper route has had a chance to appear.

## 3. Problem Statement

**Input.** Initial state `s0`, goal predicate, `successors(state)` yielding `(action, next_state, step_cost)` records, optional `state_key`. Every `step_cost` must be a real number that is **finite and nonnegative**; zero is allowed. `bool`, complex numbers, strings, `None`, NaN, ±∞ and negative values are rejected.

**Output** ([C1 contract](../../../docs/uninformed-search-conventions.md)). `FOUND` with a path to a goal minimizing the path cost

```text
g(n) = Σ c(e)  over every transition e on the returned path from s0 to n
```

with `cost = g(goal)` and actions in path order; or `FAILURE` when no goal is reachable. UCS has no depth bound, so it never returns `CUTOFF`. Equal-cost alternatives are broken deterministically by frontier insertion order (first inserted first).

## 4. Why Do We Need This Algorithm?

BFS and IDDFS minimize the number of actions. When actions have different costs — minutes, fuel, money — the path with the fewest actions can be the most expensive (the example's single toll-bridge road costs 30 minutes while a four-road route costs 15). UCS is the uninformed search that is optimal for general nonnegative costs, and it is A* with the zero heuristic.

## 5. Real-World Applications

- **Route planning on implicit maps** where costs are travel time or distance and the state space is generated on demand.
- **Least-cost planning** in AI problem formulations with action costs (Russell & Norvig, §3.4).
- **Baseline for heuristic search:** A* with `h = 0` is exactly UCS, so UCS results check A* implementations (C2).

Felner (2011) argues that this lazily generated, goal-terminating formulation is often preferable to textbook Dijkstra in AI settings because it never needs the whole graph in memory.

## 6. Core Intuition

Pour water into the start state and let it flow along edges at a speed equal to cost. States are reached in order of their distance from the start. The first goal the water reaches is the cheapest goal. A priority queue simulates this "wavefront" one state at a time.

## 7. Prerequisites

Binary heaps / priority queues, [Dijkstra's Algorithm](../../../dsa/graph-algorithms/dijkstra/README.md) and its greedy-choice proof, [BFS](../../../dsa/graph-algorithms/breadth-first-search/README.md), and the [C1 state-space model](../README.md#10-state-space-search-model).

## 8. Step-by-Step Working Process

1. Set `best[s0] = 0`, push `(0, counter 0, s0)`.
2. Pop the entry with the least `(g, counter)`. If its state is closed or `g ≠ best[state]`, it is **stale** (a cheaper entry superseded it): skip it.
3. Goal-test the state. If it is a goal, rebuild the path from parent links and return `FOUND` with cost `g`.
4. Close the state and generate its successors. For each child not closed, compute `g + c`. If the child is new or `g + c < best[child]` (strictly), record the new best cost, parent and action, and push a new entry with the next counter value.
5. If the frontier empties, return `FAILURE`.

**Correctness.** *Invariant:* when a state `u` is popped non-stale, `best[u]` equals the true minimum cost `g*(u)`. Suppose not, and let `P` be an optimal path to `u`. Some state on `P` is not closed; let `x` be the first one, whose predecessor `p` on `P` is closed with `best[p] = g*(p)` (by the invariant for earlier pops). When `p` was expanded, `x` received `best[x] ≤ g*(p) + c(p, x) = g*(x)`, so `x` is in the frontier with key `g*(x) ≤ g*(u) < best[u]` (costs are nonnegative, so prefixes are no more expensive). The heap would have popped `x` before `u` — contradiction. Hence the first goal popped has cost equal to the minimum over all goals. *Why test on removal:* a goal generated with cost 10 may later be reached with cost 3; returning at generation time would be wrong (tested). *Parent safety:* parents of a closed state never change, and every ancestor of a popped state is closed, so reconstructed paths never use stale predecessor data. *Closed children:* skipping them is safe because `g(u) + c ≥ g(u) ≥ best[closed]`; IEEE-754 addition of a nonnegative value never decreases a number, so this also holds for floats.

## 9. Pseudocode

```text
function UCS(s0, is_goal, successors):
    best[s0] ← 0; parent[s0] ← none; counter ← 1
    frontier ← min-heap {(0, 0, s0)}; closed ← ∅
    while frontier not empty:
        (g, _, s) ← pop-min(frontier)
        if s ∈ closed or g ≠ best[s]: continue            # stale entry
        if is_goal(s): return FOUND(path via parent, cost g)
        closed ← closed ∪ {s}
        for (a, t, c) in successors(s):                  # c finite, c ≥ 0
            if t ∈ closed: continue
            if t ∉ best or g + c < best[t]:
                best[t] ← g + c; parent[t] ← (s, a)
                push(frontier, (g + c, counter, t)); counter ← counter + 1
    return FAILURE
```

## 10. Dry Run

CLI graph with costs: `e0: 0→1 (1)`, `e1: 1→3 (5)`, `e2: 0→2 (2)`, `e3: 2→3 (2)`; start 0, goal 3.

| Pop `(g, counter, state)` | Action | Frontier after |
| --- | --- | --- |
| `(0, 0, 0)` | not goal; expand: `best[1]=1`, `best[2]=2` | `(1,1,1) (2,2,2)` |
| `(1, 1, 1)` | not goal; expand: goal 3 generated with `best[3]=6` | `(2,2,2) (6,3,3)` |
| `(2, 2, 2)` | not goal; expand: `2+2=4 < 6` → improve 3, parent 2 | `(4,4,3) (6,3,3)` |
| `(4, 4, 3)` | goal popped with its best cost → `FOUND [0,2,3]`, cost 4 | `(6,3,3)` stale, never popped |

Stats: 3 expansions, 4 generated, 4 goal tests, 5 pushes, 1 improvement, max frontier 2 — as printed in §15. Stopping when 3 was first generated would have returned cost 6.

## 11. Time Complexity

Variables: `V` states and `E` transitions reachable at cost `≤ C*` (the optimal goal cost), `b` branching factor, `ε` the minimum **positive** step cost.

- **Explicit-graph view:** every state is closed at most once and each transition is relaxed once; there are at most `1 + E` pushes (one per strict improvement), each `O(log E)` on a binary heap. Total `O((V + E) log E)`, i.e. `O((V + E) log V)` for simple graphs, plus `O(1)` expected hashing per generated record.
- **Implicit tree view (Russell & Norvig):** with all costs `≥ ε > 0`, UCS examines paths of up to `1 + ⌊C*/ε⌋` actions, giving `O(b^{1 + ⌊C*/ε⌋})` time; this can be much worse than `O(b^d)` when costs vary widely.
- **Zero-cost edges:** allowed and handled correctly on finite spaces, but they break the `ε`-based bound; an infinite space containing infinitely many states at the same cost may never terminate.
- **Best case:** `O(1)` when `s0` is a goal.

## 12. Space Complexity

`O(V + E)` in the explicit-graph view: `best`, parent links and the closed set are `O(V)`, and the heap can hold one entry per push (`O(E)` including stale entries — lazy deletion trades memory for simplicity). In the implicit view memory is `O(b^{1+⌊C*/ε⌋})`, the main practical limitation. No recursion is used.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) defines `uniform_cost_search(start, is_goal, successors, *, state_key=None)` with `heapq`. Heap entries are `(g, counter, key)`; the unique counter guarantees deterministic FIFO tie-breaking and that states are **never compared** (tested with states whose ordering operators raise). Costs are validated by the shared [`support.step_cost`](../support.py) and summed exactly as given: `int` and `fractions.Fraction` stay exact, `float` follows IEEE-754 rounding, and **no tolerance** is applied (for example `0.1 + 0.2 > 0.3`, so the direct `0.3` edge wins — tested). `stats`: `expanded`, `generated`, `goal_tests`, `pushed`, `stale_skipped`, `improvements`, `max_frontier`.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) defines `atlas_search::uniform_cost_search<State, Action, Cost>(start, is_goal, successors)` returning `SearchResult<State, Action, Cost>`; successors return `std::vector<WeightedStep<State, Action, Cost>>`. States are mapped to dense ids; the frontier is a `std::priority_queue` of `(cost, counter, id)` tuples with `std::greater`. `checked_step_cost` throws `std::invalid_argument` for negative values and, for floating-point `Cost`, for NaN and ±∞; every record of an expansion is validated before any is used. The CLI uses `long long` costs `0 … 10^12`, so sums stay far below `2^63`. Tested under C++17 and C++20.

## 15. Input and Output Examples

Grammar: `n m start g goal_1 … goal_g` then `m` triples `u v cost` with integer `0 ≤ cost ≤ 10^12`.

```sh
printf '4 4 0 1 3  0 1 1 1 3 5 0 2 2 2 3 2\n' | python artificial-intelligence/uninformed-search/uniform-cost-search/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic artificial-intelligence/uninformed-search/uniform-cost-search/cpp/solution.cpp -o /tmp/atlas-ucs
printf '4 4 0 1 3  0 1 1 1 3 5 0 2 2 2 3 2\n' | /tmp/atlas-ucs
```

Both print:

```json
{"status":"FOUND","states":[0,2,3],"actions":[2,3],"cost":4,"depth":2,"stats":{"expanded":3,"generated":4,"goal_tests":4,"pushed":5,"stale_skipped":0,"improvements":1,"max_frontier":2}}
```

A negative or non-integer cost token exits with status 2 and `error: …`.

[`python/example.py`](python/example.py) — the cheapest route is not the one with the fewest roads:

```text
cheapest: A -> B -> C -> E -> D roads ['coast-1', 'coast-2', 'tunnel', 'e-road'] minutes 15
fewest roads: A -> D via toll-bridge costs 30 minutes with 1 road
stats: {'expanded': 4, 'generated': 8, 'goal_tests': 5, 'pushed': 9, 'stale_skipped': 1, 'improvements': 4, 'max_frontier': 5}
```

## 16. Edge Cases

- Goal is the start: cost 0, no expansion.
- Cheaper route discovered after the goal was generated: improvement, goal still returned with the lower cost.
- Stale entries: skipped and counted; the returned path follows the improved parent, not the stale one (tested).
- Zero-cost edges, zero-cost cycles and self-loops: handled; closed states are never reopened.
- Equal-cost routes: first inserted wins; permuting successor order may change the path but never the cost (metamorphic test).
- Multiple goals: the cheapest goal is returned. Disconnected goals: `FAILURE`. Duplicate parallel records: the cheapest is used.
- Invalid costs (negative, NaN, ±∞, non-numeric, `bool`, complex), malformed records, non-callables and unhashable states raise `ValueError`/`TypeError`.

## 17. Advantages

- Optimal for any finite nonnegative costs, including zero costs.
- Complete on finite spaces, and on infinite spaces with finite branching when every step cost is at least some `ε > 0`.
- Generates states lazily and stops at the first cheapest goal; no heuristic is required.

## 18. Disadvantages and Limitations

- Explores every state cheaper than the goal in all directions; memory grows with the frontier.
- Negative costs are not supported (use [Bellman-Ford](../../../dsa/graph-algorithms/bellman-ford/README.md) on explicit graphs).
- Lazy deletion keeps stale heap entries in memory.
- Floating-point costs inherit rounding; ties between mathematically equal sums can be broken by rounding. Use integers or `Fraction` when exact ties matter.

## 19. When to Use It

Use UCS for least-cost paths in a state space with nonnegative action costs when no informative heuristic is available, or as the correctness baseline for A*.

## 20. When Not to Use It

Use BFS/IDDFS when all costs are equal (cheaper bookkeeping), A* when an admissible heuristic exists, Bellman-Ford with negative costs, and A5 Dijkstra when you need distances to every vertex of an explicit graph.

## 21. Comparison With Related Algorithms

| | **UCS (C1)** | Dijkstra (A5) | BFS (A5) | A* (A5 / C2) |
| --- | --- | --- | --- | --- |
| Interface | `start, is_goal, successors` (implicit, lazy) | `n, edges, source` (explicit graph) | explicit graph | explicit graph / state space + heuristic |
| Stops | first goal popped | after all vertices settled | after all reachable vertices | first goal popped |
| Costs | finite `≥ 0` reals | integers `0 … 10^12` | unit | `≥ 0` |
| Output | one cheapest path to a goal | all distances + parents | all hop counts | one cheapest path |

Both UCS and Dijkstra rely on nonnegative costs and on the same exchange argument; on the same graph their goal costs agree (tested on 200 random graphs against the A5 implementation).

## 22. Interview Questions

1. Why must the goal test happen when a state is removed from the frontier rather than when it is generated?
2. What breaks with a negative edge? Give a three-state counterexample.
3. Why add an insertion counter to heap entries?
4. How are stale entries detected, and why is lazy deletion correct?
5. What is the relationship between UCS, Dijkstra and A*?

## 23. Practice Problems

1. Add a `max_cost` bound that returns `CUTOFF` when the frontier minimum exceeds it.
2. Implement decrease-key with an indexed heap and compare the number of heap operations with lazy deletion.
3. Find all minimum-cost paths in a small graph with ties.
4. Model a 3×3 grid where moving uphill costs 3 and downhill 1; find the cheapest route corner to corner.

## 24. References

- E. W. Dijkstra, "A note on two problems in connexion with graphs," *Numerische Mathematik* 1:269–271, 1959. doi:[10.1007/BF01386390](https://doi.org/10.1007/BF01386390).
- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., Pearson, 2020, §3.4 (uniform-cost search). <https://aima.cs.berkeley.edu/>.
- A. Felner, "Position Paper: Dijkstra's Algorithm versus Uniform Cost Search or a Case Against Dijkstra's Algorithm," *Proceedings of the Fourth Annual Symposium on Combinatorial Search (SoCS)*, 2011.
- Python documentation, [`heapq` — Heap queue algorithm](https://docs.python.org/3/library/heapq.html) (priority-queue implementation notes, including tie-breaking counters).

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). See [CONTRIBUTING.md](../../../CONTRIBUTING.md); distributed under the [MIT License](../../../LICENSE).
