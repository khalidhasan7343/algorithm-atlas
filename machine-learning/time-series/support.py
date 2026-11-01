"""Bounded time grids, owned data, chronological evaluation and scalar metrics."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

TOPICS = ('arima', 'sarima', 'exponential-smoothing', 'holt-winters', 'prophet', 'hidden-markov-models')

class NumericalError(FloatingPointError):
    """A valid request cannot be represented safely in the declared float64 domain."""


def integer(value, name, low, high):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)) or not low <= value <= high:
        raise ValueError(f'{name} must be an integer in [{low}, {high}]')
    return int(value)


def scalar(value, name, low, high):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, float, np.integer, np.floating)):
        raise ValueError(f'{name} must be real')
    try:
        result = float(value)
    except OverflowError as error:
        raise ValueError(f'{name} must fit float64') from error
    if not np.isfinite(result) or not low <= result <= high:
        raise ValueError(f'{name} outside [{low}, {high}]')
    return result


def vector(value, name='series', minimum=1):
    a = np.asarray(value)
    if a.ndim != 1 or not minimum <= len(a) <= 512 or a.dtype.kind not in 'iuf':
        raise ValueError(f'{name} must be a real vector with length {minimum}..512')
    a = np.array(a, dtype=float, copy=True)
    if not np.isfinite(a).all() or np.any(np.abs(a) > 1e6):
        raise ValueError(f'{name} must be finite with magnitude <=1e6')
    return a


def finite(value, name='computed state'):
    a = np.asarray(value)
    if not np.isfinite(a).all() or np.any(np.abs(a) > 1e100):
        raise NumericalError(f'nonfinite or excessive {name}')
    return value


def horizon(value):
    return integer(value, 'horizon', 1, 128)


class TimeGrid:
    """Regular numeric ticks or whole-second datetime64; never sort/impute."""
    def __init__(self, n, timestamps=None, frequency=None):
        self.datetime = False
        if timestamps is None:
            self.values = np.arange(n, dtype=float)
            self.step = 1. if frequency is None else scalar(frequency, 'frequency', 1e-8, 1e8)
            self.values *= self.step
        else:
            raw = np.asarray(timestamps)
            if raw.ndim != 1 or len(raw) != n:
                raise ValueError('timestamps must match series length')
            self.datetime = raw.dtype.kind == 'M'
            if self.datetime:
                if np.isnat(raw).any():
                    raise ValueError('missing timestamp')
                seconds = raw.astype('datetime64[s]')
                if np.any(seconds.astype(raw.dtype) != raw):
                    raise ValueError('timestamps require whole-second resolution')
                values = seconds.astype(np.int64)
            elif raw.dtype.kind in 'iuf':
                values = np.array(raw, dtype=float, copy=True)
            else:
                raise ValueError('numeric or datetime64 timestamps required')
            if not np.isfinite(values).all() or np.any(np.abs(values) > 1e12):
                raise ValueError('timestamp outside finite supported range')
            differences = np.diff(values)
            if len(differences) and (np.any(differences <= 0) or not np.allclose(differences, differences[0], rtol=1e-10, atol=1e-10)):
                raise ValueError('timestamps must be strictly increasing and regular')
            if not len(differences) and frequency is None:
                raise ValueError('one explicit timestamp requires frequency')
            inferred = float(differences[0]) if len(differences) else float(frequency)
            self.step = scalar(inferred, 'frequency', 1e-8, 1e8)
            if frequency is not None and not np.isclose(scalar(frequency, 'frequency', 1e-8, 1e8), self.step, rtol=1e-10, atol=1e-10):
                raise ValueError('frequency differs from timestamp spacing')
            self.values = values.copy()
        if self.datetime and self.step != int(self.step):
            raise ValueError('datetime frequency must be whole seconds')

    def future(self, h):
        h = horizon(h)
        values = self.values[-1] + self.step * np.arange(1, h + 1)
        if not np.isfinite(values).all() or np.any(np.abs(values) > 1e12):
            raise NumericalError('future timestamp outside supported range')
        if self.datetime:
            return values.astype(np.int64).astype('datetime64[s]')
        return values.copy()


class Forecaster:
    def _ready(self):
        if not hasattr(self, 'grid_'):
            raise ValueError('fit/filter the model first')

    def forecast_index(self, h):
        self._ready()
        return self.grid_.future(h)


def difference(y, lags):
    """Apply ordered differencing; retain each pre-operation training history."""
    values = vector(y)
    traces = []
    if not isinstance(lags, (tuple, list)) or len(lags) > 3:
        raise ValueError('at most three difference operators')
    for lag in lags:
        lag = integer(lag, 'lag', 1, 12)
        if len(values) <= lag:
            raise ValueError('insufficient differencing history')
        traces.append((lag, values.copy()))
        values = values[lag:] - values[:-lag]
    return values, traces


def inverse_difference(future, traces):
    values = np.array(future, dtype=float, copy=True)
    if values.ndim != 1 or not 1 <= len(values) <= 128:
        raise ValueError('1..128 differenced future values required')
    finite(values, 'differenced forecast')
    for lag, history in reversed(traces):
        memory = list(history)
        restored = []
        for item in values:
            value = float(item + memory[-lag])
            finite(value, 'inverse difference')
            restored.append(value)
            memory.append(value)
        values = np.array(restored)
    return finite(values, 'forecast')


def forecast_metrics(actual, predicted, *, training=None, seasonal_period=1):
    a, p = vector(actual, 'actual'), vector(predicted, 'predicted')
    if a.shape != p.shape:
        raise ValueError('metric shapes differ')
    error = a-p
    out = dict(mae=float(np.mean(np.abs(error))), mse=float(np.mean(error**2)), rmse=float(np.sqrt(np.mean(error**2))))
    denominator = np.abs(a)+np.abs(p)
    ratios = np.divide(2*np.abs(error), denominator, out=np.zeros_like(a), where=denominator != 0)
    out['smape'] = float(100*np.mean(ratios))
    if np.any(a == 0):
        out['mape'] = None
    else:
        try:
            with np.errstate(over='raise', divide='raise', invalid='raise'):
                out['mape'] = float(100*np.mean(np.abs(error/a)))
        except FloatingPointError as error:
            raise NumericalError('MAPE exceeds supported float64 range') from error
    if training is not None:
        train = vector(training, 'training')
        lag = integer(seasonal_period, 'seasonal_period', 1, 12)
        if len(train) <= lag:
            raise ValueError('insufficient MASE training history')
        scale = float(np.mean(np.abs(train[lag:]-train[:-lag])))
        if scale == 0:
            raise ValueError('MASE undefined for zero training scale')
        try:
            with np.errstate(over='raise', divide='raise', invalid='raise'):
                out['mase'] = float(np.float64(out['mae'])/scale)
        except FloatingPointError as error:
            raise NumericalError('MASE exceeds supported float64 range') from error
    for value in out.values():
        if value is not None:
            finite(value, 'forecast metric')
    return out


def backtest(factory, y, *, initial, horizon_size=1, step=1, window=None):
    """Fresh fits on chronological prefixes/windows; fixed-origin recursive forecasts."""
    y = vector(y)
    initial = integer(initial, 'initial', 1, len(y)-1)
    h = horizon(horizon_size)
    step = integer(step, 'step', 1, 512)
    if window is not None:
        window = integer(window, 'window', 1, initial)
    origins = list(range(initial, len(y)-h+1, step))
    if not origins or len(origins) > 32 or not callable(factory):
        raise ValueError('1..32 evaluation origins and a model factory required')
    models, records = [], []
    for origin in origins:
        start = 0 if window is None else origin-window
        model = factory()
        if not callable(getattr(model, 'fit', None)) or not callable(getattr(model, 'forecast', None)):
            raise ValueError('factory must return a forecasting model with fit/forecast')
        if any(model is previous for previous in models):
            raise ValueError('factory must return a fresh model per origin')
        models.append(model)
        model.fit(y[start:origin].copy())
        predictions = vector(model.forecast(h), 'forecast')
        if predictions.shape != (h,):
            raise ValueError('forecast length differs from horizon')
        records.append(dict(train_start=start, train_stop=origin, test_start=origin, test_stop=origin+h,
                            predicted=predictions, actual=y[origin:origin+h].copy(),
                            metrics=forecast_metrics(y[origin:origin+h], predictions)))
    return records


def load(topic):
    if topic not in TOPICS:
        raise ValueError('unknown B11 canonical')
    name = 'atlas_b11_' + topic.replace('-', '_')
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).parent/topic/'python/solution.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:
            del sys.modules[name]
            raise
    return sys.modules[name]
