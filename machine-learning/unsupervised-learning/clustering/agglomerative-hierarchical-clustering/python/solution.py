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


class AgglomerativeClustering(s.Clusterer):
    """Full Euclidean hierarchy, with single/complete/average/Ward linkage."""
    def __init__(self, n_clusters=2, *, linkage='ward'):
        self.n_clusters = s.integer(n_clusters, 'n_clusters', 1, 128)
        if linkage not in ('single', 'complete', 'average', 'ward'):
            raise ValueError('unsupported linkage')
        self.linkage = linkage

    @s.numerical
    def fit(self, X):
        X = s.features(X, fitting=True, max_samples=128)
        k = s.integer(self.n_clusters, 'n_clusters', 1, len(X))
        if self.linkage not in ('single', 'complete', 'average', 'ward'):
            raise ValueError('unsupported linkage')
        D = s.pairwise(X)
        groups = {i: [i] for i in range(len(X))}
        means = {i: X[i].copy() for i in groups}
        cut = [g.copy() for g in groups.values()] if k == len(X) else None
        children, heights, sizes = [], [], []
        while len(groups) > 1:
            best = None
            keys = sorted(groups)
            for position, left in enumerate(keys):
                for right in keys[position+1:]:
                    A, B = groups[left], groups[right]
                    if self.linkage == 'ward':
                        height = float(np.sqrt(2*len(A)*len(B)/(len(A)+len(B)))*s.row_norm(means[left]-means[right]))
                    else:
                        values = D[np.ix_(A, B)]
                        if self.linkage == 'single':
                            height = float(values.min())
                        elif self.linkage == 'complete':
                            height = float(values.max())
                        else:
                            height = float(values.mean())
                    candidate = height, left, right
                    if best is None or candidate < best:
                        best = candidate
            height, left, right = best
            joined = groups.pop(left)+groups.pop(right)
            node = len(X)+len(children)
            groups[node] = joined
            means[node] = s.mean(X[joined])
            children.append((left, right));heights.append(height);sizes.append(len(joined))
            if len(groups) == k:
                cut = [g.copy() for g in groups.values()]
        self.__dict__.update(n_features_in_=X.shape[1], labels_=s.partition_labels(cut, len(X)),
                             children_=np.array(children, dtype=np.int64).reshape(-1, 2),
                             distances_=np.array(heights), counts_=np.array(sizes, dtype=np.int64),
                             n_leaves_=len(X), n_clusters_=k)
        return self


if __name__ == '__main__':
    s.main(AgglomerativeClustering)
