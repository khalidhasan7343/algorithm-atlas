import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as Reference

pytestmark=pytest.mark.ml


@pytest.mark.numerical
def test_known_shared_covariance_linear_scores_and_priors(algorithm):
    X=np.array([[-2.],[-1],[1],[2]]);y=['a','a','b','b'];model=algorithm.LinearDiscriminantAnalysis(reg=0).fit(X,y)
    assert_allclose(model.means_,[[-1.5],[1.5]]);assert_allclose(model.covariance_,[[.25]])
    query=np.array([[-1.],[0],[1.]])
    expected=query @ np.array([[-6.,6.]])+(-4.5+np.log(.5))
    assert_allclose(model.decision_function(query),expected,atol=1e-13)
    assert_array_equal(model.predict(query),['a','a','b'])
    prior=algorithm.LinearDiscriminantAnalysis(reg=0,priors=[.9,.1]).fit(X,y)
    assert_array_equal(prior.predict([[0]]),['a'])
    assert_allclose(prior.predict_proba([[0]]),[[.9,.1]],atol=1e-13)


@pytest.mark.reference
@pytest.mark.parametrize('seed',[14411,14412,14413])
@pytest.mark.parametrize('priors',[None,[.1,.3,.6]])
def test_seeded_multiclass_shared_covariance_reference(algorithm,seed,priors):
    rng=np.random.default_rng(seed);X=rng.normal(size=(90,4));y=np.repeat([-4,2,9],30);X+=np.repeat([-1.,0.,1.],30)[:,None];query=rng.normal(size=(17,4))
    model=algorithm.LinearDiscriminantAnalysis(reg=0,priors=priors).fit(X,y)
    reference=Reference(solver='lsqr',priors=priors).fit(X,y)
    assert_allclose(model.covariance_,reference.covariance_,atol=1e-13)
    assert_allclose(model.predict_proba(query),reference.predict_proba(query),atol=1e-12,rtol=1e-10)
    assert_array_equal(model.predict(query),reference.predict(query))


@pytest.mark.numerical
def test_singular_covariance_regularization_small_classes_and_translation(algorithm):
    X=np.array([[0.,0],[1,1],[3,3],[4,4]]);y=[0,0,1,1]
    with pytest.raises(ValueError):algorithm.LinearDiscriminantAnalysis(reg=0).fit(X,y)
    model=algorithm.LinearDiscriminantAnalysis(reg=.1).fit(X,y)
    assert np.linalg.eigvalsh(model.covariance_).min()>0
    shifted=algorithm.LinearDiscriminantAnalysis(reg=.1).fit(X+1e9,y)
    assert_allclose(model.predict_proba(X),shifted.predict_proba(X+1e9),atol=1e-11)
    single_per_class=algorithm.LinearDiscriminantAnalysis().fit([[0,0],[1,1]],[0,1])
    assert_array_equal(single_per_class.predict([[0,0],[1,1]]),[0,1])
    near=np.column_stack((np.arange(6.),np.arange(6.)+1e-12*np.array([-1,1,-1,1,-1,1])))
    with pytest.raises(ValueError):algorithm.LinearDiscriminantAnalysis(reg=0).fit(near,[0,0,0,1,1,1])
    assert np.isfinite(algorithm.LinearDiscriminantAnalysis(reg=1e-4).fit(near,[0,0,0,1,1,1]).predict_proba(near)).all()


def test_transactional_state_and_shape_contract(algorithm):
    X=np.array([[-2.],[-1],[1],[2]]);y=np.array(['a','a','b','b']);model=algorithm.LinearDiscriminantAnalysis()
    with pytest.raises(ValueError):model.predict(X)
    assert model.fit(X,y) is model
    before=model.predict_proba(X);saved=X.copy()
    with pytest.raises(ValueError):model.fit([[np.inf]],[0])
    assert_allclose(model.predict_proba(saved),before)
    X[:]=100;y[:]='z';assert_allclose(model.predict_proba(saved),before)
    assert model.predict_proba(np.empty((0,1))).shape==(0,2)
    with pytest.raises(ValueError):model.predict([[0,1]])


@pytest.mark.parametrize('parameters',[{'reg':-1},{'reg':True},{'reg':np.nan},{'priors':[0,1]},{'priors':[.2,.2]}])
def test_invalid_parameters_and_priors(algorithm,parameters):
    with pytest.raises(ValueError):algorithm.LinearDiscriminantAnalysis(**parameters).fit([[0],[1]],[0,1])
