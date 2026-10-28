"""Binary L2 logistic regression: Newton updates and bounded Armijo line search."""
import importlib.util
from pathlib import Path
import sys

import numpy as np

if "atlas_classification_support" not in sys.modules:
    _spec = importlib.util.spec_from_file_location("atlas_classification_support", Path(__file__).resolve().parents[2]/"support.py")
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = _module
    _spec.loader.exec_module(_module)
_support = sys.modules["atlas_classification_support"]


def _objective(A, target, parameters, penalty):
    logits = A @ parameters
    return float(np.logaddexp(0, -(2*target-1)*logits).mean() + (penalty*parameters) @ parameters/2)


@_support.numerical
def loss_gradient(X, y, coefficient, intercept=0.0, alpha=1.0):
    """Mean binary cross-entropy + alpha/2 ||w||², y explicitly in {0,1}."""
    X = _support.features(X, fitting=True)
    target = np.asarray(y)
    if target.shape != (len(X),) or not np.isin(target, (0, 1)).all():
        raise ValueError("gradient targets must be 0 or 1 and match X")
    target = target.astype(float)
    w = np.asarray(coefficient, dtype=float)
    if w.shape != (X.shape[1],) or not np.isfinite(w).all():
        raise ValueError("one finite coefficient per feature required")
    alpha = _support.scalar(alpha, "alpha", high=1e6)
    b = _support.scalar(intercept, "intercept", low=-1e12)
    z = X @ w + b
    residual = np.where(target == 1, -_support.sigmoid(-z), _support.sigmoid(z))
    loss = float(np.logaddexp(0, -(2*target-1)*z).mean() + alpha*(w @ w)/2)
    return loss, X.T @ residual/len(X) + alpha*w, float(residual.mean())


class LogisticRegression(_support.Classifier):
    def __init__(self, alpha=1.0, *, fit_intercept=True, tol=1e-8, max_iter=100):
        self.alpha = _support.scalar(alpha, "alpha", high=1e6)
        self.fit_intercept = _support.boolean(fit_intercept, "fit_intercept")
        self.tol = _support.scalar(tol, "tol", high=0.01, positive=True)
        self.max_iter = _support.integer(max_iter, "max_iter", 1, 10000)

    @_support.numerical
    def fit(self, X, y):
        alpha = _support.scalar(self.alpha, "alpha", high=1e6)
        use_bias = _support.boolean(self.fit_intercept, "fit_intercept")
        tolerance = _support.scalar(self.tol, "tol", high=0.01, positive=True)
        maximum = _support.integer(self.max_iter, "max_iter", 1, 10000)
        X, _, classes, encoded = _support.training(X, y, binary=True)
        offset = X.mean(axis=0) if use_bias else np.zeros(X.shape[1])
        centered = X-offset
        A = np.column_stack((centered, np.ones(len(X)))) if use_bias else centered
        penalty = np.full(A.shape[1], alpha)
        if use_bias:
            penalty[-1] = 0
        parameters = np.zeros(A.shape[1])
        history = [_objective(A, encoded, parameters, penalty)]
        for iteration in range(maximum+1):
            logits = A @ parameters
            probability = _support.sigmoid(logits)
            residual = np.where(encoded == 1, -_support.sigmoid(-logits), probability)
            gradient = A.T @ residual/len(X) + penalty*parameters
            violation = float(np.linalg.norm(gradient, ord=np.inf))
            if violation <= tolerance:
                coefficient = parameters[:-1].copy() if use_bias else parameters.copy()
                intercept = float(parameters[-1]-offset @ coefficient) if use_bias else 0.0
                _support.finite(coefficient); _support.finite(intercept)
                self.__dict__.update(classes_=classes.copy(), coef_=coefficient, intercept_=intercept,
                                     n_features_in_=X.shape[1], n_iter_=iteration, converged_=True,
                                     objective_=history[-1], loss_history_=np.array(history), gradient_norm_=violation)
                return self
            if iteration == maximum:
                break
            curvature = probability*_support.sigmoid(-logits)
            hessian = (A.T*curvature) @ A/len(X) + np.diag(penalty)
            direction = np.linalg.lstsq(hessian, gradient, rcond=None)[0]
            descent = float(gradient @ direction)
            if descent <= 0:
                direction = gradient/max(1.0, float(np.linalg.norm(gradient)))
                descent = float(gradient @ direction)
            step = 1.0
            for _ in range(60):
                candidate = parameters-step*direction
                objective = _objective(A, encoded, candidate, penalty)
                if objective <= history[-1]-1e-4*step*descent:
                    parameters = candidate
                    history.append(objective)
                    break
                step /= 2
            else:
                raise _support.ConvergenceError("logistic line search did not find a descent step; rescale input")
        raise _support.ConvergenceError(f"logistic gradient {violation:g} exceeds tol after {maximum} iterations")

    @_support.numerical
    def decision_function(self, X):
        X = self._check_X(X)
        return _support.finite(X @ self.coef_ + self.intercept_, "logit")

    @_support.numerical
    def predict_proba(self, X):
        logits = self.decision_function(X)
        return np.column_stack((_support.sigmoid(-logits), _support.sigmoid(logits)))

    def predict(self, X):
        scores = self.decision_function(X)
        return self.classes_[(scores >= 0).astype(int)]


if __name__ == "__main__":
    _support.main(LogisticRegression)
