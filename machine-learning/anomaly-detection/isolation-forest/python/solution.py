import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec = importlib.util.spec_from_file_location('atlas_b12_support', Path(__file__).resolve().parents[2]/'support.py')
s = sys.modules.get(_spec.name)
if s is None:
    s = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = s
    _spec.loader.exec_module(s)

from dataclasses import dataclass


def expected_path_length(count):
    count = s.integer(count, 'leaf/sample count', 0, 256)
    if count <= 1:
        return 0.
    if count == 2:
        return 1.
    return float(2*sum(1/j for j in range(1, count))-2*(count-1)/count)


@dataclass(frozen=True)
class IsolationNode:
    count: int
    depth: int = 0
    feature: int | None = None
    split: float | None = None
    left: object = None
    right: object = None

    def __post_init__(self):
        s.integer(self.count, 'node count', 1, 256)
        s.integer(self.depth, 'node depth', 0, 32)
        if self.feature is None:
            if self.split is not None or self.left is not None or self.right is not None:
                raise ValueError('leaf must have no split or children')
        else:
            s.integer(self.feature, 'feature index', 0, 31)
            s.scalar(self.split, 'split', -1e12, 1e12)
            if not isinstance(self.left, IsolationNode) or not isinstance(self.right, IsolationNode):
                raise ValueError('internal node requires two children')
            if self.left.count+self.right.count != self.count or self.left.depth != self.depth+1 or self.right.depth != self.depth+1:
                raise ValueError('child sample counts/depths must match parent')


def _build(X, depth, limit, rng):
    if depth >= limit or len(X) <= 1:
        return IsolationNode(len(X), depth)
    minimum, maximum = X.min(axis=0), X.max(axis=0)
    varying = np.flatnonzero(minimum < maximum)
    if not len(varying):
        return IsolationNode(len(X), depth)
    feature = int(varying[int(rng.integers(len(varying)))])
    low, high = float(minimum[feature]), float(maximum[feature])
    split = low+(high-low)*float(rng.random())
    # A minimally adjusted float split in (low,high] keeps both branches nonempty.
    split = max(float(np.nextafter(low, high)), min(split, high))
    mask = X[:, feature] < split
    if not mask.any() or mask.all():
        raise s.NumericalError('random split failed to separate a nonconstant feature')
    left, right = _build(X[mask], depth+1, limit, rng), _build(X[~mask], depth+1, limit, rng)
    return IsolationNode(len(X), depth, feature, split, left, right)


def path_lengths(X, tree):
    X = s.features(X)
    if not isinstance(tree, IsolationNode) or tree.depth != 0:
        raise ValueError('root isolation node required')
    result = np.empty(len(X))
    for i, row in enumerate(X):
        node, depth = tree, 0
        while node.feature is not None:
            if depth >= 32 or node.feature >= len(row):
                raise ValueError('tree depth/feature incompatible with query')
            node = node.left if row[node.feature] < node.split else node.right
            depth += 1
        result[i] = depth+expected_path_length(node.count)
    return result


class IsolationForest(s.Detector):
    """Random subsamples/variable-feature uniform splits; exact harmonic corrections."""
    def __init__(self, n_estimators=64, *, max_samples='auto', max_depth=None, contamination='auto', random_state=0):
        self.n_estimators = s.integer(n_estimators, 'n_estimators', 1, 128)
        if not (isinstance(max_samples, str) and max_samples == 'auto'):
            s.integer(max_samples, 'max_samples', 1, 256)
        self.max_samples = max_samples
        self.max_depth = None if max_depth is None else s.integer(max_depth, 'max_depth', 0, 32)
        self.contamination = s.contamination(contamination)
        self.random_state = s.integer(random_state, 'random_state', 0, 2**32-1)

    def fit(self, X):
        X = s.features(X, fitting=True)
        count = s.integer(self.n_estimators, 'n_estimators', 1, 128)
        size = min(256, len(X)) if self.max_samples == 'auto' else s.integer(self.max_samples, 'max_samples', 1, len(X))
        limit = int(np.ceil(np.log2(size))) if self.max_depth is None else s.integer(self.max_depth, 'max_depth', 0, 32)
        fraction = s.contamination(self.contamination)
        seed = s.integer(self.random_state, 'random_state', 0, 2**32-1)
        rng = np.random.default_rng(seed)
        trees, samples = [], []
        for _ in range(count):
            indices = rng.choice(len(X), size=size, replace=False)
            trees.append(_build(X[indices], 0, limit, rng))
            samples.append(indices.copy())
        paths = np.mean(np.stack([path_lengths(X, tree) for tree in trees]), axis=0)
        normalizer = expected_path_length(size)
        scores = np.exp2(-paths/normalizer) if normalizer else np.full(len(X), .5)
        threshold = s.training_threshold(scores, fraction, .5)
        decisions = s.decision_from_anomaly(scores, threshold)
        self.n_features_in_, self.n_samples_, self.max_samples_, self.max_depth_ = X.shape[1], len(X), size, limit
        self.trees_, self.sample_indices_ = tuple(trees), tuple(samples)
        self.anomaly_scores_, self.threshold_, self.labels_ = scores.copy(), threshold, s.labels_from_decision(decisions)
        self.training_path_lengths_, self.normalizer_ = paths.copy(), normalizer
        self.status_, self.converged_ = 'constructed', None
        return self

    def anomaly_scores(self, X):
        X = self._query(X)
        if self.normalizer_ == 0:
            return np.full(len(X), .5)
        paths = np.mean(np.stack([path_lengths(X, tree) for tree in self.trees_]), axis=0)
        return np.exp2(-paths/self.normalizer_)

    def score_samples(self, X):
        return -self.anomaly_scores(X)

    def decision_function(self, X):
        return s.decision_from_anomaly(self.anomaly_scores(X), self.threshold_)

    def predict(self, X):
        return s.labels_from_decision(self.decision_function(X))
