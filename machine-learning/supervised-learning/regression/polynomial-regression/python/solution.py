"""Graded multivariate monomial expansion plus canonical ordinary least squares."""
import importlib.util
from itertools import combinations_with_replacement
from math import comb
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("atlas_regression_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)


def _expand(X, powers):
    result = np.ones((len(X), len(powers)), dtype=np.float64)
    for j, power in enumerate(powers):
        for i, exponent in enumerate(power):
            if exponent:
                result[:, j] *= X[:, i] ** int(exponent)
    return _support.finite(result, "polynomial features")


class PolynomialRegression(_support.LinearPredictor):
    def __init__(self, degree=2, *, fit_intercept=True):
        self.degree = _support.integer(degree, "degree", 1, 8)
        self.fit_intercept = _support.boolean(fit_intercept, "fit_intercept")

    @_support.numerical
    def fit(self, X, y):
        degree = _support.integer(self.degree, "degree", 1, 8)
        X = _support.features(X, fitting=True, max_features=32)
        y = _support.targets(y, len(X))
        count = comb(X.shape[1] + degree, degree) - 1
        if count > 512 or len(X) * count > _support.MAX_CELLS:
            raise ValueError("polynomial expansion exceeds 512 features or cell budget")
        powers = []
        for order in range(1, degree + 1):
            for indices in combinations_with_replacement(range(X.shape[1]), order):
                powers.append(np.bincount(indices, minlength=X.shape[1]))
        powers = np.array(powers, dtype=np.int64)
        expanded = _expand(X, powers)
        model = _support.load("linear-regression").LinearRegression(fit_intercept=self.fit_intercept).fit(expanded, y)
        self.__dict__.update(n_features_in_=X.shape[1], powers_=powers, n_output_features_=count,
                             coef_=model.coef_.copy(), intercept_=model.intercept_, _linear_model=model,
                             rank_=model.rank_, condition_number_=model.condition_number_,
                             training_mse_=model.training_mse_, n_iter_=1, converged_=True)
        return self

    @_support.numerical
    def transform(self, X):
        if not hasattr(self, "n_features_in_"):
            raise ValueError("fit must succeed before transform")
        X = _support.features(X, expected=self.n_features_in_, max_features=32)
        if len(X) * self.n_output_features_ > _support.MAX_CELLS:
            raise ValueError("polynomial expansion cell budget exceeded")
        result = _expand(X, self.powers_)
        if np.any(np.abs(result) > _support.MAX_VALUE):
            raise ValueError("expanded features exceed supported magnitude 10^12")
        return result

    @_support.numerical
    def predict(self, X):
        expanded = self.transform(X)
        return self._linear_model.predict(expanded)


if __name__ == "__main__":
    _support.main(PolynomialRegression)
