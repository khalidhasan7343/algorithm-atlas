"""Shared bounded array contracts and canonical imports; no estimator wrappers."""
from functools import lru_cache
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parent

@lru_cache(None)
def module_at(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = sys.modules.get(name)
    if module is None:
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return module

classification = module_at('atlas_b5_classification_support', ROOT.parents[1]/'supervised-learning/classification/support.py')
integer, scalar = classification.integer, classification.scalar
numerical, ConvergenceError = classification.numerical, classification.ConvergenceError
encode_labels = classification.encode_labels


def features(X, *, fitting=False, expected=None, max_samples=512):
    return classification.features(X, fitting=fitting, expected=expected,
                                   max_samples=max_samples if fitting else 4096, max_features=32)


def latent_features(Z, expected):
    """Latent coordinates can exceed input units; validate finite real arrays only."""
    a = np.asarray(Z)
    if a.ndim != 2 or a.shape[1] != expected or len(a)>4096 or a.dtype.kind not in 'iuf':
        raise ValueError('latent array must be real 2D with fitted component count')
    a = np.array(a,dtype=np.float64,copy=True)
    if not np.isfinite(a).all():
        raise ValueError('latent coordinates must be finite')
    return a


def centered(X):
    mean = X[0] + np.mean(X-X[0], axis=0)
    return X-mean, mean


def uniform_scale(X):
    value = float(np.max(np.abs(X)))
    return value if value else 1.0


def squared_distances(X):
    # Direct differences avoid cancellation in ||x||² + ||y||² - 2<x,y>.
    return np.array([np.sum((X-row)**2, axis=1) for row in X])


def orient(U, V):
    for j in range(len(V)):
        i = np.argmax(np.abs(V[j]))
        if V[j, i] < 0:
            V[j] *= -1; U[:, j] *= -1
    return U, V


class Projection:
    def fit_transform(self, X, y=None):
        return self.fit(X, y).transform(X)

    def _query(self, X):
        if not hasattr(self, 'n_features_in_'):
            raise ValueError('fit must succeed before transform')
        return features(X, expected=self.n_features_in_)


@lru_cache(None)
def load(name):
    if name == 'vanilla-autoencoders':
        path = ROOT.parents[1]/'deep-learning/vanilla-autoencoders/python/solution.py'
    else:
        if name not in {'principal-component-analysis','singular-value-decomposition',
                        'linear-discriminant-analysis-projection','independent-component-analysis','t-sne','umap'}:
            raise ValueError('unknown canonical topic')
        path = ROOT/name/'python/solution.py'
    return module_at('atlas_b5_'+name.replace('-', '_'), path)


def optimize(initial, objective_gradient, max_iter, learning_rate, tol):
    """Bounded full gradients with Armijo backtracking; report budget exhaustion."""
    Y = initial.copy()
    value, grad = objective_gradient(Y)
    history = [float(value)]
    status = 'budget-exhausted'
    for iteration in range(max_iter):
        norm = float(np.linalg.norm(grad))
        if norm <= tol:
            status = 'gradient-tolerance'; break
        step = learning_rate
        for _ in range(60):
            candidate = Y-step*grad
            new_value, new_grad = objective_gradient(candidate)
            if np.isfinite(new_value) and new_value <= value - 1e-4*step*norm**2:
                break
            step *= .5
        else:
            raise ConvergenceError('backtracking failed to resolve a descent step')
        Y, value, grad = candidate, new_value, new_grad
        history.append(float(value))
    norm = float(np.linalg.norm(grad))
    if norm <= tol:
        status = 'gradient-tolerance'
    return Y, dict(objective_history_=np.array(history), n_iter_=len(history)-1,
                   gradient_norm_=norm, converged_=norm<=tol, optimization_status_=status)


def main(estimator):
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict) or 'X' not in data or set(data)-{'X','y','parameters'}:
            raise ValueError('JSON requires X and optional y/parameters')
        params = data.get('parameters', {})
        if not isinstance(params, dict):
            raise ValueError('parameters must be an object')
        model = estimator(**params)
        embedding = model.fit_transform(data['X'], data.get('y'))
        result = dict(embedding=embedding.tolist())
        if hasattr(model, 'optimization_status_'):
            result['optimization_status'] = model.optimization_status_
        print(json.dumps(result, allow_nan=False))
    except (TypeError, ValueError, ConvergenceError) as error:
        print('error: '+str(error), file=sys.stderr)
        raise SystemExit(2)
