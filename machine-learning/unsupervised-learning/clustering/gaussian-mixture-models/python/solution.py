import importlib.util
from pathlib import Path
import sys

import numpy as np

if 'atlas_clustering_support' not in sys.modules:
    _spec = importlib.util.spec_from_file_location('atlas_clustering_support', Path(__file__).resolve().parents[2]/'support.py')
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = _module
    _spec.loader.exec_module(_module)
s = sys.modules['atlas_clustering_support']


def _evaluate(X, means, covariance, weights):
    """Full Gaussian log densities via Cholesky solves, then stable E-step."""
    scores = np.empty((len(X), len(weights)))
    for component in range(len(weights)):
        factor = s.classification.positive_definite_factor(covariance[component])
        residual = np.linalg.solve(factor, (X-means[component]).T)
        mahalanobis = np.sum(residual*residual, axis=0)
        logdet = 2*np.log(np.diag(factor)).sum()
        scores[:, component] = np.log(weights[component])-.5*(X.shape[1]*np.log(2*np.pi)+logdet+mahalanobis)
    s.finite(scores, 'Gaussian log density')
    maximum = scores.max(axis=1)
    exponentials = np.exp(scores-maximum[:, None])
    mass = exponentials.sum(axis=1)
    # Divide shifted exponentials directly. Subtracting a rounded huge negative
    # log-sum from every score could otherwise destroy row normalization.
    responsibilities = exponentials/mass[:, None]
    log_density = maximum+np.log(mass)
    return s.finite(log_density), s.finite(responsibilities)


class GaussianMixture(s.Clusterer):
    """Regularized full-covariance EM; bounded convergence and canonical K-Means init."""
    def __init__(self, n_components=1, *, reg_covar=1e-6, tol=1e-6,
                 max_iter=300, n_init=1, means_init=None, random_state=0):
        self.n_components = s.integer(n_components, 'n_components', 1, 32)
        self.reg_covar = s.scalar(reg_covar, 'reg_covar', low=1e-12)
        self.tol = s.scalar(tol, 'tol', high=1, positive=True)
        self.max_iter = s.integer(max_iter, 'max_iter', 1, 1000)
        self.n_init = s.integer(n_init, 'n_init', 1, 8)
        self.means_init = means_init
        self.random_state = s.seed(random_state)

    @s.numerical
    def fit(self, X):
        X = s.features(X, fitting=True)
        k = s.integer(self.n_components, 'n_components', 1, min(32, len(X)))
        regularization = s.scalar(self.reg_covar, 'reg_covar', low=1e-12)
        tolerance = s.scalar(self.tol, 'tol', high=1, positive=True)
        limit = s.integer(self.max_iter, 'max_iter', 1, 1000)
        repeats = s.integer(self.n_init, 'n_init', 1, 8)
        rng = np.random.default_rng(s.seed(self.random_state))
        supplied = None
        if self.means_init is not None:
            supplied = s.features(self.means_init, fitting=True, expected=X.shape[1])
            if supplied.shape != (k, X.shape[1]) or repeats != 1:
                raise ValueError('means_init needs shape (K,p) and n_init=1')
        centered = X-s.mean(X)
        initial_covariance = centered.T @ centered/len(X)+regularization*np.eye(X.shape[1])
        best = None
        failed = 0
        reason = 'iteration limit'
        for _ in range(repeats):
            if supplied is not None:
                means = supplied.copy()
            elif len(np.unique(X, axis=0)) >= k:
                try:
                    initializer = s.load('k-means').KMeans(k, n_init=1, random_state=int(rng.integers(2**32))).fit(X)
                except (s.ConvergenceError, ValueError) as error:
                    failed += 1
                    reason = 'K-Means initialization: '+str(error)
                    continue
                means = initializer.cluster_centers_.copy()
            else:
                # Mixture components may be identical; unlike K-Means, a valid
                # soft mixture need not have K distinct observed prototypes.
                means = X[rng.choice(len(X), k, replace=False)].copy()
            weights = np.full(k, 1/k)
            covariance = np.repeat(initial_covariance[None], k, axis=0)
            try:
                density, responsibilities = _evaluate(X, means, covariance, weights)
                history = [float(density.mean())]
                for iteration in range(1, limit+1):
                    count = responsibilities.sum(axis=0)
                    if np.any(count <= np.finfo(float).eps*len(X)):
                        raise s.ConvergenceError('component has numerically collapsed mass')
                    weights = count/len(X)
                    updated_means, updated_covariance = [], []
                    anchor = X[0]
                    for component in range(k):
                        r = responsibilities[:, component]
                        mean = anchor+(r @ (X-anchor))/count[component]
                        delta = X-mean
                        cov = (delta.T*r) @ delta/count[component]
                        cov += regularization*np.eye(X.shape[1])
                        updated_means.append(mean)
                        updated_covariance.append((cov+cov.T)/2)
                    means = s.finite(np.array(updated_means))
                    covariance = s.finite(np.array(updated_covariance))
                    density, responsibilities = _evaluate(X, means, covariance, weights)
                    value = float(density.mean())
                    change = value-history[-1]
                    history.append(value)
                    if abs(change) <= tolerance:
                        candidate = dict(means=means.copy(), covariance=covariance.copy(), weights=weights.copy(),
                                         responsibilities=responsibilities.copy(), history=np.array(history),
                                         n_iter=iteration, likelihood=value)
                        if best is None or value > best['likelihood']:
                            best = candidate
                        break
                else:
                    raise s.ConvergenceError('EM exhausted max_iter before likelihood tolerance')
            except (s.ConvergenceError, ValueError) as error:
                failed += 1
                reason = str(error)
        if best is None:
            raise s.ConvergenceError('no EM initialization converged: '+reason)
        self.__dict__.update(n_features_in_=X.shape[1], means_=best['means'], covariances_=best['covariance'],
                             weights_=best['weights'], responsibilities_=best['responsibilities'],
                             labels_=np.argmax(best['responsibilities'], axis=1).astype(np.int64),
                             lower_bound_=best['likelihood'], log_likelihood_history_=best['history'],
                             n_iter_=best['n_iter'], converged_=True, failed_initializations_=failed)
        return self

    @s.numerical
    def predict_proba(self, X):
        X = self._check_X(X)
        return _evaluate(X, self.means_, self.covariances_, self.weights_)[1]

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)

    @s.numerical
    def score_samples(self, X):
        X = self._check_X(X)
        return _evaluate(X, self.means_, self.covariances_, self.weights_)[0]

    def score(self, X):
        values = self.score_samples(X)
        if len(values) == 0:
            raise ValueError('mean log likelihood requires nonempty evaluation data')
        return float(values.mean())

    def _information_criterion(self, X, bic):
        values = self.score_samples(X)
        if len(values) == 0:
            raise ValueError('information criteria require nonempty evaluation data')
        k, p = len(self.weights_), self.n_features_in_
        parameters = k*p+k*p*(p+1)/2+k-1
        penalty = np.log(len(values)) if bic else 2
        return float(-2*values.sum()+penalty*parameters)

    def aic(self, X):
        return self._information_criterion(X, False)

    def bic(self, X):
        return self._information_criterion(X, True)


if __name__ == '__main__':
    s.main(GaussianMixture)
