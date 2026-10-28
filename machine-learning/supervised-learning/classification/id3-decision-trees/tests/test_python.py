from collections import Counter
import math
import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest

pytestmark=pytest.mark.ml


def uncertainty(labels):
    return -sum((v/len(labels))*math.log2(v/len(labels)) for v in Counter(labels).values())


@pytest.mark.numerical
def test_known_play_tennis_entropy_gain_and_unseen_fallback(algorithm):
    X=[[0,0,0,0],[0,0,0,1],[1,0,0,0],[2,1,0,0],[2,2,1,0],[2,2,1,1],[1,2,1,1],[0,1,0,0],[0,2,1,0],[2,1,1,0],[0,1,1,1],[1,1,0,1],[1,0,1,0],[2,1,0,1]]
    y=['no','no','yes','yes','yes','no','yes','no','yes','yes','yes','yes','yes','no']
    model=algorithm.ID3Classifier().fit(X,y)
    assert model.tree_.feature==0;assert_allclose(model.tree_.gain,.2467498197744391,atol=1e-14)
    assert_array_equal(model.predict(X),y)
    assert_allclose(model.predict_proba([[3,0,0,0]]),[[5/14,9/14]],atol=1e-14)
    assert model.predict([[3,0,0,0]])[0]=='yes'
    assert algorithm.entropy([2,2])==pytest.approx(1)
    assert algorithm.entropy([2,1])==pytest.approx(.9182958340544896)
    assert algorithm.entropy([0,0])==0


@pytest.mark.numerical
def test_exhaustive_seeded_categorical_information_gain_oracle(algorithm):
    rng=np.random.default_rng(14331)
    for _ in range(60):
        X=rng.integers(0,3,size=(12,3));y=rng.integers(0,3,size=12);model=algorithm.ID3Classifier(max_depth=1).fit(X,y)
        gains=[]
        for j in range(3):
            groups=[[y[i] for i in range(len(y)) if X[i,j]==v] for v in sorted(set(X[:,j]))]
            if len(groups)>1:gains.append((uncertainty(y)-sum(len(g)*uncertainty(g) for g in groups)/len(y),j))
        if uncertainty(y)==0 or not gains:assert model.tree_.feature is None;continue
        best=gains[0]
        for g in gains[1:]:
            if g[0]>best[0]+1e-14:best=g
        assert model.tree_.feature==best[1];assert_allclose(model.tree_.gain,best[0],atol=1e-14)


def test_feature_exhaustion_conflicts_zero_gain_and_leaf_constraints(algorithm):
    X=[[0,0],[0,1],[1,0],[1,1]];y=[0,1,1,0]
    model=algorithm.ID3Classifier(max_depth=2).fit(X,y);assert_array_equal(model.predict(X),y);assert model.tree_.feature==0
    assert algorithm.ID3Classifier(min_gain=.01).fit(X,y).n_leaves_==1
    conflict=algorithm.ID3Classifier().fit([[0],[0],[1],[1]],['a','b','b','a'])
    assert_allclose(conflict.predict_proba([[0],[1],[2]]),np.full((3,2),.5))
    small=algorithm.ID3Classifier(min_samples_leaf=2).fit([[0],[1],[1]],[0,1,1]);assert small.n_leaves_==1
    with pytest.raises(ValueError):model.fit([[.5,0]],[0])
    assert_array_equal(model.predict(X),y)
    assert model.predict_proba(np.empty((0,2))).shape==(0,2)


@pytest.mark.parametrize('X',[np.arange(65)[:,None],[[.5]],[[np.nan]],[[True]]])
def test_invalid_categorical_domains(algorithm,X):
    with pytest.raises(ValueError):algorithm.ID3Classifier().fit(X,[0]*len(X))


@pytest.mark.parametrize('parameters',[{'max_depth':0},{'min_samples_leaf':0},{'min_gain':-1},{'max_depth':True}])
def test_invalid_parameters(algorithm,parameters):
    with pytest.raises(ValueError):algorithm.ID3Classifier(**parameters)
