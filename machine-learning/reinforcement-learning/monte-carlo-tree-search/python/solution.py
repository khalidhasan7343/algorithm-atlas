"""UCT Monte Carlo tree search for deterministic, single-agent terminal planning.

Model callbacks are pure and prompt: terminal(state), legal_actions(state),
transition(state, action), outcome(terminal_state). No adversarial sign changes,
chance nodes, intermediate rewards or discounting are implied by this API.
"""
from dataclasses import dataclass, field
from itertools import islice
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


@dataclass
class Node:
    state: object
    parent: object = None
    action: object = None
    untried: list = field(default_factory=list)
    children: dict = field(default_factory=dict)
    visits: int = 0
    value_sum: float = 0.

    @property
    def mean(self):
        return self.value_sum / self.visits if self.visits else 0.


def legal(model, state):
    terminal = support.boolean(model.terminal(state))
    # Inspect only one element beyond the allowed branching bound.
    actions = list(islice(model.legal_actions(state),33))
    if len(actions) > 32:
        raise ValueError('at most32 unique integer legal actions required')
    for action in actions:
        support.integer(action, 'legal action', 0, 31)
    if len(actions) != len(set(actions)):
        raise ValueError('at most32 unique integer legal actions required')
    if (terminal and actions) or (not terminal and not actions):
        raise ValueError('terminal/legal action contract mismatch')
    return sorted(actions)


def uct(node, parent_visits, exploration=np.sqrt(2.)):
    support.integer(parent_visits, 'parent visits', 1, 10000)
    exploration = support.scalar(exploration, 'exploration', 0, 100)
    if node.visits == 0:
        return float('inf')
    support.scalar(node.value_sum, 'value sum', -1e10, 1e10)
    return float(node.mean + exploration * np.sqrt(np.log(parent_visits) / node.visits))


def backpropagate(node, outcome):
    reward = support.scalar(outcome, 'outcome')
    while node is not None:
        node.visits += 1
        node.value_sum += reward
        node = node.parent


def rollout(model, state, rng, remaining_depth):
    support.integer(remaining_depth, 'remaining depth', 0, 64)
    for _ in range(remaining_depth):
        options = legal(model, state)
        if not options:
            return support.scalar(model.outcome(state), 'outcome')
        action = options[int(rng.integers(len(options)))]
        state = model.transition(state, action)
    if support.boolean(model.terminal(state)):
        legal(model, state)
        return support.scalar(model.outcome(state), 'outcome')
    raise ValueError('rollout depth exhausted before a terminal outcome')


def search(model, state, iterations=200, max_depth=32, exploration=np.sqrt(2.), seed=0):
    support.integer(iterations, 'iterations', 1, 10000)
    support.integer(max_depth, 'max depth', 1, 64)
    support.scalar(exploration, 'exploration', 0, 100)
    rng = np.random.default_rng(support.integer(seed, 'seed', 0, 2 ** 32 - 1))
    root = Node(state, untried=legal(model, state))
    if not root.untried:
        support.scalar(model.outcome(state), 'terminal outcome')
        return None, root
    for _ in range(iterations):
        node, depth = root, 0
        # Selection follows UCT only through fully expanded internal nodes.
        while not node.untried and node.children:
            action = max(sorted(node.children), key=lambda a: uct(node.children[a], node.visits, exploration))
            node = node.children[action]
            depth += 1
            if depth > max_depth:
                raise ValueError('selection depth budget exceeded')
        # Expansion adds at most one node per iteration.
        if node.untried:
            if depth >= max_depth:
                raise ValueError('expansion depth budget exceeded')
            action = node.untried.pop(int(rng.integers(len(node.untried))))
            next_state = model.transition(node.state, action)
            child = Node(next_state, parent=node, action=action, untried=legal(model, next_state))
            node.children[action] = child
            node, depth = child, depth + 1
        outcome = rollout(model, node.state, rng, max_depth - depth)
        backpropagate(node, outcome)
    # Robust child: largest visits, then mean, then smallest action index.
    chosen = max(sorted(root.children), key=lambda a: (root.children[a].visits, root.children[a].mean))
    return chosen, root


class TinyPlanning:
    """Binary depth3 tree; only path111 has terminal reward1, all others0."""
    def terminal(self, state):
        return state[0] == 3

    def legal_actions(self, state):
        return [] if self.terminal(state) else [0, 1]

    def transition(self, state, action):
        if action not in self.legal_actions(state):
            raise ValueError('illegal planning action')
        return state[0] + 1, 2 * state[1] + action

    def outcome(self, state):
        if not self.terminal(state):
            raise ValueError('terminal state required for outcome')
        return float(state[1] == 7)
