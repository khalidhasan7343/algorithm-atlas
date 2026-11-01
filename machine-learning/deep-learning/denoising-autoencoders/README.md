# Denoising Autoencoder — Gaussian corruption

## 1. Algorithm Name

Denoising Autoencoder — Gaussian corruption

## 2. Overview

Change the learning objective while retaining a genuine encoder bottleneck and decoder.

## 3. Problem Statement

X=(N,p),2<=p<=16; latent_dim k1..15 and k<p. Canonical vanilla AE forward/unpack/initialization are reused without modifying its approved source/API. Encoder p×k,decoder k×p, tanh hidden and linear output.

Encoder bias has shape(k),decoder bias(p); the concatenated parameter vector follows the preserved vanilla unpack convention.

## 4. Why Do We Need This Algorithm?

Training an autoencoder only to copy its input does not explicitly teach robustness to corruption. Here the encoder sees a noisy input while the loss compares reconstruction with the original clean target. That distinction changes both the task and the gradient target.

## 5. Real-World Applications

Denoising small numerical vectors sampled around a low-dimensional synthetic signal. It can illustrate representation robustness, but real sensor noise, structured missingness and images require task-specific corruption and evaluation beyond this Gaussian example.

## 6. Core Intuition

Change the learning objective while retaining a genuine encoder bottleneck and decoder.

Normalize clean A=(X-training_mean)/scale. Corrupt input Atilde=A+noise_std*epsilon with fresh local Gaussian noise per minibatch. Z=tanh(Atilde W1+b1),R=Z W2+b2; objective mean((R-A)²), targeting clean A.

## 7. Prerequisites

Matrix shapes, derivatives/chain rule, floating-point arithmetic and the declared learning objective. Read [B7 contracts](../../../docs/neural-networks-and-deep-learning-conventions.md) and [scope](../../../docs/neural-networks-and-deep-learning-scope.md).

## 8. Step-by-Step Working Process

D=2(R-A)/(N*p),dW2=Z.T D,db2=sum D; G=(D W2.T)*(1-Z²),dW1=Atilde.T G,db1=sum G. Corruption is fixed when checking gradients; noise is not differentiated and clean targets are never replaced by corrupted inputs.

Copy/validate inputs, initialize locally, run bounded CPU gradient updates, and install fitted state only after a finite completed run. Mini-batches are shuffled with a local RNG except full-graph GNN. Defaults epochs100,learning_rate0.1,batch_size16,gradient_clip5 where supported; model-specific architecture controls are stated above. At most10000 updates,20000 parameter values and the common array limits apply. Histories are pre-update minibatch averages; fixed-budget status explicitly does not certify convergence.

## 9. Pseudocode

```text
fit and retain the clean-data normalization; initialize the approved tanh/linear core
for each shuffled minibatch of normalized clean rows C:
  draw fresh local Gaussian noise; U = C + noise_std*noise
  Z = tanh(U@We+be); R = Z@Wd+bd
  loss = mean((R-C)^2); D = 2*(R-C)/(rows*features)
  compute decoder gradients, then encoder gradients using U as input
  clip the parameter gradient and update the packed core parameters
at inference, encode the supplied noisy rows and undo normalization after decoding
```

## 10. Dry Run

A two-row fixed-corruption fixture independently computes R and mean((R-clean)²), which differs from reconstructing corrupted input. Controlled seeded line data with Gaussian noise0.2 has lower reconstructed-clean error than the raw-noisy baseline after the executed training test. The executable example below runs fixed-seed training and emits the actual learned outputs and first/final losses; they are recorded in Phase19 evidence rather than invented.

## 11. Time Complexity

Fit O(E*N*p*k), with O(E*N*p) corruption or O(E*N*k) activation penalty. Prediction/encoding/decoding O(q*p*k). Bounded SGD does not guarantee the global reconstruction/sparsity optimum.

## 12. Space Complexity

O(B*(p+k)+p*k) activations/parameters plus O(N*p) copied normalized training input. No autograd graph or model serialization.

## 13. Python Implementation

[DenoisingAutoencoder source](python/solution.py) contains the actual architecture and analytic gradients. [Example](python/example.py); [tests](tests/test_python.py). Core imports NumPy/stdlib/local primitives only, never a framework estimator. Loss/forward/backward functions take explicit parameter arrays so independent finite differences can freeze all stochastic inputs. Tests independently check this model’s forward equations/objective, every weight and bias by central finite differences with fixed stochastic inputs, controlled training and repeated seeded outputs. Common tests add invalid rank/domain/shape/limits, constant/duplicate rows, global RNG/input copies, finite-state detection and atomic failed refits.

## 14. C++ Implementation

C++ is optional and absent under the Phase19 ML policy. No placeholder source/test. DSA still requires actual Python/C++17/C++20 tests.

## 15. Input and Output Examples

Run the fixed-seed example from the repository root:

```sh
python machine-learning/deep-learning/denoising-autoencoders/python/example.py
```

The equivalent JSON input to `python/solution.py` is:

```json
{"X":[[-1,-0.5],[-0.3,-0.15],[0.3,0.15],[1,0.5]],"parameters":{"latent_dim":1,"epochs":80,"learning_rate":0.2,"batch_size":4}}
```

Observed output in this phase's [executed example records](../../../docs/neural-networks-and-deep-learning-evidence/examples-results.json):

```json
{"loss_initial":0.4725115064980791,"loss_final":0.006216973351496903,"optimization_status":"fixed-budget-completed","embedding":[[0.609887156596086],[0.21387235939421964],[-0.2012869255062744],[-0.6015606655721628]],"reconstruction":[[-0.9965489582461585,-0.5205428085211561],[-0.35469850828095695,-0.18529007174773862],[0.31818082780299684,0.16616974097445528],[0.9669340612322597,0.5050279547679579]]}
```

Floating-point last digits may vary across numerical environments. Losses describe the actual small training run and its declared reduction; fixed-budget completion does not establish convergence or generalization.

## 16. Edge Cases

The architecture sizes and loss-normalization axes above are part of the API, not inferred by broadcasting. Fitted tensor trailing dimensions must match at inference; unsupported sequence/image/graph forms fail explicitly. One tanh bottleneck and linear decoder; strict k<p. Gaussian corruption std0..1 in normalized training units; no image/dataset denoising guarantee, masking/salt-and-pepper noise, mini-batch normalization, deep decoder or learned corruption.

Inputs copy caller arrays and use local default_rng. Reject nonfinite/nonreal arrays, bool data, invalid dimensions/learning rates/batches/seeds, excess compute budgets and inference before fit. Fit commits state only after a complete finite run; invalid/failed refits preserve a prior successful model.

## 17. Advantages

The specific Denoising Autoencoder — Gaussian corruption forward and reverse equations are visible in a compact NumPy implementation; independent mathematical invariants and per-entry gradients make the mechanism inspectable.

## 18. Disadvantages and Limitations

One tanh bottleneck and linear decoder; strict k<p. Gaussian corruption std0..1 in normalized training units; no image/dataset denoising guarantee, masking/salt-and-pepper noise, mini-batch normalization, deep decoder or learned corruption.

## 19. When to Use It

Use for learning and validating the stated Denoising Autoencoder — Gaussian corruption mechanism on a small controlled CPU dataset.

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

Hold one corruption draw fixed and derive why the decoder residual uses C rather than U. Compare raw noisy-to-clean MSE with reconstructed-to-clean MSE on the controlled fixture. Repeat with noise_std=0 to recover the ordinary reconstruction objective.

## 24. References

[Vincent et al., Extracting and Composing Robust Features with Denoising Autoencoders](https://doi.org/10.1145/1390156.1390294).

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). New Phase19 B7 owner review pending.
