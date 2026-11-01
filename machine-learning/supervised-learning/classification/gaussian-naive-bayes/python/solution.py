"""Gaussian NB with explicit diagonal class likelihoods and variance smoothing."""
import importlib.util
from pathlib import Path
import sys
import numpy as np
if 'atlas_classification_support' not in sys.modules:
    _spec = importlib.util.spec_from_file_location('atlas_classification_support', Path(__file__).resolve().parents[2] / 'support.py')
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = _module
    _spec.loader.exec_module(_module)
_support = sys.modules['atlas_classification_support']

class GaussianNaiveBayes(_support.ProbabilisticClassifier):

    def __init__(self, *, var_smoothing=1e-09, priors=None):
        self.var_smoothing = _support.scalar(var_smoothing, 'var_smoothing', low=1e-12, high=1)
        self.priors = priors

    @_support.numerical
    def fit(self, X, y):
        smoothing = _support.scalar(self.var_smoothing, 'var_smoothing', low=1e-12, high=1)
        X, _, classes, encoded = _support.training(X, y)
        counts = np.bincount(encoded, minlength=len(classes)).astype(float)
        prior = _support.priors(counts, self.priors)
        epsilon = smoothing * max(1.0, float(np.max(np.var(X, axis=0))))
        means = np.array([X[encoded == k].mean(axis=0) for k in range(len(classes))])
        variance = np.array([np.var(X[encoded == k], axis=0) for k in range(len(classes))]) + epsilon
        _support.finite(means)
        _support.finite(variance)
        self.__dict__.update(classes_=classes.copy(), n_features_in_=X.shape[1], class_count_=counts, class_prior_=prior.copy(), class_log_prior_=np.log(prior), theta_=means, var_=variance, epsilon_=epsilon, converged_=True)
        return self

    @_support.numerical
    def decision_function(self, X):
        X = self._check_X(X)
        result = np.empty((len(X), len(self.classes_)))
        for k in range(len(self.classes_)):
            residual = X - self.theta_[k]
            result[:, k] = self.class_log_prior_[k] - 0.5 * np.sum(np.log(2 * np.pi * self.var_[k]) + residual * residual / self.var_[k], axis=1)
        return _support.finite(result, 'Gaussian joint log likelihood')

    @_support.numerical
    def _comparative_scores(self, X):
        """Cancel class-common quadratic terms before adding small log priors."""
        X = self._check_X(X)
        reference_mean, reference_variance = self.theta_[0], self.var_[0]
        residual = X - reference_mean
        result = np.empty((len(X), len(self.classes_)))
        for k in range(len(self.classes_)):
            variance = self.var_[k]
            difference = reference_mean - self.theta_[k]
            # q_k-q_0 = r²(1/v_k-1/v_0) + d(2r+d)/v_k.
            # These factorizations preserve equal/near-equal density differences
            # without subtracting already rounded enormous quadratic scores.
            inverse_difference = (reference_variance-variance)/(variance*reference_variance)
            quadratic_difference = residual*residual*inverse_difference + difference*(2*residual+difference)/variance
            log_ratio = np.log(variance/reference_variance)
            result[:, k] = self.class_log_prior_[k] - .5*np.sum(log_ratio+quadratic_difference, axis=1)
        return _support.finite(result, 'Gaussian comparative scores')

    def predict_proba(self, X):
        return _support.normalize_log_scores(self._comparative_scores(X))

    def predict(self, X):
        scores = self._comparative_scores(X)
        return self.classes_[np.argmax(scores, axis=1)]
if __name__ == '__main__':
    _support.main(GaussianNaiveBayes)
