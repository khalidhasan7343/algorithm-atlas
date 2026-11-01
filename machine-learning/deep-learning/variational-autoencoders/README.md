# Variational Autoencoder — linear Gaussian variant

## 1. Algorithm Name

Variational Autoencoder — linear Gaussian variant

## 2. Overview

Fit a probabilistic latent model with a learned approximate posterior and a reparameterized stochastic reconstruction objective.

## 3. Problem Statement

X=(N,p),p<=16; latent_dim k<p. Encoder has separate p×k mean/log-variance projections; linear decoder k×p. encode returns(N,k) mean/logvar, transform returns mean, reconstruct decodes posterior mean, sample draws prior/observation noise.

## 4. Why Do We Need This Algorithm?

A deterministic bottleneck does not define a probabilistic latent-variable model or a sampling objective. A VAE learns a Gaussian posterior and a decoder while penalizing deviation from a standard-normal prior. Reparameterization moves random noise outside the parameter derivative so the sampled reconstruction remains differentiable.

## 5. Real-World Applications

Tiny latent sampling and reconstruction experiments with Gaussian numerical vectors. This linear Gaussian model exposes posterior, KL and observation-noise conventions; it is not a high-capacity image generator or a claim of calibrated density estimation.

## 6. Core Intuition

Fit a probabilistic latent model with a learned approximate posterior and a reparameterized stochastic reconstruction objective.

mu=X Wmu+bmu, logvar=5*tanh(X Wvar+bvar),std=exp(0.5*logvar),Z=mu+std*epsilon. Gaussian unit-variance decoder R=Z Wd+bd. Negative ELBO excluding the observation normalizing constant is 0.5*mean_N(sum_p((R-X)²))+0.5*mean_N(sum_k(mu²+exp(logvar)-1-logvar)). Prior is standard normal; training X is centered/uniformly scaled.

## 7. Prerequisites

Matrix shapes, derivatives/chain rule, floating-point arithmetic and the declared learning objective. Read [B7 contracts](../../../docs/neural-networks-and-deep-learning-conventions.md) and [scope](../../../docs/neural-networks-and-deep-learning-scope.md).

## 8. Step-by-Step Working Process

dR=(R-X)/N,dZ=dR Wd.T,dmu=dZ+mu/N. dlogvar=0.5*dZ*std*epsilon+0.5*(exp(logvar)-1)/N; multiply by5*(1-tanh(raw)²) for the raw variance projection. Accumulate mean/variance encoder matrices/biases and decoder gradients. Freeze the same epsilon for plus/minus perturbations.

Copy/validate inputs, initialize locally, run bounded CPU gradient updates, and install fitted state only after a finite completed run. Mini-batches are shuffled with a local RNG except full-graph GNN. Defaults epochs100,learning_rate0.1,batch_size16,gradient_clip5 where supported; model-specific architecture controls are stated above. At most10000 updates,20000 parameter values and the common array limits apply. Histories are pre-update minibatch averages; fixed-budget status explicitly does not certify convergence.

## 9. Pseudocode

```text
normalize X and initialize separate mean/logvariance encoders and linear decoder
for each minibatch:
  mu = X@Wmu+bmu; lv = 5*tanh(X@Wvar+bvar)
  draw epsilon locally; z = mu + exp(0.5*lv)*epsilon
  R = z@Wd+bd
  L = mean_rows(0.5*sum_features((R-X)^2)
                + 0.5*sum_latents(mu^2+exp(lv)-1-lv))
  backpropagate reconstruction through decoder and sampled z
  add KL adjoints; differentiate the smooth logvariance bound
  clip all parameter gradients and update
sample prior z, decode, add independent unit observation noise, undo normalization
```

## 10. Dry Run

At mu0,logvar0,decoder0 and epsilon0, KL=0 and objective=0.5*sum(X²)/N. A nonzero fixed-epsilon fixture independently checks Z=mu+exp(logvar/2)*epsilon and the complete negative ELBO. Sampling uses prior Z~N(0,I) and independent unit observation noise before undoing preprocessing. The executable example below runs fixed-seed training and emits the actual learned outputs and first/final losses; they are recorded in Phase19 evidence rather than invented.

## 11. Time Complexity

Fit O(E*N*p*k); encoding/decoding/sampling O(q*p*k). KL and reparameterization add O(N*k) elementwise work; no tractable exact posterior is assumed by the training API.

## 12. Space Complexity

O(B*(p+k)+p*k) state/parameters and O(N*p) copied input. Sampling is bounded to128 draws; no MCMC chain, framework or weights file.

## 13. Python Implementation

[VariationalAutoencoder source](python/solution.py) contains the actual architecture and analytic gradients. [Example](python/example.py); [tests](tests/test_python.py). Core imports NumPy/stdlib/local primitives only, never a framework estimator. Loss/forward/backward functions take explicit parameter arrays so independent finite differences can freeze all stochastic inputs. Tests independently check this model’s forward equations/objective, every weight and bias by central finite differences with fixed stochastic inputs, controlled training and repeated seeded outputs. Common tests add invalid rank/domain/shape/limits, constant/duplicate rows, global RNG/input copies, finite-state detection and atomic failed refits.

## 14. C++ Implementation

C++ is optional and absent under the Phase19 ML policy. No placeholder source/test. DSA still requires actual Python/C++17/C++20 tests.

## 15. Input and Output Examples

Run the fixed-seed example from the repository root:

```sh
python machine-learning/deep-learning/variational-autoencoders/python/example.py
```

The equivalent JSON input to `python/solution.py` is:

```json
{"X":[[-1,-0.5],[-0.3,-0.15],[0.3,0.15],[1,0.5]],"parameters":{"latent_dim":1,"epochs":40,"learning_rate":0.03,"batch_size":4}}
```

Observed output in this phase's [executed example records](../../../docs/neural-networks-and-deep-learning-evidence/examples-results.json):

```json
{"loss_initial":0.4755841637547126,"loss_final":0.35546400959531405,"optimization_status":"fixed-budget-completed","embedding":[[0.057987481369833276],[0.017550200523888202],[-0.01711032591549329],[-0.057547606761438365]],"reconstruction":[[-0.005105388607796911,0.009687400602052908],[-0.0017215549325915913,0.004080655232817205],[0.001178873931870111,-0.0007251265122419702],[0.00456270760707543,-0.006331871881477673]],"sample":[[0.09412594570100173,-0.5165892467303504],[0.37239679120738206,1.2873305950523342],[0.893236794427821,-0.613291522743588]]}
```

Floating-point last digits may vary across numerical environments. Losses describe the actual small training run and its declared reduction; fixed-budget completion does not establish convergence or generalization.

## 16. Edge Cases

The architecture sizes and loss-normalization axes above are part of the API, not inferred by broadcasting. Fitted tensor trailing dimensions must match at inference; unsupported sequence/image/graph forms fail explicitly. Linear Gaussian decoder and linear mean encoder with smooth bounded logvar[-5,5]. This is a genuine VAE but not a deep nonlinear image VAE. Variance bound changes the variational family; reconstruction through posterior mean is deterministic, while full generative samples include observation noise. No guarantee against posterior collapse or local optima.

Inputs copy caller arrays and use local default_rng. Reject nonfinite/nonreal arrays, bool data, invalid dimensions/learning rates/batches/seeds, excess compute budgets and inference before fit. Fit commits state only after a complete finite run; invalid/failed refits preserve a prior successful model.

## 17. Advantages

The specific Variational Autoencoder — linear Gaussian variant forward and reverse equations are visible in a compact NumPy implementation; independent mathematical invariants and per-entry gradients make the mechanism inspectable.

## 18. Disadvantages and Limitations

Linear Gaussian decoder and linear mean encoder with smooth bounded logvar[-5,5]. This is a genuine VAE but not a deep nonlinear image VAE. Variance bound changes the variational family; reconstruction through posterior mean is deterministic, while full generative samples include observation noise. No guarantee against posterior collapse or local optima.

## 19. When to Use It

Use for learning and validating the stated Variational Autoencoder — linear Gaussian variant mechanism on a small controlled CPU dataset.

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

Why reuse epsilon in a gradient check? Different draws would change the objective, not approximate one derivative. Why include KL? It regularizes the approximate posterior toward the prior. Unlike vanilla AE, this model learns a distribution and optimizes an ELBO, not only deterministic reconstruction.

## 23. Practice Problems

Show that the KL term is zero at mu=0,lv=0. Freeze epsilon and derive the reconstruction derivative with respect to lv. Compare deterministic decode(mu) reconstruction with prior samples that also include observation noise.

## 24. References

[Kingma and Welling, Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114).

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). New Phase19 B7 owner review pending.
