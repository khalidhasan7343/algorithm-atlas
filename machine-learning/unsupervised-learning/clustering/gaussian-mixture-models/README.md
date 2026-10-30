# Gaussian Mixture Models — full-covariance EM

## 1. Algorithm Name

Gaussian Mixture Models — full-covariance EM

## 2. Overview

Represent numeric observations by a weighted mixture of full-covariance Gaussians and fit its parameters by bounded expectation-maximization. Responsibilities are computed in stable log/shifted-exponential form; covariance regularization and Cholesky solves handle finite-precision density calculations.

## 3. Problem Statement

All fitting inputs are dense finite real numeric X=(n_samples,n_features);
1D X, booleans, strings, complex numbers, missing/infinite values and implicit
reshaping are rejected. Numeric features have magnitude <=10^12. Standard limits
are n<=512,p<=32; hierarchical and spectral/density methods state tighter limits
below. Prediction, when defined, requires the fitted feature count and at most
4096 rows; empty query matrices are supported. No supervised target y is consumed.
Caller inputs and global NumPy RNG state are unchanged. Failed fits do not replace
an earlier complete fitted state. See the exact task-specific API below.

GaussianMixture(n_components=1,reg_covar=1e-6,tol=1e-6,max_iter=300,n_init=1,means_init=None,random_state=0). K is a native integer 1..min(n,32), covariance diagonal addition in [10^-12,10^12], tolerance in (0,1], max_iter 1..1000, n_init 1..8 and seed 0..2^32-1. Explicit initial means need shape (K,p) and n_init=1. fit/fit_predict, predict, predict_proba, score_samples, mean-log-likelihood score, AIC and BIC are provided. Labels are component IDs, not supervised classes; empty query predictions are supported but mean-likelihood/information-criterion evaluation needs rows.

## 4. Why Do We Need This Algorithm?

Hard centroid assignments cannot express soft overlapping membership or a component’s full elliptical spread. Gaussian mixtures provide a normalized generative density and likelihood diagnostics, while EM exposes how posterior assignments drive parameter estimates.

## 5. Real-World Applications

Small numeric density-estimation or soft-segmentation studies can inspect component means, covariance ellipses and posterior responsibilities. Held-out density likelihood and information criteria answer different questions from supervised accuracy. The model does not establish semantic classes or calibrated application risk; Gaussian assumptions and local-optimum sensitivity must be evaluated.

## 6. Core Intuition

With parameters fixed, calculate the relative weighted Gaussian density of each component for each row. With those responsibilities fixed, update component masses, weighted means and full covariance matrices. Repeat E and regularized M steps until the change in mean observed log likelihood is small.

p(x)=sum_k pi_k*N(x|mu_k,Sigma_k). Responsibilities r_ik=pi_k*N_k(x_i)/sum_j pi_j*N_j(x_i). Nk=sum_i r_ik; pi_k=Nk/n; mu_k=sum_i r_ik*x_i/Nk; Sigma_k=sum_i r_ik*(xi-mu_k)(xi-mu_k)^T/Nk+reg_covar*I. Cholesky factors supply log determinants and Mahalanobis solves without an explicit inverse. The covariance addition is regularization; it does not imply unconditional monotonicity of the unregularized likelihood.

## 7. Prerequisites

Gaussian densities, covariance matrices, conditional probabilities, latent-variable EM, Cholesky factorization and log-sum-exp. Read [ML development](../../../../docs/ml-development.md), [current scope](../../../../docs/clustering-scope.md) and [numerical contracts](../../../../docs/clustering-conventions.md).

## 8. Step-by-Step Working Process

1. Validate data and parameters. Initialize means from explicit input, canonical K-Means, or observed repeated rows when fewer than K distinct values exist; identical mixture components can be valid.
2. Initialize uniform positive weights and a shared global population covariance plus the specified diagonal regularization.
3. Evaluate full Gaussian log densities with resolved positive-definite Cholesky factors.
4. Subtract each row’s largest log score, exponentiate and divide shifted exponentials by their row sum. This preserves normalized responsibilities even when adding log(sum) to a huge score rounds.
5. Reject numerically collapsed component mass; compute weighted anchored means, full covariance updates, diagonal regularization and normalized masses.
6. Re-evaluate density/responsibilities and record the mean log likelihood. Accept when absolute change<=tol, otherwise continue within max_iter.
7. Keep the best converged bounded initialization. If none converges or covariances are unresolved, raise ConvergenceError with the reason rather than returning partial parameters.
8. Store fitted weights/means/covariances, responsibilities, likelihood history and iteration diagnostics. New rows use the same fitted density, with first-component argmax ties.

All loops/recursion are bounded by explicit data/iteration limits. Fitted arrays and diagnostics are copied into state only after the full procedure succeeds.

## 9. Pseudocode

```text
for bounded initialization:
    initialize means, full covariances and uniform weights
    repeat at most max_iter:
        log_scores <- log(weight)+Gaussian log density using Cholesky
        r <- normalized exp(log_scores-row_max)
        Nk <- sum responsibilities; reject collapsed mass
        weights, means, covariances <- weighted M step plus reg*I
        evaluate updated mean log likelihood
        if absolute likelihood change<=tol: retain converged candidate; stop
keep converged candidate with best likelihood, otherwise fail
predict_proba <- fitted responsibilities; labels <- first argmax
```

## 10. Dry Run

For X=[-3.1,-3,-2.9,2.9,3,3.1], two components initialized at [-3,3] separate into the two three-row groups. Their final weights are 1/2, means approximately -3 and 3, and one-dimensional population variances are 0.0066666667 plus reg_covar. At reg_covar=0.001, each variance is about 0.0076666667. The example labels are [0,0,0,1,1,1]. A separate one-component oracle directly calculates weighted ML moments, SciPy Gaussian likelihood, AIC and BIC.

## 11. Time Complexity

With n rows, p features, K<=32, R<=8 starts and I<=1000 iterations, full covariance updates cost O(nKp²), Cholesky/eigen resolution O(Kp³), and likelihood solves O(nKp²) per iteration. Total O(R*I*(nKp²+Kp³)) plus canonical K-Means initialization when used. Query density on q rows costs O(qKp²+Kp³).

## 12. Space Complexity

Responsibilities/log scores use O(nK), data O(np), parameters O(Kp²+Kp), and one component’s centered/solved data O(np). Histories use O(I) per best run. No n*n*p tensor or saved dataset/model checkpoint is introduced.

## 13. Python Implementation

The from-scratch implementation is [python/solution.py](python/solution.py), with reusable `GaussianMixture` and the API described above. [python/example.py](python/example.py) is a fixed executable example. Core logic uses NumPy/local code, never a scikit-learn/SciPy estimator. Shared [support.py](../support.py) supplies strict contracts and stable Euclidean distances. Tests are in [tests/test_python.py](tests/test_python.py). Install [requirements-ml.txt](../../../../requirements-ml.txt) for runtime; use [requirements-ml-test.txt](../../../../requirements-ml-test.txt) for reference tests. Initialization explicitly reuses the canonical [K-Means](../k-means/README.md); its bounded initialization failures are recorded and other configured starts can continue.

## 14. C++ Implementation

Classical ML has a Python-first policy. Optional C++ is **not implemented** here; there are no dummy C++ source/test files. DSA remains Python/C++ mandatory, with actual C++17/C++20 validation. This status is explicit in the catalog rather than represented by a fake implementation.

## 15. Input and Output Examples

From the repository root with the existing ML environment:

```sh
python machine-learning/unsupervised-learning/clustering/gaussian-mixture-models/python/example.py
```

The independently justified labels are `[0, 0, 0, 1, 1, 1]`. Cluster IDs are conventional, not class meanings; the dry run explains their ordering. Equivalent Python API, from this topic's python directory:

```python
from solution import GaussianMixture
model = GaussianMixture(**{'n_components': 2, 'means_init': [[-3], [3]], 'reg_covar': 0.001, 'random_state': 0})
labels = model.fit_predict([[-3.1], [-3], [-2.9], [2.9], [3], [3.1]])
```

The JSON CLI accepts exactly X and optional parameters and prints a labels object. Invalid input exits 2 with stderr and no labels JSON. Numeric comparisons use tolerances; exact labels are used only when the example/tie rule fixes them.

## 16. Edge Cases

Exactly repeated observations may yield identical positive-weight components, uniform responsibilities and one hard argmax label; nonidentifiability is not a fake failure. Positive regularization resolves ordinary rank-deficient small data, but a floor too tiny relative to huge covariance eigenvalues may remain unresolved and fail explicitly. Component mass<=machine_epsilon*n is treated as collapsed. Query responsibilities normalize even when negligible tails underflow; very small input variation can be dominated by the regularization scale.

Predict/transform before fit, where those methods exist, raises ValueError. Invalid hyperparameters are checked again at fit. Exhausted iterative fitting is not silently returned as converged. Unsupported keywords fail rather than being ignored.

## 17. Advantages

Soft membership, full covariance shape and an explicit normalized density with likelihood/AIC/BIC diagnostics. Stable shifted E steps and transactional failures expose numerical behavior.

## 18. Disadvantages and Limitations

Nonconvex local solutions; no global optimum or universal likelihood monotonicity with covariance regularization. Only full covariance and dense vector observations, no missing/sparse data, weights, Bayesian mixture, automatic K or covariance-type options. Extreme ill-conditioning/relative precision can fail despite finite inputs. AIC/BIC use the conventional parameter count and do not certify true clusters.

## 19. When to Use It

Use when elliptical Gaussian components and soft density membership are meaningful for bounded numeric data.

## 20. When Not to Use It

Avoid strongly non-Gaussian/noise-heavy geometry without a suitable model, unresolved covariance scales, semantic interpretation of component IDs or a need for arbitrary production mixture features.

## 21. Comparison With Related Algorithms

| Method | Membership / objective |
| --- | --- |
| GMM | Soft posterior components, Gaussian likelihood |
| K-Means | Hard nearest means, squared error |
| HDBSCAN | Density hierarchy and noise, not a generative Gaussian mixture |

## 22. Interview Questions

1. Derive the responsibility and weighted-mean updates.
2. Why divide shifted exponentials directly?
3. Why can covariance regularization alter likelihood monotonicity?
4. How many free parameters are used in full-covariance AIC/BIC?

## 23. Practice Problems

1. Compute one-component ML moments and Gaussian density independently.
2. Align initial means/weights/covariance with sklearn and compare density predictions.
3. Demonstrate a collapsed component and verify a previous fitted model is preserved.

Validation commands, from the root:

```sh
python -m pytest machine-learning/unsupervised-learning/clustering/gaussian-mixture-models -q
python -m pytest machine-learning/unsupervised-learning/clustering -m numerical -q
python -m pytest machine-learning/unsupervised-learning/clustering -m oracle -q
python -m pytest machine-learning/unsupervised-learning/clustering -m reference -q
```

Oracles use independent formulas, exhaustive tiny cases or separately fitted references. Different valid labelings/trees/eigenvector signs are compared through the appropriate invariants. Marker groups overlap and are not additive. Seeds, data sizes and tolerances are fixed; no network dataset download or hidden library fit is used.

## 24. References

[scikit-learn Gaussian mixture formulation](https://scikit-learn.org/1.8/modules/mixture.html); [SciPy multivariate-normal reference density](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.multivariate_normal.html).

References identify the mathematical method. The exact implemented subset, numeric domain, tie policy and unsupported features are stated here; external libraries can use different valid initialization, ordering, stopping or metric conventions.

## 25. Author Attribution

Maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)** for [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../../LICENSE) · [Contribution guidance](../../../../CONTRIBUTING.md). Current Phase 16 review approval is pending.
