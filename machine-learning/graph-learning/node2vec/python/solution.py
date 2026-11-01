"""Weighted undirected Node2Vec walks and fixed-sample full-batch SGNS training."""
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


def _indices(value, name, n, columns=None):
    a = np.asarray(value)
    if (a.ndim != 2 or a.dtype.kind not in 'iu' or len(a) > 20000
            or not 1 <= a.shape[1] <= (columns or 8) or (columns is not None and a.shape[1] != columns)
            or np.any(a < 0) or np.any(a >= n)):
        raise ValueError(f'{name}: bounded integer node-index matrix required')
    return np.array(a, dtype=np.int64, copy=True)


def context_pairs(walks, window_size):
    """Ordered pairs from a fixed symmetric positional window, including revisits."""
    window = support.integer(window_size, 'window_size', 1, 8)
    if not isinstance(walks, (list, tuple)) or len(walks) > 640:
        raise ValueError('at most640 explicit walks required')
    validated = []
    for walk in walks:
        if not isinstance(walk, (list, tuple)) or not 1 <= len(walk) <= 64:
            raise ValueError('each walk requires1..64 node indices')
        validated.append([support.integer(x, 'node', 0, 31) for x in walk])
    if sum(map(len, validated)) * 2 * window > 20000:
        raise ValueError('conservative pair budget exceeds20000')
    pairs = [(walk[i], walk[j]) for walk in validated for i in range(len(walk))
             for j in range(max(0, i - window), min(len(walk), i + window + 1)) if i != j]
    return np.array(pairs, dtype=np.int64).reshape(-1, 2)


def sgns_loss_gradients(input_embeddings, output_embeddings, pairs, negatives):
    """Mean [softplus(-positive logit)+sum softplus(negative logits)]."""
    U = support.array(input_embeddings, 'input_embeddings', max_cells=512)
    V = support.array(output_embeddings, 'output_embeddings', max_cells=512)
    if U.shape != V.shape or not 1 <= len(U) <= 32 or not 1 <= U.shape[1] <= 16:
        raise ValueError('matching n-by-d embeddings,n1..32,d1..16 required')
    pairs = _indices(pairs, 'pairs', len(U), 2)
    negatives = _indices(negatives, 'negatives', len(U))
    if len(pairs) == 0 or len(negatives) != len(pairs) or negatives.shape[1] > 8:
        raise ValueError('nonempty pairs with1..8 negatives per pair required')
    centers, contexts = pairs.T
    target = U[centers]
    positive = np.einsum('ij,ij->i', target, V[contexts])
    negative = np.einsum('ij,ikj->ik', target, V[negatives])
    loss = float(np.mean(np.logaddexp(0., -positive) + np.logaddexp(0., negative).sum(axis=1)))
    pos_delta = (.5 * (1 + np.tanh(positive / 2)) - 1) / len(pairs)
    neg_delta = .5 * (1 + np.tanh(negative / 2)) / len(pairs)
    gU, gV = np.zeros_like(U), np.zeros_like(V)
    np.add.at(gU, centers, pos_delta[:, None] * V[contexts] + np.einsum('ik,ikj->ij', neg_delta, V[negatives]))
    np.add.at(gV, contexts, pos_delta[:, None] * target)
    np.add.at(gV, negatives.ravel(), (neg_delta[:, :, None] * target[:, None, :]).reshape(-1, U.shape[1]))
    return loss, dict(input=gU, output=gV)


def _transition(A, current, previous, p, q):
    candidates = np.flatnonzero(A[current] > 0)
    probabilities = np.zeros(len(A))
    if len(candidates):
        weights = A[current, candidates].copy()
        weights /= weights.max()  # Preserve tiny common edge scales before biasing.
        if previous is not None:
            bias = np.where(candidates == previous, 1 / p,
                            np.where(A[previous, candidates] > 0, 1., 1 / q))
            weights *= bias
        probabilities[candidates] = weights / weights.sum()
    return probabilities


class Node2Vec:
    """Fixed sampled SGNS objective; transductive node-index embeddings only."""

    def __init__(self, dimensions=4, walk_length=8, num_walks=4, p=1., q=1.,
                 window_size=2, negative_samples=3, epochs=100,
                 learning_rate=.5, random_state=0, gradient_clip=5.):
        self.dimensions, self.walk_length, self.num_walks = dimensions, walk_length, num_walks
        self.p, self.q, self.window_size = p, q, window_size
        self.negative_samples, self.epochs = negative_samples, epochs
        self.learning_rate, self.random_state, self.gradient_clip = learning_rate, random_state, gradient_clip
        self._settings()

    def _settings(self):
        for name, high in [('dimensions',16), ('walk_length',64), ('num_walks',20),
                           ('window_size',8), ('negative_samples',8), ('epochs',500)]:
            support.integer(getattr(self, name), name, 1, high)
        support.integer(self.random_state, 'random_state', 0, 2**32 - 1)
        support.real(self.p, 'p', 1e-3, 1e3)
        support.real(self.q, 'q', 1e-3, 1e3)
        support.real(self.learning_rate, 'learning_rate', 1e-6, 1.)
        support.real(self.gradient_clip, 'gradient_clip', 1e-6, 1000.)

    def transition_probabilities(self, graph, current, previous=None):
        self._settings()
        A = support.adjacency(graph, undirected=True, zero_diagonal=True)
        current = support.integer(current, 'current', 0, len(A) - 1)
        if previous is not None:
            previous = support.integer(previous, 'previous', 0, len(A) - 1)
            if A[previous, current] == 0:
                raise ValueError('previous→current must be an existing edge')
        return _transition(A, current, previous, self.p, self.q)

    def _walks(self, A, rng):
        walks = []
        for _ in range(int(self.num_walks)):
            for root in rng.permutation(len(A)):
                walk = [int(root)]
                for _ in range(int(self.walk_length) - 1):
                    probabilities = _transition(A, walk[-1], walk[-2] if len(walk) > 1 else None, self.p, self.q)
                    if not np.any(probabilities):
                        break
                    walk.append(int(rng.choice(len(A), p=probabilities)))
                walks.append(walk)
        return walks

    def generate_walks(self, graph):
        self._settings()
        A = support.adjacency(graph, undirected=True, zero_diagonal=True)
        return self._walks(A, np.random.default_rng(self.random_state))

    def fit(self, graph):
        self._settings()
        A = support.adjacency(graph, undirected=True, zero_diagonal=True)
        pair_bound = len(A) * int(self.num_walks) * int(self.walk_length) * 2 * int(self.window_size)
        if pair_bound > 20000 or pair_bound * int(self.epochs) * (int(self.negative_samples) + 1) * int(self.dimensions) > 20000000:
            raise ValueError('conservative pair/training operation budget exceeded')
        rng = np.random.default_rng(self.random_state)
        walks = self._walks(A, rng)
        pairs = context_pairs(walks, self.window_size)
        if not len(pairs):
            raise ValueError('at least one positive target/context pair is required')
        counts = np.bincount(pairs[:, 1], minlength=len(A)).astype(float)
        noise = counts ** .75
        noise /= noise.sum()
        parameters = {key:rng.normal(0., .1, (len(A), int(self.dimensions))) for key in ('input', 'output')}
        initial = parameters['input'].copy()
        negatives = rng.choice(len(A), size=(len(pairs), int(self.negative_samples)), p=noise)
        loss, gradients = sgns_loss_gradients(parameters['input'], parameters['output'], pairs, negatives)
        history = [loss]
        for _ in range(int(self.epochs)):
            parameters, norm = support.step(parameters, gradients, self.learning_rate, self.gradient_clip)
            loss, gradients = sgns_loss_gradients(parameters['input'], parameters['output'], pairs, negatives)
            history.append(loss)
        self.__dict__.update(parameters_=parameters, embeddings_=parameters['input'].copy(),
                             context_embeddings_=parameters['output'].copy(), initial_embeddings_=initial,
                             adjacency_=A, walks_=walks, positive_pairs_=pairs, negative_indices_=negatives,
                             noise_distribution_=noise, loss_history_=np.array(history), n_updates_=int(self.epochs),
                             last_update_gradient_norm_=norm, converged_=False, optimization_status_='epoch-budget')
        return self

    def transform(self, nodes=None):
        if not hasattr(self, 'embeddings_'):
            raise ValueError('successful fit required')
        if nodes is None:
            return self.embeddings_.copy()
        raw = np.asarray(nodes)
        if raw.ndim == 1 and raw.size == 0:
            return self.embeddings_[:0].copy()
        if raw.ndim != 1 or raw.dtype.kind not in 'iu' or len(raw) > 32 or np.any(raw < 0) or np.any(raw >= len(self.embeddings_)):
            raise ValueError('at most32 known integer node IDs required')
        return self.embeddings_[raw].copy()

    def fit_transform(self, graph):
        return self.fit(graph).transform()
