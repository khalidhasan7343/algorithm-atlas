"""Regression array contracts, metrics and local import/CLI support; no solver."""
from __future__ import annotations

from functools import lru_cache, wraps
import importlib.util
import json
from pathlib import Path
import re
import sys

import numpy as np

MAX_CELLS = 262144
MAX_VALUE = 1e12


class ConvergenceError(RuntimeError):
    """A bounded iterative fit did not meet its documented numerical checks."""


def numerical(function):
    @wraps(function)
    def guarded(*args, **kwargs):
        try:
            with np.errstate(over="raise", invalid="raise", divide="raise"):
                return function(*args, **kwargs)
        except (FloatingPointError, OverflowError, np.linalg.LinAlgError) as error:
            raise ValueError("numerical computation failed; rescale or inspect the input") from error
    return guarded


def scalar(value, name, low=0.0, high=1e12, *, positive=False):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, float, np.integer, np.floating)):
        raise ValueError(f"{name} must be a real scalar")
    try:
        value = float(value)
    except (OverflowError, ValueError) as error:
        raise ValueError(f"{name} cannot be represented as a finite scalar") from error
    if not np.isfinite(value) or not low <= value <= high or (positive and value == low):
        raise ValueError(f"{name} outside the finite supported range")
    return value


def integer(value, name, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} must be an integer in {low}..{high}")
    return value


def boolean(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} must be bool")
    return value


def _array(value, name):
    try:
        array = np.asarray(value)
        if array.size > MAX_CELLS:
            raise ValueError(f"{name} exceeds the cell resource budget")
        if array.dtype.kind not in "iuf":
            raise ValueError(f"{name} must contain real numeric values, excluding bool")
        result = np.array(array, dtype=np.float64, copy=True)
    except (TypeError, OverflowError) as error:
        raise ValueError(f"{name} cannot be converted to float64") from error
    if not np.isfinite(result).all() or np.any(np.abs(result) > MAX_VALUE):
        raise ValueError(f"{name} must be finite and have magnitude <= 10^12")
    return result


def features(X, *, fitting=False, expected=None, max_samples=None, max_features=512):
    X = _array(X, "X")
    limit = (2048 if fitting else 10000) if max_samples is None else max_samples
    if X.ndim != 2 or not 1 <= X.shape[1] <= max_features:
        raise ValueError(f"X must be 2D with 1..{max_features} columns")
    if X.shape[0] > limit or (fitting and X.shape[0] == 0) or X.size > MAX_CELLS:
        raise ValueError("X sample/cell resource limit exceeded or empty training data")
    if expected is not None and X.shape[1] != expected:
        raise ValueError("prediction feature count differs from fitted data")
    return X


def targets(y, n):
    y = _array(y, "y")
    if y.ndim != 1 or y.shape[0] != n or n == 0:
        raise ValueError("y must be one-dimensional with one target per nonempty sample")
    return y


def training(X, y, fit_intercept, **limits):
    boolean(fit_intercept, "fit_intercept")
    X = features(X, fitting=True, **limits)
    y = targets(y, len(X))
    x_offset = X.mean(axis=0) if fit_intercept else np.zeros(X.shape[1])
    y_offset = float(y.mean()) if fit_intercept else 0.0
    return X, y, X - x_offset, y - y_offset, x_offset, y_offset


def mse(y, prediction):
    y = targets(y, len(prediction))
    prediction = np.asarray(prediction, dtype=np.float64)
    if prediction.shape != y.shape or not np.isfinite(prediction).all():
        raise ValueError("finite one-dimensional predictions matching y required")
    return float(np.mean((y - prediction)**2))


def r2(y, prediction):
    error = mse(y, prediction)
    variance = float(np.mean((np.asarray(y) - np.mean(y))**2))
    return 1.0 - error / variance if variance else (1.0 if error == 0 else 0.0)


def finite(value, name="result"):
    if not np.isfinite(value).all():
        raise ValueError(f"nonfinite {name}; rescale the problem")
    return value


def commit_linear(model, X, y, coefficient, intercept, **diagnostics):
    coefficient = np.array(finite(coefficient, "coefficient"), copy=True)
    intercept = float(finite(intercept, "intercept"))
    prediction = finite(X @ coefficient + intercept, "training prediction")
    state = dict(coef_=coefficient, intercept_=intercept, n_features_in_=X.shape[1],
                 training_mse_=mse(y, prediction), converged_=True, **diagnostics)
    model.__dict__.update(state)
    return model


class LinearPredictor:
    @numerical
    def predict(self, X):
        if not hasattr(self, "n_features_in_"):
            raise ValueError("fit must succeed before prediction")
        X = features(X, expected=self.n_features_in_)
        return finite(X @ self.coef_ + self.intercept_, "prediction")

    @numerical
    def score(self, X, y):
        return r2(y, self.predict(X))


def kkt_violation(X, y, coefficient, l1, l2):
    gradient = X.T @ (X @ coefficient - y) / len(y) + l2 * coefficient
    active = coefficient != 0
    residual = np.maximum(np.abs(gradient) - l1, 0)
    residual[active] = np.abs(gradient[active] + l1 * np.sign(coefficient[active]))
    return float(np.max(residual, initial=0.0))


@lru_cache(None)
def load(name):
    if re.fullmatch(r"[a-z]+(?:-[a-z]+)*", name) is None:
        raise ValueError("canonical name required")
    path = Path(__file__).parent / name / "python/solution.py"
    spec = importlib.util.spec_from_file_location("atlas_regression_" + name.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main(estimator):
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict) or not {"X", "y", "predict"} <= payload.keys():
            raise ValueError("JSON object with X, y and predict required")
        if set(payload) - {"X", "y", "predict", "parameters"}:
            raise ValueError("unexpected JSON fields")
        parameters = payload.get("parameters", {})
        if not isinstance(parameters, dict):
            raise ValueError("parameters must be an object")
        model = estimator(**parameters).fit(payload["X"], payload["y"])
        print(json.dumps({"predictions": model.predict(payload["predict"]).tolist()}, allow_nan=False, separators=(",", ":")))
    except (ValueError, TypeError, ConvergenceError) as error:
        print("error: " + str(error), file=sys.stderr)
        raise SystemExit(2)
