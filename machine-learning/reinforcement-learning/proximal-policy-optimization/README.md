# Proximal Policy Optimization (PPO)

## 1. Algorithm Name

Proximal Policy Optimization (PPO). Categorical clipped-surrogate PPO, separate tanh critic, frozen n-step advantages, repeated shuffled minibatch SGD.

## 2. Overview

Categorical clipped-surrogate PPO, separate tanh critic, frozen n-step advantages, repeated shuffled minibatch SGD. Several minibatch passes reuse a rollout while limiting incentives for large selected-action probability changes.

## 3. Problem Statement

An MDP supplies observation vectors s∈R^d, actions, scalar rewards, transition law P and γ∈[0,1]. The environment API is `reset(seed)` and `step(action)→(s_next,r,terminated,truncated,info)`. Actions are categorical indices0..A−1. True termination ends future return; a time limit is an observation cut. Return inspectable learned networks and bounded training diagnostics.

## 4. Why Do We Need This Algorithm?

Several minibatch passes reuse a rollout while limiting incentives for large selected-action probability changes. The baseline/target and data-collection rules distinguish this algorithm from superficially similar updates.

## 5. Real-World Applications

Small educational reward-control experiments with inspectable transitions and gradients. The diagnostic Bandit observes[1], actions0/1 reward0/1 and terminates after one step. These synthetic tasks validate components and bounded learning, not benchmark superiority.

## 6. Core Intuition

r=exp(logπ_new(a|s)−logπ_old(a|s)); maximize mean(min(r A,clip(r,1−ε,1+ε) A)). Minimize its negative. A=R_nstep−V_old is frozen across every epoch; R bootstraps truncation/budget cuts, masks true terminals, and is not GAE. Critic minimizes half mean squared error to fixed R. No advantage normalization, entropy bonus, value clipping or hard KL constraint.

## 7. Prerequisites

MDPs, discounted n-step returns, softmax or bounded tanh policies, chain-rule differentiation and SGD. Read [RL contracts](../../../docs/reinforcement-learning-conventions.md) and [A2C](../advantage-actor-critic/README.md) for stopped advantages; [DQN](../deep-q-networks/README.md) explains replay/targets.

## 8. Step-by-Step Working Process

Copy old actor and critic once per rollout round; collect rollout_episodes with those copies; store taken-action old log probabilities and n-step targets; compute fixed advantages. For each epoch shuffle indices, form minibatches and apply analytic clipped actor and critic gradients. Never refresh old log probabilities within the epochs. Norm-clip each network gradient at10.

Both networks use explicit tanh-MLP backpropagation from [support](../support.py): dW2=HᵀD, db2=ΣD, dH=(DW2ᵀ)⊙(1−H²), dW1=XᵀdH. Objectives supply D analytically. Stored sampled losses and return histories do not certify convergence.

## 9. Pseudocode

```text
repeat rollout rounds:
    old_actor, old_critic = deep_copy(actor,critic)
    X,A,R = collect_episodes(old_actor,old_critic)
    old_logp = log_pi(old_actor,A|X); advantages = R - V(old_critic,X)
    repeat epochs:
        shuffle rollout indices
        for each minibatch:
            ratio = exp(log_pi(actor,A|X) - old_logp)
            loss = -mean(min(ratio*adv,clip(ratio)*adv))
            update actor with analytic clipped gradient
            update critic toward fixed R
```

## 10. Dry Run

Ratios[1.3,.7,1.3,.7], advantages[2,2,−2,−2], ε=.2 give surrogate terms[2.4,1.4,−2.6,−1.6]. Negative mean loss=.10000000000000009 (float64 rounding). Derivative with respect to new log probabilities is[0,−.35,.65,0]. Positive advantages clip high ratios; negative advantages clip low ratios.

## 11. Time Complexity

For I rollout rounds,R episodes,T steps,K epochs,B minibatch and P total parameters: rollout O(IRT(P+A)); optimization O(I K R T(P+A)) plus shuffling O(IKRT).

## 12. Space Complexity

Storage O(P+RT(d+A+h)+B(d+A+h)+I K ceil(RT/B)).

## 13. Python Implementation

[Canonical source](python/solution.py). PPO inherits A2C network initialization. `train(factory=Bandit,iterations=50,max_steps=32,rollout_episodes=8,epochs=4,batch_size=8,clip=.2)`. old_actor_,old_log_probs_,rollout_observations_,rollout_actions_ expose the last frozen rollout, while actor/critic contain updated parameters. Float64 NumPy/stdlib only. All gradients are analytic; finite differences appear only in independent tests. B7 source remains unchanged because streaming trajectory/worker state requires separate RL bookkeeping.

## 14. C++ Implementation

Optional ML C++ is absent. No dummy source/test files; DSA Python/C++17/C++20 requirements remain enforced.

## 15. Input and Output Examples

Run from repository root:

```sh
python machine-learning/reinforcement-learning/proximal-policy-optimization/python/example.py
```

Executed output:

```json
{"loss": 0.10000000000000009}
```

Use `support.evaluate(agent,factory)` for separately reset episodes with greedy categorical actions or a noise-free deterministic actor. Multiworker training ordering is not an evaluation seed guarantee.

## 16. Edge Cases

Validate real finite nonempty arrays, exact feature/action shapes, native scalar flags, hyperparameters and resource limits before indexing/updating. Observation/reward magnitudes≤1e6; stable log-softmax subtracts row maxima. NaN/Inf state/outputs raise; gradient clipping cannot rescue a nonfinite computation. No global NumPy RNG mutation. R≤32,K≤32,B≤4096,I≤5000,T≤256,total interactions≤100000 and conservative optimizer bound≤10000. Ratio overflow/nonfinite logs fail; no silent ratio capping substitutes for the objective. The min/clip kink has a documented active-branch choice; gradient checks avoid boundaries. Clipping is not an exact hard KL constraint or monotonic policy guarantee.

## 17. Advantages

Several minibatch passes reuse a rollout while limiting incentives for large selected-action probability changes.

## 18. Disadvantages and Limitations

R≤32,K≤32,B≤4096,I≤5000,T≤256,total interactions≤100000 and conservative optimizer bound≤10000. Ratio overflow/nonfinite logs fail; no silent ratio capping substitutes for the objective. The min/clip kink has a documented active-branch choice; gradient checks avoid boundaries. Clipping is not an exact hard KL constraint or monotonic policy guarantee. Fixed-budget-completed means execution ended within a budget, not that the objective converged. Only the reported seeded diagnostics establish local behavior.

## 19. When to Use It

Use when categorical clipped-surrogate ppo, separate tanh critic, frozen n-step advantages, repeated shuffled minibatch sgd. matches the intended data and update semantics.

## 20. When Not to Use It

Avoid high-dimensional production control or tasks where the stated estimator, action family or fixed budget is inappropriate.

## 21. Comparison With Related Algorithms

Ordinary policy gradient lacks the old/new ratio and clipped minimum. A2C performs one synchronous update. PPO reuses frozen rollout data across epochs, retaining a fixed old policy denominator.

## 22. Interview Questions

Derive the stated objective and its stopped quantities. Why distinguish termination and truncation? Which inputs or snapshots must remain fixed during a numerical gradient check?

## 23. Practice Problems

1. Reproduce the dry run.
2. Derive all output-bias gradients independently.
3. Change an exploration setting and compare separate evaluation.
4. Add a two-step MDP and hand-check bootstrapping before measuring training.

## 24. References

[Schulman et al., Proximal Policy Optimization Algorithms, 2017](https://arxiv.org/abs/1707.06347), clipped probability-ratio objective.

Verification: Independent ratios/minimum for both advantage signs, active and clipped gradients away from kinks, actor and critic finite differences, old-policy ownership across6 actual minibatch updates,3 repeated seeded bounded training trials, invalid logs/clip and separate greedy evaluation. [Tests](tests/test_python.py) distinguish exact mathematics, stochastic training and concurrency invariants.

## 25. Author Attribution

Maintained by **MD.Khalid Hasan**. [Project](https://github.com/khalidhasan7343/algorithm-atlas),
[MIT License](../../../LICENSE), [contribution policy](../../../CONTRIBUTING.md).
