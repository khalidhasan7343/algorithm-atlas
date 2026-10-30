"""Small explicit clustering metrics; noise treatment and undefined cases are visible."""
import importlib.util
from pathlib import Path
import sys

import numpy as np

if 'atlas_clustering_support' not in sys.modules:
    spec = importlib.util.spec_from_file_location('atlas_clustering_support', Path(__file__).with_name('support.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
s = sys.modules['atlas_clustering_support']


def labels(value, n=None):
    a = np.asarray(value)
    if a.ndim != 1 or not 1 <= len(a) <= 512 or a.dtype.kind not in 'iu' or (n is not None and len(a) != n):
        raise ValueError('integer label vector with 1..512 matching rows required')
    return np.array(a, copy=True)


def adjusted_rand_index(truth, prediction):
    """Permutation-invariant pair agreement; -1 is a label, not silently excluded."""
    a = labels(truth)
    b = labels(prediction, len(a))
    if len(a) < 2:
        return 1.0
    _, first = np.unique(a, return_inverse=True)
    _, second = np.unique(b, return_inverse=True)
    contingency = np.zeros((int(first.max())+1, int(second.max())+1), dtype=np.int64)
    np.add.at(contingency, (first, second), 1)
    def pairs(counts):
        return sum(int(v)*(int(v)-1)//2 for v in counts.flat)
    observed = pairs(contingency)
    rows, columns = pairs(contingency.sum(axis=1)), pairs(contingency.sum(axis=0))
    total = len(a)*(len(a)-1)//2
    expected = rows*columns/total
    denominator = .5*(rows+columns)-expected
    return 1.0 if denominator == 0 else float((observed-expected)/denominator)


@s.numerical
def silhouette_samples(X, prediction, *, ignore_noise=True):
    """Euclidean silhouette; dropped noise rows receive NaN diagnostics."""
    s.boolean(ignore_noise, 'ignore_noise')
    X = s.features(X, fitting=True)
    prediction = labels(prediction, len(X))
    keep = prediction != -1 if ignore_noise else np.ones(len(X), dtype=bool)
    groups = np.unique(prediction[keep])
    if not 2 <= len(groups) < int(keep.sum()):
        raise ValueError('silhouette needs 2..n_kept-1 clusters')
    distances = s.pairwise(X[keep])
    y = prediction[keep]
    scores = np.empty(len(y))
    for i in range(len(y)):
        same = y == y[i]
        count = int(same.sum())
        if count == 1:
            scores[i] = 0.0
            continue
        within = float(distances[i, same].sum()/(count-1))
        between = min(float(distances[i, y == group].mean()) for group in groups if group != y[i])
        maximum = max(within, between)
        scores[i] = (between-within)/maximum if maximum else 0.0
    result = np.full(len(X), np.nan)
    result[keep] = scores
    return result


def silhouette_score(X, prediction, *, ignore_noise=True):
    values = silhouette_samples(X, prediction, ignore_noise=ignore_noise)
    return float(values[np.isfinite(values)].mean())


def clustering_report(X, prediction, *, truth=None):
    X = s.features(X, fitting=True)
    y = labels(prediction, len(X))
    noise = y == -1
    clusters = np.unique(y[~noise])
    quality = silhouette_score(X, y) if 2 <= len(clusters) < int((~noise).sum()) else None
    result = dict(n_clusters=len(clusters), noise_count=int(noise.sum()), coverage=float((~noise).mean()),
                  cluster_sizes={str(int(c)): int(np.sum(y == c)) for c in clusters},
                  silhouette=quality, silhouette_noise_policy='exclude -1; undefined -> None',
                  adjusted_rand=None, adjusted_rand_noise_policy='all rows; -1 treated as one label')
    if truth is not None:
        result['adjusted_rand'] = adjusted_rand_index(truth, y)
    return result
