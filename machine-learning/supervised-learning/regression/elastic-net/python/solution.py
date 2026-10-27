"""Cyclic coordinate minimization for an explicitly normalized L1/L2 objective."""
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("atlas_regression_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)


class ElasticNetRegression(_support.LinearPredictor):
    def __init__(self, alpha=1.0, l1_ratio=0.5, *, fit_intercept=True, tol=1e-7, max_iter=10000):
        self.alpha = _support.scalar(alpha, "alpha")
        self.l1_ratio = _support.scalar(l1_ratio, "l1_ratio", high=1.0)
        self.fit_intercept = _support.boolean(fit_intercept, "fit_intercept")
        self.tol = _support.scalar(tol, "tol", high=1.0, positive=True)
        self.max_iter = _support.integer(max_iter, "max_iter", 1, 100000)

    @_support.numerical
    def fit(self, X, y):
        alpha = _support.scalar(self.alpha, "alpha")
        ratio = _support.scalar(self.l1_ratio, "l1_ratio", high=1.0)
        tol = _support.scalar(self.tol, "tol", high=1.0, positive=True)
        iterations = _support.integer(self.max_iter, "max_iter", 1, 100000)
        X, y, A, target, x_offset, y_offset = _support.training(X, y, self.fit_intercept)
        n, p = A.shape
        l1, l2 = alpha * ratio, alpha * (1.0 - ratio)
        coefficient = np.zeros(p)
        curvature = np.sum(A * A, axis=0) / n
        residual = target.copy()
        history = [float(target @ target / (2*n))]
        threshold = tol * max(1.0, float(np.max(np.abs(A.T @ target / n))))
        for iteration in range(1, iterations + 1):
            for j in range(p):
                denominator = curvature[j] + l2
                if denominator == 0:
                    continue
                partial = residual + A[:, j] * coefficient[j]
                correlation = float(A[:, j] @ partial / n)
                coefficient[j] = np.sign(correlation) * max(abs(correlation) - l1, 0.0) / denominator
                residual = partial - A[:, j] * coefficient[j]
            residual = target - A @ coefficient
            objective = float(residual @ residual / (2*n) + l1 * np.abs(coefficient).sum() + l2 * (coefficient @ coefficient) / 2)
            violation = _support.kkt_violation(A, target, coefficient, l1, l2)
            history.append(objective)
            if violation <= threshold:
                return _support.commit_linear(self, X, y, coefficient, y_offset - x_offset @ coefficient,
                                              n_iter_=iteration, objective_=objective, loss_history_=np.array(history),
                                              kkt_violation_=violation, stopping_threshold_=threshold)
        raise _support.ConvergenceError(f"Elastic Net did not meet KKT tolerance in {iterations} cycles (violation={violation:g}, threshold={threshold:g})")


if __name__ == "__main__":
    _support.main(ElasticNetRegression)
