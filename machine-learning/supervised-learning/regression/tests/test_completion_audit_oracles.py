"""Additional requested mathematical coverage; no fitted model serves as its oracle."""
import importlib.util
from itertools import product
from pathlib import Path

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest
from sklearn.svm import SVR as ReferenceSVR

spec = importlib.util.spec_from_file_location("regression_completion_oracles", Path(__file__).parents[1]/"support.py")
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)
pytestmark = pytest.mark.ml


@pytest.mark.numerical
@pytest.mark.parametrize("degree", [1, 3, 8])
def test_polynomial_exact_functions_and_independently_enumerated_basis(degree):
    rng = np.random.default_rng(13321)
    X = rng.uniform(-.8, .8, size=(80, 2))
    terms = [power for power in product(range(degree+1), repeat=2) if 1 <= sum(power) <= degree]
    terms.sort(key=lambda power: (sum(power), -power[0]))
    expected = np.column_stack([np.prod(X**power, axis=1) for power in terms])
    target = 1 + 2*X[:, 0] - X[:, 1]
    if degree >= 3:
        target += 3*X[:, 0]**3 - 2*X[:, 0]*X[:, 1]**2
    model = support.load("polynomial-regression").PolynomialRegression(degree).fit(X, target)
    assert_array_equal(model.powers_, terms)
    assert_allclose(model.transform(X), expected, atol=2e-16, rtol=1e-14)
    assert_allclose(model.predict(X), target, atol=2e-11, rtol=1e-11)


@pytest.mark.numerical
def test_ridge_feature_scaling_requires_squared_penalty_mapping():
    X = np.array([[-2.], [-1.], [1.], [2.]])
    y = 3*X[:, 0]+5
    ridge = support.load("ridge-regression").RidgeRegression
    original = ridge(alpha=2).fit(X, y)
    scaled = ridge(alpha=200).fit(10*X, y)
    assert_allclose(scaled.coef_*10, original.coef_, atol=1e-13)
    assert_allclose(scaled.predict(10*X), original.predict(X), atol=1e-12)


@pytest.mark.numerical
def test_sparse_lasso_elastic_net_orthogonal_closed_forms_and_units():
    # Hadamard columns have zero means and X.T X/n == I; no fitted oracle.
    X = np.array([[1,1,1], [1,-1,-1], [-1,1,-1], [-1,-1,1]], dtype=float)
    beta = np.array([3., .2, -2.]);y = 7+X @ beta
    lasso = support.load("lasso-regression").LassoRegression(alpha=.5, tol=1e-12).fit(X, y)
    assert_allclose(lasso.coef_, [2.5,0,-1.5], atol=1e-13)
    elastic = support.load("elastic-net").ElasticNetRegression(alpha=1,l1_ratio=.5,tol=1e-12).fit(X,y)
    assert_allclose(elastic.coef_, np.array([2.5,0,-1.5])/1.5, atol=1e-13)
    scaled_lasso = support.load("lasso-regression").LassoRegression(alpha=5,tol=1e-12).fit(10*X,y)
    assert_allclose(scaled_lasso.coef_*10,lasso.coef_,atol=1e-13)
    assert_allclose(lasso.intercept_,7,atol=1e-13)


@pytest.mark.numerical
def test_tree_resolves_tiny_piecewise_targets_without_false_purity():
    X = [[0.], [1.], [2.], [3.]]
    y = [0., 0., 1e-200, 1e-200]
    tree = support.load("decision-tree-regression").DecisionTreeRegression(max_depth=1).fit(X, y)
    assert tree.n_leaves_ == 2 and tree.tree_.threshold == 1.5
    assert_allclose(tree.predict(X), y, atol=0, rtol=1e-14)
    assert tree.score(X, y) == 1
    # Its true MSE gain is far below this positive original-unit threshold.
    blocked = support.load("decision-tree-regression").DecisionTreeRegression(min_impurity_decrease=1e-300).fit(X, y)
    assert blocked.n_leaves_ == 1


@pytest.mark.numerical
def test_tree_target_rescaling_preserves_partitions_and_gain_units():
    X = [[0.], [1.], [2.], [3.]]
    cls = support.load("decision-tree-regression").DecisionTreeRegression
    regular = cls(max_depth=1, min_impurity_decrease=.2).fit(X, [0.,0.,1.,1.])
    tiny = cls(max_depth=1, min_impurity_decrease=.2e-200).fit(X, [0.,0.,1e-100,1e-100])
    assert regular.tree_.threshold == tiny.tree_.threshold == 1.5
    assert_allclose(tiny.predict(X)/1e-100,regular.predict(X),atol=1e-14)
    constant = cls().fit(X, [.1]*4)
    assert_allclose(constant.predict(X), [.1]*4, atol=0, rtol=0)


@pytest.mark.reference
def test_svr_outliers_C_epsilon_effects_and_independent_primal_values():
    X = np.linspace(-1,1,9)[:,None];y = X[:,0].copy();y[-1]=5
    cls = support.load("support-vector-regression").SupportVectorRegression
    models=[]
    for C in (.1, 3.):
        model = cls(C=C,epsilon=.1,kernel="linear",tol=1e-8,max_iter=30000).fit(X,y)
        reference = ReferenceSVR(C=C,epsilon=.1,kernel="linear",tol=1e-10,shrinking=False).fit(X,y)
        query=np.array([[-.75],[.25],[1.25]])
        assert_allclose(model.predict(query),reference.predict(query),atol=2e-4,rtol=2e-4)
        tube_loss=float(np.maximum(np.abs(y-model.predict(X))-.1,0).sum())
        primal=float(model.coef_ @ model.coef_/2+C*tube_loss)
        assert_allclose(primal,model.primal_objective_,atol=1e-6,rtol=1e-7)
        models.append((model,tube_loss))
    assert models[1][1] <= models[0][1]+1e-6
    assert np.linalg.norm(models[1][0].coef_) >= np.linalg.norm(models[0][0].coef_)-1e-6
    wide=cls(C=3,epsilon=10,kernel="linear",tol=1e-9).fit(X,y)
    assert_allclose(wide.dual_coef_,0,atol=1e-10)
    assert wide.primal_objective_==pytest.approx(0,abs=1e-12)
