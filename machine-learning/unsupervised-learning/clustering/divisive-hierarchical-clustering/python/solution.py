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


class DivisiveClustering(s.Clusterer):
    """Euclidean DIANA: largest diameter, most-dissimilar seed, splinter moves."""
    def __init__(self, n_clusters=2):
        self.n_clusters = s.integer(n_clusters, 'n_clusters', 1, 128)

    @s.numerical
    def fit(self, X):
        X = s.features(X, fitting=True, max_samples=128)
        k = s.integer(self.n_clusters, 'n_clusters', 1, len(X))
        D = s.pairwise(X)
        groups = [tuple(range(len(X)))]
        cut = groups.copy() if k == 1 else None
        splits = []
        while len(groups) < len(X):
            eligible = [g for g in groups if len(g) > 1]
            parent = min(eligible, key=lambda g: (-float(D[np.ix_(g, g)].max()), min(g)))
            diameter = float(D[np.ix_(parent, parent)].max())
            averages = [(float(D[i, list(parent)].sum()/(len(parent)-1)), -i, i) for i in parent]
            seed = max(averages)[2]
            splinter = [seed]
            remaining = sorted(set(parent)-{seed})
            moves = []
            while len(remaining) > 1:
                options = []
                for i in remaining:
                    others = [j for j in remaining if j != i]
                    difference = float(D[i, others].mean()-D[i, splinter].mean())
                    options.append((difference, -i, i))
                difference, _, chosen = max(options)
                if difference <= 32*np.finfo(float).eps*diameter:
                    break
                remaining.remove(chosen)
                splinter.append(chosen)
                moves.append((chosen, difference))
            left, right = tuple(sorted(remaining)), tuple(sorted(splinter))
            groups.remove(parent)
            groups.extend((left, right))
            splits.append(dict(parent=parent, left=left, right=right, diameter=diameter,
                               splinter_seed=seed, moves=tuple(moves)))
            if len(groups) == k:
                cut = groups.copy()
        # Reverse the divisive schedule to expose a conventional leaf-ID hierarchy.
        ids = {(i,): i for i in range(len(X))}
        children, heights, counts = [], [], []
        for split in reversed(splits):
            pair = tuple(sorted((ids[split['left']], ids[split['right']])))
            children.append(pair)
            heights.append(split['diameter'])
            counts.append(len(split['parent']))
            ids[split['parent']] = len(X)+len(children)-1
        self.__dict__.update(n_features_in_=X.shape[1], labels_=s.partition_labels(cut, len(X)),
                             splits_=splits, children_=np.array(children, dtype=np.int64).reshape(-1, 2),
                             distances_=np.array(heights), counts_=np.array(counts, dtype=np.int64),
                             n_leaves_=len(X), n_clusters_=k)
        return self


if __name__ == '__main__':
    s.main(DivisiveClustering)
