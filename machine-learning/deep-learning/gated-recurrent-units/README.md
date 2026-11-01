# Gated Recurrent Unit — reset-before-matrix

## 1. Algorithm Name

Gated Recurrent Unit — reset-before-matrix

## 2. Overview

Carry a trainable state through ordered observations and backpropagate shared parameters through all timesteps.

## 3. Problem Statement

X=(N,T,p),1<=T<=16,p<=16; hidden h1..16; output/y=(N,1). Initial states zero for every row and fit/query. Fitted T,p are fixed.

For each r,z,g: W(p,h),U(h,h),b(h); output Wo(h,1),bo(1). Reset-before-matrix is fixed.

## 4. Why Do We Need This Algorithm?

The update gate interpolates between a retained state and a new candidate, while the reset gate changes how the old state enters that candidate. GRUs offer a gated recurrence without a separate LSTM cell. Reset placement changes the actual model and derivative, so this variant specifies it precisely.

## 5. Real-World Applications

Inspecting short-sequence regression and gate-controlled state retention with fewer gate blocks than an LSTM. This compact reset-before-matrix variant is not assumed identical to every framework GRU configuration.

## 6. Core Intuition

Carry a trainable state through ordered observations and backpropagate shared parameters through all timesteps.

r=sigmoid(x Wr+hprev Ur+br),z=sigmoid(x Wz+hprev Uz+bz),g=tanh(x Wg+(r*hprev) Ug+bg),h=z*hprev+(1-z)*g. Initial h0=0; scalar MSE head uses final h.

## 7. Prerequisites

Matrix shapes, derivatives/chain rule, floating-point arithmetic and the declared learning objective. Read [B7 contracts](../../../docs/neural-networks-and-deep-learning-conventions.md) and [scope](../../../docs/neural-networks-and-deep-learning-scope.md).

## 8. Step-by-Step Working Process

For upstream dh: dg=dh*(1-z),dz=dh*(hprev-g),direct dhprev=dh*z. Backpropagate dg through tanh and Ug into r*hprev; split product into reset and previous-state terms. Backpropagate both gate sigmoids and accumulate all W/U/b across time, adding every dhprev contribution.

Copy/validate inputs, initialize locally, run bounded CPU gradient updates, and install fitted state only after a finite completed run. Mini-batches are shuffled with a local RNG except full-graph GNN. Defaults epochs100,learning_rate0.1,batch_size16,gradient_clip5 where supported; model-specific architecture controls are stated above. At most10000 updates,20000 parameter values and the common array limits apply. Histories are pre-update minibatch averages; fixed-budget status explicitly does not certify convergence.

## 9. Pseudocode

```text
initialize reset, update, candidate and scalar-head parameters
for each minibatch, start h=0:
  for each timestep:
    r = sigmoid(x@Wr+h_previous@Ur+br)
    z = sigmoid(x@Wz+h_previous@Uz+bz)
    g = tanh(x@Wg+(r*h_previous)@Ug+bg)
    h = z*h_previous+(1-z)*g; retain the states
  backpropagate scalar MSE through the final state
  reverse timesteps: split dh into retained, update-gate and candidate paths
  differentiate candidate through both r and h_previous before Ug
  accumulate all shared weight/bias and input gradients
  clip gradients and update only after all timestep contributions are summed
```

## 10. Dry Run

With reset/update logits0, candidate bias0.4,Ug0.7,zero input/state and Wo1: h1=0.5*tanh0.4; h2=0.5*h1+0.5*tanh(0.4+0.5*h1*0.7). Tests verify this exact variant and all recurrent/input gradients. The executable example below runs fixed-seed training and emits the actual learned outputs and first/final losses; they are recorded in Phase19 evidence rather than invented.

## 11. Time Complexity

For hidden width h, fit O(E*N*T*(p*h+h²)) with a constant gate factor1(RNN),4(LSTM),3(GRU). Full BPTT and inference are linear in T; no assumption of constant-cost long sequences.

## 12. Space Complexity

O(B*T*h+B*T*p) states/adjoints plus O(p*h+h²+h) parameters with gate-dependent constants. Reverse traversal is iterative, not Python recursion.

## 13. Python Implementation

[GRURegressor source](python/solution.py) contains the actual architecture and analytic gradients. [Example](python/example.py); [tests](tests/test_python.py). Core imports NumPy/stdlib/local primitives only, never a framework estimator. Loss/forward/backward functions take explicit parameter arrays so independent finite differences can freeze all stochastic inputs. Tests independently check this model’s forward equations/objective, every weight and bias by central finite differences with fixed stochastic inputs, controlled training and repeated seeded outputs. Common tests add invalid rank/domain/shape/limits, constant/duplicate rows, global RNG/input copies, finite-state detection and atomic failed refits.

## 14. C++ Implementation

C++ is optional and absent under the Phase19 ML policy. No placeholder source/test. DSA still requires actual Python/C++17/C++20 tests.

## 15. Input and Output Examples

Run the fixed-seed example from the repository root:

```sh
python machine-learning/deep-learning/gated-recurrent-units/python/example.py
```

The equivalent JSON input to `python/solution.py` is:

```json
{"X":[[[-0.4],[-0.2]],[[-0.2],[0.1]],[[0.1],[0.3]],[[0.4],[0.2]]],"y":[[-0.6],[-0.1],[0.4],[0.6]],"parameters":{"hidden_dim":3,"epochs":100,"learning_rate":0.2,"batch_size":4}}
```

Observed output in this phase's [executed example records](../../../docs/neural-networks-and-deep-learning-evidence/examples-results.json):

```json
{"loss_initial":0.31359343879124046,"loss_final":0.08837074825451544,"optimization_status":"fixed-budget-completed","prediction":[[-0.17121830182030673],[0.02985364249025943],[0.23396585433124947],[0.26801670860826876]]}
```

Floating-point last digits may vary across numerical environments. Losses describe the actual small training run and its declared reduction; fixed-budget completion does not establish convergence or generalization.

## 16. Edge Cases

The architecture sizes and loss-normalization axes above are part of the API, not inferred by broadcasting. Fitted tensor trailing dimensions must match at inference; unsupported sequence/image/graph forms fail explicitly. Reset gate acts before the candidate recurrent matrix; h=z*old+(1-z)*candidate. Other libraries may put reset after the matrix or reverse update convention. No incompatible raw-parameter parity, padding, stateful inference or bidirectionality is claimed.

Inputs copy caller arrays and use local default_rng. Reject nonfinite/nonreal arrays, bool data, invalid dimensions/learning rates/batches/seeds, excess compute budgets and inference before fit. Fit commits state only after a complete finite run; invalid/failed refits preserve a prior successful model.

## 17. Advantages

The specific Gated Recurrent Unit — reset-before-matrix forward and reverse equations are visible in a compact NumPy implementation; independent mathematical invariants and per-entry gradients make the mechanism inspectable.

## 18. Disadvantages and Limitations

Reset gate acts before the candidate recurrent matrix; h=z*old+(1-z)*candidate. Other libraries may put reset after the matrix or reverse update convention. No incompatible raw-parameter parity, padding, stateful inference or bidirectionality is claimed.

## 19. When to Use It

Use for learning and validating the stated Gated Recurrent Unit — reset-before-matrix mechanism on a small controlled CPU dataset.

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

Compute two scalar GRU steps for the documented fixture. Compare (r*h)@Ug with r*(h@Ug) for a non-diagonal Ug: explain why they differ. Derive the direct z*dh path into the previous state.

## 24. References

[Cho et al., Learning Phrase Representations using RNN Encoder-Decoder](https://arxiv.org/abs/1406.1078).

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). New Phase19 B7 owner review pending.
