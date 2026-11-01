import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec = importlib.util.spec_from_file_location('atlas_b13_support', Path(__file__).resolve().parents[2] / 'support.py')
s = sys.modules.get(_spec.name)
if s is None:
    s = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = s
    _spec.loader.exec_module(s)

class ImpossibleSequenceError(ValueError):
    """No label sequence satisfies the structural masks."""


class LinearChainCRF:
    """Globally normalized dense-feature CRF; all four parameter groups train."""
    def __init__(self, labels, n_features, *, l2=.01, learning_rate=.5, max_iter=100,
                 tolerance=1e-6, allowed_transitions=None, allowed_start=None):
        if not isinstance(labels, (list, tuple)) or not 1 <= len(labels) <= 8 or any(not isinstance(t, str) or not t or len(t) > 32 for t in labels) or len(set(labels)) != len(labels):
            raise ValueError('1..8 unique nonempty string labels required')
        self.labels_ = tuple(labels)
        self.label_index_ = {t: i for i, t in enumerate(labels)}
        self.n_features = s.integer(n_features, 'n_features', 1, 128)
        self.l2 = s.scalar(l2, 'l2', 0., 10.)
        self.learning_rate = s.scalar(learning_rate, 'learning_rate', 1e-8, 1.)
        self.max_iter = s.integer(max_iter, 'max_iter', 1, 200)
        self.tolerance = s.scalar(tolerance, 'tolerance', 0., .1)
        k = len(labels)
        self.allowed_transitions_ = self._mask(allowed_transitions, (k, k))
        self.allowed_start_ = self._mask(allowed_start, (k,))
        self.parameters_ = dict(emission=np.zeros((self.n_features, k)), transition=np.zeros((k, k)), start=np.zeros(k), end=np.zeros(k))
        self.status_, self.converged_, self.n_iter_ = 'initialized', None, 0

    @staticmethod
    def _mask(mask, shape):
        if mask is None:
            return np.ones(shape, dtype=bool)
        a = np.asarray(mask)
        if a.shape != shape or a.dtype.kind != 'b':
            raise ValueError('structural mask must have Boolean dtype and correct shape')
        return a.copy()

    def _parameters(self, parameters=None):
        p = self.parameters_ if parameters is None else parameters
        expected = dict(emission=(self.n_features, len(self.labels_)), transition=(len(self.labels_),)*2, start=(len(self.labels_),), end=(len(self.labels_),))
        if not isinstance(p, dict) or set(p) != set(expected):
            raise ValueError('four parameter groups required')
        for name, shape in expected.items():
            a = np.asarray(p[name])
            if a.shape != shape or a.dtype.kind not in 'iuf' or not np.isfinite(a).all() or np.max(np.abs(a)) > 1e4:
                raise ValueError('finite bounded parameters with correct shapes required')
        return p

    def _features(self, features, length=None):
        x = s.finite_matrix(features, 'features', rows=64, cols=128)
        if x.shape[1] != self.n_features or np.max(np.abs(x)) > 100.:
            raise ValueError('feature dimension must match; magnitudes at most100')
        length = len(x) if length is None else s.integer(length, 'length', 1, len(x))
        return x[:length].copy()

    def _labels(self, labels, length):
        if not isinstance(labels, (list, tuple)) or len(labels) != length or any(not isinstance(t, str) or t not in self.label_index_ for t in labels):
            raise ValueError('known string labels aligned with active rows required')
        ids = np.array([self.label_index_[t] for t in labels], dtype=np.int64)
        if not self.allowed_start_[ids[0]] or (len(ids) > 1 and not self.allowed_transitions_[ids[:-1], ids[1:]].all()):
            raise ValueError('gold path violates structural constraints')
        return ids

    def _inference(self, x, p):
        emission = x @ p['emission']
        transition = np.where(self.allowed_transitions_, p['transition'], -np.inf)
        start = np.where(self.allowed_start_, p['start'], -np.inf)
        alpha = np.empty_like(emission)
        alpha[0] = start + emission[0]
        for t in range(1, len(x)):
            alpha[t] = emission[t] + s.logsumexp(alpha[t-1, :, None]+transition, axis=0)
        log_z = float(s.logsumexp(alpha[-1]+p['end']))
        if not np.isfinite(log_z):
            raise ImpossibleSequenceError('no finite legal path')
        beta = np.empty_like(emission)
        beta[-1] = p['end']
        for t in range(len(x)-2, -1, -1):
            beta[t] = s.logsumexp(transition+emission[t+1][None, :]+beta[t+1][None, :], axis=1)
        token = np.exp(alpha+beta-log_z)
        token /= token.sum(axis=1, keepdims=True)
        pair = np.empty((len(x)-1, len(self.labels_), len(self.labels_)))
        for t in range(len(x)-1):
            pair[t] = np.exp(alpha[t, :, None]+transition+emission[t+1][None, :]+beta[t+1][None, :]-log_z)
            pair[t] /= pair[t].sum()
        return dict(log_partition=log_z, log_forward=alpha, log_backward=beta, token_marginals=token, pair_marginals=pair)

    def infer(self, features, *, length=None):
        return self._inference(self._features(features, length), self._parameters())

    def log_partition(self, features, *, length=None):
        return self.infer(features, length=length)['log_partition']

    @staticmethod
    def _score(x, y, p):
        return float(p['start'][y[0]] + p['end'][y[-1]] + np.sum((x@p['emission'])[np.arange(len(x)), y]) + np.sum(p['transition'][y[:-1], y[1:]]))

    def sequence_score(self, features, labels, *, length=None):
        x = self._features(features, length)
        y = self._labels(labels, len(x))
        return self._score(x, y, self._parameters())

    def log_probability(self, features, labels, *, length=None):
        return self.sequence_score(features, labels, length=length) - self.log_partition(features, length=length)

    def _loss(self, x, y, p):
        info = self._inference(x, p)
        delta = info['token_marginals'].copy()
        delta[np.arange(len(x)), y] -= 1.
        g = dict(emission=x.T@delta, transition=info['pair_marginals'].sum(axis=0), start=delta[0].copy(), end=delta[-1].copy())
        np.add.at(g['transition'], (y[:-1], y[1:]), -1.)
        return info['log_partition'] - self._score(x, y, p), g

    def loss_gradients(self, features, labels, *, length=None):
        """Unregularized sequence NLL and all exact score-parameter gradients."""
        x = self._features(features, length)
        return self._loss(x, self._labels(labels, len(x)), self._parameters())

    def decode(self, features, *, length=None):
        x, p = self._features(features, length), self._parameters()
        emission = x@p['emission']
        transition = np.where(self.allowed_transitions_, p['transition'], -np.inf)
        delta = np.where(self.allowed_start_, p['start'], -np.inf)+emission[0]
        back = np.zeros((len(x), len(self.labels_)), dtype=np.int64)
        for t in range(1, len(x)):
            choices = delta[:, None]+transition
            back[t] = np.argmax(choices, axis=0)
            delta = np.max(choices, axis=0)+emission[t]
        last = int(np.argmax(delta+p['end']))
        score = float(delta[last]+p['end'][last])
        if not np.isfinite(score):
            raise ImpossibleSequenceError('no finite legal path')
        path = np.empty(len(x), dtype=np.int64)
        path[-1] = last
        for t in range(len(x)-1, 0, -1):
            path[t-1] = back[t, path[t]]
        return path, score

    def predict(self, features, *, length=None):
        return [self.labels_[i] for i in self.decode(features, length=length)[0]]

    def fit(self, sequences, labels, *, lengths=None):
        s.integer(self.max_iter, 'max_iter', 1, 200)
        s.scalar(self.learning_rate, 'learning_rate', 1e-8, 1.)
        s.scalar(self.l2, 'l2', 0., 10.)
        s.scalar(self.tolerance, 'tolerance', 0., .1)
        if not isinstance(sequences, (list, tuple)) or not 1 <= len(sequences) <= 32 or not isinstance(labels, (list, tuple)) or len(labels) != len(sequences):
            raise ValueError('aligned lists of1..32 feature/label sequences required')
        if lengths is None:
            lengths = [None]*len(sequences)
        if not isinstance(lengths, (list, tuple)) or len(lengths) != len(sequences):
            raise ValueError('one optional active length per sequence required')
        data = [self._features(x, length) for x, length in zip(sequences, lengths)]
        targets = [self._labels(y, len(x)) for x, y in zip(data, labels)]
        if sum(map(len, data)) > 1024 or self.max_iter*sum(map(len, data))*(self.n_features*len(self.labels_)+len(self.labels_)**2) > 2e7:
            raise ValueError('CRF training work budget exceeded')
        p = {name: np.zeros_like(a) for name, a in self._parameters().items()}
        def objective(q):
            value = .5*self.l2*sum(float(np.sum(a*a)) for a in q.values())
            gradient = {name: self.l2*a for name, a in q.items()}
            for x, y in zip(data, targets):
                loss, g = self._loss(x, y, q)
                value += loss/len(data)
                for name in gradient:
                    gradient[name] = gradient[name]+g[name]/len(data)
            if not np.isfinite(value) or any(not np.isfinite(a).all() for a in gradient.values()):
                raise FloatingPointError('nonfinite CRF training objective/gradient')
            return float(value), gradient
        value, gradient = objective(p)
        history, status, converged, steps = [value], 'iteration-budget', False, 0
        for iteration in range(self.max_iter):
            if max(np.max(np.abs(a)) for a in gradient.values()) <= self.tolerance:
                status, converged = 'gradient-tolerance', True
                break
            rate = self.learning_rate
            for _ in range(32):
                candidate = {name: p[name]-rate*gradient[name] for name in p}
                self._parameters(candidate)
                trial, trial_gradient = objective(candidate)
                if trial <= value:
                    break
                rate *= .5
            else:
                status = 'line-search-stagnation'
                break
            p, value, gradient = candidate, trial, trial_gradient
            history.append(value)
            steps += 1
        self.parameters_ = {name: a.copy() for name, a in p.items()}
        self.loss_history_ = np.array(history)
        self.status_, self.converged_, self.n_iter_ = status, converged, steps
        return self
