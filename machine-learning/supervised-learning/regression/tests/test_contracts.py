"""Public contracts across all seven estimators, independent of solver details."""
import importlib.util
from pathlib import Path

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest

_spec = importlib.util.spec_from_file_location("regression_contract_support", Path(__file__).parents[1] / "support.py")
support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(support)

CASES = [("linear-regression", "LinearRegression"), ("ridge-regression", "RidgeRegression"),
         ("polynomial-regression", "PolynomialRegression"), ("lasso-regression", "LassoRegression"),
         ("elastic-net", "ElasticNetRegression"), ("support-vector-regression", "SupportVectorRegression"),
         ("decision-tree-regression", "DecisionTreeRegression")]
pytestmark = pytest.mark.ml


@pytest.fixture(params=CASES, ids=[name for name, _ in CASES])
def estimator(request):
    topic, name = request.param
    return getattr(support.load(topic), name)


@pytest.mark.parametrize("X,y", [([[np.nan]], [0]), ([[np.inf]], [0]), ([[0]], [np.inf]),
                                      ([[0]], [np.nan]), ([[0]], [[1]]), ([[1]], [1, 2]),
                                      (np.empty((2, 0)), [1, 2]), ([["1"]], [1]),
                                      ([[False]], [0]), ([[1j]], [0]), ([[1e13]], [0]),
                                      (np.zeros((2049, 1)), np.zeros(2049))])
def test_rejects_invalid_training_data_before_fitting(estimator, X, y):
    model = estimator()
    with pytest.raises(ValueError):
        model.fit(X, y)
    with pytest.raises(ValueError):
        model.predict([[0]])


@pytest.mark.numerical
def test_deterministic_state_shapes_scores_and_query_validation(estimator):
    X = np.array([[-1.0], [0], [1]])
    y = np.array([2.0, 2, 2])
    saved = X.copy(), y.copy()
    global_state = np.random.get_state()
    first, second = estimator(), estimator()
    assert first.fit(X, y) is first
    second.fit(X, y)
    assert first.predict(X).shape == (3,)
    assert_allclose(first.predict(X), second.predict(X), atol=0, rtol=0)
    assert first.predict(np.empty((0, 1))).shape == (0,)
    assert first.score(X, y) == 1
    assert first.score(X, np.zeros(3)) == 0
    assert_array_equal(X, saved[0]); assert_array_equal(y, saved[1])
    after = np.random.get_state()
    assert global_state[0] == after[0] and global_state[2:] == after[2:]
    assert_array_equal(global_state[1], after[1])
    for query in ([1], [[1, 2]], [[np.nan]], [[np.inf]], [[True]], [[1e13]]):
        with pytest.raises(ValueError):
            first.predict(query)


@pytest.mark.parametrize("value", [True, np.inf, np.nan, 10**1000, "1"])
def test_scalar_hyperparameters_fail_with_documented_error(value):
    with pytest.raises(ValueError):
        support.load("ridge-regression").RidgeRegression(alpha=value)
