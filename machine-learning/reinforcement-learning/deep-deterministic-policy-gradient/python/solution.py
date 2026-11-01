"""Continuous-action DDPG: tanh-bounded actor, neural Q critic, replay, soft targets."""
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


def bounds(low, high, count):
    low = support.array(low, 1, (count,))
    high = support.array(high, 1, (count,))
    if np.any(high <= low):
        raise ValueError('each action high bound must exceed low')
    return (high + low) / 2, (high - low) / 2


@support.numerical
def actor_forward(actor, observations, low, high):
    raw, hidden = support.forward(actor, observations)
    center, scale = bounds(low, high, raw.shape[1])
    return center + scale * np.tanh(raw), raw


@support.numerical
def critic_loss(critic, observations, actions, targets):
    x = support.array(observations, 2)
    a = support.array(actions, 2)
    if len(a) != len(x):
        raise ValueError('action/observation row mismatch')
    return support.value_loss(critic, np.column_stack([x, a]), targets)


@support.numerical
def actor_loss(actor, critic, observations, low, high):
    x = support.array(observations, 2)
    a, raw = actor_forward(actor, x, low, high)
    joined = np.column_stack([x, a])
    q = support.forward(critic, joined)[0]
    if q.shape[1] != 1:
        raise ValueError('scalar Q critic required')
    # Minimize -mean Q(s, mu(s)); critic parameters are held fixed.
    _, input_gradient = support.backward(critic, joined, -np.ones_like(q) / len(x))
    _, scale = bounds(low, high, a.shape[1])
    delta = input_gradient[:, x.shape[1]:] * scale * (1 - np.tanh(raw) ** 2)
    return float(-np.mean(q)), support.backward(actor, x, delta)[0]


@support.numerical
def td_targets(target_actor, target_critic, next_x, rewards, terminated, gamma, low, high):
    a = actor_forward(target_actor, next_x, low, high)[0]
    q = support.forward(target_critic, np.column_stack([next_x, a]))[0][:, 0]
    r = support.array(rewards, 1, q.shape)
    terminal = support.flags(terminated, len(q))
    gamma = support.scalar(gamma, 'discount', 0, 1)
    return r + gamma * (~terminal) * q


@support.numerical
def soft_update(target, online, tau):
    tau = support.scalar(tau, 'tau', 0, 1)
    support.finite(target)
    support.finite(online)
    if target.keys() != online.keys() or any(target[k].shape != online[k].shape for k in target):
        raise ValueError('target/online shape mismatch')
    updated = {k: tau * online[k] + (1 - tau) * target[k] for k in target}
    support.finite(updated)
    target.update(updated)


class DDPG:
    def __init__(self, inputs=1, action_dim=1, low=None, high=None, hidden=16,
                 learning_rate=.02, actor_learning_rate=.001, warmup_steps=128,
                 gamma=.9, tau=.05, noise=.3, capacity=512, batch_size=32, seed=0):
        self.inputs = support.integer(inputs, 'inputs', 1, 16)
        self.action_dim = support.integer(action_dim, 'action dim', 1, 16)
        self.low = support.array([-1.] * action_dim if low is None else low, 1, (action_dim,))
        self.high = support.array([1.] * action_dim if high is None else high, 1, (action_dim,))
        bounds(self.low, self.high, action_dim)
        self.rng = np.random.default_rng(support.integer(seed, 'seed', 0, 2 ** 32 - 1))
        self.actor = support.initialize(inputs, action_dim, self.rng, hidden)
        self.critic = support.initialize(inputs + action_dim, 1, self.rng, hidden)
        # Shift tanh units off their odd-symmetry center: a quadratic reward is
        # even in its action error, unlike a zero-bias tanh basis at initialization.
        self.critic['b1'] = self.rng.uniform(-.5, .5, hidden)
        self.target_actor, self.target_critic = support.copy(self.actor), support.copy(self.critic)
        self.learning_rate = support.scalar(learning_rate, 'learning rate', 0, 1, positive=True)
        self.actor_learning_rate = support.scalar(actor_learning_rate, 'actor learning rate', 0, 1, positive=True)
        self.warmup_steps = support.integer(warmup_steps, 'warmup steps', 0, 4096)
        self.gamma = support.scalar(gamma, 'discount', 0, 1)
        self.tau = support.scalar(tau, 'tau', 0, 1, positive=True)
        self.noise = support.scalar(noise, 'noise std', 0, 2)
        self.replay = support.Replay(capacity)
        self.batch_size = support.integer(batch_size, 'batch size', 1, capacity)
        self.updates_, self.interactions_, self.loss_history_ = 0, 0, []

    def action(self, observation, explore=True):
        support.boolean(explore)
        x = support.array(observation, 1, (self.inputs,))
        action = actor_forward(self.actor, x[None, :], self.low, self.high)[0][0]
        if explore:
            action += self.rng.normal(0, support.scalar(self.noise, 'noise', 0, 2), self.action_dim)
        return np.clip(action, self.low, self.high)

    def step(self, update_actor=True):
        support.boolean(update_actor)
        if self.updates_ >= 10000:
            raise ValueError('gradient update budget exceeded')
        x, a, r, next_x, done, _ = self.replay.sample(self.batch_size, self.rng)
        y = td_targets(self.target_actor, self.target_critic, next_x, r, done, self.gamma, self.low, self.high)
        cl, cg = critic_loss(self.critic, x, a, y)
        critic = support.copy(self.critic)
        support.apply(critic, cg, self.learning_rate)
        actor = support.copy(self.actor)
        al, ag = actor_loss(actor, critic, x, self.low, self.high)
        if update_actor:
            support.apply(actor, ag, self.actor_learning_rate)
        ta, tc = support.copy(self.target_actor), support.copy(self.target_critic)
        soft_update(ta, actor, self.tau)
        soft_update(tc, critic, self.tau)
        self.actor, self.critic, self.target_actor, self.target_critic = actor, critic, ta, tc
        self.updates_ += 1
        self.loss_history_.append((al, cl))
        return al, cl

    def train(self, env, episodes=2400, max_steps=1):
        support.budget(episodes, max_steps)
        self.returns_ = []
        for _ in range(episodes):
            x = support.array(env.reset(seed=int(self.rng.integers(2 ** 31))), 1, (self.inputs,))
            total = 0.
            for index in range(max_steps):
                a = self.rng.uniform(self.low, self.high) if self.interactions_ < self.warmup_steps else self.action(x)
                next_x, reward, terminal, truncated, _ = env.step(a)
                support.boolean(terminal)
                support.boolean(truncated)
                self.replay.add(x, a, reward, next_x, terminal, truncated or index + 1 == max_steps)
                self.interactions_ += 1
                if len(self.replay.data) >= self.batch_size:
                    self.step(update_actor=self.interactions_ >= self.warmup_steps)
                total += reward
                x = support.array(next_x, 1, (self.inputs,))
                if terminal or truncated:
                    break
            self.returns_.append(float(total))
        self.optimization_status_ = 'fixed-budget-completed'
        return self
