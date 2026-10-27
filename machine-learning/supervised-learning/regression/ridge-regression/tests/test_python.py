import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest
from sklearn.linear_model import Ridge, LinearRegression

pytestmark = pytest.mark.ml


@pytest.mark.numerical
def test_closed_form_ridge_and_unpenalized_intercept(algorithm):
    X = np.array([[-1.0], [0], [1]]); y = np.array([8.0, 10, 12])
    model = algorithm.RidgeRegression(alpha=2).fit(X, y)
    assert_allclose(model.coef_, [1])
    assert_allclose(model.intercept_, 10)
    assert_allclose(model.predict([[2]]), [12])
    assert_allclose(model.objective_, 2)


@pytest.mark.reference
@pytest.mark.parametrize("alpha", [0.0, 0.1, 1.0, 100.0])
@pytest.mark.parametrize("intercept", [False, True])
def test_seeded_ridge_reference(algorithm, alpha, intercept):
    rng = np.random.default_rng(13021)
    X = rng.normal(size=(32, 4)); X[:, 3] = X[:, 1]; y = rng.normal(size=32)
    query = rng.normal(size=(12, 4))
    model = algorithm.RidgeRegression(alpha, fit_intercept=intercept).fit(X, y)
    # At alpha=0 this contract chooses minimum-norm OLS. Ridge's fixed SVD
    # cutoff can retain a roundoff singular value on duplicate columns; its
    # enormous cancelling coefficients are not a unique oracle off-manifold.
    reference = (LinearRegression(fit_intercept=intercept) if alpha == 0 else
                 Ridge(alpha=alpha, fit_intercept=intercept, solver="svd")).fit(X, y)
    assert_allclose(model.predict(query), reference.predict(query), atol=2e-10, rtol=2e-10)


@pytest.mark.numerical
def test_ridge_gradient_and_stationarity(algorithm):
    rng = np.random.default_rng(13022)
    X = rng.normal(size=(16, 3)); y = rng.normal(size=16); w = np.array([0.7, -1.2, 0.4]); b = 0.2; alpha = 0.8
    _, gradient, gb = algorithm.loss_gradient(X, y, w, b, alpha)
    h = 1e-6
    for j in range(3):
        delta = np.eye(3)[j] * h
        numerical = (algorithm.loss_gradient(X, y, w + delta, b, alpha)[0] - algorithm.loss_gradient(X, y, w - delta, b, alpha)[0]) / (2*h)
        assert_allclose(gradient[j], numerical, rtol=1e-6, atol=1e-8)
    assert_allclose(gb, (algorithm.loss_gradient(X, y, w, b+h, alpha)[0] - algorithm.loss_gradient(X, y, w, b-h, alpha)[0])/(2*h), rtol=1e-6)
    model = algorithm.RidgeRegression(alpha).fit(X, y)
    _, gradient, gb = algorithm.loss_gradient(X, y, model.coef_, model.intercept_, alpha)
    assert_allclose(gradient, 0, atol=1e-12)
    assert abs(gb) < 1e-12


@pytest.mark.numerical
def test_shrinkage_constant_features_and_single_sample(algorithm):
    X = np.array([[-2.0, 1], [0, 1], [2, 1]]); y = [-3, 1, 5]
    weak = algorithm.RidgeRegression(0.1).fit(X, y)
    strong = algorithm.RidgeRegression(100).fit(X, y)
    assert np.linalg.norm(strong.coef_) < np.linalg.norm(weak.coef_)
    assert strong.coef_[1] == pytest.approx(0)
    assert_allclose(algorithm.RidgeRegression().fit([[4, 2]], [9]).predict([[10, -2]]), [9])


@pytest.mark.parametrize("alpha", [-1, np.nan, np.inf, True, "1"])
def test_invalid_penalty(algorithm, alpha):
    with pytest.raises(ValueError): algorithm.RidgeRegression(alpha)


def test_no_input_mutation_and_failed_refit(algorithm):
    X = np.array([[0.0], [1], [2]]); y = np.array([1.0, 3, 5]); before = (X.copy(), y.copy())
    model = algorithm.RidgeRegression().fit(X, y); expected = model.predict(X)
    with pytest.raises(ValueError): model.fit(X, [[1], [3], [5]])
    assert_allclose(model.predict(X), expected)
    assert_array_equal(X, before[0]); assert_array_equal(y, before[1])
