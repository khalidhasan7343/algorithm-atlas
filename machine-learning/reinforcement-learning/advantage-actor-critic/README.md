# Advantage Actor-Critic (A2C)

## 1. Algorithm Name

Advantage Actor-Critic (A2C). Synchronous categorical n-step actor-critic with separate tanh actor and scalar value networks.

## 2. Overview

Synchronous categorical n-step actor-critic with separate tanh actor and scalar value networks. A learned baseline and bootstrapped tail can reduce Monte Carlo variance and support finite rollout cuts.

## 3. Problem Statement

An MDP supplies observation vectors s∈R^d, actions, scalar rewards, transition law P and γ∈[0,1]. The environment API is `reset(seed)` and `step(action)→(s_next,r,terminated,truncated,info)`. Actions are categorical indices0..A−1. True termination ends future return; a time limit is an observation cut. Return inspectable learned networks and bounded training diagnostics.

## 4. Why Do We Need This Algorithm?

A learned baseline and bootstrapped tail can reduce Monte Carlo variance and support finite rollout cuts. The baseline/target and data-collection rules distinguish this algorithm from superficially similar updates.

## 5. Real-World Applications

Small educational reward-control experiments with inspectable transitions and gradients. The diagnostic Bandit observes[1], actions0/1 reward0/1 and terminates after one step. These synthetic tasks validate components and bounded learning, not benchmark superiority.

## 6. Core Intuition

For a bounded trajectory ending at k, R_t=Σ_{j=t}^{k−1}γ^(j−t)r_j+γ^(k−t)V_old(s_k), with tail0 only for true termination. A_t=R_t−V_old(s_t). Minimize actor Lπ=−mean(logπ(a_t|s_t) stop_gradient(A_t)) and critic Lv=mean((V(s_t)−R_t)²)/2. This is the usual sampled n-step advantage surrogate, without GAE, entropy bonus or an extra episodic γ^t actor weight.

## 7. Prerequisites

MDPs, discounted n-step returns, softmax or bounded tanh policies, chain-rule differentiation and SGD. Read [RL contracts](../../../docs/reinforcement-learning-conventions.md) and [A2C](../advantage-actor-critic/README.md) for stopped advantages; [DQN](../deep-q-networks/README.md) explains replay/targets.

## 8. Step-by-Step Working Process

For every iteration create envs independent environments; freeze parameters across all their collected trajectories; concatenate their observations, actions and n-step targets; compute separate actor and critic gradients; norm-clip each to10; apply one SGD update to each network atomically. No worker applies an update before the complete synchronous batch is collected.

Both networks use explicit tanh-MLP backpropagation from [support](../support.py): dW2=HᵀD, db2=ΣD, dH=(DW2ᵀ)⊙(1−H²), dW1=XᵀdH. Objectives supply D analytically. Stored sampled losses and return histories do not certify convergence.

## 9. Pseudocode

```text
repeat iterations:
    rows = []
    for each environment: rows += rollout(fixed_actor, fixed_critic)
    X,A,R = concatenate(rows)
    advantage = stop_gradient(R - critic(X))
    actor_gradient = gradient(-mean(log_pi(A|X) * advantage))
    critic_gradient = gradient(mean((critic(X)-R)**2)/2)
    apply one clipped SGD update to actor and critic
```

## 10. Dry Run

Zero actor logits give [.5,.5]. With V=.25, terminal reward1 and chosen action1, R=1,A=.75. Actor loss=.75log2=0.5198603854199589, logit/bias gradient=[.375,−.375]; critic loss=.28125 and bias gradient=−.75. For a truncation with reward1,γ=.9 and tail value2, R=2.8.

## 11. Time Complexity

For P combined parameters, K environments, T maximum steps and I iterations, O(IKT(P+A)) work; each iteration makes one actor and one critic update.

## 12. Space Complexity

Storage O(P+KT(d+A+h)+I). No replay or target copy beyond frozen current rollout parameters.

## 13. Python Implementation

[Canonical source](python/solution.py). A2C(inputs=1,n_actions=2,hidden=8,learning_rate=.05,gamma=.9,seed=0). `train(factory=Bandit,iterations=200,max_steps=64,envs=2)`, `action`, actor,critic,returns_,loss_history_. `loss_gradients` exposes both stopped-target objectives and explicit gradients. Float64 NumPy/stdlib only. All gradients are analytic; finite differences appear only in independent tests. B7 source remains unchanged because streaming trajectory/worker state requires separate RL bookkeeping.

## 14. C++ Implementation

Optional ML C++ is absent. No dummy source/test files; DSA Python/C++17/C++20 requirements remain enforced.

## 15. Input and Output Examples

Run from repository root:

```sh
python machine-learning/reinforcement-learning/advantage-actor-critic/python/example.py
```

Executed output:

```json
{"actor_loss": 0.5198603854199589, "critic_loss": 0.28125}
```

Use `support.evaluate(agent,factory)` for separately reset episodes with greedy categorical actions or a noise-free deterministic actor. Multiworker training ordering is not an evaluation seed guarantee.

## 16. Edge Cases

Validate real finite nonempty arrays, exact feature/action shapes, native scalar flags, hyperparameters and resource limits before indexing/updating. Observation/reward magnitudes≤1e6; stable log-softmax subtracts row maxima. NaN/Inf state/outputs raise; gradient clipping cannot rescue a nonfinite computation. No global NumPy RNG mutation. envs≤8,iterations≤5000,max_steps≤256,total interactions≤100000. Synchronous rollouts are sequential collection under frozen parameters, not concurrent A3C. No GAE/entropy regularization, variable-length padding, importance corrections or convergence guarantee.

## 17. Advantages

A learned baseline and bootstrapped tail can reduce Monte Carlo variance and support finite rollout cuts.

## 18. Disadvantages and Limitations

envs≤8,iterations≤5000,max_steps≤256,total interactions≤100000. Synchronous rollouts are sequential collection under frozen parameters, not concurrent A3C. No GAE/entropy regularization, variable-length padding, importance corrections or convergence guarantee. Fixed-budget-completed means execution ended within a budget, not that the objective converged. Only the reported seeded diagnostics establish local behavior.

## 19. When to Use It

Use when synchronous categorical n-step actor-critic with separate tanh actor and scalar value networks. matches the intended data and update semantics.

## 20. When Not to Use It

Avoid high-dimensional production control or tasks where the stated estimator, action family or fixed budget is inappropriate.

## 21. Comparison With Related Algorithms

REINFORCE has no critic and requires complete terminal rollouts here. A2C waits for the full rollout batch before updating. A3C applies independently computed worker gradients asynchronously.

## 22. Interview Questions

Derive the stated objective and its stopped quantities. Why distinguish termination and truncation? Which inputs or snapshots must remain fixed during a numerical gradient check?

## 23. Practice Problems

1. Reproduce the dry run.
2. Derive all output-bias gradients independently.
3. Change an exploration setting and compare separate evaluation.
4. Add a two-step MDP and hand-check bootstrapping before measuring training.

## 24. References

[Sutton and Barto, chapter13](https://www.incompleteideas.net/book/bookdraft2018mar21.pdf) for actor-critic; [Mnih et al.](https://proceedings.mlr.press/v48/mniha16.html) for n-step actor-critic components.

Verification: Independent advantages/value targets and logit gradients; actor finite differences with a frozen advantage; separate critic finite differences; truncation tail versus terminal mask;3 seeded replicated training/evaluation trials. [Tests](tests/test_python.py) distinguish exact mathematics, stochastic training and concurrency invariants.

## 25. Author Attribution

Maintained by **MD.Khalid Hasan**. [Project](https://github.com/khalidhasan7343/algorithm-atlas),
[MIT License](../../../LICENSE), [contribution policy](../../../CONTRIBUTING.md).
