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

def _component(order, values, jacobian, sign, lag=1):
    poly = np.zeros(order*lag+1)
    poly[0] = 1
    deriv = np.zeros((jacobian.shape[0], len(poly)))
    for i in range(order):
        poly[(i+1)*lag] = sign*values[i]
        deriv[:, (i+1)*lag] = sign*jacobian[:, i]
    return poly, deriv


def _b10():
    name = 'atlas_b10_support'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parents[3]/'optimization/support.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


class ARIMA(s.Forecaster):
    """Conditional-sum-of-squares ARIMA with real innovations and analytic sensitivities."""
    def __init__(self, order=(1, 0, 0), *, include_intercept=True, max_iter=200, tolerance=1e-7):
        if not isinstance(order, (list, tuple)) or len(order) != 3:
            raise ValueError('order must be (p,d,q)')
        self.p = s.integer(order[0], 'p', 0, 2)
        self.d = s.integer(order[1], 'd', 0, 2)
        self.q = s.integer(order[2], 'q', 0, 2)
        if not isinstance(include_intercept, (bool, np.bool_)):
            raise ValueError('include_intercept must be boolean')
        self.include_intercept = bool(include_intercept)
        self.max_iter = s.integer(max_iter, 'max_iter', 1, 400)
        self.tolerance = s.scalar(tolerance, 'tolerance', 1e-12, 1)

    def _groups(self):
        return dict(ar=self.p, ma=self.q, seasonal_ar=0, seasonal_ma=0)

    def _lags(self):
        return [1]*self.d

    def _decode(self, u):
        groups = self._groups()
        k = int(self.include_intercept)+sum(groups.values())
        u = np.asarray(u)
        if u.shape != (k,) or u.dtype.kind not in 'iuf' or not np.isfinite(u).all() or np.any(np.abs(u) > 1e6):
            raise ValueError('unconstrained parameter shape/domain differs from model')
        u = u.astype(float)
        offset = int(self.include_intercept)
        parts = dict(intercept=float(u[0]) if self.include_intercept else 0.)
        jac = {}
        for name, count in groups.items():
            transformed = np.tanh(u[offset:offset+count])
            parts[name] = .95*transformed/max(count, 1)
            jac[name] = np.zeros((k, count))
            for j in range(count):
                jac[name][offset+j, j] = .95*(1-transformed[j]**2)/count
            offset += count
        return parts, jac

    def _physical(self, parameters):
        if not isinstance(parameters, dict) or parameters.keys()-{'intercept', *self._groups()}:
            raise ValueError('invalid physical parameter keys')
        out = dict(intercept=s.scalar(parameters.get('intercept', 0.), 'intercept', -1e6, 1e6))
        if not self.include_intercept and out['intercept'] != 0:
            raise ValueError('this model has no intercept')
        k = int(self.include_intercept)+sum(self._groups().values())
        jac = {}
        for name, count in self._groups().items():
            values = np.asarray(parameters.get(name, []))
            if values.shape != (count,) or values.dtype.kind not in 'iuf' or not np.isfinite(values).all() or np.sum(np.abs(values)) > .95+1e-12:
                raise ValueError('component must have declared size and absolute sum <=.95')
            out[name] = values.astype(float, copy=True)
            jac[name] = np.zeros((k, count))
        return out, jac

    def _polynomials(self, parts, jac):
        ar, dar = _component(self.p, parts['ar'], jac['ar'], -1)
        ma, dma = _component(self.q, parts['ma'], jac['ma'], 1)
        return ar, ma, dar, dma

    def lag_polynomials(self, parameters):
        parts, jac = self._physical(parameters)
        ar, ma, _, _ = self._polynomials(parts, jac)
        return ar.copy(), ma.copy()

    def _innovations(self, z, parts, jac):
        arpoly, mapoly, d_arpoly, d_mapoly = self._polynomials(parts, jac)
        ar, ma = -arpoly[1:], mapoly[1:]
        dar, dma = -d_arpoly[:, 1:], d_mapoly[:, 1:]
        k = dar.shape[0]
        burn = max(len(ar), len(ma))
        if len(z) <= burn:
            raise ValueError('insufficient history for declared lag polynomials')
        residuals = np.zeros(len(z))
        derivatives = np.zeros((len(z), k))
        dc = np.zeros(k)
        if self.include_intercept:
            dc[0] = 1
        la, lm = np.arange(1, len(ar)+1), np.arange(1, len(ma)+1)
        with np.errstate(over='raise', invalid='raise', divide='raise'):
            for t in range(burn, len(z)):
                residuals[t] = z[t]-parts['intercept']-ar@z[t-la]-ma@residuals[t-lm]
                derivatives[t] = -dc-dar@z[t-la]-dma@residuals[t-lm]-ma@derivatives[t-lm]
            objective = .5*float(residuals[burn:]@residuals[burn:])/(len(z)-burn)
            gradient = residuals[burn:]@derivatives[burn:]/(len(z)-burn)
        s.finite(residuals, 'innovations')
        s.finite(gradient, 'CSS gradient')
        return objective, gradient, residuals, burn

    def _data(self, y, timestamps=None, frequency=None):
        y = s.vector(y)
        grid = s.TimeGrid(len(y), timestamps, frequency)
        z, traces = s.difference(y, self._lags())
        # Scale only; no mean subtraction changes the intercept convention.
        scale = max(float(np.std(z)), float(np.max(np.abs(z)))*1e-3, 1e-8)
        return y, grid, z/scale, traces, scale

    def css_objective_gradient(self, y, unconstrained):
        _, _, z, _, _ = self._data(y)
        parts, jac = self._decode(unconstrained)
        objective, gradient, _, _ = self._innovations(z, parts, jac)
        return objective, gradient.copy()

    def _commit(self, y, grid, z, traces, scale, parts, jac, status, converged, iterations):
        objective, gradient, residuals, burn = self._innovations(z, parts, jac)
        fitted = np.full(len(y), np.nan)
        offset = len(y)-len(z)
        fitted[offset+burn:] = y[offset+burn:]-scale*residuals[burn:]
        params = {name: value.copy() if isinstance(value, np.ndarray) else float(value*scale) for name, value in parts.items()}
        ar, ma, _, _ = self._polynomials(parts, jac)
        self.grid_, self.n_observations_ = grid, len(y)
        self.params_, self.normalization_scale_, self.objective_ = params, scale, objective
        self.innovations_ = scale*residuals
        self.fitted_values_, self.residuals_ = fitted, y-fitted
        self.status_, self.converged_, self.n_iter_ = status, converged, iterations
        self.gradient_norm_, self.burn_ = float(np.linalg.norm(gradient)), burn
        self._z, self._epsilon = z.copy(), residuals.copy()
        self._traces = [(lag, values.copy()) for lag, values in traces]
        self._ar, self._ma, self._intercept = -ar[1:], ma[1:], float(parts['intercept'])
        return self

    def fit(self, y, *, timestamps=None, frequency=None):
        y, grid, z, traces, scale = self._data(y, timestamps, frequency)
        k = int(self.include_intercept)+sum(self._groups().values())
        initial = np.zeros(k)
        if self.include_intercept:
            initial[0] = float(np.mean(z))
        parts, jac = self._decode(initial)
        _, _, _, burn = self._innovations(z, parts, jac)
        if len(z)-burn < max(4, 2*k+1):
            raise ValueError('insufficient effective CSS training history')
        if k:
            cache_x, cache_value = None, None
            def evaluate(u):
                nonlocal cache_x, cache_value
                if cache_x is None or not np.array_equal(u, cache_x):
                    pp, jj = self._decode(u)
                    result = self._innovations(z, pp, jj)
                    cache_x, cache_value = u.copy(), (result[0], result[1].copy())
                return cache_value
            result = _b10().load('l-bfgs').LBFGS().minimize(lambda u: evaluate(u)[0], lambda u: evaluate(u)[1].copy(), initial, max_iter=self.max_iter, tolerance=self.tolerance)
            parts, jac = self._decode(result.x)
            status, converged, iterations = result.status, result.converged, result.n_iter
        else:
            status, converged, iterations = 'no-free-parameters', True, 0
        return self._commit(y, grid, z, traces, scale, parts, jac, status, converged, iterations)

    def filter(self, y, parameters, *, timestamps=None, frequency=None):
        y, grid, z, traces, scale = self._data(y, timestamps, frequency)
        parts, jac = self._physical(parameters)
        parts['intercept'] /= scale
        return self._commit(y, grid, z, traces, scale, parts, jac, 'fixed-parameters', None, 0)

    def forecast(self, h):
        self._ready()
        h = s.horizon(h)
        values, errors, future = list(self._z), list(self._epsilon), []
        for _ in range(h):
            value = self._intercept
            value += sum(coefficient*values[-lag] for lag, coefficient in enumerate(self._ar, 1))
            value += sum(coefficient*errors[-lag] for lag, coefficient in enumerate(self._ma, 1))
            s.finite(value, 'recursive forecast')
            future.append(value*self.normalization_scale_)
            values.append(value)
            errors.append(0.)
        return s.inverse_difference(future, self._traces).copy()
