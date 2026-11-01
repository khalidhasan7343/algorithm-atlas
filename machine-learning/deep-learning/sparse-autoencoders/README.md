# Sparse Autoencoder — L1 hidden-activation penalty

## 1. Algorithm Name

Sparse Autoencoder — L1 hidden-activation penalty

## 2. Overview

Change the learning objective while retaining a genuine encoder bottleneck and decoder.

## 3. Problem Statement

X=(N,p),2<=p<=16; latent_dim k1..15 and k<p. Canonical vanilla AE forward/unpack/initialization are reused without modifying its approved source/API. Encoder p×k,decoder k×p, tanh hidden and linear output.

Encoder bias has shape(k),decoder bias(p); the concatenated parameter vector follows the preserved vanilla unpack convention.

## 4. Why Do We Need This Algorithm?

A bottleneck restricts latent dimension, but does not by itself make individual latent activations small. An explicit L1 activation penalty makes that preference part of the objective and adds a distinct encoder gradient. Small activations are not a guarantee of exact zeros.

## 5. Real-World Applications

Studying the reconstruction-versus-activation tradeoff on small normalized vectors. Sparse representation learning motivates the penalty, but this lesson uses L1 tanh activations rather than a KL target-activation objective or a full sparse-coding solver.

## 6. Core Intuition

Change the learning objective while retaining a genuine encoder bottleneck and decoder.

Normalize A from training rows; Z=tanh(A W1+b1),R=Z W2+b2. L=mean((R-A)²)+sparsity*mean(abs(Z)). Sparsity is an explicit L1 activation objective, not inferred from bottleneck size.

## 7. Prerequisites

Matrix shapes, derivatives/chain rule, floating-point arithmetic and the declared learning objective. Read [B7 contracts](../../../docs/neural-networks-and-deep-learning-conventions.md) and [scope](../../../docs/neural-networks-and-deep-learning-scope.md).

## 8. Step-by-Step Working Process

Decoder gradients use MSE residual D=2(R-A)/(N*p). Hidden upstream adds sparsity*sign(Z)/(N*k) before multiplying tanh derivative1-Z²; use subgradient0 at Z=0. Finite differences avoid zero-activation kinks.

Copy/validate inputs, initialize locally, run bounded CPU gradient updates, and install fitted state only after a finite completed run. Mini-batches are shuffled with a local RNG except full-graph GNN. Defaults epochs100,learning_rate0.1,batch_size16,gradient_clip5 where supported; model-specific architecture controls are stated above. At most10000 updates,20000 parameter values and the common array limits apply. Histories are pre-update minibatch averages; fixed-budget status explicitly does not certify convergence.

## 9. Pseudocode

```text
normalize clean rows; initialize the shared tanh/linear autoencoder core
for each shuffled minibatch X:
  Z = tanh(X@We+be); R = Z@Wd+bd
  loss = mean((R-X)^2) + sparsity*mean(abs(Z))
  backpropagate reconstruction residual through decoder
  add sparsity*sign(Z)/(rows*latent_dim) to the latent adjoint
  multiply by (1-Z*Z), then accumulate encoder weight/bias gradients
  use sign(0)=0 as the declared subgradient; clip and update
encode/decode using the fitted normalization and core parameters
```

## 10. Dry Run

At fixed two-row parameters, adding strength0.2 increases total loss by exactly0.2*mean(abs(Z)); only encoder gradients receive its direct term. Controlled seeded fits at strength0 versus0.2 verify reduced mean absolute latent activation, while reconstruction/sparsity trade off. The executable example below runs fixed-seed training and emits the actual learned outputs and first/final losses; they are recorded in Phase19 evidence rather than invented.

## 11. Time Complexity

Fit O(E*N*p*k), with O(E*N*p) corruption or O(E*N*k) activation penalty. Prediction/encoding/decoding O(q*p*k). Bounded SGD does not guarantee the global reconstruction/sparsity optimum.

## 12. Space Complexity

O(B*(p+k)+p*k) activations/parameters plus O(N*p) copied normalized training input. No autograd graph or model serialization.

## 13. Python Implementation

[SparseAutoencoder source](python/solution.py) contains the actual architecture and analytic gradients. [Example](python/example.py); [tests](tests/test_python.py). Core imports NumPy/stdlib/local primitives only, never a framework estimator. Loss/forward/backward functions take explicit parameter arrays so independent finite differences can freeze all stochastic inputs. Tests independently check this model’s forward equations/objective, every weight and bias by central finite differences with fixed stochastic inputs, controlled training and repeated seeded outputs. Common tests add invalid rank/domain/shape/limits, constant/duplicate rows, global RNG/input copies, finite-state detection and atomic failed refits.

## 14. C++ Implementation

C++ is optional and absent under the Phase19 ML policy. No placeholder source/test. DSA still requires actual Python/C++17/C++20 tests.

## 15. Input and Output Examples

Run the fixed-seed example from the repository root:

```sh
python machine-learning/deep-learning/sparse-autoencoders/python/example.py
```

The equivalent JSON input to `python/solution.py` is:

```json
{"X":[[-1,-0.5],[-0.3,-0.15],[0.3,0.15],[1,0.5]],"parameters":{"latent_dim":1,"epochs":80,"learning_rate":0.2,"batch_size":4}}
```

Observed output in this phase's [executed example records](../../../docs/neural-networks-and-deep-learning-evidence/examples-results.json):

```json
{"loss_initial":0.4130213202577581,"loss_final":0.017961998546944653,"optimization_status":"fixed-budget-completed","embedding":[[0.5176666696381395],[0.17026939375635897],[-0.17026939375635897],[-0.5176666696381395]],"reconstruction":[[-0.9512861666835312,-0.5091760131927574],[-0.3128942394596113,-0.1674766720874918],[0.3128942394596113,0.1674766720874918],[0.9512861666835312,0.5091760131927574]]}
```

Floating-point last digits may vary across numerical environments. Losses describe the actual small training run and its declared reduction; fixed-budget completion does not establish convergence or generalization.

## 16. Edge Cases

The architecture sizes and loss-normalization axes above are part of the API, not inferred by broadcasting. Fitted tensor trailing dimensions must match at inference; unsupported sequence/image/graph forms fail explicitly. One tanh bottleneck/linear decoder, strength0..1, no KL target-rate objective, weight sparsity, hard thresholding or guaranteed exact zeros. Decoder rescaling and nonconvex optimization affect interpretation; an L1 activation penalty alone does not guarantee a uniquely identified representation.

Inputs copy caller arrays and use local default_rng. Reject nonfinite/nonreal arrays, bool data, invalid dimensions/learning rates/batches/seeds, excess compute budgets and inference before fit. Fit commits state only after a complete finite run; invalid/failed refits preserve a prior successful model.

## 17. Advantages

The specific Sparse Autoencoder — L1 hidden-activation penalty forward and reverse equations are visible in a compact NumPy implementation; independent mathematical invariants and per-entry gradients make the mechanism inspectable.

## 18. Disadvantages and Limitations

One tanh bottleneck/linear decoder, strength0..1, no KL target-rate objective, weight sparsity, hard thresholding or guaranteed exact zeros. Decoder rescaling and nonconvex optimization affect interpretation; an L1 activation penalty alone does not guarantee a uniquely identified representation.

## 19. When to Use It

Use for learning and validating the stated Sparse Autoencoder — L1 hidden-activation penalty mechanism on a small controlled CPU dataset.

## 20. When Not to Use It

Use a validated production architecture for large-scale workloads or features excluded by this contract. A short synthetic fit does not establish generalization or generative quality.

## 21. Comparison With Related Algorithms

| Representation | Training objective |
| --- | --- |
| Preserved vanilla AE | Deterministic reconstruction MSE |
| Denoising AE | Corrupted input to clean target MSE |
| Sparse AE | Reconstruction plus explicit L1 latent activation penalty |
| Linear Gaussian VAE | Stochastic reconstruction plus posterior/prior KL |

## 22. Interview Questions

How does this variant differ from vanilla AE? Its displayed corruption/penalty changes the objective and encoder gradients. Why train normalization only on clean training data? It prevents query information from defining the representation. Neither variant is guaranteed to outperform PCA or other autoencoders.

## 23. Practice Problems

Derive the latent adjoint with and without the L1 term. Verify that changing sparsity leaves a fixed-parameter decoder gradient unchanged. Run two seeded fits at strengths0 and0.2 and compare activation magnitude alongside reconstruction error.

## 24. References

[Stanford UFLDL sparse autoencoder tutorial](https://web.stanford.edu/class/cs294a/tutorial) discusses reconstruction regularization; this implementation explicitly selects L1 activation penalty rather than its KL target-activation variant.

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). New Phase19 B7 owner review pending.
