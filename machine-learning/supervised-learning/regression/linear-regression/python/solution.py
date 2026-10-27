"""Ordinary least squares with an unpenalized optional intercept and SVD solve."""
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("atlas_regression_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)


class LinearRegression(_support.LinearPredictor):
    def __init__(self, *, fit_intercept=True):
        self.fit_intercept = _support.boolean(fit_intercept, "fit_intercept")

    @_support.numerical
    def fit(self, X, y):
        X, y, centered, target, x_offset, y_offset = _support.training(X, y, self.fit_intercept)
        coefficient, _, rank, singular = np.linalg.lstsq(centered, target, rcond=None)
        intercept = y_offset - x_offset @ coefficient
        condition = float(singular[0] / singular[-1]) if rank == X.shape[1] and singular[-1] > 0 else float("inf")
        return _support.commit_linear(self, X, y, coefficient, intercept, rank_=int(rank),
                                      singular_values_=singular.copy(), condition_number_=condition, n_iter_=1)


@_support.numerical
def loss_gradient(X, y, coefficient, intercept=0.0):
    """Half mean squared loss and smooth gradients, for mathematical inspection."""
    X = _support.features(X, fitting=True)
    y = _support.targets(y, len(X))
    coefficient = np.asarray(coefficient, dtype=np.float64)
    if coefficient.shape != (X.shape[1],) or not np.isfinite(coefficient).all():
        raise ValueError("one finite coefficient per feature required")
    intercept = _support.scalar(intercept, "intercept", -1e12)
    residual = X @ coefficient + intercept - y
    return float(residual @ residual / (2 * len(y))), X.T @ residual / len(y), float(residual.mean())


if __name__ == "__main__":
    _support.main(LinearRegression)
