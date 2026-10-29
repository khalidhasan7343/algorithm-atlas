"""B3 contracts and canonical ML reuse; no ensemble training loops here."""
from functools import lru_cache
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parent


def module_at(name, path):
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


classification = module_at('atlas_classification_support', ROOT.parent/'supervised-learning/classification/support.py')
regression = module_at('atlas_regression_support', ROOT.parent/'supervised-learning/regression/support.py')
metrics = module_at('atlas_classification_metrics', ROOT.parent/'supervised-learning/classification/metrics.py')
numerical = classification.numerical
integer = classification.integer
scalar = classification.scalar
boolean = classification.boolean
finite = classification.finite
encode_labels = classification.encode_labels


def features(X, *, fitting=False, expected=None, max_samples=None, max_features=32):
    return classification.features(X, fitting=fitting, expected=expected,
                                   max_samples=(512 if fitting else 4096) if max_samples is None else max_samples,
                                   max_features=max_features)


def training(X, y, task, **limits):
    X = features(X, fitting=True, **limits)
    if task == 'classification':
        original, classes, encoded = encode_labels(y, n=len(X))
        return X, encoded, classes, original
    return X, regression.targets(y, len(X)), None, None


def seed(value):
    return integer(value, 'random_state', 0, 2**32-1)


def weights(value, n):
    if value is None:
        return np.full(n, 1/n)
    a = np.asarray(value)
    if a.shape != (n,) or a.dtype.kind not in 'iuf':
        raise ValueError('sample weights must be a real vector matching samples')
    a = np.array(a, dtype=float, copy=True)
    if not np.isfinite(a).all() or np.any(a < 0) or not np.any(a > 0):
        raise ValueError('sample weights must be finite, nonnegative and have positive total')
    a /= a.max()  # Avoid overflowing the unnormalized sum.
    a /= a.sum()
    return a


def sample_count(value, n):
    if type(value) is int:
        return integer(value, 'max_samples', 1, 512)
    ratio = scalar(value, 'max_samples', high=1, positive=True)
    return max(1, int(np.ceil(ratio*n)))


def feature_count(value, p):
    if value is None:
        return p
    if isinstance(value, str) and value == 'sqrt':
        return max(1, int(np.sqrt(p)))
    return integer(value, 'max_features', 1, p)


def new_estimator(factory, random_state):
    if not callable(factory):
        raise ValueError('base estimators must be factories accepting one integer seed')
    model = factory(random_state)
    if not callable(getattr(model, 'fit', None)) or not callable(getattr(model, 'predict', None)):
        raise ValueError('factory must return an unfitted fit/predict estimator')
    if any(hasattr(model, name) for name in ('n_features_in_', 'classes_', 'coef_', 'tree_')):
        raise ValueError('factory must return a fresh unfitted estimator')
    return model


def probability(model, X, classes):
    if not callable(getattr(model, 'predict_proba', None)) or not hasattr(model, 'classes_'):
        raise ValueError('soft aggregation requires predict_proba and classes_')
    observed, ordered, _ = encode_labels(model.classes_)
    if len(observed) != len(ordered):
        raise ValueError('base classes must be unique')
    if observed.dtype.kind != classes.dtype.kind:
        raise ValueError('base class label family differs from ensemble')
    a = np.asarray(model.predict_proba(X))
    if a.dtype.kind not in 'iuf' or a.shape != (len(X), len(observed)):
        raise ValueError('base probability shape/type is invalid')
    a = np.array(a, dtype=float, copy=True)
    if not np.isfinite(a).all() or np.any(a < 0) or np.any(a > 1) or not np.allclose(a.sum(axis=1), 1, atol=1e-10, rtol=1e-10):
        raise ValueError('base probabilities must be normalized and finite')
    out = np.zeros((len(X), len(classes)))
    lookup = {v: j for j, v in enumerate(classes.tolist())}
    for j, label in enumerate(observed.tolist()):
        if label not in lookup:
            raise ValueError('base class absent from ensemble classes')
        out[:, lookup[label]] = a[:, j]
    return out


def label_votes(model, X, classes):
    prediction = model.predict(X)
    if len(X) == 0:
        if np.asarray(prediction).shape != (0,):
            raise ValueError('base prediction shape is invalid')
        return np.zeros((0, len(classes)))
    original, _, _ = encode_labels(prediction, n=len(X))
    if original.dtype.kind != classes.dtype.kind:
        raise ValueError('base prediction label family differs')
    lookup = {v: j for j, v in enumerate(classes.tolist())}
    try:
        indices = np.array([lookup[v] for v in original.tolist()])
    except KeyError as error:
        raise ValueError('unknown predicted class') from error
    return np.eye(len(classes))[indices]


def regression_prediction(model, X):
    value = np.asarray(model.predict(X))
    if value.dtype.kind not in 'iuf' or value.shape != (len(X),):
        raise ValueError('base regression predictions must be a real vector')
    return finite(np.array(value, dtype=float, copy=True), 'base predictions')


class Regressor:
    def _check_X(self, X):
        if not hasattr(self, 'n_features_in_'):
            raise ValueError('fit must succeed before prediction')
        return features(X, expected=self.n_features_in_)

    def score(self, X, y):
        return regression.r2(y, self.predict(X))


class Classifier(classification.Classifier):
    def _check_X(self, X):
        if not hasattr(self, 'classes_'):
            raise ValueError('fit must succeed before prediction')
        return features(X, expected=self.n_features_in_)

    def predict(self, X):
        probabilities = self.predict_proba(X)
        return self.classes_[np.argmax(probabilities, axis=1)]


@lru_cache(None)
def load(name):
    import re
    if re.fullmatch(r'[a-z]+(?:-[a-z]+)*', name) is None:
        raise ValueError('canonical name required')
    return module_at('atlas_ensemble_'+name.replace('-', '_'), ROOT/name/'python/solution.py')


def main(estimator):
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict) or not {'X', 'y', 'predict'} <= data.keys() or set(data)-{'X', 'y', 'predict', 'parameters'}:
            raise ValueError('JSON requires X, y, predict and optional parameters')
        parameters = data.get('parameters', {})
        if not isinstance(parameters, dict):
            raise ValueError('parameters must be an object')
        model = estimator(**parameters).fit(data['X'], data['y'])
        print(json.dumps(dict(predictions=model.predict(data['predict']).tolist()), allow_nan=False))
    except (ValueError, TypeError, classification.ConvergenceError) as error:
        print('error: '+str(error), file=sys.stderr)
        raise SystemExit(2)
