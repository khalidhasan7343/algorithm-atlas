import math
import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
from sklearn.naive_bayes import GaussianNB as Reference

pytestmark=pytest.mark.ml


@pytest.mark.numerical
def test_hand_gaussian_likelihood_posterior_and_priors(algorithm):
    X=np.array([[0.],[1],[5],[6]]);y=['a','a','b','b']
    model=algorithm.GaussianNaiveBayes(priors=[.8,.2]).fit(X,y)
    query=np.array([[0.],[3],[6]])
    expected=np.array([[math.log(prior)-.5*(math.log(2*math.pi*(.25+model.epsilon_))+(q[0]-mean)**2/(.25+model.epsilon_)) for prior,mean in ((.8,.5),(.2,5.5))] for q in query])
    assert_allclose(model.decision_function(query),expected,atol=1e-12)
    weights=np.exp(expected-expected.max(axis=1,keepdims=True));weights/=weights.sum(axis=1,keepdims=True)
    assert_allclose(model.predict_proba(query),weights,atol=1e-12)
    assert_array_equal(model.classes_,['a','b'])


@pytest.mark.reference
@pytest.mark.parametrize('seed',[14211,14212,14213])
def test_seeded_reference_with_matched_variance_floor(algorithm,seed):
    rng=np.random.default_rng(seed);X=rng.normal(size=(90,5))*3;y=np.repeat([-4,2,9],30);X+=y[:,None]/3
    query=rng.normal(size=(17,5))*4
    model=algorithm.GaussianNaiveBayes(var_smoothing=1e-5,priors=[.2,.3,.5]).fit(X,y)
    reference=Reference(var_smoothing=model.epsilon_/np.var(X,axis=0).max(),priors=[.2,.3,.5]).fit(X,y)
    assert_allclose(model.theta_,reference.theta_,atol=1e-12)
    assert_allclose(model.var_,reference.var_,atol=1e-12)
    assert_allclose(model.predict_proba(query),reference.predict_proba(query),atol=1e-12,rtol=1e-10)
    assert_array_equal(model.predict(query),reference.predict(query))


@pytest.mark.numerical
def test_zero_variance_tiny_classes_imbalance_and_high_dimensional_offsets(algorithm):
    X=np.full((4,128),1e9); y=[0,1,1,1]
    model=algorithm.GaussianNaiveBayes().fit(X,y)
    assert_allclose(model.var_,1e-9)
    assert_allclose(model.predict_proba(X),np.tile([.25,.75],(4,1)),atol=1e-11)
    assert_array_equal(model.predict(X),[1]*4)
    probability=model.predict_proba(np.full((1,128),1e9+1e6))
    assert np.isfinite(probability).all();assert_allclose(probability.sum(axis=1),1)
    single=algorithm.GaussianNaiveBayes().fit([[1,2]],['only'])
    assert_allclose(single.predict_proba([[100,200]]),[[1]])


def test_transactional_state_empty_outputs_and_invalid_data(algorithm):
    X=np.array([[0.],[1],[5],[6]]);saved=X.copy();model=algorithm.GaussianNaiveBayes()
    with pytest.raises(ValueError):model.predict(X)
    assert model.fit(X,['a','a','b','b']) is model
    before=model.predict_proba(X)
    with pytest.raises(ValueError):model.fit([[np.inf]],[0])
    assert_allclose(model.predict_proba(X),before);assert_array_equal(X,saved)
    assert model.predict_proba(np.empty((0,1))).shape==(0,2)
    with pytest.raises(ValueError):model.predict([[1,2]])


@pytest.mark.parametrize('value',[0,-1,1e-13,2,np.inf,True])
def test_invalid_smoothing(algorithm,value):
    with pytest.raises(ValueError):algorithm.GaussianNaiveBayes(var_smoothing=value)


@pytest.mark.parametrize('prior',[[1],[-1,2],[0,1],[.2,.2],[np.nan,1]])
def test_invalid_class_priors(algorithm,prior):
    with pytest.raises(ValueError):algorithm.GaussianNaiveBayes(priors=prior).fit([[0],[1]],[0,1])
