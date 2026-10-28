import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
from sklearn.svm import SVC

pytestmark=pytest.mark.ml


@pytest.mark.numerical
def test_analytical_margin_primal_dual_and_support_conditions(algorithm):
    X=np.array([[-2.],[-1],[1],[2]]);y=np.array([-1,-1,1,1])
    model=algorithm.SupportVectorMachine(tol=1e-9).fit(X,y)
    assert_allclose(model.coef_,[1],atol=1e-8);assert_allclose(model.intercept_,0,atol=1e-8)
    assert_allclose(model.primal_objective_,.5,atol=1e-8);assert_allclose(model.dual_objective_,.5,atol=1e-8)
    assert model.duality_gap_<1e-8 and model.equality_residual_<1e-12
    assert_array_equal(model.support_,[1,2]);assert_allclose(model.alpha_,[0,.5,.5,0],atol=1e-8)
    assert_allclose(y*model.decision_function(X),[2,1,1,2],atol=1e-8)
    assert not hasattr(model,'predict_proba')


@pytest.mark.reference
@pytest.mark.parametrize('C',[.2,1.,4.])
@pytest.mark.parametrize('seed',[14311,14312])
def test_seeded_nonseparable_linear_reference_and_kkt(algorithm,C,seed):
    rng=np.random.default_rng(seed);X=rng.normal(size=(30,3));y=np.where(X @ [1.,-.8,.3]+rng.normal(0,.7,30)>0,7,-4);query=rng.normal(size=(19,3))
    model=algorithm.SupportVectorMachine(C,tol=1e-8,max_iter=40000).fit(X,y)
    reference=SVC(C=C,kernel='linear',tol=1e-10,shrinking=False).fit(X,y)
    assert_allclose(model.decision_function(query),reference.decision_function(query),atol=2e-4,rtol=2e-4)
    assert_array_equal(model.predict(query),reference.predict(query))
    assert np.min(model.alpha_)>=0 and np.max(model.alpha_)<=C
    assert abs(np.where(y==7,1,-1) @ model.alpha_)<1e-9
    margin=np.where(y==7,1,-1)*model.decision_function(X);free=(model.alpha_>1e-6)&(model.alpha_<C-1e-6)
    assert_allclose(margin[free],1,atol=2e-5)
    assert np.all(margin[model.alpha_<1e-6]>=1-2e-5)
    assert np.all(margin[model.alpha_>C-1e-6]<=1+2e-5)
    assert model.duality_gap_<=model.tol*(1+abs(model.primal_objective_)+abs(model.dual_objective_))


@pytest.mark.numerical
def test_constant_features_imbalance_duplicates_and_translation(algorithm):
    model=algorithm.SupportVectorMachine(tol=1e-9).fit(np.ones((4,2)),['a','a','a','b'])
    assert_array_equal(model.predict([[1,1]]),['a']);assert_allclose(model.coef_,0,atol=1e-12)
    X=np.array([[-2.],[-1],[1],[2]]);y=['a','a','b','b']
    base=algorithm.SupportVectorMachine().fit(X,y);shifted=algorithm.SupportVectorMachine().fit(X+1e9,y)
    assert_allclose(base.decision_function(X),shifted.decision_function(X+1e9),atol=1e-6)


def test_nonconvergence_failed_refit_owned_state_and_shapes(algorithm):
    X=np.array([[-2.],[-1],[1],[2]]);y=np.array([0,0,1,1]);model=algorithm.SupportVectorMachine()
    with pytest.raises(ValueError):model.predict(X)
    assert model.fit(X,y) is model
    before=model.decision_function(X);model.max_iter=1;model.tol=1e-14
    with pytest.raises(algorithm._support.ConvergenceError):model.fit(X,y)
    assert_allclose(model.decision_function(X),before)
    X[:]=99;y[:]=9
    assert_allclose(model.decision_function([[-2],[-1],[1],[2]]),before)
    assert model.predict(np.empty((0,1))).shape==(0,)
    with pytest.raises(ValueError):model.fit(np.zeros((257,1)),[0]*128+[1]*129)
    with pytest.raises(ValueError):model.predict([[np.inf]])


@pytest.mark.parametrize('parameters',[{'C':0},{'C':-1},{'rho':0},{'tol':0},{'max_iter':False},{'C':np.nan}])
def test_invalid_parameters(algorithm,parameters):
    with pytest.raises(ValueError):algorithm.SupportVectorMachine(**parameters)


@pytest.mark.parametrize('labels',[[0,0],[0,1,2],[True,False],[1.,2.],[1,'1']])
def test_binary_label_restrictions(algorithm,labels):
    with pytest.raises(ValueError):algorithm.SupportVectorMachine().fit([[0],[1]],labels)
