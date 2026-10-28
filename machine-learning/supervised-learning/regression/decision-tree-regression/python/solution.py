"""Deterministic squared-error CART regression with explicit mean-leaf nodes."""
from dataclasses import dataclass
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("atlas_regression_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)


@dataclass(frozen=True)
class Node:
    value: float
    n_samples: int
    squared_error: float
    feature: int | None = None
    threshold: float | None = None
    left: "Node | None" = None
    right: "Node | None" = None


class DecisionTreeRegression(_support.LinearPredictor):
    def __init__(self, *, max_depth=5, min_samples_leaf=1, min_impurity_decrease=0.0):
        self.max_depth = _support.integer(max_depth, "max_depth", 1, 32)
        self.min_samples_leaf = _support.integer(min_samples_leaf, "min_samples_leaf", 1, 1024)
        self.min_impurity_decrease = _support.scalar(min_impurity_decrease, "min_impurity_decrease")

    @_support.numerical
    def fit(self, X, y):
        depth_limit = _support.integer(self.max_depth, "max_depth", 1, 32)
        leaf_size = _support.integer(self.min_samples_leaf, "min_samples_leaf", 1, 1024)
        minimum_gain = _support.scalar(self.min_impurity_decrease, "min_impurity_decrease")
        X = _support.features(X, fitting=True, max_features=32)
        y = _support.targets(y, len(X))
        n_total = len(y)
        leaves, actual_depth = 0, 0

        def best_split(indices, parent_error, normalized_targets):
            best = None
            tolerance = 32*np.finfo(float).eps*max(parent_error, np.finfo(float).tiny)
            for feature in range(X.shape[1]):
                positions = np.argsort(X[indices, feature], kind="mergesort")
                order = indices[positions]
                values = X[order, feature]
                centered_y = normalized_targets[positions]
                sums = np.cumsum(centered_y)
                squares = np.cumsum(centered_y*centered_y)
                for left_count in range(leaf_size, len(order) - leaf_size + 1):
                    if values[left_count-1] == values[left_count]:
                        continue
                    right_count = len(order) - left_count
                    left_sum, right_sum = sums[left_count-1], sums[-1] - sums[left_count-1]
                    left_error = max(0.0, float(squares[left_count-1] - left_sum*left_sum/left_count))
                    right_error = max(0.0, float(squares[-1] - squares[left_count-1] - right_sum*right_sum/right_count))
                    error = left_error + right_error
                    if best is None or error < best[0] - tolerance:
                        lower, upper = values[left_count-1], values[left_count]
                        threshold = float(lower + (upper-lower)/2)
                        if threshold >= upper:
                            threshold = float(lower)
                        best = error, feature, threshold
            return best

        def build(indices, depth):
            nonlocal leaves, actual_depth
            actual_depth = max(actual_depth, depth)
            targets = y[indices]
            pure = bool(np.all(targets == targets[0]))
            value = float(targets[0]) if pure else float(targets.mean())
            if pure:
                leaves += 1
                return Node(value, len(indices), 0.0)
            centered = targets - value
            scale = float(np.max(np.abs(centered)))
            with np.errstate(under="ignore"):
                normalized = centered / scale
                normalized_error = float(normalized @ normalized)
                # Diagnostic SSE can underflow in original squared units; it
                # never determines purity or split selection.
                error = float(np.square(scale * np.sqrt(normalized_error)))
            if depth >= depth_limit or len(indices) < 2*leaf_size:
                leaves += 1
                return Node(value, len(indices), error)
            split = best_split(indices, normalized_error, normalized)
            with np.errstate(under="ignore"):
                root_gain = (scale * np.sqrt(max(0.0, normalized_error-split[0])/n_total)
                             if split is not None else 0.0)
            # Comparing square roots preserves the original target-squared
            # minimum-gain units without forming scale**2 prematurely.
            if split is None or root_gain < np.sqrt(minimum_gain):
                leaves += 1
                return Node(value, len(indices), error)
            _, feature, threshold = split
            left_mask = X[indices, feature] <= threshold
            left, right = indices[left_mask], indices[~left_mask]
            return Node(value, len(indices), error, feature, threshold, build(left, depth+1), build(right, depth+1))

        root = build(np.arange(len(y)), 0)
        prediction = self._predict_tree(X, root)
        self.__dict__.update(tree_=root, n_features_in_=X.shape[1], depth_=actual_depth,
                             n_leaves_=leaves, training_mse_=_support.mse(y, prediction), converged_=True)
        return self

    @staticmethod
    def _predict_tree(X, root):
        prediction = np.empty(len(X))
        for i, row in enumerate(X):
            node = root
            while node.feature is not None:
                node = node.left if row[node.feature] <= node.threshold else node.right
            prediction[i] = node.value
        return prediction

    @_support.numerical
    def predict(self, X):
        if not hasattr(self, "tree_"):
            raise ValueError("fit must succeed before prediction")
        X = _support.features(X, expected=self.n_features_in_, max_features=32)
        return self._predict_tree(X, self.tree_)


if __name__ == "__main__":
    _support.main(DecisionTreeRegression)
