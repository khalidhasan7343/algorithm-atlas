# Phase 15 — B3 Ensemble Methods locked scope

Owner **MD.Khalid Hasan** explicitly approved the latest prior work and authorized
Phase 15. [Approval verification](ensemble-methods-evidence/approval-verification.json)
checks the actual latest Regression and Classification packages. Their generation-time
pending statuses are historical; their bytes remain unchanged. Current B3 review
approval is pending. No Phase 16, commit, push, tag, release or publication.

B3 is `machine-learning/ensemble-methods`, eight canonicals, no cross-category
memberships. Inventory is 35 categories / 256 memberships / 235 canonicals.

| ID | Canonical folder | Implemented educational variant |
| --- | --- | --- |
| bagging | machine-learning/ensemble-methods/bagging | Bootstrap classifier and regressor; factory-created independent bases |
| random-forest | machine-learning/ensemble-methods/random-forest | Gini classifier / squared-error regressor, per-node random features |
| adaboost | machine-learning/ensemble-methods/adaboost | Discrete multiclass SAMME with weighted shallow trees |
| gradient-boosting-machine | machine-learning/ensemble-methods/gradient-boosting-machine | Squared-error regression with residual trees and shrinkage |
| xgboost | machine-learning/ensemble-methods/xgboost | Dense exact-split second-order squared-error tree boosting, L2/gamma |
| catboost | machine-learning/ensemble-methods/catboost | Squared loss, ordered target statistics and naive prefix ordered boosting (paper Algorithm 1), oblivious trees |
| voting-classifiers | machine-learning/ensemble-methods/voting-classifiers | Hard/soft weighted classifier aggregation, explicit class alignment |
| stacking | machine-learning/ensemble-methods/stacking | Out-of-fold regressor and classifier meta-learning, full-data refits |

No Extra Trees, LightGBM or invented canonical is added. XGBoost and CatBoost
implement their named mathematical mechanisms, without claiming production-library
feature/API parity. CatBoost uses genuine independently fitted prefix models;
this intentionally costly educational form has strict small-data limits.

Four sequential internal stages: (1) Bagging/Random Forest; (2) AdaBoost/GBM;
(3) XGBoost/CatBoost; (4) Voting/Stacking, then final integration/review package.
Every stage needs actual tests before status changes. B1/B2/DSA algorithms, original
tests/lessons and historical reports/evidence/packages are preserved byte-for-byte.
Only current guides, navigation, B3 metadata and new B3 files may change.
