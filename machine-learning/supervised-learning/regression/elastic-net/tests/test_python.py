import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest
from sklearn.linear_model import ElasticNet, Ridge

pytestmark = pytest.mark.ml


@pytest.mark.numerical
def test_analytical_l1_l2_coordinate_minimum(algorithm):
    X = np.array([[-1.0], [0], [1]]); y = [-2.0, 0, 2]
    model = algorithm.ElasticNetRegression(alpha=0.5, l1_ratio=0.5).fit(X, y)
    assert_allclose(model.coef_, [13/11])
    assert_allclose(model.predict([[2]]), [26/11])
    assert model.kkt_violation_ <= model.stopping_threshold_


@pytest.mark.reference
@pytest.mark.parametrize("ratio", [0.0, 0.2, 0.7, 1.0])
@pytest.mark.parametrize("intercept", [False, True])
def test_reference_predictions_with_matched_normalization(algorithm, ratio, intercept):
    rng = np.random.default_rng(13051)
    X = rng.normal(size=(45, 5)); X[:, 4] = X[:, 0]
    y = 1.2 + X[:, 0] - 2*X[:, 2] + rng.normal(scale=0.03, size=45)
    query = rng.normal(size=(15, 5)); query[:, 4] = query[:, 0]
    model = algorithm.ElasticNetRegression(0.1, ratio, fit_intercept=intercept, tol=1e-10).fit(X, y)
    reference = (Ridge(alpha=len(X)*0.1, fit_intercept=intercept) if ratio == 0 else
                 ElasticNet(alpha=0.1, l1_ratio=ratio, fit_intercept=intercept, tol=1e-12, max_iter=20000)).fit(X, y)
    assert_allclose(model.predict(query), reference.predict(query), atol=2e-8, rtol=2e-7)


@pytest.mark.numerical
def test_loss_monotonicity_stationarity_and_finite_difference(algorithm):
    rng = np.random.default_rng(13052)
    X = rng.normal(size=(30, 4)); X -= X.mean(axis=0)
    y = rng.normal(size=30); y -= y.mean()
    alpha, ratio = 0.08, 0.4
    l1, l2 = alpha*ratio, alpha*(1-ratio)
    model = algorithm.ElasticNetRegression(alpha, ratio, tol=1e-10).fit(X, y)
    assert np.all(np.diff(model.loss_history_) <= 1e-12)
    w = np.array([0.4, -0.7, 1.1, -0.2]); h = 1e-6
    def objective(v): return np.mean((X @ v-y)**2)/2 + l1*np.abs(v).sum() + l2*(v@v)/2
    fd = [(objective(w+h*np.eye(4)[j])-objective(w-h*np.eye(4)[j]))/(2*h) for j in range(4)]
    assert_allclose(algorithm._support.kkt_violation(X, y, w, l1, l2), max(abs(np.array(fd))), rtol=1e-6, atol=1e-8)
    assert model.objective_ == pytest.approx(objective(model.coef_), abs=1e-12)


@pytest.mark.numerical
def test_penalty_endpoints_zero_alpha_and_constant_data(algorithm):
    rng = np.random.default_rng(13053); X = rng.normal(size=(20, 3)); y = rng.normal(size=20)
    lasso = algorithm._support.load("lasso-regression").LassoRegression(0.1, tol=1e-10).fit(X, y)
    en = algorithm.ElasticNetRegression(0.1, 1, tol=1e-10).fit(X, y)
    assert_allclose(en.predict(X), lasso.predict(X), atol=1e-12)
    linear = algorithm._support.load("linear-regression").LinearRegression().fit(X, y)
    zero = algorithm.ElasticNetRegression(0, 0.5, tol=1e-10).fit(X, y)
    assert_allclose(zero.predict(X), linear.predict(X), atol=1e-8)
    assert_allclose(algorithm.ElasticNetRegression().fit([[1], [1], [1]], [2, 4, 6]).predict([[1]]), [4])


@pytest.mark.parametrize("kwargs", [{"alpha": -1}, {"l1_ratio": -0.1}, {"l1_ratio": 1.1}, {"l1_ratio": np.nan}, {"tol": 0}, {"max_iter": 0}, {"fit_intercept": None}])
def test_invalid_hyperparameters(algorithm, kwargs):
    with pytest.raises(ValueError): algorithm.ElasticNetRegression(**kwargs)


def test_failure_ownership_and_iteration_limit(algorithm):
    rng = np.random.default_rng(13054); X = rng.normal(size=(20, 4)); y = rng.normal(size=20); saved = (X.copy(), y.copy())
    model = algorithm.ElasticNetRegression(0.01, 0.5, tol=1e-10)
    with pytest.raises(ValueError): model.predict(X)
    assert model.fit(X, y) is model
    before = model.predict(X); model.max_iter = 1
    with pytest.raises(RuntimeError, match="KKT"): model.fit(X, y+X[:, 0])
    assert_allclose(model.predict(X), before)
    assert_array_equal(X, saved[0]); assert_array_equal(y, saved[1])
    assert model.predict(np.empty((0, 4))).shape == (0,)
    with pytest.raises(ValueError): model.fit(X, y[:, None])
