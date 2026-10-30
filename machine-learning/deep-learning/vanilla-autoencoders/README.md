# Vanilla Autoencoder — shared B5/B7 NumPy canonical

## 1. Algorithm Name

Vanilla Autoencoder — shared B5/B7 NumPy canonical

## 2. Overview

Learn an encoder bottleneck and a decoder through explicit reconstruction-loss backpropagation. This single B7-owned implementation also fulfills B5 dimensionality reduction.

## 3. Problem Statement

For X(n,p),n>=2,p>=2 and1<=k<p, fit a one-hidden-bottleneck dense network; expose latent transform, decoded inverse_transform and reconstruction.

## 4. Why Do We Need This Algorithm?

A nonlinear bottleneck can represent curved reconstruction structure that a linear projection cannot, provided sufficient architecture and training; superiority to PCA is not guaranteed.

## 5. Real-World Applications

Educational reconstruction/compression experiments on small numeric tables. No pretraining, image dataset download, framework or stored model checkpoint is needed.

## 6. Core Intuition

Encode each row into fewer coordinates and use the reconstruction error to adjust both mappings by the chain rule.

Normalize A=(X-mean)/scale using training-only mean and uniform max centered magnitude. Z=f(AW1+b1), R=ZW2+b2 with f=tanh or explicitly linear. MSE L=sum(R-A)²/(n*p). Let D=2(R-A)/(n*p); dW2=Z.T D, db2=sum D, H=(D W2.T)*fprime, dW1=A.T H, db1=sum H. For tanh, fprime=1-Z². Decode to original units R*scale+mean.

## 7. Prerequisites

Vectors, inner products, matrix multiplication, derivatives where optimization is used, and floating-point tolerances. Read the [B5 contracts](../../../docs/dimensionality-reduction-conventions.md) and linked comparisons below.

## 8. Step-by-Step Working Process

Validate a strict bottleneck and bounded parameters; initialize independent encoder/decoder weights with local seeded Glorot-uniform draws and zero biases. Optimize the concatenated parameter vector with full-batch gradient descent and Armijo backtracking. Retain actual history, gradient norm, iteration count and honest convergence/budget status. Fit state is installed atomically; inference retains the fitted activation even if training settings are later changed.

## 9. Pseudocode

```text
fit mean/scale on training rows only; normalize X
initialize W1,b1,W2,b2 with local RNG
repeat bounded epochs:
  Z=activation(A W1+b1); R=Z W2+b2
  compute MSE and all four gradients by chain rule
  backtrack step until sufficient loss decrease
return parameters, transform and original-unit decoder, diagnostics
```

## 10. Dry Run

X=[(-1,-0.5),(0,0),(1,0.5)], latent_dim1, seed0, max_iter30. Training mean=(0,0), scale1. There are seven trainable scalars: W1(2),b1(1),W2(2),b2(2). The example prints the three one-coordinate latents and explicit optimization status. A separate exact one-step test verifies theta_new=theta_initial-0.01*gradient with independently expanded backprop. Constant training X has normalized A=0, zero initial loss/gradient and exact mean reconstruction.

## 11. Time Complexity

With n rows,p inputs,k latent coordinates, each forward/backward trial O(n*p*k). T epochs and B<=60 line-search trials cost O(T*B*n*p*k), T<=5000,default500. Transform/decoder O(q*p*k). No mini-batch or optimizer-state overhead.

## 12. Space Complexity

O(n*p+n*k+p*k) fit storage and O(p*k+p+k) trained parameters/preprocessing; no recursion, dataset/model serialization or autodiff graph.

## 13. Python Implementation

[Autoencoder source](python/solution.py) implements the stated mechanism using NumPy primitives and shared bounded contracts; no reference estimator is imported. [Executable example](python/example.py); [tests](tests/test_python.py). Fit copies caller data and installs state only after successful validation/computation. Queries validate fitted feature dimensions.

Validation independently expands forward/MSE/backprop equations, central-differences every parameter for both activations, and uses SciPy check_grad with a separate forward/loss oracle. Exact one-step updates, controlled training-loss reduction, constant/tiny/large data, strict bottleneck and fitted-activation state are covered.

## 14. C++ Implementation

C++ is optional for this authorized Python/NumPy scope and is absent; no placeholder source or test is provided. DSA still requires actual Python/C++17/C++20 checks.

## 15. Input and Output Examples

From repository root, with requirements-ml-test.txt installed:

```sh
python machine-learning/deep-learning/vanilla-autoencoders/python/example.py
```

The example uses the dry-run input and prints a JSON embedding. The solution also accepts a JSON object with X, optional parameters and y for supervised LDA on stdin. Actual example/CLI outputs are retained in the Phase 17 evidence. Numeric coordinates are sign/rotation dependent where explained; objectives and subspaces are the comparison contract.

## 16. Edge Cases

Reject latent_dim>=p, nonpositive budgets/rates, unsupported activations and invalid seeds. Constant features, duplicate rows and rank-deficient inputs are valid; constant training rows reconstruct exactly. tanh saturation may make gradients small without recovering desired structure. Full-batch fixed budgets expose non-convergence honestly. Extremely disproportionate query/training scales can be rejected as unresolved numerical arithmetic.

Reject nonfinite/nonreal arrays, invalid dimensions and unsupported resource limits before fitting. Invalid refits preserve previous fitted arrays. Random methods use a local generator and never modify global RNG state.

## 17. Advantages

Explicit forward/backward equations, reusable latent/decoder methods, deterministic initialization, independent analytical/numerical gradient checks, and no heavyweight dependencies.

## 18. Disadvantages and Limitations

One tanh or linear bottleneck, linear decoder, MSE, full-batch gradient descent only; no deep stacks, tied weights, mini-batches, stochastic regularization, denoising, sparse or variational objectives. Reconstruction is nonconvex even with two trainable linear matrices. No claim that this simple tanh encoder/linear decoder represents every nonlinear manifold. Its decoder output lies in an affine subspace; a deeper nonlinear decoder is outside scope.

## 19. When to Use It

Use for learning reconstruction backpropagation and comparing controlled bottleneck representations with linear PCA.

## 20. When Not to Use It

Use PCA for a guaranteed optimal linear rank-k least-squares reconstruction or a production neural framework for large/deep models. No B7 category expansion is authorized.

## 21. Comparison With Related Algorithms

A linear autoencoder can attain the PCA subspace under suitable optimization, but its latent axes/weights are nonunique and gradient descent need not reach the optimum. tanh changes encoder coordinates and optimization; it does not guarantee better reconstruction, especially with this linear decoder. Denoising/sparse/variational autoencoders remain distinct planned canonicals.

## 22. Interview Questions

Why divide gradient by n*p? To match the declared mean-over-all-cells MSE. Why a bottleneck k<p? Otherwise dimensional reduction is not established. Does small training loss establish generalization? No: held-out reconstruction and the task assumptions still matter.

## 23. Practice Problems

Expand all seven gradients for the three-row dry run. Check them by central finite differences independently. Fit preprocessing only on a training split and compare held-out MSE to PCA without tuning on that split.

## 24. References

[Hinton and Salakhutdinov author publication record](https://www.cs.toronto.edu/~rsalakhu/bibtex/HinSal06.html) motivates neural dimensionality reduction; this shallow NumPy variant does not reproduce their deep pretraining architecture. [NumPy tanh primitive](https://numpy.org/doc/stable/reference/generated/numpy.tanh.html).

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). This lesson is part of Phase 17 B5; owner review is pending.
