import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest
from sklearn.linear_model import LogisticRegression as Reference

pytestmark = pytest.mark.ml


@pytest.mark.numerical
def test_constant_features_analytical_intercept_imbalance_and_threshold(algorithm):
    X = np.ones((20, 2)); y = ["no"]*15+["yes"]*5
    model = algorithm.LogisticRegression().fit(X, y)
    assert_allclose(model.coef_, 0, atol=1e-14)
    assert_allclose(model.intercept_, np.log(1/3), atol=1e-7)
    assert_allclose(model.predict_proba([[1, 1]]), [[0.75, 0.25]], atol=1e-9)
    assert_array_equal(model.predict([[1, 1]]), ["no"])
    model.fit([[0], [0]], ["a", "b"])
    assert model.predict([[0]])[0] == "b"  # threshold includes zero margin


@pytest.mark.numerical
def test_finite_difference_log_loss_gradient_and_stable_extremes(algorithm):
    rng = np.random.default_rng(14011)
    X = rng.normal(size=(13, 3)); y = (rng.random(13) > .3).astype(np.uint8)
    w = rng.normal(size=3); b = .3; alpha = .2; h = 1e-6
    loss, gradient, bias = algorithm.loss_gradient(X, y, w, b, alpha)
    assert np.isfinite(loss)
    for j in range(3):
        delta = np.eye(3)[j]*h
        finite = (algorithm.loss_gradient(X, y, w+delta, b, alpha)[0]-algorithm.loss_gradient(X, y, w-delta, b, alpha)[0])/(2*h)
        assert_allclose(gradient[j], finite, atol=1e-8, rtol=1e-6)
    finite = (algorithm.loss_gradient(X, y, w, b+h, alpha)[0]-algorithm.loss_gradient(X, y, w, b-h, alpha)[0])/(2*h)
    assert_allclose(bias, finite, atol=1e-8, rtol=1e-6)
    loss, g, _ = algorithm.loss_gradient([[1000], [-1000]], [0, 1], [1], alpha=0)
    assert loss == pytest.approx(1000) and g[0] == pytest.approx(1000)
    assert_allclose(algorithm._support.sigmoid(np.array([-1000., 0, 1000.])), [0, .5, 1])


@pytest.mark.reference
@pytest.mark.parametrize("alpha", [0.0, 0.05, 1.0])
@pytest.mark.parametrize("bias", [False, True])
def test_seeded_independent_objective_matched_reference(algorithm, alpha, bias):
    rng = np.random.default_rng(14012)
    X = rng.normal(size=(60, 3)); query = rng.normal(size=(17, 3))
    y = (rng.random(60) < algorithm._support.sigmoid(X @ np.array([1.1, -.8, .5])+.3)).astype(int)
    model = algorithm.LogisticRegression(alpha, fit_intercept=bias, tol=1e-10).fit(X, y)
    reference = Reference(C=np.inf if alpha == 0 else 1/(len(X)*alpha), fit_intercept=bias, solver="lbfgs", tol=1e-12, max_iter=1000)
    if alpha == 0:
        with pytest.warns(UserWarning, match="Setting penalty=None"):
            reference.fit(X, y)
    else:
        reference.fit(X, y)
    assert_allclose(model.predict_proba(query), reference.predict_proba(query), atol=2e-7, rtol=2e-7)
    assert np.max(np.diff(model.loss_history_), initial=0) <= 1e-14
    assert model.gradient_norm_ <= model.tol


@pytest.mark.numerical
def test_separable_data_large_offset_and_feature_scale(algorithm):
    X = np.array([[-2.], [-1], [1], [2]])
    model = algorithm.LogisticRegression(alpha=.1).fit(X, [-4, -4, 7, 7])
    assert_array_equal(model.predict(X), [-4, -4, 7, 7])
    shifted = algorithm.LogisticRegression(alpha=.1).fit(X+1e9, [-4, -4, 7, 7])
    assert_allclose(model.predict_proba(X), shifted.predict_proba(X+1e9), atol=1e-7)
    # Scaling changes the meaning of L2: w for c*X maps to a penalty c^2*alpha.
    scaled = algorithm.LogisticRegression(alpha=10).fit(10*X, [-4, -4, 7, 7])
    assert_allclose(scaled.predict_proba(10*X), model.predict_proba(X), atol=1e-8)


def test_state_shapes_nonconvergence_and_failed_refit(algorithm):
    X = np.array([[-2.], [-1], [1], [2]]); y = np.array([0, 1, 0, 1])
    model = algorithm.LogisticRegression()
    with pytest.raises(ValueError): model.predict(X)
    with pytest.raises(ValueError): model.predict_proba(X)
    assert model.fit(X, y) is model
    before = model.predict_proba(X)
    model.max_iter = 1; model.tol = 1e-14
    with pytest.raises(algorithm._support.ConvergenceError): model.fit(X, y)
    assert_allclose(model.predict_proba(X), before)
    assert model.predict(np.empty((0, 1))).shape == (0,)
    assert model.predict_proba(np.empty((0, 1))).shape == (0, 2)
    assert_array_equal(X, [[-2], [-1], [1], [2]])


@pytest.mark.parametrize("y", [[0, 0], [0, 1, 2], [True, False], [1., 2.], [1, "1"], [[0], [1]], [np.nan, 1]])
def test_invalid_label_domains(algorithm, y):
    with pytest.raises(ValueError): algorithm.LogisticRegression().fit([[0], [1]], y)


@pytest.mark.parametrize("parameters", [{"alpha": -1}, {"alpha": np.inf}, {"tol": 0}, {"max_iter": True}, {"fit_intercept": 1}])
def test_invalid_parameters(algorithm, parameters):
    with pytest.raises(ValueError): algorithm.LogisticRegression(**parameters)
