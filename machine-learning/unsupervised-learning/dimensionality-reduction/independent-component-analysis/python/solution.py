"""Parallel tanh FastICA with explicit centering, whitening and decorrelation."""
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

def decorrelate(W):
    values, vectors = np.linalg.eigh(W@W.T)
    if values[0] <= max(values[-1],1e-300)*1e-14:
        raise ValueError('ICA orthogonalization is numerically singular')
    return (vectors/np.sqrt(values))@vectors.T@W


class FastICA(support.Projection):
    def __init__(self, n_components=2, max_iter=1000, tol=1e-6, random_state=0):
        self.n_components, self.max_iter, self.tol = n_components, max_iter, tol
        self.random_state = random_state
        self._parameters()

    def _parameters(self):
        support.integer(self.n_components,'n_components',1,32)
        support.integer(self.max_iter,'max_iter',1,5000)
        support.scalar(self.tol,'tol',1e-12,1e-2)
        support.integer(self.random_state,'random_state',0,2**32-1)

    @support.numerical
    def fit(self, X, y=None):
        self._parameters(); X = support.features(X, fitting=True)
        n, p = X.shape; k = self.n_components
        if n < 2 or k > min(n-1,p):raise ValueError('ICA components<=min(n-1,p)')
        A, mean = support.centered(X); scale = support.uniform_scale(A); A /= scale
        eigenvalues, directions = np.linalg.eigh(A.T@A/n)
        order = np.argsort(-eigenvalues,kind='stable')[:k]; values = eigenvalues[order]
        if values[-1] <= max(eigenvalues[-1],1e-300)*1e-12:
            raise ValueError('requested ICA directions exceed resolved covariance rank')
        whitening = (directions[:,order]/np.sqrt(values)).T
        Z = A@whitening.T
        W = decorrelate(np.random.default_rng(self.random_state).normal(size=(k,k)))
        converged = False
        for iteration in range(self.max_iter):
            U = Z@W.T; G = np.tanh(U)
            proposal = G.T@Z/n - np.mean(1-G*G,axis=0)[:,None]*W
            new_W = decorrelate(proposal)
            delta = float(np.max(abs(abs(np.sum(new_W*W,axis=1))-1)))
            W = new_W
            if delta <= self.tol:
                converged = True;break
        if not converged:raise support.ConvergenceError('FastICA exhausted iterations')
        normalized_components = W@whitening
        components = normalized_components/scale
        mixing = np.linalg.pinv(components)
        self.__dict__.update(n_features_in_=p,mean_=mean,scale_=scale,
            whitening_=whitening/scale, normalized_whitening_=whitening,
            rotation_=W,components_=components,mixing_=mixing,
            normalized_components_=normalized_components,n_iter_=iteration+1,
            converged_=True, convergence_delta_=delta)
        return self

    @support.numerical
    def transform(self, X):
        return ((self._query(X)-self.mean_)/self.scale_)@self.normalized_components_.T

    @support.numerical
    def inverse_transform(self, Z):
        self._query(np.empty((0,getattr(self,'n_features_in_',1))))
        return support.latent_features(Z,len(self.components_))@self.mixing_.T+self.mean_

if __name__ == '__main__':support.main(FastICA)
