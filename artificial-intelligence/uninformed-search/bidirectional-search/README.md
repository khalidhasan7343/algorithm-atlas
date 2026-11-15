# Bidirectional Search

## 1. Algorithm Name

**Bidirectional Search**, implemented here as **bidirectional breadth-first search** for unit-cost (unweighted) state spaces. One BFS grows forward from the initial state; another grows backward from a single explicit goal state; the search stops when the two can be joined into a provably shortest path. Weighted variants (bidirectional Dijkstra, front-to-end bidirectional A*, the MM algorithm) need different stopping rules and are not implemented here.

## 2. Overview

If a shortest solution has `d` actions and every state has about `b` successors and `b` predecessors, one BFS explores roughly `b^d` states while two searches meeting in the middle explore roughly `2·b^{d/2}`. Realizing that speedup safely requires (1) a genuine way to search backward — predecessors, not successors — and (2) a stopping rule that does not accept a non-shortest first meeting. This implementation expands whole BFS layers, always on the side with the smaller frontier, and accepts the best meeting only when a proven bound shows no shorter path remains.

## 3. Problem Statement

**Input.** `start`, a single `goal` state, `successors(s)` yielding `(action, t)` for each transition `s → t`, and either

- `predecessors(t)` yielding `(action, s)` for each transition `s → t` with the **same forward action** (required for directed state spaces), or
- `undirected=True` (and no predecessor function) when every transition is reversible; backward actions are then recovered from forward successors.

Optional `state_key`. A directed space with neither is rejected with `ValueError`; supplying both is ambiguous and also rejected.

**Output** ([C1 contract](../../../docs/uninformed-search-conventions.md)). `FOUND` with a path from `start` to `goal` having the minimum number of actions, every action a real forward transition (verified), `cost = depth`; or `FAILURE` if the goal is unreachable. `stats` reports `forward_expanded`, `backward_expanded`, `generated`, `forward_depth` and `backward_depth` (depths of the unexpanded frontiers at termination), and `meeting_index` (`states[meeting_index] → states[meeting_index + 1]` is the joining transition; `0` when `start = goal`, `-1` on failure).

## 4. Why Do We Need This Algorithm?

Shortest-path search in unweighted spaces with large branching factors is dominated by the size of the deepest BFS layer. When the goal state is known explicitly and predecessors can be generated, splitting the search depth between two directions can reduce explored states dramatically — for example in word ladders, social-network distance queries or puzzle states with reversible moves.

## 5. Real-World Applications

- **Degrees of separation / unweighted network distance** between two known nodes.
- **Puzzle solving with reversible moves** (sliding puzzles, Rubik's-cube-style spaces) where the goal configuration is known.
- **Word ladders and transformation problems** where moves can be enumerated in both directions.

Pohl (1971) introduced bidirectional heuristic path finding; Holte et al. (2016) analyse when bidirectional searches are guaranteed to meet in the middle.

## 6. Core Intuition

Two people dig a tunnel from opposite sides of a hill. Each digs one full "ring" (BFS layer) at a time, and the one with less work to do digs next. Once their tunnels touch, the shortest tunnel is known — but only after checking that no shorter connection could still be hidden between the two current digging faces.

## 7. Prerequisites

[Breadth-First Search](../../../dsa/graph-algorithms/breadth-first-search/README.md) and its layer invariant, directed versus undirected transitions, hashing for state identity, and the [C1 state-space model](../README.md#10-state-space-search-model).

## 8. Step-by-Step Working Process

1. Validate arguments; if `key(start) = key(goal)`, return the one-state path.
2. Label `start` with forward distance 0 and `goal` with backward distance 0. Frontiers: `F = [start]`, `B = [goal]`; depths `d_f = d_b = 0` (the depth of the unexpanded frontier on each side).
3. Before each layer, stop if a best meeting of length `best ≤ d_f + d_b + 1` is known.
4. Choose the side: smaller frontier; on equal sizes the shallower side; then forward.
5. Expand the **whole** chosen frontier in order. For each generated neighbor: label it (distance `d + 1`, parent link) if unlabeled on this side; if it is labeled by the other side, offer the candidate length `d_side + 1 + d_other(neighbor)` together with its joining transition. Keep the strictly smallest candidate (first found wins ties).
6. Replace the frontier with the newly labeled states and increase that side's depth. Repeat from step 3; stop with `FAILURE` if either frontier becomes empty without a candidate.
7. Rebuild the forward half from forward parents, add the joining transition, and follow backward parents to the goal. Each backward-discovered hop is confirmed against `successors` (exact action in directed mode, first matching transition in undirected mode); an inconsistent predecessor function raises `ValueError`.

**Correctness of the stopping rule.** Let `d_f, d_b` be the current unexpanded depths. BFS layering guarantees every state with true forward distance `≤ d_f` is labeled forward, and every state with true backward distance `≤ d_b` is labeled backward. *Claim:* every `start→goal` path `P` of length `ℓ ≤ d_f + d_b` has already produced a candidate `≤ ℓ`. Pick position `j = min(d_f, ℓ)` on `P`; its state `p_j` has forward distance `≤ j ≤ d_f` and backward distance `≤ ℓ − j ≤ d_b`, so it is labeled by both sides. At the moment the second of those labels was created, the generating side checked the opposite label and offered `dist_f(p_j) + dist_b(p_j) ≤ ℓ`. (When `p_j` is `start` or `goal`, its initial label plays the role of one side.) Therefore, if `best ≤ d_f + d_b + 1`, any strictly shorter path would have length `≤ d_f + d_b` and would already have produced a candidate smaller than `best` — a contradiction; `best` is optimal. If a frontier empties, that side has labeled its whole reachable set and the same argument applies to every path. Because all candidates found while expanding a layer have length exactly `d_f + d_b + 1`, the first meeting found in that layer is already optimal; the pitfall of accepting a non-shortest "first meeting" arises in node-alternating variants that only test the other side's *expanded* states, and the test suite contains a concrete counterexample to such a variant.

## 9. Pseudocode

```text
function BIDIRECTIONAL_BFS(start, goal, successors, predecessors):
    if start = goal: return FOUND([start])
    dist_f ← {start: 0}; dist_b ← {goal: 0}; F ← [start]; B ← [goal]
    d_f ← 0; d_b ← 0; best ← none
    while F ≠ [] and B ≠ []:
        if best ≠ none and best.length ≤ d_f + d_b + 1: break
        if (|F|, d_f) ≤ (|B|, d_b):                       # forward layer
            L ← []
            for u in F: for (a, v) in successors(u):
                if v ∉ dist_f: dist_f[v] ← d_f + 1; parent_f[v] ← (u, a); L.append(v)
                if v ∈ dist_b: offer(d_f + 1 + dist_b[v], u → v via a)
            F ← L; d_f ← d_f + 1
        else:                                              # backward layer
            L ← []
            for y in B: for (a, x) in predecessors(y):      # x --a--> y
                if x ∉ dist_b: dist_b[x] ← d_b + 1; parent_b[x] ← (y, a); L.append(x)
                if x ∈ dist_f: offer(dist_f[x] + 1 + d_b, x → y via a)
            B ← L; d_b ← d_b + 1
    if best = none: return FAILURE
    return forward chain to best.a + best edge + backward chain from best.b to goal
```

## 10. Dry Run

Undirected CLI graph: `e0: 0–1`, `e1: 1–2`, `e2: 2–5`, `e3: 0–3`, `e4: 3–4`, `e5: 4–5`; start 0, goal 5. Two shortest paths of length 3 exist.

| Step | (size F, d_f) vs (size B, d_b) | Side expanded | New labels / candidates | Check |
| --- | --- | --- | --- | --- |
| 1 | (1,0) vs (1,0) | forward: 0 | `1, 3` at forward depth 1 | none yet |
| 2 | (2,1) vs (1,0) | backward: 5 | `2, 4` at backward depth 1 | none yet |
| 3 | (2,1) vs (2,1) | forward: 1, 3 | `2` (via e1) is backward-labeled → candidate `1+1+1 = 3`; `4` gives 3 again (not better) | `3 ≤ 2+1+1` → stop |

Reconstruction: forward chain `0 –e0→ 1`, joining edge `1 –e1→ 2`, backward chain `2 → 5` whose forward action is confirmed as `e2`. Result `[0, 1, 2, 5]`, actions `[0, 1, 2]`, 3 forward and 1 backward expansions, 8 generated records, `meeting_index = 1` — exactly the output in §15.

## 11. Time Complexity

Variables: `V` and `E` reachable states and transitions (counting both directions), `d` the shortest solution length, `b_f`, `b_b` forward and backward branching factors.

- **Explicit-graph worst case:** each state is expanded at most once per side and each transition generated at most once per side, so `O(V + E)` with `O(1)` expected hashing; reconstruction adds `O(d · b)` successor calls to confirm the backward half.
- **Idealized tree model:** with `b_f = b_b = b` and both searches reaching depth about `d/2`, `O(b^{d/2})` states are generated per side versus `O(b^d)` for one-directional BFS.
- **No unconditional speedup:** the square-root effect needs comparable branching in both directions, a single explicit goal, and frontiers that actually meet near the middle. If predecessors branch much more than successors (or many goal states exist), the backward side can be the expensive one; the smaller-frontier rule mitigates but cannot remove that. In the worst case the bound is still `O(V + E)`.

## 12. Space Complexity

`O(V)` for distance maps, parent links and the state table, plus `O(max frontier)`; in the tree model `O(b^{d/2})`. Unlike IDDFS, bidirectional BFS must keep at least one whole frontier to test intersections, so its memory is exponential in `d/2`. No recursion is used. The output path is `O(d)`.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) defines `bidirectional_search(start, goal, successors, predecessors=None, *, undirected=False, state_key=None)`. Distances, parents and frontiers are dictionaries and lists keyed by `state_key`. Backward actions that are unknown in undirected mode use a private sentinel, so user actions may legitimately be `None`. `_forward_action` confirms every backward-half hop against `successors`. `solve_text` builds successor and reverse (predecessor) tables for the CLI. Standard library only.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) provides `atlas_search::bidirectional_search<State, Action>(start, goal, successors, predecessors)` for directed spaces and `bidirectional_search_undirected<State, Action>(start, goal, successors)` — the absence of a predecessor function is therefore a compile-time choice, not a silent fallback. Both forward to one internal implementation with dense state ids, `std::optional<Action>` for unknown backward actions, and identical tie-breaking and statistics. An inconsistent predecessor function throws `std::invalid_argument`. Custom `Hash`/`Equal` template arguments support composite states (tested with grid cells). Tested under C++17 and C++20.

## 15. Input and Output Examples

Grammar: `n m start goal directed` then `m` pairs `u v`; `directed = 1` builds genuine predecessors from reversed edges, `directed = 0` treats every edge as two-way.

```sh
printf '6 6 0 5 0  0 1 1 2 2 5 0 3 3 4 4 5\n' | python artificial-intelligence/uninformed-search/bidirectional-search/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic artificial-intelligence/uninformed-search/bidirectional-search/cpp/solution.cpp -o /tmp/atlas-bidirectional
printf '6 6 0 5 0  0 1 1 2 2 5 0 3 3 4 4 5\n' | /tmp/atlas-bidirectional
```

Both print:

```json
{"status":"FOUND","states":[0,1,2,5],"actions":[0,1,2],"cost":3,"depth":3,"stats":{"forward_expanded":3,"backward_expanded":1,"generated":8,"forward_depth":2,"backward_depth":1,"meeting_index":1}}
```

With `directed = 1`, input `3 2 0 2 1  0 1 2 1` (edges `0→1`, `2→1`) prints `"status":"FAILURE"`: state 1 touches both 0 and 2, but 2 is not reachable from 0.

[`python/example.py`](python/example.py) logs both frontiers on a directed word ladder:

```text
expansion order: forward:cold, backward:warm, forward:cord, forward:bold, backward:ward, backward:ware
path: cold -> cord -> card -> ward -> warm depth 4
meeting edge: card -> ward
stats: {'forward_expanded': 3, 'backward_expanded': 3, 'generated': 9, 'forward_depth': 2, 'backward_depth': 2, 'meeting_index': 2}
```

## 16. Edge Cases

- `start = goal`: one-state path, no expansion.
- Direct edge, long chains (meet in the middle: a 9-state chain ends with both depths 4), several meeting candidates, several shortest paths (deterministic choice).
- Disconnected components and unreachable goals: `FAILURE`.
- Cycles, self-loops and duplicate edges: each state is labeled once per side.
- **Directed spaces without predecessors** are rejected; treating successors as reverse edges would find false paths (tested on `0→1←2`).
- Inconsistent predecessor functions and false `undirected=True` claims are detected during reconstruction.
- Unequal frontier sizes: a start that fans out to six states and a goal with a single predecessor chain is solved with 1 forward and 3 backward expansions.
- Malformed records, non-callables, a non-`bool` `undirected`, and unhashable states raise `TypeError`/`ValueError`.

## 17. Advantages

- Optimal (fewest actions) and complete on finite spaces under the stated assumptions.
- Can explore far fewer states than one-directional BFS when both directions branch similarly.
- The meeting statistic makes the join point inspectable.

## 18. Disadvantages and Limitations

- Requires a single explicit goal state and genuine predecessor generation; goal *predicates* such as "any state with b = 2" do not fit directly.
- Unit costs only; weighted bidirectional search needs a different termination rule.
- Memory is dominated by stored frontiers and labels, like BFS.
- The square-root speedup is an idealization, not a guarantee.

## 19. When to Use It

Use it for shortest unweighted paths between two known states when predecessors are available and both directions branch comparably — word ladders, social graphs, reversible puzzles.

## 20. When Not to Use It

Use BFS or IDDFS when only a goal predicate is available or predecessors cannot be generated; use UCS or weighted bidirectional methods for unequal costs; use A* when a good heuristic exists.

## 21. Comparison With Related Algorithms

| | BFS (A5) | IDDFS | **Bidirectional BFS** | UCS |
| --- | --- | --- | --- | --- |
| Needs | successors | successors | successors + predecessors, one goal state | successors with costs |
| Optimal | fewest actions | fewest actions | fewest actions | least cost |
| Tree-model time | `O(b^d)` | `O(b^d)` | `O(b^{d/2})` when branching is symmetric | `O(b^{1+⌊C*/ε⌋})` |
| Memory | `O(b^d)` | `O(bd)` | `O(b^{d/2})` | `O(b^{1+⌊C*/ε⌋})` |

## 22. Interview Questions

1. Why can a directed state space not be searched backward with its successor function?
2. Prove that accepting the best meeting once `best ≤ d_f + d_b + 1` returns a shortest path.
3. Give an example where stopping at the first meeting is wrong for a node-alternating variant.
4. Why does expanding the smaller frontier usually help, and when does it not?
5. What changes when step costs differ?

## 23. Practice Problems

1. Turn the water-jug puzzle into an explicit goal state and write its predecessor function.
2. Measure `forward_expanded + backward_expanded` against A5 BFS on random graphs with average degree 3 and explain the ratio.
3. Extend the implementation to multiple goal states by adding a virtual super-goal.
4. Implement bidirectional Dijkstra and its stopping condition `top_f + top_b ≥ best`.

## 24. References

- I. Pohl, "Bi-directional search," in B. Meltzer and D. Michie (eds.), *Machine Intelligence 6*, Edinburgh University Press, 1971, pp. 127–140.
- R. C. Holte, A. Felner, G. Sharon and N. R. Sturtevant, "Bidirectional Search That Is Guaranteed to Meet in the Middle," *Proceedings of the AAAI Conference on Artificial Intelligence* 30(1), 2016.
- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., Pearson, 2020, §3.4 (bidirectional search). <https://aima.cs.berkeley.edu/>.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). See [CONTRIBUTING.md](../../../CONTRIBUTING.md); distributed under the [MIT License](../../../LICENSE).
