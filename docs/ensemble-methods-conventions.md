# B3 Ensemble Methods — API and numerical contracts

Owner **MD.Khalid Hasan** · [MIT](../LICENSE). [Authorized scope](ensemble-methods-scope.md).
These are bounded educational NumPy models, with no external ensemble library in
runtime code. Prior canonical ML array/label contracts and metrics are reused.

## Public models and tasks

| Canonical | Public classes | Target and aggregation |
| --- | --- | --- |
| Bagging | BaggingClassifier, BaggingRegressor | Hard vote fractions / mean regression predictions |
| Random Forest | RandomForestClassifier, RandomForestRegressor | Mean aligned leaf distributions / mean regression predictions |
| AdaBoost | AdaBoostClassifier | Discrete multiclass SAMME, weighted vote and score-softmax |
| GBM | GradientBoostingRegressor | Half squared loss, mean initialization, residual trees |
| XGBoost | XGBoostRegressor | Half squared loss, Hessian=1, exact regularized greedy trees |
| CatBoost | CatBoostRegressor | Squared loss, ordered statistics and independently fitted prefix oblivious trees |
| Voting | VotingClassifier | Hard weighted votes or soft aligned probabilities |
| Stacking | StackingClassifier, StackingRegressor | Stratified/K-fold out-of-fold columns, separate meta-model, full-data base refits |

Every model provides fit/predict/score. Classifiers provide predict_proba, whose
columns follow sorted classes_; these are model/vote probabilities, not guaranteed
calibrated probabilities. Equal computed floating-point scores choose the first
sorted class. Near ties need not be exact ties after float64 arithmetic.
Boosting models expose staged_predict, excluding initialization; an exact-fit
initial GBM/XGBoost has no fitted trees and no staged yields. CatBoost's ordered
prefix procedure always executes its configured bounded rounds.

## Input and state

For numeric models X is a dense real (n,p) array, y is one-dimensional (n,).
Training: 1<=n<=512, 1<=p<=32. Prediction: 0<=n<=4096 and the fitted p.
Numeric features and observed regression targets are finite, magnitude<=10^12;
empty fitting data, booleans, strings/objects in numeric X, complex values,
column-vector y and implicit reshaping are rejected. Class labels are homogeneous
int64-compatible integers or nonempty strings<=256 characters, at most 32 classes.
One-class bootstrap samples are valid. AdaBoost needs >=2 global classes.
StackingClassifier permits <=8 classes, each with >=n_splits rows.

Fits are transactional: validation and all training complete before fitted state is
replaced. Failed refits preserve the previous fitted model. Arrays passed to bases
are copies; models retain no caller-owned training views. Caller inputs and global
NumPy RNG state stay unchanged. random_state is a native integer 0..2^32-1, used by
local default_rng. The fixed seed is reproducible in the recorded NumPy environment;
bitwise cross-version RNG/tree parity is not promised. Prediction before fit raises
ValueError. Unsupported keyword arguments, including unsupported sample weights,
raise TypeError rather than being ignored. These objects are not thread-safe for
concurrent fit/predict or public-attribute mutation.

## Hyperparameter ranges and defaults

All constructor validation is repeated by fit, so changing an invalid public
parameter does not bypass checks. Prediction uses fitted rates/voting modes.

| Model / parameter | Default | Supported values |
| --- | --- | --- |
| All random_state | 0 | native int 0..2^32-1 |
| Bagging n_estimators / max_depth / min_samples_leaf | 10 / 3 / 1 | int 1..64 / 1..8 / 1..256 |
| Bagging max_samples / oob_score | 1.0 / False | native int 1..512 or fraction (0,1]; bool |
| Forest n_estimators / max_depth / min_samples_leaf | 10 / 4 / 1 | int 1..64 / 1..8 / 1..256 |
| Forest max_features / max_samples / oob_score | 'sqrt' / 1.0 / False | None, 'sqrt', int 1..p / as Bagging / bool |
| AdaBoost n_estimators / learning_rate / max_depth | 20 / 1.0 / 1 | int 1..64 / real (0,1] / int 1..4 |
| GBM n_estimators / learning_rate / max_depth / min_samples_leaf | 20 / 0.1 / 2 / 1 | int 1..64 / real (0,1] / int 1..8 / int 1..256 |
| XGBoost n_estimators / learning_rate / max_depth | 20 / 0.1 / 2 | int 1..64 / real (0,1] / int 1..6 |
| XGBoost reg_lambda / gamma / min_child_weight | 1 / 0 / 1 | real [0,10^12] / [0,10^12] / [0,512] |
| XGBoost subsample / colsample_bytree | 1 / 1 | real (0,1], sampled without replacement |
| CatBoost n_estimators / learning_rate / max_depth | 8 / 0.1 / 2 | int 1..16 / real (0,1] / int 1..3 |
| CatBoost prior / prior_weight / categorical_features | 0 / 1 / () | fixed real [-10^12,10^12] / real (0,10^6] / unique native column indices |
| Voting voting / weights / estimators | 'hard' / None / defaults | 'hard' or 'soft'; normalized nonnegative finite vector; 1..8 factories |
| Stacking n_splits / estimators / final_estimator | 3 / defaults / default | int 2..8 and <=n; 1..8 factories; one seed-taking meta factory |

Sample weights are accepted only by AdaBoost fit (and the shared tree primitive),
not by other public ensemble fits. Real scalar parameters exclude booleans and
nonfinite values. Factories' fit must train the returned instance; their prediction
methods must follow the stated shape/label/probability protocol and must not alter
query data. A factory is responsible for seeding and fitting any internal
preprocessing solely on its provided training fold.

## Shared weighted tree and resources

The B3 tree primitive is infrastructure, not a duplicate canonical CART topic. Public
observed regression targets remain bounded to 10^12; the internal tree accepts
finite derived residual targets up to 10^15 so a valid observed-target boundary
does not cause an artificial fit rejection. This covers the supported GBM residual
energy budget; it is not a larger public observed-target domain. The primitive
implements weighted Gini or locally normalized weighted squared error, stable
midpoints, nonempty positive-weight partitions, bounded depth and leaf constraints.
Random Forest draws a fresh feature subset at every eligible node. Bagging defaults
to all features. Classification leaves use weighted empirical distributions.
Zero-gain splits are not expanded; this can differ from trees that grow through
zero-gain XOR nodes. Ties retain the first feature/ascending threshold. Extreme
small gains can be unresolved at float64 precision; no exact-real claim is made.

Most ensembles allow 1..64 estimators and tree depth 1..8. AdaBoost depth is 1..4;
XGBoost depth is 1..6. Bagging/forest max_samples is a native integer 1..512 or
finite fraction (0,1], converted with ceil(n*fraction); bootstrap is always with
replacement. max_features for forest is None, 'sqrt' or integer 1..p. There is no
bootstrap=False switch. Bounded loops do not imply production speed: split search
is deliberately exhaustive. Avoid maximum budgets for normal examples/CI.

## Factories, bootstrap and OOB

Bagging, Voting and Stacking accept seed-taking factories: factory(integer_seed)
returns a fresh unfitted fit/predict estimator. Each factory call must return a new
independent instance; no cloning/pickling is used. Soft voting and classifier
stacking additionally require classes_ and normalized predict_proba. Columns are
explicitly aligned; unknown labels, family mismatches, bad shapes and invalid
probabilities fail. Factories are responsible for internal deep independence and
for honoring their seed; the ensemble verifies instance identity and common fitted
attributes. No arbitrary sklearn factory is used by the shipped defaults.

Bagging samples indices, then draws a separate base seed for each estimator.
Forest reuses this canonical bootstrap mechanism and adds per-node feature sampling.
Optional OOB diagnostics use only models whose bootstrap omitted that row. Counts
and coverage remain explicit; uncovered rows are NaN diagnostics and oob_score_ is
None if no row is covered. Covered-only accuracy/R2 is not a full held-out test.

## Boosting mathematics and stability

AdaBoost uses SAMME alpha=eta[log(1-e)-log(e)+log(K-1)], normalized weighted error,
and log-domain example weights. Zero initial weights stay zero. Nonnegative finite
sample weights are scaled before summing; all-zero, nonfinite or negative weights
fail. eta is in (0,1]. Exact e=0 retains that learner with finite alpha=1 and stops;
e>=1-1/K (within 10^-14 guard) stops, raising ValueError if it is the first learner.
Finite normalized weights can underflow to zero at extreme ratios; local NumPy
underflow handling permits expected negligible contributions. No infinite alpha
or claim of universal convergence. Probability output is normalized
softmax(weighted_vote/sum(alpha)/(K-1)); this is the documented score transform.

GBM starts at the mean y; residual r=y-F is the negative derivative of half squared
loss. Each tree fits r and adds eta*h. XGBoost starts at mean y and uses gradients
F-y, Hessian=1, leaves -G/(H+lambda), and split gain
0.5[G_L^2/(H_L+lambda)+G_R^2/(H_R+lambda)-G^2/(H+lambda)]-gamma.
min_child_weight bounds child Hessian mass; row and tree-column subsampling are
without replacement, with ceil(fraction*size). There is no L1, histogram, sparse,
missing-value, GPU, ranking or general custom-loss API. Gain roundoff can stop tiny
splits; finite checks catch unresolved updates. Unshrunk regularized tree gains are
surrogate gains, not a guarantee on held-out error.

CatBoost uses the original paper's naive ordered-boosting Algorithm 1 with a fixed
permutation shared by target statistics and residual estimation. Each prefix has
independently learned symmetric trees; it does not substitute plain GBM for ordered
boosting or claim the production shared-tree Algorithm 2. Observed-category TS is
(sum(previous y)+prior_weight*fixed_prior)/(previous_count+prior_weight).
The fixed prior does not depend on training labels. A row's own/future targets are
excluded; prediction uses full-training statistics and unseen categories use prior.
Each categorical column contains homogeneous nonempty strings or int64 codes;
other columns remain finite numeric. Limits: n<=64, p<=8, rounds<=16, depth<=3.
The prefix-zero model stays at the fixed prior; even constant targets can have
nontrivial ordered residuals and full-model loss need not decrease each round.
Empty symmetric cells receive zero update. No category combinations, multiple
permutations, ranking, classification loss or production optimizations are claimed.
Training ordered features and inference full-statistic features deliberately differ.

## Evaluation and review

Use deterministic training/test splits, no test-fitted preprocessing or tuning.
Reuse B2 accuracy/precision/recall/F1/confusion/log-loss and B1 MSE/RMSE/MAE/R2.
NaN OOB diagnostics are excluded from normal metric calls. Numerical/reference/
oracle selections overlap and are not additive counts. Tests never skip absent
references; required dependencies fail visibly. Source archives omit environments,
secrets, binaries, models/data and nested review archives. Hosted CI is separate
from actual local/extracted checks. Current Phase 15 owner approval is pending.
