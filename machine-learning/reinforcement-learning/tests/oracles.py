"""Test-only finite MDP oracle, independent of any canonical update helper."""
import numpy as np


def chain_model():
    p = np.zeros((3, 2, 3))
    r = np.zeros_like(p)
    for s in (0, 1):
        p[s, 0, max(0, s - 1)] = 1
        p[s, 1, s + 1] = 1
    p[2, :, 2] = 1
    r[1, 1, 2] = 1
    return p, r, np.array([False, False, True])


def value_iteration(p, r, terminal, gamma, tolerance=1e-12):
    values = np.zeros(len(p))
    for _ in range(10000):
        q = np.sum(p * (r + gamma * values[None, None, :] * (~terminal)[None, None, :]), axis=2)
        q[terminal] = 0
        new = q.max(1)
        if np.max(abs(new - values)) < tolerance:
            return new, q
        values = new
    raise AssertionError('test-only value iteration budget exhausted')
