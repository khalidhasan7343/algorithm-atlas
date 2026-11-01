"""Genuine positive-cooccurrence weighted log-bilinear GloVe objective and training."""
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


def cooccurrence_matrix(sentences, vocab_size, *, window=2, symmetric=True):
    """Ordered target/context counts weighted by inverse token distance."""
    vocab_size = s.integer(vocab_size, 'vocab_size', 1, 128)
    window = s.integer(window, 'window', 1, 4)
    symmetric = s.boolean(symmetric, 'symmetric')
    if not isinstance(sentences, (list, tuple)) or not 1 <= len(sentences) <= 64:
        raise ValueError('1..64 encoded sentences required')
    data = []
    for sentence in sentences:
        a = np.asarray(sentence)
        mixed_bool = not isinstance(sentence, np.ndarray) and any(isinstance(v, (bool, np.bool_)) for v in np.asarray(sentence, dtype=object).flat)
        if a.ndim != 1 or len(a) > 128 or mixed_bool or (len(a) and (a.dtype.kind not in 'iu' or np.any(a < 0) or np.any(a >= vocab_size))):
            raise ValueError('bounded integer token IDs in the vocabulary required')
        data.append(a.astype(np.int64))
    if sum(map(len, data)) > 2048:
        raise ValueError('at most2048 corpus tokens')
    X = np.zeros((vocab_size, vocab_size))
    for row in data:
        for i in range(len(row)):
            end = min(len(row), i+window+1) if symmetric else i
            for j in range(max(0, i-window), end):
                if j != i:
                    X[row[i], row[j]] += 1./abs(i-j)
    return X


def weighting(counts, *, x_max=10., alpha=.75):
    x_max = s.scalar(x_max, 'x_max', 1e-6, 1e6)
    alpha = s.scalar(alpha, 'alpha', .001, 1.)
    a = np.asarray(counts)
    if a.dtype.kind not in 'iuf' or a.size > 16384 or not np.isfinite(a).all() or np.any(a < 0) or np.any(a > 1e6) or np.any((a > 0) & (a < 1e-12)):
        raise ValueError('counts must be zero or finite in[1e-12,1e6]')
    return np.minimum((a.astype(float)/x_max)**alpha, 1.)


def glove_loss_gradients(parameters, cooccurrences, *, x_max=10., alpha=.75):
    """Sum f(X)*(W C^T+b+c-log X)^2 over strictly positive X cells."""
    if not isinstance(parameters, dict) or set(parameters) != {'W', 'C', 'b', 'c'}:
        raise ValueError('parameters require W,C,b,c')
    W = s.finite_matrix(parameters['W'], 'W', rows=128, cols=16)
    C = s.finite_matrix(parameters['C'], 'C', rows=128, cols=16)
    if W.shape != C.shape:
        raise ValueError('target/context embedding shapes must agree')
    biases = []
    for name in ('b', 'c'):
        a = np.asarray(parameters[name])
        if a.shape != (len(W),) or a.dtype.kind not in 'iuf' or not np.isfinite(a).all() or np.any(np.abs(a) > 1e6):
            raise ValueError('finite bounded bias vector required')
        biases.append(a.astype(float))
    X = s.finite_matrix(cooccurrences, 'cooccurrences', rows=128, cols=128)
    if X.shape != (len(W), len(W)) or np.any(X < 0) or not np.any(X > 0):
        raise ValueError('square nonnegative cooccurrences with a positive cell required')
    weights = weighting(X, x_max=x_max, alpha=alpha)
    i, j = np.nonzero(X)
    residual = np.sum(W[i]*C[j], axis=1)+biases[0][i]+biases[1][j]-np.log(X[i, j])
    loss = float(np.sum(weights[i, j]*residual**2))
    delta = 2*weights[i, j]*residual
    gradients = {'W': np.zeros_like(W), 'C': np.zeros_like(C), 'b': np.zeros(len(W)), 'c': np.zeros(len(W))}
    np.add.at(gradients['W'], i, delta[:, None]*C[j])
    np.add.at(gradients['C'], j, delta[:, None]*W[i])
    np.add.at(gradients['b'], i, delta)
    np.add.at(gradients['c'], j, delta)
    if not np.isfinite(loss) or any(not np.isfinite(g).all() for g in gradients.values()):
        raise ValueError('nonfinite GloVe objective or gradient')
    return loss, gradients


class GloVe:
    """Global weighted least-squares embeddings; bounded full-batch gradient descent."""
    def __init__(self, dimension=8, *, window=2, symmetric=True, x_max=10., alpha=.75,
                 epochs=100, learning_rate=.1, random_state=0, min_count=1,
                 max_size=128, lowercase=True, gradient_clip=5.):
        self.dimension, self.window, self.symmetric = dimension, window, symmetric
        self.x_max, self.alpha, self.epochs = x_max, alpha, epochs
        self.learning_rate, self.random_state = learning_rate, random_state
        self.min_count, self.max_size, self.lowercase = min_count, max_size, lowercase
        self.gradient_clip = gradient_clip
        self._settings()

    def _settings(self):
        s.integer(self.dimension, 'dimension', 1, 16)
        s.integer(self.window, 'window', 1, 4)
        s.boolean(self.symmetric, 'symmetric')
        s.scalar(self.x_max, 'x_max', 1e-6, 1e6)
        s.scalar(self.alpha, 'alpha', .001, 1.)
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
        if len(vocab)**2*self.dimension*self.epochs > 20000000:
            raise ValueError('GloVe dense training work budget exceeded')
        X = cooccurrence_matrix([vocab.encode(text) for text in texts], len(vocab), window=self.window, symmetric=self.symmetric)
        if not np.any(X):
            raise ValueError('training requires a sentence containing at least two tokens')
        rng = np.random.default_rng(self.random_state)
        p = {'W': rng.normal(0., .1, (len(vocab), self.dimension)), 'C': rng.normal(0., .1, (len(vocab), self.dimension)), 'b': np.zeros(len(vocab)), 'c': np.zeros(len(vocab))}
        if vocab.counts_[0] == 0:
            p['W'][0] = p['C'][0] = 0.
        initial = {key: value.copy() for key, value in p.items()}
        loss, gradient = glove_loss_gradients(p, X, x_max=self.x_max, alpha=self.alpha)
        history, status, updates = [loss], 'iteration-budget', 0
        for _ in range(self.epochs):
            rate, accepted = self.learning_rate, False
            if all(not np.any(g) for g in gradient.values()):
                status = 'stationary-gradient'
                break
            for _ in range(30):
                candidate, _ = neural.step(p, gradient, rate, self.gradient_clip)
                candidate_loss, candidate_gradient = glove_loss_gradients(candidate, X, x_max=self.x_max, alpha=self.alpha)
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
        self.target_embeddings_, self.context_embeddings_ = p['W'].copy(), p['C'].copy()
        self.embeddings_ = (p['W']+p['C']).copy()
        self.target_bias_, self.context_bias_ = p['b'].copy(), p['c'].copy()
        self.cooccurrences_ = X.copy()
        self.loss_history_ = np.array(history)
        self.objective_history_ = self.loss_history_.copy()
        self.n_iter_, self.n_updates_, self.optimization_status_ = updates, updates, status
        self.converged_ = status == 'stationary-gradient'
        return self

    def get_embeddings(self, *, combine=True):
        s.ready(self)
        s.boolean(combine, 'combine')
        return (self.parameters_['W']+self.parameters_['C'] if combine else self.parameters_['W']).copy()

    def embedding(self, word, *, combine=True):
        s.ready(self)
        ids = self.vocab_.encode(word)
        if len(ids) != 1:
            raise ValueError('embedding lookup requires one tokenizer token')
        return self.get_embeddings(combine=combine)[ids[0]].copy()
