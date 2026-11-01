import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec = importlib.util.spec_from_file_location('atlas_b11_support', Path(__file__).resolve().parents[2]/'support.py')
s = sys.modules.get(_spec.name)
if s is None:
    s = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = s
    _spec.loader.exec_module(s)

class ImpossibleSequenceError(ValueError):
    """The current model gives the sequence probability zero."""


def logsumexp(values, axis=None):
    values = np.asarray(values, dtype=float)
    maximum = np.max(values, axis=axis, keepdims=True)
    safe = np.where(np.isfinite(maximum), maximum, 0.)
    with np.errstate(divide='ignore', under='ignore'):
        total = safe+np.log(np.sum(np.exp(values-safe), axis=axis, keepdims=True))
    return np.squeeze(total, axis=axis) if axis is not None else float(total.item())


def _probability(value, shape, name):
    a = np.asarray(value)
    if a.shape != shape or a.dtype.kind not in 'iuf':
        raise ValueError(name+' probability shape/type differs')
    a = np.array(a, dtype=float, copy=True)
    if not np.isfinite(a).all() or np.any(a < 0) or np.any(a > 1) or not np.allclose(a.sum(axis=-1), 1., atol=1e-12, rtol=0):
        raise ValueError(name+' probabilities must be nonnegative and sum to one')
    return a


class CategoricalHMM:
    """Discrete categorical HMM with log inference and pure-ML Baum-Welch."""
    def __init__(self, n_states, n_symbols, *, initial=None, transition=None, emission=None, random_state=0):
        self.n_states = s.integer(n_states, 'n_states', 1, 8)
        self.n_symbols = s.integer(n_symbols, 'n_symbols', 1, 16)
        self.random_state = s.integer(random_state, 'random_state', 0, 2**32-1)
        supplied = (initial is not None, transition is not None, emission is not None)
        if any(supplied) and not all(supplied):
            raise ValueError('supply all initial/transition/emission probabilities together')
        k, m = self.n_states, self.n_symbols
        if not any(supplied):
            rng = np.random.default_rng(self.random_state)
            initial = rng.dirichlet(np.ones(k))
            transition = rng.dirichlet(np.ones(k), size=k)
            emission = rng.dirichlet(np.ones(m), size=k)
        self.initial_ = _probability(initial, (k,), 'initial')
        self.transition_ = _probability(transition, (k, k), 'transition')
        self.emission_ = _probability(emission, (k, m), 'emission')
        self.status_, self.converged_, self.n_iter_ = 'initialized', None, 0

    def _observations(self, observations):
        a = np.asarray(observations)
        if a.ndim != 1 or not 1 <= len(a) <= 2048 or a.dtype.kind not in 'iu':
            raise ValueError('1..2048 integer observation codes required')
        if np.any(a < 0) or np.any(a >= self.n_symbols):
            raise ValueError('unknown observation symbol')
        return a.astype(np.int64, copy=True)

    def _logs(self):
        with np.errstate(divide='ignore'):
            return np.log(self.initial_), np.log(self.transition_), np.log(self.emission_)

    def forward(self, observations):
        obs = self._observations(observations)
        pi, transition, emission = self._logs()
        alpha = np.empty((len(obs), self.n_states))
        alpha[0] = pi+emission[:, obs[0]]
        for t in range(1, len(obs)):
            alpha[t] = logsumexp(alpha[t-1, :, None]+transition, axis=0)+emission[:, obs[t]]
        return alpha

    def backward(self, observations):
        obs = self._observations(observations)
        _, transition, emission = self._logs()
        beta = np.zeros((len(obs), self.n_states))
        for t in range(len(obs)-2, -1, -1):
            beta[t] = logsumexp(transition+emission[:, obs[t+1]][None, :]+beta[t+1][None, :], axis=1)
        return beta

    def score(self, observations):
        return logsumexp(self.forward(observations)[-1])

    def infer(self, observations):
        obs = self._observations(observations)
        alpha, beta = self.forward(obs), self.backward(obs)
        likelihood = logsumexp(alpha[-1])
        if not np.isfinite(likelihood):
            raise ImpossibleSequenceError('posterior undefined for zero-likelihood sequence')
        _, transition, emission = self._logs()
        gamma = np.exp(alpha+beta-likelihood)
        gamma /= gamma.sum(axis=1, keepdims=True)
        xi = np.empty((len(obs)-1, self.n_states, self.n_states))
        for t in range(len(obs)-1):
            values = alpha[t, :, None]+transition+emission[:, obs[t+1]][None, :]+beta[t+1][None, :]-likelihood
            xi[t] = np.exp(values)
            xi[t] /= xi[t].sum()
        return dict(log_likelihood=likelihood, log_forward=alpha.copy(), log_backward=beta.copy(), gamma=gamma.copy(), xi=xi.copy())

    def decode(self, observations):
        obs = self._observations(observations)
        pi, transition, emission = self._logs()
        delta = np.empty((len(obs), self.n_states))
        parent = np.zeros((len(obs), self.n_states), dtype=int)
        delta[0] = pi+emission[:, obs[0]]
        for t in range(1, len(obs)):
            candidates = delta[t-1, :, None]+transition
            parent[t] = np.argmax(candidates, axis=0)
            delta[t] = np.max(candidates, axis=0)+emission[:, obs[t]]
        path = np.empty(len(obs), dtype=int)
        path[-1] = int(np.argmax(delta[-1]))
        value = float(delta[-1, path[-1]])
        if not np.isfinite(value):
            raise ImpossibleSequenceError('no possible Viterbi path')
        for t in range(len(obs)-1, 0, -1):
            path[t-1] = parent[t, path[t]]
        return path.copy(), value

    def fit(self, sequences, *, max_iter=100, tolerance=1e-6):
        if not isinstance(sequences, (tuple, list)) or not 1 <= len(sequences) <= 16:
            raise ValueError('fit requires a list of1..16 independent sequences')
        data = [self._observations(obs) for obs in sequences]
        total = sum(len(obs) for obs in data)
        max_iter = s.integer(max_iter, 'max_iter', 1, 200)
        tolerance = s.scalar(tolerance, 'tolerance', 1e-12, 1.)
        if total > 4096 or max_iter*total*self.n_states**2 > 2e7:
            raise ValueError('HMM training work budget exceeded')
        model = CategoricalHMM(self.n_states, self.n_symbols, initial=self.initial_, transition=self.transition_, emission=self.emission_, random_state=self.random_state)
        likelihood = float(sum(model.score(obs) for obs in data))
        if not np.isfinite(likelihood):
            raise ImpossibleSequenceError('cannot train on an impossible sequence')
        history = [likelihood]
        status, converged = 'iteration-budget', False
        for iteration in range(1, max_iter+1):
            first = np.zeros(self.n_states)
            transitions = np.zeros_like(model.transition_)
            emissions = np.zeros_like(model.emission_)
            for obs in data:
                posterior = model.infer(obs)
                first += posterior['gamma'][0]
                transitions += posterior['xi'].sum(axis=0)
                for symbol in range(self.n_symbols):
                    emissions[:, symbol] += posterior['gamma'][obs == symbol].sum(axis=0)
            initial = first/first.sum()
            transition, emission = model.transition_.copy(), model.emission_.copy()
            for state in range(self.n_states):
                if transitions[state].sum() > 0:
                    transition[state] = transitions[state]/transitions[state].sum()
                if emissions[state].sum() > 0:
                    emission[state] = emissions[state]/emissions[state].sum()
            candidate = CategoricalHMM(self.n_states, self.n_symbols, initial=initial, transition=transition, emission=emission, random_state=self.random_state)
            updated = float(sum(candidate.score(obs) for obs in data))
            if not np.isfinite(updated) or updated < likelihood-1e-9*(1+abs(likelihood)):
                raise s.NumericalError('EM likelihood became invalid or decreased beyond roundoff tolerance')
            improvement = updated-likelihood
            model, likelihood = candidate, updated
            history.append(likelihood)
            if abs(improvement) <= tolerance*(1+abs(likelihood)):
                status, converged = 'likelihood-tolerance', True
                break
        self.initial_, self.transition_, self.emission_ = model.initial_.copy(), model.transition_.copy(), model.emission_.copy()
        self.log_likelihood_history_ = np.array(history)
        self.status_, self.converged_, self.n_iter_ = status, converged, iteration
        return self
