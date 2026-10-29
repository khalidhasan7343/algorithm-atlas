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


class GradientBoostingRegressor(s.Regressor):
    """Squared-error additive model, mean initialization and residual trees."""
    def __init__(self, *, n_estimators=20, learning_rate=.1, max_depth=2,
                 min_samples_leaf=1, random_state=0):
        self.n_estimators = s.integer(n_estimators, 'n_estimators', 1, 64)
        self.learning_rate = s.scalar(learning_rate, 'learning_rate', high=1, positive=True)
        self.max_depth = s.integer(max_depth, 'max_depth', 1, 8)
        self.min_samples_leaf = s.integer(min_samples_leaf, 'min_samples_leaf', 1, 256)
        self.random_state = s.seed(random_state)

    @s.numerical
    def fit(self, X, y):
        X, y, _, _ = s.training(X, y, 'regression')
        total = s.integer(self.n_estimators, 'n_estimators', 1, 64)
        rate = s.scalar(self.learning_rate, 'learning_rate', high=1, positive=True)
        depth = s.integer(self.max_depth, 'max_depth', 1, 8)
        leaf = s.integer(self.min_samples_leaf, 'min_samples_leaf', 1, 256)
        rng = np.random.default_rng(s.seed(self.random_state))
        initial = float(y[0]) if np.all(y == y[0]) else float(y.mean())
        prediction = np.full(len(X), initial)
        models, losses, residuals = [], [s.regression.mse(y, prediction)], []
        for _ in range(total):
            residual = s.finite(y-prediction)
            if np.all(residual == 0):
                break
            model = tree.WeightedTree(max_depth=depth, min_samples_leaf=leaf, random_state=int(rng.integers(2**32))).fit(X, residual)
            prediction += rate*model.predict(X)
            s.finite(prediction)
            models.append(model);residuals.append(residual.copy());losses.append(s.regression.mse(y, prediction))
        self.__dict__.update(n_features_in_=X.shape[1], init_=initial, estimators_=models,
                             learning_rate_=rate, train_loss_=np.array(losses), residual_history_=residuals)
        return self

    def staged_predict(self, X):
        X = self._check_X(X)
        prediction = np.full(len(X), self.init_)
        for model in self.estimators_:
            prediction += self.learning_rate_*model.predict(X)
            yield s.finite(prediction.copy())

    @s.numerical
    def predict(self, X):
        X = self._check_X(X)
        prediction = np.full(len(X), self.init_)
        for model in self.estimators_:
            prediction += self.learning_rate_*model.predict(X)
        return s.finite(prediction)


if __name__ == '__main__':
    s.main(GradientBoostingRegressor)
