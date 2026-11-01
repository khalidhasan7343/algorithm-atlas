"""Small RL numerical primitives and bounded diagnostic environments (NumPy only).

The canonical algorithms own their objectives and update rules. No autodiff,
agent framework, downloads, global RNG, or serialization is used here.
"""
from functools import lru_cache, wraps
import importlib.util
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parent
TOPICS = ('q-learning', 'sarsa', 'deep-q-networks', 'reinforce-policy-gradient',
          'advantage-actor-critic', 'asynchronous-advantage-actor-critic',
          'proximal-policy-optimization', 'deep-deterministic-policy-gradient',
          'monte-carlo-tree-search')


def integer(value, name, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f'{name} must be int in [{low}, {high}]')
    return value


def scalar(value, name, low=-1e6, high=1e6, positive=False):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, float, np.integer, np.floating)):
        raise ValueError(f'{name} must be finite real')
    value = float(value)
    if not np.isfinite(value) or not low <= value <= high or (positive and value == low):
        raise ValueError(f'{name} outside supported range')
    return value


def boolean(value):
    if type(value) is not bool:
        raise ValueError('termination/truncation flag must be bool')
    return value


def array(value, ndim=None, shape=None):
    raw = np.asarray(value)
    if raw.dtype.kind not in 'iuf' or (ndim is not None and raw.ndim != ndim):
        raise ValueError('real numeric array with correct rank required')
    if raw.size == 0 or raw.size > 65536 or any(d > 4096 for d in raw.shape):
        raise ValueError('array outside nonempty resource bounds')
    result = np.array(raw, dtype=float, copy=True)
    if shape is not None and result.shape != tuple(shape):
        raise ValueError('array shape mismatch')
    if not np.isfinite(result).all() or np.max(abs(result)) > 1e6:
        raise ValueError('finite array with magnitude <= 1e6 required')
    return result


def numerical(function):
    @wraps(function)
    def checked(*args, **kwargs):
        try:
            with np.errstate(over='raise', divide='raise', invalid='raise', under='ignore'):
                result = function(*args, **kwargs)
                finite(result)
                return result
        except (FloatingPointError, OverflowError) as error:
            raise ValueError('nonfinite computation; reduce input scale or learning rate') from error
    return checked


def finite(value):
    if isinstance(value, dict):
        for part in value.values():
            finite(part)
    elif isinstance(value, (tuple, list)):
        for part in value:
            finite(part)
    elif isinstance(value, (np.ndarray, float, np.floating)) and not np.isfinite(value).all():
        raise ValueError('nonfinite numerical state/output')


def copy(parameters):
    return {key: value.copy() for key, value in parameters.items()}


def initialize(inputs, outputs, rng, hidden=8):
    integer(inputs, 'inputs', 1, 32)
    integer(outputs, 'outputs', 1, 32)
    integer(hidden, 'hidden', 1, 32)
    return dict(W1=rng.normal(0, 1 / np.sqrt(inputs), (inputs, hidden)),
                b1=np.zeros(hidden), W2=rng.normal(0, .1, (hidden, outputs)),
                b2=np.zeros(outputs))


@numerical
def forward(parameters, observations):
    finite(parameters)
    x = array(observations, 2)
    if x.shape[1] != parameters['W1'].shape[0]:
        raise ValueError('observation feature count mismatch')
    hidden = np.tanh(x @ parameters['W1'] + parameters['b1'])
    return hidden @ parameters['W2'] + parameters['b2'], hidden


@numerical
def backward(parameters, observations, delta):
    output, hidden = forward(parameters, observations)
    x = array(observations, 2)
    delta = array(delta, 2, output.shape)
    dh = (delta @ parameters['W2'].T) * (1 - hidden ** 2)
    return dict(W1=x.T @ dh, b1=dh.sum(0), W2=hidden.T @ delta, b2=delta.sum(0)), dh @ parameters['W1'].T


@numerical
def apply(parameters, gradients, learning_rate, max_norm=10.):
    rate = scalar(learning_rate, 'learning rate', 0, 1, positive=True)
    cap = scalar(max_norm, 'gradient cap', 0, 1e4, positive=True)
    if parameters.keys() != gradients.keys() or any(parameters[k].shape != gradients[k].shape for k in parameters):
        raise ValueError('gradient keys/shapes mismatch')
    finite(parameters)
    finite(gradients)
    # Norm computed after scaling, avoiding overflow for large finite gradients.
    scale = max(float(np.max(abs(g))) for g in gradients.values())
    norm = scale * np.sqrt(sum(float(np.sum((g / scale) ** 2)) for g in gradients.values())) if scale else 0.
    multiplier = min(1., cap / norm) if norm else 1.
    updated = {key: value - rate * multiplier * gradients[key] for key, value in parameters.items()}
    finite(updated)
    parameters.update(updated)


@numerical
def log_softmax(logits):
    x = array(logits, 2)
    shifted = x - x.max(1, keepdims=True)
    return shifted - np.log(np.exp(shifted).sum(1, keepdims=True))


def actions(value, n, count):
    raw = np.asarray(value)
    if raw.shape != (n,) or raw.dtype.kind not in 'iu' or np.any(raw < 0) or np.any(raw >= count):
        raise ValueError('valid integer action vector required')
    return raw.astype(int, copy=True)


@numerical
def policy_loss(parameters, x, action, weights):
    logits, _ = forward(parameters, x)
    a = actions(action, len(logits), logits.shape[1])
    w = array(weights, 1, (len(logits),))
    logp = log_softmax(logits)
    delta = np.exp(logp)
    delta[np.arange(len(a)), a] -= 1
    delta *= w[:, None] / len(a)
    return float(-np.mean(logp[np.arange(len(a)), a] * w)), backward(parameters, x, delta)[0]


@numerical
def value_loss(parameters, x, targets):
    values, _ = forward(parameters, x)
    t = array(targets, 1, (len(values),))
    if values.shape[1] != 1:
        raise ValueError('scalar value head required')
    difference = values[:, 0] - t
    return float(.5 * np.mean(difference ** 2)), backward(parameters, x, difference[:, None] / len(t))[0]


@numerical
def returns(rewards, gamma, bootstrap=0.):
    r = array(rewards, 1)
    discount = scalar(gamma, 'discount', 0, 1)
    tail = scalar(bootstrap, 'bootstrap')
    result = np.empty_like(r)
    for index in range(len(r) - 1, -1, -1):
        tail = r[index] + discount * tail
        result[index] = tail
    return result


def epsilon_action(values, epsilon, rng):
    q = array(values, 1)
    chance = scalar(epsilon, 'epsilon', 0, 1)
    return int(rng.integers(len(q))) if rng.random() < chance else int(np.argmax(q))


class Tabular:
    def __init__(self, n_states, n_actions, alpha=.2, gamma=.9, epsilon=.1, seed=0):
        self.n_states = integer(n_states, 'states', 1, 4096)
        self.n_actions = integer(n_actions, 'actions', 1, 32)
        if n_states * n_actions > 65536:
            raise ValueError('Q-table cell limit exceeded')
        self.alpha = scalar(alpha, 'alpha', 0, 1)
        self.gamma = scalar(gamma, 'gamma', 0, 1)
        self.epsilon = scalar(epsilon, 'epsilon', 0, 1)
        self.rng = np.random.default_rng(integer(seed, 'seed', 0, 2 ** 32 - 1))
        self.q = np.zeros((n_states, n_actions))

    def state(self, s):
        return integer(s, 'state', 0, self.n_states - 1)

    def action(self, s, explore=True):
        boolean(explore)
        finite(self.q)
        return epsilon_action(self.q[self.state(s)], self.epsilon if explore else 0., self.rng)

    def policy(self):
        finite(self.q)
        return self.q.argmax(1).copy()

    def transition(self, s, a, reward, next_s, terminated):
        self.state(s)
        self.state(next_s)
        integer(a, 'action', 0, self.n_actions - 1)
        scalar(reward, 'reward')
        boolean(terminated)
        finite(self.q)
        scalar(self.alpha, 'alpha', 0, 1)
        scalar(self.gamma, 'gamma', 0, 1)


def sample(parameters, observation, rng):
    logits, _ = forward(parameters, array(observation, 1)[None, :])
    return int(rng.choice(logits.shape[1], p=np.exp(log_softmax(logits)[0])))


def budget(iterations, max_steps):
    integer(iterations, 'iterations/episodes', 1, 5000)
    integer(max_steps, 'max steps', 1, 256)
    if iterations * max_steps > 100000:
        raise ValueError('100000 interaction budget exceeded')


def flags(value, n):
    a = np.asarray(value)
    if a.shape != (n,) or a.dtype.kind != 'b':
        raise ValueError('boolean termination vector required')
    return a.copy()


class DiscreteAgent:
    def __init__(self, inputs=1, n_actions=2, hidden=8, learning_rate=.05, gamma=.9, seed=0):
        self.learning_rate = scalar(learning_rate, 'learning rate', 0, 1, positive=True)
        self.gamma = scalar(gamma, 'discount', 0, 1)
        self.rng = np.random.default_rng(integer(seed, 'seed', 0, 2 ** 32 - 1))
        self.actor = initialize(inputs, n_actions, self.rng, hidden)
        self.inputs, self.n_actions, self.hidden = inputs, n_actions, hidden

    def action(self, observation, explore=True):
        boolean(explore)
        x = array(observation, 1, (self.inputs,))
        if explore:
            return sample(self.actor, x, self.rng)
        return int(np.argmax(forward(self.actor, x[None, :])[0][0]))


def evaluate(agent, factory, episodes=20, seed=900, max_steps=64):
    """Separate greedy/no-noise episodes, returning mean reward and episode length."""
    budget(episodes, max_steps)
    rng = np.random.default_rng(integer(seed, 'seed', 0, 2 ** 32 - 1))
    rewards, lengths = [], []
    for _ in range(episodes):
        env = factory()
        x = env.reset(seed=int(rng.integers(2 ** 31)))
        total = 0.
        for step in range(max_steps):
            x, reward, terminal, truncated, _ = env.step(agent.action(x, explore=False))
            boolean(terminal)
            boolean(truncated)
            total += scalar(reward, 'reward')
            if terminal or truncated:
                break
        rewards.append(total)
        lengths.append(step + 1)
    return dict(mean_return=float(np.mean(rewards)), mean_length=float(np.mean(lengths)))


def collect(actor, critic, env, rng, max_steps, gamma):
    """One bounded trajectory; bootstrap truncation/budget cuts, never termination."""
    integer(max_steps, 'max steps', 1, 256)
    scalar(gamma, 'discount', 0, 1)
    x = array(env.reset(seed=int(rng.integers(2 ** 31))), 1)
    observations, chosen, rewards = [], [], []
    terminated = False
    for _ in range(max_steps):
        action = sample(actor, x, rng)
        next_x, reward, terminated, truncated, _ = env.step(action)
        boolean(terminated)
        boolean(truncated)
        observations.append(x)
        chosen.append(action)
        rewards.append(scalar(reward, 'reward'))
        x = array(next_x, 1, x.shape)
        if terminated or truncated:
            break
    tail = 0. if terminated or critic is None else float(forward(critic, x[None, :])[0][0, 0])
    if critic is None and not terminated:
        raise ValueError('Monte Carlo REINFORCE requires a complete terminal episode')
    return np.array(observations), np.array(chosen), returns(rewards, gamma, tail), float(sum(rewards))


class Replay:
    """Owned transitions; bounded FIFO, uniform sampling without replacement."""
    def __init__(self, capacity=512):
        self.capacity = integer(capacity, 'capacity', 1, 4096)
        self.data = []

    def add(self, observation, action, reward, next_observation, terminated, truncated=False):
        x = array(observation, 1)
        next_x = array(next_observation, 1, x.shape)
        a = action.copy() if isinstance(action, np.ndarray) else action
        if isinstance(a, np.ndarray):
            a = array(a, 1)
        else:
            integer(a, 'action', 0, 31)
        item = (x, a, scalar(reward, 'reward'), next_x, boolean(terminated), boolean(truncated))
        if len(self.data) == self.capacity:
            self.data.pop(0)
        self.data.append(item)

    def sample(self, size, rng):
        integer(size, 'sample size', 1, self.capacity)
        if size > len(self.data):
            raise ValueError('replay underflow')
        rows = [self.data[i] for i in rng.choice(len(self.data), size, replace=False)]
        return tuple(np.array(column) for column in zip(*rows))


class Chain:
    """States 0,1,2 (2 terminal); right advances, left retreats. Reward +1 at 2."""
    n_states, n_actions = 3, 2

    def __init__(self, horizon=16):
        self.horizon = integer(horizon, 'horizon', 1, 256)
        self.done = True

    def reset(self, seed=None):
        self.state, self.steps, self.done = 0, 0, False
        return self.state

    def step(self, action):
        integer(action, 'action', 0, 1)
        if self.done:
            raise ValueError('reset required after termination/truncation')
        self.state = min(2, self.state + 1) if action else max(0, self.state - 1)
        self.steps += 1
        terminated = self.state == 2
        truncated = self.steps >= self.horizon and not terminated
        self.done = terminated or truncated
        return self.state, float(terminated), terminated, truncated, {}


class Bandit:
    """One step, observation [1], actions 0/1 give rewards 0/1."""
    n_actions, observation_dim = 2, 1

    def reset(self, seed=None):
        self.done = False
        return np.ones(1)

    def step(self, action):
        integer(action, 'action', 0, 1)
        if getattr(self, 'done', True):
            raise ValueError('reset required')
        self.done = True
        return np.ones(1), float(action), True, False, {}


class Continuous:
    """One-step bounded control: x~U[-1,1], a in [-1,1], r=-(a-x/2)^2."""
    observation_dim, action_dim = 1, 1

    def reset(self, seed=None):
        self.x = np.random.default_rng(seed).uniform(-1, 1)
        self.done = False
        return np.array([self.x])

    def step(self, action):
        a = array(action, 1, (1,))
        if np.any(abs(a) > 1) or getattr(self, 'done', True):
            raise ValueError('action outside [-1,1] or reset required')
        self.done = True
        return np.array([self.x]), -float((a[0] - .5 * self.x) ** 2), True, False, {}


@lru_cache(None)
def load(topic):
    if topic not in TOPICS:
        raise ValueError('unknown RL topic')
    spec = importlib.util.spec_from_file_location('atlas_b8_' + topic.replace('-', '_'), ROOT / topic / 'python/solution.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
