# Prophet — Educational Linear/Fourier Subset

## 1. Algorithm Name

This canonical implements a declared educational subset of the Prophet additive framework:continuous piecewise-linear trend,explicit changepoints and Fourier seasonal components. Gaussian ridge fitting is an explicit departure from official sparse changepoint inference;full Prophet library parity is not claimed.

## 2. Overview

Fit y(t)=g(t)+s(t)+error using a continuous changepoint trend and one or more specified periodic Fourier bases. The task is additive regularized forecasting with known candidate changepoints/periods,not generic ordinary regression labeled as a complete Prophet replacement.

## 3. Problem Statement

fit accepts2..512 finite regular observations with optional numeric/whole-second datetime64 timestamps. changepoints are0..8 strictly increasing interior training positions in elapsed sample steps. seasonalities is up to4(period,Fourier_order) pairs;period2..10000 samples,order1..8;duplicate periods fail. Total design columns<=32. regularization is0..1000. Forecast horizon1..128.

coef_,design_matrix_,penalty_mask_ expose the declared fit. components_ contains trend,each seasonality,seasonal sum and total for training. forecast_components(h) returns the same decomposition for future sample positions. forecast_index(h) returns real future timestamps. rank_,design_rank_,singular_values_,objective_,optimality_,status_,converged_ describe the direct solve.

## 4. Why Do We Need This Algorithm?

A fixed global line cannot change slope at a specified training changepoint,and a single level cannot express declared periodic waves. Explicit hinge and Fourier bases make these contributions inspectable in one regularized additive model.

## 5. Real-World Applications

Small regular numeric series with known candidate changepoints and seasonal periods support additive forecasting and component interpretation. This declared educational subset is useful for studying trend/seasonal assumptions without claiming the complete official library feature set.

## 6. Core Intuition

Use tau=t/(n-1),g(t)=beta0+beta1*tau+sum(delta_j*max(t-c_j,0)/(n-1)). Each period P contributes sin(2*pi*k*t/P),cos(2*pi*k*t/P),k1..K. Minimize ||y-Xb||²/(2n)+lambda*||Db||²/2,where D masks changepoint/Fourier coefficients and leaves intercept/base slope unpenalized. Solve [X;sqrt(n*lambda)D]b=[y;0] with NumPy SVD least squares. This corresponds to Gaussian penalized coefficients,not the official Laplace/L1 changepoint prior.

Hinge columns alter slopes continuously after known changepoints. Sine/cosine pairs represent smooth periodic effects with flexible phase. Regularization shrinks those added effects while preserving the base linear trend. Forecasting extends the final fitted slope and the declared seasonal waves.

## 7. Prerequisites

Linear least squares,SVD,hinge functions,Fourier sine/cosine bases and Gaussian ridge penalties are prerequisites. Understand training-only time normalization,rank deficiency and the distinction from a Laplace changepoint prior.

## 8. Step-by-Step Working Process

Validate the mathematical subset before fitting. Learn trend-duration normalization only from training length. Build explicit hinge/Fourier columns. Append masked ridge rows and solve with SVD rather than forming an unstable inverse. Compute component sums and an actual first-order optimality residual. Forecast future elapsed positions using the frozen training duration and coefficients.

## 9. Pseudocode

```text
t <- chronological elapsed sample positions
X <- intercept,normalized trend,hinges,Fourier columns
D <- mask excluding intercept/base slope
beta <- SVD_least_squares([X;sqrt(n*lambda)D],[y;0])
report rank and optimality
future_X <- same basis at n..n+h-1,using training duration
return trend component+seasonal components
```

## 10. Dry Run

For y=4+.2*t+.6*max(t-15,0),an explicit changepoint15,no seasonality and lambda0 recover the continuous trend and extrapolate its changed slope. For a seven-sample sine/cosine signal,declared period7/order1 recovers phase and amplitude. Tests build the full matrix independently,including multiple seasonalities and positive penalties.

## 11. Time Complexity

Let n be training length,k<=32 total columns. Basis construction costs O(n*k);SVD of the augmented(n+k)-by-k system costs O((n+k)*k²). No iterative statistical inference or MCMC runs. Forecast/decomposition costs O(h*k).

## 12. Space Complexity

Training stores O(n*k) design plus O(k²) ridge/SVD work and O(n) component arrays. Forecasts use O(h*k) basis and O(h*number_of_components) returned arrays. Explicit column caps prevent accidental large seasonal designs.

## 13. Python Implementation

The canonical [Prophet](python/solution.py) performs the stated mechanism from scratch with NumPy/standard library. Shared [B11 contracts](../../../docs/time-series-conventions.md) define validation and ownership. No ready-made forecasting estimator is called. See [meaningful tests](tests/test_python.py) and the executable [example](python/example.py).

## 14. C++ Implementation

C++ is optional under the authorized ML policy and is not implemented here. No placeholder C++ files or C++ pass claims. Existing DSA Python/C++17/C++20 requirements are preserved.

## 15. Input and Output Examples

From the repository root:

```sh
.venv/bin/python machine-learning/time-series/prophet/python/example.py
```

Actual captured output:

```json
{"status": "svd-solved", "converged": true, "design_rank": 5, "objective": 0.21062965, "forecast": [14.19055167, 15.20034129, 15.62430304, 15.32863865], "trend": [14.17609088, 14.4223705, 14.66865012, 14.91492975], "seasonal": [0.0144608, 0.77797079, 0.95565292, 0.4137089], "index": [56.0, 57.0, 58.0, 59.0]}
```

Re-run targeted verification with `.venv/bin/python -m pytest machine-learning/time-series/prophet -q`.

## 16. Edge Cases

Pure linear trend works with empty changepoints/seasonalities. Zero penalty permits rank deficiency;the documented NumPy minimum-norm solution and actual rank remain visible. Aliased Fourier columns do not prove identifiability. Invalid periods,orders,duplicate/interior-external changepoints,nonfinite data and irregular timestamps fail. Failed refits preserve prior state.

## 17. Advantages

The defining trend hinges and Fourier mechanisms are visible and independently testable. Additive components can be inspected separately. A stable direct convex solve avoids unnecessary nonlinear fitting while exposing actual numerical optimality diagnostics.

## 18. Disadvantages and Limitations

No logistic growth,automatic changepoints,holiday/calendar database,extra regressors,robust noise model,MCMC,uncertainty intervals or automatic seasonal detection. Ridge changepoint priors differ from official Prophet Laplace priors. Periods/changepoints are user assumptions;collinearity and short histories impair interpretation. Accurate fitted curves do not establish reliable future forecasts.

## 19. When to Use It

Use this educational subset to understand additive changepoint/Fourier forecasting,with known candidate trend changes and regular sampling. Evaluate extrapolation on chronological holdouts and report the declared regularization/objective rather than comparing incompatible full-library defaults.

## 20. When Not to Use It

Use the complete official library when its automatic calendar handling,logistic constraints or posterior uncertainty are required. Do not infer an unseen changepoint from future targets,normalize on the full dataset,or call a hinge-free/season-free straight line a full Prophet implementation.

## 21. Comparison With Related Algorithms

Holt-Winters updates local phase states recursively;this subset globally fits fixed Fourier waves and trend hinges. SARIMA models lagged dynamics/innovations. Ordinary straight-line regression lacks the defining changepoint and seasonal columns. Official Prophet uses additional priors/inference/features outside the declared subset.

## 22. Interview Questions

Why divide trend time by training duration only? Future timestamps must not change fitted coefficients. Why do hinge columns preserve continuity? They are0 before the changepoint and start at0 there. Does ridge reproduce official sparse priors? No;the different Gaussian prior is intentional and documented.

## 23. Practice Problems

Construct the design matrix without production helpers. Derive the masked normal equations and compare predictions to SVD. Show continuity at a changepoint. Test a second seasonality and an aliased design. Compare training error with honest expanding-window recursive holdout error.

## 24. References

[https://www.tandfonline.com/doi/abs/10.1080/00031305.2017.1380080](https://www.tandfonline.com/doi/abs/10.1080/00031305.2017.1380080)

[https://github.com/facebook/prophet/blob/main/docs/_docs/trend_changepoints.md](https://github.com/facebook/prophet/blob/main/docs/_docs/trend_changepoints.md)

[https://github.com/meta/prophet/blob/main/docs/_docs/seasonality,_holiday_effects,_and_regressors.md](https://github.com/meta/prophet/blob/main/docs/_docs/seasonality,_holiday_effects,_and_regressors.md)

The [phase conventions](../../../docs/time-series-conventions.md) distinguish educational variants from full libraries and record the actual estimation objective. References support mathematics;executed local tests supply implementation evidence.

## 25. Author Attribution

Maintainer: **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas),[MIT license](../../../LICENSE),[contribution policy](../../../CONTRIBUTING.md).

