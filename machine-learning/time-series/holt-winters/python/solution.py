import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec = importlib.util.spec_from_file_location('atlas_b11_support', Path(__file__).resolve().parents[2]/'support.py')
s = sys.modules.get(_spec.name)
if s is None:
    s = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = s
    _spec.loader.exec_module(s)

class HoltWinters(s.Forecaster):
    """Additive triple smoothing; first cycle initializes, recursion starts at m."""
    def __init__(self, seasonal_period, alpha=.3, beta=.1, gamma=.1, *, initial_level=None, initial_trend=None, initial_seasonal=None):
        self.seasonal_period = s.integer(seasonal_period, 'seasonal_period', 2, 12)
        self.alpha = s.scalar(alpha, 'alpha', 0, 1)
        self.beta = s.scalar(beta, 'beta', 0, 1)
        self.gamma = s.scalar(gamma, 'gamma', 0, 1)
        self.initial_level, self.initial_trend = initial_level, initial_trend
        self.initial_seasonal = initial_seasonal

    def fit(self, y, *, timestamps=None, frequency=None):
        m = s.integer(self.seasonal_period, 'seasonal_period', 2, 12)
        y = s.vector(y, minimum=2*m)
        grid = s.TimeGrid(len(y), timestamps, frequency)
        a, b, g = (s.scalar(v, name, 0, 1) for v, name in ((self.alpha, 'alpha'), (self.beta, 'beta'), (self.gamma, 'gamma')))
        supplied = (self.initial_level is not None, self.initial_trend is not None, self.initial_seasonal is not None)
        if any(supplied) and not all(supplied):
            raise ValueError('supply all initial states together')
        if all(supplied):
            level = s.scalar(self.initial_level, 'initial_level', -1e6, 1e6)
            trend = s.scalar(self.initial_trend, 'initial_trend', -1e6, 1e6)
            seasonal = s.vector(self.initial_seasonal, 'initial_seasonal')
            if len(seasonal) != m or not np.isclose(seasonal.sum(), 0, atol=1e-10, rtol=0):
                raise ValueError('m initial seasonal states with zero sum required')
        else:
            trend = float((np.mean(y[m:2*m])-np.mean(y[:m]))/m)
            level = float(np.mean(y[:m])+trend*(m-1)/2)
            seasonal = y[:m]-(level+trend*(np.arange(m)-(m-1)))
        fitted = np.full(len(y), np.nan)
        states = []
        for t in range(m, len(y)):
            slot = t % m
            old_season, old_level = seasonal[slot], level
            fitted[t] = level+trend+old_season
            level = a*(y[t]-old_season)+(1-a)*(level+trend)
            trend = b*(level-old_level)+(1-b)*trend
            seasonal[slot] = g*(y[t]-level)+(1-g)*old_season
            s.finite([level, trend, *seasonal])
            states.append(np.r_[level, trend, seasonal])
        self.grid_, self.level_, self.trend_ = grid, float(level), float(trend)
        self.seasonal_, self.states_ = seasonal.copy(), np.array(states)
        self.fitted_values_, self.residuals_ = fitted, y-fitted
        self.n_observations_ = len(y)
        self.status_, self.converged_ = 'fixed-coefficient-recursion', None
        return self

    def forecast(self, h):
        self._ready()
        h = s.horizon(h)
        positions = (self.n_observations_+np.arange(h)) % len(self.seasonal_)
        return s.finite(self.level_+np.arange(1, h+1)*self.trend_+self.seasonal_[positions], 'forecast').copy()
