# Q-Learning

## 1. Algorithm Name

Q-Learning — tabular off-policy temporal-difference control.

## 2. Overview

Learn a finite state/action value table from interactions without a transition model. Off-policy: exploration may select any behavior action, but the target uses the greedy next action.

## 3. Problem Statement

A finite MDP has states s∈{0,…,S−1}, actions a∈{0,…,A−1}, reward r, transition law P and discount γ∈[0,1]. Given bounded episodes, return Q and a deterministic greedy policy. A true terminal state has zero future return; an external time limit truncates observation without changing the underlying MDP.

## 4. Why Do We Need This Algorithm?

Learn the optimal greedy action values while collecting exploratory experience. The max target separates the learning policy from the behavior policy.

## 5. Real-World Applications

Small scheduling or navigation models with fully enumerated states and actions; diagnostic experiments before using approximation.

## 6. Core Intuition

One transition moves one table cell toward a bootstrapped target. Off-policy: exploration may select any behavior action, but the target uses the greedy next action.

`Q(s,a) ← Q(s,a) + α [r + γ max_b Q(s′,b) − Q(s,a)]`

For terminal transitions target=r. α∈[0,1] controls interpolation; α=0 is an explicit no-op.

## 7. Prerequisites

Finite probability distributions, discounted returns, Bellman equations and NumPy indexing. Compare [the other tabular method](../sarsa/README.md).

## 8. Step-by-Step Working Process

1. Initialize Q and local RNG.
2. Choose an epsilon-greedy behavior action.
3. Step the environment.
4. Update toward reward plus max next value, masking only true termination.
5. Continue with the observed next state.
6. Stop at termination, truncation or the caller budget.

The conditional expected update uses the Bellman optimality operator. Classical convergence requires sufficient visitation and suitable diminishing step sizes; this fixed-budget example does not assert those conditions.

## 9. Pseudocode

```text
initialize Q to zero
for each bounded episode:
    s = reset()
    repeat up to max_steps:
        a = epsilon_greedy(Q[s])
        s_next, r, terminal, truncated = step(a)
        target = r if terminal else r + gamma * max(Q[s_next])
        Q[s,a] += alpha * (target - Q[s,a])
        s = s_next
        break on terminal or truncated
```

## 10. Dry Run

Q(0,1)=0, Q(1,:)=[3,10], r=1, α=.5, γ=.9. Target=1+.9×10=10 and new Q(0,1)=5.0. A true terminal transition instead gives .5. SARSA with next action0 would give1.85.

## 11. Time Complexity

Let S be states, A actions, E episodes and T maximum steps. Initialization Θ(SA); action choice Θ(A). Nonterminal update Θ(A) for the max; training O(ET A). Policy extraction Θ(SA). Early termination reduces actual steps; no distribution-independent average stopping time is claimed.

## 12. Space Complexity

Θ(SA) for Q, O(E) for episode return history, O(1) temporary update state. The diagnostic Chain is O(1). Greedy policy output O(S); no trajectory or replay storage.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `QLearning(n_states,n_actions,alpha=.2,gamma=.9,epsilon=.1,seed=0)`, `update`, `action`, `policy`, `train`. Q is accessible for educational experiments. `policy()` copies indices; `train` updates existing Q and records returns_/optimization_status_. Validation rejects invalid indices before NumPy can wrap negatives. Shared [support](../support.py) provides validation and epsilon sampling, not this update rule.

## 14. C++ Implementation

C++ is optional for authorized ML and absent. No placeholder source or tests. DSA continues to require real C++17/C++20 execution.

## 15. Input and Output Examples

From repository root, run:

```sh
python machine-learning/reinforcement-learning/q-learning/python/example.py
```

Output:

```json
{"update": 5.0}
```

For training, use the `Chain` environment in [support](../support.py), three states and two actions. Reset returns state0; right advances and earns1 upon entering terminal state2, left retreats with reward0. Greedy evaluation uses `action(s, explore=False)` in separately reset episodes.

## 16. Edge Cases

Empty tables, bool/noninteger indices, out-of-range actions/states, NaN/Inf rewards/Q, invalid α/γ/ε and oversized tables/budgets raise ValueError. First index breaks greedy ties. γ=0 ignores next values; α=0 preserves Q. S≤4096,A≤32,SA≤65536; episodes≤5000,steps≤256,total budget≤100000. Stop after done and reset before another environment step.

## 17. Advantages

Simple exact table representation; independent behavior exploration and greedy target; no learned model or neural gradients.

## 18. Disadvantages and Limitations

Finite table only: large/continuous states need another representation. Constant α and ε do not guarantee convergence. High γ, rare exploration or short truncation budgets can slow learning. Rewards and all arithmetic must stay finite (input magnitude≤1e6). No arbitrary-task performance claim.

## 19. When to Use It

Use for finite-state off-policy greedy control with adequate coverage.

## 20. When Not to Use It

Avoid when the exploratory behavior policy itself is the evaluation target, or states cannot be enumerated.

## 21. Comparison With Related Algorithms

| Method | Bootstrap | Policy relation |
| --- | --- | --- |
| Q-Learning | max_a Q(s′,a) | off-policy |
| SARSA | Q(s′,sampled a′) | on-policy |
| DQN | neural max target | off-policy, replay/target network |

## 22. Interview Questions

Why is the max target off-policy? How do terminal and truncated transitions differ? What conditions are needed for convergence?

## 23. Practice Problems

1. Reproduce the dry run and terminal variant.
2. Vary γ and inspect a deterministic chain.
3. Compare exploratory SARSA and Q-Learning on a finite cliff-style model.
4. Derive a two-state Bellman solution independently before comparing learned values.

## 24. References

[Sutton and Barto, Reinforcement Learning: An Introduction, second edition](https://www.incompleteideas.net/book/bookdraft2018mar21.pdf), chapter6; compare the SARSA and Q-learning Bellman operators. Independent tests include hand updates,50 seeded random updates, exploration, truncation and the finite-MDP value-iteration oracle in the Q-Learning test suite. Training is a separate bounded diagnostic, not an oracle for update correctness.

## 25. Author Attribution

Maintained by **MD.Khalid Hasan**. [Project](https://github.com/khalidhasan7343/algorithm-atlas),
[MIT License](../../../LICENSE), [contribution policy](../../../CONTRIBUTING.md).
