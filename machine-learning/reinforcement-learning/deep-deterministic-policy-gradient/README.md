# Deep Deterministic Policy Gradient (DDPG)

## 1. Algorithm Name

Deep Deterministic Policy Gradient (DDPG). Off-policy deterministic continuous-action actor-critic with neural Q, FIFO replay, target actor/critic and Polyak interpolation.

## 2. Overview

Off-policy deterministic continuous-action actor-critic with neural Q, FIFO replay, target actor/critic and Polyak interpolation. Direct continuous actions avoid enumerating or maximizing a discrete action grid; the critic provides a differentiable actor direction and replay reuses experience.

## 3. Problem Statement

An MDP supplies observation vectors s∈R^d, actions, scalar rewards, transition law P and γ∈[0,1]. The environment API is `reset(seed)` and `step(action)→(s_next,r,terminated,truncated,info)`. Actions are continuous vectors with configured low/high bounds. True termination ends future return; a time limit is an observation cut. Return inspectable learned networks and bounded training diagnostics.

## 4. Why Do We Need This Algorithm?

Direct continuous actions avoid enumerating or maximizing a discrete action grid; the critic provides a differentiable actor direction and replay reuses experience. The baseline/target and data-collection rules distinguish this algorithm from superficially similar updates.

## 5. Real-World Applications

Small educational reward-control experiments with inspectable transitions and gradients. The Continuous environment samples x∈[−1,1], allows a∈[−1,1] and terminates after reward−(a−x/2)². These synthetic tasks validate components and bounded learning, not benchmark superiority.

## 6. Core Intuition

μθ(s)=c+b⊙tanh(fθ(s)), c=(high+low)/2,b=(high−low)/2. y=r+γ(1−terminated)Q_target(s′,μ_target(s′)). Critic minimizes mean((Q(s,a)−y)²)/2. Actor minimizes −mean Q(s,μθ(s)); backpropagate through fixed critic inputs and actor tanh bounds. Targets are constants for critic differentiation. Soft update θ_target←τθ_online+(1−τ)θ_target.

## 7. Prerequisites

MDPs, discounted n-step returns, softmax or bounded tanh policies, chain-rule differentiation and SGD. Read [RL contracts](../../../docs/reinforcement-learning-conventions.md) and [A2C](../advantage-actor-critic/README.md) for stopped advantages; [DQN](../deep-q-networks/README.md) explains replay/targets.

## 8. Step-by-Step Working Process

First collect128 uniform exploratory actions and update only the critic. Critic hidden biases initialize in[−.5,.5] to provide a non-odd tanh basis. Critic learning rate.02 and actor rate.001 separate their timescales. Then add independent Gaussian exploration noise to the bounded actor action, then clip to low/high. Store owned continuous transitions in FIFO replay. Sample a uniform minibatch; compute fixed target-network y; update critic; use that updated but actor-gradient-frozen critic to differentiate actions into the actor; update actor; softly interpolate both targets. True terminals mask bootstrap; truncation does not.

Both networks use explicit tanh-MLP backpropagation from [support](../support.py): dW2=HᵀD, db2=ΣD, dH=(DW2ᵀ)⊙(1−H²), dW1=XᵀdH. Objectives supply D analytically. Stored sampled losses and return histories do not certify convergence.

## 9. Pseudocode

```text
initialize actor,critic and deep-copied targets
for each bounded interaction:
    a = uniform(low,high) during warmup, otherwise clip(actor(s)+Gaussian_noise, low, high)
    store transition in bounded replay
    if replay ready:
        y = r + gamma*(not terminal)*target_critic(next_s,target_actor(next_s))
        update critic on fixed-target half-MSE
        after warmup: update actor on -mean(critic(s,actor(s))) via input gradient
        target_actor = tau*actor + (1-tau)*target_actor
        target_critic = tau*critic + (1-tau)*target_critic
```

## 10. Dry Run

With zero actor parameters and bounds[−2,4], tanh(0)=0 yields action1. With target bias0, online bias2,τ=.25, soft update produces.5. Reward1,next target Q3,γ=.9 gives y3.7 if nonterminal and1 if truly terminal. The actor derivative includes action scale3 and tanh derivative, not a discrete argmax.

## 11. Time Complexity

With P combined actor/critic parameters,B batch,C replay capacity,N interactions,U updates and d total state/action width: O(NP+U BP), plus bounded replay eviction/sampling overhead. Four networks need O(P), replay O(Cd), batch activations O(B(d+h)); histories O(U+episodes).

## 12. Space Complexity

With P combined actor/critic parameters,B batch,C replay capacity,N interactions,U updates and d total state/action width: O(NP+U BP), plus bounded replay eviction/sampling overhead. Four networks need O(P), replay O(Cd), batch activations O(B(d+h)); histories O(U+episodes).

## 13. Python Implementation

[Canonical source](python/solution.py). DDPG(inputs=1,action_dim=1,low=None,high=None,hidden=16,learning_rate=.02,actor_learning_rate=.001,warmup_steps=128,gamma=.9,tau=.05,noise=.3,capacity=512,batch_size=32,seed=0). Bounds default to[−1,1] per dimension. `train(env,episodes=2400,max_steps=1)`, `step`, `action(explore=False)` for evaluation. actor,critic,target_actor,target_critic,replay and loss histories are inspectable. Float64 NumPy/stdlib only. All gradients are analytic; finite differences appear only in independent tests. B7 source remains unchanged because streaming trajectory/worker state requires separate RL bookkeeping.

## 14. C++ Implementation

Optional ML C++ is absent. No dummy source/test files; DSA Python/C++17/C++20 requirements remain enforced.

## 15. Input and Output Examples

Run from repository root:

```sh
python machine-learning/reinforcement-learning/deep-deterministic-policy-gradient/python/example.py
```

Executed output:

```json
{"action": 1.0, "target_bias": 0.5}
```

Use `support.evaluate(agent,factory)` for separately reset episodes with greedy categorical actions or a noise-free deterministic actor. Multiworker training ordering is not an evaluation seed guarantee.

## 16. Edge Cases

Validate real finite nonempty arrays, exact feature/action shapes, native scalar flags, hyperparameters and resource limits before indexing/updating. Observation/reward magnitudes≤1e6; stable log-softmax subtracts row maxima. NaN/Inf state/outputs raise; gradient clipping cannot rescue a nonfinite computation. No global NumPy RNG mutation. Input/action dimensions≤16,total critic input≤32,hidden≤32; C≤4096,B≤C,episodes≤5000,steps≤256,interactions≤100000,updates≤10000. τ∈(0,1],Gaussian noise std∈[0,2],strict low<high. This is small vector control without OU noise, batch normalization, delayed actors or TD3 twin critics. Function approximation and extrapolation can destabilize learning; arbitrary continuous tasks are unsupported by evidence.

## 17. Advantages

Direct continuous actions avoid enumerating or maximizing a discrete action grid; the critic provides a differentiable actor direction and replay reuses experience.

## 18. Disadvantages and Limitations

Input/action dimensions≤16,total critic input≤32,hidden≤32; C≤4096,B≤C,episodes≤5000,steps≤256,interactions≤100000,updates≤10000. τ∈(0,1],Gaussian noise std∈[0,2],strict low<high. This is small vector control without OU noise, batch normalization, delayed actors or TD3 twin critics. Function approximation and extrapolation can destabilize learning; arbitrary continuous tasks are unsupported by evidence. Fixed-budget-completed means execution ended within a budget, not that the objective converged. Only the reported seeded diagnostics establish local behavior.

## 19. When to Use It

Use for small continuous-action problems with differentiable action-value approximation and controlled replay coverage.

## 20. When Not to Use It

Avoid high-dimensional production control or tasks where the stated estimator, action family or fixed budget is inappropriate.

## 21. Comparison With Related Algorithms

DQN selects a discrete max and has no deterministic actor. DDPG backpropagates Q through continuous actions. PPO is stochastic/on-policy clipped-ratio optimization; DDPG is replay-based and off-policy.

## 22. Interview Questions

Derive the stated objective and its stopped quantities. Why distinguish termination and truncation? Which inputs or snapshots must remain fixed during a numerical gradient check?

## 23. Practice Problems

1. Reproduce the dry run.
2. Derive all output-bias gradients independently.
3. Change an exploration setting and compare separate evaluation.
4. Add a two-step MDP and hand-check bootstrapping before measuring training.

## 24. References

[Lillicrap et al., Continuous control with deep reinforcement learning](https://arxiv.org/abs/1509.02971). The small Gaussian-noise tanh MLP example makes no robotics or benchmark-parity claim.

Verification: Independent bounded actor/critic forward expressions; every actor parameter finite-differenced through a fixed critic; separate critic finite differences; terminal/truncation TD targets;τ0/.2/1 interpolation; replay/noise/clipping/ownership;3 repeated seeded one-step continuous-control trials with separate no-noise evaluation. [Tests](tests/test_python.py) distinguish exact mathematics, stochastic training and concurrency invariants.

## 25. Author Attribution

Maintained by **MD.Khalid Hasan**. [Project](https://github.com/khalidhasan7343/algorithm-atlas),
[MIT License](../../../LICENSE), [contribution policy](../../../CONTRIBUTING.md).
