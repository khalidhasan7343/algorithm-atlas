import math
import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis as Reference

pytestmark=pytest.mark.ml


@pytest.mark.numerical
def test_hand_unequal_gaussian_variances_quadratic_boundary(algorithm):
    X=np.array([[-math.sqrt(.5)],[math.sqrt(.5)],[-math.sqrt(2)],[math.sqrt(2)]]);y=['narrow','narrow','wide','wide']
    model=algorithm.QuadraticDiscriminantAnalysis(reg_param=0).fit(X,y)
    assert_allclose(model.covariance_[:,0,0],[1,4],atol=1e-14)
    query=np.array([[-2.],[0],[2.]])
    expected=np.array([[math.log(.5)-.5*(math.log(v)+x[0]**2/v) for v in (1,4)] for x in query])
    assert_allclose(model.decision_function(query),expected,atol=1e-13)
    assert_array_equal(model.predict(query),['wide','narrow','wide'])
    boundary=math.sqrt((8/3)*math.log(2));scores=model.decision_function([[boundary]])
    assert_allclose(scores[:,0],scores[:,1],atol=1e-13)


@pytest.mark.reference
@pytest.mark.parametrize('reg',[0,.1,.7,1.])
@pytest.mark.parametrize('seed',[14421,14422])
def test_seeded_multiclass_covariance_regularization_reference(algorithm,reg,seed):
    rng=np.random.default_rng(seed);X=np.vstack([rng.normal(size=(25,3)) @ np.diag([1+k,.5+k/2,2-k/2])+k for k in range(3)]);y=np.repeat([-4,2,9],25);query=rng.normal(size=(13,3))
    model=algorithm.QuadraticDiscriminantAnalysis(reg_param=reg,priors=[.2,.3,.5]).fit(X,y)
    reference=Reference(reg_param=reg,priors=[.2,.3,.5],store_covariance=True).fit(X,y)
    assert_allclose(model.covariance_,reference.covariance_,atol=1e-12)
    assert_allclose(model.predict_proba(query),reference.predict_proba(query),atol=1e-12,rtol=1e-10)
    assert_array_equal(model.predict(query),reference.predict(query))


@pytest.mark.numerical
def test_independent_full_gaussian_scores_via_slogdet_and_solve(algorithm):
    rng=np.random.default_rng(14423);X=rng.normal(size=(30,2));y=np.repeat([0,1,2],10);X+=y[:,None];query=rng.normal(size=(8,2))
    model=algorithm.QuadraticDiscriminantAnalysis(reg_param=.2).fit(X,y)
    expected=[]
    for row in query:
        scores=[]
        for k in range(3):
            samples=X[y==k];mu=np.mean(samples,axis=0);cov=.8*np.cov(samples,rowvar=False,ddof=1)+.2*np.eye(2);sign,logdet=np.linalg.slogdet(cov);assert sign==1
            diff=row-mu;scores.append(math.log(1/3)-.5*(logdet+diff @ np.linalg.solve(cov,diff)))
        expected.append(scores)
    assert_allclose(model.decision_function(query),expected,atol=1e-12)


@pytest.mark.numerical
def test_singular_near_singular_regularization_and_large_offset(algorithm):
    X=np.array([[0.,0],[1,1],[3,3],[4,4]]);y=[0,0,1,1]
    with pytest.raises(ValueError):algorithm.QuadraticDiscriminantAnalysis(reg_param=0).fit(X,y)
    model=algorithm.QuadraticDiscriminantAnalysis(reg_param=.01).fit(X,y)
    shifted=algorithm.QuadraticDiscriminantAnalysis(reg_param=.01).fit(X+1e9,y)
    assert_allclose(model.predict_proba(X),shifted.predict_proba(X+1e9),atol=1e-11)
    assert np.all(np.linalg.eigvalsh(model.covariance_)>0)
    near=np.column_stack((np.arange(6.),np.arange(6.)+1e-12*np.array([-1,1,-1,1,-1,1])))
    with pytest.raises(ValueError):algorithm.QuadraticDiscriminantAnalysis(reg_param=0).fit(near,[0,0,0,1,1,1])
    assert np.isfinite(algorithm.QuadraticDiscriminantAnalysis(reg_param=.01).fit(near,[0,0,0,1,1,1]).predict_proba(near)).all()
    with pytest.raises(ValueError):algorithm.QuadraticDiscriminantAnalysis().fit([[0],[1],[2]],[0,1,1])


def test_owned_state_failed_fit_and_empty_prediction(algorithm):
    X=np.array([[-2.],[-1],[1],[2]]);model=algorithm.QuadraticDiscriminantAnalysis()
    with pytest.raises(ValueError):model.predict(X)
    assert model.fit(X,['a','a','b','b']) is model
    before=model.predict_proba(X);saved=X.copy();X[:]=99
    assert_allclose(model.predict_proba(saved),before)
    with pytest.raises(ValueError):model.fit([[1],[2]],[0,1])
    assert_allclose(model.predict_proba(saved),before)
    assert model.predict_proba(np.empty((0,1))).shape==(0,2)


@pytest.mark.parametrize('value',[-1,1.1,True,np.inf])
def test_invalid_regularization(algorithm,value):
    with pytest.raises(ValueError):algorithm.QuadraticDiscriminantAnalysis(reg_param=value)
