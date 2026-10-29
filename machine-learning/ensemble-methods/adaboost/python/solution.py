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


class AdaBoostClassifier(s.Classifier):
    """Discrete multiclass SAMME; alpha=eta*(log((1-e)/e)+log(K-1))."""
    def __init__(self, *, n_estimators=20, learning_rate=1.0, max_depth=1, random_state=0):
        self.n_estimators = s.integer(n_estimators, 'n_estimators', 1, 64)
        self.learning_rate = s.scalar(learning_rate, 'learning_rate', high=1, positive=True)
        self.max_depth = s.integer(max_depth, 'max_depth', 1, 4)
        self.random_state = s.seed(random_state)

    @s.numerical
    def fit(self, X, y, sample_weight=None):
        X, encoded, classes, original = s.training(X, y, 'classification')
        if len(classes) < 2:
            raise ValueError('SAMME requires at least two classes')
        total = s.integer(self.n_estimators, 'n_estimators', 1, 64)
        rate = s.scalar(self.learning_rate, 'learning_rate', high=1, positive=True)
        depth = s.integer(self.max_depth, 'max_depth', 1, 4)
        rng = np.random.default_rng(s.seed(self.random_state))
        weight = s.weights(sample_weight, len(X))
        log_weight = np.full(len(X), -np.inf)
        positive = weight > 0;log_weight[positive] = np.log(weight[positive])
        models, alphas, errors, histories = [], [], [], []
        stop = 'estimator limit reached'
        for _ in range(total):
            weight = np.exp(log_weight-log_weight.max());weight /= weight.sum()
            model = tree.WeightedTree(task='classification', max_depth=depth, random_state=int(rng.integers(2**32))).fit(X, original, weight)
            wrong = model.predict(X) != original
            error = float(weight @ wrong)
            if error >= 1-1/len(classes)-1e-14:
                stop = 'weak learner at or worse than chance'
                if not models:
                    raise ValueError(stop)
                break
            histories.append(weight.copy());models.append(model);errors.append(error)
            if error == 0:
                alphas.append(1.0);stop = 'perfect weak learner';break
            alpha = rate*(np.log1p(-error)-np.log(error)+np.log(len(classes)-1))
            alphas.append(float(alpha))
            log_weight[wrong] += alpha
            # Subtracting a common offset preserves normalized weight ratios.
            log_weight -= log_weight.max()
        self.__dict__.update(classes_=classes.copy(), n_features_in_=X.shape[1], estimators_=models,
                             estimator_weights_=np.array(alphas), estimator_errors_=np.array(errors),
                             sample_weight_history_=histories, stop_reason_=stop)
        return self

    def staged_predict(self, X):
        X = self._check_X(X)
        votes = np.zeros((len(X), len(self.classes_)))
        for alpha, model in zip(self.estimator_weights_, self.estimators_):
            votes += alpha*s.label_votes(model, X, self.classes_)
            yield self.classes_[np.argmax(votes, axis=1)].copy()

    @s.numerical
    def predict_proba(self, X):
        X = self._check_X(X)
        # SAMME score transform; these are uncalibrated model probabilities.
        votes = np.zeros((len(X), len(self.classes_)))
        for alpha, model in zip(self.estimator_weights_, self.estimators_):
            votes += alpha*s.label_votes(model, X, self.classes_)
        scores = votes/self.estimator_weights_.sum()/(len(self.classes_)-1)
        return s.classification.normalize_log_scores(scores)


if __name__ == '__main__':
    s.main(AdaBoostClassifier)
