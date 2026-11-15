# C1 Uninformed Search Conventions

This is the shared state-space contract for the four Phase27 canonical implementations: [Depth-Limited Search](../artificial-intelligence/uninformed-search/depth-limited-search/README.md), [IDDFS](../artificial-intelligence/uninformed-search/iterative-deepening-dfs/README.md), [Uniform Cost Search](../artificial-intelligence/uninformed-search/uniform-cost-search/README.md) and [Bidirectional Search](../artificial-intelligence/uninformed-search/bidirectional-search/README.md). The two shared C1 entries, [BFS](../dsa/graph-algorithms/breadth-first-search/README.md) and [DFS](../dsa/graph-algorithms/depth-first-search/README.md), keep their A5 explicit-graph APIs; the mapping is described below.

## State-space model

| Concept | Python contract | C++ contract |
| --- | --- | --- |
| Initial state | any value `start` | `const State& start` |
| Goal | predicate `is_goal(state) -> truthy` (DLS, IDDFS, UCS); one explicit `goal` state (bidirectional) | callable `bool(const State&)`; explicit `goal` |
| Successors | `successors(state)` → iterable of `(action, next_state)` | `std::vector<Step<State, Action>>` |
| Weighted successors (UCS) | `(action, next_state, step_cost)` | `std::vector<WeightedStep<State, Action, Cost>>` |
| Predecessors (bidirectional) | `predecessors(t)` → `(action, s)` for each forward transition `s --action--> t` | same `Step` type |
| Action | any value; never interpreted, only returned (bidirectional compares actions with `==` when confirming predecessor records) | `Action` with `==` where confirmation is needed |
| State identity | `state_key(state)` (default: the state itself); the identity must be hashable | `Hash`/`Equal` template parameters (default `std::hash`/`==`) |

Successor order is the exploration order: depth-first searches try records in the given order, and the UCS/bidirectional frontiers break ties by insertion order. All searches are therefore deterministic for deterministic successor functions.

## Result

Every search returns an immutable `SearchResult` ([`support.py`](../artificial-intelligence/uninformed-search/support.py), [`common.hpp`](../artificial-intelligence/uninformed-search/common.hpp)):

- `status` is `FOUND`, `CUTOFF` (only DLS and IDDFS with `max_depth`) or `FAILURE`. Failure is a structured result, never `None` or an exception.
- `states` includes the initial state first and the goal state last; `actions[i]` labels the transition `states[i] → states[i+1]`, so `len(states) = len(actions) + 1`. Unsuccessful results have empty paths.
- `cost` is the number of actions for unit-cost searches and the summed step cost for UCS; `None`/`null` without a solution. `depth` = `len(actions)`.
- `stats` is an ordered mapping of integer counters. `expanded` counts successor calls that extend the search (DLS boundary checks are counted separately as `boundary_checks`); `generated` counts successor records produced; `goal_tests` counts predicate calls. Algorithm-specific counters are documented in each lesson.

## Duplicate states and cycles

- DLS/IDDFS use **path-local** cycle detection: a successor already on the current path is skipped. No global visited set is used, because a state first reached deep may later be reachable shallowly with remaining depth.
- UCS keeps `best[g]` per state, a closed set, and lazy stale-entry skipping; a closed state is never reopened (safe for nonnegative costs).
- Bidirectional BFS labels each state at most once per direction.
- Duplicate successor records, self-loops and parallel edges are legal inputs.

## Validation

| Input | Error |
| --- | --- |
| Non-callable `is_goal`, `successors`, `predecessors`, `state_key` | `TypeError` |
| Successor output `None`, a string/bytes, a mapping, or not iterable | `TypeError` |
| Record of the wrong width (2 for unweighted, 3 for UCS) | `ValueError` |
| Unhashable state identity | `TypeError` naming `state_key` as the fix |
| Limit / `max_depth` not an `int` (or a `bool`) | `TypeError`; negative → `ValueError` |
| Step cost that is not a real number (`bool`, complex, string, `None`) | `TypeError` |
| Step cost that is negative, NaN or ±∞ | `ValueError` |
| Directed bidirectional search without `predecessors` | `ValueError` |
| Predecessor record without a matching forward transition | `ValueError` during reconstruction |

C++ templates throw `std::invalid_argument` for negative limits, invalid costs and inconsistent predecessors.

## Numerical policy

Only UCS uses costs. Costs are summed as given: `int` and `fractions.Fraction` are exact; `float` follows IEEE-754 rounding (`0.1 + 0.2 > 0.3`). **No tolerance** is applied, because a tolerance would change which path is optimal. Adding a nonnegative float never decreases a value, so the closed-set argument remains valid with floats. The command-line programs accept integer costs `0 … 10^12`, so `long long` sums are exact.

## Explicit-graph command-line programs

Each canonical folder has a Python and a C++ program reading whitespace-separated canonical decimal integers (ASCII, optional `-`, 1–18 digits, no leading zeros, no `-0`): vertices `0 … n−1`, actions are zero-based edge indexes, and the output is one JSON object with the keys of `SearchResult.to_dict()`. Limits: `1 ≤ n ≤ 100000`, `m ≤ 200000`, depth limits `≤ 100000`, costs `≤ 10^12`. Errors print `error: …` to stderr and exit with status 2. Grammars are given in each lesson's section 15.

## Mapping onto the A5 BFS/DFS APIs

A5 `bfs(n, edges, source, directed)` and `dfs(n, edges, directed)` search explicit integer graphs and return per-vertex arrays; they do not take goal predicates or successor callables. A finite state space can use them after numbering its states (without searching, for example by enumerating all `(a, b)` jug contents) and turning each successor record into an edge whose index remembers its action, as in the [shared example](../artificial-intelligence/uninformed-search/examples/shared_bfs_dfs.py). Limitations: the state set must be finite and enumerable up front, the whole graph is built before searching, there is no early goal termination, and A5 caps graphs at 1000 vertices and 10000 edges. Implicit or infinite spaces need the C1 state-space searches instead. A5 semantics were not changed.
