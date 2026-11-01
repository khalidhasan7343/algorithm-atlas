# Holt-Winters

## 1. Algorithm Name

Additive Holt-Winters tracks a level,a linear trend and one evolving state for each seasonal phase. The three actual smoothing recursions distinguish this algorithm from repeating the last cycle.

## 2. Overview

Fit regularly sampled univariate data with approximately additive repeating seasonality and a locally linear trend. Forecast using final level,trend and the correct future phase. Multiplicative effects and damped growth are outside this canonical variant.

## 3. Problem Statement

seasonal_period m is2..12;fit requires2m..512 finite observations. alpha,beta,gamma are fixed in[0,1]. Optional initial_level,initial_trend,initial_seasonal must all be supplied together;seasonal states have length m and zero initial sum. Common timestamp and horizon contracts apply.

level_,trend_ and seasonal_ hold the final state. states_ records complete post-update states for t>=m. fitted_values_ and residuals_ contain NaN for the first m entries because those fitted predictions are not defined by this initialization. forecast returns h original-unit values.

## 4. Why Do We Need This Algorithm?

A level-only forecast cannot extrapolate a local slope or repeating additive phase. Separate level,trend and seasonal states make these effects explicit while preserving a short bounded recurrence.

## 5. Real-World Applications

Short-horizon demand or usage baselines with a known regular additive seasonal period are appropriate teaching applications. Seasonal amplitude should be reasonably independent of the level; this bounded implementation is not an automatic calendar forecasting service.

## 6. Core Intuition

Initialize trend b=(mean(y[m:2m])-mean(y[:m]))/m,level l=mean(y[:m])+b*(m-1)/2 at time m-1,and s_j=y_j-(l+b*(j-(m-1))). For t>=m,j=t mod m,predict l_old+b_old+s_j_old;update l=alpha*(y_t-s_j_old)+(1-alpha)*(l_old+b_old);b=beta*(l-l_old)+(1-beta)*b_old;s_j=gamma*(y_t-l)+(1-gamma)*s_j_old. At horizon h>=1,use l+h*b+s[(n+h-1)mod m].

Subtract the seasonal effect before updating the underlying level. Compare the new level with the previous level to smooth a slope. Then subtract the new level to update this phase seasonal effect. A final partial training cycle must not shift the forecast phase.

## 7. Prerequisites

Simple exponential smoothing,linear trends,seasonal indexing and regular chronological sampling are prerequisites. Understand old-versus-new state order and that training initialization differs from causal held-out evaluation.

## 8. Step-by-Step Working Process

Validate at least two full cycles. Initialize level at the end of cycle1,not its midpoint. Use cycle2 only inside permitted training initialization. Process observations from t=m onward with old state snapshots. Store the phase array indexed by absolute t mod m. Forecast phases using n+h-1.

## 9. Pseudocode

```text
initialize level,trend,season[0:m]
for t in m..n-1:
    phase <- t mod m
    prediction <- level+trend+season[phase]
    update level using old trend/season
    update trend using old level
    update season[phase] using new level
forecast[h] <- level+h*trend+season[(n+h-1) mod m]
```

## 10. Dry Run

For a constant10 series,initial trend and every seasonal effect are0;all updates retain level10 and every forecast is10. For `y_t=10+.25*t+[-1,1][t mod2]`,the default initialization recovers level/trend/phase exactly;future h forecasts continue that generating sequence. Tests also hand-reproduce a nontrivial three-coefficient recurrence.

## 11. Time Complexity

Fit is O(n*m) in this implementation because every diagnostic state snapshot copies m entries;with bounded m this is linear in n. Arithmetic recursion alone costs O(n). Forecasting costs O(h);fixed coefficients require no optimizer iterations.

## 12. Space Complexity

Current seasonal state costs O(m). Full states_ diagnostics cost O(n*m);fitted/residual/time vectors O(n);forecasts O(h). No growing recursive call stack or downloaded model exists.

## 13. Python Implementation

The canonical [HoltWinters](python/solution.py) performs the stated mechanism from scratch with NumPy/standard library. Shared [B11 contracts](../../../docs/time-series-conventions.md) define validation and ownership. No ready-made forecasting estimator is called. See [meaningful tests](tests/test_python.py) and the executable [example](python/example.py).

## 14. C++ Implementation

C++ is optional under the authorized ML policy and is not implemented here. No placeholder C++ files or C++ pass claims. Existing DSA Python/C++17/C++20 requirements are preserved.

## 15. Input and Output Examples

From the repository root:

```sh
.venv/bin/python machine-learning/time-series/holt-winters/python/example.py
```

Actual captured output:

```json
{"level": 14.75, "trend": 0.25, "seasonal": [-1.0, 1.0], "forecast": [14.0, 16.25, 14.5, 16.75], "index": [20.0, 21.0, 22.0, 23.0], "status": "fixed-coefficient-recursion"}
```

Re-run targeted verification with `.venv/bin/python -m pytest machine-learning/time-series/holt-winters -q`.

## 16. Edge Cases

m2 is supported,including a final incomplete cycle. Fewer than2m observations,invalid coefficients,incomplete custom initialization,non-centered initial seasons and malformed timestamps fail. Constant input and trend-only input are separately tested. Output NaNs are intentional only in the unavailable initialization region.

## 17. Advantages

Separates transparent trend and seasonal states while keeping forecasting inexpensive. Independent hand recursions can audit each update and seasonal offset. It preserves additive effects in the original physical units.

## 18. Disadvantages and Limitations

Only additive,fixed-period,fixed-coefficient triple smoothing is implemented. The two-cycle default initialization uses later observations within the training set,so early fitted values are not online causal validation. No automatic parameter fitting,damping,multiplicative seasonality or prediction intervals. Trend extrapolation can become unreasonable far ahead.

## 19. When to Use It

Use a short-horizon baseline when a regular period is known and seasonal amplitude is roughly independent of the level. Evaluate whole forecast horizons at chronological origins and fit initialization on each training window alone.

## 20. When Not to Use It

Do not use it unchanged for irregular timestamps,multiple changing periods,multiplicative effects or latent-state categorical inference. Forecast errors from initialization-region fitted values are not substitutes for unseen holdout errors.

## 21. Comparison With Related Algorithms

SES has one level and flat forecasts. Holt-Winters adds trend and phase-specific recurrence. SARIMA uses seasonal lag polynomials with innovations instead. Prophet represents declared Fourier components and trend changepoints in a regularized additive design.

## 22. Interview Questions

Why does level initialize at cycle1 end? It is the state immediately before processing cycle2. Why retain old seasonal state? The level update removes the previous phase estimate. Which phase forecasts first after n points? n mod m,including incomplete final cycles.

## 23. Practice Problems

Hand-compute three updates with m2. Derive exact initialization for trend plus centered seasonality. Test a training length not divisible by m. Compare expanding versus rolling-window holdout errors when seasonal amplitude changes.

## 24. References

[https://otexts.com/fpp3/exponential-smoothing.html](https://otexts.com/fpp3/exponential-smoothing.html)

The [phase conventions](../../../docs/time-series-conventions.md) distinguish educational variants from full libraries and record the actual estimation objective. References support mathematics;executed local tests supply implementation evidence.

## 25. Author Attribution

Maintainer: **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas),[MIT license](../../../LICENSE),[contribution policy](../../../CONTRIBUTING.md).

