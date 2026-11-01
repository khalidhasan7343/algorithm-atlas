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

class ExponentialSmoothing(s.Forecaster):
    """Fixed-alpha SES; initial level y[0] unless explicitly supplied."""
    def __init__(self, alpha=.3, initial_level=None):
        self.alpha = s.scalar(alpha, 'alpha', 0, 1)
        self.initial_level = None if initial_level is None else s.scalar(initial_level, 'initial_level', -1e6, 1e6)

    def fit(self, y, *, timestamps=None, frequency=None):
        y = s.vector(y)
        grid = s.TimeGrid(len(y), timestamps, frequency)
        alpha = s.scalar(self.alpha, 'alpha', 0, 1)
        level = y[0] if self.initial_level is None else s.scalar(self.initial_level, 'initial_level', -1e6, 1e6)
        fitted, levels = [], []
        for observation in y:
            fitted.append(level)
            level = alpha*observation+(1-alpha)*level
            levels.append(level)
        self.grid_, self.level_ = grid, float(level)
        self.fitted_values_, self.levels_ = np.array(fitted), np.array(levels)
        self.residuals_ = y-self.fitted_values_
        self.n_observations_ = len(y)
        self.status_, self.converged_ = 'fixed-coefficient-recursion', None
        return self

    def forecast(self, h):
        self._ready()
        return np.full(s.horizon(h), self.level_)
