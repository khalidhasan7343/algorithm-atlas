import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec = importlib.util.spec_from_file_location('atlas_b12_support', Path(__file__).resolve().parents[2]/'support.py')
s = sys.modules.get(_spec.name)
if s is None:
    s = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = s
    _spec.loader.exec_module(s)

def project_capped_simplex(values, cap):
    """Euclidean projection onto sum(a)=1,0<=a<=cap via monotone shift root."""
    vector = np.asarray(values)
    if vector.ndim != 1 or not 1 <= len(vector) <= 256 or vector.dtype.kind not in 'iuf':
        raise ValueError('projection requires1..256 real coordinates')
    vector = np.array(vector, dtype=float, copy=True)
    if not np.isfinite(vector).all() or np.any(np.abs(vector) > 100):
        raise ValueError('projection coordinate magnitude must be<=100')
    cap = s.scalar(cap, 'simplex cap', 1/len(vector), 1e4)
    if cap == 1/len(vector):
        return np.full(len(vector), 1/len(vector))
    effective_cap = min(cap, 1.)  # Nonnegativity+unit sum already imply each coordinate<=1.
    centered = vector-vector.max()
    low, high = float(np.min(centered-effective_cap)), 0.
    for _ in range(96):
        shift = low+(high-low)/2
        result = np.clip(centered-shift, 0., effective_cap)
        if result.sum() > 1:
            low = shift
        else:
            high = shift
    result = np.clip(centered-(low+(high-low)/2), 0., effective_cap)
    if abs(result.sum()-1) > 1e-10:
        raise s.NumericalError('capped-simplex root did not meet feasibility tolerance')
    return result


def _feasibility(alpha, cap):
    return max(abs(float(alpha.sum())-1), float(np.max(np.maximum(-alpha, 0))), float(np.max(np.maximum(alpha-cap, 0))))


def _pair_gap(alpha, gradient, cap):
    increase = np.flatnonzero(alpha < cap)
    decrease = np.flatnonzero(alpha > 0)
    if not len(increase) or not len(decrease):
        return 0., None, None
    i = int(increase[np.argmin(gradient[increase])])
    j = int(decrease[np.argmax(gradient[decrease])])
    return max(0., float(gradient[j]-gradient[i])), i, j


def _certificate(K, alpha, cap):
    gradient = K@alpha
    bound_tolerance = min(1e-10, cap*1e-7)
    lower = alpha <= bound_tolerance
    upper = alpha >= cap-bound_tolerance
    free = ~(lower | upper)
    low = float(np.max(gradient[upper])) if np.any(upper) else -np.inf
    high = float(np.min(gradient[lower])) if np.any(lower) else np.inf
    if np.any(free):
        rho = float(np.mean(gradient[free]))
    elif np.isfinite(low) and np.isfinite(high):
        rho = low/2+high/2
    elif np.isfinite(low):
        rho = low
    elif np.isfinite(high):
        rho = high
    else:
        raise s.NumericalError('no KKT-consistent rho candidates')
    violations = np.zeros(len(alpha))
    violations[lower] = np.maximum(rho-gradient[lower], 0)
    violations[upper] = np.maximum(gradient[upper]-rho, 0)
    violations[free] = np.abs(gradient[free]-rho)
    norm_squared = float(alpha@gradient)
    primal = .5*norm_squared+cap*float(np.maximum(rho-gradient, 0).sum())-rho
    dual = -.5*norm_squared
    return dict(gradient=gradient, rho=rho, rho_bounds=(low, high), free=free,
                pair_gap=_pair_gap(alpha, gradient, cap)[0], kkt_residual=float(np.max(violations)),
                feasibility=_feasibility(alpha, cap), objective=.5*norm_squared,
                primal=primal, dual=dual, primal_dual_gap=primal-dual)


class OneClassSVM(s.Detector):
    """RBF one-class dual solved by bounded feasible exact pair-coordinate transfers."""
    def __init__(self, nu=.1, *, gamma=None, kernel='rbf', tolerance=1e-7, max_iter=10000):
        self.nu = s.scalar(nu, 'nu', 1e-4, 1.)
        self.gamma = None if gamma is None else s.scalar(gamma, 'gamma', 1e-12, 1e12)
        if kernel != 'rbf':
            raise ValueError('only the PSD RBF kernel is supported')
        self.kernel = kernel
        self.tolerance = s.scalar(tolerance, 'tolerance', 1e-12, 1.)
        self.max_iter = s.integer(max_iter, 'max_iter', 1, 20000)

    def fit(self, X):
        X = s.features(X, fitting=True)
        nu = s.scalar(self.nu, 'nu', 1e-4, 1.)
        gamma = 1/X.shape[1] if self.gamma is None else s.scalar(self.gamma, 'gamma', 1e-12, 1e12)
        tolerance = s.scalar(self.tolerance, 'tolerance', 1e-12, 1.)
        budget = s.integer(self.max_iter, 'max_iter', 1, 20000)
        if len(X)*budget > 3_000_000:
            raise ValueError('sample/iteration product exceeds3e6')
        if self.kernel != 'rbf':
            raise ValueError('only RBF kernel supported')
        cap = 1/(nu*len(X))
        K = s.kernel(X, X, gamma)
        alpha = project_capped_simplex(np.zeros(len(X)), cap)
        gradient = K@alpha
        history = [.5*float(alpha@gradient)]
        feasibility = [_feasibility(alpha, cap)]
        status, updates = 'iteration-budget', 0
        for _ in range(budget):
            gap, i, j = _pair_gap(alpha, gradient, cap)
            if gap <= tolerance:
                gradient = K@alpha
                gap, i, j = _pair_gap(alpha, gradient, cap)
                if gap <= tolerance:
                    status = 'kkt-tolerance'
                    break
            curvature = float(K[i, i]+K[j, j]-2*K[i, j])
            limit = min(cap-alpha[i], alpha[j])
            transfer = limit if curvature <= 0 else min(limit, gap/curvature)
            mass = float(alpha[i]+alpha[j])
            new_i = float(np.clip(alpha[i]+transfer, max(0., mass-cap), min(cap, mass)))
            new_j = mass-new_i
            di, dj = new_i-alpha[i], new_j-alpha[j]
            if di == 0 and dj == 0:
                status = 'numerical-stagnation'
                break
            alpha[i], alpha[j] = new_i, new_j
            gradient += di*K[:, i]+dj*K[:, j]
            updates += 1
            if updates % 50 == 0:
                gradient = K@alpha
            residual = _feasibility(alpha, cap)
            if residual > 1e-10:
                raise s.NumericalError('pair transfer violated capped-simplex feasibility')
            objective = .5*float(alpha@gradient)
            if not np.isfinite(objective) or objective > history[-1]+1e-10:
                raise s.NumericalError('dual objective increased beyond roundoff')
            history.append(objective)
            feasibility.append(residual)
        certificate = _certificate(K, alpha, cap)
        if certificate['feasibility'] > 1e-10 or certificate['primal_dual_gap'] < -1e-9:
            raise s.NumericalError('invalid final dual/primal certificate')
        converged = bool(max(certificate['pair_gap'], certificate['kkt_residual']) <= tolerance)
        if converged:
            status = 'kkt-tolerance'
        elif status == 'kkt-tolerance':
            status = 'certificate-not-met'
        history[-1] = certificate['objective']
        rho = certificate['rho']
        decision = self._boundary(certificate['gradient']-rho, certificate['gradient'], rho)
        self.n_features_in_, self.n_samples_ = X.shape[1], len(X)
        self.X_fit_, self.gamma_, self.cap_, self.alpha_, self.gram_ = X.copy(), gamma, cap, alpha.copy(), K.copy()
        self.rho_, self.threshold_, self.rho_bounds_ = rho, -rho, certificate['rho_bounds']
        self.support_ = np.flatnonzero(alpha > 0)
        self.support_vectors_, self.dual_coef_ = X[self.support_].copy(), alpha[self.support_][None, :].copy()
        self.free_support_ = np.flatnonzero(certificate['free'])
        self.anomaly_scores_, self.labels_ = -certificate['gradient'].copy(), s.labels_from_decision(decision)
        self.objective_history_, self.feasibility_history_ = np.array(history), np.array(feasibility)
        self.kkt_residual_, self.pair_gap_, self.feasibility_residual_ = certificate['kkt_residual'], certificate['pair_gap'], certificate['feasibility']
        self.objective_, self.primal_, self.dual_, self.primal_dual_gap_ = certificate['objective'], certificate['primal'], certificate['dual'], certificate['primal_dual_gap']
        self.status_, self.converged_, self.n_iter_ = status, converged, updates
        return self

    @staticmethod
    def _boundary(decision, score, rho):
        # Only machine-roundoff-sized boundary differences become exact zero.
        tolerance = 32*np.finfo(float).eps*(1+np.abs(score)+abs(rho))
        return np.where(np.abs(decision) <= tolerance, 0., decision)

    def score_samples(self, X):
        X = self._query(X)
        return s.kernel(X, self.X_fit_, self.gamma_)@self.alpha_

    def anomaly_scores(self, X):
        return -self.score_samples(X)

    def decision_function(self, X):
        score = self.score_samples(X)
        return self._boundary(score-self.rho_, score, self.rho_)

    def predict(self, X):
        return s.labels_from_decision(self.decision_function(X))
