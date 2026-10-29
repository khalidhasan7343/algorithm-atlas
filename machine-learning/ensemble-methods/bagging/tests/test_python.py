import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest

pytestmark = pytest.mark.ml


@pytest.mark.oracle
@pytest.mark.parametrize('task', ['Classifier','Regressor'])
def test_exact_bootstrap_seed_aggregation_and_oob(ensemble_support,task):
    s=ensemble_support;cls=getattr(s.load('bagging'),'Bagging'+task)
    X=np.arange(8.)[:,None];y=np.array(['a','a','b','b','a','a','b','b']) if task=='Classifier' else np.array([0.,1.,4.,5.,2.,7.,3.,8.])
    model=cls(n_estimators=7,max_samples=6,max_depth=2,random_state=15001,oob_score=True).fit(X,y)
    rng=np.random.default_rng(15001);counts=np.zeros(8,int)
    independent=[]
    for base,indices,seed in zip(model.estimators_,model.estimators_samples_,model.estimator_seeds_):
        assert_array_equal(indices,rng.integers(8,size=6));assert seed==int(rng.integers(2**32))
        assert len(indices)==6 and len(set(indices))<=6
        counts[np.setdiff1d(np.arange(8),indices)]+=1
        independent.append(base.predict(X))
    assert len({id(x) for x in model.estimators_})==7
    assert_array_equal(model.oob_counts_,counts)
    assert any(len(set(v))<len(v) for v in model.estimators_samples_)
    if task=='Classifier':
        p=np.column_stack([np.mean(np.array(independent)==c,axis=0) for c in model.classes_])
        assert_allclose(model.predict_proba(X),p);assert_array_equal(model.predict(X),model.classes_[p.argmax(axis=1)])
    else:assert_allclose(model.predict(X),np.mean(independent,axis=0))
    for i in range(8):
        eligible=[b for b,idx in zip(model.estimators_,model.estimators_samples_) if i not in idx]
        if not eligible:continue
        if task=='Regressor':assert_allclose(model.oob_prediction_[i],np.mean([b.predict(X[i:i+1])[0] for b in eligible]))
        else:
            pred=[b.predict(X[i:i+1])[0] for b in eligible]
            assert_allclose(model.oob_decision_function_[i],[pred.count(c)/len(pred) for c in model.classes_])


@pytest.mark.parametrize('count',[0,-1,1.5,True,65])
def test_invalid_counts(ensemble_support,count):
    with pytest.raises(ValueError):ensemble_support.load('bagging').BaggingClassifier(n_estimators=count)


@pytest.mark.parametrize('size',[0,-1,513,0.,1.5,True,np.nan])
def test_invalid_sample_sizes(ensemble_support,size):
    with pytest.raises(ValueError):ensemble_support.load('bagging').BaggingRegressor(max_samples=size).fit([[0],[1]],[0,1])


def test_single_estimator_and_uncovered_oob(ensemble_support):
    model=ensemble_support.load('bagging').BaggingRegressor(n_estimators=1,oob_score=True).fit([[0]],[.1])
    assert_allclose(model.predict([[1]]),[.1]);assert np.isnan(model.oob_prediction_[0]);assert model.oob_score_ is None


@pytest.mark.oracle
def test_custom_factories_and_lexical_tie(ensemble_support):
    class Constant:
        def __init__(self,label):self.label=label
        def fit(self,X,y):return self
        def predict(self,X):return np.full(len(X),self.label)
    labels=iter(['z','a']);factory=lambda seed:Constant(next(labels))
    model=ensemble_support.load('bagging').BaggingClassifier(factory,n_estimators=2).fit([[0],[1]],['a','z'])
    assert_array_equal(model.predict([[9]]),['a']);assert_allclose(model.predict_proba([[9]]),[[.5,.5]])


@pytest.mark.reference
@pytest.mark.parametrize('task',['Classifier','Regressor'])
def test_independent_sklearn_bases_on_actual_bootstrap_cohorts(ensemble_support,task):
    from sklearn.tree import DecisionTreeClassifier,DecisionTreeRegressor
    s=ensemble_support;X=np.arange(17.)[:,None];y=np.sin(X[:,0]) if task=='Regressor' else (X[:,0]>8).astype(int)
    model=getattr(s.load('bagging'),'Bagging'+task)(n_estimators=4,max_depth=2,random_state=51).fit(X,y)
    predictions=[]
    for indices in model.estimators_samples_:
        ref=(DecisionTreeClassifier if task=='Classifier' else DecisionTreeRegressor)(max_depth=2,random_state=0).fit(X[indices],y[indices])
        predictions.append(ref.predict(X))
    if task=='Regressor':assert_allclose(model.predict(X),np.mean(predictions,axis=0),atol=1e-13)
    else:
        p=np.column_stack([np.mean(np.array(predictions)==c,axis=0) for c in model.classes_])
        assert_allclose(model.predict_proba(X),p)
