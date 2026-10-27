import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest
from sklearn.svm import SVR

pytestmark = pytest.mark.ml


@pytest.mark.numerical
def test_analytic_epsilon_tube_and_primal_dual_optimum(algorithm):
    model = algorithm.SupportVectorRegression(C=10, epsilon=0.1, kernel="linear", tol=1e-9).fit([[-1], [0], [1]], [-1, 0, 1])
    assert_allclose(model.coef_, [0.9], atol=1e-7)
    assert_allclose(model.intercept_, 0, atol=1e-8)
    assert_allclose(model.predict([[2]]), [1.8], atol=1e-7)
    assert_allclose(model.primal_objective_, 0.405, atol=1e-7)
    assert_allclose(model.dual_objective_, 0.405, atol=1e-7)
    assert model.duality_gap_ < 1e-7
    assert abs(model.dual_coef_.sum()) < 1e-10
    assert np.max(np.abs(model.dual_coef_)) <= 10


@pytest.mark.reference
@pytest.mark.parametrize("kernel", ["linear", "rbf"])
@pytest.mark.parametrize("n", [12, 25])
def test_seeded_libsvm_prediction_and_objective_reference(algorithm, kernel, n):
    rng = np.random.default_rng(13061)
    X = rng.uniform(-1.5, 1.5, size=(n, 2))
    y = np.sin(1.4*X[:, 0]) - 0.3*X[:, 1] + rng.normal(scale=0.01, size=n)
    query = rng.uniform(-1.4, 1.4, size=(18, 2))
    model = algorithm.SupportVectorRegression(C=3, epsilon=0.05, kernel=kernel, gamma=0.7, tol=1e-8, max_iter=30000).fit(X, y)
    reference = SVR(C=3, epsilon=0.05, kernel=kernel, gamma=0.7, tol=1e-10, shrinking=False).fit(X, y)
    assert_allclose(model.predict(query), reference.predict(query), atol=2e-4, rtol=2e-4)
    assert model.duality_gap_ <= 1e-8*(1+abs(model.primal_objective_)+abs(model.dual_objective_))
    assert abs(model.dual_coef_.sum()) < 1e-9
    assert np.max(np.abs(model.dual_coef_)) <= 3


@pytest.mark.numerical
def test_smooth_dual_gradient_finite_difference(algorithm):
    rng = np.random.default_rng(13062)
    X = rng.normal(size=(8, 2)); y = rng.normal(size=8)
    model = algorithm.SupportVectorRegression(C=2, epsilon=0.02, kernel="rbf", gamma=0.8, tol=1e-8).fit(X, y)
    K = np.exp(-0.8*np.sum((X[:, None, :] - X[None, :, :])**2, axis=2))
    target = y-y.mean(); beta = model.dual_coef_; h = 1e-6
    # Smooth quadratic part only: the L1 epsilon term has kinks and is checked
    # by the independent primal/dual gap, not a differentiability assumption.
    def objective(v): return v@K@v/2-target@v
    fd = [(objective(beta+h*np.eye(8)[j])-objective(beta-h*np.eye(8)[j]))/(2*h) for j in range(8)]
    assert_allclose(model.smooth_dual_gradient_, fd, atol=2e-8, rtol=1e-6)


@pytest.mark.numerical
def test_constant_repeated_single_sample_and_large_epsilon(algorithm):
    for X, y in (([[1]], [4]), ([[1], [1], [1]], [4, 4, 4])):
        model = algorithm.SupportVectorRegression().fit(X, y)
        assert_allclose(model.predict([[1], [2]]), [4, 4], atol=1e-10)
        assert_allclose(model.dual_coef_, 0, atol=1e-10)
    model = algorithm.SupportVectorRegression(epsilon=10).fit([[-1], [1]], [-1, 1])
    assert_allclose(model.dual_coef_, 0, atol=1e-10)
    assert model.duality_gap_ == pytest.approx(0)


@pytest.mark.numerical
def test_rbf_large_offset_translation_and_underflow(algorithm):
    X = np.array([[0.0], [1], [2]])
    left = algorithm.SupportVectorRegression(C=3, gamma=0.7, tol=1e-8).fit(X, [0, 0.5, 0])
    shifted = algorithm.SupportVectorRegression(C=3, gamma=0.7, tol=1e-8).fit(X+1e9, [0, 0.5, 0])
    assert_allclose(left.predict(X), shifted.predict(X+1e9), atol=1e-10)
    K = algorithm._kernel_matrix(np.array([[0.0], [1e12]]), np.array([[0.0], [1e12]]), "rbf", 1)
    assert_allclose(K, np.eye(2))


@pytest.mark.parametrize("kwargs", [{"C": 0}, {"C": -1}, {"epsilon": -1}, {"kernel": "poly"}, {"gamma": 0},
                                       {"gamma": np.nan}, {"rho": 0}, {"tol": 0}, {"max_iter": 0}])
def test_invalid_hyperparameters(algorithm, kwargs):
    with pytest.raises(ValueError): algorithm.SupportVectorRegression(**kwargs)


def test_limits_ownership_nonconvergence_and_failed_refit(algorithm):
    rng = np.random.default_rng(13063); X = rng.normal(size=(12, 2)); y = rng.normal(size=12)
    saved = (X.copy(), y.copy()); model = algorithm.SupportVectorRegression(tol=1e-7)
    with pytest.raises(ValueError): model.predict(X)
    assert model.fit(X, y) is model
    before = model.predict(X); model.max_iter = 1
    with pytest.raises(RuntimeError, match="SVR"): model.fit(X, y + X[:, 0])
    assert_allclose(model.predict(X), before)
    assert_array_equal(X, saved[0]); assert_array_equal(y, saved[1])
    X[:] = 100; y[:] = 100
    assert_allclose(model.predict(saved[0]), before)
    assert model.predict(np.empty((0, 2))).shape == (0,)
    with pytest.raises(ValueError): model.fit(np.zeros((257, 1)), np.zeros(257))
    with pytest.raises(ValueError): model.fit([[1]], [[2]])
