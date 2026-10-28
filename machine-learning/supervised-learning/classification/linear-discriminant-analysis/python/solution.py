"""Prior-weighted shared covariance LDA with Cholesky solves and linear scores."""
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

class LinearDiscriminantAnalysis(_support.ProbabilisticClassifier):

    def __init__(self, *, reg=1e-06, priors=None):
        self.reg = _support.scalar(reg, 'reg', high=1000000.0)
        self.priors = priors

    @_support.numerical
    def fit(self, X, y):
        regularization = _support.scalar(self.reg, 'reg', high=1000000.0)
        X, _, classes, encoded = _support.training(X, y, max_features=64)
        if len(classes) < 2:
            raise ValueError('LDA requires at least two classes')
        counts = np.bincount(encoded, minlength=len(classes)).astype(float)
        prior = _support.priors(counts, self.priors)
        offset = X.mean(axis=0)
        centered = X - offset
        means = np.array([centered[encoded == k].mean(axis=0) for k in range(len(classes))])
        covariance = np.zeros((X.shape[1], X.shape[1]))
        for k in range(len(classes)):
            residual = centered[encoded == k] - means[k]
            covariance += prior[k] * (residual.T @ residual / counts[k])
        covariance += regularization * np.eye(X.shape[1])
        factor = _support.positive_definite_factor(covariance)
        coefficient = np.linalg.solve(factor.T, np.linalg.solve(factor, means.T)).T
        intercept = -0.5 * np.sum(means * coefficient, axis=1) + np.log(prior)
        _support.finite(coefficient)
        _support.finite(intercept)
        self.__dict__.update(classes_=classes.copy(), n_features_in_=X.shape[1], class_count_=counts, priors_=prior.copy(), means_=means + offset, _centered_means_=means.copy(), _offset_=offset.copy(), covariance_=covariance, cholesky_=factor, coef_=coefficient, intercept_=intercept, condition_number_=float(np.linalg.cond(covariance)), reg_=regularization, converged_=True)
        return self

    @_support.numerical
    def decision_function(self, X):
        X = self._check_X(X)
        return _support.finite((X - self._offset_) @ self.coef_.T + self.intercept_, 'LDA discriminant scores')
if __name__ == '__main__':
    _support.main(LinearDiscriminantAnalysis)
