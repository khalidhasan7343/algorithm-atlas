# Monte Carlo Tree Search (MCTS)

## 1. Algorithm Name

Monte Carlo Tree Search with UCT; deterministic single-agent terminal planning only.

## 2. Overview

Build a partial search tree by choosing promising visited branches and simulating unexpanded futures. Each simulation contributes an outcome to every ancestor, so exploration and exploitation share an explicit visit budget.

## 3. Problem Statement

Given a pure deterministic planning model and initial immutable state, return a legal action plus an inspectable tree. Model methods: terminal(state)→bool, legal_actions(state)→unique integer list, transition(state,a)→next state, outcome(terminal_state)→finite scalar. This is an undiscounted single-agent finite-horizon MDP with zero intermediate rewards and terminal payoff. No adversarial player or chance-node semantics are implied.

## 4. Why Do We Need This Algorithm?

Exact enumeration can be expensive while a bounded rollout budget can prioritize promising branches. UCT combines observed mean outcome and uncertainty rather than exhaustively expanding the entire tree.

## 5. Real-World Applications

Deterministic single-agent puzzles or finite planning trees with a cheap pure simulator and terminal outcome. The included binary depth3 tree rewards only path111. No two-player game or stochastic-transition support is claimed.

## 6. Core Intuition

For child i: UCT_i=Q_i+c sqrt(log N_parent/N_i), where Q_i=value_sum_i/N_i. An unvisited child has score+∞. Outcomes keep the same single-agent perspective at all ancestors. Final selection uses largest child visits, then mean payoff, then smallest action index.

## 7. Prerequisites

Finite planning, sample means, logarithms and tree structures. Compare [Q-Learning](../q-learning/README.md): MCTS has a simulator and plans at decision time instead of learning a reusable table from a behavior policy.

## 8. Step-by-Step Working Process

1. Make a root with sorted untried legal actions.
2. Select UCT children while the current node is fully expanded.
3. Randomly expand one untried legal action.
4. Simulate random legal actions until terminal within remaining depth.
5. Add terminal payoff and one visit to the expanded/selected node and every ancestor.
6. Repeat the fixed iteration budget, then return the robust child.

Every successful iteration increments root visits exactly once and creates at most one new node. Backpropagation is a sample-mean accounting invariant; finite search is not an optimality certificate.

## 9. Pseudocode

```text
root = node(initial_state, untried=legal_actions)
if terminal(root): return no_action, root
repeat iterations:
    node = root
    while fully_expanded(node) and node has children:
        node = child with greatest UCT, smallest-index tie
    if node has untried actions:
        randomly remove one legal action and create its child
    payoff = random_rollout(node, remaining_depth)
    for node and each ancestor: visits += 1; value_sum += payoff
return root child with most visits (then mean, then smallest action)
```

## 10. Dry Run

Child visits4,value_sum2 and parent visits16 give mean.5. With c=2, UCT=.5+2sqrt(log16/4)=2.1651092223153954. Backpropagating outcomes.75 and.25 along one edge gives visits2,sum1,mean.5 at both nodes; there is no alternating sign. The seeded depth3 example chooses root action1 after200 simulations.

## 11. Time Complexity

Let I be simulations,D depth and A≤32 branching. Selection scans children per level: O(I D A). Uniform rollout plus validation costs O(I D A) in the bounded integer-action API; each transition/outcome cost is model-dependent and must be added. Root node initialization O(A). Terminal root takes O(A) validation and no simulations. No average-case optimality or wall-clock promise.

## 12. Space Complexity

At most I+1 nodes, each retaining a state, child map and untried action list: O(I(A+state_size)) storage. Iterative traversal/backpropagation uses O(1) traversal state beyond the tree; simulator state costs depend on the model. No recursion stack grows during search.

## 13. Python Implementation

[Source](python/solution.py) exposes Node,uct,rollout,backpropagate,search,TinyPlanning. `search(model,state,iterations=200,max_depth=32,exploration=sqrt(2),seed=0)` returns `(action,root)`. Nodes expose visits,value_sum,mean,parent,children and untried. Local Generator owns expansion/rollout draws; model callbacks must be pure, deterministic and prompt.

## 14. C++ Implementation

Optional ML C++ is absent. DSA C++17/C++20 requirements remain unchanged; no dummy planning implementation is supplied.

## 15. Input and Output Examples

From repository root:

```sh
python machine-learning/reinforcement-learning/monte-carlo-tree-search/python/example.py
```

Executed output:

```json
{"action": 1, "root_visits": 200}
```

TinyPlanning state=(depth,bits), actions0/1 append a bit, depth3 terminates and only bits7 rewards1. Tests separately replan at each decision and verify final outcome1.

## 16. Edge Cases

Terminal roots return `(None,root)` with zero visits. Unvisited UCT is intentionally+∞. Reject zero/excess iterations, depth>64, duplicate/invalid actions, terminal states with legal actions, nonterminal states without actions, nonfinite outcomes or exhausted nonterminal rollouts. Iterations≤10000,branching≤32,depth≤64. Legal-action validation consumes at most33 iterable entries before rejecting excess branching; it validates native integer actions before hashing for uniqueness. Depth exhaustion raises instead of inventing a heuristic payoff.

## 17. Advantages

Any successful finite search produces a legal action with explicit visit evidence. Rollouts avoid full enumeration and the seed reproduces this deterministic model’s tree.

## 18. Disadvantages and Limitations

Deterministic single-agent terminal payoffs only. No two-player zero-sum perspective/sign propagation, stochastic transition nodes, transpositions, intermediate rewards, discounting or learned rollout policy. State mutation and indefinitely blocking model callbacks violate the pure bounded model contract. Small budgets can select poor actions and random rollout variance remains.

## 19. When to Use It

Use when a cheap deterministic simulator and finite terminal-depth bound are available and planning can spend a controlled simulation budget.

## 20. When Not to Use It

Avoid a stochastic or adversarial model without extending and validating its semantics; avoid tasks whose terminal state cannot be reached within the declared depth.

## 21. Comparison With Related Algorithms

| Method | Source of decisions | Budget |
| --- | --- | --- |
| MCTS | rollout statistics/UCT tree | simulations/depth |
| Exhaustive minimax | full adversarial backups | complete game tree |
| Q-Learning | learned model-free table | interaction episodes |

This implementation does not call minimax and does not apply adversarial sign changes.

## 22. Interview Questions

Why do unvisited children have infinite UCT? Why choose final visits rather than exploration score? Which nodes receive a rollout result? Why would two-player games require a different value perspective?

## 23. Practice Problems

1. Verify the UCT dry run.
2. Trace one expansion/rollout/backpropagation.
3. Plot counts from a saved seeded tree using your own plotting code.
4. Construct a depth-bound failure and explain why an arbitrary zero payoff would change the planning objective.

## 24. References

[Kocsis and Szepesvári, Bandit Based Monte-Carlo Planning, 2006](https://aima.cs.berkeley.edu/~russell/classes/cs294/s11/readings/Kocsis%2BSzepesvari:2006.pdf), original UCT paper in a university course mirror. [Tests](tests/test_python.py) include independent UCT arithmetic, hand backpropagation, legal expansion, visit/resource invariants, terminal/invalid models and3 seeded planning trials.

## 25. Author Attribution

Maintained by **MD.Khalid Hasan**. [Project](https://github.com/khalidhasan7343/algorithm-atlas),
[MIT License](../../../LICENSE), [contribution policy](../../../CONTRIBUTING.md).
