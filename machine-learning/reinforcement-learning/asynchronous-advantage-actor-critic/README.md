# Asynchronous Advantage Actor-Critic (A3C)

## 1. Algorithm Name

Asynchronous Advantage Actor-Critic (A3C). Genuine concurrent categorical n-step actor-critic with local parameter snapshots and lock-protected asynchronous global SGD.

## 2. Overview

Genuine concurrent categorical n-step actor-critic with local parameter snapshots and lock-protected asynchronous global SGD. Independent rollouts proceed while other workers update. A lock provides coherent parameter snapshots and avoids torn writes while retaining asynchronous stale-gradient learning.

## 3. Problem Statement

An MDP supplies observation vectors s∈R^d, actions, scalar rewards, transition law P and γ∈[0,1]. The environment API is `reset(seed)` and `step(action)→(s_next,r,terminated,truncated,info)`. Actions are categorical indices0..A−1. True termination ends future return; a time limit is an observation cut. Return inspectable learned networks and bounded training diagnostics.

## 4. Why Do We Need This Algorithm?

Independent rollouts proceed while other workers update. A lock provides coherent parameter snapshots and avoids torn writes while retaining asynchronous stale-gradient learning. The baseline/target and data-collection rules distinguish this algorithm from superficially similar updates.

## 5. Real-World Applications

Small educational reward-control experiments with inspectable transitions and gradients. The diagnostic Bandit observes[1], actions0/1 reward0/1 and terminates after one step. These synthetic tasks validate components and bounded learning, not benchmark superiority.

## 6. Core Intuition

Each worker computes the same stopped n-step advantage and half-MSE value objectives as [A2C](../advantage-actor-critic/README.md), using its own snapshot. Local gradients are applied to the CURRENT global networks after collection, so gradients can be stale. There is no synchronous gradient averaging or per-iteration worker barrier.

## 7. Prerequisites

MDPs, discounted n-step returns, softmax or bounded tanh policies, chain-rule differentiation and SGD. Read [RL contracts](../../../docs/reinforcement-learning-conventions.md) and [A2C](../advantage-actor-critic/README.md) for stopped advantages; [DQN](../deep-q-networks/README.md) explains replay/targets.

## 8. Step-by-Step Working Process

Create1..8 standard-library threads, independent environment instances and SeedSequence-derived RNGs. A start event releases them; a lock protects copying the global actor/critic and version, then releases during local rollout and gradient computation. Reacquire only to atomically apply both gradients to current global state and increment the version. Worker exceptions set cancellation and enter an error queue; finally close environments; join every supported bounded worker and rethrow with cause.

Both networks use explicit tanh-MLP backpropagation from [support](../support.py): dW2=HᵀD, db2=ΣD, dH=(DW2ᵀ)⊙(1−H²), dW1=XᵀdH. Objectives supply D analytically. Stored sampled losses and return histories do not certify convergence.

## 9. Pseudocode

```text
start workers with independent seeds/environments
worker repeats its bounded iterations:
    with lock: local_actor, local_critic, version = copy(global_state)
    rollout = collect(local_actor, local_critic, local_environment)
    gradients = actor_critic_gradients(local_snapshot, rollout)
    with lock:
        if cancelled: stop
        apply gradients to current global actor and critic
        global_version += 1
on exception: queue error; signal cancellation
finally: close environment
join workers; reject timeout or worker error
```

## 10. Dry Run

One worker, all-zero actor/critic, terminal reward1 and learning rate.1: advantage1, critic bias gradient−1, hence global critic bias.1. The actor chooses one of two equiprobable actions and moves its two biases to ±.05. With two workers and one update each, updates_=2 and workers_alive_=0; exact parameter order is scheduling-dependent.

## 11. Time Complexity

For W workers,I local iterations,T steps and P combined parameters, total work O(WIT(P+A)), storage O(W(P+T(d+A+h))+W I+P). Lock copies/applications cost O(P) per update. Wall time is scheduling/GIL/NumPy dependent; no speedup promise.

## 12. Space Complexity

For W workers,I local iterations,T steps and P combined parameters, total work O(WIT(P+A)), storage O(W(P+T(d+A+h))+W I+P). Lock copies/applications cost O(P) per update. Wall time is scheduling/GIL/NumPy dependent; no speedup promise.

## 13. Python Implementation

[Canonical source](python/solution.py). A3C uses A2C initialization and its mathematical gradient components explicitly. `train(factory=Bandit,iterations=100,max_steps=32,workers=2,timeout=30.)` owns the concurrent procedure. worker_records_ includes worker,thread_id,snapshot_version,applied_version,trajectory_length; updates_,worker_seeds_,workers_created_,workers_alive_ expose bounded diagnostics. Float64 NumPy/stdlib only. All gradients are analytic; finite differences appear only in independent tests. B7 source remains unchanged because streaming trajectory/worker state requires separate RL bookkeeping.

## 14. C++ Implementation

Optional ML C++ is absent. No dummy source/test files; DSA Python/C++17/C++20 requirements remain enforced.

## 15. Input and Output Examples

Run from repository root:

```sh
python machine-learning/reinforcement-learning/asynchronous-advantage-actor-critic/python/example.py
```

Executed output:

```json
{"updates": 2, "workers_alive": 0}
```

Use `support.evaluate(agent,factory)` for separately reset episodes with greedy categorical actions or a noise-free deterministic actor. Multiworker training ordering is not an evaluation seed guarantee.

## 16. Edge Cases

Validate real finite nonempty arrays, exact feature/action shapes, native scalar flags, hyperparameters and resource limits before indexing/updating. Observation/reward magnitudes≤1e6; stable log-softmax subtracts row maxima. NaN/Inf state/outputs raise; gradient clipping cannot rescue a nonfinite computation. No global NumPy RNG mutation. workers≤8,iterations≤5000,max_steps≤256,total interactions≤100000,global updates≤10000,timeout .01..60seconds. Lock-protected updates differ from original Hogwild lock-free writes: state is coherent, update order and staleness remain asynchronous. Multiworker runs are not bitwise reproducible. Supported environments must return promptly; Python cannot forcibly kill a thread blocked indefinitely in a user callback. Daemon fallback and timeout report that violation, not successful clean shutdown. Normal/error tests verify all threads joined.

## 17. Advantages

Independent rollouts proceed while other workers update. A lock provides coherent parameter snapshots and avoids torn writes while retaining asynchronous stale-gradient learning.

## 18. Disadvantages and Limitations

workers≤8,iterations≤5000,max_steps≤256,total interactions≤100000,global updates≤10000,timeout .01..60seconds. Lock-protected updates differ from original Hogwild lock-free writes: state is coherent, update order and staleness remain asynchronous. Multiworker runs are not bitwise reproducible. Supported environments must return promptly; Python cannot forcibly kill a thread blocked indefinitely in a user callback. Daemon fallback and timeout report that violation, not successful clean shutdown. Normal/error tests verify all threads joined. Fixed-budget-completed means execution ended within a budget, not that the objective converged. Only the reported seeded diagnostics establish local behavior.

## 19. When to Use It

Use when genuine concurrent categorical n-step actor-critic with local parameter snapshots and lock-protected asynchronous global sgd. matches the intended data and update semantics.

## 20. When Not to Use It

Avoid tasks that require deterministic multiworker ordering or callbacks that may block indefinitely.

## 21. Comparison With Related Algorithms

Synchronous A2C waits for all rollout data. A3C here computes/updates independently with actual threads. The original lock-free formulation permits unsynchronized writes; this educational variant serializes only snapshots/applications.

## 22. Interview Questions

Derive the stated objective and its stopped quantities. Why distinguish termination and truncation? Which writes require the lock and why are gradients stale?

## 23. Practice Problems

1. Reproduce the dry run.
2. Derive all output-bias gradients independently.
3. Change an exploration setting and compare separate evaluation.
4. Add a two-step MDP and hand-check bootstrapping before measuring training.

## 24. References

[Mnih et al., Asynchronous Methods for Deep Reinforcement Learning, 2016](https://proceedings.mlr.press/v48/mniha16.html). The lock-protected SGD variant is deliberately documented instead of claiming original optimizer/Hogwild parity.

Verification: A timed barrier inside two distinct worker environments proves overlapping step execution; local snapshot0/global versions1,2; independent gradient finite differences; exact single-worker global step; deterministic single-worker repeated training; multiworker bounded update/learning invariants; factory,rollout,close errors and zero live threads. [Tests](tests/test_python.py) distinguish exact mathematics, stochastic training and concurrency invariants.

## 25. Author Attribution

Maintained by **MD.Khalid Hasan**. [Project](https://github.com/khalidhasan7343/algorithm-atlas),
[MIT License](../../../LICENSE), [contribution policy](../../../CONTRIBUTING.md).
