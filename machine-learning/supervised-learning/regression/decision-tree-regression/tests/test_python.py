import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest
from sklearn.tree import DecisionTreeRegressor

pytestmark = pytest.mark.ml


def brute_split(X, y, minimum_leaf=1):
    choices = []
    for feature in range(X.shape[1]):
        distinct = np.unique(X[:, feature])
        for a, b in zip(distinct, distinct[1:]):
            threshold = a+(b-a)/2
            left = X[:, feature] <= threshold
            if left.sum() < minimum_leaf or (~left).sum() < minimum_leaf:
                continue
            error = sum(float(np.sum((group - group.mean())**2)) for group in (y[left], y[~left]))
            choices.append((error, feature, threshold))
    return min(choices) if choices else None


@pytest.mark.numerical
def test_known_partition_mean_leaves_and_zero_gain_xor(algorithm):
    model = algorithm.DecisionTreeRegression(max_depth=1).fit([[0], [1], [2], [3]], [1, 1, 5, 5])
    assert model.tree_.feature == 0 and model.tree_.threshold == 1.5
    assert_allclose(model.predict([[0.5], [2.5]]), [1, 5])
    assert model.n_leaves_ == 2 and model.depth_ == 1
    X = [[0, 0], [0, 1], [1, 0], [1, 1]]; y = [0, 1, 1, 0]
    # CART may need a valid zero-gain root split to improve at the next level.
    assert_allclose(algorithm.DecisionTreeRegression(max_depth=2).fit(X, y).predict(X), y)


@pytest.mark.numerical
def test_exhaustive_one_level_oracle_and_invariants(algorithm):
    rng = np.random.default_rng(13071)
    for _ in range(80):
        X = rng.integers(-3, 4, size=(12, 3)).astype(float); y = rng.normal(size=12)
        minimum_leaf = int(rng.integers(1, 4)); expected = brute_split(X, y, minimum_leaf)
        model = algorithm.DecisionTreeRegression(max_depth=1, min_samples_leaf=minimum_leaf).fit(X, y)
        assert model.tree_.feature == expected[1]
        assert model.tree_.threshold == expected[2]
        assert model.tree_.left.n_samples >= minimum_leaf and model.tree_.right.n_samples >= minimum_leaf
        mask = X[:, expected[1]] <= expected[2]
        assert_allclose(model.tree_.left.value, y[mask].mean())
        assert_allclose(model.tree_.right.value, y[~mask].mean())
        assert_allclose(model.training_mse_, expected[0]/len(y), atol=1e-12)


@pytest.mark.reference
@pytest.mark.parametrize("depth", [1, 2, 4])
@pytest.mark.parametrize("minimum_leaf", [1, 3])
def test_reference_on_unambiguous_continuous_splits(algorithm, depth, minimum_leaf):
    rng = np.random.default_rng(13072)
    X = rng.normal(size=(50, 3)); y = X[:, 0]**2 - X[:, 1] + rng.normal(scale=0.01, size=50)
    query = rng.normal(size=(15, 3))
    model = algorithm.DecisionTreeRegression(max_depth=depth, min_samples_leaf=minimum_leaf).fit(X, y)
    reference = DecisionTreeRegressor(max_depth=depth, min_samples_leaf=minimum_leaf, random_state=13072).fit(X, y)
    assert_allclose(model.predict(query), reference.predict(query), atol=1e-10)


@pytest.mark.numerical
def test_ties_constant_features_large_target_offset_and_adjacent_float(algorithm):
    X = np.array([[0.0, 0], [1, 1], [2, 2], [3, 3]])
    model = algorithm.DecisionTreeRegression(max_depth=1).fit(X, [1, 1, 5, 5])
    assert model.tree_.feature == 0
    constant = algorithm.DecisionTreeRegression().fit(np.ones((5, 2)), [1, 2, 3, 4, 5])
    assert constant.tree_.feature is None
    assert_allclose(constant.predict([[1, 1]]), [3])
    large = algorithm.DecisionTreeRegression(max_depth=1).fit(X, np.array([0, 0, 0.01, 0.01])+1e9)
    assert large.tree_.threshold == 1.5
    a = 1.0; b = np.nextafter(a, 2.0)
    small = algorithm.DecisionTreeRegression(max_depth=1).fit([[a], [b]], [0, 1])
    assert_allclose(small.predict([[a], [b]]), [0, 1])


@pytest.mark.numerical
def test_min_impurity_decrease_uses_root_sample_normalization(algorithm):
    X = [[0], [1], [2], [3]]; y = [1, 1, 5, 5]
    assert algorithm.DecisionTreeRegression(min_impurity_decrease=4.1).fit(X, y).n_leaves_ == 1
    assert algorithm.DecisionTreeRegression(min_impurity_decrease=4).fit(X, y).n_leaves_ == 2


@pytest.mark.parametrize("kwargs", [{"max_depth": 0}, {"max_depth": 33}, {"max_depth": True}, {"min_samples_leaf": 0},
                                       {"min_impurity_decrease": -1}, {"min_impurity_decrease": np.nan}])
def test_invalid_hyperparameters(algorithm, kwargs):
    with pytest.raises(ValueError): algorithm.DecisionTreeRegression(**kwargs)


def test_input_ownership_failed_refit_and_shapes(algorithm):
    X = np.array([[0.0], [1], [2]]); y = np.array([0.0, 1, 4]); saved = (X.copy(), y.copy())
    model = algorithm.DecisionTreeRegression()
    with pytest.raises(ValueError): model.predict(X)
    assert model.fit(X, y) is model
    before = model.predict(X)
    with pytest.raises(ValueError): model.fit(X, y[:, None])
    assert_allclose(model.predict(X), before)
    assert_array_equal(X, saved[0]); assert_array_equal(y, saved[1])
    X[:] = 100; y[:] = 100
    assert_allclose(model.predict(saved[0]), before)
    assert model.predict(np.empty((0, 1))).shape == (0,)
    with pytest.raises(ValueError): model.fit([[np.nan]], [1])
