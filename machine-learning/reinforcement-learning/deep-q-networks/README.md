# Deep Q-Networks (DQN)

## 1. Algorithm Name

Deep Q-Networks (DQN) — off-policy neural value learning.

## 2. Overview

Replay breaks immediate temporal ordering; a copied target network holds the bootstrap function fixed between hard synchronization steps. A tanh MLP approximates Q; there is no tabular substitution.

## 3. Problem Statement

Learn from an MDP (states/observations s, finite actions a, transition law P, scalar reward r, discount γ). Input observations have shape(d,), training matrices(N,d), action indices(N,). A trajectory ends at true termination or a time limit; only true termination implies zero future value. y=r+γ(1−terminated) max_b Q_target(s′,b); L=mean((Q_online(s,a)−y)²)/2. Targets are fixed when differentiating online parameters.

## 4. Why Do We Need This Algorithm?

Use off-policy neural value learning when its estimator matches the information available. Replay breaks immediate temporal ordering; a copied target network holds the bootstrap function fixed between hard synchronization steps. A tanh MLP approximates Q; there is no tabular substitution.

## 5. Real-World Applications

Diagnostic control with small numerical state descriptions: teaching reward-based decision learning, validating exploration and checking gradients before scaling. The included one-step Bandit exposes observation[1], actions0/1 and rewards0/1; it establishes component correctness, not benchmark performance.

## 6. Core Intuition

y=r+γ(1−terminated) max_b Q_target(s′,b); L=mean((Q_online(s,a)−y)²)/2. Targets are fixed when differentiating online parameters.

The shared network is H=tanh(XW1+b1), output=HW2+b2. For an output adjoint D, dW2=HᵀD, db2=ΣD; dH=(DW2ᵀ)⊙(1−H²); dW1=XᵀdH, db1=ΣdH. The canonical objective supplies D analytically.

## 7. Prerequisites

MDPs, discounted returns, vector calculus, SGD, stable log probabilities and the [tabular lessons](../q-learning/README.md). See [RL contracts](../../../docs/reinforcement-learning-conventions.md) for termination and shapes.

## 8. Step-by-Step Working Process

Collect epsilon-greedy transitions; retain owned FIFO replay; uniformly sample without replacement once batch_size is available; build targets from the target snapshot; backpropagate selected-action residuals; clip the joint gradient norm at10; SGD-update online parameters; hard-copy them every target_interval updates.

Updates are bounded diagnostics, not convergence certificates. Loss histories record pre-update sampled objectives. Mathematical correctness is established independently from noisy training returns.

## 9. Pseudocode

```text
initialize online MLP and target = deep_copy(online)
for each bounded episode and step:
    a = epsilon_greedy(online(s)); next_s,r,done,cut = env.step(a)
    replay.push(s,a,r,next_s,done,cut)
    if replay has a minibatch:
        batch = uniform_sample_without_replacement(replay)
        y = r + gamma * (not done) * max(target(next_s))
        g = gradient_of_half_MSE(online(s,a), stop_gradient(y))
        online -= learning_rate * clipped(g)
        periodically target = deep_copy(online)
    break on done or cut
```

## 10. Dry Run

With all parameters zero, observation[1], action1 and fixed target1, Q=[0,0], residual=−1 and loss=.5. Output bias gradient=[0,−1]; other gradients vanish. Separately, reward1, next target Q=[2,3], γ=.9 gives3.7 unless terminated, in which case target1.

## 11. Time Complexity

For P MLP parameters, B replay batch, C capacity, N interactions and U updates: forward/backward O(BP), max over A actions adds O(BA). Training O(NP+U B(P+A)); FIFO eviction O(C) references and sampling has NumPy-dependent overhead bounded by C. Hard sync O(P).

## 12. Space Complexity

O(P+Cd+B(d+A+h)) for online/target, replay vectors of total state/action width d, and a batch with h hidden units and A action outputs. Histories O(episodes+U).

## 13. Python Implementation

[Source](python/solution.py). DQN(inputs=1,n_actions=2,hidden=8,learning_rate=.05,gamma=.9,epsilon=.2,capacity=512,batch_size=16,target_interval=10,seed=0). `action`, `train`, `step`, `sync`; `online`, `target`, `replay`, loss_history_, updates_ are inspectable. Shared [support](../support.py) owns explicit tanh dense forward/backward primitives, validation and environments; no estimator/autodiff library is called. Parameters initialize from a local Generator; all arrays are float64.

## 14. C++ Implementation

Optional ML C++ is absent; no fake implementation. DSA still requires Python and C++17/C++20.

## 15. Input and Output Examples

From repository root:

```sh
python machine-learning/reinforcement-learning/deep-q-networks/python/example.py
```

Executed output:

```json
{"loss": 0.5, "bias_gradient": [0.0, -1.0]}
```

Training tests use separately reset greedy evaluation episodes through `support.evaluate`; exploration is disabled during that evaluation.

## 16. Edge Cases

Reject nonfinite/complex/bool observations, wrong shapes, invalid actions, empty batches, invalid hyperparameters and oversized budgets. Stable tanh and shifted log-softmax avoid exp overflow. Reward/observation magnitudes≤1e6; dimensions/hidden/actions≤32, interactions≤100000, episodes≤5000,max_steps≤256. Replay capacity≤4096; batch≤capacity; updates≤10000; underflow fails.

## 17. Advantages

Replay breaks immediate temporal ordering; a copied target network holds the bootstrap function fixed between hard synchronization steps. A tanh MLP approximates Q; there is no tabular substitution.

## 18. Disadvantages and Limitations

Uniform one-step DQN with tanh MLP, hard targets and half-MSE; no Double DQN, prioritized replay, image encoder or production stability guarantee. Nonlinear off-policy bootstrapping can diverge. Gradient clipping cannot guarantee stable learning or repair poor reward scaling. Float64 rounding and stochastic exploration limit reproducibility across platforms.

## 19. When to Use It

Small vector-observation discrete-action problems where exact state enumeration is impractical.

## 20. When Not to Use It

Continuous actions, very high-dimensional images, or tasks requiring a convergence guarantee.

## 21. Comparison With Related Algorithms

Q-Learning stores exact table cells; DQN approximates them with a neural network. REINFORCE optimizes a stochastic actor instead of a max Bellman target.

## 22. Interview Questions

Why freeze TD targets? Why can a target snapshot become stale? How does replay change data usage? Why does truncation retain bootstrapping?

## 23. Practice Problems

Hand-compute the zero-network gradient; vary target_interval; compare target snapshots before/after sync; independently solve a finite MDP before comparing approximate control.

## 24. References

[Mnih et al., Human-level control through deep reinforcement learning](https://www.nature.com/articles/nature14236); [the earlier DQN paper](https://arxiv.org/abs/1312.5602) motivates neural action values and replay; this implementation also uses hard target snapshots from the later formulation.

Verification: Hand neural forward/TD targets, fixed-target central finite differences for every weight/bias, replay ownership/FIFO/underflow, hard snapshot independence,3 repeated seeded tiny-training trials, greedy held-out evaluation and truncation masking. Tests are in [tests/test_python.py](tests/test_python.py).

## 25. Author Attribution

Maintained by **MD.Khalid Hasan**. [Project](https://github.com/khalidhasan7343/algorithm-atlas),
[MIT License](../../../LICENSE), [contribution policy](../../../CONTRIBUTING.md).
