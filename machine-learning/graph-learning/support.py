"""Bounded graph/data validation and loading; algorithm mathematics stays local."""
from functools import lru_cache
import importlib.util
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parent
TOPICS = ('pagerank', 'node2vec', 'graph-convolutional-networks')


def integer(value, name, low, high):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise ValueError(f'{name} must be an integer')
    if not low <= value <= high:
        raise ValueError(f'{name} must be in {low}..{high}')
    return int(value)


def real(value, name, low, high, *, open_low=False, open_high=False):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, float, np.integer, np.floating)):
        raise ValueError(f'{name} must be a finite real number')
    try:
        value = float(value)
    except (OverflowError, ValueError) as error:
        raise ValueError(f'{name} must fit finite float64') from error
    if (not np.isfinite(value) or not low <= value <= high
            or (open_low and value == low) or (open_high and value == high)):
        raise ValueError(f'{name} outside supported range')
    return value


def boolean(value, name):
    if type(value) is not bool:
        raise ValueError(f'{name} must be bool')
    return value


def array(value, name, *, ndim=2, max_cells=32768):
    try:
        raw = np.asarray(value)
    except (ValueError, TypeError) as error:
        raise ValueError(f'{name} must be a rectangular numeric array') from error
    if raw.ndim != ndim or raw.dtype.kind not in 'iuf' or raw.size > max_cells:
        raise ValueError(f'{name}: real numeric rank-{ndim} array within cell budget required')
    result = np.array(raw, dtype=np.float64, copy=True)
    if not np.isfinite(result).all() or np.any(np.abs(result) > 1e6):
        raise ValueError(f'{name}: finite magnitudes <=1e6 required')
    return result


def adjacency(graph, *, undirected=False, zero_diagonal=False):
    A = array(graph, 'adjacency', max_cells=1024)
    if A.shape[0] != A.shape[1] or not 1 <= len(A) <= 32 or np.any(A < 0):
        raise ValueError('nonnegative square adjacency with 1..32 nodes required')
    if undirected and not np.array_equal(A, A.T):
        raise ValueError('exactly symmetric undirected adjacency required')
    if zero_diagonal and np.any(np.diag(A) != 0):
        raise ValueError('zero input diagonal required; do not pre-add self loops')
    return A


def features(value, n, width=None):
    X = array(value, 'features', max_cells=512)
    if len(X) != n or not 1 <= X.shape[1] <= 16 or (width is not None and X.shape[1] != width):
        raise ValueError('features require n rows and 1..16 matching columns')
    return X


def step(parameters, gradients, learning_rate, gradient_clip):
    largest = max(float(np.max(np.abs(g))) for g in gradients.values())
    norm = largest * np.sqrt(sum(float(np.sum((g / largest) ** 2)) for g in gradients.values())) if largest else 0.
    scale = min(1., gradient_clip / norm) if norm else 1.
    updated = {k: value - learning_rate * scale * gradients[k] for k, value in parameters.items()}
    if any(not np.isfinite(v).all() or np.any(np.abs(v) > 1e6) for v in updated.values()):
        raise ValueError('parameter update exceeds finite magnitude budget')
    return updated, norm


@lru_cache(None)
def module_at(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = sys.modules.get(name)
    if module is None:
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return module


def load(topic):
    if topic not in TOPICS:
        raise ValueError('unknown B9 canonical')
    return module_at('atlas_b9_' + topic.replace('-', '_'), ROOT / topic / 'python/solution.py')


def b7_gnn():
    """Reuse the approved normalization utility without changing its source."""
    return module_at('atlas_b9_preserved_b7_gnn', ROOT.parent / 'deep-learning/graph-neural-networks/python/solution.py')
