"""Shared bounded weighted tree primitive for B3; split-level RNG is explicit.

This is infrastructure for ensembles, not a second canonical CART lesson.
"""
from dataclasses import dataclass
import importlib.util
from pathlib import Path
import sys

import numpy as np

if 'atlas_ensemble_support' not in sys.modules:
    spec = importlib.util.spec_from_file_location('atlas_ensemble_support', Path(__file__).with_name('support.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
s = sys.modules['atlas_ensemble_support']


@dataclass(frozen=True)
class Node:
    value: object
    feature: int | None = None
    threshold: float | None = None
    left: 'Node | None' = None
    right: 'Node | None' = None
    candidates: tuple = ()


class WeightedTree:
    def __init__(self, *, task='regression', max_depth=3, min_samples_leaf=1,
                 max_features=None, random_state=0):
        if task not in ('classification', 'regression'):
            raise ValueError('task must be classification or regression')
        self.task = task
        self.max_depth = s.integer(max_depth, 'max_depth', 1, 8)
        self.min_samples_leaf = s.integer(min_samples_leaf, 'min_samples_leaf', 1, 256)
        self.max_features = max_features
        self.random_state = s.seed(random_state)

    @s.numerical
    def fit(self, X, y, sample_weight=None):
        if self.task not in ('classification', 'regression'):
            raise ValueError('task must be classification or regression')
        if self.task == 'classification':
            X, y, classes, _ = s.training(X, y, self.task)
        else:
            # Public ensembles validate observed y at 1e12. Their derived
            # residuals can exceed that cap: preserve them in this internal
            # primitive, with a separate finite 1e15 numerical bound.
            X = s.features(X, fitting=True)
            target = np.asarray(y)
            if target.shape != (len(X),) or target.dtype.kind not in 'iuf':
                raise ValueError('tree targets must be a real vector matching X')
            y = np.array(target, dtype=float, copy=True)
            if not np.isfinite(y).all() or np.any(np.abs(y) > 1e15):
                raise ValueError('internal tree targets must be finite with magnitude<=1e15')
            classes = None
        depth = s.integer(self.max_depth, 'max_depth', 1, 8)
        leaf = s.integer(self.min_samples_leaf, 'min_samples_leaf', 1, 256)
        count = s.feature_count(self.max_features, X.shape[1])
        rng = np.random.default_rng(s.seed(self.random_state))
        w = s.weights(sample_weight, len(X))
        k = 0 if classes is None else len(classes)

        def build(indices, level):
            target, weight = y[indices], w[indices]
            if self.task == 'classification':
                value = np.bincount(target, weights=weight, minlength=k)
                value /= value.sum()
                centered = None
                def error(mask):
                    mass = np.bincount(target[mask], weights=weight[mask], minlength=k)
                    return float(mass.sum()-mass @ mass/mass.sum())
            else:
                value = float(target[0]) if np.all(target == target[0]) else float(target[0]+(weight @ (target-target[0]))/weight.sum())
                centered = target-value
                scale = float(np.max(np.abs(centered)))
                normalized = centered/scale if scale else np.zeros_like(centered)
                def error(mask):
                    weights = weight[mask];t = normalized[mask]
                    mean = float(weights @ t/weights.sum())
                    return float(weights @ ((t-mean)**2))
            if level == depth or len(indices) < 2*leaf or np.all(target == target[0]):
                return Node(value)
            candidates = tuple(sorted(rng.choice(X.shape[1], count, replace=False).tolist())) if count < X.shape[1] else tuple(range(count))
            best = None
            parent = error(np.ones(len(indices), dtype=bool))
            for feature in candidates:
                values = np.unique(X[indices, feature])
                for lower, upper in zip(values[:-1], values[1:]):
                    threshold = float(lower+(upper-lower)/2)
                    if threshold >= upper:
                        threshold = float(lower)
                    mask = X[indices, feature] <= threshold
                    if mask.sum() < leaf or (~mask).sum() < leaf:
                        continue
                    child_error = error(mask)+error(~mask)
                    gain = parent-child_error
                    tolerance = 32*np.finfo(float).eps*max(abs(parent), np.finfo(float).tiny)
                    if gain > tolerance and (best is None or gain > best[0]+tolerance):
                        best = gain, feature, threshold, mask
            if best is None:
                return Node(value, candidates=candidates)
            _, feature, threshold, mask = best
            return Node(value, feature, threshold, build(indices[mask], level+1), build(indices[~mask], level+1), candidates)

        root = build(np.flatnonzero(w > 0), 0)
        state = dict(tree_=root, n_features_in_=X.shape[1])
        if classes is not None:
            state['classes_'] = classes.copy()
        self.__dict__.update(state)
        return self

    def _nodes(self, X):
        if not hasattr(self, 'tree_'):
            raise ValueError('fit must succeed before prediction')
        X = s.features(X, expected=self.n_features_in_)
        result = []
        for row in X:
            node = self.tree_
            while node.feature is not None:
                node = node.left if row[node.feature] <= node.threshold else node.right
            result.append(node.value)
        return result

    def predict(self, X):
        values = self._nodes(X)
        if self.task == 'classification':
            return self.classes_[np.argmax(np.asarray(values).reshape(-1, len(self.classes_)), axis=1)]
        return np.asarray(values, dtype=float)

    def predict_proba(self, X):
        if self.task != 'classification':
            raise ValueError('probabilities apply only to classification')
        return np.asarray(self._nodes(X), dtype=float).reshape(-1, len(self.classes_))
