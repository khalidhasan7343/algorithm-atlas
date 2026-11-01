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

class Prophet(s.Forecaster):
    """Explicit linear-changepoint/Fourier subset with declared Gaussian ridge priors."""
    def __init__(self, *, changepoints=(), seasonalities=((7., 2),), regularization=.01):
        cp = np.asarray(changepoints)
        if cp.ndim != 1 or len(cp) > 8 or cp.dtype.kind not in 'iuf' or not np.isfinite(cp).all():
            raise ValueError('0..8 finite numeric changepoints required')
        if len(cp) and (np.any(cp <= 0) or np.any(np.diff(cp) <= 0)):
            raise ValueError('changepoints must be strictly increasing and positive')
        self.changepoints = tuple(float(x) for x in cp)
        if not isinstance(seasonalities, (list, tuple)) or len(seasonalities) > 4:
            raise ValueError('0..4 explicit seasonalities required')
        components = []
        for entry in seasonalities:
            if not isinstance(entry, (list, tuple)) or len(entry) != 2:
                raise ValueError('seasonality must be (period, Fourier order)')
            period = s.scalar(entry[0], 'seasonal period', 2, 1e4)
            order = s.integer(entry[1], 'Fourier order', 1, 8)
            if any(period == previous[0] for previous in components):
                raise ValueError('duplicate seasonal period')
            components.append((period, order))
        self.seasonalities = tuple(components)
        if 2+len(cp)+sum(2*order for _, order in components) > 32:
            raise ValueError('at most32 design columns')
        self.regularization = s.scalar(regularization, 'regularization', 0, 1e3)

    def _design(self, relative_times, training_size):
        t = np.asarray(relative_times, dtype=float)
        duration = training_size-1
        columns = [np.ones_like(t), t/duration]
        columns.extend(np.maximum(t-cp, 0.)/duration for cp in self.changepoints)
        for period, order in self.seasonalities:
            for harmonic in range(1, order+1):
                angle = 2*np.pi*harmonic*t/period
                columns.extend((np.sin(angle), np.cos(angle)))
        return np.column_stack(columns)

    def _components(self, times, coefficient, training_size):
        design = self._design(times, training_size)
        stop = 2+len(self.changepoints)
        trend = design[:, :stop]@coefficient[:stop]
        seasonal = np.zeros(len(times))
        out = dict(trend=trend.copy())
        for index, (_, order) in enumerate(self.seasonalities):
            component = design[:, stop:stop+2*order]@coefficient[stop:stop+2*order]
            out['seasonality_'+str(index)] = component.copy()
            seasonal += component
            stop += 2*order
        out['seasonal'] = seasonal.copy()
        out['total'] = trend+seasonal
        for values in out.values():
            s.finite(values, 'additive forecast component')
        return out

    def fit(self, y, *, timestamps=None, frequency=None):
        y = s.vector(y, minimum=2)
        grid = s.TimeGrid(len(y), timestamps, frequency)
        if any(cp >= len(y)-1 for cp in self.changepoints):
            raise ValueError('changepoints must be interior to this training history')
        regularization = s.scalar(self.regularization, 'regularization', 0, 1e3)
        design = self._design(np.arange(len(y)), len(y))
        mask = np.ones(design.shape[1])
        mask[:2] = 0
        penalty = np.diag(np.sqrt(len(y)*regularization)*mask)
        try:
            coefficient, _, rank, singular = np.linalg.lstsq(np.vstack((design, penalty)), np.r_[y, np.zeros(len(mask))], rcond=None)
        except np.linalg.LinAlgError as error:
            raise s.NumericalError('SVD least-squares failed') from error
        s.finite(coefficient, 'additive coefficients')
        components = self._components(np.arange(len(y)), coefficient, len(y))
        residual = components['total']-y
        gradient = design.T@residual/len(y)+regularization*mask*coefficient
        objective = .5*float(residual@residual)/len(y)+.5*regularization*float((mask*coefficient)@(mask*coefficient))
        optimality = float(np.max(np.abs(gradient)))
        converged = bool(optimality <= 1e-8*(1+np.max(np.abs(design.T@y/len(y)))))
        self.grid_, self.n_observations_ = grid, len(y)
        self.coef_, self.design_matrix_, self.penalty_mask_ = coefficient.copy(), design.copy(), mask.copy()
        self.rank_, self.design_rank_, self.singular_values_ = int(rank), int(np.linalg.matrix_rank(design)), singular.copy()
        self.components_ = components
        self.fitted_values_, self.residuals_ = components['total'].copy(), -residual
        self.objective_, self.optimality_ = objective, optimality
        self.converged_, self.status_, self.n_iter_ = converged, 'svd-solved' if converged else 'optimality-not-met', 1
        return self

    def forecast_components(self, h):
        self._ready()
        h = s.horizon(h)
        return self._components(np.arange(self.n_observations_, self.n_observations_+h), self.coef_, self.n_observations_)

    def forecast(self, h):
        return self.forecast_components(h)['total'].copy()
