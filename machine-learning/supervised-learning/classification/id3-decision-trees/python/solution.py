"""Categorical multiway ID3, Shannon information gain and majority fallback."""
from dataclasses import dataclass
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

def entropy(counts):
    counts = np.asarray(counts, dtype=float)
    if counts.ndim != 1 or np.any(counts < 0) or (not np.isfinite(counts).all()):
        raise ValueError('finite nonnegative count vector required')
    total = float(counts.sum())
    if total == 0:
        return 0.0
    probability = counts[counts > 0] / total
    return float(-np.sum(probability * np.log2(probability)))

@dataclass(frozen=True)
class Node:
    distribution: tuple
    n_samples: int
    entropy: float
    feature: int | None = None
    branches: tuple = ()
    gain: float = 0.0

class ID3Classifier(_support.Classifier):

    def __init__(self, *, max_depth=5, min_samples_leaf=1, min_gain=0.0):
        self.max_depth = _support.integer(max_depth, 'max_depth', 1, 16)
        self.min_samples_leaf = _support.integer(min_samples_leaf, 'min_samples_leaf', 1, 256)
        self.min_gain = _support.scalar(min_gain, 'min_gain', high=5)

    @_support.numerical
    def fit(self, X, y):
        depth_limit = _support.integer(self.max_depth, 'max_depth', 1, 16)
        leaf_size = _support.integer(self.min_samples_leaf, 'min_samples_leaf', 1, 256)
        minimum = _support.scalar(self.min_gain, 'min_gain', high=5)
        X, _, classes, encoded = _support.training(X, y, max_samples=512, max_features=32)
        _support.categorical_columns(X, range(X.shape[1]), fitting=True)
        leaves = 0
        actual_depth = 0
        c = len(classes)

        def build(indices, available, depth):
            nonlocal leaves, actual_depth
            actual_depth = max(actual_depth, depth)
            counts = np.bincount(encoded[indices], minlength=c)
            distribution = tuple(counts / len(indices))
            uncertainty = entropy(counts)
            if depth >= depth_limit or uncertainty == 0 or (not available) or (len(indices) < 2 * leaf_size):
                leaves += 1
                return Node(distribution, len(indices), uncertainty)
            best = None
            for feature in available:
                values = np.unique(X[indices, feature])
                if len(values) < 2:
                    continue
                groups = tuple(((float(v), indices[X[indices, feature] == v]) for v in values))
                if any((len(rows) < leaf_size for _, rows in groups)):
                    continue
                remainder = sum((len(rows) * entropy(np.bincount(encoded[rows], minlength=c)) for _, rows in groups)) / len(indices)
                gain = max(0.0, uncertainty - remainder)
                if best is None or gain > best[0] + 1e-14:
                    best = (gain, feature, groups)
            if best is None or best[0] < minimum:
                leaves += 1
                return Node(distribution, len(indices), uncertainty)
            gain, feature, groups = best
            remaining = tuple((j for j in available if j != feature))
            branches = tuple(((value, build(rows, remaining, depth + 1)) for value, rows in groups))
            return Node(distribution, len(indices), uncertainty, feature, branches, gain)
        tree = build(np.arange(len(X)), tuple(range(X.shape[1])), 0)
        self.__dict__.update(classes_=classes.copy(), n_features_in_=X.shape[1], tree_=tree, depth_=actual_depth, n_leaves_=leaves, converged_=True)
        return self

    def predict_proba(self, X):
        X = self._check_X(X)
        _support.categorical_columns(X, range(X.shape[1]))
        result = np.empty((len(X), len(self.classes_)))
        for i, row in enumerate(X):
            node = self.tree_
            while node.feature is not None:
                child = next((child for value, child in node.branches if value == row[node.feature]), None)
                if child is None:
                    break
                node = child
            result[i] = node.distribution
        return result

    def predict(self, X):
        probability = self.predict_proba(X)
        return self.classes_[np.argmax(probability, axis=1)]
if __name__ == '__main__':
    _support.main(ID3Classifier)
