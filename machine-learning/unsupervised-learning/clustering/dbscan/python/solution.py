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


class DBSCAN(s.Clusterer):
    """Dense Euclidean DBSCAN; radius support includes the observation itself."""
    def __init__(self, *, eps=.5, min_samples=5):
        self.eps = s.scalar(eps, 'eps', positive=True)
        self.min_samples = s.integer(min_samples, 'min_samples', 1, 512)

    @s.numerical
    def fit(self, X):
        X = s.features(X, fitting=True)
        eps = s.scalar(self.eps, 'eps', positive=True)
        minimum = s.integer(self.min_samples, 'min_samples', 1, 512)
        neighborhood = s.pairwise(X) <= eps
        counts = neighborhood.sum(axis=1)
        core = counts >= minimum
        labels = np.full(len(X), -1, dtype=np.int64)
        visited = np.zeros(len(X), dtype=bool)
        clusters = 0
        for start in range(len(X)):
            if visited[start]:
                continue
            if not core[start]:
                visited[start] = True
                continue
            queue = [start]
            queued = np.zeros(len(X), dtype=bool)
            queued[start] = True
            position = 0
            while position < len(queue):
                point = queue[position]
                position += 1
                if not visited[point]:
                    visited[point] = True
                    if core[point]:
                        for neighbor in np.flatnonzero(neighborhood[point]):
                            if not queued[neighbor]:
                                queued[neighbor] = True
                                queue.append(int(neighbor))
                # Previously inspected noise can become a border point; a border
                # already reached by another component keeps its first label.
                if labels[point] < 0:
                    labels[point] = clusters
            clusters += 1
        self.__dict__.update(n_features_in_=X.shape[1], labels_=labels,
                             core_sample_indices_=np.flatnonzero(core), components_=X[core].copy(),
                             neighbor_counts_=counts.copy(), n_clusters_=clusters)
        return self


if __name__ == '__main__':
    s.main(DBSCAN)
