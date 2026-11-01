# Exponential Smoothing

## 1. Algorithm Name

Simple exponential smoothing estimates one persistent level. A new observation adjusts that level; every future point forecast then uses the final estimate. This canonical implements fixed-alpha SES,not trend or seasonal ETS.

## 2. Overview

Given chronological regular univariate observations,produce one-step fitted levels and recursive fixed-origin future point forecasts. The model assumes a slowly changing level without explicit trend/seasonality;errors are not automatically independent or Gaussian.

## 3. Problem Statement

fit(y,timestamps=None,frequency=None) accepts1..512 finite observations with magnitude<=1e6. alpha is fixed in[0,1];optional initial_level is a finite scalar. forecast(h) accepts an integer1..128;forecast_index(h) returns the matching next regular timestamps.

fit returns self. levels_ are post-observation levels;fitted_values_ are pre-observation predictions;residuals_=y-fitted_values_. forecast returns an owned float64 vector of constant final level. status_ is fixed-coefficient-recursion and converged_ is None because no parameter optimizer runs.

## 4. Why Do We Need This Algorithm?

A recent observation should influence a level estimate without discarding the accumulated past. A fixed-alpha recursion provides an inspectable compromise between reacting to a change and smoothing short-term variation.

## 5. Real-World Applications

Stable-level demand or sensor baselines and teaching short-horizon smoothing are suitable applications when explicit trend and seasonal structure are unnecessary. Evaluate unseen chronological targets rather than treating initialized fitted residuals as held-out evidence.

## 6. Core Intuition

Let l_-1 be initial_level or y0. At every t, fitted_t=l_(t-1),then l_t=alpha*y_t+(1-alpha)*l_(t-1). For h>=1,forecast_(n+h-1)=l_(n-1). Alpha0 retains the initial level;alpha1 tracks each latest observation exactly. Choosing y0 as initial level makes the first fitted residual0 by convention,not held-out predictive evidence.

The recursion is a convex combination. Recent data receive more weight when alpha is large;small alpha smooths noise but reacts slowly. Repeated substitution yields geometrically decreasing past weights and the remaining initial-level weight.

## 7. Prerequisites

Weighted averages,geometric decay,chronological sampling and the distinction between a pre-observation prediction and a post-observation state are prerequisites. Understand training-only initialization and fixed-origin forecast evaluation.

## 8. Step-by-Step Working Process

Validate data/time/alpha before changing fitted state. Initialize the pre-observation level,save it as the fitted prediction,then update the level. Repeat once per observation. Store owned state only after the complete successful fit. Forecast without consuming future observations.

## 9. Pseudocode

```text
level <- supplied initial level or y[0]
for value in chronological y:
    fitted.append(level)
    level <- alpha*value+(1-alpha)*level
return repeat(level,horizon)
```

## 10. Dry Run

For y=[2,4,8],alpha=.5,initial_level=0,the pre-update fitted values are[0,1,2.5],post-update levels[1,2.5,5.25],and every future forecast is5.25. Independent tests use these numbers rather than a production recursion helper.

## 11. Time Complexity

Training is Theta(n),with constant work per observation. Forecasting and forecast-index generation are Theta(h). Fixed coefficients imply no optimizer iteration factor;input validation remains linear in n.

## 12. Space Complexity

The saved level is O(1);owned levels,fitted values,residuals and timestamps use O(n). A returned horizon vector uses O(h). There is no recursion stack or external dataset.

## 13. Python Implementation

The canonical [ExponentialSmoothing](python/solution.py) performs the stated mechanism from scratch with NumPy/standard library. Shared [B11 contracts](../../../docs/time-series-conventions.md) define validation and ownership. No ready-made forecasting estimator is called. See [meaningful tests](tests/test_python.py) and the executable [example](python/example.py).

## 14. C++ Implementation

C++ is optional under the authorized ML policy and is not implemented here. No placeholder C++ files or C++ pass claims. Existing DSA Python/C++17/C++20 requirements are preserved.

## 15. Input and Output Examples

From the repository root:

```sh
.venv/bin/python machine-learning/time-series/exponential-smoothing/python/example.py
```

Actual captured output:

```json
{"levels": [1.0, 2.5, 5.25], "fitted": [0.0, 1.0, 2.5], "forecast": [5.25, 5.25, 5.25], "index": [3.0, 4.0, 5.0], "status": "fixed-coefficient-recursion"}
```

Re-run targeted verification with `.venv/bin/python -m pytest machine-learning/time-series/exponential-smoothing -q`.

## 16. Edge Cases

A single observation works without timestamps;one explicit timestamp additionally requires frequency. Constant input remains constant. Invalid alpha,missing/nonfinite values,irregular/duplicate timestamps,wrong shapes and nonpositive/oversized horizons raise ValueError. An invalid refit preserves the prior fitted state.

## 17. Advantages

The state/update is easy to audit,cheap to compute and independent of a heavyweight forecasting package. Convex weights keep the level inside the convex hull of finite training values and the supplied initial state.

## 18. Disadvantages and Limitations

There is no trend,seasonality,uncertainty interval or automatically fitted alpha. Persistent trend causes lag. Initialization affects short histories;in-sample first-point agreement is an initialization artifact. Fixed-alpha recursion is not a claim of fitted maximum likelihood or convergence.

## 19. When to Use It

Choose this baseline when a stable level is plausible and a transparent constant-horizon forecast is useful. Evaluate alpha with chronological training-only validation rather than selecting on future target values.

## 20. When Not to Use It

Use Holt-Winters for a regular additive seasonal trend,ARIMA for lagged dynamics,or the explicit Prophet subset for changepoint/Fourier structure. Do not expect a level-only method to extrapolate a rising trend.

## 21. Comparison With Related Algorithms

SES stores level only;Holt-Winters stores level/trend/seasonal states;ARIMA models innovations and autoregressive dynamics. A last-observation baseline is exactly the alpha1 limiting choice here.

## 22. Interview Questions

Why is the forecast flat? No trend/seasonal state exists. What changes at alpha0 and alpha1? The initial level is retained versus the latest observation is retained. Is the first residual held-out? No,the default initial level uses y0.

## 23. Practice Problems

Derive observation weights after four updates. Hand-compute levels for alpha=.2. Compare expanding-window MAE across predeclared alpha values. Construct a trend where smoothing lowers noise but forecasts lag;report only unseen horizon errors.

## 24. References

[https://otexts.com/fpp3/exponential-smoothing.html](https://otexts.com/fpp3/exponential-smoothing.html)

The [phase conventions](../../../docs/time-series-conventions.md) distinguish educational variants from full libraries and record the actual estimation objective. References support mathematics;executed local tests supply implementation evidence.

## 25. Author Attribution

Maintainer: **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas),[MIT license](../../../LICENSE),[contribution policy](../../../CONTRIBUTING.md).

