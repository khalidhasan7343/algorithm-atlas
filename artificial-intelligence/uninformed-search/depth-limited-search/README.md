# Depth-Limited Search

## 1. Algorithm Name

**Depth-Limited Search (DLS)** — depth-first search of a state space that never extends a path beyond a fixed number of actions `L`. It is distinct from plain [Depth-First Search](../../../dsa/graph-algorithms/depth-first-search/README.md) (no bound, graph traversal API) and from [Iterative Deepening DFS](../iterative-deepening-dfs/README.md), which repeats DLS with growing limits.

## 2. Overview

DLS explores one path as deeply as allowed, backtracks, and tries the next successor. The limit turns an unbounded depth-first search into a procedure that always terminates on a finitely branching space, at the price of possibly missing deeper solutions. This implementation reports three distinct outcomes — `FOUND`, `CUTOFF` and `FAILURE` — so a caller can tell "no solution within the limit, but a deeper one may exist" from "no solution at all".

## 3. Problem Statement

**Input.** An initial state `s0`, a goal predicate `is_goal(state)`, a successor function `successors(state)` yielding `(action, next_state)` records in exploration order, an integer limit `L ≥ 0`, and optionally `state_key(state)` returning a hashable identity (default: the state itself).

**Output.** A `SearchResult` from the shared [C1 contract](../../../docs/uninformed-search-conventions.md):

| Status | Meaning |
| --- | --- |
| `FOUND` | `states = (s0, …, g)` with `is_goal(g)` and `len(actions) = len(states) − 1 ≤ L`; `actions[i]` leads from `states[i]` to `states[i+1]`; `cost` = number of actions. |
| `CUTOFF` | No goal on any acyclic path of length `≤ L`, and at least one acyclic path was truncated at depth `L` (a state at depth `L` has a successor not already on its path). A deeper solution may exist. |
| `FAILURE` | No goal on any acyclic path of length `≤ L`, and no acyclic path reaches depth `L + 1`: the reachable space was exhausted, so **no goal is reachable at all**. |

**Depth semantics (inclusive).** `s0` has depth 0. Every state at depth `0..L` is goal-tested. A child at depth `L + 1` is never goal-tested or explored; its existence is only used to decide `CUTOFF` versus `FAILURE`.

## 4. Why Do We Need This Algorithm?

Unbounded DFS can descend forever in an infinite space (for example, integers under `+1`) or loop in a cyclic one. Breadth-first search avoids that but stores whole layers, `O(b^d)` states. DLS keeps DFS's linear memory while guaranteeing termination whenever branching is finite. It is also the building block of IDDFS and of bounded planning ("is there a plan of at most `L` steps?").

## 5. Real-World Applications

- **Bounded planning and puzzle solving:** checking whether a puzzle position can be solved within `L` moves, as in textbook state-space formulations (Russell & Norvig, ch. 3).
- **Iterative deepening:** IDDFS and IDA* both run depth- or cost-limited depth-first passes.
- **Bounded model checking style questions:** "can a bad state be reached in at most `L` transitions?" — the bound keeps the exploration finite.

## 6. Core Intuition

Treat the limit as a fuel budget: each action spends one unit. Explore depth-first; when the budget is exhausted at depth `L`, stop descending but remember whether you *could* have continued. If at the end you never had to stop for lack of fuel, the space below `s0` was explored completely and a missing goal really is unreachable.

## 7. Prerequisites

[Depth-First Search](../../../dsa/graph-algorithms/depth-first-search/README.md) and stacks, the [C1 state-space model](../README.md#10-state-space-search-model), hashing for state identity, and asymptotic notation from the [complexity cheat sheet](../../../docs/complexity-cheatsheet.md).

## 8. Step-by-Step Working Process

1. Validate callables, the limit (an `int ≥ 0`, not `bool`) and the start key.
2. Goal-test `s0`; if it is a goal, return `FOUND` with the one-state path.
3. Keep an explicit stack of frames `(state, validated successor list, next index)` plus the current path and a set `on_path` of path keys.
4. Take the next successor of the top frame. If its key is already on the path, skip it (path-local cycle check). Otherwise push it on the path and goal-test it.
5. If the child's depth is below `L`, expand it (new frame). If its depth equals `L`, do not push a frame; instead, if no cutoff is known yet, generate its successors once and set `cutoff` when any of them is not on the path. Then remove the child from the path.
6. When a frame has no successors left, pop it and its path entry.
7. When the stack empties, return `CUTOFF` if a cutoff was recorded, otherwise `FAILURE`.

**Correctness invariant.** The stack always represents one simple path from `s0`, and states are tried in successor order; therefore DLS enumerates exactly the simple paths of length `≤ L` in depth-first preorder and returns the first one ending in a goal. *Cycle handling:* a global visited set would be wrong — a state first met at depth `L` could later be reachable at depth 1 with budget to spare (tested). Path-local checks only reject paths that repeat a state; any goal reachable within `L` actions is reachable by a simple path within `L` actions (delete the cycle), so nothing is lost. *Failure soundness:* if a goal is reachable, take a shortest simple path of length `k`. If `k ≤ L`, the enumeration finds a goal. If `k > L`, its prefix of length `L` is a simple path whose last state has the next path state as a successor not on that prefix, so the boundary check records `CUTOFF`. Hence `FAILURE` implies no goal is reachable.

## 9. Pseudocode

```text
function DLS(s0, is_goal, successors, L):
    if is_goal(s0): return FOUND([s0], [])
    path ← [s0]; actions ← []; on_path ← {key(s0)}; cutoff ← false
    stack ← []
    ENTER(s0, depth 0)
    while stack not empty:
        frame ← top(stack)
        if frame has no untried successor:
            pop stack; remove frame.state from path and on_path; continue
        (a, c) ← next successor of frame
        if key(c) ∈ on_path: continue                    # path-local cycle
        d ← |stack|                                      # depth of c
        append c to path, a to actions, key(c) to on_path
        if is_goal(c): return FOUND(path, actions)
        ENTER(c, d)
        if d = L: remove c from path, actions, on_path   # never pushed

procedure ENTER(s, d):
    if d < L: push frame(s, successors(s))
    else if not cutoff:
        cutoff ← any successor of s whose key ∉ on_path
    return CUTOFF if cutoff else FAILURE   # after the loop ends
```

## 10. Dry Run

CLI graph (edge index = action): `e0: 0→1`, `e1: 1→2`, `e2: 2→4`, `e3: 0→3`, `e4: 3→4`; start 0, goal 4, `L = 2`.

| Step | Event | Path | Notes |
| --- | --- | --- | --- |
| 1 | goal-test 0 → no; expand 0 | `0` | successors `[e0→1, e3→3]`; expanded 1 |
| 2 | child 1 (depth 1): test no; expand | `0 1` | successors `[e1→2]`; expanded 2 |
| 3 | child 2 (depth 2 = L): test no | `0 1 2` | boundary check: successor 4 not on path → `cutoff = true` |
| 4 | undo 2; frame 1 exhausted → pop | `0` | |
| 5 | child 3 (depth 1): test no; expand | `0 3` | successors `[e4→4]`; expanded 3 |
| 6 | child 4 (depth 2): goal | `0 3 4` | return `FOUND`, actions `[3, 4]` |

Statistics: 3 expansions, 5 generated records, 5 goal tests, 1 boundary check — exactly what the program prints in §15. With `L = 1` the same input ends with `CUTOFF`; the goal at depth 2 is never tested.

## 11. Time Complexity

Let `b` be the maximum branching factor (successor records per state), `L` the limit, and `P_L` the number of simple paths of length `≤ L` starting at `s0`.

- Each simple path of length `< L` is expanded once (cost `O(b)` to generate and validate its successors, `O(1)` expected per hash lookup); paths of length `L` cost at most one boundary generation, and only until the first cutoff is known.
- **Worst case:** `O(b · P_L)` time. In a tree-shaped space `P_L ≤ 1 + b + … + b^L`, so time is `O(b^{L+1})` generated records and `O(b^L)` expansions. In a graph, repeated states are re-explored along different paths; `P_L` can exceed the number of states `V` (it is still finite).
- **Best case:** `O(1)` when `s0` is a goal.
- The goal predicate and successor function are assumed `O(1)` and `O(b)`; otherwise multiply by their costs.

## 12. Space Complexity

Auxiliary memory is `O(b · L)`: at most `L` frames, each holding its validated successor list, plus the `O(L)` path, action list and `on_path` set. No visited set over all states is kept — this is DLS's main advantage over BFS. The implementation uses an explicit stack, so there is no recursion and no Python recursion-limit failure (tested with a 5000-deep chain). The returned path is `O(L)`.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `depth_limited_search(start, is_goal, successors, limit, *, state_key=None)`. It loads the shared [`support.py`](../support.py) for the immutable `SearchResult`, `FOUND/CUTOFF/FAILURE`, record and key validation; the search loop itself is entirely in the canonical file. Successor records are materialized and validated per expansion so malformed records raise `ValueError` and non-iterables raise `TypeError` immediately. `stats` reports `expanded`, `generated`, `goal_tests`, `boundary_checks`, `cycle_skips` and `max_depth_reached`. `solve_text` implements the explicit-graph CLI. Standard library only.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) provides the template `atlas_search::depth_limited_search<State, Action>(start, is_goal, successors, limit)` where `successors` returns `std::vector<Step<State, Action>>`; optional `Hash`/`Equal` template arguments define state identity. The shared [`common.hpp`](../common.hpp) holds the result type, ordered statistics, token parser and JSON writer. A negative limit throws `std::invalid_argument`. Frames copy each step before the stack can reallocate. Define `ATLAS_UNINFORMED_NO_MAIN` to include the source in another program (IDDFS does exactly this). Build with `g++ -std=c++17 -Wall -Wextra -pedantic` (C++20 is also tested).

## 15. Input and Output Examples

Token grammar for both programs (actions are zero-based edge indexes): `n m start limit g goal_1 … goal_g` followed by `m` pairs `u v`. Limits: `1 ≤ n ≤ 100000`, `m ≤ 200000`, `0 ≤ limit ≤ 100000`; tokens are canonical decimal integers.

From the repository root:

```sh
printf '5 5 0 2 1 4  0 1 1 2 2 4 0 3 3 4\n' | python artificial-intelligence/uninformed-search/depth-limited-search/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic artificial-intelligence/uninformed-search/depth-limited-search/cpp/solution.cpp -o /tmp/atlas-dls
printf '5 5 0 2 1 4  0 1 1 2 2 4 0 3 3 4\n' | /tmp/atlas-dls
```

Both print:

```json
{"status":"FOUND","states":[0,3,4],"actions":[3,4],"cost":2,"depth":2,"stats":{"expanded":3,"generated":5,"goal_tests":5,"boundary_checks":1,"cycle_skips":0,"max_depth_reached":2}}
```

Invalid input (for example a negative limit `1 0 0 -1 0`) prints `error: …` to stderr and exits with status 2.

The runnable [`python/example.py`](python/example.py) shows all three outcomes on a road map:

```text
goal=Station  limit=2 status=FOUND   route=Home -> Market -> Station actions=['high-st', 'station-rd'] expanded=3
goal=Airport  limit=2 status=CUTOFF  route=- actions=[] expanded=3
goal=Island   limit=10 status=FAILURE route=- actions=[] expanded=8
```

## 16. Edge Cases

- **Goal at the start:** `FOUND` with depth 0 for every limit, including 0.
- **`L = 0`:** only `s0` is tested; `CUTOFF` if it has a successor other than itself, `FAILURE` if it has none or only a self-loop.
- **Goal exactly at `L`** is found; **goal at `L + 1`** gives `CUTOFF` and is never goal-tested (tested by recording every goal-test call).
- **Cycles, self-loops, duplicate successors, several paths to one state:** handled by the path-local check; returned paths never repeat a state.
- **Invalid input:** negative limit → `ValueError`; non-`int` or `bool` limit → `TypeError`; non-callable arguments → `TypeError`; successor output that is `None`, a string, a mapping or not iterable → `TypeError`; records not of width 2 → `ValueError`; unhashable states without a suitable `state_key` → `TypeError` naming the fix.
- **Results are immutable** (`SearchResult` attributes and the `stats` mapping).

## 17. Advantages

- Always terminates for finite branching and gives a sound three-way verdict.
- Linear memory `O(bL)` instead of BFS's frontier of `O(b^d)` states.
- Simple and deterministic: the first solution in successor order is returned.

## 18. Disadvantages and Limitations

- **Not complete** when the shallowest solution is deeper than `L` (it reports `CUTOFF`).
- **Not optimal:** it returns the first solution in depth-first order. With edges `0→1, 1→2, 2→3, 0→3`, goal 3 and `L = 3`, DLS returns the 3-action path `0→1→2→3` although `0→3` takes one action (tested).
- Without a global visited set, states reachable by many paths are re-explored; on dense graphs the number of simple paths grows exponentially in `L`.
- The boundary check calls `successors` on some depth-`L` states purely to classify the outcome.

## 19. When to Use It

Use DLS when a natural bound on solution length is known (a plan of at most `L` moves), when memory is tight, or as the inner loop of IDDFS.

## 20. When Not to Use It

Use [BFS](../../../dsa/graph-algorithms/breadth-first-search/README.md) or [IDDFS](../iterative-deepening-dfs/README.md) when you need the shortest solution and do not know its depth; use [Uniform Cost Search](../uniform-cost-search/README.md) for unequal step costs; use a visited-set graph search when the state space is small and highly cyclic.

## 21. Comparison With Related Algorithms

| Algorithm | Bound | Complete (finite `b`) | Optimal | Memory |
| --- | --- | --- | --- | --- |
| DFS (A5) | none | only on finite graphs with a visited set | no | `O(V)` visited |
| **DLS** | fixed `L` | only if a solution has depth `≤ L` | no | `O(bL)` |
| IDDFS | `0, 1, 2, …` | yes | yes for unit costs | `O(bd)` |
| BFS (A5) | none | yes | yes for unit costs | `O(b^d)` |

## 22. Interview Questions

1. Why must DLS distinguish `CUTOFF` from `FAILURE`, and how does IDDFS use the difference?
2. Construct a graph where a global visited set makes DLS miss a solution within the limit.
3. Is the depth limit inclusive here? What exactly happens to a child at depth `L + 1`?
4. Why does `FAILURE` imply that no goal is reachable at all?
5. What is the space complexity, and why is it independent of the number of states?

## 23. Practice Problems

1. Modify the example road map so that `Airport` becomes `FOUND` at `L = 2` without changing the search code.
2. Count how many simple paths of length `≤ 3` start at a corner of a 3×3 grid, and compare with the `expanded` statistic.
3. Add an optional transposition table that stores, for each state, the largest remaining depth with which it was searched; prove it preserves correctness.
4. Use DLS to decide whether a sliding 2×2 puzzle position is solvable within 6 moves.

## 24. References

- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., Pearson, 2020, §3.4 (depth-limited and iterative deepening search). Book site: <https://aima.cs.berkeley.edu/>.
- R. E. Korf, "Depth-first iterative-deepening: An optimal admissible tree search," *Artificial Intelligence* 27(1):97–109, 1985. doi:[10.1016/0004-3702(85)90084-0](https://doi.org/10.1016/0004-3702(85)90084-0).

The three-outcome contract, inclusive depth convention and boundary-check refinement are this repository's documented contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). See [CONTRIBUTING.md](../../../CONTRIBUTING.md); distributed under the [MIT License](../../../LICENSE).
