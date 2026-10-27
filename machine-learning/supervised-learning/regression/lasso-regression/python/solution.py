"""Cyclic coordinate descent for half mean squared error plus L1 penalty."""
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("atlas_regression_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)


class LassoRegression(_support.LinearPredictor):
    def __init__(self, alpha=1.0, *, fit_intercept=True, tol=1e-7, max_iter=10000):
        self.alpha = _support.scalar(alpha, "alpha")
        self.fit_intercept = _support.boolean(fit_intercept, "fit_intercept")
        self.tol = _support.scalar(tol, "tol", high=1.0, positive=True)
        self.max_iter = _support.integer(max_iter, "max_iter", 1, 100000)

    @_support.numerical
    def fit(self, X, y):
        alpha = _support.scalar(self.alpha, "alpha")
        tol = _support.scalar(self.tol, "tol", high=1.0, positive=True)
        iterations = _support.integer(self.max_iter, "max_iter", 1, 100000)
        X, y, A, target, x_offset, y_offset = _support.training(X, y, self.fit_intercept)
        n, p = A.shape
        coefficient = np.zeros(p)
        residual = target.copy()  # target - A @ coefficient
        curvature = np.sum(A * A, axis=0) / n
        history = [float(target @ target / (2*n))]
        threshold = tol * max(1.0, float(np.max(np.abs(A.T @ target / n))))
        for iteration in range(1, iterations + 1):
            for j in range(p):
                if curvature[j] == 0:
                    continue
                partial = residual + A[:, j] * coefficient[j]
                correlation = float(A[:, j] @ partial / n)
                coefficient[j] = np.sign(correlation) * max(abs(correlation) - alpha, 0.0) / curvature[j]
                residual = partial - A[:, j] * coefficient[j]
            # Recompute once per cycle to prevent accumulated residual drift.
            residual = target - A @ coefficient
            objective = float(residual @ residual / (2*n) + alpha * np.abs(coefficient).sum())
            violation = _support.kkt_violation(A, target, coefficient, alpha, 0.0)
            history.append(objective)
            if violation <= threshold:
                return _support.commit_linear(self, X, y, coefficient, y_offset - x_offset @ coefficient,
                                              n_iter_=iteration, objective_=objective, loss_history_=np.array(history),
                                              kkt_violation_=violation, stopping_threshold_=threshold)
        raise _support.ConvergenceError(f"Lasso did not meet KKT tolerance in {iterations} cycles (violation={violation:g}, threshold={threshold:g})")


if __name__ == "__main__":
    _support.main(LassoRegression)
