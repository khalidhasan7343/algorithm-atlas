# Vanilla Recurrent Neural Network

## 1. Algorithm Name

Vanilla Recurrent Neural Network

## 2. Overview

Carry a trainable state through ordered observations and backpropagate shared parameters through all timesteps.

## 3. Problem Statement

X=(N,T,p),1<=T<=16,p<=16; hidden h1..16; output/y=(N,1). Initial states zero for every row and fit/query. Fitted T,p are fixed.

Parameter shapes: Wx(p,h),Wh(h,h),b(h),Wo(h,1),bo(1).

## 4. Why Do We Need This Algorithm?

A fixed-width state lets the same learned transition process every position while retaining information from earlier inputs. Sharing recurrent weights changes backpropagation: their gradient must sum contributions from every timestep rather than only the last state.

## 5. Real-World Applications

Short synthetic sequence regression such as a scalar function of earlier and later values. Time-series and sequence modeling motivate recurrence, but variable-length padding, streaming state persistence and autoregressive generation are outside this contract.

## 6. Core Intuition

Carry a trainable state through ordered observations and backpropagate shared parameters through all timesteps.

h_t=tanh(x_t Wx+h_(t-1) Wh+b),h_0=0; R=h_T Wo+bo. L=mean((R-y)²). Parameters are shared across every timestep.

## 7. Prerequisites

Matrix shapes, derivatives/chain rule, floating-point arithmetic and the declared learning objective. Read [B7 contracts](../../../docs/neural-networks-and-deep-learning-conventions.md) and [scope](../../../docs/neural-networks-and-deep-learning-scope.md).

## 8. Step-by-Step Working Process

Starting at d h_T=D Wo.T, traverse all timesteps backwards. dz_t=dh_t*(1-h_t²); add x_t.T dz_t to dWx,h_(t-1).T dz_t to dWh and sum dz_t to db. Propagate dh_(t-1)=dz_t Wh.T and dx_t=dz_t Wx.T. Output weights/bias receive h_T.T D and sum D.

Copy/validate inputs, initialize locally, run bounded CPU gradient updates, and install fitted state only after a finite completed run. Mini-batches are shuffled with a local RNG except full-graph GNN. Defaults epochs100,learning_rate0.1,batch_size16,gradient_clip5 where supported; model-specific architecture controls are stated above. At most10000 updates,20000 parameter values and the common array limits apply. Histories are pre-update minibatch averages; fixed-budget status explicitly does not certify convergence.

## 9. Pseudocode

```text
initialize input/recurrent matrices and final-state scalar head
for each sequence minibatch:
  h[0] = zeros
  for t in chronological order: h[t+1] = tanh(x[t]@Wx+h[t]@Wh+b)
  R = h[T]@Wo+bo; initialize dh from mean squared output loss
  zero all accumulated parameter gradients
  for t in reverse order:
    a = dh*(1-h[t+1]*h[t+1])
    accumulate x[t].T@a, h[t].T@a and sum_rows(a)
    dx[t] = a@Wx.T; dh = a@Wh.T
  clip all accumulated gradients and take one SGD step
```

## 10. Dry Run

For scalar Wx0.5,Wh0.2,b0,Wo1 and sequence(1,2), first hidden=tanh0.5 and final hidden=tanh(1+0.2*tanh0.5); output equals that final hidden. One- and three-step fixtures verify every shared-weight and input adjoint. The executable example below runs fixed-seed training and emits the actual learned outputs and first/final losses; they are recorded in Phase19 evidence rather than invented.

## 11. Time Complexity

For hidden width h, fit O(E*N*T*(p*h+h²)) with a constant gate factor1(RNN),4(LSTM),3(GRU). Full BPTT and inference are linear in T; no assumption of constant-cost long sequences.

## 12. Space Complexity

O(B*T*h+B*T*p) states/adjoints plus O(p*h+h²+h) parameters with gate-dependent constants. Reverse traversal is iterative, not Python recursion.

## 13. Python Implementation

[RNNRegressor source](python/solution.py) contains the actual architecture and analytic gradients. [Example](python/example.py); [tests](tests/test_python.py). Core imports NumPy/stdlib/local primitives only, never a framework estimator. Loss/forward/backward functions take explicit parameter arrays so independent finite differences can freeze all stochastic inputs. Tests independently check this model’s forward equations/objective, every weight and bias by central finite differences with fixed stochastic inputs, controlled training and repeated seeded outputs. Common tests add invalid rank/domain/shape/limits, constant/duplicate rows, global RNG/input copies, finite-state detection and atomic failed refits.

## 14. C++ Implementation

C++ is optional and absent under the Phase19 ML policy. No placeholder source/test. DSA still requires actual Python/C++17/C++20 tests.

## 15. Input and Output Examples

Run the fixed-seed example from the repository root:

```sh
python machine-learning/deep-learning/recurrent-neural-networks/python/example.py
```

The equivalent JSON input to `python/solution.py` is:

```json
{"X":[[[-0.4],[-0.2]],[[-0.2],[0.1]],[[0.1],[0.3]],[[0.4],[0.2]]],"y":[[-0.6],[-0.1],[0.4],[0.6]],"parameters":{"hidden_dim":3,"epochs":100,"learning_rate":0.2,"batch_size":4}}
```

Observed output in this phase's [executed example records](../../../docs/neural-networks-and-deep-learning-evidence/examples-results.json):

```json
{"loss_initial":0.1678538357949367,"loss_final":0.00046930482258646013,"optimization_status":"fixed-budget-completed","prediction":[[-0.5794483724893962],[-0.11950665829112889],[0.37921207189341777],[0.624150923573983]]}
```

Floating-point last digits may vary across numerical environments. Losses describe the actual small training run and its declared reduction; fixed-budget completion does not establish convergence or generalization.

## 16. Edge Cases

The architecture sizes and loss-normalization axes above are part of the API, not inferred by broadcasting. Fitted tensor trailing dimensions must match at inference; unsupported sequence/image/graph forms fail explicitly. Vanilla tanh recurrence with one scalar last-state regression head. Full untruncated BPTT, fixed fitted length, no padding/stateful streaming/bidirectionality. Repeated Jacobians can vanish or explode; clipping bounds update norm but does not restore vanished information.

Inputs copy caller arrays and use local default_rng. Reject nonfinite/nonreal arrays, bool data, invalid dimensions/learning rates/batches/seeds, excess compute budgets and inference before fit. Fit commits state only after a complete finite run; invalid/failed refits preserve a prior successful model.

## 17. Advantages

The specific Vanilla Recurrent Neural Network forward and reverse equations are visible in a compact NumPy implementation; independent mathematical invariants and per-entry gradients make the mechanism inspectable.

## 18. Disadvantages and Limitations

Vanilla tanh recurrence with one scalar last-state regression head. Full untruncated BPTT, fixed fitted length, no padding/stateful streaming/bidirectionality. Repeated Jacobians can vanish or explode; clipping bounds update norm but does not restore vanished information.

## 19. When to Use It

Use for learning and validating the stated Vanilla Recurrent Neural Network mechanism on a small controlled CPU dataset.

## 20. When Not to Use It

Use a validated production architecture for large-scale workloads or features excluded by this contract. A short synthetic fit does not establish generalization or generative quality.

## 21. Comparison With Related Algorithms

| Model | State mechanism |
| --- | --- |
| Vanilla RNN | One tanh hidden recurrence |
| LSTM | Separate cell/hidden states with input/forget/output gates |
| Reset-before GRU | Reset/update gates and interpolated hidden state |
| Transformer | Masked pairwise attention instead of recurrent state |

## 22. Interview Questions

Why share parameters over time? The same recurrence models each step, so gradients add. How do vanishing/exploding paths arise? They multiply recurrent Jacobians. RNN has one hidden path; LSTM adds a separate cell; GRU gates one interpolated hidden state.

## 23. Practice Problems

Expand a two-step scalar recurrence and identify both uses of Wh in its derivative. Repeat the fixed-noise-free gradient check at lengths1 and3. Construct two sequences with the same final input and different prefixes to test whether the fitted state uses history.

## 24. References

[Elman, Finding Structure in Time](https://doi.org/10.1207/s15516709cog1402_1).

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). New Phase19 B7 owner review pending.
