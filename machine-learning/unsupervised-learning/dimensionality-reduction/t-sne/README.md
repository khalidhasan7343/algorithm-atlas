# t-distributed Stochastic Neighbor Embedding (exact t-SNE)

## 1. Algorithm Name

t-distributed Stochastic Neighbor Embedding (exact t-SNE)

## 2. Overview

Build a low-dimensional visualization by matching high-dimensional neighborhood probabilities with heavy-tailed Student-t similarities.

## 3. Problem Statement

For 3<=n<=128 finite rows, choose output dimensions1..3 and perplexity1..n-1. Learn one embedding of these training rows; there is no new-row transform.

## 4. Why Do We Need This Algorithm?

Nonlinear local neighborhoods can be hard to see in a linear PCA plot. An asymmetric KL objective emphasizes retaining high-probability neighbors.

## 5. Real-World Applications

Exploratory visualization of small feature tables with repeated seeds and careful neighborhood checks; apparent island sizes and distances need not reflect input geometry.

## 6. Core Intuition

Turn distances into probabilities, choose a bandwidth per observation to match a target neighborhood entropy, and move embedded points so the important pairs remain likely neighbors.

p(j|i)=exp(-beta_i*dij²)/sum_(l!=i)exp(-beta_i*dil²), p(i|i)=0; choose entropy log(perplexity). Pij=(p(j|i)+p(i|j))/(2n). Low-dimensional numerator tij=(1+||yi-yj||²)^-1, diagonal0; Qij=tij/sum_(a!=b)tab. C=sum Pij log(Pij/Qij), summed over ordered pairs. Gradient_i=4 sum_j (Pij-Qij)tij(yi-yj). Zero P terms contribute zero.

## 7. Prerequisites

Vectors, inner products, matrix multiplication, derivatives where optimization is used, and floating-point tolerances. Read the [B5 contracts](../../../../docs/dimensionality-reduction-conventions.md) and linked comparisons below.

## 8. Step-by-Step Working Process

Center and uniformly scale X for stable distances (per-row bandwidth calibration absorbs that common scale). Binary-search each positive precision using shifted exponentials and entropy tolerance1e-7. Reject perplexity below exact nearest-distance tie multiplicity. Uniform n-1 perplexity uses beta0. Seed small Gaussian coordinates, then minimize exact KL with Armijo full-gradient steps and at most max_iter iterations. Store P, conditionals, precisions, history and final gradient norm/status; budget exhaustion is reported honestly, not called convergence.

## 9. Pseudocode

```text
compute squared distances
for each row: binary-search beta for entropy log(perplexity)
P=(conditional+conditional.T)/(2n)
Y=seeded small Gaussian coordinates
repeat bounded iterations: compute Student-t Q, KL, gradient; backtrack descent
return Y, history, converged flag and optimization status
```

## 10. Dry Run

X=(0,1,3,7), perplexity2, seed0, max_iter30. Each conditional row sums1 and has entropy approximately log2; symmetrized P has zero diagonal, total1. The example runs 30 bounded descent steps and prints the actual embedding/status. The probability/gradient tests independently compute the same objective, and evidence retains actual numeric coordinates. A uniform four-row duplicate input with perplexity3 has Pij=1/12 for i!=j.

## 11. Time Complexity

Dense pairwise work O(n²*p), 128-step binary searches O(n²*128), then O(T*B*n²*d) where d<=3, T<=max_iter<=5000 and B<=60 line-search trials. Default T500, learning_rate10; no asymptotic claim of a production Barnes-Hut solver.

## 12. Space Complexity

O(n²+n*d) retained/working pairwise matrices and embedding, plus O(n*p) input; no recursion.

## 13. Python Implementation

[TSNE source](python/solution.py) implements the stated mechanism using NumPy primitives and shared bounded contracts; no reference estimator is imported. [Executable example](python/example.py); [tests](tests/test_python.py). Fit copies caller data and installs state only after successful validation/computation. Queries validate fitted feature dimensions.

Validation independently calculates conditional weights/entropy and Student-t KL; central finite differences check every gradient entry and rigid-motion invariance. Installed sklearn joint probabilities use an explicit float32-aware tolerance. Duplicates, impossible perplexity, bounded monotone descent and seeded repeats are covered.

## 14. C++ Implementation

C++ is optional for this authorized Python/NumPy scope and is absent; no placeholder source or test is provided. DSA still requires actual Python/C++17/C++20 checks.

## 15. Input and Output Examples

From repository root, with requirements-ml-test.txt installed:

```sh
python machine-learning/unsupervised-learning/dimensionality-reduction/t-sne/python/example.py
```

The example uses the dry-run input and prints a JSON embedding. The solution also accepts a JSON object with X, optional parameters and y for supervised LDA on stdin. Actual example/CLI outputs are retained in the Phase 17 evidence. Numeric coordinates are sign/rotation dependent where explained; objectives and subspaces are the comparison contract.

## 16. Edge Cases

Duplicate observations are valid only when requested entropy is attainable; all identical n rows require perplexity n-1. Finite-difference checks use smooth finite coordinates. Nonfinite X, n<3, invalid dimensions/seed and excessive perplexity fail. Finite optimization budgets may finish unconverged; use optimization_status_, converged_ and gradient_norm_.

Reject nonfinite/nonreal arrays, invalid dimensions and unsupported resource limits before fitting. Invalid refits preserve previous fitted arrays. Random methods use a local generator and never modify global RNG state.

## 17. Advantages

Explicit normalized probabilities, auditable objective/gradient and deterministic bounded experiments with monotone accepted KL steps.

## 18. Disadvantages and Limitations

Transductive exact dense method; no transform, early exaggeration, momentum, approximate search or production-library coordinate parity. The objective is nonconvex and a finite budget does not guarantee a useful local minimum. Local similarities are emphasized; global distances, cluster area and inter-island gaps are not preserved guarantees.

## 19. When to Use It

Use for a small local-neighborhood visualization with documented perplexity, seed and optimization diagnostics.

## 20. When Not to Use It

Use an inductive projection for new rows or when global metric distances and interpretable axes are required.

## 21. Comparison With Related Algorithms

PCA is a linear variance/reconstruction projection. t-SNE normalizes all pair similarities and minimizes asymmetric KL. UMAP uses a fuzzy neighbor graph and Bernoulli cross-entropy; neither promises raw-coordinate agreement or semantic clusters.

## 22. Interview Questions

Why symmetrize? It makes unordered neighborhood importance consistent while retaining total mass1. Why Student-t? Heavy tails alleviate crowding. Why can low perplexity be impossible with duplicates? Equal minimum distances share unavoidable limiting probability mass.

## 23. Practice Problems

Derive the factor4 in the ordered-pair KL gradient. Verify a three-point uniform P by hand. Rotate/translate an embedding and show KL is unchanged; then rescale it and observe KL generally changes.

## 24. References

[van der Maaten and Hinton, original t-SNE paper](https://jmlr.org/papers/v9/vandermaaten08a.html); [author t-SNE notes](https://lvdmaaten.github.io/tsne/).

## 25. Author Attribution

**MD.Khalid Hasan**, [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../../LICENSE); [contribution policy](../../../../CONTRIBUTING.md). This lesson is part of Phase 17 B5; owner review is pending.
