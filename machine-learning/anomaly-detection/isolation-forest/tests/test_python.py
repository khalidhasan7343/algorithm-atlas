from fractions import Fraction
import numpy as np
from numpy.testing import assert_allclose
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.oracle
@pytest.mark.parametrize('n',[0,1,2,3,4,17,256])
def test_harmonic_normalization_matches_exact_rational(b12,n):
    expected=0 if n<=1 else 2*sum((Fraction(1,k) for k in range(1,n)),Fraction())-Fraction(2*(n-1),n)
    assert_allclose(b12.load('isolation-forest').expected_path_length(n),float(expected),atol=2e-14,rtol=1e-14)

@pytest.mark.oracle
def test_manual_tree_leaf_correction_and_path_lengths(b12):
    m=b12.load('isolation-forest');N=m.IsolationNode
    tree=N(5,0,0,0.,N(2,1),N(3,1,0,2.,N(1,2),N(2,2)))
    assert_allclose(m.path_lengths([[-1.],[1.],[3.]],tree),[2.,2.,3.],atol=0,rtol=0)
    assert_allclose(m.path_lengths([[-1.]],N(3)),[float(Fraction(5,3))])

@pytest.mark.oracle
def test_ensemble_average_normalized_scores_independent_walk(b12):
    X=np.array([[-2.],[-1.],[0.],[.2],[1.],[5.]])
    m=b12.load('isolation-forest').IsolationForest(7,max_samples=5,max_depth=2,random_state=17).fit(X)
    def walk(row,node):
        depth=0
        while node.feature is not None:
            node=node.left if row[node.feature]<node.split else node.right;depth+=1
        correction=0 if node.count<2 else float(2*sum(Fraction(1,j) for j in range(1,node.count))-Fraction(2*(node.count-1),node.count))
        return depth+correction
    paths=np.array([[walk(row,tree) for row in X] for tree in m.trees_]);normalizer=float(2*sum(Fraction(1,j) for j in range(1,5))-Fraction(8,5))
    assert_allclose(m.training_path_lengths_,paths.mean(axis=0),atol=1e-14)
    assert_allclose(m.anomaly_scores(X),2**(-paths.mean(axis=0)/normalizer),atol=1e-14)
    assert_allclose(m.score_samples(X),-m.anomaly_scores(X))
    assert_allclose(m.decision_function(X),m.threshold_-m.anomaly_scores(X))

@pytest.mark.parametrize('depth',[0,1,3,32])
def test_tree_depth_nonempty_splits_leaf_counts_and_sampling(b12,depth):
    X=np.c_[np.arange(20.),np.zeros(20),np.arange(20.)**2]
    model=b12.load('isolation-forest').IsolationForest(4,max_samples=13,max_depth=depth,random_state=8).fit(X)
    def inspect(node,data):
        assert node.count==len(data) and node.depth<=depth
        if node.feature is None:return [node.count]
        assert node.feature in (0,2)
        column=data[:,node.feature];assert column.min()<node.split<=column.max()
        mask=column<node.split;assert mask.any() and (~mask).any()
        return inspect(node.left,data[mask])+inspect(node.right,data[~mask])
    for tree,indices in zip(model.trees_,model.sample_indices_):
        assert len(indices)==len(np.unique(indices))==13
        assert sum(inspect(tree,X[indices]))==13
    if depth==0:assert_allclose(model.anomaly_scores(X),.5)

@pytest.mark.parametrize('n',[1,2,8])
def test_constant_duplicate_and_degenerate_normalization(b12,n):
    cls=b12.load('isolation-forest').IsolationForest
    model=cls(5,contamination=.5).fit(np.ones((n,2)))
    assert_allclose(model.anomaly_scores([[1.,1.],[100.,100.]]),.5)
    assert_allclose(model.labels_,1)
    single=cls(3,max_samples=1).fit(np.arange(max(2,n),dtype=float)[:,None])
    assert_allclose(single.anomaly_scores([[0.],[1e6]]),.5)

@pytest.mark.numerical
@pytest.mark.parametrize('X',[np.array([[1e12],[np.nextafter(1e12,np.inf)]]),np.array([[-1e-300],[1e-300]]),np.array([[0.],[np.nextafter(0.,1.)]])])
def test_float_endpoint_splits_keep_both_branches(b12,X):
    # Stay inside the declared absolute feature bound.
    if X.max()>1e12:X=np.array([[np.nextafter(1e12,-np.inf)],[1e12]])
    model=b12.load('isolation-forest').IsolationForest(4,max_samples=2).fit(X)
    assert all(t.left.count==t.right.count==1 for t in model.trees_)
    assert np.isfinite(model.anomaly_scores(X)).all()

@pytest.mark.parametrize('seed',[21,22,23])
def test_seeded_isolated_point_ranking_and_repeated_fit(b12,seed):
    rng=np.random.default_rng(seed);X=np.r_[rng.normal(0,.2,(60,2)),[[8.,8.]]]
    cls=b12.load('isolation-forest').IsolationForest
    a=cls(48,max_samples=48,contamination=.05,random_state=seed).fit(X)
    b=cls(48,max_samples=48,contamination=.05,random_state=seed).fit(X)
    assert_allclose(a.anomaly_scores_,b.anomaly_scores_,atol=0,rtol=0)
    assert a.anomaly_scores_[-1]>np.quantile(a.anomaly_scores_[:-1],.95)
    assert a.predict(X)[-1]==-1
    assert_allclose(a.fit_predict(X),b.labels_)

@pytest.mark.reference
def test_sklearn_independent_forest_ranking_orientation(b12):
    from sklearn.ensemble import IsolationForest
    rng=np.random.default_rng(241);X=np.r_[rng.normal(0,.2,(100,2)),rng.normal(7,.1,(6,2))];labels=np.r_[np.ones(100,dtype=int),-np.ones(6,dtype=int)]
    ours=b12.load('isolation-forest').IsolationForest(64,max_samples=64,random_state=17).fit(X)
    reference=IsolationForest(n_estimators=64,max_samples=64,random_state=17).fit(X)
    a=b12.anomaly_metrics(labels,ours.predict(X),ours.anomaly_scores(X))['roc_auc']
    b=b12.anomaly_metrics(labels,reference.predict(X),-reference.score_samples(X))['roc_auc']
    assert a>.98 and b>.98
    # Random trees and exact versus approximated harmonic corrections are not bitwise-equivalent.

@pytest.mark.parametrize('kwargs',[dict(n_estimators=0),dict(n_estimators=129),dict(n_estimators=True),dict(max_samples=0),dict(max_samples=257),dict(max_samples=1.5),dict(max_samples='x'),dict(max_depth=-1),dict(max_depth=33),dict(contamination=0),dict(contamination=.6),dict(contamination=np.nan),dict(random_state=-1)])
def test_invalid_hyperparameters(b12,kwargs):
    with pytest.raises(ValueError):b12.load('isolation-forest').IsolationForest(**kwargs)

def test_invalid_counts_features_unfitted_and_ownership(b12):
    cls=b12.load('isolation-forest').IsolationForest
    with pytest.raises(ValueError):cls(max_samples=3).fit([[0.],[1.]])
    with pytest.raises(ValueError):cls().predict([[1.]])
    X=np.arange(8.)[:,None];model=cls(4).fit(X);before=model.anomaly_scores(X);X[:]=100
    assert_allclose(model.anomaly_scores(np.arange(8.)[:,None]),before)
    result=model.anomaly_scores(np.arange(8.)[:,None]);result[:]=100
    assert_allclose(model.anomaly_scores(np.arange(8.)[:,None]),before)
    with pytest.raises(ValueError):model.fit([[np.nan]])
    assert_allclose(model.anomaly_scores(np.arange(8.)[:,None]),before)
    with pytest.raises(ValueError):model.predict([[0.,1.]])
    assert model.predict(np.empty((0,1))).shape==(0,)
