"""Supervised Fisher projection, distinct from the canonical B2 classifier."""
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

class LDAProjection(support.Projection):
    def __init__(self, n_components=1, reg=0.0):
        self.n_components, self.reg = n_components, reg
        self._parameters()

    def _parameters(self):
        support.integer(self.n_components, 'n_components', 1, 32)
        support.scalar(self.reg, 'reg', 0, 1)

    @support.numerical
    def fit(self, X, y=None):
        self._parameters()
        X = support.features(X, fitting=True)
        _, classes, labels = support.encode_labels(y, n=len(X))
        n, p = X.shape; count = len(classes)
        if count < 2 or self.n_components > min(p, count-1):
            raise ValueError('LDA needs >=2 classes; components<=min(p, classes-1)')
        A, mean = support.centered(X); scale = support.uniform_scale(A); A /= scale
        Sw, Sb = np.zeros((p,p)), np.zeros((p,p))
        means, counts = [], []
        for j in range(count):
            group = A[labels==j]; mu = group.mean(axis=0); residual = group-mu
            Sw += residual.T@residual
            Sb += len(group)*np.outer(mu, mu)
            means.append(mu*scale+mean); counts.append(len(group))
        regularized = Sw+self.reg*np.eye(p)
        values, basis = np.linalg.eigh(regularized)
        if values[0] <= max(values[-1], 1e-300)*1e-12:
            raise ValueError('within-class scatter unresolved; rescale or set positive reg')
        whitening = (basis/np.sqrt(values))@basis.T
        C = whitening@Sb@whitening
        eigenvalues, directions = np.linalg.eigh((C+C.T)/2)
        order = np.argsort(-eigenvalues, kind='stable')[:self.n_components]
        components = (whitening@directions[:, order]).T
        components /= np.linalg.norm(components, axis=1)[:, None]
        for row in components:
            if row[np.argmax(abs(row))] < 0:row *= -1
        self.__dict__.update(n_features_in_=p, mean_=mean, classes_=classes.copy(),
            class_means_=np.array(means), class_counts_=np.array(counts), components_=components,
            eigenvalues_=np.maximum(eigenvalues[order],0),
            within_scatter_=Sw*scale**2, between_scatter_=Sb*scale**2,
            normalized_within_scatter_=Sw, normalized_between_scatter_=Sb, scale_=scale,
            regularized_within_scatter_=regularized)
        return self

    @support.numerical
    def transform(self, X):
        return (self._query(X)-self.mean_)@self.components_.T

if __name__ == '__main__':support.main(LDAProjection)
