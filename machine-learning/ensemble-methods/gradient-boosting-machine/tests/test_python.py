import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


@pytest.mark.oracle
@pytest.mark.numerical
def test_analytical_stages_shrinkage_and_gradients(ensemble_support):
    cls=ensemble_support.load('gradient-boosting-machine').GradientBoostingRegressor
    X=np.arange(4.)[:,None];y=np.array([0.,0.,4.,4.]);rate=.25
    model=cls(n_estimators=3,learning_rate=rate,max_depth=1).fit(X,y)
    assert model.init_==2
    expected=np.full(4,2.)
    for i,prediction in enumerate(model.staged_predict(X)):
        residual=y-expected;assert_allclose(model.residual_history_[i],residual)
        # Exact two constant leaves, so the fitted negative gradient is residual.
        expected+=rate*residual;assert_allclose(prediction,expected)
    assert_allclose(model.predict(X),expected);assert np.all(np.diff(model.train_loss_)<=1e-14)
    f=np.array([1.,2.,3.,4.]);epsilon=1e-5
    numeric=np.array([(np.sum((y-(f+epsilon*np.eye(4)[i]))**2)/2-np.sum((y-(f-epsilon*np.eye(4)[i]))**2)/2)/(2*epsilon) for i in range(4)])
    assert_allclose(numeric,f-y,atol=1e-9)


@pytest.mark.reference
def test_compatible_sklearn_squared_error(ensemble_support):
    from sklearn.ensemble import GradientBoostingRegressor
    X=np.arange(16.)[:,None];y=np.sin(X[:,0])
    ours=ensemble_support.load('gradient-boosting-machine').GradientBoostingRegressor(n_estimators=5,max_depth=2,learning_rate=.2).fit(X,y)
    ref=GradientBoostingRegressor(n_estimators=5,max_depth=2,learning_rate=.2,random_state=0).fit(X,y)
    assert_allclose(ours.predict(X),ref.predict(X),atol=1e-12)


@pytest.mark.numerical
@pytest.mark.parametrize('target',[.1,0.,1e-200,1e12])
def test_constant_exact_initialization(ensemble_support,target):
    model=ensemble_support.load('gradient-boosting-machine').GradientBoostingRegressor().fit([[0],[1],[2]],[target]*3)
    assert len(model.estimators_)==0;assert list(model.staged_predict([[1]]))==[]
    assert_array_equal(model.predict([[4],[5]]),[target,target])


@pytest.mark.parametrize('rate',[0,-1,2,np.nan,np.inf,True])
def test_bad_learning_rate(ensemble_support,rate):
    with pytest.raises(ValueError):ensemble_support.load('gradient-boosting-machine').GradientBoostingRegressor(learning_rate=rate)


@pytest.mark.numerical
@pytest.mark.oracle
def test_valid_boundary_targets_can_have_larger_internal_residuals(ensemble_support):
    X=np.arange(3.)[:,None];y=np.array([-1e12,1e12,1e12]);mean=y.mean()
    cls=ensemble_support.load('gradient-boosting-machine').GradientBoostingRegressor
    model=cls(n_estimators=2,learning_rate=.5,max_depth=1).fit(X,y)
    # Two exactly representable tree residual stages: F2=mean+3/4*(y-mean).
    assert_allclose(model.predict(X),mean+.75*(y-mean),rtol=1e-14,atol=1e-3)
    assert np.max(np.abs(model.residual_history_[0]))>1e12
