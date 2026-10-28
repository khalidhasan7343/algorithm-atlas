# B1 Regression — completion audit scope

Owner **MD.Khalid Hasan** explicitly approved all previously completed work and
authorized this Regression completion/verification request on 2026-10-28
(Asia/Dhaka). This is a return to **Phase 13, B1**, not Phase 15 or permission to
start another category. Previous Phase 13/14 and DSA work is owner-approved;
**the newly changed Regression artifacts and current review remain pending**.

Current catalog: **B1 — Supervised Learning — Regression**, slug `regression`,
seven canonicals, no cross-category memberships for these seven. All seven
already have Python solutions/tests/examples and 25-section lessons. Preserve
them; change only confirmed defects or demonstrated Regression evaluation gaps.

| Canonical ID | Existing canonical directory | Audit focus |
| --- | --- | --- |
| linear-regression | machine-learning/supervised-learning/regression/linear-regression | OLS, rank/intercept/gradient/reference and scoring |
| ridge-regression | machine-learning/supervised-learning/regression/ridge-regression | L2 objective/scaling, augmented solve, intercept |
| lasso-regression | machine-learning/supervised-learning/regression/lasso-regression | L1 soft threshold, KKT/objective/convergence |
| elastic-net | machine-learning/supervised-learning/regression/elastic-net | L1/L2 mixing/endpoints and convergence |
| polynomial-regression | machine-learning/supervised-learning/regression/polynomial-regression | Basis ordering/interactions, high degree, canonical OLS reuse |
| support-vector-regression | machine-learning/supervised-learning/regression/support-vector-regression | Epsilon tube, C/outlier effects, kernel/dual gap |
| decision-tree-regression | machine-learning/supervised-learning/regression/decision-tree-regression | Squared-error greedy splits, means and depth/leaf constraints |

Inventory remains **35 categories, 256 memberships, 235 canonicals**. Preserve
Classification's eleven implementations, DSA's 97 and all original historical
evidence/packages. The starting tree contains the previous Classification work
and its staged completion report; preserve every such source/artifact byte and
the staged index contents. [Baseline hashes](regression-audit-evidence/baseline.json)
capture this state before any audit changes.

The existing B1 suite must run before broader checks. One completion-audit batch
covers all seven already-implemented topics: investigate independently, reproduce
defects before fixing, add mathematical/numerical checks, verify docs/examples,
then validate Classification, DSA/Python/C++17/C++20 and the actual source ZIP.
C++ stays optional for ML and mandatory for DSA. No dependency upgrade or dataset
download is planned. No commit, push, release, other category or owner approval
of the new package is authorized.
