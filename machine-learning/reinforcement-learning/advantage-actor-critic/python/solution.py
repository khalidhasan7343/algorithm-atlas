"""Synchronous n-step categorical actor-critic, separate tanh actor/value MLPs."""
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
def loss_gradients(actor, critic, observations, actions, targets):
    values = support.forward(critic, observations)[0][:, 0]
    targets = support.array(targets, 1, values.shape)
    # Stop-gradient advantage and bootstrapped return target.
    advantage = targets - values
    actor_loss, actor_gradient = support.policy_loss(actor, observations, actions, advantage)
    critic_loss, critic_gradient = support.value_loss(critic, observations, targets)
    return actor_loss, critic_loss, actor_gradient, critic_gradient


class A2C(support.DiscreteAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.critic = support.initialize(self.inputs, 1, self.rng, self.hidden)

    def train(self, factory=support.Bandit, iterations=200, max_steps=64, envs=2):
        support.budget(iterations, max_steps)
        support.integer(envs, 'environments', 1, 8)
        if iterations * max_steps * envs > 100000:
            raise ValueError('interaction budget exceeded')
        self.returns_, self.loss_history_ = [], []
        for _ in range(iterations):
            # All trajectories in this synchronous batch use unchanged actor/critic.
            rows = []
            for _ in range(envs):
                env = factory()
                try:
                    rows.append(support.collect(self.actor, self.critic, env, self.rng, max_steps, self.gamma))
                finally:
                    if hasattr(env, 'close'):
                        env.close()
            x = np.concatenate([row[0] for row in rows])
            a = np.concatenate([row[1] for row in rows])
            target = np.concatenate([row[2] for row in rows])
            actor_loss, critic_loss, ag, cg = loss_gradients(self.actor, self.critic, x, a, target)
            actor, critic = support.copy(self.actor), support.copy(self.critic)
            support.apply(actor, ag, self.learning_rate)
            support.apply(critic, cg, self.learning_rate)
            self.actor, self.critic = actor, critic
            self.returns_.append(float(np.mean([row[3] for row in rows])))
            self.loss_history_.append((actor_loss, critic_loss))
        self.optimization_status_ = 'fixed-budget-completed'
        return self
