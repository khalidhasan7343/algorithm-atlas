"""Ridge by augmented least squares; no inverse or penalized intercept."""
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("atlas_regression_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)


class RidgeRegression(_support.LinearPredictor):
    def __init__(self, alpha=1.0, *, fit_intercept=True):
        self.alpha = _support.scalar(alpha, "alpha")
        self.fit_intercept = _support.boolean(fit_intercept, "fit_intercept")

    @_support.numerical
    def fit(self, X, y):
        alpha = _support.scalar(self.alpha, "alpha")
        X, y, centered, target, x_offset, y_offset = _support.training(X, y, self.fit_intercept)
        augmented = np.vstack((centered, np.sqrt(alpha) * np.eye(X.shape[1])))
        rhs = np.concatenate((target, np.zeros(X.shape[1])))
        coefficient, _, rank, singular = np.linalg.lstsq(augmented, rhs, rcond=None)
        return _support.commit_linear(self, X, y, coefficient, y_offset - x_offset @ coefficient,
                                      rank_=int(rank), singular_values_=singular.copy(), n_iter_=1,
                                      objective_=float(np.sum((centered @ coefficient - target)**2) / 2 + alpha * (coefficient @ coefficient) / 2))


@_support.numerical
def loss_gradient(X, y, coefficient, intercept=0.0, alpha=1.0):
    """Half RSS plus alpha/2 squared norm; intercept is unpenalized."""
    X = _support.features(X, fitting=True)
    y = _support.targets(y, len(X))
    coefficient = np.asarray(coefficient, dtype=np.float64)
    if coefficient.shape != (X.shape[1],) or not np.isfinite(coefficient).all():
        raise ValueError("one finite coefficient per feature required")
    alpha = _support.scalar(alpha, "alpha")
    intercept = _support.scalar(intercept, "intercept", -1e12)
    residual = X @ coefficient + intercept - y
    return float((residual @ residual + alpha * (coefficient @ coefficient)) / 2), X.T @ residual + alpha * coefficient, float(residual.sum())


if __name__ == "__main__":
    _support.main(RidgeRegression)
