"""Episodic Monte Carlo REINFORCE, reward-to-go, no baseline/critic."""
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
def loss_gradients(parameters, observations, actions, returns, gamma=1.):
    # Episodic J=E[sum gamma^t r_t]: gamma^t weights accompany reward-to-go.
    gamma = support.scalar(gamma, 'discount', 0, 1)
    # policy_loss uses a mean; compensate to obtain the episodic SUM estimator
    # even when trajectory lengths differ.
    weights = support.array(returns, 1) * gamma ** np.arange(len(observations)) * len(observations)
    return support.policy_loss(parameters, observations, actions, weights)


class REINFORCE(support.DiscreteAgent):
    def train(self, env, episodes=200, max_steps=64):
        support.budget(episodes, max_steps)
        self.returns_, self.loss_history_ = [], []
        for _ in range(episodes):
            x, a, target, total = support.collect(self.actor, None, env, self.rng, max_steps, self.gamma)
            loss, gradient = loss_gradients(self.actor, x, a, target, self.gamma)
            support.apply(self.actor, gradient, self.learning_rate)
            self.returns_.append(total)
            self.loss_history_.append(loss)
        self.optimization_status_ = 'fixed-budget-completed'
        return self
