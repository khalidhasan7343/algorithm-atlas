"""Dense, personalized PageRank with explicit dangling mass and residual diagnostics."""
import importlib.util
from pathlib import Path
import sys

import numpy as np

_spec = importlib.util.spec_from_file_location('atlas_b9_support', Path(__file__).resolve().parents[2] / 'support.py')
support = sys.modules.get(_spec.name)
if support is None:
    support = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = support
    _spec.loader.exec_module(support)


class PageRank:
    """Rows encode outgoing weights. Dangling rows use personalization v.

    tolerance bounds the exact-arithmetic L1 rank error via residual/(1-d).
    A finite budget returns an approximation and exposes converged_=False.
    Failed refits leave the last successfully computed state untouched.
    """

    def __init__(self, damping=0.85, tolerance=1e-10, max_iter=1000, personalization=None):
        self.damping = damping
        self.tolerance = tolerance
        self.max_iter = max_iter
        self.personalization = personalization
        self._settings()

    def _settings(self):
        support.real(self.damping, 'damping', 0., 1., open_high=True)
        support.real(self.tolerance, 'tolerance', 1e-14, 1.)
        support.integer(self.max_iter, 'max_iter', 1, 100000)

    def fit(self, graph):
        self._settings()
        A = support.adjacency(graph)
        n = len(A)
        if self.personalization is None:
            v = np.full(n, 1 / n)
        else:
            v = support.array(self.personalization, 'personalization', ndim=1, max_cells=32)
            if v.shape != (n,) or np.any(v < 0) or not np.isclose(v.sum(), 1., rtol=0, atol=1e-12):
                raise ValueError('personalization must be a nonnegative length-n probability vector summing to one')
            v /= v.sum()
        degrees = A.sum(axis=1)
        P = np.zeros_like(A)
        positive = degrees > 0
        P[positive] = A[positive] / degrees[positive, None]
        P[~positive] = v
        rank = v.copy()
        d = float(self.damping)
        for iteration in range(1, int(self.max_iter) + 1):
            rank = d * (P.T @ rank) + (1 - d) * v
            rank /= rank.sum()  # Remove accumulated float64 mass drift.
            residual = float(np.linalg.norm(d * (P.T @ rank) + (1 - d) * v - rank, ord=1))
            bound = residual / (1 - d)
            if bound <= self.tolerance:
                break
        self.__dict__.update(scores_=rank, transition_matrix_=P, personalization_=v,
                             dangling_nodes_=np.flatnonzero(~positive), n_iter_=iteration,
                             residual_=residual, error_bound_=bound,
                             converged_=bool(bound <= self.tolerance),
                             optimization_status_='residual-tolerance' if bound <= self.tolerance else 'iteration-budget')
        return self

    def fit_transform(self, graph):
        return self.fit(graph).scores_.copy()
