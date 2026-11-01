"""Tanh-MLP DQN with FIFO uniform replay and hard target-network snapshots."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec = importlib.util.spec_from_file_location('atlas_b8_support', Path(__file__).resolve().parents[2] / 'support.py')
support = sys.modules.get(_spec.name)
if support is None:
    support = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = support
    _spec.loader.exec_module(support)


@support.numerical
def td_targets(target_parameters, next_x, rewards, terminated, gamma):
    values, _ = support.forward(target_parameters, next_x)
    r = support.array(rewards, 1, (len(values),))
    done = support.flags(terminated, len(values))
    gamma = support.scalar(gamma, 'discount', 0, 1)
    return r + gamma * (~done) * values.max(1)


@support.numerical
def loss_gradients(parameters, observations, actions, targets):
    values, _ = support.forward(parameters, observations)
    a = support.actions(actions, len(values), values.shape[1])
    y = support.array(targets, 1, (len(values),))
    residual = values[np.arange(len(values)), a] - y
    delta = np.zeros_like(values)
    delta[np.arange(len(values)), a] = residual / len(values)
    return float(.5 * np.mean(residual ** 2)), support.backward(parameters, observations, delta)[0]


class DQN:
    def __init__(self, inputs=1, n_actions=2, hidden=8, learning_rate=.05, gamma=.9,
                 epsilon=.2, capacity=512, batch_size=16, target_interval=10, seed=0):
        self.rng = np.random.default_rng(support.integer(seed, 'seed', 0, 2 ** 32 - 1))
        self.online = support.initialize(inputs, n_actions, self.rng, hidden)
        self.target = support.copy(self.online)
        self.inputs, self.n_actions = inputs, n_actions
        self.learning_rate = support.scalar(learning_rate, 'learning rate', 0, 1, positive=True)
        self.gamma = support.scalar(gamma, 'discount', 0, 1)
        self.epsilon = support.scalar(epsilon, 'epsilon', 0, 1)
        self.replay = support.Replay(capacity)
        self.batch_size = support.integer(batch_size, 'batch size', 1, capacity)
        self.target_interval = support.integer(target_interval, 'target interval', 1, 1000)
        self.updates_ = 0
        self.loss_history_ = []

    def sync(self):
        support.finite(self.online)
        self.target = support.copy(self.online)

    def action(self, observation, explore=True):
        support.boolean(explore)
        x = support.array(observation, 1, (self.inputs,))
        q = support.forward(self.online, x[None, :])[0][0]
        return support.epsilon_action(q, self.epsilon if explore else 0., self.rng)

    def step(self):
        if self.updates_ >= 10000:
            raise ValueError('gradient update budget exceeded')
        x, a, r, next_x, done, _ = self.replay.sample(self.batch_size, self.rng)
        y = td_targets(self.target, next_x, r, done, self.gamma)
        loss, gradient = loss_gradients(self.online, x, a, y)
        support.apply(self.online, gradient, self.learning_rate)
        self.updates_ += 1
        if self.updates_ % self.target_interval == 0:
            self.sync()
        self.loss_history_.append(loss)
        return loss

    def train(self, env, episodes=200, max_steps=64):
        support.budget(episodes, max_steps)
        self.returns_ = []
        for _ in range(episodes):
            x = support.array(env.reset(seed=int(self.rng.integers(2 ** 31))), 1, (self.inputs,))
            total = 0.
            for index in range(max_steps):
                a = self.action(x)
                next_x, reward, terminal, truncated, _ = env.step(a)
                support.boolean(terminal)
                support.boolean(truncated)
                self.replay.add(x, a, reward, next_x, terminal, truncated or index + 1 == max_steps)
                if len(self.replay.data) >= self.batch_size:
                    self.step()
                x = support.array(next_x, 1, (self.inputs,))
                total += reward
                if terminal or truncated:
                    break
            self.returns_.append(float(total))
        self.optimization_status_ = 'fixed-budget-completed'
        return self
