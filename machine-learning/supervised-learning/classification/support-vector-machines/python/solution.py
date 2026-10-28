"""Binary linear C-SVM dual with bounded ADMM and primal/dual certificates."""
import importlib.util
from pathlib import Path
import sys
import numpy as np
if 'atlas_classification_support' not in sys.modules:
    _spec = importlib.util.spec_from_file_location('atlas_classification_support', Path(__file__).resolve().parents[2] / 'support.py')
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = _module
    _spec.loader.exec_module(_module)
_support = sys.modules['atlas_classification_support']

def _project(vector, signed, C):
    bound = float(np.max(np.abs(vector))) + C
    low, high = (-bound, bound)
    for _ in range(80):
        middle = low + (high - low) / 2
        result = np.clip(vector - middle * signed, 0, C)
        total = float(signed @ result)
        if total == 0:
            return result
        if total > 0:
            low = middle
        else:
            high = middle
    return np.clip(vector - (low + (high - low) / 2) * signed, 0, C)

def _certificate(X, signed, alpha, C):
    coefficient = X.T @ (signed * alpha)
    raw = X @ coefficient
    boundaries = np.sort(signed - raw)
    positives = int(np.count_nonzero(signed > 0))
    bias = float(boundaries[positives - 1] / 2 + boundaries[positives] / 2)
    margin = signed * (raw + bias)
    norm = float(coefficient @ coefficient)
    primal = norm / 2 + C * float(np.maximum(1 - margin, 0).sum())
    dual = float(alpha.sum()) - norm / 2
    return (coefficient, bias, margin, primal, dual, primal - dual)

class SupportVectorMachine(_support.Classifier):

    def __init__(self, C=1.0, *, rho=1.0, tol=1e-07, max_iter=20000):
        self.C = _support.scalar(C, 'C', high=1000000.0, positive=True)
        self.rho = _support.scalar(rho, 'rho', high=1000000.0, positive=True)
        self.tol = _support.scalar(tol, 'tol', high=0.01, positive=True)
        self.max_iter = _support.integer(max_iter, 'max_iter', 1, 100000)

    @_support.numerical
    def fit(self, X, y):
        C = _support.scalar(self.C, 'C', high=1000000.0, positive=True)
        rho = _support.scalar(self.rho, 'rho', high=1000000.0, positive=True)
        tolerance = _support.scalar(self.tol, 'tol', high=0.01, positive=True)
        maximum = _support.integer(self.max_iter, 'max_iter', 1, 100000)
        X, _, classes, encoded = _support.training(X, y, binary=True, max_samples=256, max_features=64)
        signed = 2 * encoded - 1
        offset = X.mean(axis=0)
        A = X - offset
        Q = A @ A.T * signed[:, None] * signed[None, :]
        eigenvalues, eigenvectors = np.linalg.eigh(Q)
        scale = max(1.0, float(np.max(np.abs(eigenvalues))))
        if eigenvalues[0] < -64 * np.finfo(float).eps * len(X) * scale:
            raise ValueError('dual Gram matrix unresolved beyond roundoff')
        reciprocal = 1 / (np.maximum(eigenvalues, 0) + rho)

        def inverse(v):
            return eigenvectors @ (eigenvectors.T @ v * reciprocal)
        constraint = inverse(signed)
        denominator = float(signed @ constraint)
        if denominator <= 0:
            raise ValueError('unresolved dual equality solve; rescale input')
        z = np.zeros(len(X))
        multiplier = np.zeros(len(X))
        ones = np.ones(len(X))
        last_gap = float('inf')
        for iteration in range(1, maximum + 1):
            unconstrained = inverse(ones + rho * (z - multiplier))
            alpha = unconstrained - constraint * (signed @ unconstrained / denominator)
            old = z.copy()
            z = np.clip(alpha + multiplier, 0, C)
            multiplier += alpha - z
            primal_residual = float(np.linalg.norm(alpha - z))
            dual_residual = float(rho * np.linalg.norm(z - old))
            primal_limit = tolerance * (np.sqrt(len(X)) + max(np.linalg.norm(alpha), np.linalg.norm(z)))
            dual_limit = tolerance * (np.sqrt(len(X)) + np.linalg.norm(rho * multiplier))
            if primal_residual <= primal_limit and dual_residual <= dual_limit:
                feasible = _project(z, signed, C)
                coefficient, bias, margin, primal, dual, last_gap = _certificate(A, signed, feasible, C)
                limit = tolerance * (1 + abs(primal) + abs(dual))
                if last_gap < -10 * limit:
                    raise ValueError('numerically inconsistent SVM gap; rescale data')
                if last_gap <= limit:
                    intercept = float(bias - offset @ coefficient)
                    _support.finite(coefficient)
                    _support.finite(intercept)
                    support = np.flatnonzero(feasible > tolerance)
                    self.__dict__.update(classes_=classes.copy(), n_features_in_=X.shape[1], coef_=coefficient.copy(), intercept_=intercept, alpha_=feasible.copy(), dual_coef_=(signed * feasible).copy(), support_=support, support_vectors_=X[support].copy(), training_margin_=margin.copy(), primal_objective_=primal, dual_objective_=dual, duality_gap_=max(0.0, last_gap), equality_residual_=abs(float(signed @ feasible)), primal_residual_=primal_residual, dual_residual_=dual_residual, n_iter_=iteration, converged_=True)
                    return self
        raise _support.ConvergenceError(f'SVM residual/gap checks unmet after {maximum} iterations (last_gap={last_gap:g})')

    @_support.numerical
    def decision_function(self, X):
        X = self._check_X(X)
        return _support.finite(X @ self.coef_ + self.intercept_, 'SVM margin')

    def predict(self, X):
        margin = self.decision_function(X)
        return self.classes_[(margin >= 0).astype(int)]
if __name__ == '__main__':
    _support.main(SupportVectorMachine)
