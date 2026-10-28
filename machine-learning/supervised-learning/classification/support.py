"""Classification contracts, label encoding, probability normalization and CLI.

No model fitting logic lives here. Implementations use NumPy, never reference
estimators. Labels are homogeneous int64-compatible integers or nonempty strings.
"""
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
    """A bounded optimizer did not satisfy its documented stopping conditions."""


def numerical(function):
    @wraps(function)
    def guarded(*args, **kwargs):
        try:
            with np.errstate(over="raise", divide="raise", invalid="raise", under="ignore"):
                return function(*args, **kwargs)
        except (FloatingPointError, OverflowError, np.linalg.LinAlgError) as error:
            raise ValueError("unresolved numerical computation; rescale or regularize data") from error
    return guarded


def scalar(value, name, low=0.0, high=1e12, *, positive=False):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, float, np.integer, np.floating)):
        raise ValueError(f"{name} must be a finite real scalar")
    try:
        value = float(value)
    except OverflowError as error:
        raise ValueError(f"{name} cannot be represented") from error
    if not np.isfinite(value) or not low <= value <= high or (positive and value == low):
        raise ValueError(f"{name} outside supported range")
    return value


def integer(value, name, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} must be a native integer in {low}..{high}")
    return value


def boolean(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} must be bool")
    return value


def features(X, *, fitting=False, expected=None, max_samples=None, max_features=128):
    a = np.asarray(X)
    limit = (2048 if fitting else 10000) if max_samples is None else max_samples
    if a.ndim != 2 or not 1 <= a.shape[1] <= max_features:
        raise ValueError(f"X must be 2D with 1..{max_features} features")
    if a.size > MAX_CELLS or len(a) > limit or (fitting and len(a) == 0):
        raise ValueError("X sample/cell limit exceeded or empty training matrix")
    if a.dtype.kind not in "iuf":
        raise ValueError("X must be real numeric, excluding bool/complex/string/object")
    if expected is not None and a.shape[1] != expected:
        raise ValueError("prediction feature count differs from fitted features")
    a = np.array(a, dtype=np.float64, copy=True)
    if not np.isfinite(a).all() or np.any(np.abs(a) > MAX_VALUE):
        raise ValueError("X must be finite with magnitude <= 10^12")
    return a


def encode_labels(y, *, n=None):
    a = np.asarray(y, dtype=object)
    if a.ndim != 1 or not 1 <= len(a) <= 20000 or (n is not None and len(a) != n):
        raise ValueError("y must be a nonempty 1D label vector matching X")
    values = a.tolist()
    ints = all(isinstance(v, (int, np.integer)) and not isinstance(v, (bool, np.bool_)) for v in values)
    strings = all(isinstance(v, str) and 1 <= len(v) <= 256 for v in values)
    if not ints and not strings:
        raise ValueError("labels must be homogeneous int64 integers or nonempty strings; no bool/float/mixed coercion")
    if ints:
        if any(not -(2**63) <= int(v) < 2**63 for v in values):
            raise ValueError("integer labels must fit signed int64")
        values = [int(v) for v in values]
    unique = sorted(set(values))
    if len(unique) > 32:
        raise ValueError("at most 32 classes supported")
    classes = np.array(unique, dtype=np.int64 if ints else str)
    lookup = {v: i for i, v in enumerate(unique)}
    encoded = np.array([lookup[v] for v in values], dtype=np.int64)
    return np.array(values, dtype=classes.dtype), classes, encoded


def training(X, y, *, binary=False, **limits):
    X = features(X, fitting=True, **limits)
    original, classes, encoded = encode_labels(y, n=len(X))
    if binary and len(classes) != 2:
        raise ValueError("exactly two classes required by this binary classifier")
    return X, original, classes, encoded


def categorical_columns(X, columns, *, fitting=False):
    for j in columns:
        if not np.equal(X[:, j], np.floor(X[:, j])).all():
            raise ValueError("categorical columns require numeric integer codes")
        if fitting and len(np.unique(X[:, j])) > 64:
            raise ValueError("at most 64 observed categories per feature")
    return X


def priors(counts, supplied=None):
    if supplied is None:
        return counts/counts.sum()
    a = np.asarray(supplied)
    if a.shape != counts.shape or a.dtype.kind not in "iuf":
        raise ValueError("one numeric prior per sorted class required")
    a = np.array(a, dtype=float, copy=True)
    if not np.isfinite(a).all() or np.any(a <= 0) or not np.isclose(a.sum(), 1, atol=1e-12, rtol=1e-12):
        raise ValueError("class priors must be positive and sum to one")
    return a


def finite(value, name="result"):
    if not np.isfinite(value).all():
        raise ValueError(f"nonfinite {name}; rescale data")
    return value


def positive_definite_factor(matrix):
    """Reject unresolved covariance directions before Cholesky roundoff can hide them."""
    eigenvalues=np.linalg.eigvalsh(matrix)
    threshold=np.finfo(float).eps*len(matrix)*max(float(eigenvalues[-1]),np.finfo(float).tiny)
    if eigenvalues[0]<=threshold:
        raise ValueError("covariance is singular or unresolved at float64 precision; regularize/rescale")
    return np.linalg.cholesky(matrix)


def sigmoid(z):
    z = np.asarray(z, dtype=float)
    result = np.empty_like(z)
    positive = z >= 0
    result[positive] = 1/(1+np.exp(-z[positive]))
    ez = np.exp(z[~positive])
    result[~positive] = ez/(1+ez)
    return result


def normalize_log_scores(scores):
    scores = finite(np.asarray(scores), "log scores")
    if len(scores) == 0:
        return np.empty_like(scores)
    shifted = scores - scores.max(axis=1, keepdims=True)
    weights = np.exp(shifted)
    return weights/weights.sum(axis=1, keepdims=True)


class Classifier:
    def _check_X(self, X):
        if not hasattr(self, "classes_"):
            raise ValueError("fit must succeed before prediction")
        return features(X, expected=self.n_features_in_)

    def score(self, X, y):
        prediction = self.predict(X)
        original, _, _ = encode_labels(y, n=len(prediction))
        if original.dtype.kind != prediction.dtype.kind and not (original.dtype.kind in "iu" and prediction.dtype.kind in "iu"):
            raise ValueError("evaluation labels must use the fitted label family")
        return float(np.mean(original == prediction))


class ProbabilisticClassifier(Classifier):
    @numerical
    def predict_proba(self, X):
        return normalize_log_scores(self.decision_function(X))

    def predict(self, X):
        scores = self.decision_function(X)
        return self.classes_[np.argmax(scores, axis=1)]


@lru_cache(None)
def load(name):
    if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) is None:
        raise ValueError("canonical kebab-case topic required")
    spec = importlib.util.spec_from_file_location("atlas_classification_"+name.replace("-", "_"), Path(__file__).parent/name/"python/solution.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main(estimator):
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict) or not {"X", "y", "predict"} <= data.keys() or set(data)-{"X", "y", "predict", "parameters"}:
            raise ValueError("JSON requires X,y,predict and optional parameters")
        parameters = data.get("parameters", {})
        if not isinstance(parameters, dict):
            raise ValueError("parameters must be an object")
        model = estimator(**parameters).fit(data["X"], data["y"])
        print(json.dumps(dict(predictions=model.predict(data["predict"]).tolist()), allow_nan=False))
    except (ValueError, TypeError, ConvergenceError) as error:
        print("error: "+str(error), file=sys.stderr)
        raise SystemExit(2)
