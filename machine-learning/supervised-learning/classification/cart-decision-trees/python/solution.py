"""Greedy classification CART with Gini splits and class-frequency leaves."""
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

@dataclass(frozen=True)
class Node:
    distribution: tuple
    n_samples: int
    impurity: float
    feature: int | None = None
    threshold: float | None = None
    left: 'Node|None' = None
    right: 'Node|None' = None

def gini(counts):
    counts = np.asarray(counts, dtype=float)
    if counts.ndim != 1 or np.any(counts < 0) or (not np.isfinite(counts).all()):
        raise ValueError('finite nonnegative count vector required')
    total = float(counts.sum())
    return 0.0 if total == 0 else max(0.0, 1 - float(counts / total @ (counts / total)))

class CARTClassifier(_support.Classifier):

    def __init__(self, *, max_depth=5, min_samples_leaf=1, min_impurity_decrease=0.0):
        self.max_depth = _support.integer(max_depth, 'max_depth', 1, 16)
        self.min_samples_leaf = _support.integer(min_samples_leaf, 'min_samples_leaf', 1, 1024)
        self.min_impurity_decrease = _support.scalar(min_impurity_decrease, 'min_impurity_decrease', high=1)

    @_support.numerical
    def fit(self, X, y):
        depth_limit = _support.integer(self.max_depth, 'max_depth', 1, 16)
        leaf_size = _support.integer(self.min_samples_leaf, 'min_samples_leaf', 1, 1024)
        minimum = _support.scalar(self.min_impurity_decrease, 'min_impurity_decrease', high=1)
        X, _, classes, encoded = _support.training(X, y, max_features=32)
        leaves = 0
        actual_depth = 0
        total = len(X)
        c = len(classes)

        def build(indices, depth):
            nonlocal leaves, actual_depth
            actual_depth = max(actual_depth, depth)
            counts = np.bincount(encoded[indices], minlength=c).astype(float)
            distribution = tuple(counts / len(indices))
            impurity = gini(counts)
            if depth >= depth_limit or impurity == 0 or len(indices) < 2 * leaf_size:
                leaves += 1
                return Node(distribution, len(indices), impurity)
            best = None
            for feature in range(X.shape[1]):
                order = indices[np.argsort(X[indices, feature], kind='stable')]
                values = X[order, feature]
                left = np.zeros(c)
                for cut in range(1, len(order)):
                    left[encoded[order[cut - 1]]] += 1
                    if cut < leaf_size or len(order) - cut < leaf_size or values[cut - 1] == values[cut]:
                        continue
                    right = counts - left
                    score = (cut * gini(left) + (len(order) - cut) * gini(right)) / len(order)
                    if best is None or score < best[0] - 1e-14:
                        threshold = float(values[cut - 1] + (values[cut] - values[cut - 1]) / 2)
                        if threshold >= values[cut]:
                            threshold = float(values[cut - 1])
                        best = (score, feature, threshold)
            if best is None or len(indices) / total * max(0.0, impurity - best[0]) < minimum:
                leaves += 1
                return Node(distribution, len(indices), impurity)
            _, feature, threshold = best
            mask = X[indices, feature] <= threshold
            return Node(distribution, len(indices), impurity, feature, threshold, build(indices[mask], depth + 1), build(indices[~mask], depth + 1))
        tree = build(np.arange(total), 0)
        self.__dict__.update(classes_=classes.copy(), n_features_in_=X.shape[1], tree_=tree, depth_=actual_depth, n_leaves_=leaves, converged_=True)
        return self

    def predict_proba(self, X):
        X = self._check_X(X)
        result = np.empty((len(X), len(self.classes_)))
        for i, row in enumerate(X):
            node = self.tree_
            while node.feature is not None:
                node = node.left if row[node.feature] <= node.threshold else node.right
            result[i] = node.distribution
        return result

    def predict(self, X):
        probability = self.predict_proba(X)
        return self.classes_[np.argmax(probability, axis=1)]
if __name__ == '__main__':
    _support.main(CARTClassifier)
