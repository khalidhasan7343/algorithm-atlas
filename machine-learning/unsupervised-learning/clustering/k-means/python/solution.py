import importlib.util
from pathlib import Path
import sys

import numpy as np

if 'atlas_clustering_support' not in sys.modules:
    _spec = importlib.util.spec_from_file_location('atlas_clustering_support', Path(__file__).resolve().parents[2]/'support.py')
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = _module
    _spec.loader.exec_module(_module)
s = sys.modules['atlas_clustering_support']


class KMeans(s.Clusterer):
    """Lloyd iterations with strict assignment fixed-point convergence.

    A single uniform normalization protects tiny distances during fitting; the
    public inertia retains original squared units and can round to zero.
    """
    def __init__(self, n_clusters=8, *, init='k-means++', n_init=10,
                 max_iter=300, random_state=0):
        self.n_clusters = s.integer(n_clusters, 'n_clusters', 1, 64)
        self.init = init
        self.n_init = s.integer(n_init, 'n_init', 1, 16)
        self.max_iter = s.integer(max_iter, 'max_iter', 1, 1000)
        self.random_state = s.seed(random_state)

    @s.numerical
    def fit(self, X):
        X = s.features(X, fitting=True)
        k = s.integer(self.n_clusters, 'n_clusters', 1, min(64, len(X)))
        repeats = s.integer(self.n_init, 'n_init', 1, 16)
        limit = s.integer(self.max_iter, 'max_iter', 1, 1000)
        rng = np.random.default_rng(s.seed(self.random_state))
        if len(np.unique(X, axis=0)) < k:
            raise ValueError('n_clusters must not exceed distinct observed rows')
        offset = X[0].copy()
        scale = float(np.max(np.abs(X-offset)))
        scale = scale if scale else 1.0
        Z = (X-offset)/scale
        supplied = None
        if isinstance(self.init, str):
            if self.init not in ('k-means++', 'random'):
                raise ValueError('init must be k-means++, random or an explicit center matrix')
        else:
            supplied = s.features(self.init, fitting=True, expected=X.shape[1])
            if supplied.shape != (k, X.shape[1]) or repeats != 1:
                raise ValueError('explicit centers require shape (k,p) and n_init=1')
            supplied = (supplied-offset)/scale

        def distances(centers):
            return np.sum((Z[:, None, :]-centers[None, :, :])**2, axis=2)

        def initialize():
            if supplied is not None:
                return supplied.copy()
            if self.init == 'random':
                return Z[rng.choice(len(Z), k, replace=False)].copy()
            chosen = [int(rng.integers(len(Z)))]
            nearest = np.sum((Z-Z[chosen[0]])**2, axis=1)
            while len(chosen) < k:
                total = float(nearest.sum())
                if total <= 0:
                    raise ValueError('distinct directions unresolved at float64 precision')
                index = int(rng.choice(len(Z), p=nearest/total))
                chosen.append(index)
                nearest = np.minimum(nearest, np.sum((Z-Z[index])**2, axis=1))
            return Z[chosen].copy()

        best = None
        failed = 0
        for _ in range(repeats):
            centers = initialize()
            history = []
            repaired = 0
            for iteration in range(1, limit+1):
                d2 = distances(centers)
                labels = np.argmin(d2, axis=1)
                counts = np.bincount(labels, minlength=k)
                error = d2[np.arange(len(Z)), labels]
                for empty in np.flatnonzero(counts == 0):
                    eligible = counts[labels] > 1
                    donor = int(np.argmax(np.where(eligible, error, -1)))
                    counts[labels[donor]] -= 1
                    labels[donor] = empty
                    counts[empty] += 1
                    error[donor] = -1
                    repaired += 1
                updated = np.array([s.mean(Z[labels == j]) for j in range(k)])
                final_d2 = distances(updated)
                final_labels = np.argmin(final_d2, axis=1)
                objective = float(final_d2[np.arange(len(Z)), labels].sum())
                history.append(objective)
                centers = updated
                if np.array_equal(final_labels, labels):
                    candidate = dict(centers=centers.copy(), labels=labels.copy(),
                                     objective=objective, n_iter=iteration,
                                     history=np.array(history), repairs=repaired)
                    if best is None or objective < best['objective']:
                        best = candidate
                    break
            else:
                failed += 1
        if best is None:
            raise s.ConvergenceError('no initialization reached a Lloyd assignment fixed point')
        with np.errstate(under='ignore'):
            inertia = float(scale*scale*best['objective'])
        original_centers = s.finite(offset+scale*best['centers'])
        self.__dict__.update(n_features_in_=X.shape[1], cluster_centers_=original_centers.copy(),
                             labels_=best['labels'], inertia_=inertia,
                             normalized_inertia_=best['objective'], inertia_history_=best['history']*scale*scale,
                             normalized_inertia_history_=best['history'], offset_=offset, scale_=scale,
                             normalized_centers_=best['centers'], n_iter_=best['n_iter'],
                             empty_cluster_repairs_=best['repairs'], failed_initializations_=failed,
                             converged_=True)
        return self

    @s.numerical
    def transform(self, X):
        X = self._check_X(X)
        result = np.empty((len(X), len(self.normalized_centers_)))
        # Keep the offset and scaled center separate to avoid losing small
        # centroid displacements when adding a large common input offset.
        for i, row in enumerate(X):
            delta = (row-self.offset_)-self.scale_*self.normalized_centers_
            result[i] = s.row_norm(delta)
        return result

    def predict(self, X):
        return np.argmin(self.transform(X), axis=1)

    @s.numerical
    def score(self, X):
        distance = self.transform(X).min(axis=1)
        return -float(distance @ distance)


if __name__ == '__main__':
    s.main(KMeans)
