"""Count-event multinomial NB with additive smoothing and explicit log scores."""
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

class MultinomialNaiveBayes(_support.ProbabilisticClassifier):

    def __init__(self, alpha=1.0, *, priors=None):
        self.alpha = _support.scalar(alpha, 'alpha', low=1e-09, high=1000000.0)
        self.priors = priors

    @_support.numerical
    def fit(self, X, y):
        alpha = _support.scalar(self.alpha, 'alpha', low=1e-09, high=1000000.0)
        X, _, classes, encoded = _support.training(X, y)
        if np.any(X < 0):
            raise ValueError('multinomial features must be nonnegative counts/weights')
        counts = np.bincount(encoded, minlength=len(classes)).astype(float)
        prior = _support.priors(counts, self.priors)
        feature_count = np.array([X[encoded == k].sum(axis=0) for k in range(len(classes))])
        smoothed = feature_count + alpha
        log_probability = np.log(smoothed) - np.log(smoothed.sum(axis=1, keepdims=True))
        _support.finite(log_probability)
        self.__dict__.update(classes_=classes.copy(), n_features_in_=X.shape[1], class_count_=counts, class_prior_=prior.copy(), class_log_prior_=np.log(prior), feature_count_=feature_count, feature_log_prob_=log_probability, alpha_=alpha, converged_=True)
        return self

    @_support.numerical
    def decision_function(self, X):
        X = self._check_X(X)
        if np.any(X < 0):
            raise ValueError('multinomial features must be nonnegative counts/weights')
        return _support.finite(X @ self.feature_log_prob_.T + self.class_log_prior_, 'multinomial joint log likelihood')
if __name__ == '__main__':
    _support.main(MultinomialNaiveBayes)
