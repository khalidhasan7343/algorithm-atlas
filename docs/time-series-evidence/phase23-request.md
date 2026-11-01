# ALGORITHM ATLAS — PHASE 23
# B11: TIME SERIES
## COMPREHENSIVE CODEX MASTER PROMPT
### Six Canonical Algorithms | From-Scratch Python + NumPy | Forecasting | Probabilistic Inference | Independent Oracles | Time-Aware Validation | Full Regression Audit | Review Package

---

# 0. PROJECT IDENTITY

Repository: `algorithm-atlas`
Owner: MD.Khalid Hasan
GitHub: `khalidhasan7343`
License: MIT

Target phase: **23**
Target category: **B11 — Time Series**

Canonical directory:

`machine-learning/time-series`

The owner-provided catalog snapshot identifies exactly six algorithms:

| # | Canonical ID | Algorithm |
|---|---|---|
| 1 | `arima` | ARIMA |
| 2 | `sarima` | SARIMA |
| 3 | `exponential-smoothing` | Exponential Smoothing |
| 4 | `holt-winters` | Holt-Winters |
| 5 | `prophet` | Prophet |
| 6 | `hidden-markov-models` | Hidden Markov Models (HMM) |

All six entries were marked `planned` in the supplied Phase 22 catalog snapshot.

Reinspect the CURRENT repository before changing anything. The current `catalog.yaml` and `AGENTS.md` remain authoritative.

## PRIMARY MISSION

Complete all six B11 algorithms with:

1. Genuine from-scratch Python implementations.
2. NumPy-based mathematical computation.
3. Correct statistical assumptions and mathematical objectives.
4. Forecasting or sequence-inference APIs appropriate to each method.
5. Independent mathematical test oracles.
6. Deterministic and reproducible tests.
7. Time-series-aware validation without future leakage.
8. Numerical stability and convergence verification.
9. Complete educational examples.
10. Exact repository-mandated 25-section algorithm READMEs.
11. Catalog and documentation integration.
12. Full ML and DSA regression verification.
13. Comprehensive Phase 23 review report.
14. Reproducible review ZIP.
15. SHA-256 checksum.
16. JSON review metadata.

Never substitute a simpler algorithm while claiming to implement a more complex one.

Do not commit, push, tag, release, or begin Phase 24 without explicit owner permission.

---

# 1. MANDATORY PHASE 22 OWNER APPROVAL GATE

The supplied catalog snapshot records:

- Phase 22: B10 Optimization.
- Four completed implementation batches.
- Status: `awaiting-review`.
- Owner approval: `pending`.
- Completion report:
  `docs/reviews/optimization/OPTIMIZATION-REVIEW-REPORT.md`

This means implementation completion is not the same as final owner approval.

Before starting Phase 23:

1. Inspect the current Phase 22 review report.
2. Inspect the final Phase 22 review package.
3. Check all ten B10 canonical algorithms.
4. Verify Phase 22 validation evidence.
5. Check whether the owner has explicitly approved the Phase 22 handoff.
6. If explicit approval is missing, ask for it and STOP before making Phase 23 implementation changes.

Do not manufacture an approval record.

Once the Phase 22 approval checkpoint is satisfied, proceed through all six Phase 23 algorithms without requesting permission between ordinary implementation batches.

---

# 2. REPOSITORY PREFLIGHT

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
- `docs/ml-development.md`, if present
- `requirements-ml.txt`
- `requirements-ml-test.txt`
- B1–B10 implementations and relevant review reports
- Phase 22 Optimization review report
- Existing numerical optimization utilities
- Existing probabilistic models
- Existing forecasting utilities
- Existing ML test infrastructure
- Catalog validation scripts
- Documentation generation scripts
- Existing review-package tooling

Record:

- Current branch
- HEAD commit
- Working-tree status
- Pre-existing changes
- Python version
- NumPy version
- pytest version
- Available optional reference libraries
- C++ compiler availability
- CI configuration
- Phase 22 approval status

Never overwrite unrelated owner changes.

Do not run destructive Git cleanup.

---

# 3. EXACT B11 CANONICAL INVENTORY

Verify these canonical paths:

```text
machine-learning/time-series/
├── arima/
├── sarima/
├── exponential-smoothing/
├── holt-winters/
├── prophet/
└── hidden-markov-models/
```

For every algorithm, inspect:

- Catalog identity
- Canonical location
- Existing implementation
- Existing tests
- Existing documentation
- Related algorithms
- Existing examples
- Current statuses
- Existing numerical dependencies

Do not rename canonical IDs.

Do not create duplicate canonical implementations.

Do not expand the B11 syllabus.

If a canonical path differs in the current authoritative catalog, report the discrepancy and follow the current catalog.

---

# 4. IMPLEMENTATION POLICY

Machine Learning requirements:

- Python mandatory.
- NumPy mandatory where mathematically appropriate.
- Core algorithms implemented from scratch.
- Python tests mandatory.
- Independent mathematical verification mandatory.
- C++ optional.

Do not create placeholder C++ implementations.

Existing DSA requirements remain unchanged:

- Python mandatory.
- C++ mandatory.
- C++17 and C++20 verification mandatory.

## External libraries

Do not delegate core implementations to:

- `statsmodels` ARIMA or SARIMAX
- `statsmodels` ExponentialSmoothing
- Prophet forecasting library
- `hmmlearn`
- Ready-made scikit-learn estimators
- Other complete forecasting or HMM implementations

These libraries may serve as independent verification references where appropriate.

Do not require heavyweight optional packages for ordinary CI.

---

# 5. TIME SERIES INPUT CONTRACT

Establish a consistent data contract.

For univariate forecasting methods, define:

- One-dimensional numerical observations
- Chronological ordering
- Regular sampling assumption
- Training series length
- Forecast horizon
- Missing-value policy
- Nonfinite-value policy
- Optional timestamps
- Optional frequency
- Optional exogenous variables, only if actually implemented

For HMM, define:

- Observation sequences
- State space
- Observation alphabet or emission model
- Sequence lengths
- Initial state probabilities
- Transition probabilities
- Emission probabilities

Do not force HMM into an inappropriate forecasting-only API.

Validate:

- Empty sequences
- Too-short sequences
- NaNs
- Infinities
- Invalid shapes
- Irregular timestamps
- Duplicate timestamps
- Invalid frequencies
- Nonpositive forecast horizons
- Unsupported configurations

Do not silently reorder observations.

Do not silently interpolate missing values.

---

# 6. TIME-AWARE VALIDATION AND DATA LEAKAGE

This is a critical Phase 23 requirement.

Use chronological training and testing.

Do not randomly shuffle observations before time-series forecasting evaluation.

Implement or test:

- Holdout evaluation
- Expanding-window evaluation
- Rolling-window evaluation where appropriate
- Multi-step forecasting
- Forecast-horizon alignment
- Training-only parameter estimation
- Training-only normalization
- Training-only differencing initialization
- Correct handling of lag features
- Correct inverse transformations

Never use future observations to calculate training features.

Never fit preprocessing on the entire dataset before splitting.

Document whether evaluation is:

- One-step-ahead with observed-history updates
- Recursive multi-step forecasting
- Direct multi-horizon forecasting

Do not mix these protocols when reporting performance.

---

# 7. IMPLEMENTATION BATCHES

Use four internal batches.

## Batch 1 — Exponential Smoothing Foundations

1. Exponential Smoothing
2. Holt-Winters

## Batch 2 — Autoregressive Integrated Models

3. ARIMA
4. SARIMA

## Batch 3 — Additive Decomposition Forecasting

5. Prophet

## Batch 4 — Probabilistic Sequence Models

6. Hidden Markov Models

For every batch:

1. Inspect existing code.
2. Establish exact mathematical requirements.
3. Implement missing logic.
4. Add independent oracles.
5. Add deterministic tests.
6. Add numerical stability tests.
7. Verify examples.
8. Complete documentation.
9. Run targeted tests.
10. Fix confirmed defects.

Proceed automatically between batches after successful checks.

Stop for genuine mathematical ambiguities, missing owner authorization, or irreducible blockers.

---

# 8. EXPONENTIAL SMOOTHING

Canonical ID:

`exponential-smoothing`

Implement Simple Exponential Smoothing (SES) as the clearly documented foundational variant unless the authoritative repository specification requires another variant.

The standard recursion is:

l_t = alpha * y_t + (1 - alpha) * l_(t-1)

where:

- y_t is the observed value.
- l_t is the smoothed level.
- alpha is the smoothing coefficient.

For the standard no-trend, no-seasonality model, future forecasts are based on the final estimated level.

Required:

1. Input validation.
2. Smoothing parameter validation.
3. Initial level handling.
4. Recursive level updates.
5. Fitted values.
6. Forecast generation.
7. Multi-step forecasts.
8. Optional parameter estimation if supported.
9. Reproducible output.
10. Explicit forecast indexing.

If alpha is estimated, document the actual objective and optimizer.

Do not claim maximum-likelihood estimation when only sum-of-squared-errors minimization was performed.

## Independent tests

Verify:

- Constant series.
- Single observation where supported.
- Alpha approaching zero.
- Alpha equal to one if supported.
- Linear trend diagnostic.
- Missing observations.
- Invalid alpha.
- Invalid horizon.
- Hand-calculated recursive updates.
- Exact multi-step forecasts.
- Deterministic outputs.

Construct an independent reference using the mathematical recursion, not the production helper function.

Optional: compare against `statsmodels` with matching initialization and parameter conventions.

---

# 9. HOLT-WINTERS

Canonical ID:

`holt-winters`

Implement genuine Holt-Winters triple exponential smoothing.

At minimum, support a clearly specified additive-seasonality formulation.

The model must contain:

- Level.
- Trend.
- Seasonal state.
- Smoothing coefficients.
- Seasonal period.
- Forecast horizon.

For a standard additive formulation, document and implement equations equivalent to:

Level:
l_t = alpha * (y_t - s_(t-m)) + (1-alpha) * (l_(t-1) + b_(t-1))

Trend:
b_t = beta * (l_t - l_(t-1)) + (1-beta) * b_(t-1)

Seasonality:
s_t = gamma * (y_t - l_t) + (1-gamma) * s_(t-m)

Forecast:
y_hat_(t+h) = l_t + h*b_t + s_(t-m+((h-1) mod m)+1)

Use a consistent time-index convention and verify all offsets.

Here:

- m is the seasonal period.
- alpha, beta, gamma are smoothing parameters.

If the repository specification requires multiplicative seasonality, implement and test it separately.

Do not claim multiplicative support unless implemented.

Required:

1. Seasonal initialization.
2. Level initialization.
3. Trend initialization.
4. Recursive updates.
5. Fitted values.
6. Seasonal forecasts.
7. Multi-step forecasts.
8. Seasonal period validation.
9. Minimum history validation.
10. Optional parameter fitting.

## Required tests

- Constant series.
- Trend-only series.
- Additive seasonal series.
- Seasonal period of two.
- Multiple seasonal cycles.
- Multi-step horizon.
- Seasonal indexing.
- Hand-computed update equations.
- Invalid coefficients.
- Insufficient observations.
- Missing values.
- Nonfinite values.
- Deterministic output.

Verify that the implementation uses the actual seasonal state and does not simply repeat the last observations.

---

# 10. ARIMA

Canonical ID:

`arima`

Implement genuine AutoRegressive Integrated Moving Average.

ARIMA(p,d,q) combines:

- Autoregression.
- Differencing.
- Moving-average innovations.

The mathematical model must explicitly define the lag-polynomial convention.

A standard formulation is:

phi(B) * (1-B)^d * y_t = theta(B) * epsilon_t

where:

- B is the backshift operator.
- p is the autoregressive order.
- d is the differencing order.
- q is the moving-average order.
- epsilon_t is the innovation.

Sign conventions must be explicit.

## Mandatory components

1. Validate p, d, q.
2. Apply differencing.
3. Construct autoregressive terms.
4. Construct moving-average innovation terms.
5. Estimate model parameters.
6. Compute residuals consistently.
7. Generate fitted values.
8. Forecast differenced values.
9. Invert differencing correctly.
10. Generate forecasts in original units.
11. Define intercept or drift behavior.
12. Bound optimization iterations.
13. Report convergence status.
14. Handle insufficient history.

Choose a mathematically legitimate educational estimation method, such as conditional sum of squares, and document it precisely.

If using conditional sum of squares:

- State the residual initialization.
- State the parameter objective.
- State the optimization method.
- State any parameter constraints.
- Do not claim exact maximum-likelihood equivalence.

The moving-average component must use estimated innovations, not raw lagged observations.

Do not implement AR(p) and label it ARIMA(p,d,q).

## Required tests

- ARIMA(0,0,0).
- ARIMA(1,0,0).
- ARIMA(0,1,0).
- ARIMA(0,0,1).
- Mixed AR and MA terms.
- First-order differencing.
- Second-order differencing.
- Inverse differencing.
- Constant series.
- Synthetic autoregressive series.
- Synthetic moving-average series.
- Invalid orders.
- Insufficient history.
- Nonfinite observations.
- Multi-step forecasts.
- Parameter estimation.
- Forecast alignment.

## Independent oracles

Use:

- Exact lag-polynomial calculations.
- Hand-computed differencing.
- Hand-computed innovation recursions.
- Analytical AR(1) forecasts.
- Independently computed objective values.
- Optional `statsmodels` comparison under matched assumptions.

Parameter comparisons must account for estimation method and model conventions.

---

# 11. SARIMA

Canonical ID:

`sarima`

Implement Seasonal ARIMA with explicit nonseasonal and seasonal components.

A standard SARIMA(p,d,q)(P,D,Q)_s formulation uses:

phi(B) * Phi(B^s) * (1-B)^d * (1-B^s)^D * y_t
=
theta(B) * Theta(B^s) * epsilon_t

where:

- p,d,q are nonseasonal orders.
- P,D,Q are seasonal orders.
- s is the seasonal period.

## Required components

1. Nonseasonal differencing.
2. Seasonal differencing.
3. Nonseasonal AR polynomial.
4. Seasonal AR polynomial.
5. Nonseasonal MA polynomial.
6. Seasonal MA polynomial.
7. Correct multiplicative polynomial interactions.
8. Parameter estimation.
9. Innovation recursion.
10. Forecast generation.
11. Seasonal inverse differencing.
12. Nonseasonal inverse differencing.
13. Convergence status.
14. Valid seasonal periods.

Important:

Do not implement only seasonal differencing followed by ordinary ARIMA and claim full SARIMA support.

Seasonal AR and MA terms must be genuinely represented.

Polynomial interactions must be correct.

## Required tests

- Zero seasonal orders.
- Seasonal AR(1).
- Seasonal MA(1).
- Seasonal differencing.
- Mixed seasonal and nonseasonal terms.
- Seasonal period validation.
- Seasonal polynomial multiplication.
- Inverse seasonal differencing.
- Multi-step seasonal forecasting.
- Insufficient seasonal history.
- Synthetic seasonal data.
- Deterministic output.
- Invalid model orders.

Verify that SARIMA with all seasonal orders zero and no seasonal differencing reduces consistently to the corresponding ARIMA formulation under matching settings.

Use independent lag-polynomial calculations as a core oracle.

Optional: compare against `statsmodels` with aligned model assumptions.

---

# 12. PROPHET — SPECIFICATION-FIRST IMPLEMENTATION

Canonical ID:

`prophet`

The catalog identifies Prophet as an additive forecasting framework with trend and seasonal assumptions.

Prophet is not merely a single smoothing equation.

Before implementation:

1. Identify the authoritative Prophet mathematical formulation.
2. Document the chosen educational subset.
3. Define supported trend types.
4. Define seasonal components.
5. Define changepoints.
6. Define parameter estimation.
7. Define optional holidays or regressors.
8. Define limitations relative to the complete Prophet library.

A standard additive decomposition is:

y(t) = g(t) + s(t) + h(t) + epsilon_t

where:

- g(t) is trend.
- s(t) is seasonality.
- h(t) is holiday/event contribution when supported.
- epsilon_t is observation noise.

For an educational from-scratch implementation, a defensible scope is:

- Piecewise-linear trend.
- Explicit changepoints.
- Fourier seasonal basis.
- Additive component fitting.
- Documented regularization.
- Forecast generation.

Use a legitimate mathematical objective.

For example, a Gaussian-noise additive model can be fitted with a documented least-squares or MAP-style regularized objective.

Clearly distinguish a simplified educational implementation from full Prophet functionality.

Do not claim full library parity.

Do not import the Prophet package and delegate training or forecasting to it.

Do not substitute ordinary linear regression and label it Prophet without the defining trend and seasonal structure.

## Required tests

- Linear trend.
- Piecewise-linear trend.
- Known changepoint.
- Fourier seasonal component.
- Multiple seasonal components if supported.
- Trend extrapolation.
- Future timestamp generation.
- Timestamp normalization.
- Irregular timestamps.
- Duplicate timestamps.
- Missing timestamps.
- Invalid seasonal periods.
- Invalid changepoint configuration.
- Parameter fitting.
- Forecast decomposition.
- Deterministic results.

## Independent oracle

Construct the design matrix independently.

Verify:

- Trend basis.
- Changepoint basis.
- Fourier terms.
- Fitted coefficients.
- Predicted components.
- Total forecast.

For a linear-Gaussian objective, compare against an independent NumPy least-squares or regularized normal-equation solution.

Optional: compare against the Prophet library with aligned components, priors and fitting assumptions.

Do not claim numerical equivalence when the reference uses a different inference method.

If a sufficiently defensible Prophet specification cannot be established, stop this algorithm, document the blocker, and request owner approval rather than inventing an implementation.

Continue unrelated B11 work where permitted.

---

# 13. HIDDEN MARKOV MODELS

Canonical ID:

`hidden-markov-models`

Implement a genuine Hidden Markov Model.

Use a clearly documented discrete-state, categorical-emission formulation as the educational baseline.

Required parameters:

- Initial state distribution pi.
- Transition matrix A.
- Emission matrix B.
- Number of hidden states.
- Observation alphabet.

Required algorithms:

1. Forward algorithm.
2. Backward algorithm.
3. Sequence likelihood.
4. Viterbi decoding.
5. Posterior state probabilities.
6. Baum-Welch / EM training.
7. Model parameter validation.
8. Reproducible initialization.
9. Convergence reporting.
10. Prediction or inference interfaces appropriate to the model.

Do not implement only Viterbi decoding and claim a complete trainable HMM.

## Numerical stability

Use scaling or log-space calculations.

Prevent probability underflow on longer sequences.

Handle impossible observations consistently.

Do not silently divide by zero during EM.

## Required mathematical verification

For small models:

- Enumerate all hidden-state sequences.
- Compute exact observation likelihood.
- Compare with forward recursion.
- Compare with backward recursion.
- Verify Viterbi best-path probability.
- Verify posterior normalization.
- Verify transition row normalization.
- Verify emission row normalization.
- Verify initial probability normalization.

## Baum-Welch requirements

Verify:

- Gamma posterior calculations.
- Xi pairwise posterior calculations.
- Expected transition counts.
- Expected emission counts.
- Parameter updates.
- Correct sequence-boundary handling.
- Multiple independent sequences if supported.
- Convergence behavior.
- Likelihood history.

Test EM monotonicity only under the documented mathematical assumptions and numerical tolerances.

Do not claim global optimality.

## Edge cases

- One hidden state.
- One observation symbol.
- Very short sequence.
- Repeated symbols.
- Unreachable states.
- Zero-probability emissions.
- Invalid probability matrices.
- Nonfinite probabilities.
- Unknown symbols.
- Multiple sequences.
- Long-sequence stability.

Optional: compare against `hmmlearn` with aligned initialization, emission type and training settings.

---

# 14. SHARED TIME SERIES UTILITIES

Create reusable utilities only when justified.

Possible components:

- Lag construction.
- Differencing.
- Inverse differencing.
- Forecast horizon validation.
- Chronological splitting.
- Rolling evaluation.
- Seasonal indexing.
- Stable probability calculations.
- Numerical parameter optimization.

Avoid unnecessary abstraction.

Do not introduce circular imports.

Preserve each canonical algorithm's independently understandable implementation.

Shared utilities must have dedicated tests.

---

# 15. OPTIMIZATION INTEGRATION WITH B10

Phase 22 implemented optimization methods including:

- Batch Gradient Descent.
- Stochastic Gradient Descent.
- Mini-Batch Gradient Descent.
- Momentum.
- RMSProp.
- Adam.
- AdamW.
- L-BFGS.
- Genetic Algorithms.
- Simulated Annealing.

Inspect these implementations before choosing a parameter-estimation strategy.

Reuse suitable mathematical utilities where practical, but do not force unsuitable optimizers into statistical models.

If a B10 optimizer is reused:

1. Verify its objective contract.
2. Verify gradient correctness.
3. Verify convergence handling.
4. Add B10/B11 compatibility tests.
5. Preserve its existing canonical implementation.

Do not alter previously approved B10 code without demonstrated necessity.

---

# 16. FORECASTING METRICS

Implement or independently verify suitable evaluation metrics:

- MAE.
- MSE.
- RMSE.
- MAPE where mathematically valid.
- sMAPE if explicitly documented.
- MASE where appropriate.

Handle:

- Zero denominators.
- Empty evaluation sets.
- Nonfinite predictions.
- Shape mismatches.
- Multi-step alignment.

Do not report MAPE as meaningful when actual observations are zero without documenting the chosen handling.

Metrics must use genuine out-of-sample predictions.

Do not report training error as test error.

---

# 17. INDEPENDENT ORACLE MATRIX

Each algorithm must have independent verification.

| Algorithm | Primary independent oracle |
|---|---|
| Exponential Smoothing | Hand-calculated recursive level updates |
| Holt-Winters | Independent level/trend/seasonal recursions |
| ARIMA | Lag-polynomial, innovation and inverse-differencing calculations |
| SARIMA | Seasonal polynomial expansion and independent forecast recursions |
| Prophet | Independent trend/Fourier design matrix and optimization objective |
| HMM | Exhaustive hidden-state enumeration and probability identities |

Optional external references:

- `statsmodels`.
- Prophet library.
- `hmmlearn`.

These are verification tools, not implementation dependencies.

Do not use the same production helper as both implementation and oracle.

---

# 18. SYNTHETIC DATASETS

Create deterministic, lightweight test datasets.

Include:

- Constant signal.
- Linear trend.
- Trend with Gaussian noise.
- Additive seasonality.
- Seasonal trend.
- Stationary AR process.
- MA process.
- Integrated random walk.
- Seasonal autoregressive process.
- Piecewise-linear trend.
- Hidden-state categorical sequences.

Generate data with fixed seeds.

Document the generating equations.

Avoid external downloads.

Do not require large datasets or GPUs.

---

# 19. MATHEMATICAL CORRECTNESS AUDIT

For every algorithm, verify:

1. Mathematical assumptions.
2. Input contract.
3. State initialization.
4. Parameter estimation.
5. Recursion equations.
6. Forecast equations.
7. Forecast horizon indexing.
8. Inverse transformations.
9. Numerical stability.
10. Convergence reporting.
11. Edge-case behavior.
12. Independent oracle agreement.

For stochastic or statistical estimators, distinguish:

- Correct algorithm implementation.
- Parameter estimation quality.
- Forecast accuracy.
- Statistical consistency.
- Theoretical guarantees.

Do not use good forecast accuracy alone as proof of mathematical correctness.

---

# 20. NUMERICAL STABILITY

Audit:

- Singular design matrices.
- Ill-conditioned optimization.
- Nonstationary series.
- Noninvertible MA parameters.
- Overflow.
- Underflow.
- Probability underflow.
- Division by zero.
- Invalid smoothing coefficients.
- Invalid seasonal periods.
- Degenerate observations.
- Constant series.
- Nonfinite residuals.
- Divergent optimization.
- Invalid likelihood values.
- Excessive memory usage.

Use stable linear algebra.

Use log probabilities or scaling where needed.

Do not silently replace invalid results with arbitrary values.

---

# 21. MODEL IDENTIFIABILITY AND LIMITATIONS

Document algorithm-specific limitations.

For ARIMA and SARIMA:

- Stationarity assumptions.
- Invertibility assumptions.
- Parameter identifiability.
- Estimation method limitations.
- Sensitivity to model order.
- Seasonal period assumptions.

For smoothing models:

- Initialization sensitivity.
- Trend assumptions.
- Seasonal assumptions.
- Extrapolation limitations.

For Prophet:

- Changepoint assumptions.
- Seasonality basis.
- Regularization.
- Limited educational scope.
- Differences from official Prophet inference.

For HMM:

- Label switching.
- Local EM optima.
- Hidden-state identifiability.
- Emission assumptions.
- Sequence-length sensitivity.

Do not promise universally accurate forecasts.

---

# 22. PERFORMANCE AND COMPLEXITY

For each algorithm, document:

- Training complexity.
- Forecasting complexity.
- Memory complexity.
- Dependence on series length.
- Dependence on model orders.
- Dependence on seasonal period.
- Dependence on forecast horizon.
- Dependence on hidden-state count where relevant.
- Optimization iteration cost.

For HMM, explain the computational cost of forward-backward and Viterbi.

For ARIMA/SARIMA, explain the cost of repeated likelihood or residual evaluations.

Benchmark only with executed measurements.

Do not fabricate runtime or memory results.

---

# 23. EDUCATIONAL EXAMPLES

Create one executable, meaningful example per algorithm.

## Exponential Smoothing

Demonstrate level smoothing and future forecasts.

## Holt-Winters

Demonstrate trend plus additive seasonality.

## ARIMA

Demonstrate fitting and forecasting an integrated process.

## SARIMA

Demonstrate a seasonal synthetic series.

## Prophet

Demonstrate piecewise trend and Fourier seasonality.

## HMM

Demonstrate sequence likelihood, decoding and training.

All examples must:

- Use small datasets.
- Run without network access.
- Use deterministic seeds where relevant.
- Show actual outputs.
- Match the implementation.
- Avoid fabricated performance claims.

---

# 24. DOCUMENTATION REQUIREMENTS

Every B11 algorithm must follow the exact 25-section README structure required by `AGENTS.md`.

Do not invent a different heading structure.

Each README must explain:

- Problem definition.
- Mathematical model.
- Statistical assumptions.
- Inputs and outputs.
- Core equations.
- Initialization.
- Training or estimation.
- Forecasting or inference.
- Pseudocode.
- Correctness reasoning.
- Complexity.
- Numerical stability.
- Worked example.
- Python implementation.
- Tests.
- Independent oracle.
- Applications.
- Limitations.
- Related algorithms.
- References.

Use actual verified examples.

Document C++ as optional for ML.

Do not create fake C++ files.

---

# 25. CATEGORY README

Create or update:

`machine-learning/time-series/README.md`

Include:

1. Time-series learning overview.
2. Six canonical algorithms.
3. Forecasting versus sequence modeling.
4. Trend and seasonality.
5. Stationarity and differencing.
6. Autoregressive and moving-average terms.
7. Exponential smoothing.
8. Additive decomposition.
9. Hidden-state probabilistic modeling.
10. Chronological validation.
11. Forecast metrics.
12. Numerical stability.
13. Algorithm comparison table.
14. Learning order.
15. Canonical implementation links.

Do not duplicate full algorithm implementations in the category README.

---

# 26. CATALOG AND DOCUMENTATION INTEGRATION

Update relevant repository records:

- `catalog.yaml`
- `docs/progress.md`
- `docs/learning-roadmap.md`
- `docs/algorithm-index.md`
- B11 category README
- Root README if necessary

Preserve:

- All DSA implementations.
- All B1–B10 implementations.
- All previously approved phase records.
- Existing canonical IDs.
- Existing canonical paths.
- Existing shared memberships.
- Existing review reports.

Important:

B8 Dynamic Policy Optimization remains owner-approved as blocked.

Do not rename, replace, implement or mark it complete during Phase 23.

Do not mark Phase 23 owner-approved.

---

# 27. TARGETED TESTING

Run tests for all six algorithms.

Suggested targeted command:

```bash
python -m pytest machine-learning/time-series -q
```

Also execute:

- Mathematical recursion tests.
- Parameter estimation tests.
- Forecast alignment tests.
- Inverse differencing tests.
- Seasonal indexing tests.
- Independent oracle tests.
- HMM probability tests.
- HMM EM tests.
- Numerical stability tests.
- Reproducibility tests.
- Invalid-input tests.
- Chronological leakage tests.
- Synthetic forecasting tests.

Do not weaken assertions merely to pass tests.

---

# 28. FULL REGRESSION TESTING

Run regression checks across:

- B1 Regression.
- B2 Classification.
- B3 Ensemble Methods.
- B4 Clustering.
- B5 Dimensionality Reduction.
- B6 Association Rule Learning.
- B7 Neural Networks and Deep Learning.
- B8 Reinforcement Learning.
- B9 Graph-Based Learning.
- B10 Optimization.
- B11 Time Series.
- DSA Python.
- DSA C++17.
- DSA C++20.
- Shared numerical infrastructure.
- Catalog validation.
- Documentation generation.
- CI-equivalent checks.

Pay particular attention to B10 optimization compatibility.

Do not silently modify previously approved algorithms.

---

# 29. REQUIRED VALIDATION COMMANDS

Run:

```bash
python scripts/validate_catalog.py
python scripts/generate_catalog_docs.py --check
python -m pytest --require-cpp
```

Also run targeted B11 tests.

If the full suite cannot finish:

1. Split tests into bounded groups.
2. Execute every feasible group.
3. Record exact commands.
4. Record pass/fail/skip counts.
5. Identify unexecuted checks.
6. Explain environmental limitations.

Never claim an unexecuted test passed.

---

# 30. NEGATIVE INFRASTRUCTURE TESTS

Verify:

- Missing required ML Python implementation is rejected.
- Missing ML Python tests are rejected.
- Invalid canonical IDs are rejected.
- Duplicate canonical paths are rejected.
- Missing README sections are detected.
- Documentation drift is detected.
- B11 tests are discovered by CI.
- Optional ML C++ follows repository policy.
- Missing mandatory DSA C++ is rejected.
- C++17/C++20 requirements remain enforced.
- Existing blocked entries remain valid.

Do not weaken validators.

---

# 31. SECURITY AND RESOURCE LIMITS

Inspect for:

- Unbounded optimization.
- Infinite loops.
- Excessive model orders.
- Excessive seasonal periods.
- Excessive HMM state counts.
- Large accidental allocations.
- Unsafe file loading.
- Arbitrary code execution.
- Network downloads.
- Unexpected subprocess calls.
- Hidden secrets.
- Global RNG mutation.

Keep mandatory tests CPU-friendly.

Do not require GPUs.

Do not download external datasets.

---

# 32. PHASE 23 REVIEW REPORT

Create:

`docs/reviews/time-series/TIME-SERIES-REVIEW-REPORT.md`

Follow stricter repository conventions if they exist.

Include:

1. Phase identity.
2. Category identity.
3. Six-algorithm inventory.
4. Canonical paths.
5. Implementation status by algorithm.
6. Existing versus new work.
7. Exponential Smoothing correctness.
8. Holt-Winters correctness.
9. ARIMA correctness.
10. SARIMA correctness.
11. Prophet specification and scope.
12. HMM correctness.
13. Parameter estimation verification.
14. Forecasting verification.
15. Independent mathematical oracles.
16. HMM exact likelihood verification.
17. HMM Viterbi verification.
18. HMM EM verification.
19. Time-series leakage audit.
20. Numerical stability.
21. Reproducibility.
22. Synthetic dataset tests.
23. Edge-case tests.
24. Educational examples.
25. Documentation validation.
26. Catalog validation.
27. B1–B10 regression results.
28. DSA regression results.
29. C++17/C++20 results.
30. CI-equivalent checks.
31. Dependencies.
32. Files created.
33. Files modified.
34. Bugs discovered.
35. Fixes applied.
36. Known limitations.
37. Unresolved blockers.
38. Exact reproduction commands.
39. Review package paths.
40. Owner approval: pending.

Use actual test results.

Do not fabricate counts, benchmark results or verification evidence.

---

# 33. PHASE 23 REVIEW PACKAGE

Create:

```text
artifacts/review-packages/time-series/
├── algorithm-atlas-time-series-review.zip
├── algorithm-atlas-time-series-review.zip.sha256
└── algorithm-atlas-time-series-review.json
```

Include:

- All six B11 implementations.
- All B11 tests.
- All B11 algorithm READMEs.
- B11 category README.
- B11 review report.
- Relevant shared utilities.
- Relevant B10 optimization utilities.
- Relevant ML source and tests.
- Relevant DSA source and tests.
- `AGENTS.md`.
- `catalog.yaml`.
- Root `README.md`.
- `pyproject.toml`.
- `conftest.py`.
- Dependency configuration.
- Validation scripts.
- Documentation generation scripts.
- CI configuration.

Exclude:

- `.git`.
- Virtual environments.
- Python caches.
- pytest caches.
- Compiled binaries.
- Secrets.
- Large datasets.
- Model checkpoints.
- Historical review ZIPs.
- Nested ZIPs.
- Temporary files.

Verify:

1. ZIP opens successfully.
2. ZIP CRC passes.
3. Extraction paths are safe.
4. Required files are present.
5. SHA-256 checksum matches.
6. JSON metadata matches.
7. Independent extraction succeeds.
8. Catalog validation works from extracted source.
9. Documentation validation works from extracted source.
10. Relevant tests execute from extracted source.

Record any verification steps that could not run.

---

# 34. FINAL PHASE 23 COMPLETION SUMMARY

Present:

| Field | Result |
|---|---|
| Phase | 23 |
| Category | B11 — Time Series |
| Catalog algorithms | 6 |
| Implemented algorithms | Actual count |
| Completed batches | Actual count |
| Exponential Smoothing tests | Actual results |
| Holt-Winters tests | Actual results |
| ARIMA tests | Actual results |
| SARIMA tests | Actual results |
| Prophet tests | Actual results |
| HMM tests | Actual results |
| Independent oracles | Actual results |
| Forecast alignment | Actual results |
| Inverse differencing | Actual results |
| Seasonal correctness | Actual results |
| HMM inference | Actual results |
| HMM EM training | Actual results |
| Numerical stability | Actual results |
| Reproducibility | Actual results |
| Data leakage audit | Actual result |
| B1–B10 regression | Actual results |
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

Also provide a per-algorithm table:

| Algorithm | Implementation | Tests | Oracle | Documentation | Status |
|---|---|---|---|---|---|

List:

- Completed algorithms.
- Incomplete algorithms.
- Blocked algorithms.
- Failed tests.
- Skipped tests.
- Unexecuted checks.
- Statistical limitations.
- Numerical limitations.
- Dependency changes.
- Infrastructure changes.
- Reproduction commands.

Do not claim six out of six complete if any mandatory algorithm remains blocked or unfinished.

---

# 35. MANDATORY STOP CONDITION

After completing Phase 23 implementation, validation, documentation and review packaging:

**STOP AND WAIT FOR EXPLICIT OWNER APPROVAL.**

Do not:

- Start Phase 24.
- Start B12 Anomaly Detection.
- Commit.
- Push.
- Tag.
- Release.
- Publish.
- Mark Phase 23 owner-approved.
- Modify the B8 DPO decision.
- Invent additional algorithms.
- Hide failed tests.
- Fabricate verification results.

The owner must review the Phase 23 report and ZIP before authorizing the next phase.

---

# 36. EXECUTION ORDER

STEP 1 — Verify Phase 22 final owner approval.

STEP 2 — Inspect current repository and authoritative catalog.

STEP 3 — Verify all six B11 canonical entries.

STEP 4 — Implement Exponential Smoothing and Holt-Winters.

STEP 5 — Implement ARIMA and SARIMA.

STEP 6 — Implement Prophet using an explicitly documented mathematical specification.

STEP 7 — Implement Hidden Markov Models with genuine inference and EM training.

STEP 8 — Run independent mathematical oracles.

STEP 9 — Run time-series leakage and numerical stability audits.

STEP 10 — Complete exact 25-section READMEs.

STEP 11 — Update category documentation and catalog statuses.

STEP 12 — Run targeted tests.

STEP 13 — Run full ML and DSA regression checks.

STEP 14 — Run catalog, documentation and CI-equivalent validation.

STEP 15 — Produce Phase 23 review report.

STEP 16 — Generate and verify ZIP, SHA-256 and JSON metadata.

STEP 17 — Present final results and STOP for owner review.

Do not request confirmation between ordinary batches.

Ask for owner input only when a real approval or specification blocker exists.

**BEGIN PHASE 23 ONLY AFTER THE PHASE 22 OWNER APPROVAL CHECKPOINT IS SATISFIED.**