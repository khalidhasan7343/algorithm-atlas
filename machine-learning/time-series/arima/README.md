# ARIMA

## 1. Algorithm Name

ARIMA combines autoregressive observations,moving-average innovations and integration. This implementation estimates a real conditional innovation recursion from scratch;nonzero q always refers to past errors,not lagged observations.

## 2. Overview

For chronological univariate observations,fit ARIMA(p,d,q) using conditional sum of squares and forecast the transformed process before inverting all differences. p,q control short-memory dynamics;d controls integration. Statistical forecast quality depends on the selected orders and data assumptions.

## 3. Problem Statement

order=(p,d,q),p/q0..2,d0..2;include_intercept is boolean. fit requires a finite series whose post-difference length exceeds burn=max(p,q) by at least max(4,2k+1),where k is free-parameter count. max_iter1..400;tolerance1e-12..1. Common regular timestamps and bounded horizons apply. filter(y,parameters) accepts explicit physical coefficient arrays within the declared stability boxes.

params_ contains the original-unit innovation intercept and AR/MA components. innovations_ contains raw-unit conditional innovations after differencing,with the initial burn entries0. fitted_values_/residuals_ align with original y and have unavailable prefixes marked NaN. normalization_scale_,objective_,gradient_norm_,n_iter_,status_ and converged_ expose estimation diagnostics. forecast(h) returns owned original-unit point predictions.

## 4. Why Do We Need This Algorithm?

Lagged observations and past unpredictable shocks express different temporal information. ARIMA combines those mechanisms with explicit differencing instead of treating every series as a fixed level or repeating a last cycle.

## 5. Real-World Applications

Small low-order numeric series with plausible lag dependence,innovation effects and specified integration are suitable forecasting baselines. Model orders and coefficients require training-only selection and honest recursive holdout evaluation.

## 6. Core Intuition

A(B)=1-sum(phi_i B^i),M(B)=1+sum(theta_j B^j),z=(1-B)^d y,and A(B)z=c+M(B)epsilon. Starting at burn=max(p,q),epsilon_t=z_t-c-sum(phi_i*z_(t-i))-sum(theta_j*epsilon_(t-j));earlier conditional errors are0. Objective0.5*mean(epsilon[burn:]**2) uses only training-scaled z. Each component is .95*tanh(raw_j)/order,which is a sufficient stationarity/invertibility box rather than the full admissible region.

AR terms propagate recent transformed observations;MA terms correct using inferred innovations. Differencing removes a specified polynomial level structure. Unknown future shocks have expectation0,while the known final training innovations still influence the first q forecast steps.

## 7. Prerequisites

Lag polynomials,differencing,inversion of retained histories,conditional innovations and the chain rule are prerequisites. Understand [L-BFGS](../../optimization/l-bfgs/README.md),local optimization and why CSS differs from exact maximum likelihood.

## 8. Step-by-Step Working Process

Validate data,derive all training-only difference histories and a positive training scale. Decode bounded physical components. Recurse innovations and their analytic parameter sensitivities. Reuse the unchanged B10 L-BFGS canonical to minimize CSS. Preserve its actual convergence/budget/search-failure status. Forecast transformed observations recursively and undo differences in reverse order.

## 9. Pseudocode

```text
z,trace <- difference(training_y,d times)
scale <- training-only scale
initialize transformed coefficients
repeat bounded B10 L-BFGS evaluations:
    recurse conditional innovations and sensitivities
    return mean squared innovation objective/gradient
for future step:
    predict z from past z and known errors
    append predicted z and zero future error
return inverse differences in reverse order
```

## 10. Dry Run

With y_t=t² and ARIMA(0,2,0),the second differences are constant2. The fitted transformed intercept is2;two retained training difference histories recover future squares. ARIMA(0,1,0) with no intercept forecasts the final observed level. For AR(1),one-step forecast is c+phi*y_last and further steps repeatedly apply that equation.

## 11. Time Complexity

An innovation/gradient evaluation costs O(n*L*k),where L=max(p,q),k<=5 and n is transformed length. Up to40 line-search trials per optimizer iteration imply O(I*n*L*k) with that bounded constant;zero-lag cases still cost O(n*k). Forecast costs O(h*(L+d));validation/differencing O(n*d). Training is a nonlinear local solve,not an automatic global order search.

## 12. Space Complexity

Innovation sensitivities cost O(n*k);training data,traces,fitted values and residuals cost O(n*(d+1)). B10 limited-memory state costs O(memory*k),rather than a dense n-dimensional Hessian. Forecast recurrence/history costs O(n+h) with O(h*d) inverse work buffers.

The reused optimizer also materializes O(I*k) trajectory/history output during fit,where I is its accepted iteration count;this temporary allocation is released after the forecasting model commits. Peak training space includes that term as well as the limited curvature memory.

## 13. Python Implementation

The canonical [ARIMA](python/solution.py) performs the stated mechanism from scratch with NumPy/standard library. Shared [B11 contracts](../../../docs/time-series-conventions.md) define validation and ownership. No ready-made forecasting estimator is called. See [meaningful tests](tests/test_python.py) and the executable [example](python/example.py).

## 14. C++ Implementation

C++ is optional under the authorized ML policy and is not implemented here. No placeholder C++ files or C++ pass claims. Existing DSA Python/C++17/C++20 requirements are preserved.

## 15. Input and Output Examples

From the repository root:

```sh
.venv/bin/python machine-learning/time-series/arima/python/example.py
```

Actual captured output:

```json
{"order": [1, 1, 1], "status": "gradient-tolerance", "converged": true, "iterations": 88, "intercept": 0.03358521, "ar": [0.85969686], "ma": [-0.95], "forecast": [15.0998527, 15.32689555, 15.55566878, 15.78592963], "index": [60.0, 61.0, 62.0, 63.0]}
```

Re-run targeted verification with `.venv/bin/python -m pytest machine-learning/time-series/arima -q`.

## 16. Edge Cases

Zero AR/MA/difference orders are supported. Parameter-free white-noise/random-walk models need no optimizer. Constant series can be nonidentifiable even with zero objective. Invalid/nonstationary box coefficients,wrong orders,insufficient history and nonfinite data fail. Bounded non-convergence remains visible. A failed refit does not replace an earlier fitted model.

## 17. Advantages

True innovation recursion,differencing inversion,analytic sensitivities and a reused verified optimizer make the estimator inspectable. Independent OLS/MA scalar-search/lag-recurrence tests distinguish fitting from merely producing plausible forecasts.

## 18. Disadvantages and Limitations

CSS is not exact maximum likelihood. Zero pre-burn innovations are conditional assumptions. The sufficient coefficient boxes omit valid stationary/invertible models. Near-boundary or mixed ARMA estimation can be ill-conditioned/nonidentifiable;L-BFGS is local and bounded. No automatic orders,prediction intervals,exogenous regressors or universal accuracy guarantee. An intercept with integration is differenced-level drift,not the unconditional mean.

## 19. When to Use It

Use when a low-order lag/innovation model and a small specified differencing order are plausible. Fit only the chronological training prefix;evaluate entire recursive horizons and report actual convergence diagnostics alongside held-out metrics.

## 20. When Not to Use It

Do not label unmodeled seasonality as nonseasonal ARIMA success. Use SARIMA for explicit seasonal lag polynomials,Holt-Winters for level/trend/phase smoothing,or HMM for categorical latent states. Do not compare parameter values to exact-ML libraries without matching intercept,initialization,burn and objective conventions.

## 21. Comparison With Related Algorithms

AR-only models omit MA innovations;this canonical supports q>0 and mixed p/q. SARIMA extends these same mechanisms with genuine multiplicative seasonal polynomials. SES has a fixed level recursion rather than a CSS-estimated ARMA model.

## 22. Interview Questions

Why are future errors zero but recent errors retained? Future innovations are unknown;past ones have been inferred. Why reverse difference operations? Each retained history belongs to its own input scale. Does a low CSS prove stationarity or global optimality? No;admissibility is specified separately and optimization is local.

## 23. Practice Problems

Derive analytic residual sensitivities for MA(1). Compare AR(1) CSS with independent OLS. Hand-invert second differences. Construct a trend where no-drift random walk and drift differ. Fit one prefix,mutate only future targets and show unchanged parameters/forecasts.

## 24. References

[https://otexts.com/fpp3/arima.html](https://otexts.com/fpp3/arima.html)

[https://arxiv.org/abs/1606.04838](https://arxiv.org/abs/1606.04838)

The [phase conventions](../../../docs/time-series-conventions.md) distinguish educational variants from full libraries and record the actual estimation objective. References support mathematics;executed local tests supply implementation evidence.

## 25. Author Attribution

Maintainer: **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas),[MIT license](../../../LICENSE),[contribution policy](../../../CONTRIBUTING.md).

