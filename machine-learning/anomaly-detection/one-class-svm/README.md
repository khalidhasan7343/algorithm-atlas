# One-Class SVM

## 1. Algorithm Name

One-Class SVM learns a kernel-space support boundary by solving a constrained convex dual. This canonical implements real capped-simplex feasibility and pairwise optimality;it is not distance-to-mean,kernel density estimation or a wrapped binary classifier.

## 2. Overview

Estimate a support region for unlabeled reference features using the RBF one-class SVM dual. Inference evaluates a learned kernel expansion relative to a KKT-derived rho. The parameter nu controls the optimization constraints;it is not an arbitrary contamination quantile.

## 3. Problem Statement

fit(X) accepts1..256 finite rows,1..32 features,magnitude<=1e12. nu is1e-4..1. RBF is the only supported kernel;gammaNone means1/d,otherwise1e-12..1e12. tolerance1e-12..1,max_iter1..20000,with n*max_iter<=3e6. Query matrices preserve feature count and allow0..1024 rows. Public projection helper inputs are1..256 real coordinates with magnitude<=100 and cap in[1/n,1e4].

alpha_,cap_,gram_ expose the normalized feasible dual. support_,support_vectors_,dual_coef_ identify positive coefficients without pretending nonunique supports must match a library. rho_,rho_bounds_,free_support_ expose the boundary certificate. objective_history_,feasibility_history_,objective_,primal_,dual_,primal_dual_gap_,kkt_residual_,pair_gap_,n_iter_,status_,converged_ retain actual optimization evidence. score_samples is kernel normality g,anomaly_scores=-g,decision=g-rho,predict uses+1/-1.

## 4. Why Do We Need This Algorithm?

A support boundary can be learned from unlabeled reference observations when anomaly labels are scarce. A constrained kernel objective gives a smooth nonlinear boundary with auditable feasibility and optimality conditions.

## 5. Real-World Applications

Small novelty/support-estimation experiments on finite reference features are suitable applications when an RBF similarity is meaningful. Choose feature scaling and kernel parameters with permitted training data; no guaranteed anomaly rate is inferred.

## 6. Core Intuition

Minimize.5*alpha.T*K*alpha with sum(alpha)=1 and0<=alpha<=C=1/(nu*n). Kij=exp(-gamma*||xi-xj||²). For g=Kalpha,the KKT conditions are g>=rho at alpha0,g<=rho at alphaC,and g=rho at free coefficients. Pair transfer d=e_i-e_j has derivative g_i-g_j and curvature Kii+Kjj-2Kij;the exact bounded minimizer increases the minimum-gradient eligible coordinate and decreases the maximum-gradient positive coordinate. rho averages free values,or uses the justified bound interval when none are free.

Dual mass is distributed over reference observations under a cap. A valid update moves mass between two coordinates rather than changing total mass. At optimality no feasible pair transfer can reduce the objective. The resulting kernel expansion describes support,with rho separating negative novelty decisions from nonnegative inlier decisions.

## 7. Prerequisites

Positive-semidefinite kernels,convex quadratic objectives,equality/box constraints,capped-simplex projection and KKT conditions are prerequisites. Understand support-vector boundary conventions and finite-tolerance optimization diagnostics.

## 8. Step-by-Step Working Process

Validate bounded RBF data and parameters;reuse the approved direct-difference kernel helper unchanged. Initialize by a genuine capped-simplex projection. Repeatedly find the most violating feasible pair and minimize that line while preserving pair mass and bounds. Verify feasibility after every update and periodically recompute the gradient. Derive rho and all final diagnostics from a fresh gradient. Report approximate KKT convergence only when both pair gap and rho residual meet tolerance;budgets/stagnation stay distinct.

## 9. Pseudocode

```text
K <- validated RBF Gram
alpha <- capped_simplex_projection(zeros,C)
for bounded iterations:
    i <- minimum gradient among coordinates below C
    j <- maximum gradient among positive coordinates
    if fresh pair gap<=tol:stop
    transfer <- min(C-alpha[i],alpha[j],gap/curvature)
    update pair preserving mass;check feasibility
rho <- free-gradient mean or valid no-free KKT bounds
return kernel expansion-rho and actual certificates
```

## 10. Dry Run

For two symmetric points,the Gram is[[1,k],[k,1]] and alpha=[.5,.5] minimizes the dual;objective=(1+k)/4 and rho=(1+k)/2. At nu1 every coefficient is exactly1/n,so the feasible set is a singleton. If there are no free or zero coefficients,the valid rho interval is[max(Kalpha),+infinity);choose the finite lower endpoint rather than an arbitrary mean. A separate four-point test verifies a finite no-free-support interval.

## 11. Time Complexity

Gram construction costs O(n²*d) time and O(n²) memory. Each pair-coordinate update searches and updates O(n) gradient/state entries;periodic fresh matrix-vector products add O(n²) every50 updates. Conservative training cost is O(n²*d+I*n+I*n²/50). The bounded96-step initial projection costs O(n). Scoring m query rows costs O(m*n*d),because all learned coefficients are retained for numerical fidelity,including tiny positive supports.

## 12. Space Complexity

Gram storage is O(n²);owned features/support vectors O(n*d). Optimization vectors cost O(n);objective/feasibility histories O(I). Query kernels materialize O(m*n) entries,with blocked direct-difference temporary storage inherited from the approved helper. All dimensions/iterations are capped.

## 13. Python Implementation

The canonical [OneClassSVM](python/solution.py) performs the stated mechanism from scratch with NumPy/standard library. Shared [B12 contracts](../../../docs/anomaly-detection-conventions.md) define validation and ownership. No ready-made anomaly detection estimator is called. See [meaningful tests](tests/test_python.py) and the executable [example](python/example.py).

## 14. C++ Implementation

C++ is optional under the authorized ML policy and is not implemented here. No placeholder C++ files or C++ pass claims. Existing DSA Python/C++17/C++20 requirements are preserved.

## 15. Input and Output Examples

From the repository root:

```sh
.venv/bin/python machine-learning/anomaly-detection/one-class-svm/python/example.py
```

Actual captured output:

```json
{"training": [[-1.0], [-0.7], [-0.3], [0.0], [0.2], [0.6], [1.0]], "kernel": "rbf", "nu": 0.3, "gamma": 0.8, "status": "kkt-tolerance", "converged": true, "iterations": 36, "support": [0, 3, 6], "alpha": [0.4428587, 0.0, 0.0, 0.1142826, 0.0, 0.0, 0.4428587], "rho": 0.51226108, "objective": 0.25613054, "kkt_residual": 8.84e-10, "feasibility": 0.0, "query": [[0.0], [0.5], [4.0]], "decisions": [0.0, 0.01709169, -0.51193013], "labels": [1, 1, -1]}
```

Re-run targeted verification with `.venv/bin/python -m pytest machine-learning/anomaly-detection/one-class-svm -q`.

## 16. Edge Cases

Singletons,duplicates,identical points,near-constant kernels and nu1 are supported. No-free-SV rho uses mathematical bounds;nu1 can classify many training points as outliers and should not be compared to a library that returns a nonfinite boundary there. Large-distance RBF tails legitimately round to0;tiny distances can round the kernel to1. Only machine-roundoff-sized decision differences are snapped to0. Invalid kernels,nu/gamma/shapes and excessive work fail;failed fits preserve old state.

## 17. Advantages

The dual objective,feasibility and KKT conditions are independently auditable. Exact feasible pair steps avoid inappropriate unconstrained optimizers. A true capped-simplex root projection is supplied and tested against exhaustive face minimization. Kernel reuse preserves previous numerical behavior.

## 18. Disadvantages and Limitations

Dense Gram storage and pair scans are educational rather than large-scale LIBSVM replacements. Approximate KKT stopping does not claim exact optimality;primal-dual gap is separately reported and can be sensitive to low nu. RBF-only,finite parameter bounds and a fixed gamma convention are explicit. No probability calibration,automatic scaling or guaranteed anomaly rate. The constrained dual may have nonunique coefficients/support sets.

## 19. When to Use It

Use when a smooth kernel support boundary is a plausible unlabeled novelty model. Select kernel scale using training-only procedures and report nu,tolerance,status and certificate diagnostics. Evaluate unseen query margins separately from the training support-vector boundary.

## 20. When Not to Use It

Do not feed unscaled heterogeneous features and assume gamma is universally appropriate. Do not replace the equality/box constraints with clip-and-renormalize or generic unconstrained gradient descent. Use LOF for explicitly local density comparisons and Isolation Forest for randomized partitioning.

## 21. Comparison With Related Algorithms

Isolation Forest has a random partition construction;One-Class SVM solves a convex kernel dual;LOF computes training-set reachability ratios. sklearn/LIBSVM coefficients,offsets and scores use an equivalent scaling bynu*n:divide those values before comparing this normalized dual. Nonunique support indices need not match.

## 22. Interview Questions

Which KKT inequality applies at alpha0? g>=rho. Why must a pair move preserve mass? The equality constraint sum(alpha)=1 is mandatory. What happens at nu1? Alpha is fixed and rho may have a half-infinite valid interval. Does an iteration budget prove convergence? No,actual KKT diagnostics remain visible.

## 23. Practice Problems

Enumerate small capped-simplex faces and compare projection. Solve the two-point symmetric dual analytically. Verify all KKT inequalities and primal-dual gap independently. Compare against SciPy SLSQP and scaled sklearn decisions away from boundaries. Construct duplicate data with nonunique coefficients and compare objectives rather than support sets.

## 24. References

[https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-99-87.pdf](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-99-87.pdf)

[https://scikit-learn.org/stable/modules/generated/sklearn.svm.OneClassSVM.html](https://scikit-learn.org/stable/modules/generated/sklearn.svm.OneClassSVM.html)

The [phase conventions](../../../docs/anomaly-detection-conventions.md) distinguish educational variants from full libraries and record the actual estimation objective. References support mathematics;executed local tests supply implementation evidence.

## 25. Author Attribution

Maintainer: **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas),[MIT license](../../../LICENSE),[contribution policy](../../../CONTRIBUTING.md).

