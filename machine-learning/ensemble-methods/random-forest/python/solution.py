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

bagging = s.load('bagging')


class _Forest:
    def __init__(self, *, n_estimators=10, max_features='sqrt', max_samples=1.0,
                 max_depth=4, min_samples_leaf=1, random_state=0, oob_score=False):
        super().__init__(n_estimators=n_estimators, max_samples=max_samples,
                         max_depth=max_depth, min_samples_leaf=min_samples_leaf,
                         random_state=random_state, oob_score=oob_score)
        self.max_features = max_features

    def fit(self, X, y):
        checked = s.features(X, fitting=True)
        s.feature_count(self.max_features, checked.shape[1])
        return super().fit(checked, y)


class RandomForestClassifier(_Forest, bagging.BaggingClassifier):
    """Bootstrap trees; random feature subset at EACH node; mean leaf probabilities."""
    _soft = True


class RandomForestRegressor(_Forest, bagging.BaggingRegressor):
    """Bootstrap squared-error trees with per-node random features and mean outputs."""


if __name__ == '__main__':
    s.main(RandomForestClassifier)
