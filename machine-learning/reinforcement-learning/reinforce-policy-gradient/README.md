# REINFORCE Policy Gradient

## 1. Algorithm Name

REINFORCE Policy Gradient — episodic on-policy Monte Carlo policy gradient.

## 2. Overview

Increase log-probabilities of sampled actions weighted by discounted reward-to-go. Gradient descent on the negative surrogate is ascent in its sampled return direction. No critic or baseline is present.

## 3. Problem Statement

Learn from an MDP (states/observations s, finite actions a, transition law P, scalar reward r, discount γ). Input observations have shape(d,), training matrices(N,d), action indices(N,). A trajectory ends at true termination or a time limit; only true termination implies zero future value. J(θ)=E[Σ_t γ^t r_t]. Reward-to-go G_t=Σ_{k=t}^{T−1}γ^(k−t)r_k. Minimize L=−Σ_t[γ^t G_t log πθ(a_t|s_t)], treating sampled G_t as fixed. The episodic sum avoids an unintended trajectory-length-dependent scaling.

## 4. Why Do We Need This Algorithm?

Use episodic on-policy Monte Carlo policy gradient when its estimator matches the information available. Increase log-probabilities of sampled actions weighted by discounted reward-to-go. Gradient descent on the negative surrogate is ascent in its sampled return direction. No critic or baseline is present.

## 5. Real-World Applications

Diagnostic control with small numerical state descriptions: teaching reward-based decision learning, validating exploration and checking gradients before scaling. The included one-step Bandit exposes observation[1], actions0/1 and rewards0/1; it establishes component correctness, not benchmark performance.

## 6. Core Intuition

J(θ)=E[Σ_t γ^t r_t]. Reward-to-go G_t=Σ_{k=t}^{T−1}γ^(k−t)r_k. Minimize L=−Σ_t[γ^t G_t log πθ(a_t|s_t)], treating sampled G_t as fixed. The episodic sum avoids an unintended trajectory-length-dependent scaling.

The shared network is H=tanh(XW1+b1), output=HW2+b2. For an output adjoint D, dW2=HᵀD, db2=ΣD; dH=(DW2ᵀ)⊙(1−H²); dW1=XᵀdH, db1=ΣdH. The canonical objective supplies D analytically.

## 7. Prerequisites

MDPs, discounted returns, vector calculus, SGD, stable log probabilities and the [tabular lessons](../q-learning/README.md). See [RL contracts](../../../docs/reinforcement-learning-conventions.md) for termination and shapes.

## 8. Step-by-Step Working Process

Collect a complete terminal episode from the current categorical softmax actor; compute reverse discounted returns; multiply each by γ^t; backpropagate the negative weighted log probability; clip norm at10 and apply one SGD update. Reject a truncated/budget-cut episode instead of pretending its incomplete Monte Carlo return is exact.

Updates are bounded diagnostics, not convergence certificates. Loss histories record pre-update sampled objectives. Mathematical correctness is established independently from noisy training returns.

## 9. Pseudocode

```text
for each bounded episode:
    trajectory = sample actor until true termination
    reject if time limit or caller budget cuts trajectory
    G = 0
    for t in reverse trajectory order: G[t] = r[t] + gamma * G[t+1]
    weights[t] = gamma**t * G[t]
    loss = -sum(weights * log_policy_of_taken_actions)
    actor -= learning_rate * clipped(analytic_gradient(loss))
```

## 10. Dry Run

A zero-parameter two-action actor assigns probability.5 to both actions. For observation[1], sampled action1 and return1, loss=log2=0.6931471805599453 and logit/bias gradient=[.5,−.5]. Rewards[1,2,3] with γ=.5 give reward-to-go[2.75,3.5,3].

## 11. Time Complexity

Let P be actor parameters, T episode length, E episodes and A actions. Collection/backpropagation O(ET(P+A)); reverse returns O(ET). Each episode performs one full-trajectory update; no replay or target synchronization.

## 12. Space Complexity

O(P+T(d+A+h)+E) for actor, one trajectory with d features/h hidden units and episode histories. No critic, target network or replay memory.

## 13. Python Implementation

[Source](python/solution.py). REINFORCE(inputs=1,n_actions=2,hidden=8,learning_rate=.05,gamma=.9,seed=0); `train(env,episodes,max_steps)` and `action(observation,explore=True)`. `actor`, loss_history_ and returns_ expose the actual state. `loss_gradients` accepts fixed returns. Shared [support](../support.py) owns explicit tanh dense forward/backward primitives, validation and environments; no estimator/autodiff library is called. Parameters initialize from a local Generator; all arrays are float64.

## 14. C++ Implementation

Optional ML C++ is absent; no fake implementation. DSA still requires Python and C++17/C++20.

## 15. Input and Output Examples

From repository root:

```sh
python machine-learning/reinforcement-learning/reinforce-policy-gradient/python/example.py
```

Executed output:

```json
{"loss": 0.6931471805599453, "bias_gradient": [0.5, -0.5]}
```

Training tests use separately reset greedy evaluation episodes through `support.evaluate`; exploration is disabled during that evaluation.

## 16. Edge Cases

Reject nonfinite/complex/bool observations, wrong shapes, invalid actions, empty batches, invalid hyperparameters and oversized budgets. Stable tanh and shifted log-softmax avoid exp overflow. Reward/observation magnitudes≤1e6; dimensions/hidden/actions≤32, interactions≤100000, episodes≤5000,max_steps≤256. Partial episodes fail explicitly; zero/negative returns remain valid surrogate weights.

## 17. Advantages

Increase log-probabilities of sampled actions weighted by discounted reward-to-go. Gradient descent on the negative surrogate is ascent in its sampled return direction. No critic or baseline is present.

## 18. Disadvantages and Limitations

High-variance no-baseline episodic estimator; requires truly complete terminal episodes. No continuing-task/truncation estimator or guaranteed monotonic improvement. Gradient clipping cannot guarantee stable learning or repair poor reward scaling. Float64 rounding and stochastic exploration limit reproducibility across platforms.

## 19. When to Use It

Small episodic finite-action tasks with affordable terminal rollouts and inspectable policy gradients.

## 20. When Not to Use It

Long-horizon continuing environments, partial trajectories or tasks needing replay sample efficiency.

## 21. Comparison With Related Algorithms

A2C learns a critic and subtracts its value; REINFORCE here uses complete Monte Carlo returns and no baseline. DQN learns action values and uses off-policy replay.

## 22. Interview Questions

Why is log-softmax stable? Why freeze sampled returns in backpropagation? Why include γ^t for the stated discounted objective? How does a critic reduce variance?

## 23. Practice Problems

Derive the two-action logit gradient; verify a three-reward return by hand; measure sampling frequencies; add a state-independent baseline in a separate experiment and derive its effect.

## 24. References

[Sutton and Barto, Reinforcement Learning: An Introduction](https://www.incompleteideas.net/book/bookdraft2018mar21.pdf), chapter13, episodic policy gradient and REINFORCE.

Verification: Analytical log-softmax/bias gradient, independently expressed discounted surrogate finite differences, complete-episode rejection, uniform sampling, local RNG preservation and3 repeated seeded training/evaluation trials. Tests are in [tests/test_python.py](tests/test_python.py).

## 25. Author Attribution

Maintained by **MD.Khalid Hasan**. [Project](https://github.com/khalidhasan7343/algorithm-atlas),
[MIT License](../../../LICENSE), [contribution policy](../../../CONTRIBUTING.md).
