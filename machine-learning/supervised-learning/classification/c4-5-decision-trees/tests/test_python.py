from collections import Counter
import math
import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest

pytestmark=pytest.mark.ml


def H(labels):
    return -sum(v/len(labels)*math.log2(v/len(labels)) for v in Counter(labels).values())


def oracle(X,y,categories,mdl):
    candidates=[];n=len(y)
    for j in range(X.shape[1]):
        values=sorted(set(X[:,j]));best=None
        if len(values)<2:continue
        tests=[(None,[[i for i in range(n) if X[i,j]==v] for v in values])] if j in categories else [((a+b)/2,[[i for i in range(n) if X[i,j]<=(a+b)/2],[i for i in range(n) if X[i,j]>(a+b)/2]]) for a,b in zip(values,values[1:])]
        for threshold,groups in tests:
            gain=H(y)-sum(len(g)*H([y[i] for i in g]) for g in groups)/n
            split=-sum(len(g)/n*math.log2(len(g)/n) for g in groups)
            if best is None or gain>best[0]+1e-14:best=gain,split,threshold
        gain,split,threshold=best;adjusted=gain-(math.log2(len(values)-1)/n if mdl and j not in categories else 0)
        if adjusted>1e-14:candidates.append((adjusted,adjusted/split,j,threshold,gain,split))
    if not candidates:return None
    average=sum(v[0] for v in candidates)/len(candidates);eligible=[v for v in candidates if v[0]>=average-1e-14 and v[0]>=1e-12]
    best=eligible[0]
    for v in eligible[1:]:
        if v[1]>best[1]+1e-14:best=v
    return best


@pytest.mark.numerical
def test_hand_gain_ratio_continuous_mdl_and_categorical_high_cardinality(algorithm):
    model=algorithm.C45Classifier(max_depth=1).fit([[0],[1],[2],[3]],[0,0,1,1]);node=model.tree_
    assert node.threshold==1.5;assert_allclose(node.gain,1);assert_allclose(node.split_information,1)
    assert_allclose(node.adjusted_gain,1-math.log2(3)/4);assert_allclose(node.gain_ratio,node.adjusted_gain)
    assert_allclose(algorithm.C45Classifier(mdl_correction=False).fit([[0],[1],[2],[3]],[0,0,1,1]).tree_.gain_ratio,1)
    X=np.column_stack((np.arange(8),[0]*4+[1]*4));y=[0]*4+[1]*4
    selected=algorithm.C45Classifier(categorical_features=[0,1]).fit(X,y)
    assert selected.tree_.feature==1  # gain-ratio avoids ID3's equal-gain identifier tie
    assert selected.tree_.categorical


@pytest.mark.numerical
@pytest.mark.parametrize('mdl',[False,True])
def test_exhaustive_seeded_mixed_feature_split_oracle(algorithm,mdl):
    rng=np.random.default_rng(14341)
    for _ in range(50):
        X=rng.integers(-2,3,size=(12,3));y=rng.integers(0,3,size=12);model=algorithm.C45Classifier(categorical_features=[1],max_depth=1,mdl_correction=mdl).fit(X,y)
        expected=oracle(X,y,{1},mdl)
        if H(y)==0 or expected is None:assert model.tree_.feature is None;continue
        node=model.tree_;assert node.feature==expected[2];assert node.threshold==expected[3]
        assert_allclose([node.adjusted_gain,node.gain_ratio,node.gain,node.split_information],[expected[0],expected[1],expected[4],expected[5]],atol=1e-13)


def test_mixed_domains_unseen_fallback_zero_information_missing_and_ownership(algorithm):
    X=np.array([[0.,0],[0,1],[1,2],[1,3]]);y=np.array(['no','no','yes','yes'])
    model=algorithm.C45Classifier(categorical_features=[0]).fit(X,y)
    assert_array_equal(model.predict([[0,99],[1,-1],[2,2]]),['no','yes','no'])
    assert_allclose(model.predict_proba([[2,2]]),[[.5,.5]])
    X[:]=99;y[:]='z';assert_array_equal(model.predict([[0,0],[1,0]]),['no','yes'])
    with pytest.raises(ValueError):model.fit([[np.nan,0]],[0])
    assert_array_equal(model.predict([[0,0],[1,0]]),['no','yes'])
    with pytest.raises(ValueError):model.predict([[.5,0]])
    assert model.pruning_=='none' and model.missing_values_=='reject'
    assert model.predict_proba(np.empty((0,2))).shape==(0,2)
    assert algorithm.C45Classifier().fit(np.ones((4,2)),[0,1,0,1]).n_leaves_==1


@pytest.mark.parametrize('parameters',[{'categorical_features':[0,0]},{'categorical_features':[True]},{'categorical_features':[32]},{'mdl_correction':1},{'max_depth':17},{'min_gain':-1}])
def test_invalid_parameters(algorithm,parameters):
    with pytest.raises(ValueError):algorithm.C45Classifier(**parameters)
