# Phase27 owner request (verbatim record)

Owner statement accompanying the request, received 2026-11-14 Asia/Dhaka:

> Approved pervious work and review done.now follow this properly.

The master prompt follows exactly as supplied.

---

# ALGORITHM ATLAS — PHASE 27

# C1: UNINFORMED SEARCH MASTER IMPLEMENTATION PROMPT

**Track:** C — Artificial Intelligence
**Category:** C1 — Uninformed Search
**Repository:** `algorithm-atlas`
**Owner:** MD.Khalid Hasan
**GitHub:** `khalidhasan7343`
**License:** MIT

---

# 0. MISSION

Begin Phase 27, the first implementation phase of the Artificial Intelligence C Track.

The owner has explicitly authorized starting C Track after declaring A and B complete.

The uploaded catalog records Phase 26 ML Final Audit as `CONDITIONAL PASS` with owner approval previously pending. Preserve that historical audit verdict. Record the owner's current authorization to begin C1 as new dated approval evidence. Do not silently convert `CONDITIONAL PASS` to `PASS` or invent an earlier approval date.

The B8 Dynamic Policy Optimization (DPO) decision remains owner-approved as intentionally blocked. Do not modify or substitute it.

Your mission is to implement and validate the C1 Uninformed Search category.

**Six syllabus entries, but only four new canonical implementations.**

BFS and DFS already have canonical implementations in A5. Reuse those canonical implementations and link to them. Never create duplicate BFS or DFS implementations.

The four new implementations are:

1. Depth-Limited Search.
2. Iterative Deepening DFS (IDDFS).
3. Uniform Cost Search (UCS).
4. Bidirectional Search.

Deliver:

- Correct implementations.
- Explicit input/output contracts.
- Independent mathematical oracles.
- Deterministic tests.
- Edge-case and invalid-input tests.
- Numerical and complexity analysis.
- Exact 25-section algorithm documentation required by `AGENTS.md`.
- Category documentation.
- Catalog and progress integration.
- Full regression verification.
- Review report.
- ZIP review package.
- SHA-256 checksum.
- JSON metadata.

Do not commit, push, tag, release, publish, or begin C2 without explicit owner permission.

---

# 1. AUTHORITATIVE REPOSITORY INSPECTION

Read before changing files:

- `AGENTS.md`
- `catalog.yaml`
- `README.md`
- `pyproject.toml`
- `conftest.py`
- `.gitignore`
- `.github/workflows/ci.yml`
- `docs/progress.md`
- `docs/learning-roadmap.md`
- `docs/algorithm-index.md`
- Existing AI category directories, if any.
- A5 Graph Algorithms category README.
- A5 BFS implementation and tests.
- A5 DFS implementation and tests.
- A5 Dijkstra implementation and tests.
- Existing search utilities.
- Catalog validators.
- Documentation generators.
- Existing review-package conventions.

Record:

- Git branch.
- HEAD commit.
- Working-tree status.
- Existing owner modifications.
- Python version.
- C++ compiler availability.
- C++17/C++20 availability.
- Current test and CI conventions.
- AI implementation language requirements.
- Canonical directory structure.
- Current catalog status.

Preserve unrelated modifications.

Do not use destructive Git operations.

Do not assume AI implementation requirements are identical to ML or DSA requirements. Follow `AGENTS.md` and existing AI-track policy.

Python implementations and Python tests are mandatory. Implement C++ and C++ tests if required by the repository's authoritative AI/algorithm policy. Never create fake C++ placeholders or mark unimplemented C++ as tested.

---

# 2. EXACT C1 CATALOG INVENTORY

Verify the following against the CURRENT `catalog.yaml`.

| # | Syllabus entry                  | Canonical ID              | Canonical ownership |
| - | ------------------------------- | ------------------------- | ------------------- |
| 1 | Breadth-First Search (BFS)      | `breadth-first-search`    | Existing A5         |
| 2 | Depth-First Search (DFS)        | `depth-first-search`      | Existing A5         |
| 3 | Depth-Limited Search            | `depth-limited-search`    | New C1              |
| 4 | Iterative Deepening DFS (IDDFS) | `iterative-deepening-dfs` | New C1              |
| 5 | Uniform Cost Search (UCS)       | `uniform-cost-search`     | New C1              |
| 6 | Bidirectional Search            | `bidirectional-search`    | New C1              |

C1 category path:

`artificial-intelligence/uninformed-search`

Expected new canonical directories:

```text
artificial-intelligence/
└── uninformed-search/
    ├── README.md
    ├── depth-limited-search/
    ├── iterative-deepening-dfs/
    ├── uniform-cost-search/
    └── bidirectional-search/
```

BFS and DFS must continue to resolve to:

- `dsa/graph-algorithms/breadth-first-search`
- `dsa/graph-algorithms/depth-first-search`

Do not create these duplicate directories under C1.

The C1 README must link to the A5 canonical BFS and DFS documentation and implementations.

Do not change canonical IDs or paths without owner approval.

---

# 3. CANONICAL OWNERSHIP AND SHARED ALGORITHM POLICY

The catalog explicitly identifies BFS and DFS as shared canonical topics.

Their canonical implementations are owned by A5.

Therefore:

1. Inspect the actual A5 BFS and DFS APIs.
2. Reuse their implementations where the interfaces are compatible.
3. Reference their canonical source and tests.
4. Explain their role in uninformed state-space search.
5. Provide C1-specific educational examples without duplicating the algorithms.
6. Do not create a second BFS or DFS implementation.
7. Do not modify A5 semantics merely to fit C1 documentation.
8. Do not change A5 canonical ownership.
9. Preserve the catalog's shared-membership relationship.

Explain the distinction between:

- Graph traversal APIs.
- General state-space search APIs.

If the existing A5 implementation does not directly support a generic state-space interface, explain the mapping and its limitations. Do not conceal an interface mismatch by creating an undocumented duplicate canonical algorithm.

UCS must also be distinguished from A5 Dijkstra:

- Dijkstra is the existing graph shortest-path canonical algorithm.
- UCS is the C1 state-space best-first formulation.
- Both rely on nonnegative costs.
- UCS must have a clearly defined state-space successor and goal-test contract.
- Compare the algorithms without duplicating Dijkstra's canonical ownership.

---

# 4. IMPLEMENTATION BATCHES

Use five internal batches.

## Batch 1 — Shared BFS/DFS Integration

- Inspect A5 BFS and DFS.
- Verify their current tests.
- Confirm C1 shared canonical references.
- Write C1 documentation sections for BFS and DFS.
- Add integration examples using the existing canonical implementations.
- Confirm there are no duplicate canonical files.

## Batch 2 — Depth-Limited Search and IDDFS

Implement:

- `depth-limited-search`
- `iterative-deepening-dfs`

Add independent bounded-search oracles.

## Batch 3 — Uniform Cost Search

Implement:

- `uniform-cost-search`

Verify against independent shortest-path oracles.

## Batch 4 — Bidirectional Search

Implement:

- `bidirectional-search`

Verify path reconstruction and optimality.

## Batch 5 — Integration, Regression and Packaging

- Complete category documentation.
- Complete algorithm READMEs.
- Update catalog and progress.
- Run targeted tests.
- Run regression tests.
- Generate review report.
- Generate ZIP, SHA-256 and JSON metadata.

Proceed automatically between ordinary batches after validation. Do not request approval after each batch.

Stop only for a genuine specification conflict, canonical identity change, or other owner-level decision.

---

# 5. COMMON STATE-SPACE SEARCH CONTRACT

Use a consistent documented state-space model for new C1 algorithms.

Define:

- Initial state.
- Goal predicate.
- Successor function.
- Action representation.
- Optional transition cost.
- State identity/key.
- Path representation.
- Search result.
- Search statistics.

A conceptual successor contract may be:

```python
successors(state) -> iterable of (action, next_state)
```

For weighted search:

```python
successors(state) -> iterable of (action, next_state, step_cost)
```

Define a stable state-key policy. Require hashable states or provide an explicit `state_key` function.

Define:

- Whether returned paths include the initial state.
- Whether actions are returned.
- Whether the goal state is included.
- Whether failure returns `None` or a structured result.
- How expansion counts are measured.
- How duplicate states are handled.
- How deterministic tie-breaking works.

Use a consistent result type across new algorithms where practical.

Do not introduce unnecessary shared abstractions that make simple algorithms harder to understand.

Validate callable arguments and malformed successor records.

---

# 6. DEPTH-LIMITED SEARCH

Canonical ID:

`depth-limited-search`

Canonical path:

`artificial-intelligence/uninformed-search/depth-limited-search`

Implement genuine Depth-Limited Search.

## Required behavior

- DFS-style exploration.
- Explicit maximum depth.
- Initial state at depth zero.
- Goal test at every permitted depth.
- Path reconstruction.
- Action reconstruction if supported.
- Correct cutoff handling.
- Correct failure handling.
- Cycle prevention.
- Deterministic successor ordering.

The result must distinguish three outcomes:

1. `FOUND` — a goal was reached.
2. `CUTOFF` — exploration was stopped by the depth limit and a deeper solution may exist.
3. `FAILURE` — no solution was found within the explored finite search space.

Do not conflate cutoff and failure.

## Depth semantics

Document whether the depth limit is inclusive.

Use the conventional interpretation:

- Initial state depth = 0.
- A goal at depth L is allowed when the limit is L.
- A child at depth L+1 is not explored under limit L.

Test this explicitly.

## Cycle handling

Use path-local cycle detection or another proven depth-aware approach.

Do not use a simplistic global visited set that incorrectly prevents revisiting a state through a shallower path.

If a transposition table is used, document and test its remaining-depth semantics.

## Required tests

- Goal at initial state.
- Goal exactly at depth limit.
- Goal one level beyond limit.
- No solution.
- Cutoff versus failure.
- Cyclic graph.
- Multiple paths to same state.
- Duplicate successors.
- Empty successor list.
- Zero depth.
- Negative depth rejected.
- Deterministic path selection.
- Invalid successor records.
- Unhashable state behavior.
- Path reconstruction.

## Independent oracle

For tiny finite graphs, independently enumerate all paths up to the depth bound and compare:

- Whether a solution exists.
- Whether cutoff is appropriate.
- Whether the returned path is valid.
- Whether the path respects the depth limit.

Do not use production DLS as its own oracle.

---

# 7. ITERATIVE DEEPENING DFS

Canonical ID:

`iterative-deepening-dfs`

Canonical path:

`artificial-intelligence/uninformed-search/iterative-deepening-dfs`

Implement genuine IDDFS by repeatedly running depth-limited search with increasing bounds.

## Required behavior

- Start with depth limit zero.
- Increase the limit by one.
- Stop when a goal is found.
- Stop when the search returns definitive failure.
- Respect an optional maximum depth.
- Preserve deterministic successor order.
- Return a valid solution path.
- Report iterations and search statistics if supported.

Do not simply run ordinary DFS once and label it IDDFS.

## Correctness requirements

Explain:

- Completeness under finite branching and appropriate conditions.
- Optimality in solution depth when all actions have equal cost.
- Repeated expansion cost.
- Memory characteristics.
- Why IDDFS is useful when solution depth is unknown.

Do not claim cost optimality when edge costs vary.

## Required tests

- Goal at depth zero.
- Goal at depth one.
- Goal at deeper levels.
- Multiple solutions at different depths.
- Shallowest solution returned.
- No solution in finite search space.
- Maximum-depth cutoff.
- Cyclic graph.
- Repeated states.
- Deterministic output.
- Correct iteration count.
- Correct DLS cutoff propagation.
- Invalid maximum depth.

## Independent oracle

Compare IDDFS against an independently implemented BFS reference on small unweighted graphs.

Verify:

- Reachability.
- Shortest solution depth.
- Path validity.
- Correct behavior when the maximum depth is reached.

Do not use the production DLS implementation as the sole IDDFS oracle.

---

# 8. UNIFORM COST SEARCH

Canonical ID:

`uniform-cost-search`

Canonical path:

`artificial-intelligence/uninformed-search/uniform-cost-search`

Implement genuine Uniform Cost Search for state spaces with nonnegative transition costs.

## Required behavior

- Priority queue.
- Cumulative path cost.
- Best-known cost per state.
- Parent/action reconstruction.
- Goal test when a state is removed from the priority queue with its current best cost.
- Stale queue entry detection.
- Correct handling of improved paths.
- Deterministic tie-breaking.
- Search statistics where supported.

## Critical mathematical requirements

The path cost is:

[
g(n)=\sum\_{e \in path(start,n)} c(e)
]

Expand frontier states in nondecreasing cumulative path cost.

Do not terminate merely because a goal was first generated.

Terminate when a valid minimum-cost goal is removed from the priority queue.

Require all transition costs to be:

- Numeric.
- Finite.
- Nonnegative.

Reject negative, NaN and infinite edge costs.

Support zero-cost edges.

Do not assume strictly positive costs.

Handle multiple paths to the same state.

Handle a later cheaper path correctly.

## Priority queue correctness

Use a deterministic tie-break counter or equivalent mechanism so arbitrary state objects are never compared accidentally.

Ignore stale heap entries.

Maintain correct best-cost and parent information.

Avoid returning a path reconstructed from stale predecessor data.

## Required tests

- Single edge.
- Multiple possible routes.
- Cheapest route discovered after a more expensive route.
- Zero-cost edge.
- Equal-cost routes.
- Multiple goals.
- Goal is initial state.
- Disconnected goal.
- Cycles.
- Duplicate successors.
- Negative cost rejected.
- NaN cost rejected.
- Infinite cost rejected.
- Non-numeric cost rejected.
- Deterministic tie-breaking.
- Correct path cost.
- Correct path reconstruction.
- Stale heap entries.

## Independent oracle

Use an independently implemented Bellman-Ford reference or exhaustive simple-path enumeration on tiny nonnegative graphs.

Compare:

- Reachability.
- Optimal path cost.
- Returned path validity.
- Goal termination.
- Zero-cost behavior.

Do not use the production UCS or A5 Dijkstra as its sole oracle.

Compare UCS with A5 Dijkstra on equivalent graph-shaped state spaces as an additional integration check.

Document their distinct public interfaces.

---

# 9. BIDIRECTIONAL SEARCH

Canonical ID:

`bidirectional-search`

Canonical path:

`artificial-intelligence/uninformed-search/bidirectional-search`

Implement genuine bidirectional BFS for unweighted state spaces.

## Required contract

Define:

- Forward initial state.
- Backward goal state.
- Forward successor function.
- Backward predecessor function.
- State identity.
- Frontier representation.
- Distance maps.
- Parent maps.
- Meeting condition.
- Path reconstruction.

For an undirected graph, the same adjacency function may be used in both directions.

For a directed graph, reverse search must use a genuine predecessor function. Do not assume that forward successors are valid reverse edges.

If predecessor information is unavailable for a directed state space, reject or clearly report that the requested bidirectional search cannot be performed.

Do not silently perform an invalid reverse traversal.

## Required behavior

- Source equals goal.
- Forward frontier.
- Backward frontier.
- Layer-based expansion.
- Frontier intersection detection.
- Correct meeting-state selection.
- Forward path reconstruction.
- Backward path reconstruction.
- Joined path.
- Correct shortest-path result.
- No duplicate meeting state.
- Deterministic behavior.

## Termination correctness

Expand complete BFS layers.

Maintain the best complete meeting path.

Use a mathematically justified termination condition based on the minimum unexpanded forward and backward depths.

Do not stop at an arbitrary first collision if that can produce a non-shortest path.

Document the proof or provide a clear correctness argument for the chosen termination strategy.

## Required tests

- Source equals goal.
- Direct edge.
- Shortest path with several intermediate states.
- Multiple meeting candidates.
- Disconnected components.
- Cyclic graph.
- Directed graph with correct predecessor function.
- Directed graph without predecessor function.
- Unequal frontier sizes.
- Multiple shortest paths.
- Correct path joining.
- Correct path length.
- Deterministic behavior.
- No-solution behavior.

## Independent oracle

Compare against an independently implemented single-source BFS on small unweighted graphs.

Also test tiny graphs using exhaustive path enumeration.

Verify:

- Reachability.
- Shortest path length.
- Path validity.
- Directed-edge orientation.
- Correct reverse reconstruction.

Do not use the production bidirectional implementation as its own oracle.

Do not claim bidirectional BFS is suitable for every search problem. Explain its requirements and limitations.

---

# 10. CROSS-ALGORITHM MATHEMATICAL VERIFICATION

Build independent test references for:

| Algorithm            | Independent verification                                       |
| -------------------- | -------------------------------------------------------------- |
| BFS                  | Existing A5 implementation; independent small-graph BFS oracle |
| DFS                  | Existing A5 implementation; independent reachability checks    |
| Depth-Limited Search | Bounded exhaustive path enumeration                            |
| IDDFS                | Independent BFS shortest-depth reference                       |
| UCS                  | Bellman-Ford and tiny exhaustive path enumeration              |
| Bidirectional Search | Independent BFS and exhaustive path enumeration                |

Verify these mathematical properties:

1. BFS returns a minimum-edge path in unweighted graphs.
2. DFS does not claim shortest-path optimality.
3. DLS never exceeds the depth bound.
4. DLS distinguishes cutoff from failure.
5. IDDFS returns a shallowest-depth solution for unit-cost transitions.
6. UCS returns minimum cumulative cost for nonnegative edges.
7. UCS handles zero-cost edges.
8. Bidirectional BFS returns a shortest path in an unweighted graph when its assumptions hold.
9. Every returned path consists of valid transitions.
10. Every returned action corresponds to the reconstructed transition.

Use exhaustive enumeration on small graphs.

Use deterministic randomized graphs as additional evidence.

Do not rely exclusively on production-to-production comparisons.

---

# 11. PROPERTY-BASED AND METAMORPHIC TESTING

Add deterministic property-based tests where practical.

Examples:

- Adding an unreachable component does not change an existing reachable shortest path.
- Permuting successor order may change tie-selected paths but must not change optimal path cost or depth.
- Adding a more expensive parallel route must not improve UCS cost.
- Adding a nonnegative-cost edge cannot make the optimal UCS cost worse when it creates an additional route.
- Increasing a DLS limit must not invalidate an already found valid path.
- IDDFS solution depth must agree with BFS on unit-cost finite graphs.
- Bidirectional and single-direction BFS must agree on shortest path length.
- Reversing an undirected graph must preserve shortest path length.
- Reconstructed paths must begin at the initial state and end at a goal.

State assumptions for every property.

Do not use an invalid metamorphic relation.

---

# 12. NUMERICAL AND INPUT VALIDATION

Validate:

- Invalid depth limits.
- Negative depth.
- Invalid start or goal state.
- Invalid successor outputs.
- Non-callable functions.
- Invalid state keys.
- Negative transition costs.
- NaN costs.
- Infinite costs.
- Non-numeric costs.
- Malformed predecessor outputs.
- Duplicate edges.
- Self-loops.
- Cycles.
- Empty successor lists.
- Unreachable goals.

Use clear, documented exceptions or structured results.

Avoid silently ignoring invalid input.

Use numerically appropriate cost comparisons and document any floating-point tolerance.

Do not introduce arbitrary tolerances that change the mathematical result.

---

# 13. COMPLEXITY ANALYSIS

Document time and space complexity with clear variables.

For each algorithm, define:

- b = branching factor.
- d = depth of the shallowest solution.
- L = depth limit.
- m = maximum search depth where relevant.
- V = number of reachable states.
- E = number of transitions.
- C\* = optimal solution cost where relevant.
- ε = minimum positive step cost when needed for UCS bounds.

Explain the assumptions behind every complexity claim.

Do not claim that bidirectional search always guarantees a square-root speedup; explain the branching and meeting assumptions.

For UCS, explain that complexity depends on graph size, priority queue behavior, and cost assumptions.

For IDDFS, explain repeated expansion.

For DLS, explain depth-bound behavior.

Avoid quoting a complexity formula without defining its variables.

---

# 14. EDUCATIONAL EXAMPLES

Provide runnable, deterministic examples for all six C1 syllabus entries.

For BFS and DFS:

- Link to the existing A5 canonical implementation.
- Demonstrate the existing API.
- Explain how the example corresponds to uninformed search.
- Do not create duplicate source files.

For DLS:

- Demonstrate a successful search.
- Demonstrate a cutoff.
- Demonstrate a definitive failure.

For IDDFS:

- Demonstrate increasing depth limits.
- Show how the shallowest solution is found.

For UCS:

- Demonstrate a weighted state space.
- Include a case where the cheapest route is not the path with the fewest edges.

For bidirectional search:

- Demonstrate forward and backward frontiers.
- Demonstrate correct path reconstruction.

Do not fabricate outputs.

Examples must run without network access or external datasets.

---

# 15. TEST STRUCTURE

Follow the repository's existing AI testing conventions.

For each new canonical algorithm, provide:

- Python implementation.
- Python tests.
- Runnable example.
- README.
- Invalid-input tests.
- Independent oracle tests.
- Deterministic randomized tests.

If the authoritative AI policy requires C++:

- Implement genuine C++.
- Add C++ tests.
- Follow the repository's C++ standard requirements.
- Verify C++17 and C++20 as required.

Do not leave placeholder implementations.

Do not mark catalog statuses as tested until the actual tests pass.

Do not weaken assertions to force a green suite.

---

# 16. EXACT 25-SECTION README POLICY

Every new canonical algorithm README must follow the exact 25-section structure in `AGENTS.md`.

Do not invent a different heading order.

Include:

- Problem definition.
- Mathematical formulation.
- Assumptions.
- Input/output contract.
- State-space model.
- Data structures.
- Pseudocode.
- Correctness argument.
- Complexity.
- Edge cases.
- Numerical considerations.
- Worked example.
- Python implementation.
- C++ implementation if required.
- Independent oracle.
- Testing methodology.
- Applications.
- Limitations.
- Related algorithms.
- References.

Do not omit mathematical correctness reasoning.

Do not use placeholder sections.

For BFS and DFS, the C1 category documentation must link to the A5 canonical README rather than creating duplicate canonical READMEs.

---

# 17. C1 CATEGORY README

Create or update:

`artificial-intelligence/uninformed-search/README.md`

Include:

1. Introduction to uninformed search.
2. Exact six-entry syllabus inventory.
3. Canonical ownership explanation.
4. BFS canonical link to A5.
5. DFS canonical link to A5.
6. Depth-Limited Search.
7. IDDFS.
8. Uniform Cost Search.
9. Bidirectional Search.
10. State-space search model.
11. Goal testing.
12. Successor generation.
13. Path reconstruction.
14. Frontier management.
15. Cycle handling.
16. Completeness.
17. Optimality.
18. Time complexity.
19. Space complexity.
20. Algorithm comparison.
21. Worked examples.
22. Limitations.
23. Testing and independent oracles.
24. Learning roadmap.
25. Canonical source links.

Clearly distinguish four new canonical implementations from two shared A5 entries.

---

# 18. ALGORITHM COMPARISON TABLE

Include a mathematically accurate comparison:

| Algorithm         | Uses depth limit | Uses costs        | Complete under stated assumptions                                 | Optimal under stated assumptions                         |
| ----------------- | ---------------- | ----------------- | ----------------------------------------------------------------- | -------------------------------------------------------- |
| BFS               | No               | Unit cost         | Yes, finite branching                                             | Yes, unit costs                                          |
| DFS               | No               | No                | Not generally for infinite-depth spaces                           | No                                                       |
| DLS               | Yes              | No                | Only if solution is within limit, under suitable finite branching | No                                                       |
| IDDFS             | Repeated limits  | Unit cost         | Yes, finite branching                                             | Yes, unit costs                                          |
| UCS               | No               | Nonnegative costs | Under suitable positive-cost/finite branching assumptions         | Yes, nonnegative costs with correct goal-pop termination |
| Bidirectional BFS | No               | Unit cost         | Under compatible forward/reverse search assumptions               | Yes, unit costs                                          |

Refine the table to match the actual implementation and precise assumptions.

Do not state unconditional completeness or optimality.

---

# 19. CATALOG INTEGRATION

Update the existing `catalog.yaml` entries for the four new canonical algorithms only after implementation and tests actually exist.

Expected new canonical locations:

- `artificial-intelligence/uninformed-search/depth-limited-search`
- `artificial-intelligence/uninformed-search/iterative-deepening-dfs`
- `artificial-intelligence/uninformed-search/uniform-cost-search`
- `artificial-intelligence/uninformed-search/bidirectional-search`

For BFS and DFS:

- Preserve A5 canonical locations.
- Preserve shared membership.
- Preserve implementation and test statuses.
- Ensure C1 category links resolve to A5.

Update statuses based on actual evidence.

Do not mark unimplemented C++ as tested.

Do not alter unrelated catalog entries.

Do not modify B8 DPO.

---

# 20. PROJECT DOCUMENTATION INTEGRATION

Update where necessary:

- `README.md`
- `docs/progress.md`
- `docs/learning-roadmap.md`
- `docs/algorithm-index.md`
- C1 category README
- Relevant generated documentation
- `catalog.yaml`

Record:

- Phase 27.
- C Track.
- C1 Uninformed Search.
- Six syllabus entries.
- Four new canonical implementations.
- Two shared A5 implementations.
- Completed batches.
- Test status.
- Review status.
- Owner approval pending.

Preserve the existing A and B records.

Do not claim the whole C Track is complete.

Do not mark Phase 27 owner-approved before the owner reviews it.

---

# 21. TARGETED TESTING

Run targeted tests for:

- Existing A5 BFS.
- Existing A5 DFS.
- DLS.
- IDDFS.
- UCS.
- Bidirectional Search.
- Shared state-space contracts.
- Path reconstruction.
- Invalid inputs.
- Independent oracles.
- Deterministic randomized tests.
- Metamorphic properties.
- Complexity-sensitive edge cases.

Verify no duplicate BFS/DFS implementation exists under C1.

Record exact commands and actual pass/fail/skip counts.

---

# 22. FULL REGRESSION TESTING

Run the repository's full supported regression suite.

Include:

- DSA Python.
- DSA C++17.
- DSA C++20.
- ML regression.
- ML classification.
- Ensemble methods.
- Clustering.
- Dimensionality reduction.
- Association rule learning.
- Deep learning.
- Reinforcement learning.
- Graph-based learning.
- Optimization.
- Time series.
- Anomaly detection.
- NLP.
- Existing shared infrastructure.
- Catalog validation.
- Documentation generation.
- CI-equivalent tests.

Use the repository's actual commands and test conventions.

If a full invocation cannot finish, split it into bounded groups and record every command and result.

Never claim an unexecuted test passed.

Do not modify approved A/B algorithms to accommodate C1 unless a genuine regression is demonstrated and the fix is narrowly scoped.

---

# 23. REQUIRED VALIDATION COMMANDS

Run:

```bash
python scripts/validate_catalog.py
python scripts/generate_catalog_docs.py --check
python -m pytest --require-cpp
```

Also run the targeted C1 tests.

If any command is not available, explain why and use the repository's documented equivalent.

Verify C++17 and C++20 if required by the authoritative project policy.

Verify that all generated documentation is current.

Verify that C1 shared links to A5 resolve.

---

# 24. REVIEW REPORT

Create:

`docs/reviews/uninformed-search/UNINFORMED-SEARCH-REVIEW-REPORT.md`

Include:

1. Phase identity.
2. C1 category identity.
3. Six syllabus entries.
4. Four new canonical implementations.
5. Two shared A5 canonical entries.
6. Canonical ownership verification.
7. BFS/DFS reuse evidence.
8. DLS implementation.
9. DLS cutoff/failure verification.
10. IDDFS implementation.
11. IDDFS shortest-depth verification.
12. UCS implementation.
13. UCS nonnegative-cost verification.
14. UCS independent oracle results.
15. Bidirectional implementation.
16. Bidirectional termination proof or correctness argument.
17. Bidirectional path reconstruction.
18. Independent mathematical oracles.
19. Deterministic tests.
20. Invalid-input tests.
21. Property-based/metamorphic tests.
22. Complexity analysis.
23. Documentation compliance.
24. Catalog validation.
25. Regression results.
26. C++17/C++20 results where required.
27. CI-equivalent verification.
28. Files created.
29. Files modified.
30. Known limitations.
31. Unresolved blockers.
32. Exact reproduction commands.
33. Review package paths.
34. Owner approval: pending.

Do not fabricate results.

Clearly distinguish tested, untested, skipped, and blocked items.

---

# 25. REVIEW PACKAGE

Create:

```text
artifacts/review-packages/uninformed-search/
├── algorithm-atlas-uninformed-search-review.zip
├── algorithm-atlas-uninformed-search-review.zip.sha256
└── algorithm-atlas-uninformed-search-review.json
```

Include:

- Four new C1 canonical implementations.
- Four new C1 test suites.
- Four new algorithm READMEs.
- C1 category README.
- Phase 27 review report.
- Existing A5 BFS implementation and tests.
- Existing A5 DFS implementation and tests.
- Relevant A5 category documentation.
- Relevant shared search utilities.
- `AGENTS.md`.
- `catalog.yaml`.
- Root README.
- `pyproject.toml`.
- `conftest.py`.
- Relevant dependency configuration.
- Catalog validator.
- Documentation generator.
- CI configuration.

Do not duplicate canonical source files merely to make the package look self-contained. Include the existing A5 canonical source files once and explain the shared references.

Exclude:

- `.git`.
- Virtual environments.
- Python caches.
- pytest caches.
- Compiled binaries.
- Secrets.
- Temporary files.
- Nested review ZIPs.
- Unnecessary large datasets.

Verify:

1. ZIP opens.
2. CRC passes.
3. Extraction paths are safe.
4. Required files exist.
5. SHA-256 matches.
6. JSON metadata matches.
7. Independent extraction succeeds.
8. Catalog validation runs from extracted source.
9. Documentation validation runs from extracted source.
10. Targeted C1 tests run from extracted source.

Record any verification step that cannot be completed.

---

# 26. PHASE 27 FINAL SUMMARY

Present:

| Field                             | Actual result                    |
| --------------------------------- | -------------------------------- |
| Phase                             | 27                               |
| Track                             | C — Artificial Intelligence      |
| Category                          | C1 — Uninformed Search           |
| Syllabus entries                  | 6                                |
| New canonical implementations     | 4                                |
| Shared A5 canonical entries       | 2                                |
| Duplicate BFS/DFS implementations | 0 expected                       |
| DLS tests                         | Actual result                    |
| IDDFS tests                       | Actual result                    |
| UCS tests                         | Actual result                    |
| Bidirectional tests               | Actual result                    |
| Independent oracles               | Actual result                    |
| Regression tests                  | Actual result                    |
| Catalog validation                | Actual result                    |
| Documentation validation          | Actual result                    |
| C++17/C++20                       | Actual result or N/A with reason |
| Review report                     | Exact path                       |
| Review ZIP                        | Exact path                       |
| SHA-256                           | Exact path                       |
| JSON metadata                     | Exact path                       |
| Owner approval                    | Pending                          |

Provide a per-algorithm status table.

List:

- Completed implementations.
- Incomplete implementations.
- Failed tests.
- Skipped tests.
- Unexecuted checks.
- Known limitations.
- Dependency changes.
- Exact reproduction commands.

Do not claim six new algorithms. There are four new canonical implementations and two shared A5 entries.

---

# 27. NEXT-PHASE APPROVAL GATE

After Phase 27:

STOP.

Do not:

- Start C2 Informed Search.
- Begin another category.
- Commit.
- Push.
- Tag.
- Release.
- Publish.
- Mark Phase 27 owner-approved.

Wait for explicit owner review and approval.

The next planned category is:

**C2 — Informed Search**

Its implementation phase may begin only after the owner approves the C1 review handoff.

---

# 28. EXECUTION ORDER

1. Record the owner's current authorization to start C1.
2. Preserve Phase 26's historical `CONDITIONAL PASS` verdict.
3. Inspect `AGENTS.md` and the current catalog.
4. Verify all six C1 entries.
5. Inspect A5 BFS and DFS canonical implementations.
6. Confirm shared ownership and avoid duplicates.
7. Implement Depth-Limited Search.
8. Implement IDDFS.
9. Implement Uniform Cost Search.
10. Implement Bidirectional Search.
11. Build independent mathematical oracles.
12. Add deterministic, randomized and invalid-input tests.
13. Complete exact 25-section READMEs.
14. Complete C1 category README.
15. Update catalog and progress.
16. Run targeted C1 tests.
17. Run full regression tests.
18. Run catalog and documentation validation.
19. Verify C++ policy.
20. Create review report.
21. Create ZIP, SHA-256 and JSON metadata.
22. Present actual results.
23. STOP for owner approval.

**BEGIN PHASE 27 — C1 UNINFORMED SEARCH.**
