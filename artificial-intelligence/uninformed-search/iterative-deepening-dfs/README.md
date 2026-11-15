# Iterative Deepening DFS (IDDFS)

## 1. Algorithm Name

**Iterative Deepening Depth-First Search (IDDFS, also "iterative deepening search")** — repeated [Depth-Limited Search](../depth-limited-search/README.md) with limits `0, 1, 2, …`. It is not plain [DFS](../../../dsa/graph-algorithms/depth-first-search/README.md), and it is distinct from IDA* (C2), which deepens an `f = g + h` cost bound instead of a depth bound.

## 2. Overview

IDDFS combines depth-first search's small memory with breadth-first search's guarantee of finding a shallowest solution. Each iteration reruns DLS with a limit one larger than before; the first iteration that finds a goal finds it at the minimum possible depth. Repeating shallow work looks wasteful but costs only a constant factor in typical branching search spaces.

## 3. Problem Statement

**Input.** Initial state `s0`, goal predicate, successor function yielding `(action, next_state)` in exploration order, optional `max_depth` (`int ≥ 0` or `None` for unbounded) and optional `state_key`.

**Output.** A `SearchResult` ([C1 contract](../../../docs/uninformed-search-conventions.md)):

| Status | Meaning |
| --- | --- |
| `FOUND` | A path to a goal with the **fewest actions** among all paths from `s0` to any goal; it is simple and `cost = depth`. |
| `FAILURE` | Some DLS iteration returned `FAILURE`: no goal is reachable from `s0`. |
| `CUTOFF` | Only with `max_depth`: the iteration with limit `max_depth` still reported `CUTOFF`, so any solution needs more than `max_depth` actions. |

`stats` sums the DLS counters over all iterations and adds `iterations` and `final_limit`.

## 4. Why Do We Need This Algorithm?

BFS finds shallowest solutions but stores an entire frontier, `O(b^d)` states, which is often the bottleneck. DLS uses `O(bL)` memory but needs the right `L`: too small gives `CUTOFF`, too large returns deep, non-shortest paths and wastes time. IDDFS removes the need to guess `d` while keeping linear memory (Korf, 1985).

## 5. Real-World Applications

- **Puzzle solving with unit-cost moves** (sliding-tile puzzles, Rubik's-cube-style state spaces) where BFS memory is prohibitive; Korf's analysis was motivated by such tree searches.
- **Game-tree search with time limits:** iterative deepening is the standard way to always have a completed shallower search available when time expires (C5 adversarial search builds on this idea).
- **Unknown-depth reachability in large implicit spaces**, such as shortest command sequences in a protocol model.

## 6. Core Intuition

Search a "pond" depth by depth: first check everything 0 steps away, then everything at most 1 step away, then 2, and so on. The first time you see a goal, nothing shallower can exist, because the previous round looked at every shallower possibility. Each round is a cheap depth-first sweep, so memory never holds a whole layer.

## 7. Prerequisites

[Depth-Limited Search](../depth-limited-search/README.md) (its `CUTOFF`/`FAILURE` semantics are essential), [BFS](../../../dsa/graph-algorithms/breadth-first-search/README.md) shortest-hop reasoning, geometric series, and the [C1 state-space model](../README.md#10-state-space-search-model).

## 8. Step-by-Step Working Process

1. Validate callables, `max_depth` (`int ≥ 0` or `None`, never `bool`) and `state_key`.
2. For `limit = 0, 1, 2, …`: run the canonical C1 DLS with that limit and add its counters to the totals.
3. If DLS returns `FOUND`, return its path. If it returns `FAILURE`, return `FAILURE` — larger limits cannot help.
4. If it returns `CUTOFF` and `limit = max_depth`, return `CUTOFF`; otherwise increase the limit by one.

**Correctness (shallowest solution).** Let `d` be the smallest number of actions on any path from `s0` to a goal, so some shortest goal path is simple and has length `d`. For every `L < d`, no path of length `≤ L` reaches a goal, so DLS(`L`) cannot return `FOUND`; it returns `CUTOFF` (the length-`L` prefix of the shortest path is truncated), never `FAILURE`. DLS(`d`) enumerates all simple paths of length `≤ d`, so it finds a goal, and that path has length `≥ d` by minimality and `≤ d` by the limit. **Termination.** With finite branching each DLS terminates. If a goal exists the loop stops at `L = d`. If none exists and the space reachable from `s0` is finite, simple paths have length `< V`, so DLS(`V − 1`) or earlier returns `FAILURE`. On an infinite space with no reachable goal the unbounded loop does not terminate — pass `max_depth`.

## 9. Pseudocode

```text
function IDDFS(s0, is_goal, successors, max_depth = ∞):
    totals ← zero counters
    for L ← 0, 1, 2, …:
        r ← DLS(s0, is_goal, successors, L)     # canonical C1 implementation
        totals ← totals + r.stats; totals.iterations += 1; totals.final_limit ← L
        if r.status = FOUND:   return FOUND(r.path, totals)
        if r.status = FAILURE: return FAILURE(totals)
        if L = max_depth:      return CUTOFF(totals)
```

## 10. Dry Run

CLI graph: `e0: 0→1`, `e1: 1→2`, `e2: 2→4`, `e3: 0→3`, `e4: 3→4`; start 0, goal 4, unbounded.

| Limit | DLS events | Status | expanded / generated / goal tests / boundary checks |
| --- | --- | --- | --- |
| 0 | test 0; boundary check of 0 finds successor 1 | `CUTOFF` | 0 / 2 / 1 / 1 |
| 1 | test 0, expand 0; test 1, boundary check finds 2 (cutoff); test 3 (boundary skipped, cutoff known) | `CUTOFF` | 1 / 3 / 3 / 1 |
| 2 | test 0, expand 0; 1 → 2 (boundary, cutoff); 3 → 4 goal | `FOUND [0,3,4]` | 3 / 5 / 5 / 1 |

Totals: 3 iterations, 4 expansions, 10 generated records, 9 goal tests, 3 boundary checks — the exact statistics printed in §15. The independent BFS distance from 0 to 4 is 2, as returned.

## 11. Time Complexity

Variables: `b` maximum branching factor, `d` depth of the shallowest goal, `L` current limit, `V` reachable states.

- **Tree-shaped space (no repeated states):** depth-`i` nodes are expanded in the iterations `L = i+1, …, d`, i.e. `d − i` times, giving `(d)b + (d−1)b² + … + 1·b^d = O(b^d)` generated nodes. For `b ≥ 2` the total is at most `b/(b−1)` times one full depth-`d` pass asymptotically (at most twice), so repeated work is a constant factor (Korf, 1985).
- **Graph space:** each iteration explores simple paths, not states, so the per-iteration bound is that of DLS: `O(b · P_L)` where `P_L` counts simple paths of length `≤ L`. This can far exceed `V`; BFS with a visited set is `O(V + E)` on explicit graphs.
- **Unsuccessful search** costs `O(Σ_{L ≤ L_final} b · P_L)`; with `max_depth = m` at most `m + 1` iterations run.
- **Best case:** `O(1)` iterations' work when `s0` is a goal.

## 12. Space Complexity

`O(b · d)` auxiliary memory — the space of one DLS run at limit `d` — plus the `O(d)` returned path. Earlier iterations release their stacks. This is the main advantage over BFS's `O(b^d)` frontier. No recursion is used.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) defines `iterative_deepening_search(start, is_goal, successors, *, max_depth=None, state_key=None)`. It loads the **canonical C1 DLS** from [`../depth-limited-search/python/solution.py`](../depth-limited-search/python/solution.py) rather than copying it, so IDDFS cannot drift from DLS semantics. `stats`: `iterations`, `final_limit`, `expanded`, `generated`, `goal_tests`, `boundary_checks`, `cycle_skips` (all summed). `solve_text` implements the CLI. Standard library only.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) includes the DLS canonical source with its `main()` disabled and defines `atlas_search::iterative_deepening_search<State, Action>(start, is_goal, successors, std::optional<long long> max_depth)`. A negative `max_depth` throws `std::invalid_argument`. The macros `ATLAS_UNINFORMED_NO_MAIN` (set by callers that include the file) and `ATLAS_IDDFS_OWNS_MAIN` (internal) ensure exactly one `main`. Tested with `-std=c++17` and `-std=c++20`.

## 15. Input and Output Examples

Grammar: `n m start max_depth g goal_1 … goal_g` then `m` pairs `u v`; `max_depth = -1` means unbounded (explicit graphs are finite, so this always terminates).

```sh
printf '5 5 0 -1 1 4  0 1 1 2 2 4 0 3 3 4\n' | python artificial-intelligence/uninformed-search/iterative-deepening-dfs/python/solution.py
g++ -std=c++20 -Wall -Wextra -pedantic artificial-intelligence/uninformed-search/iterative-deepening-dfs/cpp/solution.cpp -o /tmp/atlas-iddfs
printf '5 5 0 -1 1 4  0 1 1 2 2 4 0 3 3 4\n' | /tmp/atlas-iddfs
```

Both print:

```json
{"status":"FOUND","states":[0,3,4],"actions":[3,4],"cost":2,"depth":2,"stats":{"iterations":3,"final_limit":2,"expanded":4,"generated":10,"goal_tests":9,"boundary_checks":3,"cycle_skips":0}}
```

`printf '3 2 0 1 1 2 0 1 1 2\n'` (goal at depth 2, `max_depth` 1) prints `"status":"CUTOFF"`. Invalid input exits with status 2 and `error: …` on stderr.

[`python/example.py`](python/example.py) shows the growing limits on the infinite `+1`/`*2` integer puzzle (from 1 to 10):

```text
limit=0 status=CUTOFF  expanded=0
limit=1 status=CUTOFF  expanded=1
limit=2 status=CUTOFF  expanded=3
limit=3 status=CUTOFF  expanded=7
limit=4 status=FOUND   expanded=7 route=+1 *2 +1 *2
IDDFS: 1 -> 2 -> 4 -> 5 -> 10 actions ['+1', '*2', '+1', '*2'] depth 4 iterations 5 total expanded 18
```

## 16. Edge Cases

- Goal at depth 0: one iteration. Goal at depth 1: two iterations.
- Several goals at different depths: the shallowest is returned even when DFS order would reach a deeper one first (tested).
- Finite space without a goal: `FAILURE` once a DLS iteration exhausts all simple paths (cycle `0→1→2→0` takes limits 0, 1, 2).
- `max_depth = 0` tests only `s0`; `max_depth` smaller than the solution depth gives `CUTOFF`.
- Cycles, self-loops and duplicate successors are handled by DLS's path-local check.
- Invalid `max_depth` (negative → `ValueError`; float or `bool` → `TypeError`), invalid callables, malformed records and unhashable states are rejected as in DLS.

## 17. Advantages

- Complete for finite branching (when a goal exists) and optimal in the number of actions.
- Linear memory, like DFS.
- Needs no prior knowledge of the solution depth; each iteration is simple and restartable.

## 18. Disadvantages and Limitations

- **Not cost-optimal with unequal step costs** — it minimizes the number of actions only; use [UCS](../uniform-cost-search/README.md) for costs.
- Repeats shallow work; on graphs with many paths to the same states the repetition can be far worse than BFS with a visited set.
- Does not terminate on an infinite space with no reachable goal unless `max_depth` is given.

## 19. When to Use It

Use IDDFS when all actions cost the same, the solution depth is unknown, and memory for a BFS frontier is not available — typically large implicit trees with modest duplication.

## 20. When Not to Use It

For small explicit graphs, BFS with a visited set is simpler and linear-time. For weighted costs use UCS; for a good heuristic use the informed searches in C2 (A*, IDA*).

## 21. Comparison With Related Algorithms

| Property | BFS (A5) | DLS | **IDDFS** | UCS |
| --- | --- | --- | --- | --- |
| Complete (finite `b`) | yes | only if `d ≤ L` | yes | yes if step costs `≥ ε > 0` |
| Optimal | fewest actions | no | fewest actions | least cost |
| Memory | `O(b^d)` | `O(bL)` | `O(bd)` | `O(b^{1+⌊C*/ε⌋})` |
| Repeated work | none | none | shallow levels | none |

## 22. Interview Questions

1. Prove that the first solution IDDFS finds has the minimum number of actions.
2. Why is the overhead of repeating shallow iterations only a constant factor in a tree with `b ≥ 2`?
3. What happens if DLS conflated `CUTOFF` and `FAILURE`?
4. Why is IDDFS not cost-optimal when actions have different costs?
5. How does IDA* generalize this idea?

## 23. Practice Problems

1. Compute the exact number of generated nodes of IDDFS and BFS on a complete binary tree with the goal at depth 10.
2. Add an option that increases the limit by `k > 1` per iteration and analyze what optimality guarantee remains.
3. Solve the 3/4-litre water-jug problem with IDDFS and compare its depth with A5 BFS (see the [shared example](../examples/shared_bfs_dfs.py)).
4. Make IDDFS return all shallowest solutions.

## 24. References

- R. E. Korf, "Depth-first iterative-deepening: An optimal admissible tree search," *Artificial Intelligence* 27(1):97–109, 1985. doi:[10.1016/0004-3702(85)90084-0](https://doi.org/10.1016/0004-3702(85)90084-0).
- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., Pearson, 2020, §3.4. <https://aima.cs.berkeley.edu/>.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). See [CONTRIBUTING.md](../../../CONTRIBUTING.md); distributed under the [MIT License](../../../LICENSE).
