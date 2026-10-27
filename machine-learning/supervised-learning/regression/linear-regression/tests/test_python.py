import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest
from sklearn.linear_model import LinearRegression as Reference

pytestmark = pytest.mark.ml


@pytest.mark.numerical
def test_analytical_fit_and_minimum_norm_singular_system(algorithm):
    X = np.array([[0.0], [1], [2]])
    y = np.array([1.0, 3, 5])
    model = algorithm.LinearRegression().fit(X, y)
    assert_allclose(model.coef_, [2])
    assert_allclose(model.intercept_, 1)
    assert_allclose(model.predict([[3]]), [7])
    assert model.score(X, y) == pytest.approx(1)
    singular = np.column_stack((X[:, 0], X[:, 0]))
    model.fit(singular, y)
    assert_allclose(model.coef_, [1, 1])
    assert model.rank_ == 1 and np.isinf(model.condition_number_)


@pytest.mark.reference
@pytest.mark.parametrize("intercept", [False, True])
def test_seeded_reference_predictions_and_parameters(algorithm, intercept):
    rng = np.random.default_rng(13011)
    for n, p in ((1, 3), (8, 2), (30, 5)):
        X = rng.normal(size=(n, p)); y = rng.normal(size=n); query = rng.normal(size=(12, p))
        model = algorithm.LinearRegression(fit_intercept=intercept).fit(X, y)
        reference = Reference(fit_intercept=intercept).fit(X, y)
        assert_allclose(model.predict(query), reference.predict(query), atol=1e-10, rtol=1e-10)


@pytest.mark.numerical
def test_finite_difference_gradient_and_residual_orthogonality(algorithm):
    rng = np.random.default_rng(13012)
    X = rng.normal(size=(11, 3)); y = rng.normal(size=11); w = rng.normal(size=3); b = 0.7
    loss, gradient, bias_gradient = algorithm.loss_gradient(X, y, w, b)
    h = 1e-6
    for j in range(3):
        delta = np.eye(3)[j] * h
        numerical = (algorithm.loss_gradient(X, y, w + delta, b)[0] - algorithm.loss_gradient(X, y, w - delta, b)[0]) / (2 * h)
        assert_allclose(gradient[j], numerical, atol=1e-8, rtol=1e-6)
    numerical = (algorithm.loss_gradient(X, y, w, b + h)[0] - algorithm.loss_gradient(X, y, w, b - h)[0]) / (2 * h)
    assert_allclose(bias_gradient, numerical, atol=1e-8, rtol=1e-6)
    model = algorithm.LinearRegression().fit(X, y)
    residual = model.predict(X) - y
    assert_allclose(X.T @ residual, 0, atol=1e-12)
    assert abs(residual.mean()) < 1e-12


@pytest.mark.numerical
def test_large_offset_constant_and_nearly_singular_features(algorithm):
    x = np.arange(8.0)
    X = np.column_stack((1e9 + x, np.ones(8)))
    y = 3 * x - 2
    model = algorithm.LinearRegression().fit(X, y)
    assert_allclose(model.predict(X), y, atol=1e-6)
    model.fit(np.ones((4, 2)), [7, 7, 7, 7])
    assert_allclose(model.coef_, 0)
    assert_allclose(model.predict([[1, 1]]), [7])


def test_input_ownership_shapes_and_failed_refit(algorithm):
    X = np.arange(6.0).reshape(3, 2); y = np.array([1.0, 2, 3]); saved = (X.copy(), y.copy())
    model = algorithm.LinearRegression()
    with pytest.raises(ValueError): model.predict(X)
    assert model.fit(X, y) is model
    prediction = model.predict(X)
    with pytest.raises(ValueError): model.fit(X, [1, np.nan, 3])
    assert_allclose(model.predict(X), prediction)
    assert_array_equal(X, saved[0]); assert_array_equal(y, saved[1])
    assert model.predict(np.empty((0, 2))).shape == (0,)


@pytest.mark.parametrize("X,y", [([], []), ([1, 2], [1, 2]), ([[1], [2]], [[1], [2]]),
                                         ([[1]], [1, 2]), ([[np.inf]], [1]), ([[1j]], [1]),
                                         ([[True]], [1]), ([[1e13]], [1]), ([[1]], [np.nan])])
def test_invalid_shapes_domains_and_types(algorithm, X, y):
    with pytest.raises(ValueError): algorithm.LinearRegression().fit(X, y)
