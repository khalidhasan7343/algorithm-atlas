"""C4.5-style mixed-feature gain-ratio tree; no pruning or missing-value routing.

Continuous thresholds maximize information gain, with an optional MDL charge.
Feature selection uses an average-positive-gain filter before gain-ratio choice.
"""
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
entropy = _support.load('id3-decision-trees').entropy

def _columns(value, p):
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)) or any((type(j) is not int or not 0 <= j < p for j in value)) or len(set(value)) != len(value):
        raise ValueError('categorical_features must be distinct native integer column indices')
    return tuple(sorted(value))

@dataclass(frozen=True)
class Node:
    distribution: tuple
    n_samples: int
    entropy: float
    feature: int | None = None
    categorical: bool = False
    threshold: float | None = None
    values: tuple = ()
    children: tuple = ()
    gain: float = 0.0
    adjusted_gain: float = 0.0
    split_information: float = 0.0
    gain_ratio: float = 0.0

class C45Classifier(_support.Classifier):

    def __init__(self, *, categorical_features=None, max_depth=5, min_samples_leaf=1, min_gain=1e-12, mdl_correction=True):
        self.categorical_features = _columns(categorical_features, 32)
        self.max_depth = _support.integer(max_depth, 'max_depth', 1, 16)
        self.min_samples_leaf = _support.integer(min_samples_leaf, 'min_samples_leaf', 1, 256)
        self.min_gain = _support.scalar(min_gain, 'min_gain', high=5)
        self.mdl_correction = _support.boolean(mdl_correction, 'mdl_correction')

    @_support.numerical
    def fit(self, X, y):
        depth_limit = _support.integer(self.max_depth, 'max_depth', 1, 16)
        leaf_size = _support.integer(self.min_samples_leaf, 'min_samples_leaf', 1, 256)
        minimum = _support.scalar(self.min_gain, 'min_gain', high=5)
        mdl = _support.boolean(self.mdl_correction, 'mdl_correction')
        X, _, classes, encoded = _support.training(X, y, max_samples=512, max_features=32)
        categories = _columns(self.categorical_features, X.shape[1])
        _support.categorical_columns(X, categories, fitting=True)
        leaves = 0
        actual_depth = 0
        c = len(classes)

        def build(indices, used_categories, depth):
            nonlocal leaves, actual_depth
            actual_depth = max(actual_depth, depth)
            counts = np.bincount(encoded[indices], minlength=c).astype(float)
            distribution = tuple(counts / len(indices))
            uncertainty = entropy(counts)
            if depth >= depth_limit or uncertainty == 0 or len(indices) < 2 * leaf_size:
                leaves += 1
                return Node(distribution, len(indices), uncertainty)
            candidates = []
            for feature in range(X.shape[1]):
                if feature in used_categories:
                    continue
                unique = np.unique(X[indices, feature])
                if len(unique) < 2:
                    continue
                if feature in categories:
                    groups = tuple((indices[X[indices, feature] == v] for v in unique))
                    if any((len(rows) < leaf_size for rows in groups)):
                        continue
                    sizes = np.array([len(rows) for rows in groups])
                    gain = max(0.0, uncertainty - sum((len(rows) * entropy(np.bincount(encoded[rows], minlength=c)) for rows in groups)) / len(indices))
                    split = entropy(sizes)
                    candidates.append((gain, gain / split, feature, True, None, tuple((float(v) for v in unique)), gain, split))
                else:
                    order = indices[np.argsort(X[indices, feature], kind='stable')]
                    values = X[order, feature]
                    left = np.zeros(c)
                    best = None
                    for cut in range(1, len(order)):
                        left[encoded[order[cut - 1]]] += 1
                        if cut < leaf_size or len(order) - cut < leaf_size or values[cut - 1] == values[cut]:
                            continue
                        gain = max(0.0, uncertainty - (cut * entropy(left) + (len(order) - cut) * entropy(counts - left)) / len(order))
                        if best is None or gain > best[0] + 1e-14:
                            threshold = float(values[cut - 1] + (values[cut] - values[cut - 1]) / 2)
                            if threshold >= values[cut]:
                                threshold = float(values[cut - 1])
                            best = (gain, threshold, entropy([cut, len(order) - cut]))
                    if best is not None:
                        gain, threshold, split = best
                        adjusted = gain - (np.log2(len(unique) - 1) / len(indices) if mdl else 0.0)
                        candidates.append((adjusted, adjusted / split, feature, False, threshold, (), gain, split))
            positive = [v for v in candidates if v[0] > 1e-14]
            average = float(np.mean([v[0] for v in positive])) if positive else float('inf')
            eligible = [v for v in positive if v[0] >= minimum and v[0] >= average - 1e-14]
            if not eligible:
                leaves += 1
                return Node(distribution, len(indices), uncertainty)
            best = eligible[0]
            for candidate in eligible[1:]:
                if candidate[1] > best[1] + 1e-14:
                    best = candidate
            adjusted, ratio, feature, categorical, threshold, values, gain, split = best
            if categorical:
                children = tuple((build(indices[X[indices, feature] == v], used_categories | {feature}, depth + 1) for v in values))
            else:
                mask = X[indices, feature] <= threshold
                children = (build(indices[mask], used_categories, depth + 1), build(indices[~mask], used_categories, depth + 1))
            return Node(distribution, len(indices), uncertainty, feature, categorical, threshold, values, children, gain, adjusted, split, ratio)
        tree = build(np.arange(len(X)), frozenset(), 0)
        self.__dict__.update(classes_=classes.copy(), n_features_in_=X.shape[1], categorical_features_=categories, tree_=tree, depth_=actual_depth, n_leaves_=leaves, mdl_correction_=mdl, missing_values_='reject', pruning_='none', converged_=True)
        return self

    def predict_proba(self, X):
        X = self._check_X(X)
        _support.categorical_columns(X, self.categorical_features_)
        result = np.empty((len(X), len(self.classes_)))
        for i, row in enumerate(X):
            node = self.tree_
            while node.feature is not None:
                if node.categorical:
                    try:
                        index = node.values.index(float(row[node.feature]))
                    except ValueError:
                        break
                    node = node.children[index]
                else:
                    node = node.children[0 if row[node.feature] <= node.threshold else 1]
            result[i] = node.distribution
        return result

    def predict(self, X):
        probability = self.predict_proba(X)
        return self.classes_[np.argmax(probability, axis=1)]
if __name__ == '__main__':
    _support.main(C45Classifier)
