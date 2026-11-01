# SARIMA

## 1. Algorithm Name

Seasonal ARIMA multiplies ordinary and seasonal AR/MA polynomials. Seasonal AR and MA coefficients,interaction cross-lags,differencing and innovation-based forecasting are all genuinely represented;this is not only seasonal preprocessing followed by ordinary ARIMA.

## 2. Overview

Fit SARIMA(p,d,q)(P,D,Q)_s to regular univariate data. Explain whether repeated structure belongs to seasonal autoregression,moving-average innovations or integration. Forecast transformed observations recursively and reverse all seasonal/nonseasonal differences.

## 3. Problem Statement

order=(p,d,q) has p/q0..2,d0..2;seasonal_order=(P,D,Q,s) has P/Q0..1,D0..1,s2..12. Effective post-difference history must exceed the full polynomial burn by max(4,2k+1) for fit. k<=7. filter accepts explicit seasonal_ar/seasonal_ma arrays of the declared sizes. Other timestamp,coefficient,optimizer and forecast contracts match ARIMA.

params_ contains the original-unit innovation intercept and AR/MA components. innovations_ contains raw-unit conditional innovations after differencing,with the initial burn entries0. fitted_values_/residuals_ align with original y and have unavailable prefixes marked NaN. normalization_scale_,objective_,gradient_norm_,n_iter_,status_ and converged_ expose estimation diagnostics. forecast(h) returns owned original-unit point predictions.

## 4. Why Do We Need This Algorithm?

A nonseasonal model can miss dependence one cycle back. Multiplying ordinary and seasonal lag polynomials represents that dependence and its interaction cross-lags explicitly; seasonal differencing alone does not supply seasonal AR/MA effects.

## 5. Real-World Applications

Known-period regular demand,usage or sensor sequences are suitable small seasonal forecasting experiments when multiplicative lag dynamics are plausible. The educational fixed orders and periods do not provide automatic seasonal detection.

## 6. Core Intuition

A(B)=phi(B)*Phi(B^s);M(B)=theta(B)*Theta(B^s);z=(1-B)^d*(1-B^s)^D y;A(B)z=c+M(B)epsilon. For p=P=1,effective AR weights are phi at1,Phi at s,and -phi*Phi at s+1. MA weights are theta at1,Theta at s,and +theta*Theta at s+1. Core code constructs both products by convolution and differentiates them with the product rule. Component absolute-sum boxes imply stationary/invertible factor polynomials;their product retains those roots.

Recent observations and observations one seasonal cycle back interact through the product model. Omitting the s+1 cross-term changes the statistical model. Seasonal MA acts on inferred errors at seasonal lags,not on raw observations.

## 7. Prerequisites

[ARIMA](../arima/README.md),seasonal lags,polynomial convolution,product-rule differentiation and reversing multiple difference operations are prerequisites. Understand chronological evaluation and local bounded CSS estimation.

## 8. Step-by-Step Working Process

Apply D seasonal differences first,then d ordinary differences;retain each training-only pre-transform history. Build full multiplicative AR/MA polynomials and analytic Jacobians. Reuse canonical ARIMA innovation/CSS/L-BFGS machinery with the correct full burn. Forecast with all cross-lags,append zero future innovations,and invert transformations in reverse order.

## 9. Pseudocode

```text
z,trace <- seasonal differences then ordinary differences
ar_poly <- convolve(nonseasonal_AR,seasonal_AR)
ma_poly <- convolve(nonseasonal_MA,seasonal_MA)
construct product-rule polynomial Jacobians
fit CSS with canonical innovation sensitivities/B10 L-BFGS
recurse forecast using all expanded lags
undo ordinary differences,then seasonal differences
```

## 10. Dry Run

With phi=.4,Phi=.5,s4,AR polynomial is[1,-.4,0,0,-.5,.2],so the recurrence includes -.2*z_(t-5). With theta=.2,Theta=-.3,the MA polynomial is[1,.2,0,0,-.3,-.06]. Independent tests state these arrays directly. A series increasing by2 each seasonal cycle is reconstructed by seasonal differencing,constant transformed forecast and retained phase histories.

## 11. Time Complexity

Let L=max(p+P*s,q+Q*s),k<=7. Polynomial convolution/Jacobians cost O(k*L²) at these bounded degrees;each innovation/gradient evaluation costs O(n*L*k),with a bounded40-trial line search per optimizer iteration. Forecasts cost O(h*L) plus O(h*(d+D)) inverse operations. Seasonal periods are bounded rather than arbitrary allocations.

## 12. Space Complexity

Sensitivities cost O(n*k);lag polynomials O(k*L);retained difference histories O(n*(d+D+1));diagnostics O(n). Limited-memory optimization remains O(memory*k). Forecast history is O(n+h),without external models or datasets.

The reused optimizer also materializes O(I*k) trajectory/history output during fit,where I is its accepted iteration count;this temporary allocation is released after the forecasting model commits. Peak training space includes that term as well as the limited curvature memory.

## 13. Python Implementation

The canonical [SARIMA](python/solution.py) performs the stated mechanism from scratch with NumPy/standard library. Shared [B11 contracts](../../../docs/time-series-conventions.md) define validation and ownership. No ready-made forecasting estimator is called. See [meaningful tests](tests/test_python.py) and the executable [example](python/example.py).

## 14. C++ Implementation

C++ is optional under the authorized ML policy and is not implemented here. No placeholder C++ files or C++ pass claims. Existing DSA Python/C++17/C++20 requirements are preserved.

## 15. Input and Output Examples

From the repository root:

```sh
.venv/bin/python machine-learning/time-series/sarima/python/example.py
```

Actual captured output:

```json
{"seasonal_order": [1, 0, 0, 4], "status": "gradient-tolerance", "converged": true, "iterations": 6, "seasonal_ar": [0.53938392], "forecast": [0.01013655, -0.03190306, 0.12595536, -0.05328388, 0.00546749, -0.017208], "index": [80.0, 81.0, 82.0, 83.0, 84.0, 85.0]}
```

Re-run targeted verification with `.venv/bin/python -m pytest machine-learning/time-series/sarima -q`.

## 16. Edge Cases

Zero AR/MA/difference orders are supported. Parameter-free white-noise/random-walk models need no optimizer. Constant series can be nonidentifiable even with zero objective. Invalid/nonstationary box coefficients,wrong orders,insufficient history and nonfinite data fail. Bounded non-convergence remains visible. A failed refit does not replace an earlier fitted model.

## 17. Advantages

Exact multiplicative polynomial construction makes seasonal/nonseasonal interactions auditable. Shared canonical ARIMA machinery avoids duplicate innovation estimators while keeping SARIMA-specific polynomials and product-rule derivatives explicit in its own source.

## 18. Disadvantages and Limitations

All ARIMA CSS/local-estimation limitations apply. Seasonal periods must be known and regular;P/Q<=1 and D<=1 are explicit educational bounds. Long seasonal lags need substantially more history. Component stability boxes restrict the admissible domain. No automatic seasonal-order search,multiple seasonal periods,intervals or complete SARIMAX parity.

## 19. When to Use It

Choose this method for a known repeating sampling period with plausible seasonal autoregressive or innovation dependence. Retain whole seasons inside each training fold and evaluate recursive horizons across multiple future phases.

## 20. When Not to Use It

Do not claim a seasonal-difference-only model supports arbitrary seasonal AR/MA terms. Do not randomly shuffle seasonal observations or derive seasonal preprocessing from the full train/test series. Use Prophet-style Fourier components for an explicitly additive basis model instead.

## 21. Comparison With Related Algorithms

With P=D=Q=0,SARIMA reduces to the matching ARIMA estimator under identical settings;tests compare innovations,forecasts and statuses. Holt-Winters represents phase states directly;SARIMA represents seasonal lag-polynomial dynamics and innovations.

## 22. Interview Questions

What sign does the AR cross-term have in the recurrence? Negative phi*Phi. Why is the MA cross-term positive? The positive-sign MA factor polynomials multiply. Is seasonal differencing sufficient for SARIMA? No,seasonal AR/MA factors are separate mechanisms.

## 23. Practice Problems

Expand AR/MA products by hand for s3. Verify a seasonal MA forecast using past errors. Compare a zero-seasonal-order fit to ARIMA. Reconstruct combined D1/d1 differences of a quadratic. Generate a seasonal AR process and compare estimated Phi with direct lag-s OLS.

## 24. References

[https://otexts.com/fpp3/arima.html](https://otexts.com/fpp3/arima.html)

[https://arxiv.org/abs/1606.04838](https://arxiv.org/abs/1606.04838)

The [phase conventions](../../../docs/time-series-conventions.md) distinguish educational variants from full libraries and record the actual estimation objective. References support mathematics;executed local tests supply implementation evidence.

## 25. Author Attribution

Maintainer: **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas),[MIT license](../../../LICENSE),[contribution policy](../../../CONTRIBUTING.md).

