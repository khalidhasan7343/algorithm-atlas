# Long Short-Term Memory

## 1. Algorithm Name

Long Short-Term Memory

## 2. Overview

Carry a trainable state through ordered observations and backpropagate shared parameters through all timesteps.

## 3. Problem Statement

X=(N,T,p),1<=T<=16,p<=16; hidden h1..16; output/y=(N,1). Initial states zero for every row and fit/query. Fitted T,p are fixed.

Parameter shapes: Wx(p,4h),Wh(h,4h),b(4h),Wo(h,1),bo(1); fused gate order i,f,o,g.

## 4. Why Do We Need This Algorithm?

The separate cell state provides an additive temporal path controlled by forget and input gates. Its derivative must carry both cell and hidden adjoints backward; ignoring either loses a genuine dependency. Gates can help retain information, although they do not remove all conditioning problems.

## 5. Real-World Applications

Small sequence experiments in which an earlier value affects the final regression target. LSTMs are also used in larger temporal models, but this lesson implements one modern forget-gated layer and a final-state scalar head.

## 6. Core Intuition

Carry a trainable state through ordered observations and backpropagate shared parameters through all timesteps.

[a_i,a_f,a_o,a_g]=x_t Wx+hprev Wh+b; i/f/o=sigmoid(a),g=tanh(a_g),c=f*cprev+i*g,h=o*tanh(c). Initial h,c are zero; forget bias initializes1, other biases0. Last h gives a scalar MSE head.

## 7. Prerequisites

Matrix shapes, derivatives/chain rule, floating-point arithmetic and the declared learning objective. Read [B7 contracts](../../../docs/neural-networks-and-deep-learning-conventions.md) and [scope](../../../docs/neural-networks-and-deep-learning-scope.md).

## 8. Step-by-Step Working Process

Reverse-time adjoints track both dh and dc. Add dh*o*(1-tanh(c)²) to dc; di=dc*g,df=dc*cprev,do=dh*tanh(c),dg=dc*i. Multiply sigmoid/tanh derivatives, concatenate in i/f/o/g order, accumulate shared matrices/bias, then pass dcprev=dc*f and dhprev=da Wh.T.

Copy/validate inputs, initialize locally, run bounded CPU gradient updates, and install fitted state only after a finite completed run. Mini-batches are shuffled with a local RNG except full-graph GNN. Defaults epochs100,learning_rate0.1,batch_size16,gradient_clip5 where supported; model-specific architecture controls are stated above. At most10000 updates,20000 parameter values and the common array limits apply. Histories are pre-update minibatch averages; fixed-budget status explicitly does not certify convergence.

## 9. Pseudocode

```text
initialize fused i,f,o,g projections; set forget-gate bias to1
for each minibatch:
  start h=0,c=0
  for each timestep:
    i,f,o = sigmoid(three gate projections); g = tanh(candidate projection)
    c = f*c_previous + i*g; h = o*tanh(c); retain gate/cell states
  form final-hidden scalar prediction and MSE head adjoint
  set future cell adjoint dc=0
  reverse timesteps, combining hidden-to-cell and carried dc terms
  differentiate all four gates; accumulate Wx,Wh,b and input adjoints
  carry dc_previous=dc*f and dh_previous through recurrent projection
  clip the combined parameter gradient and update
```

## 10. Dry Run

With zero preactivation gate logits i/f/o=0.5, candidate0.4,zero prior cell and Wo1: c=0.2,h=0.5*tanh0.2. Tests verify gate ranges/cell update and one-/three-step full gradients. The executable example below runs fixed-seed training and emits the actual learned outputs and first/final losses; they are recorded in Phase19 evidence rather than invented.

## 11. Time Complexity

For hidden width h, fit O(E*N*T*(p*h+h²)) with a constant gate factor1(RNN),4(LSTM),3(GRU). Full BPTT and inference are linear in T; no assumption of constant-cost long sequences.

## 12. Space Complexity

O(B*T*h+B*T*p) states/adjoints plus O(p*h+h²+h) parameters with gate-dependent constants. Reverse traversal is iterative, not Python recursion.

## 13. Python Implementation

[LSTMRegressor source](python/solution.py) contains the actual architecture and analytic gradients. [Example](python/example.py); [tests](tests/test_python.py). Core imports NumPy/stdlib/local primitives only, never a framework estimator. Loss/forward/backward functions take explicit parameter arrays so independent finite differences can freeze all stochastic inputs. Tests independently check this model’s forward equations/objective, every weight and bias by central finite differences with fixed stochastic inputs, controlled training and repeated seeded outputs. Common tests add invalid rank/domain/shape/limits, constant/duplicate rows, global RNG/input copies, finite-state detection and atomic failed refits.

## 14. C++ Implementation

C++ is optional and absent under the Phase19 ML policy. No placeholder source/test. DSA still requires actual Python/C++17/C++20 tests.

## 15. Input and Output Examples

Run the fixed-seed example from the repository root:

```sh
python machine-learning/deep-learning/long-short-term-memory/python/example.py
```

The equivalent JSON input to `python/solution.py` is:

```json
{"X":[[[-0.4],[-0.2]],[[-0.2],[0.1]],[[0.1],[0.3]],[[0.4],[0.2]]],"y":[[-0.6],[-0.1],[0.4],[0.6]],"parameters":{"hidden_dim":3,"epochs":100,"learning_rate":0.2,"batch_size":4}}
```

Observed output in this phase's [executed example records](../../../docs/neural-networks-and-deep-learning-evidence/examples-results.json):

```json
{"loss_initial":0.3157256722622744,"loss_final":0.0029670930640217945,"optimization_status":"fixed-budget-completed","prediction":[[-0.5248324521205328],[-0.08865467167693221],[0.3836609581402263],[0.5316748669535045]]}
```

Floating-point last digits may vary across numerical environments. Losses describe the actual small training run and its declared reduction; fixed-budget completion does not establish convergence or generalization.

## 16. Edge Cases

The architecture sizes and loss-normalization axes above are part of the API, not inferred by broadcasting. Fitted tensor trailing dimensions must match at inference; unsupported sequence/image/graph forms fail explicitly. One LSTM layer and scalar last-state regression. No peepholes, projection, learned initial state, padding/masking or truncated BPTT. Cell/hidden paths are distinct; gates can saturate and do not guarantee arbitrary long-term memory.

Inputs copy caller arrays and use local default_rng. Reject nonfinite/nonreal arrays, bool data, invalid dimensions/learning rates/batches/seeds, excess compute budgets and inference before fit. Fit commits state only after a complete finite run; invalid/failed refits preserve a prior successful model.

## 17. Advantages

The specific Long Short-Term Memory forward and reverse equations are visible in a compact NumPy implementation; independent mathematical invariants and per-entry gradients make the mechanism inspectable.

## 18. Disadvantages and Limitations

One LSTM layer and scalar last-state regression. No peepholes, projection, learned initial state, padding/masking or truncated BPTT. Cell/hidden paths are distinct; gates can saturate and do not guarantee arbitrary long-term memory.

## 19. When to Use It

Use for learning and validating the stated Long Short-Term Memory mechanism on a small controlled CPU dataset.

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

With gates i=f=o=0.5 and candidate0.4, compute the first cell and hidden state from zeros. Derive the carried cell adjoint for two steps. Remove the forget contribution on paper and identify which finite-difference comparison would fail.

## 24. References

[Hochreiter and Schmidhuber, Long Short-Term Memory](https://doi.org/10.1162/neco.1997.9.8.1735).

The implemented modern forget-gated form also follows [Gers, Schmidhuber and Cummins, Learning to Forget](https://doi.org/10.1162/089976600300015015).

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). New Phase19 B7 owner review pending.
