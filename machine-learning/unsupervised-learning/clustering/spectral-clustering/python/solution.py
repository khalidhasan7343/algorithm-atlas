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


class SpectralClustering(s.Clusterer):
    """Normalized-affinity eigenvectors, row normalization and canonical K-Means."""
    def __init__(self, n_clusters=8, *, affinity='rbf', gamma=1.0, n_init=10, random_state=0):
        self.n_clusters = s.integer(n_clusters, 'n_clusters', 1, 64)
        if affinity not in ('rbf', 'precomputed'):
            raise ValueError('affinity must be rbf or precomputed')
        self.affinity = affinity
        self.gamma = s.scalar(gamma, 'gamma', positive=True)
        self.n_init = s.integer(n_init, 'n_init', 1, 16)
        self.random_state = s.seed(random_state)

    @s.numerical
    def fit(self, X):
        if self.affinity not in ('rbf', 'precomputed'):
            raise ValueError('affinity must be rbf or precomputed')
        gamma = s.scalar(self.gamma, 'gamma', positive=True)
        repeats = s.integer(self.n_init, 'n_init', 1, 16)
        random_state = s.seed(self.random_state)
        if self.affinity == 'rbf':
            X = s.features(X, fitting=True, max_samples=256)
            distance = s.pairwise(X)
            W = np.exp(-gamma*distance*distance)
            np.fill_diagonal(W, 0)
            p = X.shape[1]
        else:
            value = np.asarray(X)
            if value.ndim != 2 or value.shape[0] != value.shape[1] or not 2 <= len(value) <= 256 or value.dtype.kind not in 'iuf':
                raise ValueError('precomputed affinity must be a real square matrix with 2..256 rows')
            W = np.array(value, dtype=float, copy=True)
            if not np.isfinite(W).all() or np.any(W < 0) or np.any(W > 1e12):
                raise ValueError('affinity entries must be finite in [0,1e12]')
            if np.any(np.diag(W) != 0) or not np.allclose(W, W.T, atol=1e-12, rtol=1e-12):
                raise ValueError('zero diagonal and symmetric affinity required')
            W = (W+W.T)/2
            p = W.shape[1]
        k = s.integer(self.n_clusters, 'n_clusters', 1, min(64, len(W)))
        degree = W.sum(axis=1)
        if np.any(degree <= 0):
            raise ValueError('isolated vertices are unsupported; rescale or repair affinity')
        component = np.full(len(W), -1, dtype=int)
        count = 0
        for root in range(len(W)):
            if component[root] >= 0:
                continue
            queue = [root]
            component[root] = count
            for vertex in queue:
                for neighbor in np.flatnonzero(W[vertex] > 0):
                    if component[neighbor] < 0:
                        component[neighbor] = count
                        queue.append(int(neighbor))
            count += 1
        if count > k:
            raise ValueError('requested clusters must cover all disconnected graph components')
        root_degree = np.sqrt(degree)
        normalized = (W/root_degree[:, None])/root_degree[None, :]
        normalized = (normalized+normalized.T)/2
        eigenvalues, eigenvectors = np.linalg.eigh(normalized)
        order = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[order]
        vectors = eigenvectors[:, order[:k]]
        norms = s.row_norm(vectors)
        if np.any(norms == 0):
            raise ValueError('spectral embedding row is numerically unresolved')
        embedding = vectors/norms[:, None]
        partitioner = s.load('k-means').KMeans(k, n_init=repeats, random_state=random_state).fit(embedding)
        groups = [np.flatnonzero(partitioner.labels_ == j).tolist() for j in range(k)]
        labels = s.partition_labels(groups, len(W))
        cut = 0.0
        for group in groups:
            outside = np.setdiff1d(np.arange(len(W)), group)
            cut += float(W[np.ix_(group, outside)].sum()/degree[group].sum())
        self.__dict__.update(n_features_in_=p, labels_=labels,
                             affinity_matrix_=W.copy(), degree_=degree.copy(),
                             normalized_affinity_=normalized, eigenvalues_=eigenvalues[:k].copy(),
                             all_eigenvalues_=eigenvalues.copy(), eigenvectors_=vectors.copy(),
                             embedding_=embedding.copy(), kmeans_=partitioner, normalized_cut_=cut,
                             n_connected_components_=count, graph_component_labels_=component.copy())
        return self


if __name__ == '__main__':
    s.main(SpectralClustering)
