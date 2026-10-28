import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
from sklearn.naive_bayes import BernoulliNB as Reference

pytestmark=pytest.mark.ml


@pytest.mark.numerical
def test_hand_likelihood_presence_absence_and_all_zero_one_queries(algorithm):
    X=[[1,0],[1,0],[0,1],[0,1]];y=['a','a','b','b']
    model=algorithm.BernoulliNaiveBayes(binarize=None).fit(X,y)
    query=np.array([[1,0],[0,1],[0,0],[1,1]])
    p=np.array([[.75,.25],[.25,.75]])
    raw=np.array([[.5*np.prod(p[k]**row*(1-p[k])**(1-row)) for k in range(2)] for row in query])
    assert_allclose(model.predict_proba(query),raw/raw.sum(axis=1,keepdims=True),atol=1e-14)
    assert_allclose(model.predict_proba(query)[:2],[[.9,.1],[.1,.9]])
    # Presence-only scoring favors a; correct absence evidence changes it to b.
    absence=algorithm.BernoulliNaiveBayes(binarize=None).fit([[1,1],[1,1],[1,0],[0,0]],['a','a','b','b'])
    assert absence.predict([[1,0]])[0]=='b'


@pytest.mark.reference
@pytest.mark.parametrize('threshold',[None,0.0,.5])
@pytest.mark.parametrize('alpha',[1e-9,1.0])
def test_seeded_binary_and_threshold_reference(algorithm,threshold,alpha):
    rng=np.random.default_rng(14231);X=rng.integers(0,2,size=(48,9)).astype(float) if threshold is None else rng.normal(size=(48,9));y=np.repeat([-5,2,9],16);query=X[:13].copy()
    model=algorithm.BernoulliNaiveBayes(alpha,binarize=threshold,priors=[.1,.2,.7]).fit(X,y)
    reference=Reference(alpha=alpha,binarize=threshold,class_prior=[.1,.2,.7],force_alpha=True).fit(X,y)
    assert_allclose(model.feature_log_prob_,reference.feature_log_prob_,atol=1e-12)
    assert_allclose(model.predict_proba(query),reference.predict_proba(query),atol=1e-11,rtol=1e-9)
    assert_array_equal(model.predict(query),reference.predict(query))


@pytest.mark.numerical
def test_exact_threshold_single_class_constant_features_and_tiny_smoothing(algorithm):
    model=algorithm.BernoulliNaiveBayes(1e-9,binarize=.5).fit([[.5],[np.nextafter(.5,1)]],[0,1])
    assert_array_equal(model.predict([[.5],[np.nextafter(.5,1)]]),[0,1])
    single=algorithm.BernoulliNaiveBayes(1e-9,binarize=None).fit(np.ones((20,128)),['a']*20)
    assert np.isfinite(single.decision_function(np.zeros((1,128)))).all()
    assert_allclose(single.predict_proba(np.zeros((1,128))),[[1]])
    with pytest.raises(ValueError):algorithm.BernoulliNaiveBayes(binarize=None).fit([[.5]],[0])


def test_transactional_owned_fit_and_empty_prediction(algorithm):
    X=np.array([[1.,0],[0,1]]);y=np.array(['a','b']);model=algorithm.BernoulliNaiveBayes(binarize=None)
    with pytest.raises(ValueError):model.predict(X)
    assert model.fit(X,y) is model
    before=model.predict_proba(X);saved=X.copy()
    with pytest.raises(ValueError):model.fit([[.2,0],[0,1]],y)
    assert_allclose(model.predict_proba(saved),before)
    X[:]=9;y[:]='z';assert_allclose(model.predict_proba(saved),before)
    assert model.predict_proba(np.empty((0,2))).shape==(0,2)
    with pytest.raises(ValueError):model.predict([[.2,0]])


@pytest.mark.parametrize('parameters',[{'alpha':0},{'alpha':True},{'alpha':np.nan},{'binarize':np.inf},{'binarize':True}])
def test_invalid_parameters(algorithm,parameters):
    with pytest.raises(ValueError):algorithm.BernoulliNaiveBayes(**parameters)
