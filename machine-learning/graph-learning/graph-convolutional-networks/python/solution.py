"""Two-layer tanh GCN node classifier, masked cross-entropy and full backpropagation."""
import importlib.util
from pathlib import Path
import sys

import numpy as np

_spec = importlib.util.spec_from_file_location('atlas_b9_support', Path(__file__).resolve().parents[2] / 'support.py')
support = sys.modules.get(_spec.name)
if support is None:
    support = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = support
    _spec.loader.exec_module(support)


def normalize_adjacency(adjacency, self_loops=True):
    support.boolean(self_loops, 'self_loops')
    A = support.adjacency(adjacency, undirected=True, zero_diagonal=True)
    return support.b7_gnn().normalize_adjacency(A, len(A), self_loops)


def initialize(n_features, hidden_dim, n_classes, random_state=0):
    p = support.integer(n_features, 'n_features', 1, 16)
    h = support.integer(hidden_dim, 'hidden_dim', 1, 16)
    c = support.integer(n_classes, 'n_classes', 2, 8)
    support.integer(random_state, 'random_state', 0, 2**32 - 1)
    rng = np.random.default_rng(random_state)
    return dict(W1=rng.normal(0., np.sqrt(2/(p+h)), (p,h)), b1=np.zeros(h),
                W2=rng.normal(0., np.sqrt(2/(h+c)), (h,c)), b2=np.zeros(c))


def _data(parameters, features, propagation):
    S = support.array(propagation, 'propagation', max_cells=1024)
    if S.shape[0] != S.shape[1] or not 1 <= len(S) <= 32 or np.any(S < 0):
        raise ValueError('nonnegative square propagation matrix for1..32 nodes required')
    X = support.features(features, len(S))
    if not isinstance(parameters, dict) or set(parameters) != {'W1','b1','W2','b2'}:
        raise ValueError('exact W1,b1,W2,b2 parameter blocks required')
    p = {k:support.array(v, k, ndim=1 if k.startswith('b') else 2, max_cells=256) for k,v in parameters.items()}
    h = p['W1'].shape[1]
    if (p['W1'].shape[0] != X.shape[1] or not 1 <= h <= 16
            or p['b1'].shape != (h,) or p['W2'].shape[0] != h
            or not 2 <= p['W2'].shape[1] <= 8 or p['b2'].shape != (p['W2'].shape[1],)):
        raise ValueError('parameter dimensions do not match graph features/hidden/classes')
    return p, X, S


def _forward(p, X, S):
    aggregated = S @ X
    hidden = np.tanh(aggregated @ p['W1'] + p['b1'])
    messages = S @ hidden
    logits = messages @ p['W2'] + p['b2']
    return logits, (aggregated, hidden, messages)


def forward(parameters, features, normalized_adjacency):
    """Return node logits and backward cache for a caller-supplied propagation S."""
    return _forward(*_data(parameters, features, normalized_adjacency))


def _labels(labels, train_mask, n, n_classes=None):
    raw = np.asarray(labels)
    if raw.ndim != 1 or raw.shape != (n,) or raw.dtype.kind not in 'iu' or np.any(raw < -1) or np.any(raw > 7):
        raise ValueError('length-n integer labels in-1..7 required; -1 means unknown')
    y = np.array(raw, dtype=int, copy=True)
    if train_mask is None:
        mask = y >= 0
    else:
        mask = np.asarray(train_mask)
        if mask.dtype.kind != 'b' or mask.shape != (n,):
            raise ValueError('train_mask must be a boolean length-n vector')
        mask = mask.copy()
    if not np.any(mask) or np.any(y[mask] < 0):
        raise ValueError('training mask must select at least one known label')
    if n_classes is None:
        classes = np.unique(y[mask])
        if not 2 <= len(classes) <= 8 or not np.array_equal(classes, np.arange(len(classes))):
            raise ValueError('selected training labels must contain all classes0..C-1,C2..8')
        n_classes = len(classes)
    if np.any(y >= n_classes):
        raise ValueError('known labels outside fitted class range')
    return y, mask, int(n_classes)


def _loss_gradients(p, X, y, S, mask, l2):
    logits, (aggregated, hidden, messages) = _forward(p, X, S)
    shifted = logits - logits.max(axis=1, keepdims=True)
    weights = np.exp(shifted)
    probabilities = weights / weights.sum(axis=1, keepdims=True)
    rows = np.flatnonzero(mask)
    loss = float(np.mean(np.log(weights[rows].sum(axis=1)) - shifted[rows, y[rows]])
                 + .5*l2*(np.sum(p['W1']**2) + np.sum(p['W2']**2)))
    delta = probabilities.copy()
    delta[rows, y[rows]] -= 1
    delta[~mask] = 0
    delta /= len(rows)
    hidden_delta = (S.T @ (delta @ p['W2'].T)) * (1 - hidden**2)
    gradients = dict(W1=aggregated.T @ hidden_delta + l2*p['W1'], b1=hidden_delta.sum(axis=0),
                     W2=messages.T @ delta + l2*p['W2'], b2=delta.sum(axis=0))
    return loss, gradients


def loss_gradients(parameters, features, normalized_adjacency, labels, train_mask=None, l2=0.):
    p, X, S = _data(parameters, features, normalized_adjacency)
    l2 = support.real(l2, 'l2', 0., 1000.)
    y, mask, _ = _labels(labels, train_mask, len(X), p['W2'].shape[1])
    return _loss_gradients(p, X, y, S, mask, l2)


class GCNClassifier:
    """Tanh graph-convolution classifier; known unselected labels do not train."""

    def __init__(self, hidden_dim=4, epochs=200, learning_rate=.1, random_state=0,
                 self_loops=True, l2=0., gradient_clip=5.):
        self.hidden_dim, self.epochs, self.learning_rate = hidden_dim, epochs, learning_rate
        self.random_state, self.self_loops, self.l2, self.gradient_clip = random_state, self_loops, l2, gradient_clip
        self._settings()

    def _settings(self):
        support.integer(self.hidden_dim, 'hidden_dim', 1, 16)
        support.integer(self.epochs, 'epochs', 1, 2000)
        support.integer(self.random_state, 'random_state', 0, 2**32 - 1)
        support.boolean(self.self_loops, 'self_loops')
        support.real(self.learning_rate, 'learning_rate', 1e-6, 1.)
        support.real(self.l2, 'l2', 0., 1000.)
        support.real(self.gradient_clip, 'gradient_clip', 1e-6, 1000.)

    def fit(self, adjacency, features, labels, train_mask=None):
        self._settings()
        A = support.adjacency(adjacency, undirected=True, zero_diagonal=True)
        X = support.features(features, len(A))
        y, mask, classes = _labels(labels, train_mask, len(A))
        S = normalize_adjacency(A, self.self_loops)
        p = initialize(X.shape[1], self.hidden_dim, classes, self.random_state)
        loss, gradient = _loss_gradients(p, X, y, S, mask, self.l2)
        history = [loss]
        for _ in range(int(self.epochs)):
            p, norm = support.step(p, gradient, self.learning_rate, self.gradient_clip)
            loss, gradient = _loss_gradients(p, X, y, S, mask, self.l2)
            history.append(loss)
        self.__dict__.update(parameters_=p, classes_=np.arange(classes), n_features_in_=X.shape[1],
                             self_loops_=self.self_loops, normalized_adjacency_=S, train_mask_=mask,
                             loss_history_=np.array(history), n_updates_=int(self.epochs),
                             last_update_gradient_norm_=norm, converged_=False, optimization_status_='epoch-budget')
        return self

    def predict_proba(self, adjacency, features):
        if not hasattr(self, 'parameters_'):
            raise ValueError('successful fit required')
        A = support.adjacency(adjacency, undirected=True, zero_diagonal=True)
        X = support.features(features, len(A), self.n_features_in_)
        S = normalize_adjacency(A, self.self_loops_)
        logits, _ = _forward(self.parameters_, X, S)
        weights = np.exp(logits - logits.max(axis=1, keepdims=True))
        return weights / weights.sum(axis=1, keepdims=True)

    def predict(self, adjacency, features):
        probabilities = self.predict_proba(adjacency, features)
        return self.classes_[np.argmax(probabilities, axis=1)]
