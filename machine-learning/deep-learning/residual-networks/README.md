# Residual Network — compact identity block

## 1. Algorithm Name

Residual Network — compact identity block

## 2. Overview

Learn a correction to an existing representation and preserve a direct path through addition.

## 3. Problem Statement

X=(N,p),p<=16; W1=(p,h),W2=(h,p),Wout=(p,1). Identity skip requires residual output exactly X.shape; y=(N,1).

Bias shapes: b1(h),b2(p),bout(1); the identity branch has no trainable parameters.

## 4. Why Do We Need This Algorithm?

A plain nonlinear block makes both information and gradients pass through its learned transformation. Adding the input gives the block an exact identity route; a zero residual can preserve the input rather than learning an identity through tanh. It improves the available gradient routes without guaranteeing successful optimization.

## 5. Real-World Applications

Inspecting identity preservation and gradient splitting in a tiny tabular regressor. Deep residual architectures are useful in vision and other domains; this one-block numerical model demonstrates their skip mechanism without claiming to reproduce an image ResNet.

## 6. Core Intuition

Learn a correction to an existing representation and preserve a direct path through addition.

H=tanh(X W1+b1), F=H W2+b2, Z=X+F, R=Z Wout+bout, L=mean((R-y)²). Identity shortcut only; no projection shortcut.

## 7. Prerequisites

Matrix shapes, derivatives/chain rule, floating-point arithmetic and the declared learning objective. Read [B7 contracts](../../../docs/neural-networks-and-deep-learning-conventions.md) and [scope](../../../docs/neural-networks-and-deep-learning-scope.md).

## 8. Step-by-Step Working Process

D=2(R-y)/N,dZ=D Wout.T. Both paths receive dZ: dF=dZ and direct dXskip=dZ. Hidden preactivation adjoint=(dZ W2.T)*(1-H²). Accumulate dW2=H.T dZ,dW1=X.T dH and biases; total dX=dZ+dH W1.T.

Copy/validate inputs, initialize locally, run bounded CPU gradient updates, and install fitted state only after a finite completed run. Mini-batches are shuffled with a local RNG except full-graph GNN. Defaults epochs100,learning_rate0.1,batch_size16,gradient_clip5 where supported; model-specific architecture controls are stated above. At most10000 updates,20000 parameter values and the common array limits apply. Histories are pre-update minibatch averages; fixed-budget status explicitly does not certify convergence.

## 9. Pseudocode

```text
initialize W1,b1,W2,b2 and scalar output head
for each shuffled minibatch:
  H = tanh(X@W1+b1); Z = X + H@W2+b2; R = Z@Wout+bout
  D = 2*(R-y)/batch_rows; compute output-head gradients
  G = D@Wout.T; dW2 = H.T@G; db2 = sum_rows(G)
  A = (G@W2.T)*(1-H*H); dW1 = X.T@A; db1 = sum_rows(A)
  input_adjoint = G + A@W1.T
  clip parameter gradients and update; do not update the identity route
```

## 10. Dry Run

With zero residual weights/biases and Wout=(1,1), inputs(1,2),(-1,0.5) produce3,-0.5. Unit output adjoints give input gradients(1,1) through the shortcut, even though the residual branch is zero. A separate nonlinear fixture checks all parameter and input gradients. The executable example below runs fixed-seed training and emits the actual learned outputs and first/final losses; they are recorded in Phase19 evidence rather than invented.

## 11. Time Complexity

Fit O(E*N*p*h); scalar head O(E*N*p), prediction O(q*p*h). A single residual block has no depth-scaling claim.

## 12. Space Complexity

O(B*(p+h)) activations plus O(p*h+p) parameters; skip adds O(B*p) state, no recursion.

## 13. Python Implementation

[ResidualRegressor source](python/solution.py) contains the actual architecture and analytic gradients. [Example](python/example.py); [tests](tests/test_python.py). Core imports NumPy/stdlib/local primitives only, never a framework estimator. Loss/forward/backward functions take explicit parameter arrays so independent finite differences can freeze all stochastic inputs. Tests independently check this model’s forward equations/objective, every weight and bias by central finite differences with fixed stochastic inputs, controlled training and repeated seeded outputs. Common tests add invalid rank/domain/shape/limits, constant/duplicate rows, global RNG/input copies, finite-state detection and atomic failed refits.

## 14. C++ Implementation

C++ is optional and absent under the Phase19 ML policy. No placeholder source/test. DSA still requires actual Python/C++17/C++20 tests.

## 15. Input and Output Examples

Run the fixed-seed example from the repository root:

```sh
python machine-learning/deep-learning/residual-networks/python/example.py
```

The equivalent JSON input to `python/solution.py` is:

```json
{"X":[[-1,-0.5],[-0.2,-0.1],[0.3,0.1],[1,0.5]],"y":[[-1.5],[-0.3],[0.4],[1.5]],"parameters":{"hidden_dim":3,"epochs":80,"batch_size":4}}
```

Observed output in this phase's [executed example records](../../../docs/neural-networks-and-deep-learning-evidence/examples-results.json):

```json
{"loss_initial":6.725661119716871,"loss_final":0.009262194597573329,"optimization_status":"fixed-budget-completed","prediction":[[-1.4579416894060766],[-0.42460268529151485],[0.5309087109466318],[1.4517787867708603]]}
```

Floating-point last digits may vary across numerical environments. Losses describe the actual small training run and its declared reduction; fixed-budget completion does not establish convergence or generalization.

## 16. Edge Cases

The architecture sizes and loss-normalization axes above are part of the API, not inferred by broadcasting. Fitted tensor trailing dimensions must match at inference; unsupported sequence/image/graph forms fail explicitly. One fully connected tanh residual block, scalar regression, no convolutional stack, batch normalization, learned projection shortcut or ImageNet architecture. Shortcut and residual must match shape exactly.

Inputs copy caller arrays and use local default_rng. Reject nonfinite/nonreal arrays, bool data, invalid dimensions/learning rates/batches/seeds, excess compute budgets and inference before fit. Fit commits state only after a complete finite run; invalid/failed refits preserve a prior successful model.

## 17. Advantages

The specific Residual Network — compact identity block forward and reverse equations are visible in a compact NumPy implementation; independent mathematical invariants and per-entry gradients make the mechanism inspectable.

## 18. Disadvantages and Limitations

One fully connected tanh residual block, scalar regression, no convolutional stack, batch normalization, learned projection shortcut or ImageNet architecture. Shortcut and residual must match shape exactly.

## 19. When to Use It

Use for learning and validating the stated Residual Network — compact identity block mechanism on a small controlled CPU dataset.

## 20. When Not to Use It

Use a validated production architecture for large-scale workloads or features excluded by this contract. A short synthetic fit does not establish generalization or generative quality.

## 21. Comparison With Related Algorithms

| Model | Forward/gradient path |
| --- | --- |
| This residual model | X+F(X),with direct identity adjoint |
| Ordinary MLP | All feature gradients pass through learned nonlinear layers |
| CNN | Spatially shared kernels; a CNN may separately include residual blocks |

## 22. Interview Questions

Why does dX have two terms? Addition sends the same adjoint down both branches. Compared with an ordinary MLP, the identity path remains when the residual transform is zero; that does not guarantee every deep optimization succeeds.

## 23. Practice Problems

Set the learned residual output to zero and verify Z=X. Derive the identity and nonlinear terms in the input gradient separately. Compare the two terms numerically when tanh saturates, while keeping the scalar head fixed.

## 24. References

[He et al., Deep Residual Learning for Image Recognition](https://arxiv.org/abs/1512.03385). This compact residual block is not their production image network.

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). New Phase19 B7 owner review pending.
