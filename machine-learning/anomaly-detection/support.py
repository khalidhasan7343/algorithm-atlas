"""B12 contracts, unchanged B4/B2 distance reuse, calibration and anomaly metrics."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parent
TOPICS = ('isolation-forest', 'one-class-svm', 'local-outlier-factor')


def module_at(name, path):
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:
            del sys.modules[name]
            raise
    return sys.modules[name]


b4 = module_at('atlas_clustering_support', ROOT.parent/'unsupervised-learning/clustering/support.py')
integer = b4.integer


class NumericalError(FloatingPointError):
    """A supported computation is not representable or fails its numeric certificate."""


def scalar(value, name, low, high, *, open_low=False):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, float, np.integer, np.floating)):
        raise ValueError(name+' must be a real scalar')
    try:
        value = float(value)
    except OverflowError as error:
        raise ValueError(name+' must fit float64') from error
    if not np.isfinite(value) or not low <= value <= high or (open_low and value == low):
        raise ValueError(name+' outside supported range')
    return value


def features(X, *, fitting=False, expected=None, minimum=1):
    values = b4.features(X, fitting=fitting, expected=expected, max_samples=256 if fitting else 1024)
    if fitting and len(values) < minimum:
        raise ValueError('insufficient training samples')
    return values


def finite(values, name='computed values'):
    if not np.isfinite(values).all():
        raise NumericalError(name+' must be finite')
    return values


def contamination(value):
    if isinstance(value, str):
        if value != 'auto':
            raise ValueError('contamination string must be auto')
        return value
    return scalar(value, 'contamination', 0, .5, open_low=True)


def anomaly_vector(values, *, maximum=2048):
    a = np.asarray(values)
    if a.ndim != 1 or not 1 <= len(a) <= maximum or a.dtype.kind not in 'iuf':
        raise ValueError('nonempty real anomaly-score vector required')
    a = np.array(a, dtype=float, copy=True)
    if np.isnan(a).any() or np.isneginf(a).any():
        raise ValueError('scores may be finite or explicitly positive infinity only')
    return a


def training_threshold(scores, fraction, default):
    values = np.sort(anomaly_vector(scores, maximum=256))
    fraction = contamination(fraction)
    if fraction == 'auto':
        return scalar(default, 'default threshold', -1e12, 1e12)
    position = (len(values)-1)*(1-fraction)
    lo, hi = int(np.floor(position)), int(np.ceil(position))
    weight = position-lo
    if lo == hi or weight == 0:
        return float(values[lo])
    # Continuous extended-real limit: any positive weight on +inf gives +inf.
    if np.isposinf(values[hi]):
        return float('inf')
    return float((1-weight)*values[lo]+weight*values[hi])


def decision_from_anomaly(scores, threshold):
    values = np.asarray(scores, dtype=float)
    if np.isnan(values).any() or np.isneginf(values).any() or np.isnan(threshold) or np.isneginf(threshold):
        raise NumericalError('invalid extended anomaly score/threshold')
    if np.isposinf(threshold):
        return np.where(np.isposinf(values), 0., np.inf)
    return threshold-values


def labels_from_decision(values):
    return np.where(np.asarray(values) >= 0, 1, -1).astype(np.int64)


class Detector:
    def _ready(self):
        if not hasattr(self, 'n_features_in_'):
            raise ValueError('fit must succeed before inference')

    def _query(self, X):
        self._ready()
        return features(X, expected=self.n_features_in_)

    def fit_predict(self, X):
        return self.fit(X).labels_.copy()


def kernel(X, Y, gamma):
    """Reuse the approved blocked direct-difference RBF implementation unchanged."""
    module = module_at('atlas_b12_svr_kernel', ROOT.parent/'supervised-learning/regression/support-vector-regression/python/solution.py')
    with np.errstate(under='ignore'):
        values = module._kernel_matrix(X, Y, 'rbf', gamma)
    return finite(values, 'RBF kernel')


def anomaly_metrics(actual, predicted, scores):
    """Positive evaluation class is -1 (anomaly); AP is a tied-group step integral."""
    y, labels = np.asarray(actual), np.asarray(predicted)
    values = anomaly_vector(scores)
    for array in (y, labels):
        if array.shape != values.shape or array.dtype.kind not in 'iu' or not np.isin(array, [-1, 1]).all():
            raise ValueError('evaluation labels must be matching integer +/-1 vectors')
    positive, chosen = y == -1, labels == -1
    tp = int(np.sum(positive & chosen));fp = int(np.sum(~positive & chosen))
    fn = int(np.sum(positive & ~chosen));tn = int(np.sum(~positive & ~chosen))
    precision = tp/(tp+fp) if tp+fp else None
    recall = tp/(tp+fn) if tp+fn else None
    f1 = 2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None
    p, n = int(positive.sum()), int((~positive).sum())
    order = np.argsort(-values, kind='stable')
    groups = []
    start = 0
    while start < len(order):
        stop = start+1
        while stop < len(order) and values[order[stop]] == values[order[start]]:
            stop += 1
        members = order[start:stop]
        groups.append((int(positive[members].sum()), len(members)))
        start = stop
    seen_p = seen_n = 0
    area = average_precision = 0.
    for group_p, size in groups:
        group_n = size-group_p
        # Positives above every remaining negative, half credit for within-score ties.
        area += group_p*(n-seen_n-group_n+.5*group_n)
        seen_p += group_p;seen_n += group_n
        if p:
            average_precision += (group_p/p)*(seen_p/(seen_p+seen_n))
    return dict(confusion_matrix=[[tn, fp], [fn, tp]], precision=precision, recall=recall, f1=f1,
                roc_auc=area/(p*n) if p and n else None,
                average_precision=average_precision if p else None)


def load(topic):
    if topic not in TOPICS:
        raise ValueError('unknown B12 canonical')
    return module_at('atlas_b12_'+topic.replace('-', '_'), ROOT/topic/'python/solution.py')
