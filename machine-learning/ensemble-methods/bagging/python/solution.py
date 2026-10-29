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

tree = s.module_at('atlas_ensemble_tree', s.ROOT/'tree.py')


class _Bagging:
    _soft = False

    def __init__(self, base_factory=None, *, n_estimators=10, max_samples=1.0,
                 max_depth=3, min_samples_leaf=1, random_state=0, oob_score=False):
        self.base_factory = base_factory
        self.n_estimators = s.integer(n_estimators, 'n_estimators', 1, 64)
        self.max_samples = max_samples
        self.max_depth = s.integer(max_depth, 'max_depth', 1, 8)
        self.min_samples_leaf = s.integer(min_samples_leaf, 'min_samples_leaf', 1, 256)
        self.random_state = s.seed(random_state)
        self.oob_score = s.boolean(oob_score, 'oob_score')

    @s.numerical
    def fit(self, X, y):
        X, encoded, classes, original = s.training(X, y, self._task)
        target = original if classes is not None else encoded
        total = s.integer(self.n_estimators, 'n_estimators', 1, 64)
        size = s.sample_count(self.max_samples, len(X))
        depth = s.integer(self.max_depth, 'max_depth', 1, 8)
        leaf = s.integer(self.min_samples_leaf, 'min_samples_leaf', 1, 256)
        oob = s.boolean(self.oob_score, 'oob_score')
        rng = np.random.default_rng(s.seed(self.random_state))
        factory = self.base_factory
        if factory is None:
            factory = lambda seed: tree.WeightedTree(task=self._task, max_depth=depth,
                min_samples_leaf=leaf, max_features=getattr(self, 'max_features', None), random_state=seed)
        models, samples, seeds = [], [], []
        accum = np.zeros((len(X), len(classes))) if classes is not None else np.zeros(len(X))
        counts = np.zeros(len(X), dtype=int)
        for _ in range(total):
            indices = rng.integers(len(X), size=size)
            seed = int(rng.integers(2**32))
            model = s.new_estimator(factory, seed)
            if any(model is previous for previous in models):
                raise ValueError('factories must create independent estimators')
            model.fit(X[indices].copy(), target[indices].copy())
            models.append(model);samples.append(indices.copy());seeds.append(seed)
            if oob:
                held = np.setdiff1d(np.arange(len(X)), indices)
                if len(held):
                    if classes is not None:
                        prediction = s.probability(model, X[held], classes) if self._soft else s.label_votes(model, X[held], classes)
                    else:
                        prediction = s.regression_prediction(model, X[held])
                    accum[held] += prediction;counts[held] += 1
        state = dict(estimators_=models, estimators_samples_=samples, estimator_seeds_=seeds,
                     n_features_in_=X.shape[1], oob_counts_=counts, oob_score_=None)
        if classes is not None:
            state['classes_'] = classes.copy()
        if oob:
            covered = counts > 0
            if classes is not None:
                result = np.full(accum.shape, np.nan)
                result[covered] = accum[covered]/counts[covered, None]
                state['oob_decision_function_'] = result
                if covered.any():
                    state['oob_score_'] = float(np.mean(classes[np.argmax(result[covered], axis=1)] == target[covered]))
            else:
                result = np.full(len(X), np.nan);result[covered] = accum[covered]/counts[covered]
                state['oob_prediction_'] = result
                if covered.any():
                    state['oob_score_'] = s.regression.r2(target[covered], result[covered])
        # Remove obsolete optional diagnostics on successful refit only.
        for name in ('oob_prediction_', 'oob_decision_function_'):
            self.__dict__.pop(name, None)
        self.__dict__.update(state)
        return self


class BaggingClassifier(_Bagging, s.Classifier):
    _task = 'classification'

    @s.numerical
    def predict_proba(self, X):
        X = self._check_X(X)
        result = np.zeros((len(X), len(self.classes_)))
        for model in self.estimators_:
            result += s.probability(model, X, self.classes_) if self._soft else s.label_votes(model, X, self.classes_)
        return result/len(self.estimators_)


class BaggingRegressor(_Bagging, s.Regressor):
    _task = 'regression'

    @s.numerical
    def predict(self, X):
        X = self._check_X(X)
        return s.finite(np.mean([s.regression_prediction(model, X) for model in self.estimators_], axis=0))


if __name__ == '__main__':
    s.main(BaggingClassifier)
