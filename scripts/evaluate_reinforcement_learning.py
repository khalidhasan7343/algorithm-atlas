"""Record modest multi-seed training and separate greedy/no-noise evaluation.

This is a diagnostic ledger, not a benchmark or convergence certificate.
"""
import importlib.util
import json
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('atlas_b8_support', ROOT / 'machine-learning/reinforcement-learning/support.py')
support = sys.modules.get(spec.name)
if support is None:
    support = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = support
    spec.loader.exec_module(support)


def main():
    records = []
    for seed in (201, 202, 203):
        for topic, cls in [('q-learning', 'QLearning'), ('sarsa', 'SARSA'),
                           ('deep-q-networks', 'DQN'), ('reinforce-policy-gradient', 'REINFORCE'),
                           ('advantage-actor-critic', 'A2C'), ('asynchronous-advantage-actor-critic', 'A3C'),
                           ('proximal-policy-optimization', 'PPO'), ('deep-deterministic-policy-gradient', 'DDPG')]:
            before = time.monotonic()
            factory = support.Chain if topic in {'q-learning', 'sarsa'} else support.Continuous if cls == 'DDPG' else support.Bandit
            model = getattr(support.load(topic), cls)(3, 2, seed=seed) if factory == support.Chain else getattr(support.load(topic), cls)(seed=seed)
            evaluation_before = support.evaluate(model, factory, episodes=100, seed=990)
            if factory == support.Chain:
                settings = dict(episodes=600, max_steps=16)
                model.train(factory(), **settings)
            elif cls == 'A2C':
                settings = dict(iterations=200, max_steps=1, envs=2)
                model.train(factory, **settings)
            elif cls == 'A3C':
                settings = dict(iterations=100, max_steps=1, workers=3)
                model.train(factory, **settings)
            elif cls == 'PPO':
                settings = dict(iterations=35, max_steps=1)
                model.train(factory, **settings)
            else:
                settings = dict(episodes=2400 if cls == 'DDPG' else 250 if cls == 'DQN' else 200, max_steps=1)
                model.train(factory(), **settings)
            record = dict(topic=topic, seed=seed, settings=settings, environment=factory.__name__,
                          evaluation_before=evaluation_before,
                          evaluation_after=support.evaluate(model, factory, episodes=100, seed=990),
                          evaluation_exploration='disabled; greedy/no-noise', evaluation_episodes=100,
                          training_last100_mean_return=float(np.mean(model.returns_[-100:])),
                          optimization_status=model.optimization_status_, elapsed_seconds=round(time.monotonic() - before, 4))
            if hasattr(model, 'updates_'):
                record['updates'] = model.updates_
            if cls == 'A3C':
                record.update(workers_alive=model.workers_alive_, workers=model.workers_created_,
                              ordering='asynchronous nondeterministic; seed is not an ordering guarantee')
            records.append(record)
        mod = support.load('monte-carlo-tree-search')
        state = (0, 0)
        choices = []
        model = mod.TinyPlanning()
        while not model.terminal(state):
            action, tree = mod.search(model, state, iterations=200, max_depth=3, seed=seed)
            choices.append(dict(action=action, root_visits=tree.visits))
            state = model.transition(state, action)
        records.append(dict(topic='monte-carlo-tree-search', seed=seed, choices=choices, terminal_outcome=model.outcome(state)))
    path = ROOT / 'docs/reinforcement-learning-evidence/educational-training-results.json'
    path.write_text(json.dumps(dict(scope='small synthetic diagnostics only; no controlled benchmark superiority claim', records=records), indent=2) + '\n')
    print(f'{len(records)} seeded training/planning records saved to {path.relative_to(ROOT)}')
    for r in records:
        if r['topic'] == 'deep-deterministic-policy-gradient':
            print('DDPG', r['seed'], r['evaluation_before'], r['evaluation_after'])


if __name__ == '__main__':
    main()
