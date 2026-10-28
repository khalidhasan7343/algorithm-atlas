from collections import Counter
import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
from sklearn.tree import DecisionTreeClassifier

pytestmark=pytest.mark.ml


def impurity(labels):
    counts=Counter(labels);return 1-sum((n/len(labels))**2 for n in counts.values())


def brute_split(X,y,leaf):
    best=None
    for j in range(X.shape[1]):
        values=sorted(set(X[:,j]))
        for lower,upper in zip(values,values[1:]):
            t=(lower+upper)/2;left=[y[i] for i in range(len(y)) if X[i,j]<=t];right=[y[i] for i in range(len(y)) if X[i,j]>t]
            if min(len(left),len(right))<leaf:continue
            score=(len(left)*impurity(left)+len(right)*impurity(right))/len(y)
            if best is None or score<best[0]-1e-14:best=score,j,t
    return best


@pytest.mark.numerical
def test_gini_analytical_threshold_probabilities_and_zero_gain_xor(algorithm):
    assert algorithm.gini([2,2])==pytest.approx(.5);assert algorithm.gini([0,0])==0
    model=algorithm.CARTClassifier(max_depth=1).fit([[0],[1],[2],[3]],['a','a','b','b'])
    assert model.tree_.threshold==1.5 and model.tree_.feature==0
    assert_allclose(model.predict_proba([[.5],[2.5]]),[[1,0],[0,1]])
    X=[[0,0],[0,1],[1,0],[1,1]];y=[0,1,1,0]
    xor=algorithm.CARTClassifier(max_depth=2).fit(X,y);assert_array_equal(xor.predict(X),y)
    assert xor.tree_.feature==0
    blocked=algorithm.CARTClassifier(min_impurity_decrease=.50001).fit([[0],[1],[2],[3]],[0,0,1,1])
    assert blocked.n_leaves_==1


@pytest.mark.numerical
def test_seeded_exhaustive_multiclass_stump_oracle(algorithm):
    rng=np.random.default_rng(14321)
    for _ in range(70):
        X=rng.integers(-3,4,size=(12,3));y=rng.integers(0,3,size=12);leaf=int(rng.integers(1,4));model=algorithm.CARTClassifier(max_depth=1,min_samples_leaf=leaf).fit(X,y)
        expected=brute_split(X,y,leaf)
        if impurity(y)==0 or expected is None:assert model.tree_.feature is None;continue
        assert model.tree_.feature==expected[1] and model.tree_.threshold==expected[2]
        actual=(model.tree_.left.n_samples*model.tree_.left.impurity+model.tree_.right.n_samples*model.tree_.right.impurity)/len(y)
        assert_allclose(actual,expected[0],atol=1e-14)


@pytest.mark.reference
@pytest.mark.parametrize('depth',[1,2,4])
def test_reference_on_ordered_unique_feature_partitions(algorithm,depth):
    rng=np.random.default_rng(14322);X=np.sort(rng.uniform(-3,3,60))[:,None];y=np.where(X[:,0]<-1,0,np.where(X[:,0]<1,1,2));query=np.linspace(-4,4,51)[:,None]
    model=algorithm.CARTClassifier(max_depth=depth,min_samples_leaf=2).fit(X,y)
    reference=DecisionTreeClassifier(criterion='gini',max_depth=depth,min_samples_leaf=2,random_state=14322).fit(X,y)
    assert_array_equal(model.predict(query),reference.predict(query));assert_allclose(model.predict_proba(query),reference.predict_proba(query),atol=1e-14)


def test_constant_duplicate_conflicts_ownership_failure_and_adjacent_values(algorithm):
    X=np.ones((4,2));model=algorithm.CARTClassifier().fit(X,['b','a','b','a'])
    assert model.n_leaves_==1;assert_array_equal(model.predict([[1,1]]),['a']);assert_allclose(model.predict_proba([[1,1]]),[[.5,.5]])
    with pytest.raises(ValueError):model.fit([[np.nan,0]],['a'])
    assert_allclose(model.predict_proba([[1,1]]),[[.5,.5]])
    X[:]=99;assert_allclose(model.predict_proba([[1,1]]),[[.5,.5]])
    near=np.nextafter(1.,2.);tiny=algorithm.CARTClassifier().fit([[1.],[near]],[0,1]);assert tiny.tree_.threshold==1.
    assert_array_equal(tiny.predict([[1.],[near]]),[0,1]);assert tiny.predict_proba(np.empty((0,1))).shape==(0,2)
    with pytest.raises(ValueError):algorithm.CARTClassifier().predict([[1]])


@pytest.mark.parametrize('parameters',[{'max_depth':0},{'max_depth':17},{'min_samples_leaf':0},{'min_impurity_decrease':-1},{'max_depth':True}])
def test_invalid_parameters(algorithm,parameters):
    with pytest.raises(ValueError):algorithm.CARTClassifier(**parameters)
