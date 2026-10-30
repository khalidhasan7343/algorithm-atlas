"""Reduced SVD through explicit one-sided Jacobi rotations (no SVD/eigh call)."""
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

def _tall_jacobi(A, tol, max_sweeps):
    n, p = A.shape
    B, V = A.copy(), np.eye(p)
    converged = False
    for sweep in range(max_sweeps):
        changed = False
        for i in range(p-1):
            for j in range(i+1, p):
                alpha, beta = B[:, i]@B[:, i], B[:, j]@B[:, j]
                gamma = B[:, i]@B[:, j]
                if alpha == 0 or beta == 0 or abs(gamma) <= tol*np.sqrt(alpha)*np.sqrt(beta):
                    continue
                # atan2 avoids the overflow-prone (beta-alpha)/(2*gamma).
                theta = .5*np.arctan2(2*gamma, beta-alpha)
                c, s = np.cos(theta), np.sin(theta)
                bi, bj = B[:, i].copy(), B[:, j].copy()
                B[:, i], B[:, j] = c*bi-s*bj, s*bi+c*bj
                vi, vj = V[:, i].copy(), V[:, j].copy()
                V[:, i], V[:, j] = c*vi-s*vj, s*vi+c*vj
                changed = True
        if not changed:
            converged = True; break
    if not converged:
        raise support.ConvergenceError('Jacobi sweeps exhausted before column orthogonality')
    singular = np.sqrt(np.sum(B*B, axis=0))
    order = np.argsort(-singular, kind='stable')
    singular, B, V = singular[order], B[:, order], V[:, order]
    U = np.zeros((n, p))
    threshold = np.finfo(float).eps*max(A.shape)*max(singular[0], 1e-300)
    resolved = singular > threshold
    for j in range(p):
        if resolved[j]:
            U[:, j] = B[:, j]/singular[j]
        else:
            singular[j] = 0
            # Complete a deterministic orthonormal basis for zero singular values.
            for axis in range(n):
                v = np.eye(1, n, axis).ravel()
                for _ in range(2):
                    v -= U[:, :j]@(U[:, :j].T@v)
                length = np.linalg.norm(v)
                if length > 1e-10:
                    U[:, j] = v/length; break
            else:
                raise ValueError('could not resolve null-space basis')
    return U, singular, V.T, sweep+1


class SVD(support.Projection):
    def __init__(self, n_components=None, tol=1e-12, max_sweeps=100):
        self.n_components, self.tol, self.max_sweeps = n_components, tol, max_sweeps
        self._parameters()

    def _parameters(self):
        if self.n_components is not None:
            support.integer(self.n_components, 'n_components', 1, 32)
        support.scalar(self.tol, 'tol', 1e-15, 1e-6)
        support.integer(self.max_sweeps, 'max_sweeps', 1, 1000)

    @support.numerical
    def fit(self, X, y=None):
        self._parameters()
        X = support.features(X, fitting=True)
        n, p = X.shape
        k = min(n, p) if self.n_components is None else self.n_components
        if k > min(n, p):
            raise ValueError('n_components exceeds min(n,p)')
        scale = support.uniform_scale(X)
        A = X/scale
        if n >= p:
            U, s, V, sweeps = _tall_jacobi(A, self.tol, self.max_sweeps)
        else:
            left, s, right, sweeps = _tall_jacobi(A.T, self.tol, self.max_sweeps)
            U, V = right.T, left.T
        U, V = support.orient(U, V)
        state = dict(n_features_in_=p, left_singular_vectors_=U[:, :k].copy(),
                     singular_values_=s[:k]*scale, components_=V[:k].copy(),
                     full_singular_values_=s*scale, scaled_singular_values_=s,
                     scale_=scale, n_iter_=sweeps, converged_=True)
        self.__dict__.update(state)
        return self

    @support.numerical
    def transform(self, X):
        return self._query(X)@self.components_.T

    @support.numerical
    def inverse_transform(self, Z):
        self._query(np.empty((0, getattr(self, 'n_features_in_', 1))))
        Z = support.latent_features(Z, len(self.components_))
        return Z@self.components_


if __name__ == '__main__':
    support.main(SVD)
