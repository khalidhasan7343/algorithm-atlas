import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

pytestmark = pytest.mark.ml


@pytest.mark.numerical
def test_known_parabola_and_multivariate_interaction(algorithm):
    X = np.arange(-2.0, 3).reshape(-1, 1)
    model = algorithm.PolynomialRegression(2).fit(X, X[:, 0]**2)
    assert_allclose(model.coef_, [0, 1], atol=1e-12)
    assert_allclose(model.predict([[3]]), [9])
    assert model.n_output_features_ == 2
    X = np.array([[x, y] for x in (-1, 0, 1) for y in (-1, 0, 1)], dtype=float)
    target = 1 + 2*X[:, 0] - X[:, 1] + 3*X[:, 0]*X[:, 1]
    model.fit(X, target)
    assert_array_equal(model.powers_, [[1, 0], [0, 1], [2, 0], [1, 1], [0, 2]])
    assert_allclose(model.predict([[2, 3]]), [20], atol=1e-10)


@pytest.mark.reference
@pytest.mark.parametrize("degree", [1, 2, 3, 4])
def test_seeded_reference_pipeline_and_feature_order(algorithm, degree):
    rng = np.random.default_rng(13031)
    X = rng.normal(size=(40, 2)); y = rng.normal(size=40); query = rng.normal(size=(12, 2))
    features = PolynomialFeatures(degree, include_bias=False)
    reference = LinearRegression().fit(features.fit_transform(X), y)
    model = algorithm.PolynomialRegression(degree).fit(X, y)
    assert_allclose(model.transform(query), features.transform(query), atol=1e-12)
    assert_allclose(model.predict(query), reference.predict(features.transform(query)), atol=1e-9, rtol=1e-9)


@pytest.mark.numerical
def test_rank_deficient_and_training_only_expansion(algorithm):
    X = np.ones((4, 2)); model = algorithm.PolynomialRegression(3).fit(X, [4, 4, 4, 4])
    assert model.rank_ == 0
    assert_allclose(model.predict([[1, 1]]), [4])
    assert model.predict(np.empty((0, 2))).shape == (0,)


@pytest.mark.parametrize("degree", [0, -1, 9, True, 2.5])
def test_invalid_degree(algorithm, degree):
    with pytest.raises(ValueError): algorithm.PolynomialRegression(degree)


def test_resource_numeric_limits_and_failed_refit(algorithm):
    model = algorithm.PolynomialRegression(2)
    with pytest.raises(ValueError): model.predict([[1]])
    with pytest.raises(ValueError): model.fit(np.ones((10, 32)), np.ones(10))
    with pytest.raises(ValueError): model.fit([[1e12], [2]], [1, 2])
    X = np.array([[0.0], [1], [2]]); y = np.array([0.0, 1, 4]); before = (X.copy(), y.copy())
    assert model.fit(X, y) is model
    expected = model.predict(X)
    with pytest.raises(ValueError): model.fit(X, [1, np.nan, 2])
    assert_allclose(model.predict(X), expected)
    assert_array_equal(X, before[0]); assert_array_equal(y, before[1])
