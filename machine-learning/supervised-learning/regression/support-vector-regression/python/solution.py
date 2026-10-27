"""Epsilon-SVR dual solved by bounded ADMM; linear or RBF kernels."""
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("atlas_regression_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)


def _kernel_matrix(X, Y, kernel, gamma):
    if kernel == "linear":
        return X @ Y.T
    result = np.empty((len(X), len(Y)))
    # Explicit differences avoid catastrophic cancellation in norm expansion.
    block = max(1, _support.MAX_CELLS // max(1, len(Y) * X.shape[1]))
    for start in range(0, len(X), block):
        difference = X[start:start + block, None, :] - Y[None, :, :]
        distance = np.sum(difference * difference, axis=2)
        # exp(-large positive) legitimately rounds to zero in an RBF kernel.
        result[start:start + block] = np.exp(-gamma * distance)
    return result


def _project_box_zero(vector, C):
    """Euclidean projection onto [-C,C]^n intersect sum(beta)=0."""
    low, high = float(np.min(vector - C)), float(np.max(vector + C))
    for _ in range(80):
        middle = low + (high - low)/2
        projected = np.clip(vector - middle, -C, C)
        total = float(projected.sum())
        if total == 0:
            return projected
        if total > 0:
            low = middle
        else:
            high = middle
    return np.clip(vector - (low + (high - low)/2), -C, C)


def _certificate(K, target, beta, C, epsilon):
    fitted = K @ beta
    residual = target - fitted
    # For fixed beta, minimize summed epsilon-insensitive loss over b. The
    # central interval of the 2n residual +/- epsilon breakpoints is optimal.
    endpoints = np.concatenate((residual - epsilon, residual + epsilon))
    n = len(target)
    central = np.partition(endpoints, (n-1, n))
    offset = float(central[n-1]/2 + central[n]/2)
    squared_norm = max(0.0, float(beta @ fitted))
    primal = squared_norm/2 + C * float(np.maximum(np.abs(residual - offset) - epsilon, 0).sum())
    dual = float(target @ beta) - squared_norm/2 - epsilon * float(np.abs(beta).sum())
    return offset, primal, dual, primal - dual


class SupportVectorRegression(_support.LinearPredictor):
    def __init__(self, C=1.0, epsilon=0.1, *, kernel="rbf", gamma=None, rho=1.0, tol=1e-7, max_iter=10000):
        self.C = _support.scalar(C, "C", high=1e6, positive=True)
        self.epsilon = _support.scalar(epsilon, "epsilon")
        if kernel not in ("linear", "rbf"):
            raise ValueError("kernel must be linear or rbf")
        self.kernel = kernel
        self.gamma = None if gamma is None else _support.scalar(gamma, "gamma", positive=True)
        self.rho = _support.scalar(rho, "rho", high=1e6, positive=True)
        self.tol = _support.scalar(tol, "tol", high=0.01, positive=True)
        self.max_iter = _support.integer(max_iter, "max_iter", 1, 100000)

    @_support.numerical
    def fit(self, X, y):
        C = _support.scalar(self.C, "C", high=1e6, positive=True)
        epsilon = _support.scalar(self.epsilon, "epsilon")
        rho = _support.scalar(self.rho, "rho", high=1e6, positive=True)
        tol = _support.scalar(self.tol, "tol", high=0.01, positive=True)
        iterations = _support.integer(self.max_iter, "max_iter", 1, 100000)
        if self.kernel not in ("linear", "rbf"):
            raise ValueError("kernel must be linear or rbf")
        X = _support.features(X, fitting=True, max_samples=256, max_features=128)
        y = _support.targets(y, len(X))
        gamma = 1.0/X.shape[1] if self.gamma is None else _support.scalar(self.gamma, "gamma", positive=True)
        n = len(y)
        y_offset = float(y.mean())
        target = y - y_offset  # sum(beta)=0 makes this translation invariant.
        K = _support.finite(_kernel_matrix(X, X, self.kernel, gamma), "kernel")
        eigenvalues, eigenvectors = np.linalg.eigh(K)
        scale = max(1.0, float(np.max(np.abs(eigenvalues))))
        if eigenvalues[0] < -64*np.finfo(float).eps*n*scale:
            raise ValueError("computed kernel is not positive semidefinite within roundoff")
        inverse_eigenvalues = 1.0/(np.maximum(eigenvalues, 0.0) + rho)

        def inverse(vector):
            return eigenvectors @ ((eigenvectors.T @ vector) * inverse_eigenvalues)

        ones = np.ones(n)
        inverse_ones = inverse(ones)
        denominator = float(inverse_ones.sum())
        if denominator <= 0:
            raise ValueError("unresolved equality-constraint solve; rescale input")
        z, multiplier = np.zeros(n), np.zeros(n)
        last_gap = float("inf")
        for iteration in range(1, iterations + 1):
            unconstrained = inverse(target + rho*(z - multiplier))
            beta = unconstrained - inverse_ones*(unconstrained.sum()/denominator)
            old_z = z.copy()
            value = beta + multiplier
            z = np.clip(np.sign(value)*np.maximum(np.abs(value) - epsilon/rho, 0), -C, C)
            multiplier += beta - z
            primal_residual = float(np.linalg.norm(beta - z))
            dual_residual = float(rho*np.linalg.norm(z - old_z))
            primal_limit = tol*(np.sqrt(n) + max(np.linalg.norm(beta), np.linalg.norm(z)))
            dual_limit = tol*(np.sqrt(n) + np.linalg.norm(rho*multiplier))
            if primal_residual <= primal_limit and dual_residual <= dual_limit:
                feasible = _project_box_zero(z, C)
                offset, primal, dual, last_gap = _certificate(K, target, feasible, C, epsilon)
                gap_limit = tol*(1 + abs(primal) + abs(dual))
                if last_gap < -10*gap_limit:
                    raise ValueError("numerically inconsistent primal/dual certificate; rescale data")
                if last_gap <= gap_limit:
                    intercept = y_offset + offset
                    prediction = _support.finite(K @ feasible + intercept, "training prediction")
                    state = dict(n_features_in_=X.shape[1], _X_fit_=X.copy(), kernel_=self.kernel, gamma_=gamma,
                                 dual_coef_=feasible.copy(), intercept_=float(intercept),
                                 support_=np.flatnonzero(np.abs(feasible) > tol),
                                 n_iter_=iteration, converged_=True,
                                 primal_objective_=primal, dual_objective_=dual, duality_gap_=max(0.0, last_gap),
                                 primal_residual_=primal_residual, dual_residual_=dual_residual,
                                 equality_residual_=abs(float(feasible.sum())),
                                 smooth_dual_gradient_=(K @ feasible - target),
                                 training_mse_=_support.mse(y, prediction))
                    if self.kernel == "linear":
                        state["coef_"] = _support.finite(X.T @ feasible, "primal coefficient")
                    elif hasattr(self, "coef_"):
                        del self.coef_
                    self.__dict__.update(state)
                    return self
        raise _support.ConvergenceError(f"SVR did not meet residual and primal/dual gap checks in {iterations} iterations (last_gap={last_gap:g})")

    @_support.numerical
    def predict(self, X):
        if not hasattr(self, "n_features_in_"):
            raise ValueError("fit must succeed before prediction")
        X = _support.features(X, expected=self.n_features_in_, max_features=128)
        result = np.empty(len(X))
        for start in range(0, len(X), 128):
            kernel = _kernel_matrix(X[start:start + 128], self._X_fit_, self.kernel_, self.gamma_)
            result[start:start + 128] = kernel @ self.dual_coef_ + self.intercept_
        return _support.finite(result, "prediction")


if __name__ == "__main__":
    _support.main(SupportVectorRegression)
