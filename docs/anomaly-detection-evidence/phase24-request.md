# ALGORITHM ATLAS — PHASE 24
# B12: ANOMALY DETECTION
## COMPLETE CODEX MASTER PROMPT
### Isolation Forest | One-Class SVM | Local Outlier Factor
### From-Scratch Python + NumPy | Mathematical Oracles | Numerical Stability | Independent Reference Verification | Full Regression Audit | Review Package

---

# 0. PROJECT IDENTITY

Repository: `algorithm-atlas`
Owner: MD.Khalid Hasan
GitHub: `khalidhasan7343`
License: MIT

Target phase: **24**
Target category: **B12 — Anomaly Detection**

Expected canonical directory:

`machine-learning/anomaly-detection`

Expected canonical inventory:

1. Isolation Forest — `isolation-forest`
2. One-Class SVM — `one-class-svm`
3. Local Outlier Factor — `local-outlier-factor`

Expected algorithm count: **3**

These names and slugs come from the previously supplied catalog snapshot.

The CURRENT `catalog.yaml` and `AGENTS.md` are authoritative. Verify them before implementation.

## PRIMARY MISSION

Complete the three canonical anomaly detection algorithms with:

- Genuine from-scratch Python implementations
- NumPy-based numerical computation
- Correct mathematical formulations
- Robust input validation
- Explicit anomaly score conventions
- Independent mathematical oracles
- Deterministic randomized tests
- Numerical stability tests
- Reproducible experiments
- Correct threshold and contamination handling
- Exact 25-section README documentation
- Category and catalog integration
- Full ML regression testing
- Full DSA regression testing
- C++17 and C++20 verification
- Comprehensive Phase 24 review report
- Reproducible ZIP review package
- SHA-256 checksum
- JSON metadata

Do not substitute heuristic approximations while claiming to implement the canonical algorithms.

Do not fabricate test results.

Do not commit, push, tag, release, or start Phase 25 without explicit owner authorization.

---

# 1. PHASE 23 OWNER APPROVAL CHECKPOINT

The owner reports that Phase 23 Time Series is done.

Before starting Phase 24:

1. Inspect the Phase 23 review report.
2. Inspect the final Phase 23 review package.
3. Verify the six B11 algorithm statuses.
4. Review the recorded test results.
5. Verify catalog and documentation validation.
6. Confirm explicit owner approval for the Phase 23 handoff.

Expected report:

`docs/reviews/time-series/TIME-SERIES-REVIEW-REPORT.md`

If formal owner approval cannot be established, request confirmation and STOP before Phase 24 implementation changes.

Do not invent approval evidence.

Once the checkpoint is satisfied, complete all Phase 24 internal batches without requesting repeated approval.

---

# 2. MANDATORY REPOSITORY DISCOVERY

Read:

- `AGENTS.md`
- `catalog.yaml`
- `README.md`
- `pyproject.toml`
- `conftest.py`
- `.gitignore`
- `.github/workflows/ci.yml`
- `docs/progress.md`
- `docs/learning-roadmap.md`
- `docs/algorithm-index.md`
- Existing ML development documentation
- Existing ML dependency files
- B1–B11 implementations
- B1–B11 review reports
- Phase 23 Time Series review report
- Existing distance and kernel utilities
- Existing tree implementations
- Existing numerical optimization utilities
- Existing anomaly detection code, if any
- Catalog validation scripts
- Documentation generation scripts
- Review-package generation conventions

Record:

- Current branch
- HEAD commit
- Working-tree status
- Pre-existing modifications
- Python version
- NumPy version
- pytest version
- Optional scikit-learn availability
- Optional SciPy availability
- C++ compiler versions
- CI configuration
- Phase 23 owner approval status

Preserve unrelated owner changes.

Never use destructive Git cleanup.

---

# 3. VERIFY THE EXACT B12 INVENTORY

Inspect the current `catalog.yaml`.

Verify:

| # | Canonical ID | Expected directory |
|---|---|---|
| 1 | `isolation-forest` | `machine-learning/anomaly-detection/isolation-forest` |
| 2 | `one-class-svm` | `machine-learning/anomaly-detection/one-class-svm` |
| 3 | `local-outlier-factor` | `machine-learning/anomaly-detection/local-outlier-factor` |

For every algorithm, inspect:

- Canonical identity
- Current implementation status
- Current documentation status
- Current testing status
- Existing Python implementation
- Existing tests
- Existing examples
- Existing mathematical references
- Shared canonical memberships

If the current catalog differs, report the discrepancy and follow the authoritative repository.

Do not rename canonical IDs.

Do not add unrelated algorithms.

Do not create duplicate implementations.

---

# 4. IMPLEMENTATION LANGUAGE POLICY

For Machine Learning:

Mandatory:

- Python
- NumPy
- From-scratch core logic
- Python tests
- Mathematical verification
- Reproducible examples

Optional:

- C++
- C++ tests

Do not create placeholder C++ files.

For DSA:

Preserve mandatory Python and C++ implementations.

Preserve C++17 and C++20 verification.

## External libraries

Do not delegate the core algorithm to:

- `sklearn.ensemble.IsolationForest`
- `sklearn.svm.OneClassSVM`
- `sklearn.neighbors.LocalOutlierFactor`
- Ready-made anomaly detection packages
- Other complete third-party implementations

These libraries may be used only as independent reference oracles.

Core implementations must remain independently understandable.

---

# 5. COMMON ANOMALY DETECTION CONTRACT

Define a clear input/output contract for each algorithm.

Required concepts:

- Training feature matrix
- Number of samples
- Number of features
- Fitted state
- Raw anomaly scores
- Decision scores
- Anomaly labels
- Thresholds
- Contamination assumptions
- Training versus unseen-sample inference

Use an explicit score convention.

Recommended public convention:

- `predict(X)` returns +1 for inliers and -1 for outliers.
- `decision_function(X)` returns positive values for inliers and negative values for outliers, with zero representing the decision boundary.

This convention should be used only if compatible with existing repository APIs.

Algorithm-specific raw scores may have different orientations.

Document all conversions.

Never silently treat high anomaly scores as high normality scores.

Do not force LOF training-only outlier detection into an unsupported novelty-detection interface.

---

# 6. DATA VALIDATION

For all three algorithms, validate:

- Two-dimensional feature matrices
- Nonempty training data
- Minimum sample count
- Finite numerical values
- Consistent feature dimensions
- Invalid parameter types
- Invalid parameter ranges
- Unfitted-model calls
- Duplicate samples
- Constant features
- High-dimensional inputs
- Tiny datasets
- Zero-variance features

Document missing-value policy.

Do not silently impute NaNs.

Do not mutate caller-owned input arrays.

Avoid unexpected global random-state mutation.

---

# 7. IMPLEMENTATION BATCH PLAN

Use three internal implementation batches.

## Batch 1 — Isolation-Based Detection

- Isolation Forest

## Batch 2 — Kernel-Based Detection

- One-Class SVM

## Batch 3 — Density-Based Detection

- Local Outlier Factor

For each batch:

1. Inspect existing code.
2. Establish the mathematical specification.
3. Implement missing core logic.
4. Add independent mathematical oracles.
5. Add numerical stability tests.
6. Add deterministic randomized tests.
7. Add edge-case tests.
8. Verify educational examples.
9. Complete the README.
10. Run targeted tests.
11. Fix confirmed defects.

Proceed automatically between batches after successful checks.

Do not request owner approval after every batch.

---

# 8. ISOLATION FOREST — CORE IMPLEMENTATION

Canonical ID:

`isolation-forest`

Implement genuine Isolation Forest using randomized isolation trees.

Required components:

1. Training sample selection
2. Random feature selection
3. Random split selection
4. Recursive isolation tree construction
5. Tree depth tracking
6. Leaf sample counts
7. Path-length calculation
8. Expected unsuccessful search-length correction
9. Ensemble aggregation
10. Anomaly score calculation
11. Threshold handling
12. Prediction

A genuine isolation tree must randomly partition the feature space.

Do not substitute ordinary decision trees trained on labels.

Do not use random distance thresholds as a replacement for isolation trees.

## Required hyperparameters

Support documented equivalents of:

- Number of estimators
- Maximum samples
- Maximum tree depth
- Contamination
- Random seed

Optional:

- Feature subsampling
- Bootstrap sampling

Do not claim optional behavior unless implemented.

---

# 9. ISOLATION FOREST — MATHEMATICS

For a sample x, let h(x) denote its path length through an isolation tree, including the appropriate leaf correction.

The expected path-length normalization for sample size n is commonly defined using:

c(n) = 2H_(n-1) - 2(n-1)/n

for n greater than 2, where H is the harmonic number.

Handle the special cases for n = 1 and n = 2 explicitly.

A standard anomaly score is:

s(x,n) = 2^(-E[h(x)] / c(n))

Higher scores indicate greater anomaly likelihood.

Define behavior for degenerate normalization cases.

Document:

- Tree construction
- Split distributions
- Stopping rules
- Leaf corrections
- Expected path length
- Score orientation
- Threshold calculation

Do not confuse anomaly scores with inlier decision scores.

---

# 10. ISOLATION FOREST — TEST REQUIREMENTS

Required tests:

- One-feature data
- Two-feature data
- Constant data
- Duplicate samples
- Identical samples
- Small sample counts
- Large isolated point
- Random feature selection
- Random split validity
- Maximum depth enforcement
- Leaf sample count
- Path-length calculation
- Harmonic-number correction
- Ensemble averaging
- Fixed-seed reproducibility
- Contamination threshold
- Invalid contamination
- Invalid estimator count
- Invalid sample count
- Invalid feature dimensions
- Unfitted prediction

## Independent oracles

Construct tiny manually specified isolation trees.

Independently calculate:

- Tree path lengths
- Leaf corrections
- Expected path lengths
- Normalized anomaly scores

Verify that scores are finite and have the documented orientation.

Use seeded synthetic datasets to check anomaly ranking.

Optional scikit-learn comparison must align:

- Sampling
- Randomness where feasible
- Contamination
- Score conventions
- Maximum sample count

Do not require bitwise equality between independently randomized forests.

---

# 11. ONE-CLASS SVM — CORE IMPLEMENTATION

Canonical ID:

`one-class-svm`

Implement a genuine One-Class Support Vector Machine.

The implementation must optimize the One-Class SVM objective.

Do not substitute:

- Ordinary binary SVM
- Distance from the mean
- Kernel density estimation
- A fixed-radius sphere heuristic
- A one-class perceptron
- A wrapper around scikit-learn

Use a mathematically defensible optimization method.

A suitable educational implementation is the kernelized dual formulation with constrained optimization.

---

# 12. ONE-CLASS SVM — MATHEMATICAL FORMULATION

For training samples x_1, ..., x_n, the standard One-Class SVM dual can be expressed as:

minimize:

0.5 * alpha.T @ K @ alpha

subject to:

sum(alpha_i) = 1

and:

0 <= alpha_i <= 1 / (nu * n)

where:

- K is the kernel Gram matrix.
- alpha contains dual variables.
- nu is the One-Class SVM parameter.
- n is the training sample count.

Document the assumptions behind this formulation.

The decision function is:

f(x) = sum_i alpha_i * K(x_i, x) - rho

where rho is estimated consistently with the KKT conditions.

Required:

1. Kernel computation
2. Dual variable initialization
3. Feasible optimization
4. Equality constraint preservation
5. Box constraint preservation
6. Dual objective calculation
7. Convergence criteria
8. Support vector identification
9. Decision boundary estimation
10. Decision function
11. Anomaly prediction

Do not claim a valid One-Class SVM if the optimizer does not solve the required constrained objective.

---

# 13. ONE-CLASS SVM — KERNELS

At minimum, support one explicitly documented positive-semidefinite kernel, preferably RBF.

The RBF kernel is:

K(x,z) = exp(-gamma * ||x-z||^2)

Document gamma selection.

Optional kernels:

- Linear
- Polynomial

Do not claim support unless implemented and tested.

Validate:

- Gamma
- Kernel name
- Input dimensions
- Numerical stability
- Symmetry of Gram matrices

For supported positive-semidefinite kernels, test the Gram matrix's expected mathematical properties.

Do not claim arbitrary custom kernels are valid without defining the required assumptions.

---

# 14. ONE-CLASS SVM — DUAL OPTIMIZATION

Implement a genuine constrained optimizer.

A suitable approach is projected gradient descent with a correct projection onto the capped simplex:

sum(alpha_i) = 1

0 <= alpha_i <= C

where:

C = 1 / (nu * n)

The projection must be mathematically correct.

Do not merely clip alpha values and normalize afterward if that violates the box constraints.

Possible projection methods include:

- Monotone root-finding for the capped-simplex projection
- Another independently justified exact or tolerance-controlled projection

Verify feasibility after every update.

Use bounded iterations.

Define a convergence criterion based on appropriate optimization residuals.

Report non-convergence honestly.

Do not silently treat maximum iterations as successful convergence.

---

# 15. ONE-CLASS SVM — RHO ESTIMATION

Estimate rho using KKT-consistent conditions.

For free support vectors satisfying:

0 < alpha_i < C

rho can be estimated from their kernel decision values.

Handle the case where no free support vectors are available.

Use mathematically justified KKT bounds rather than an arbitrary threshold.

Verify:

- Dual feasibility
- Equality constraint
- Box constraints
- Objective behavior
- KKT residuals
- Decision function
- Prediction labels

Document numerical tolerances.

Do not claim exact optimality from approximate numerical solutions.

---

# 16. ONE-CLASS SVM — TEST REQUIREMENTS

Required tests:

- Small one-dimensional dataset
- Two-dimensional dataset
- Identical samples
- Duplicate samples
- Constant data
- Linear kernel if supported
- RBF kernel
- Kernel symmetry
- Gram matrix correctness
- Valid dual initialization
- Capped-simplex projection
- Equality constraint preservation
- Box constraint preservation
- Dual objective
- KKT conditions
- Support vector selection
- Rho estimation
- Decision function
- Prediction labels
- Invalid nu
- Invalid gamma
- Invalid dimensions
- Unfitted prediction
- Fixed-seed reproducibility where applicable
- Optimization non-convergence handling

## Independent oracles

Use:

- Hand-computed Gram matrices
- Small analytically solvable dual problems
- Independent capped-simplex projection calculations
- Independent KKT residual checks
- Optional SciPy constrained optimization
- Optional scikit-learn OneClassSVM comparison

For scikit-learn comparison, align:

- Kernel
- Gamma
- Nu
- Training data
- Decision-score convention

Allow justified numerical tolerances.

Do not claim identical support vector sets when the dual solution is nonunique.

---

# 17. LOCAL OUTLIER FACTOR — CORE IMPLEMENTATION

Canonical ID:

`local-outlier-factor`

Implement genuine Local Outlier Factor.

Required components:

1. Pairwise distance calculation
2. k-nearest-neighbor search
3. k-distance calculation
4. k-distance neighborhoods
5. Reachability distance
6. Local reachability density
7. Local Outlier Factor calculation
8. Score normalization or conversion
9. Threshold handling
10. Training-sample outlier detection

Do not substitute average k-nearest-neighbor distance and call it LOF.

Do not substitute global density estimation.

Do not ignore the reachability-distance definition.

---

# 18. LOCAL OUTLIER FACTOR — MATHEMATICS

For a point p, define its k-distance.

The k-distance neighborhood N_k(p) includes the points satisfying the k-distance rule, including all ties where the formal definition requires them.

Define reachability distance:

reach_dist_k(p,o) = max(k_distance(o), d(p,o))

Define local reachability density:

lrd_k(p) =
1 / average_{o in N_k(p)} reach_dist_k(p,o)

Then:

LOF_k(p) =
average_{o in N_k(p)}
[lrd_k(o) / lrd_k(p)]

Interpretation:

- LOF approximately 1 suggests density comparable to neighbors.
- Larger LOF suggests a locally sparse point.
- Scores below 1 can occur.

Do not assume LOF is a probability.

Do not claim every point with LOF greater than 1 is necessarily an outlier.

---

# 19. LOF — NEIGHBORHOOD SEMANTICS

Carefully define:

- Whether self-neighbors are excluded
- How ties are handled
- How duplicate points are handled
- How k-distance is computed
- Whether neighborhoods may contain more than k points
- Which distance metric is supported
- What happens when reachability distances are zero

The mathematical definition must match the implementation.

If using a fixed-size k-nearest-neighbor approximation rather than tie-inclusive neighborhoods, explicitly document the difference and obtain approval if it changes the required canonical algorithm semantics.

Do not silently change neighborhood semantics to simplify implementation.

---

# 20. LOF — DEGENERATE DENSITIES

Handle cases such as:

- Identical points
- Duplicate points
- Zero pairwise distances
- Zero reachability distances
- Infinite local reachability densities
- Undefined density ratios
- Too few samples
- All points equal
- Tied k-distances

Choose and document a mathematically defensible convention.

Do not allow uncontrolled NaNs.

Do not arbitrarily assign extreme anomaly scores without justification.

Ensure deterministic behavior.

---

# 21. LOF — NOVELTY VERSUS OUTLIER DETECTION

Distinguish:

## Outlier detection

Scores the training observations using neighborhoods derived from the training dataset.

## Novelty detection

Scores previously unseen observations using a reference dataset and an explicitly defined procedure.

These modes are not automatically interchangeable.

At minimum, implement genuine training-set LOF.

If novelty detection is supported:

1. Define the reference-neighborhood semantics.
2. Define how unseen samples are scored.
3. Test training versus unseen-sample behavior.
4. Document differences from standard training-set LOF.
5. Verify the implementation independently.

Do not expose unsupported novelty prediction behavior.

---

# 22. LOF — TEST REQUIREMENTS

Required tests:

- One-dimensional points
- Two-dimensional points
- Uniform-density cluster
- Two clusters with different densities
- Isolated point
- Duplicate points
- All-identical points
- Tied distances
- Small datasets
- Invalid neighbor count
- Invalid feature dimensions
- Invalid distance metric
- Exact pairwise distances
- Exact k-distance
- Exact neighborhoods
- Reachability distances
- Local reachability density
- Final LOF scores
- Deterministic output
- Threshold behavior
- Training-set detection
- Novelty behavior if supported

## Independent oracles

Construct tiny datasets with hand-calculable distances.

Independently compute:

- Neighbor sets
- k-distances
- Reachability distances
- Local reachability densities
- LOF ratios

Compare with the implementation.

Optional scikit-learn LOF comparisons must align:

- Number of neighbors
- Distance metric
- Neighborhood semantics
- Score orientation
- Novelty setting
- Contamination

Do not claim equivalence where the definitions differ.

---

# 23. ANOMALY SCORE CALIBRATION

For all three algorithms, document:

- Raw score
- Score orientation
- Decision score
- Threshold
- Prediction label
- Contamination parameter
- Training-score distribution
- Unseen-sample behavior

Important:

Contamination is a threshold-selection assumption, not proof of the true anomaly rate.

If contamination is used:

1. Validate its range.
2. Define quantile calculation.
3. Define tie behavior.
4. Define whether thresholding is based on training scores.
5. Test extreme valid values.
6. Document expected predicted anomaly counts.

Do not silently force exactly the requested anomaly count when score ties make that convention ambiguous.

Do not call raw scores calibrated probabilities.

---

# 24. INDEPENDENT ORACLE MATRIX

| Algorithm | Primary independent oracle |
|---|---|
| Isolation Forest | Manually specified trees, path lengths and harmonic normalization |
| One-Class SVM | Independent dual optimization, capped-simplex feasibility and KKT checks |
| Local Outlier Factor | Hand-calculated neighborhoods, reachability densities and LOF ratios |

Optional references:

- scikit-learn IsolationForest
- scikit-learn OneClassSVM
- scikit-learn LocalOutlierFactor
- SciPy constrained optimization

Reference libraries must not be used inside the production implementation.

Do not use production helper functions as the sole oracle.

---

# 25. SYNTHETIC DATASETS

Create small deterministic datasets.

Recommended examples:

1. Gaussian inlier cluster
2. Uniform inlier cluster
3. Single isolated anomaly
4. Two separated clusters
5. Two clusters with different local densities
6. High-dimensional Gaussian data
7. Constant data
8. Duplicate observations
9. Tied-distance data
10. Contaminated training data

Use fixed random seeds.

Do not download external datasets.

Keep standard CI workloads CPU-friendly.

Document the generating process.

---

# 26. ANOMALY DETECTION METRICS

For labeled synthetic evaluation datasets, implement or independently verify appropriate metrics:

- Precision
- Recall
- F1 score
- ROC-AUC
- Average precision / PR-AUC
- Confusion matrix

Document score orientation.

Do not calculate ROC-AUC using reversed score direction.

Do not assume labels are available during unsupervised training.

Handle:

- Single-class evaluation sets
- Undefined metrics
- Zero denominators
- Tied scores
- Empty inputs
- Invalid labels

Use scikit-learn metrics as optional independent references.

Do not report supervised evaluation metrics as part of the unsupervised fitting objective.

---

# 27. RANDOMIZED AND PROPERTY TESTS

Use deterministic seeds.

Test:

- Randomized datasets
- Different feature counts
- Different sample counts
- Duplicate points
- Constant features
- Large-magnitude values
- Small-magnitude values
- Extreme valid hyperparameters
- Invalid hyperparameters
- Repeated fitting
- Unfitted inference
- Input permutation
- Feature permutation where appropriate

Check mathematical properties only when their assumptions hold.

Examples:

- Isolation Forest scores must remain finite for supported valid inputs.
- One-Class SVM dual variables must satisfy constraints.
- LOF scores must follow the documented density-ratio semantics.

Do not claim universal anomaly ranking guarantees.

---

# 28. NUMERICAL STABILITY AUDIT

Audit:

- Division by zero
- Harmonic-number edge cases
- Invalid tree depth
- Empty tree branches
- Zero-variance features
- Kernel underflow
- Kernel overflow
- Invalid Gram matrices
- Ill-conditioned optimization
- Constraint violation
- Invalid rho estimation
- Zero reachability distance
- Infinite local density
- Undefined density ratios
- Nonfinite inputs
- Invalid thresholds
- Excessive memory allocation

Use stable mathematical formulations.

Do not silently suppress warnings.

Do not fabricate finite values when the mathematical quantity is undefined.

---

# 29. PERFORMANCE AND COMPLEXITY

Document algorithm-specific complexity.

## Isolation Forest

Analyze:

- Number of trees
- Subsample size
- Tree depth
- Training complexity
- Scoring complexity
- Memory complexity

## One-Class SVM

Analyze:

- Gram matrix construction
- Kernel evaluation
- Dual optimization iterations
- Memory complexity
- Support vector count
- Inference complexity

## Local Outlier Factor

Analyze:

- Pairwise distance computation
- Neighbor search
- Neighborhood storage
- Reachability density computation
- LOF score computation
- Dense versus scalable implementations

Do not claim a NumPy brute-force LOF implementation scales like an indexed nearest-neighbor implementation.

Benchmark only with actual executed measurements.

Do not fabricate performance results.

---

# 30. REPRODUCIBLE EDUCATIONAL EXAMPLES

Create one meaningful example per algorithm.

## Isolation Forest

Show:

- Training data
- Random isolation trees
- Anomaly scores
- Threshold
- Predicted anomalies

## One-Class SVM

Show:

- Training data
- Kernel
- Nu parameter
- Optimization result
- Support vectors
- Decision scores
- Predictions

## Local Outlier Factor

Show:

- Training data
- Nearest neighbors
- Local densities
- LOF scores
- Predicted outliers

Verify outputs by executing the examples.

Do not hardcode fabricated scores.

---

# 31. DOCUMENTATION REQUIREMENTS

Every B12 algorithm must follow the exact 25-section README structure required by `AGENTS.md`.

Do not reorder mandatory headings.

Each README must explain:

- Problem definition
- Mathematical assumptions
- Core algorithm
- Input/output contract
- Hyperparameters
- Equations
- Pseudocode
- Correctness reasoning
- Time complexity
- Space complexity
- Numerical stability
- Worked example
- Python implementation
- Testing methodology
- Independent oracle
- Practical applications
- Limitations
- Related algorithms
- References

Document the exact implementation variant.

Do not claim unsupported functionality.

---

# 32. CATEGORY README

Create or update:

`machine-learning/anomaly-detection/README.md`

Include:

1. Anomaly detection overview
2. Unsupervised anomaly detection
3. Outlier versus novelty detection
4. Isolation-based methods
5. Kernel-based methods
6. Density-based methods
7. Score interpretation
8. Threshold selection
9. Contamination assumptions
10. Algorithm comparison
11. Numerical stability
12. Computational complexity
13. Reproducible examples
14. Evaluation methodology
15. Canonical implementation links

Do not duplicate full implementations.

---

# 33. CATALOG AND DOCUMENTATION INTEGRATION

Update relevant records:

- `catalog.yaml`
- `docs/progress.md`
- `docs/learning-roadmap.md`
- `docs/algorithm-index.md`
- B12 category README
- Root README if necessary

Preserve:

- DSA canonical implementations
- B1–B11 implementations
- Existing canonical IDs
- Existing canonical paths
- Previous review reports
- Previous owner approvals
- Shared canonical memberships
- Existing blocked catalog entries

The B8 Dynamic Policy Optimization entry must remain blocked under the owner's earlier approved decision.

Do not rename or replace DPO.

Do not mark Phase 24 owner-approved.

---

# 34. PREVIOUS-PHASE COMPATIBILITY

Pay particular attention to:

- B2 Classification
- B3 Ensemble Methods
- B4 Clustering
- B5 Dimensionality Reduction
- B7 Deep Learning
- B10 Optimization
- B11 Time Series

Potential reusable components:

- Kernel calculations
- Distance calculations
- Tree structures
- Numerical optimization
- Probability utilities
- Evaluation metrics

Avoid unnecessary code duplication.

Do not introduce circular imports.

If shared utilities change:

1. Document changes.
2. Add compatibility tests.
3. Run affected regression tests.
4. Preserve previous behavior unless a confirmed defect requires correction.

---

# 35. TARGETED TESTING

Run:

```bash
python -m pytest machine-learning/anomaly-detection -q
```

Also execute:

- Isolation tree tests
- Path-length oracle tests
- Harmonic normalization tests
- One-Class SVM kernel tests
- Dual optimization tests
- Capped-simplex projection tests
- KKT residual tests
- LOF neighbor tests
- Reachability distance tests
- Local density tests
- Score orientation tests
- Contamination threshold tests
- Numerical stability tests
- Reproducibility tests
- Edge-case tests
- Synthetic anomaly tests

Do not weaken assertions merely to make tests pass.

---

# 36. REQUIRED VALIDATION COMMANDS

Run:

```bash
python scripts/validate_catalog.py
python scripts/generate_catalog_docs.py --check
python -m pytest --require-cpp
```

Verify:

- Catalog integrity
- Generated documentation consistency
- ML Python policy
- DSA Python policy
- DSA C++ policy
- C++17 compatibility
- C++20 compatibility
- Test discovery
- CI-equivalent behavior

If the full suite cannot finish:

1. Split tests into bounded groups.
2. Execute all feasible groups.
3. Record exact commands.
4. Record pass/fail/skip counts.
5. Identify unexecuted checks.
6. Explain environmental limitations.

Never claim unexecuted tests passed.

---

# 37. FULL REGRESSION AUDIT

Run regression checks across:

- B1 Regression
- B2 Classification
- B3 Ensemble Methods
- B4 Clustering
- B5 Dimensionality Reduction
- B6 Association Rule Learning
- B7 Neural Networks and Deep Learning
- B8 Reinforcement Learning
- B9 Graph-Based Learning
- B10 Optimization
- B11 Time Series
- B12 Anomaly Detection
- DSA Python
- DSA C++17
- DSA C++20
- Shared numerical infrastructure
- Catalog validation
- Documentation generation
- CI-equivalent checks

Do not silently modify previously approved algorithms.

---

# 38. NEGATIVE INFRASTRUCTURE TESTS

Verify:

- Missing required ML Python implementation is rejected.
- Missing ML Python tests are rejected.
- Invalid canonical IDs are rejected.
- Duplicate canonical paths are rejected.
- Missing README sections are detected.
- Generated documentation drift is detected.
- B12 tests are discovered by CI.
- Optional ML C++ follows repository policy.
- Missing mandatory DSA C++ is rejected.
- C++17/C++20 requirements remain enforced.
- Existing blocked catalog entries remain valid.

Do not weaken validators.

---

# 39. SECURITY AND RESOURCE LIMITS

Inspect for:

- Unbounded recursion
- Excessive tree depth
- Excessive tree count
- Unbounded optimization
- Excessive Gram matrix allocation
- Excessive pairwise distance allocation
- Invalid kernel values
- Unsafe serialization
- Arbitrary code execution
- Hidden network downloads
- Unexpected subprocess execution
- Hardcoded secrets
- Global RNG mutation

Keep mandatory tests CPU-friendly.

Do not require GPUs.

Do not download external datasets.

---

# 40. PHASE 24 REVIEW REPORT

Create:

`docs/reviews/anomaly-detection/ANOMALY-DETECTION-REVIEW-REPORT.md`

Include:

1. Phase identity
2. Category identity
3. Three-algorithm inventory
4. Canonical paths
5. Existing versus new implementations
6. Isolation Forest mathematical correctness
7. Isolation tree correctness
8. Path-length oracle verification
9. One-Class SVM mathematical correctness
10. Dual optimization verification
11. KKT condition verification
12. Kernel correctness
13. LOF mathematical correctness
14. Neighborhood verification
15. Reachability density verification
16. Score orientation verification
17. Threshold verification
18. Contamination handling
19. Outlier versus novelty semantics
20. Independent oracle results
21. Numerical stability
22. Reproducibility
23. Synthetic anomaly tests
24. Evaluation metrics
25. Edge-case tests
26. Educational examples
27. Documentation validation
28. Catalog validation
29. B1–B11 regression results
30. DSA regression results
31. C++17/C++20 results
32. CI-equivalent checks
33. Shared utility compatibility
34. Files created
35. Files modified
36. Dependencies
37. Bugs discovered
38. Fixes applied
39. Known limitations
40. Unresolved blockers
41. Exact reproduction commands
42. Review package paths
43. Owner approval: pending

Use actual test counts.

Do not fabricate mathematical verification evidence.

---

# 41. PHASE 24 REVIEW PACKAGE

Create:

```text
artifacts/review-packages/anomaly-detection/
├── algorithm-atlas-anomaly-detection-review.zip
├── algorithm-atlas-anomaly-detection-review.zip.sha256
└── algorithm-atlas-anomaly-detection-review.json
```

Include:

- All three B12 implementations
- All B12 tests
- All B12 algorithm READMEs
- B12 category README
- B12 review report
- Relevant shared numerical utilities
- Relevant previous ML implementations
- Relevant DSA implementations
- `AGENTS.md`
- `catalog.yaml`
- Root `README.md`
- `pyproject.toml`
- `conftest.py`
- Dependency configuration
- Validation scripts
- Documentation generators
- CI configuration

Exclude:

- `.git`
- Virtual environments
- Python caches
- pytest caches
- Compiled binaries
- Secrets
- Large datasets
- Model checkpoints
- Previous review ZIPs
- Nested ZIPs
- Temporary files

Verify:

1. ZIP opens.
2. ZIP CRC passes.
3. Extraction paths are safe.
4. Required files exist.
5. SHA-256 matches.
6. JSON metadata matches.
7. Independent extraction succeeds.
8. Catalog validation runs from extracted source.
9. Documentation validation runs from extracted source.
10. Relevant tests run from extracted source.

Record any checks that could not execute.

---

# 42. FINAL PHASE 24 COMPLETION SUMMARY

Present:

| Field | Result |
|---|---|
| Phase | 24 |
| Category | B12 — Anomaly Detection |
| Catalog algorithms | 3 |
| Implemented algorithms | Actual count |
| Completed batches | Actual count |
| Isolation Forest tests | Actual results |
| Isolation path-length oracle | Actual result |
| One-Class SVM tests | Actual results |
| One-Class SVM KKT verification | Actual result |
| One-Class SVM kernel verification | Actual result |
| LOF tests | Actual results |
| LOF density oracle | Actual result |
| Score orientation | Actual result |
| Contamination handling | Actual result |
| Independent oracle tests | Actual results |
| Numerical stability | Actual result |
| Reproducibility | Actual result |
| Edge-case tests | Actual result |
| B1–B11 regression | Actual results |
| DSA regression | Actual results |
| C++17/C++20 | Actual results |
| Catalog validation | Actual result |
| Documentation validation | Actual result |
| CI-equivalent checks | Actual result |
| B8 DPO blocked status | Preserved |
| Review report | Exact path |
| Review ZIP | Exact path |
| SHA-256 | Exact path |
| JSON metadata | Exact path |
| Owner approval | Pending |

Also provide:

| Algorithm | Implementation | Tests | Oracle | Documentation | Status |
|---|---|---|---|---|---|

List:

- Completed algorithms
- Incomplete algorithms
- Blocked algorithms
- Failed tests
- Skipped tests
- Unexecuted checks
- Numerical limitations
- Mathematical limitations
- Performance limitations
- Infrastructure modifications
- Exact reproduction commands

Do not claim 3/3 complete if mandatory work remains unfinished.

---

# 43. MANDATORY STOP CONDITION

After completing all B12 implementations, tests, documentation and review artifacts:

**STOP AND WAIT FOR EXPLICIT OWNER REVIEW AND APPROVAL.**

Do not:

- Start Phase 25.
- Start another ML category.
- Commit.
- Push.
- Tag.
- Release.
- Publish.
- Mark Phase 24 owner-approved.
- Modify the B8 DPO decision.
- Add unrelated algorithms.
- Hide failed tests.
- Fabricate verification results.

The owner must review the Phase 24 report and ZIP before authorizing the next phase.

---

# 44. EXECUTION ORDER

STEP 1 — Verify Phase 23 final owner approval.

STEP 2 — Inspect current repository and authoritative catalog.

STEP 3 — Verify the three B12 canonical entries.

STEP 4 — Implement Isolation Forest.

STEP 5 — Verify isolation trees, path lengths and anomaly scores.

STEP 6 — Implement One-Class SVM.

STEP 7 — Verify kernel calculations, dual optimization, capped-simplex feasibility and KKT conditions.

STEP 8 — Implement Local Outlier Factor.

STEP 9 — Verify neighborhoods, reachability distances and local density ratios.

STEP 10 — Audit anomaly score orientation and contamination thresholds.

STEP 11 — Run independent mathematical oracles.

STEP 12 — Run numerical stability and randomized tests.

STEP 13 — Complete exact 25-section READMEs.

STEP 14 — Update category documentation and catalog statuses.

STEP 15 — Run targeted B12 tests.

STEP 16 — Run full ML and DSA regression tests.

STEP 17 — Run catalog, documentation and CI-equivalent validation.

STEP 18 — Produce Phase 24 review report.

STEP 19 — Generate and verify ZIP, SHA-256 and JSON metadata.

STEP 20 — Present final results and STOP for owner review.

Do not request confirmation between ordinary implementation batches.

Ask for owner input only when a genuine approval, catalog, or mathematical specification blocker exists.

**BEGIN PHASE 24 ONLY AFTER SATISFYING THE PHASE 23 OWNER APPROVAL CHECKPOINT.**