import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
from sklearn.naive_bayes import MultinomialNB as Reference

pytestmark=pytest.mark.ml


@pytest.mark.numerical
def test_hand_count_likelihood_additive_smoothing_and_zero_row(algorithm):
    X=[[3,0],[2,1],[0,3],[1,2]];y=['left','left','right','right']
    model=algorithm.MultinomialNaiveBayes().fit(X,y)
    assert_allclose(np.exp(model.feature_log_prob_),[[.75,.25],[.25,.75]])
    assert_allclose(model.feature_count_,[[5,1],[1,5]])
    query=np.array([[2,0],[0,2],[0,0]])
    raw=np.array([[.5*.75**2,.5*.25**2],[.5*.25**2,.5*.75**2],[.5,.5]])
    assert_allclose(model.predict_proba(query),raw/raw.sum(axis=1,keepdims=True),atol=1e-14)
    assert_array_equal(model.predict(query),['left','right','left'])
    high=algorithm.MultinomialNaiveBayes(100).fit(X,y)
    assert abs(high.predict_proba([[2,0]])[0,0]-.5)<abs(model.predict_proba([[2,0]])[0,0]-.5)


@pytest.mark.reference
@pytest.mark.parametrize('alpha',[1e-9,.3,5])
def test_seeded_count_and_fractional_count_reference(algorithm,alpha):
    rng=np.random.default_rng(14221);X=rng.poisson(2,size=(45,7)).astype(float)/2;y=np.repeat(['a','b','c'],15);query=rng.poisson(3,size=(16,7)).astype(float)/3
    model=algorithm.MultinomialNaiveBayes(alpha,priors=[.1,.3,.6]).fit(X,y)
    reference=Reference(alpha=alpha,class_prior=[.1,.3,.6],force_alpha=True).fit(X,y)
    assert_allclose(model.feature_log_prob_,reference.feature_log_prob_,atol=1e-13)
    assert_allclose(model.predict_proba(query),reference.predict_proba(query),atol=1e-12,rtol=1e-10)
    assert_array_equal(model.predict(query),reference.predict(query))


@pytest.mark.numerical
def test_all_zero_data_imbalance_large_counts_and_underflow_avoidance(algorithm):
    model=algorithm.MultinomialNaiveBayes().fit(np.zeros((5,128)),[0,0,1,1,1])
    assert_allclose(model.predict_proba(np.zeros((1,128))),[[.4,.6]])
    assert np.isfinite(model.decision_function(np.full((1,128),1e12))).all()
    assert_allclose(model.predict_proba(np.full((1,128),1e12)).sum(axis=1),1)
    assert algorithm.MultinomialNaiveBayes().fit([[0,0]],['only']).predict([[1,2]])[0]=='only'


def test_owned_state_and_failed_refit(algorithm):
    X=np.array([[3.,0],[0,3]]);y=np.array([0,1]);model=algorithm.MultinomialNaiveBayes()
    with pytest.raises(ValueError):model.predict(X)
    assert model.fit(X,y) is model
    before=model.predict_proba(X);saved=X.copy()
    with pytest.raises(ValueError):model.fit([[-1,0],[0,1]],y)
    assert_allclose(model.predict_proba(saved),before)
    X[:]=100;y[:]=7
    assert_allclose(model.predict_proba(saved),before)
    assert model.predict_proba(np.empty((0,2))).shape==(0,2)
    with pytest.raises(ValueError):model.predict([[-1,0]])


@pytest.mark.parametrize('alpha',[0,-1,1e-10,True,np.inf])
def test_invalid_smoothing(algorithm,alpha):
    with pytest.raises(ValueError):algorithm.MultinomialNaiveBayes(alpha)


@pytest.mark.parametrize('X',[[[-1]],[[np.inf]],[[np.nan]],[[True]],[[1j]],[1,2]])
def test_invalid_feature_domain(algorithm,X):
    with pytest.raises(ValueError):algorithm.MultinomialNaiveBayes().fit(X,[0])
