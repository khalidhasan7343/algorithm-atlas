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

base = s.load('arima')


class SARIMA(base.ARIMA):
    """Multiplicative seasonal ARIMA, sharing the canonical innovation/CSS engine."""
    def __init__(self, order=(1, 0, 0), seasonal_order=(1, 0, 0, 4), **kwargs):
        if not isinstance(seasonal_order, (tuple, list)) or len(seasonal_order) != 4:
            raise ValueError('seasonal_order must be (P,D,Q,s)')
        self.P = s.integer(seasonal_order[0], 'P', 0, 1)
        self.D = s.integer(seasonal_order[1], 'D', 0, 1)
        self.Q = s.integer(seasonal_order[2], 'Q', 0, 1)
        self.period = s.integer(seasonal_order[3], 'seasonal period', 2, 12)
        super().__init__(order, **kwargs)

    def _groups(self):
        return dict(ar=self.p, ma=self.q, seasonal_ar=self.P, seasonal_ma=self.Q)

    def _lags(self):
        return [self.period]*self.D+[1]*self.d

    def _polynomials(self, parts, jac):
        ar, ma, dar, dma = super()._polynomials(parts, jac)
        seasonal_ar, dsa = base._component(self.P, parts['seasonal_ar'], jac['seasonal_ar'], -1, self.period)
        seasonal_ma, dsm = base._component(self.Q, parts['seasonal_ma'], jac['seasonal_ma'], 1, self.period)
        # Product-rule sensitivities preserve nonseasonal/seasonal cross-lags.
        product_ar = np.convolve(ar, seasonal_ar)
        product_ma = np.convolve(ma, seasonal_ma)
        k = dar.shape[0]
        product_dar = np.empty((k, len(product_ar)))
        product_dma = np.empty((k, len(product_ma)))
        for j in range(k):
            product_dar[j] = np.convolve(dar[j], seasonal_ar)+np.convolve(ar, dsa[j])
            product_dma[j] = np.convolve(dma[j], seasonal_ma)+np.convolve(ma, dsm[j])
        return product_ar, product_ma, product_dar, product_dma
