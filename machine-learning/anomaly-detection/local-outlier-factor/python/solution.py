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

class LocalOutlierFactor(s.Detector):
    """Exact tie-inclusive training LOF; duplicate extension via a common epsilon limit."""
    def __init__(self, n_neighbors=5, *, contamination='auto', metric='euclidean'):
        self.n_neighbors = s.integer(n_neighbors, 'n_neighbors', 1, 255)
        self.contamination = s.contamination(contamination)
        if metric != 'euclidean':
            raise ValueError('only Euclidean metric supported')
        self.metric = metric

    def fit(self, X):
        X = s.features(X, fitting=True, minimum=2)
        k = s.integer(self.n_neighbors, 'n_neighbors', 1, len(X)-1)
        if self.metric != 'euclidean':
            raise ValueError('only Euclidean metric supported')
        fraction = s.contamination(self.contamination)
        distance = s.b4.pairwise(X)
        other = distance.copy()
        np.fill_diagonal(other, np.inf)
        kdistance = np.sort(other, axis=1)[:, k-1]
        neighborhoods, reachability = [], []
        log_mean = np.empty(len(X));means = np.empty(len(X));zero = np.empty(len(X), dtype=bool)
        for i in range(len(X)):
            neighbors = np.flatnonzero((np.arange(len(X)) != i) & (distance[i] <= kdistance[i]))
            values = np.maximum(kdistance[neighbors], distance[i, neighbors])
            neighborhoods.append(neighbors.copy())
            reachability.append(values.copy())
            maximum = float(values.max())
            zero[i] = maximum == 0
            if zero[i]:
                means[i], log_mean[i] = 0., -np.inf
            else:
                # Keep a finite log mean even if the displayed ordinary mean underflows.
                with np.errstate(under='ignore'):
                    normalized_mean = float(np.mean(values/maximum))
                    means[i] = maximum*normalized_mean
                log_mean[i] = np.log(maximum)+np.log(normalized_mean)
        log_density = -log_mean
        with np.errstate(over='ignore', under='ignore'):
            density = np.exp(log_density)
        # Infinite ordinary density can be a representation limit,not a true zero mean.
        density_overflow = np.isposinf(density) & ~zero
        scores, log_scores = np.empty(len(X)), np.empty(len(X))
        for i, neighbors in enumerate(neighborhoods):
            if zero[i]:
                if not zero[neighbors].all():
                    raise s.NumericalError('zero-reach duplicate neighborhood violated Euclidean geometry')
                scores[i], log_scores[i] = 1., 0.
            elif zero[neighbors].any():
                scores[i], log_scores[i] = np.inf, np.inf
            else:
                ratios = log_mean[i]-log_mean[neighbors]
                maximum = float(ratios.max())
                with np.errstate(under='ignore'):
                    log_score = maximum+np.log(np.mean(np.exp(ratios-maximum)))
                if log_score > np.log(np.finfo(float).max):
                    raise s.NumericalError('finite LOF exceeds float64 representation')
                with np.errstate(over='ignore', under='ignore'):
                    score = float(np.exp(log_score))
                if not np.isfinite(score) or score <= 0:
                    raise s.NumericalError('finite positive LOF is not representable')
                scores[i], log_scores[i] = score, log_score
        threshold = s.training_threshold(scores, fraction, 1.5)
        decision = s.decision_from_anomaly(scores, threshold)
        self.n_features_in_, self.n_samples_, self.n_neighbors_ = X.shape[1], len(X), k
        self.X_fit_, self.distance_matrix_, self.k_distances_ = X.copy(), distance.copy(), kdistance.copy()
        self.neighborhoods_, self.reachability_distances_ = tuple(neighborhoods), tuple(reachability)
        self.mean_reachability_, self.log_mean_reachability_ = means.copy(), log_mean.copy()
        self.zero_reachability_, self.lrd_, self.log_lrd_ = zero.copy(), density.copy(), log_density.copy()
        self.density_representation_overflow_ = density_overflow.copy()
        self.anomaly_scores_, self.log_lof_, self.threshold_ = scores.copy(), log_scores.copy(), threshold
        self.labels_ = s.labels_from_decision(decision)
        self.status_, self.converged_ = 'training-lof-computed', None
        return self

    def _training_only(self, X):
        self._ready()
        if X is not None:
            raise ValueError('training-set LOF only;unseen-query novelty inference is unsupported')

    def anomaly_scores(self, X=None):
        self._training_only(X)
        return self.anomaly_scores_.copy()

    def score_samples(self, X=None):
        return -self.anomaly_scores(X)

    def decision_function(self, X=None):
        self._training_only(X)
        return s.decision_from_anomaly(self.anomaly_scores_, self.threshold_)

    def predict(self, X=None):
        return s.labels_from_decision(self.decision_function(X))
