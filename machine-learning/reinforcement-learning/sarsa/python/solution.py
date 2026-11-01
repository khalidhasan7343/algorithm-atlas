"""On-policy tabular SARSA; the sampled next action is reused at the next step."""
import importlib.util
from pathlib import Path
import sys

_spec = importlib.util.spec_from_file_location('atlas_b8_support', Path(__file__).resolve().parents[2] / 'support.py')
support = sys.modules.get(_spec.name)
if support is None:
    support = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = support
    _spec.loader.exec_module(support)


class SARSA(support.Tabular):
    @support.numerical
    def update(self, s, a, reward, next_s, next_a=None, terminated=False):
        self.transition(s, a, reward, next_s, terminated)
        if not terminated:
            support.integer(next_a, 'next action', 0, self.n_actions - 1)
        target = reward + (0. if terminated else self.gamma * self.q[next_s, next_a])
        value = self.q[s, a] + self.alpha * (target - self.q[s, a])
        support.finite(float(value))
        self.q[s, a] = value
        return float(value)

    def train(self, env, episodes=200, max_steps=64):
        support.integer(episodes, 'episodes', 1, 5000)
        support.integer(max_steps, 'max steps', 1, 256)
        if episodes * max_steps > 100000:
            raise ValueError('training step budget exceeded')
        self.returns_ = []
        for _ in range(episodes):
            s = self.state(env.reset(seed=int(self.rng.integers(2 ** 31))))
            a = self.action(s)
            total = 0.
            for _ in range(max_steps):
                next_s, reward, terminal, truncated, _ = env.step(a)
                support.boolean(terminal)
                support.boolean(truncated)
                # A truncated state still has a next on-policy action/value.
                next_a = None if terminal else self.action(next_s)
                self.update(s, a, reward, next_s, next_a, terminal)
                total += reward
                if terminal or truncated:
                    break
                s, a = next_s, next_a
            self.returns_.append(float(total))
        self.optimization_status_ = 'fixed-budget-completed'
        return self
