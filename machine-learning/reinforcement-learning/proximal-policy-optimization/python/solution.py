"""Clipped categorical PPO with frozen n-step returns/advantages and minibatch SGD."""
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
base = support.load('advantage-actor-critic')


@support.numerical
def surrogate(new_logp, old_logp, advantage, clip=.2):
    new = support.array(new_logp, 1)
    old = support.array(old_logp, 1, new.shape)
    advantage = support.array(advantage, 1, new.shape)
    clip = support.scalar(clip, 'clip epsilon', 0, 1, positive=True)
    if np.any(new > 0) or np.any(old > 0):
        raise ValueError('log probabilities must be nonpositive')
    ratio = np.exp(new - old)
    clipped = np.clip(ratio, 1 - clip, 1 + clip)
    loss = -np.mean(np.minimum(ratio * advantage, clipped * advantage))
    active = ~(((advantage >= 0) & (ratio > 1 + clip)) | ((advantage < 0) & (ratio < 1 - clip)))
    dlogp = -advantage * ratio * active / len(ratio)
    return float(loss), dlogp, ratio


@support.numerical
def loss_gradients(actor, observations, actions, old_logp, advantage, clip=.2):
    logits, _ = support.forward(actor, observations)
    a = support.actions(actions, len(logits), logits.shape[1])
    logp = support.log_softmax(logits)
    loss, dlogp, ratio = surrogate(logp[np.arange(len(a)), a], old_logp, advantage, clip)
    delta = -np.exp(logp)
    delta[np.arange(len(a)), a] += 1
    delta *= dlogp[:, None]
    return loss, support.backward(actor, observations, delta)[0], ratio


class PPO(base.A2C):
    def train(self, factory=support.Bandit, iterations=50, max_steps=32, rollout_episodes=8,
              epochs=4, batch_size=8, clip=.2):
        support.budget(iterations, max_steps)
        support.integer(rollout_episodes, 'rollout episodes', 1, 32)
        support.integer(epochs, 'epochs', 1, 32)
        support.integer(batch_size, 'batch size', 1, 4096)
        support.scalar(clip, 'clip epsilon', 0, 1, positive=True)
        interactions = iterations * rollout_episodes * max_steps
        upper_updates = iterations * epochs * ((rollout_episodes * max_steps + batch_size - 1) // batch_size)
        if interactions > 100000 or upper_updates > 10000:
            raise ValueError('rollout or optimizer budget exceeded')
        self.returns_, self.loss_history_ = [], []
        self.updates_ = 0
        for _ in range(iterations):
            self.old_actor_ = support.copy(self.actor)
            old_critic = support.copy(self.critic)
            rows = []
            for _ in range(rollout_episodes):
                env = factory()
                try:
                    rows.append(support.collect(self.old_actor_, old_critic, env, self.rng, max_steps, self.gamma))
                finally:
                    if hasattr(env, 'close'):
                        env.close()
            x = np.concatenate([row[0] for row in rows])
            a = np.concatenate([row[1] for row in rows])
            targets = np.concatenate([row[2] for row in rows])
            advantage = targets - support.forward(old_critic, x)[0][:, 0]
            self.old_log_probs_ = support.log_softmax(support.forward(self.old_actor_, x)[0])[np.arange(len(a)), a].copy()
            self.rollout_observations_, self.rollout_actions_ = x.copy(), a.copy()
            for _ in range(epochs):
                order = self.rng.permutation(len(a))
                for start in range(0, len(a), batch_size):
                    index = order[start:start + batch_size]
                    al, ag, _ = loss_gradients(self.actor, x[index], a[index], self.old_log_probs_[index], advantage[index], clip)
                    cl, cg = support.value_loss(self.critic, x[index], targets[index])
                    actor, critic = support.copy(self.actor), support.copy(self.critic)
                    support.apply(actor, ag, self.learning_rate)
                    support.apply(critic, cg, self.learning_rate)
                    self.actor, self.critic = actor, critic
                    self.loss_history_.append((al, cl))
                    self.updates_ += 1
            self.returns_.append(float(np.mean([row[3] for row in rows])))
        self.optimization_status_ = 'fixed-budget-completed'
        return self
