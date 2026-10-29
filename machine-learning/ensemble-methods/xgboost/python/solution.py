import importlib.util
from pathlib import Path
import sys

import numpy as np

if 'atlas_ensemble_support' not in sys.modules:
    _spec = importlib.util.spec_from_file_location('atlas_ensemble_support', Path(__file__).resolve().parents[2]/'support.py')
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = _module
    _spec.loader.exec_module(_module)
s = sys.modules['atlas_ensemble_support']

from dataclasses import dataclass


@dataclass(frozen=True)
class NewtonNode:
    value: float
    gradient_sum: float
    hessian_sum: float
    gain: float = 0.0
    feature: int | None = None
    threshold: float | None = None
    left: 'NewtonNode | None' = None
    right: 'NewtonNode | None' = None


def _predict(root, X):
    result = np.empty(len(X))
    for i, row in enumerate(X):
        node = root
        while node.feature is not None:
            node = node.left if row[node.feature] <= node.threshold else node.right
        result[i] = node.value
    return result


class XGBoostRegressor(s.Regressor):
    """Dense exact greedy Newton boosting, half-squared loss and L2/gamma trees.

    No library wrapper, sparse/default routing, histograms, L1, GPU or DART.
    """
    def __init__(self, *, n_estimators=20, learning_rate=.1, max_depth=2,
                 reg_lambda=1.0, gamma=0.0, min_child_weight=1.0,
                 subsample=1.0, colsample_bytree=1.0, random_state=0):
        self.n_estimators = s.integer(n_estimators, 'n_estimators', 1, 64)
        self.learning_rate = s.scalar(learning_rate, 'learning_rate', high=1, positive=True)
        self.max_depth = s.integer(max_depth, 'max_depth', 1, 6)
        self.reg_lambda = s.scalar(reg_lambda, 'reg_lambda')
        self.gamma = s.scalar(gamma, 'gamma')
        self.min_child_weight = s.scalar(min_child_weight, 'min_child_weight', high=512)
        self.subsample = s.scalar(subsample, 'subsample', high=1, positive=True)
        self.colsample_bytree = s.scalar(colsample_bytree, 'colsample_bytree', high=1, positive=True)
        self.random_state = s.seed(random_state)

    @s.numerical
    def fit(self, X, y):
        X, y, _, _ = s.training(X, y, 'regression')
        total = s.integer(self.n_estimators, 'n_estimators', 1, 64)
        rate = s.scalar(self.learning_rate, 'learning_rate', high=1, positive=True)
        depth = s.integer(self.max_depth, 'max_depth', 1, 6)
        penalty = s.scalar(self.reg_lambda, 'reg_lambda');gamma = s.scalar(self.gamma, 'gamma')
        minimum = s.scalar(self.min_child_weight, 'min_child_weight', high=512)
        rows = s.scalar(self.subsample, 'subsample', high=1, positive=True)
        columns = s.scalar(self.colsample_bytree, 'colsample_bytree', high=1, positive=True)
        rng = np.random.default_rng(s.seed(self.random_state))
        initial = float(y[0]) if np.all(y == y[0]) else float(y.mean())
        prediction = np.full(len(X), initial)
        models, samples, features, gradients = [], [], [], []
        losses = [s.regression.mse(y, prediction)]
        for _ in range(total):
            g = prediction-y;h = np.ones(len(X))
            if np.all(g == 0):
                break
            selected = np.sort(rng.choice(len(X), max(1, int(np.ceil(rows*len(X)))), replace=False))
            chosen = tuple(sorted(rng.choice(X.shape[1], max(1, int(np.ceil(columns*X.shape[1]))), replace=False).tolist()))

            def build(indices, level):
                G, H = float(g[indices].sum()), float(h[indices].sum())
                value = -G/(H+penalty)
                parent = G*G/(H+penalty)
                best = None
                if level < depth:
                    for feature in chosen:
                        values = np.unique(X[indices, feature])
                        for lower, upper in zip(values[:-1], values[1:]):
                            threshold = float(lower+(upper-lower)/2)
                            if threshold >= upper:threshold = float(lower)
                            mask = X[indices, feature] <= threshold
                            left, right = indices[mask], indices[~mask]
                            GL, HL = float(g[left].sum()), float(h[left].sum())
                            GR, HR = float(g[right].sum()), float(h[right].sum())
                            if HL < minimum or HR < minimum:continue
                            gain = .5*(GL*GL/(HL+penalty)+GR*GR/(HR+penalty)-parent)-gamma
                            tolerance = 32*np.finfo(float).eps*max(abs(parent), np.finfo(float).tiny)
                            if gain > tolerance and (best is None or gain > best[0]+tolerance):
                                best = gain, feature, threshold, left, right
                if best is None:return NewtonNode(value, G, H)
                gain, feature, threshold, left, right = best
                return NewtonNode(value, G, H, gain, feature, threshold, build(left,level+1),build(right,level+1))

            root = build(selected, 0)
            prediction += rate*_predict(root, X)
            s.finite(prediction)
            models.append(root);samples.append(selected);features.append(chosen);gradients.append(g.copy())
            losses.append(s.regression.mse(y, prediction))
        self.__dict__.update(n_features_in_=X.shape[1], init_=initial, estimators_=models,
                             learning_rate_=rate, estimators_samples_=samples, estimators_features_=features,
                             gradient_history_=gradients, train_loss_=np.array(losses))
        return self

    def staged_predict(self, X):
        X = self._check_X(X);prediction = np.full(len(X), self.init_)
        for root in self.estimators_:
            prediction += self.learning_rate_*_predict(root, X)
            yield s.finite(prediction.copy())

    @s.numerical
    def predict(self, X):
        X = self._check_X(X);prediction = np.full(len(X), self.init_)
        for root in self.estimators_:
            prediction += self.learning_rate_*_predict(root, X)
        return s.finite(prediction)


if __name__ == '__main__':
    s.main(XGBoostRegressor)
