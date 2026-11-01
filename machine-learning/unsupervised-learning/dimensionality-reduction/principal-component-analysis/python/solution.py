"""Centered PCA reusing the canonical Jacobi SVD; no automatic standardization."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_support_path = Path(__file__).resolve().parents[2]/'support.py'
_spec = importlib.util.spec_from_file_location('atlas_b5_support', _support_path)
support = sys.modules.get(_spec.name)
if support is None:
    support = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = support
    _spec.loader.exec_module(support)

class PCA(support.Projection):
    def __init__(self, n_components=2):
        self.n_components = n_components
        support.integer(n_components, 'n_components', 1, 32)

    @support.numerical
    def fit(self, X, y=None):
        support.integer(self.n_components, 'n_components', 1, 32)
        X = support.features(X, fitting=True)
        if len(X) < 2 or self.n_components > min(X.shape):
            raise ValueError('PCA needs n>=2 and components<=min(n,p)')
        A, mean = support.centered(X)
        # Centering can exceed the validated raw-feature magnitude bound.
        # Scale internally before reusing the public SVD, then restore units.
        centered_scale = support.uniform_scale(A)
        decomposition = support.load('singular-value-decomposition').SVD().fit(A/centered_scale)
        physical_scale = centered_scale*decomposition.scale_
        squares = decomposition.scaled_singular_values_**2
        total = squares.sum()
        ratios = squares/total if total else np.zeros_like(squares)
        k = self.n_components
        self.__dict__.update(n_features_in_=X.shape[1], mean_=mean,
            components_=decomposition.components_[:k].copy(),
            singular_values_=decomposition.singular_values_[:k]*centered_scale,
            explained_variance_=squares[:k]*physical_scale**2/(len(X)-1),
            explained_variance_ratio_=ratios[:k], total_variance_=total*physical_scale**2/(len(X)-1))
        return self

    @support.numerical
    def transform(self, X):
        return (self._query(X)-self.mean_)@self.components_.T

    @support.numerical
    def inverse_transform(self, Z):
        self._query(np.empty((0, getattr(self, 'n_features_in_', 1))))
        return support.latent_features(Z, len(self.components_))@self.components_+self.mean_

if __name__ == '__main__':
    support.main(PCA)
