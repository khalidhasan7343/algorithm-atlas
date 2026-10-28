# Regression evaluation and numeric contracts

Maintainer **MD.Khalid Hasan** · [MIT](../LICENSE) · [B1 audit scope](regression-audit-scope.md).
The seven canonical estimators are dense **single-output** models: fit X=(n,p),
y=(n,), predict=(m,). Multi-output targets and ambiguous implicit reshaping are
unsupported. The existing limits and optimizer contracts remain in each lesson.

## Definitions and units

For nonempty paired targets yᵢ and predictions fᵢ, residual eᵢ=yᵢ−fᵢ:

| Metric | Definition | Units / interpretation |
| --- | --- | --- |
| MSE | Σeᵢ²/n | Squared target units, smaller is better |
| RMSE | sqrt(Σeᵢ²/n) | Original target units, smaller is better |
| MAE | Σ|eᵢ|/n | Original target units, smaller is better |
| R² | 1−Σeᵢ²/Σ(yᵢ−mean(y))² | Dimensionless; can be negative, perfect fit is 1 |

For exactly constant observed targets, including one observation, the repository
convention is R²=1 for elementwise-exact predictions and 0 otherwise. It is not
computed from an underflowed error or a rounded nonzero variance. Empty metrics,
multi-output arrays, nonnumeric/bool/complex predictions, nonfinite values and
shape/count mismatches raise ValueError. Sample weighting is not implemented.
Target values retain the existing finite magnitude≤10¹²/cell budget. Predictions
may exceed that target magnitude if finite, subject to representable results.

## Scale-safe arithmetic

The shared [support module](../machine-learning/supervised-learning/regression/support.py)
provides `mse`, `rmse`, `mae`, `r2` and `regression_metrics(y,prediction)`.
All estimators' `score` methods use R².

RMSE first divides residuals by their maximum absolute value, computes the RMS
in normalized units and restores the scale. MSE squares that root after averaging;
this avoids an overflowing individual square when the true mean remains finite.
MAE similarly avoids overflowing a raw absolute-error sum. R² rescales target
deviations and compares root errors before tiny squared units disappear. Constant
targets are detected from actual target equality, preserving the stated convention
even when mean([0.1,0.1,0.1]) rounds away from 0.1.

Finite precision still has limits. A final MSE below the float64 range can round
to zero while its RMSE remains representable; tiny negligible normalized terms
can also round to zero. Those expected underflows are handled locally, not used
as an exact-fit or constant-target test. Unrepresentable final MSE/R² or invalid
arithmetic raises ValueError rather than returning infinity. Metrics are O(n)
time and O(n) checked working storage. This does not change or certify optimizer
accuracy on ill-conditioned data.

## Training, validation and test data

Report training and held-out metrics separately. Fit all preprocessing solely on
training rows, retain its parameters for inference, choose hyperparameters using
validation data and reserve the test split for final evaluation. Do not infer
generalization from a training loss, KKT residual or duality gap. Metric units and
target scale must be comparable across the models being compared.

The category [experiment](../machine-learning/supervised-learning/regression/experiments/benchmark.py)
uses seed 13027, 48 training/24 held-out observations, the same two-feature
synthetic response and training-fitted scaler for all seven models. Hyperparameters
are fixed before test evaluation. It now reports all four metrics, timings and
available convergence/tree diagnostics. One synthetic split establishes no
universal algorithm superiority. No external data or model downloads are used.

## Independent audit cases

For targets [2,4,6] and predictions [1,3,5], R²=1−3/8=0.625; multiplying both
by 10⁻²⁰⁰ must preserve that score even though direct squared errors underflow.
For a 2,048-element zero target with one prediction 10¹⁵⁵, the correct MSE is
10³¹⁰/2048≈4.8828125×10³⁰⁶, finite despite an overflowing individual square.
These cases and constant decimal/tiny targets reproduced the original defects.
New tests include all seven score methods, normal-scale scikit-learn metric
comparisons, shape/domain errors, high-degree polynomial basis oracles, orthogonal
L1/L2 solutions and SVR outlier/C/epsilon checks. The original failed transcript
is retained in [audit evidence](regression-audit-evidence/metric-investigation.json).

## References

- [Official Regression metric definitions](https://scikit-learn.org/1.8/modules/model_evaluation.html#regression-metrics).
- [R² API and constant-target conventions](https://scikit-learn.org/1.8/modules/generated/sklearn.metrics.r2_score.html).

The repository explicitly defines single-observation R² through its constant-target
rule; it does not claim the reference library defines that case identically.
