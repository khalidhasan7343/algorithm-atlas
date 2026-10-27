# Phase 13 — Regression scope lock

Owner MD.Khalid Hasan authorized the first ML category on **2026-10-27
(Asia/Dhaka)** after confirming DSA implementation complete. The next sequential
development phase after DSA Phases 1–12 is **Phase 13**, the first ML phase.
This authorization supersedes the earlier stop-before-13 instruction. It does
not retroactively mark the DSA final audit or Phases 11/12 owner-approved.

The first ML category in catalog order is **B1, Supervised Learning — Regression**,
slug **regression**. All seven entries are distinct canonical topics; none has a
cross-category membership. Their starting statuses were planned with no source
or tests. Category order, all 35 categories, 256 memberships and 235 canonicals
are frozen. Preserve prior DSA canonical files, reports, archives and evidence.

| Batch | Canonical ID | Existing path | Implementation dependency |
| --- | --- | --- | --- |
| 1 | linear-regression | machine-learning/supervised-learning/regression/linear-regression | NumPy least-squares primitive; model logic here |
| 1 | ridge-regression | machine-learning/supervised-learning/regression/ridge-regression | Augmented least squares; unpenalized intercept |
| 1 | polynomial-regression | machine-learning/supervised-learning/regression/polynomial-regression | Reuses canonical Linear Regression after explicit monomial expansion |
| 2 | lasso-regression | machine-learning/supervised-learning/regression/lasso-regression | Cyclic L1 coordinate minimization and KKT stopping |
| 2 | elastic-net | machine-learning/supervised-learning/regression/elastic-net | Cyclic L1/L2 coordinate minimization and KKT stopping |
| 3 | support-vector-regression | machine-learning/supervised-learning/regression/support-vector-regression | Epsilon-SVR dual, linear/RBF kernels, bounded ADMM and primal/dual checks |
| 3 | decision-tree-regression | machine-learning/supervised-learning/regression/decision-tree-regression | Greedy CART squared-error splits and mean leaves |

Shared category support covers array contracts, metrics and transport; numerical
algorithm logic remains in the canonical topics. No scikit-learn estimator is
called by implementation code. No second ML category, Deep Learning, AI,
external dataset/model download, commit, push or release is authorized.

Finish and validate each internal batch before proceeding. The [ML standard](ml-development.md)
retains all 25 lesson headings; section 14 explains optional C++ honestly. DSA
still requires Python/C++17/C++20. See [the checkpoint](regression-checkpoints.md).
Final owner approval is **pending**.
