"""Bounded Skip-Gram with Negative Sampling; no pretrained embeddings or delegates."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec = importlib.util.spec_from_file_location('atlas_b13_support', Path(__file__).resolve().parents[2]/'support.py')
s = sys.modules.get(_spec.name)
if s is None:
    s = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = s
    _spec.loader.exec_module(s)
neural = s.module('atlas_b7_support', s.ROOT.parent/'deep-learning/support.py')


def context_pairs(sentences, window=2):
    """Fixed symmetric windows; rows are (center, context), never cross sentences."""
    window = s.integer(window, 'window', 1, 4)
    if not isinstance(sentences, (list, tuple)) or not 1 <= len(sentences) <= 64:
        raise ValueError('1..64 encoded sentences required')
    data = []
    for sentence in sentences:
        a = np.asarray(sentence)
        mixed_bool = not isinstance(sentence, np.ndarray) and any(isinstance(v, (bool, np.bool_)) for v in np.asarray(sentence, dtype=object).flat)
        if a.ndim != 1 or len(a) > 128 or mixed_bool or (len(a) and (a.dtype.kind not in 'iu' or np.any(a < 0) or np.any(a >= 128))):
            raise ValueError('each sentence requires at most128 integer IDs in0..127')
        data.append(a.astype(np.int64))
    if sum(map(len, data)) > 2048:
        raise ValueError('at most2048 corpus tokens')
    pairs = [(int(row[i]), int(row[j])) for row in data for i in range(len(row))
             for j in range(max(0, i-window), min(len(row), i+window+1)) if i != j]
    return np.array(pairs, dtype=np.int64).reshape(-1, 2)


def noise_distribution(counts):
    """Normalized mapped-training unigram counts raised to3/4; zero stays zero."""
    a = np.asarray(counts)
    if a.ndim != 1 or not 1 <= len(a) <= 128 or a.dtype.kind not in 'iu' or np.any(a < 0) or np.any(a > 2048) or not np.any(a):
        raise ValueError('nonnegative bounded integer counts with positive total required')
    weights = a.astype(float)**.75
    return weights/weights.sum()


def sample_negatives(counts, pair_count, negative_samples=5, random_state=0):
    """Independent replacement draws; collisions/repeats are legitimate noise."""
    probabilities = noise_distribution(counts)
    pair_count = s.integer(pair_count, 'pair_count', 1, 16384)
    negative_samples = s.integer(negative_samples, 'negative_samples', 1, 8)
    random_state = s.integer(random_state, 'random_state', 0, 2**32-1)
    return np.random.default_rng(random_state).choice(len(probabilities), (pair_count, negative_samples), p=probabilities)


def sgns_loss_gradients(parameters, pairs, negative_ids):
    """Mean over positive pairs of positive softplus plus summed noise softplus."""
    if not isinstance(parameters, dict) or set(parameters) != {'W_in', 'W_out'}:
        raise ValueError('parameters require W_in and W_out')
    W = s.finite_matrix(parameters['W_in'], 'W_in', rows=128, cols=16)
    U = s.finite_matrix(parameters['W_out'], 'W_out', rows=128, cols=16)
    if W.shape != U.shape:
        raise ValueError('input/output embedding shapes must agree')
    pairs, negatives = np.asarray(pairs), np.asarray(negative_ids)
    if pairs.ndim != 2 or pairs.shape[1] != 2 or not 1 <= len(pairs) <= 16384 or pairs.dtype.kind not in 'iu':
        raise ValueError('1..16384 integer center/context pairs required')
    if negatives.ndim != 2 or negatives.shape[0] != len(pairs) or not 1 <= negatives.shape[1] <= 8 or negatives.dtype.kind not in 'iu':
        raise ValueError('one row of1..8 integer negative IDs per pair required')
    if np.any(pairs < 0) or np.any(pairs >= len(W)) or np.any(negatives < 0) or np.any(negatives >= len(W)):
        raise ValueError('embedding ID outside vocabulary')
    center, context = pairs.T
    source, positive, noise = W[center], U[context], U[negatives]
    z_positive = np.sum(source*positive, axis=1)
    z_negative = np.einsum('md,mkd->mk', source, noise)
    loss = float((np.logaddexp(0., -z_positive).sum()+np.logaddexp(0., z_negative).sum())/len(pairs))
    dp = (neural.sigmoid(z_positive)-1.)/len(pairs)
    dn = neural.sigmoid(z_negative)/len(pairs)
    gW, gU = np.zeros_like(W), np.zeros_like(U)
    np.add.at(gW, center, dp[:, None]*positive+np.einsum('mk,mkd->md', dn, noise))
    np.add.at(gU, context, dp[:, None]*source)
    np.add.at(gU, negatives.ravel(), (dn[:, :, None]*source[:, None, :]).reshape(-1, W.shape[1]))
    if not np.isfinite(loss) or not np.isfinite(gW).all() or not np.isfinite(gU).all():
        raise ValueError('nonfinite SGNS objective or gradient')
    return loss, {'W_in': gW, 'W_out': gU}


class Word2Vec:
    """Fixed-noise empirical SGNS with bounded, monotone full-batch gradient steps."""
    def __init__(self, dimension=8, *, window=2, negative_samples=5, epochs=100,
                 learning_rate=.3, random_state=0, min_count=1, max_size=128,
                 lowercase=True, gradient_clip=5.):
        self.dimension, self.window, self.negative_samples = dimension, window, negative_samples
        self.epochs, self.learning_rate, self.random_state = epochs, learning_rate, random_state
        self.min_count, self.max_size, self.lowercase = min_count, max_size, lowercase
        self.gradient_clip = gradient_clip
        self._settings()

    def _settings(self):
        s.integer(self.dimension, 'dimension', 1, 16)
        s.integer(self.window, 'window', 1, 4)
        s.integer(self.negative_samples, 'negative_samples', 1, 8)
        s.integer(self.epochs, 'epochs', 1, 200)
        s.scalar(self.learning_rate, 'learning_rate', 1e-6, 1.)
        s.integer(self.random_state, 'random_state', 0, 2**32-1)
        s.integer(self.min_count, 'min_count', 1, 2048)
        s.integer(self.max_size, 'max_size', 1, 128)
        s.boolean(self.lowercase, 'lowercase')
        s.scalar(self.gradient_clip, 'gradient_clip', 1e-6, 100.)

    def fit(self, texts):
        self._settings()
        vocab = s.Vocabulary(min_count=self.min_count, max_size=self.max_size, lowercase=self.lowercase).fit(texts)
        sentences = [vocab.encode(text) for text in texts]
        pairs = context_pairs(sentences, self.window)
        if not len(pairs):
            raise ValueError('training requires a sentence containing at least two tokens')
        if len(pairs)*(self.negative_samples+1)*self.dimension*self.epochs > 20000000:
            raise ValueError('SGNS training work budget exceeded')
        negatives = sample_negatives(vocab.counts_, len(pairs), self.negative_samples, self.random_state)
        rng = np.random.default_rng(self.random_state)
        p = {name: rng.normal(0., .1, (len(vocab), self.dimension)) for name in ('W_in', 'W_out')}
        if vocab.counts_[0] == 0:
            p['W_in'][0] = p['W_out'][0] = 0.
        initial = {key: value.copy() for key, value in p.items()}
        loss, gradient = sgns_loss_gradients(p, pairs, negatives)
        history, status, updates = [loss], 'iteration-budget', 0
        for _ in range(self.epochs):
            rate, accepted = self.learning_rate, False
            if all(not np.any(g) for g in gradient.values()):
                status = 'stationary-gradient'
                break
            for _ in range(30):
                candidate, _ = neural.step(p, gradient, rate, self.gradient_clip)
                candidate_loss, candidate_gradient = sgns_loss_gradients(candidate, pairs, negatives)
                if candidate_loss <= loss:
                    accepted = True
                    break
                rate *= .5
            if not accepted:
                status = 'line-search-stagnation'
                break
            p, loss, gradient = candidate, candidate_loss, candidate_gradient
            history.append(loss)
            updates += 1
        self.vocab_, self.vocabulary_ = vocab, dict(vocab.index_)
        self.parameters_, self.initial_parameters_ = p, initial
        self.input_embeddings_, self.output_embeddings_ = p['W_in'].copy(), p['W_out'].copy()
        self.embeddings_ = p['W_in'].copy()
        self.pairs_, self.negative_ids_ = pairs.copy(), negatives.copy()
        self.noise_distribution_ = noise_distribution(vocab.counts_)
        self.loss_history_ = np.array(history)
        self.objective_history_ = self.loss_history_.copy()
        self.n_iter_, self.n_updates_, self.optimization_status_ = updates, updates, status
        self.converged_ = status == 'stationary-gradient'
        return self

    def get_embeddings(self, *, combine=False):
        s.ready(self)
        s.boolean(combine, 'combine')
        return (self.parameters_['W_in']+self.parameters_['W_out'] if combine else self.parameters_['W_in']).copy()

    def embedding(self, word, *, combine=False):
        s.ready(self)
        ids = self.vocab_.encode(word)
        if len(ids) != 1:
            raise ValueError('embedding lookup requires one tokenizer token')
        return self.get_embeddings(combine=combine)[ids[0]].copy()
