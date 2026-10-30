"""Clustering contracts, bounded stable distances and canonical import/CLI reuse."""
from functools import lru_cache
import importlib.util
import json
from pathlib import Path
import re
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


classification = module_at('atlas_classification_support', ROOT.parents[1]/'supervised-learning/classification/support.py')
numerical = classification.numerical
integer = classification.integer
scalar = classification.scalar
boolean = classification.boolean
finite = classification.finite
ConvergenceError = classification.ConvergenceError


def features(X, *, fitting=False, expected=None, max_samples=None):
    limit = (512 if fitting else 4096) if max_samples is None else max_samples
    return classification.features(X, fitting=fitting, expected=expected,
                                   max_samples=limit, max_features=32)


def seed(value):
    return integer(value, 'random_state', 0, 2**32-1)


def row_norm(values):
    """Euclidean norm without squaring raw huge/tiny components."""
    a = np.asarray(values, dtype=float)
    scale = np.max(np.abs(a), axis=-1)
    divisor = np.where(scale == 0, 1, scale)
    with np.errstate(under='ignore'):
        result = scale*np.sqrt(np.sum((a/divisor[..., None])**2, axis=-1))
    return finite(result, 'distance')


def pairwise(X, Y=None):
    Y = X if Y is None else Y
    if len(X)*len(Y) > 4194304:
        raise ValueError('pairwise distance cell budget exceeded')
    result = np.empty((len(X), len(Y)))
    for i, row in enumerate(X):
        result[i] = row_norm(Y-row)
    return result


def mean(X):
    """Anchor-centering preserves an exactly constant column."""
    return X[0]+np.mean(X-X[0], axis=0)


def partition_labels(groups, n):
    result = np.empty(n, dtype=np.int64)
    for label, members in enumerate(sorted(groups, key=lambda g: min(g))):
        result[list(members)] = label
    return result


class Clusterer:
    def fit_predict(self, X):
        return self.fit(X).labels_.copy()

    def _check_X(self, X):
        if not hasattr(self, 'n_features_in_'):
            raise ValueError('fit must succeed before prediction')
        return features(X, expected=self.n_features_in_)


@lru_cache(None)
def load(name):
    if re.fullmatch(r'[a-z]+(?:-[a-z]+)*', name) is None:
        raise ValueError('canonical name required')
    return module_at('atlas_clustering_'+name.replace('-', '_'), ROOT/name/'python/solution.py')


def main(estimator):
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict) or 'X' not in data or set(data)-{'X','parameters'}:
            raise ValueError('JSON requires X and optional parameters')
        parameters = data.get('parameters', {})
        if not isinstance(parameters, dict):
            raise ValueError('parameters must be an object')
        model = estimator(**parameters).fit(data['X'])
        print(json.dumps(dict(labels=model.labels_.tolist()), allow_nan=False))
    except (ValueError, TypeError, ConvergenceError) as error:
        print('error: '+str(error), file=sys.stderr)
        raise SystemExit(2)
