"""Bernoulli NB includes both presence and absence evidence."""
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

def _binary(X, threshold):
    if threshold is None:
        if not np.isin(X, (0, 1)).all():
            raise ValueError('binarize=None requires exact numeric 0/1 features')
        return X
    return (X > threshold).astype(float)

class BernoulliNaiveBayes(_support.ProbabilisticClassifier):

    def __init__(self, alpha=1.0, *, binarize=0.0, priors=None):
        self.alpha = _support.scalar(alpha, 'alpha', low=1e-09, high=1000000.0)
        self.binarize = None if binarize is None else _support.scalar(binarize, 'binarize', low=-1000000000000.0)
        self.priors = priors

    @_support.numerical
    def fit(self, X, y):
        alpha = _support.scalar(self.alpha, 'alpha', low=1e-09, high=1000000.0)
        threshold = None if self.binarize is None else _support.scalar(self.binarize, 'binarize', low=-1000000000000.0)
        X, _, classes, encoded = _support.training(X, y)
        binary = _binary(X, threshold)
        counts = np.bincount(encoded, minlength=len(classes)).astype(float)
        prior = _support.priors(counts, self.priors)
        feature_count = np.array([binary[encoded == k].sum(axis=0) for k in range(len(classes))])
        probability = (feature_count + alpha) / (counts[:, None] + 2 * alpha)
        log_presence = np.log(probability)
        log_absence = np.log1p(-probability)
        _support.finite(log_presence)
        _support.finite(log_absence)
        self.__dict__.update(classes_=classes.copy(), n_features_in_=X.shape[1], class_count_=counts, class_prior_=prior.copy(), class_log_prior_=np.log(prior), feature_count_=feature_count, feature_log_prob_=log_presence, feature_log_absence_=log_absence, binarize_=threshold, alpha_=alpha, converged_=True)
        return self

    @_support.numerical
    def decision_function(self, X):
        binary = _binary(self._check_X(X), self.binarize_)
        return _support.finite(binary @ self.feature_log_prob_.T + (1 - binary) @ self.feature_log_absence_.T + self.class_log_prior_, 'Bernoulli joint log likelihood')
if __name__ == '__main__':
    _support.main(BernoulliNaiveBayes)
