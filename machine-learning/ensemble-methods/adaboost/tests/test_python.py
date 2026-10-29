import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


@pytest.mark.oracle
@pytest.mark.numerical
def test_hand_computed_weight_rounds(ensemble_support):
    X=np.arange(4.)[:,None];y=np.array(['a','b','a','b'])
    model=ensemble_support.load('adaboost').AdaBoostClassifier(n_estimators=3,learning_rate=.5).fit(X,y)
    weight=np.full(4,.25)
    for base,alpha,error,stored in zip(model.estimators_,model.estimator_weights_,model.estimator_errors_,model.sample_weight_history_):
        assert_allclose(stored,weight)
        wrong=base.predict(X)!=y;e=sum(weight[i] for i in range(4) if wrong[i])
        assert_allclose(error,e)
        if not e:assert alpha==1;break
        expected=.5*np.log((1-e)/e)
        assert_allclose(alpha,expected)
        weight=weight*np.exp(expected*wrong);weight/=weight.sum()
    staged=list(model.staged_predict(X));assert_array_equal(staged[-1],model.predict(X))


@pytest.mark.reference
def test_samme_matches_aligned_sklearn(ensemble_support):
    from sklearn.ensemble import AdaBoostClassifier
    from sklearn.tree import DecisionTreeClassifier
    X=np.arange(10.)[:,None];y=np.array([0,0,1,1,2,2,0,1,2,2])
    ours=ensemble_support.load('adaboost').AdaBoostClassifier(n_estimators=4,learning_rate=.4).fit(X,y)
    ref=AdaBoostClassifier(estimator=DecisionTreeClassifier(max_depth=1),n_estimators=4,learning_rate=.4,random_state=0).fit(X,y)
    assert_array_equal(ours.predict(X),ref.predict(X))
    assert_allclose(ours.estimator_weights_,ref.estimator_weights_[:len(ours.estimators_)],atol=1e-13)


@pytest.mark.parametrize('weights',[[0,0],[1,-1],[np.nan,1],[np.inf,1],[1],[True,False]])
def test_invalid_weights(ensemble_support,weights):
    with pytest.raises(ValueError):ensemble_support.load('adaboost').AdaBoostClassifier().fit([[0],[1]],[0,1],weights)


@pytest.mark.numerical
def test_perfect_chance_zero_and_extreme_weights(ensemble_support):
    cls=ensemble_support.load('adaboost').AdaBoostClassifier
    perfect=cls().fit([[0],[1]],['n','y'],[1e300,1e300]);assert len(perfect.estimators_)==1;assert perfect.stop_reason_=='perfect weak learner'
    assert_allclose(perfect.predict_proba([[0],[1]]).sum(axis=1),1)
    with pytest.raises(ValueError,match='chance'):cls().fit([[0],[0]],[0,1])
    with pytest.raises(ValueError,match='chance'):cls().fit([[0],[0],[0]],[0,1,2])
    model=cls(n_estimators=64).fit([[0],[1],[2],[3]],[0,1,0,1],[0,1e-300,1,1])
    assert np.isfinite(model.estimator_weights_).all()
    assert_allclose([v.sum() for v in model.sample_weight_history_],1)


def test_worse_than_chance_guard_is_explicit(ensemble_support,monkeypatch):
    module=ensemble_support.load('adaboost')
    class AlwaysWrong:
        def __init__(self,**kwargs):pass
        def fit(self,X,y,w):self.labels=np.array(y);return self
        def predict(self,X):return 1-self.labels
    monkeypatch.setattr(module.tree,'WeightedTree',AlwaysWrong)
    with pytest.raises(ValueError,match='chance'):module.AdaBoostClassifier().fit([[0],[1]],[0,1])
