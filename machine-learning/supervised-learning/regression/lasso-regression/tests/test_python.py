import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest
from sklearn.linear_model import Lasso, LinearRegression

pytestmark = pytest.mark.ml


@pytest.mark.numerical
def test_analytical_soft_threshold_and_exact_sparsity(algorithm):
    X = np.array([[-1.0], [0], [1]]); y = np.array([-2.0, 0, 2])
    model = algorithm.LassoRegression(alpha=1/3).fit(X, y)
    assert_allclose(model.coef_, [1.5])
    assert_allclose(model.predict([[2]]), [3])
    assert model.objective_ == pytest.approx(7/12)
    assert_allclose(algorithm.LassoRegression(alpha=2).fit(X, y).coef_, 0)


@pytest.mark.reference
@pytest.mark.parametrize("alpha", [0.0, 0.02, 0.2, 2.0])
@pytest.mark.parametrize("intercept", [False, True])
def test_reference_objective_and_held_out_predictions(algorithm, alpha, intercept):
    rng = np.random.default_rng(13041)
    X = rng.normal(size=(40, 5)); y = 0.8 + X @ np.array([2, 0, -1, 0, 0.3]) + rng.normal(scale=0.02, size=40)
    query = rng.normal(size=(15, 5))
    model = algorithm.LassoRegression(alpha, fit_intercept=intercept, tol=1e-10).fit(X, y)
    reference = (LinearRegression(fit_intercept=intercept) if alpha == 0 else
                 Lasso(alpha=alpha, fit_intercept=intercept, tol=1e-12, max_iter=20000)).fit(X, y)
    assert_allclose(model.predict(query), reference.predict(query), rtol=1e-7, atol=1e-8)
    assert model.kkt_violation_ <= model.stopping_threshold_


@pytest.mark.numerical
def test_loss_descent_independent_kkt_and_gradient_away_from_zero(algorithm):
    rng = np.random.default_rng(13042)
    X = rng.normal(size=(24, 4)); X -= X.mean(axis=0); y = rng.normal(size=24); y -= y.mean()
    alpha = 0.07
    model = algorithm.LassoRegression(alpha, tol=1e-10).fit(X, y)
    assert np.all(np.diff(model.loss_history_) <= 1e-12)
    w = np.array([0.4, -0.7, 1.1, -0.2]); h = 1e-6
    def objective(v): return np.mean((X @ v - y)**2)/2 + alpha*np.abs(v).sum()
    finite_gradient = np.array([(objective(w + h*np.eye(4)[j]) - objective(w - h*np.eye(4)[j]))/(2*h) for j in range(4)])
    assert_allclose(algorithm._support.kkt_violation(X, y, w, alpha, 0), np.max(np.abs(finite_gradient)), rtol=1e-6, atol=1e-8)
    gradient = X.T @ (model.predict(X) - y)/len(y)
    for j, coefficient in enumerate(model.coef_):
        assert (abs(gradient[j] + alpha*np.sign(coefficient)) if coefficient else max(abs(gradient[j])-alpha, 0)) < 1e-8


@pytest.mark.numerical
def test_zero_variance_nonuniqueness_and_determinism(algorithm):
    X = np.array([[-1.0, -1, 1], [0, 0, 1], [1, 1, 1]])
    first = algorithm.LassoRegression(0.1).fit(X, [-2, 0, 2])
    second = algorithm.LassoRegression(0.1).fit(X, [-2, 0, 2])
    assert_allclose(first.predict(X), second.predict(X), atol=0)
    assert first.coef_[2] == 0
    assert first.n_iter_ <= 10000
    assert_allclose(algorithm.LassoRegression().fit(np.ones((3, 2)), [1, 4, 7]).predict([[1, 1]]), [4])


def test_nonconvergence_is_explicit_and_preserves_successful_state(algorithm):
    rng = np.random.default_rng(13043)
    X = rng.normal(size=(20, 4)); y = X @ np.array([1.0, 2, -1, 0.5])
    model = algorithm.LassoRegression(0.01, tol=1e-10).fit(X, y)
    before = model.predict(X)
    model.max_iter = 1
    with pytest.raises(RuntimeError, match="KKT"):
        model.fit(X, y + X[:, 0])
    assert_allclose(model.predict(X), before)


@pytest.mark.parametrize("kwargs", [{"alpha": -1}, {"alpha": np.inf}, {"tol": 0}, {"tol": np.nan}, {"max_iter": 0}, {"max_iter": True}, {"fit_intercept": 1}])
def test_invalid_hyperparameters(algorithm, kwargs):
    with pytest.raises(ValueError): algorithm.LassoRegression(**kwargs)


def test_shapes_input_ownership_and_empty_queries(algorithm):
    X = np.array([[0.0], [1], [2]]); y = np.array([1.0, 3, 5]); before = (X.copy(), y.copy())
    model = algorithm.LassoRegression(0.1)
    with pytest.raises(ValueError): model.predict(X)
    model.fit(X, y)
    assert_array_equal(X, before[0]); assert_array_equal(y, before[1])
    assert model.predict(np.empty((0, 1))).shape == (0,)
    for bad_X, bad_y in ((X, y[:, None]), (X[:, 0], y), ([[np.nan]], [1]), (X, y[:1])):
        with pytest.raises(ValueError): model.fit(bad_X, bad_y)
