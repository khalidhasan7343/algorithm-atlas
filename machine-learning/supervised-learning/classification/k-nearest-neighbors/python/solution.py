"""Dense Euclidean KNN, stable neighbor selection and uniform class votes."""
import importlib.util
from pathlib import Path
import sys

import numpy as np

if "atlas_classification_support" not in sys.modules:
    _spec = importlib.util.spec_from_file_location("atlas_classification_support", Path(__file__).resolve().parents[2]/"support.py")
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = _module
    _spec.loader.exec_module(_module)
_support = sys.modules["atlas_classification_support"]


class KNearestNeighbors(_support.Classifier):
    def __init__(self, n_neighbors=5):
        self.n_neighbors = _support.integer(n_neighbors, "n_neighbors", 1, 2048)

    @_support.numerical
    def fit(self, X, y):
        k = _support.integer(self.n_neighbors, "n_neighbors", 1, 2048)
        X, _, classes, encoded = _support.training(X, y)
        if k > len(X):
            raise ValueError("n_neighbors cannot exceed training rows")
        self.__dict__.update(classes_=classes.copy(), n_features_in_=X.shape[1], _X_fit_=X.copy(),
                             _encoded_y_=encoded.copy(), n_neighbors_=k, converged_=True)
        return self

    @_support.numerical
    def kneighbors(self, X):
        X = self._check_X(X)
        n, p = self._X_fit_.shape
        if len(X)*self.n_neighbors_ > _support.MAX_CELLS:
            raise ValueError("query neighbor output exceeds cell budget")
        block = max(1, _support.MAX_CELLS//(n*p))
        indices = np.empty((len(X), self.n_neighbors_), dtype=int)
        distances = np.empty_like(indices, dtype=float)
        for start in range(0, len(X), block):
            differences = X[start:start+block, None, :]-self._X_fit_[None, :, :]
            squared = np.sum(differences*differences, axis=2)
            order = np.argsort(squared, axis=1, kind="stable")[:, :self.n_neighbors_]
            indices[start:start+block] = order
            distances[start:start+block] = np.sqrt(np.take_along_axis(squared, order, axis=1))
        return distances, indices

    def predict_proba(self, X):
        _, indices = self.kneighbors(X)
        result = np.zeros((len(indices), len(self.classes_)))
        for i, neighbors in enumerate(indices):
            result[i] = np.bincount(self._encoded_y_[neighbors], minlength=len(self.classes_))/self.n_neighbors_
        return result

    def predict(self, X):
        probabilities = self.predict_proba(X)
        return self.classes_[np.argmax(probabilities, axis=1)]


if __name__ == "__main__":
    _support.main(KNearestNeighbors)
