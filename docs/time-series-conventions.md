# B11 mathematical and API contracts

Owner MD.Khalid Hasan;MIT.Scope is exactly six canonicals. No external model delegates.

## Shared data and time

Forecasting fit(y,timestamps=None,frequency=None) consumes an owned finite float64 vector,length1..512,magnitude<=1e6; each algorithm adds minimum-history requirements. Observations are already chronological and regularly sampled; never sort,interpolate,shuffle or impute. Optional timestamps are numeric ticks or whole-second datetime64,strictly increasing with uniform spacing;NaT,duplicates,irregular spacing and conflicting frequencies fail. Datetime frequency is seconds;numeric frequency is numeric units. No exogenous regressors are supported. forecast(h) is recursive fixed-origin,original-unit point forecasts,with horizon1..128;forecast_index(h) starts one step after the final training timestamp. HMM has a separate sequence API.

## SES

Fixed alpha in[0,1]. Initial pre-observation level is explicit or y0. For every t,fitted[t]=level_old;level=alpha*y[t]+(1-alpha)*level_old. All future point forecasts equal final level. No estimated-alpha or maximum-likelihood claim;converged=None,status fixed-coefficient-recursion.

## Additive Holt-Winters

m2..12;at least2m training points;fixed alpha,beta,gamma in[0,1]. First-cycle initialization targets state at t=m-1: b=(mean(cycle2)-mean(cycle1))/m;l=mean(cycle1)+b*(m-1)/2;s_j=y_j-(l+b*(j-(m-1))). These centered initial seasonal states have sum0. Alternatively all three initial states may be supplied at that same time origin. The second cycle informs initialization inside the training set,so this is not a strictly causal online fit within the initialization region. Fitted values before m are unavailable NaN;do not score them as out-of-sample predictions.

For t>=m and slot=t mod m,fitted=l_old+b_old+s_old; l=alpha*(y-s_old)+(1-alpha)*(l_old+b_old);b=beta*(l-l_old)+(1-beta)*b_old;s_slot=gamma*(y-l)+(1-gamma)*s_old. Forecast h uses l+h*b+s[(n+h-1)mod m]. No multiplicative seasonality,damping or parameter estimation is claimed.

## ARIMA and SARIMA

AR polynomial 1-sum(phi_i B^i);MA polynomial1+sum(theta_j B^j). A(B)z=c+M(B)epsilon. Nonseasonal orders p,q0..2,d0..2;seasonal P,Q0..1,D0..1,s2..12. Difference seasonally first,then d ordinary times;reverse the retained training-only transformations for forecasts. Full multiplicative AR/MA polynomials include cross-lags,not merely seasonal differencing.

Conditional innovations before burn=max(ARdegree,MAdegree) are zero;for t>=burn,epsilon_t=z_t-c-sum(ar_l*z[t-l])-sum(ma_l*epsilon[t-l]). CSS objective is0.5*mean(epsilon[burn:]**2) after scaling z by a training-only scale;this is not exact Gaussian maximum likelihood. Free coefficients use sufficient stability boxes phi_i=.95*tanh(u_i)/p and theta_j=.95*tanh(v_j)/q;seasonal components likewise. This restricts the admissible domain but guarantees component stationarity/invertibility via absolute sums<1. c is the innovation-equation intercept,not unconditional mean. With d>0 it produces differenced-level drift. No automatic order search,intervals or complete stationary-region coverage.

B10 canonical L-BFGS is reused unchanged with analytic CSS gradients through polynomial and innovation recurrences. Bounded max_iter1..400; convergence/failure/budget status is preserved. Parameter-free models have no optimizer. An explicit filter(y,parameters) supports validated fixed physical components without claiming estimation convergence. First burn residuals are conditional zeros,fitted entries there are NaN. Original one-step fitted values are y-epsilon in original units after differencing/burn. Recursive forecasts use known past innovations and zero unknown future innovations.

## Prophet specification decision

Authoritative formulation: Sean J.Taylor and Benjamin Letham,Forecasting at Scale,The American Statistician72(1),37–45,2018,DOI10.1080/00031305.2017.1380080. Official source repository contains the author preprint and changepoint documentation. Continuous piecewise-linear trend is equivalently intercept+slope*t+sum(delta_j*max(0,t-c_j));seasonality uses Fourier sine/cosine pairs.

The authorized educational subset uses explicit training-interior changepoints,linear growth,one or more user-declared Fourier seasonalities and additive components. Time is elapsed sample steps;only the trend basis is divided by training duration n-1. Seasonal periods are sample steps. No future normalization or automatic changepoint selection. Gaussian-noise objective: ||y-Xbeta||²/(2n)+lambda*||D beta||²/2,where D masks changepoint/Fourier coefficients and leaves intercept/base slope unpenalized. Solve the augmented system with NumPy SVD least squares. This **Gaussian ridge changepoint prior differs from official Prophet's Laplace/L1 prior**;we explicitly do not claim equivalent inference or full library parity. No holidays,regressors,logistic growth,MCMC,uncertainty intervals or automatic seasonality detection. Maximum32 columns;rank/optimality diagnostics retained. Independent normal equations and B10 objective compatibility verify the declared variant.

## Categorical HMM

K1..8 states,M1..16 symbols;integer observations0..M-1. Owned normalized pi,A,B may contain structural zeros. Local seeded positive initialization when no parameters supplied. Forward/backward,posterior and Viterbi operate in log space. score returns log likelihood including -inf for impossible sequences;posterior/decoding/EM reject impossible observations rather than inventing mass. Viterbi ties choose first state/predecessor;no global lexicographic-tie promise. Baum-Welch performs pure ML updates with no pseudocount,independent sequence boundaries and old-row retention for exactly zero expected occupancy. Fit accepts a list of1..16 independent sequences,total<=4096,T<=2048;max_iter1..200 with work cap max_iter*total*K²<=2e7. Relative likelihood tolerance is convergence to a local EM fixed point,not global optimality. Failed fits are atomic. Histories include the initial likelihood and each accepted update.

## Evaluation and metrics

Chronological holdout/expanding/rolling origins fit fresh models to training prefixes/windows,then recursively forecast the whole horizon without observing its targets. At most32 origins. MAE/MSE/RMSE have usual units;sMAPE=100mean(2|a-p|/(|a|+|p|)),with0/0 defined0. MAPE=100mean(|(a-p)/a|) is None if any actual is zero. Optional MASE divides MAE by mean training absolute seasonal differences;zero scale is an explicit error. Do not sum overlapping target audit counts or substitute training error for held-out accuracy.

Computed states and metrics are finite with magnitude<=1e100. Nonrepresentable MAPE/MASE ratios raise NumericalError rather than returning infinity or emitting overflow warnings;exact-zero denominator conventions remain as stated above.
