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


class MeanShift(s.Clusterer):
    """Every-row flat-kernel mean shift, then deterministic support-based merging."""
    def __init__(self, *, bandwidth=1.0, max_iter=300, tol=1e-3, cluster_all=True):
        self.bandwidth = s.scalar(bandwidth, 'bandwidth', positive=True)
        self.max_iter = s.integer(max_iter, 'max_iter', 1, 1000)
        self.tol = s.scalar(tol, 'tol', high=1, positive=True)
        self.cluster_all = s.boolean(cluster_all, 'cluster_all')

    @s.numerical
    def fit(self, X):
        X = s.features(X, fitting=True)
        bandwidth = s.scalar(self.bandwidth, 'bandwidth', positive=True)
        limit = s.integer(self.max_iter, 'max_iter', 1, 1000)
        tolerance = s.scalar(self.tol, 'tol', high=1, positive=True)
        all_points = s.boolean(self.cluster_all, 'cluster_all')
        candidates, counts, iterations = [], [], []
        for start in X:
            center = start.copy()
            for iteration in range(1, limit+1):
                mask = s.row_norm(X-center) <= bandwidth
                if not mask.any():
                    raise s.ConvergenceError('no supported flat-kernel mode neighborhood')
                updated = s.mean(X[mask])
                movement = float(s.row_norm(updated-center))
                center = updated
                if movement <= tolerance*bandwidth:
                    break
            else:
                raise s.ConvergenceError('mean-shift seed exhausted max_iter')
            count = int(np.sum(s.row_norm(X-center) <= bandwidth))
            if count == 0:
                raise s.ConvergenceError('mode support unresolved at float64 precision')
            candidates.append(center.copy())
            counts.append(count)
            iterations.append(iteration)
        order = sorted(range(len(X)), key=lambda i: (-counts[i], tuple(-v for v in candidates[i]), i))
        kept = []
        for index in order:
            if not kept or np.all(s.row_norm(np.array(kept)-candidates[index]) > bandwidth):
                kept.append(candidates[index])
        centers = np.array(kept)
        distance = s.pairwise(X, centers)
        labels = np.argmin(distance, axis=1)
        if not all_points:
            labels[distance.min(axis=1) > bandwidth] = -1
        self.__dict__.update(n_features_in_=X.shape[1], labels_=labels.astype(np.int64),
                             cluster_centers_=centers.copy(), candidate_centers_=np.array(candidates),
                             candidate_support_=np.array(counts), seed_iterations_=np.array(iterations),
                             n_iter_=max(iterations), converged_=True, bandwidth_=bandwidth,
                             cluster_all_=all_points)
        return self

    @s.numerical
    def predict(self, X):
        X = self._check_X(X)
        distance = s.pairwise(X, self.cluster_centers_)
        labels = np.argmin(distance, axis=1)
        if not self.cluster_all_:
            labels[distance.min(axis=1) > self.bandwidth_] = -1
        return labels.astype(np.int64)


if __name__ == '__main__':
    s.main(MeanShift)
