"""Class-specific regularized sample covariances and Cholesky QDA scores."""
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

class QuadraticDiscriminantAnalysis(_support.ProbabilisticClassifier):

    def __init__(self, *, reg_param=1e-06, priors=None):
        self.reg_param = _support.scalar(reg_param, 'reg_param', high=1)
        self.priors = priors

    @_support.numerical
    def fit(self, X, y):
        regularization = _support.scalar(self.reg_param, 'reg_param', high=1)
        X, _, classes, encoded = _support.training(X, y, max_features=64)
        if len(classes) < 2:
            raise ValueError('QDA requires at least two classes')
        counts = np.bincount(encoded, minlength=len(classes)).astype(float)
        if np.any(counts < 2):
            raise ValueError('QDA requires at least two observations per class')
        prior = _support.priors(counts, self.priors)
        offset = X.mean(axis=0)
        centered = X - offset
        means = np.array([centered[encoded == k].mean(axis=0) for k in range(len(classes))])
        covariance = []
        factors = []
        log_det = []
        for k in range(len(classes)):
            residual = centered[encoded == k] - means[k]
            sample_covariance = residual.T @ residual / (counts[k] - 1)
            matrix = (1 - regularization) * sample_covariance + regularization * np.eye(X.shape[1])
            factor = _support.positive_definite_factor(matrix)
            covariance.append(matrix)
            factors.append(factor)
            log_det.append(float(2 * np.log(np.diag(factor)).sum()))
        _support.finite(log_det)
        self.__dict__.update(classes_=classes.copy(), n_features_in_=X.shape[1], class_count_=counts, priors_=prior.copy(), means_=means + offset, _centered_means_=means.copy(), _offset_=offset.copy(), covariance_=np.array(covariance), cholesky_=tuple(factors), log_det_=np.array(log_det), reg_param_=regularization, converged_=True)
        return self

    @_support.numerical
    def decision_function(self, X):
        X = self._check_X(X)
        centered = X - self._offset_
        result = np.empty((len(X), len(self.classes_)))
        for k in range(len(self.classes_)):
            whitened = np.linalg.solve(self.cholesky_[k], (centered - self._centered_means_[k]).T)
            result[:, k] = np.log(self.priors_[k]) - 0.5 * (self.log_det_[k] + np.sum(whitened * whitened, axis=0))
        return _support.finite(result, 'QDA discriminant scores')
if __name__ == '__main__':
    _support.main(QuadraticDiscriminantAnalysis)
