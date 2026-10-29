"""Cross-ensemble contracts and adversarial inputs; no fitting helper is an oracle."""
import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest

pytestmark=pytest.mark.ml
SPECS=[('bagging','BaggingClassifier'),('bagging','BaggingRegressor'),('random-forest','RandomForestClassifier'),('random-forest','RandomForestRegressor'),('adaboost','AdaBoostClassifier'),('gradient-boosting-machine','GradientBoostingRegressor'),('xgboost','XGBoostRegressor'),('catboost','CatBoostRegressor'),('voting-classifiers','VotingClassifier'),('stacking','StackingClassifier'),('stacking','StackingRegressor')]


def model(s,name,cls):
    kwargs={'n_estimators':3} if name not in ('voting-classifiers','stacking') else {}
    return getattr(s.load(name),cls)(**kwargs)


@pytest.mark.parametrize('name,cls',SPECS)
def test_copy_determinism_empty_query_and_failed_refit(ensemble_support,name,cls):
    s=ensemble_support;rng=np.random.default_rng(15100);X=rng.normal(size=(12,2));y=np.repeat(['a','b'],6) if cls.endswith('Classifier') else .5*X[:,0]+X[:,1]
    original=X.copy();truth=y.copy();np.random.seed(381);state=np.random.get_state()
    a=model(s,name,cls).fit(X,y);b=model(s,name,cls).fit(X,y)
    assert_array_equal(X,original);assert_array_equal(y,truth)
    after=np.random.get_state();assert state[0]==after[0];assert_array_equal(state[1],after[1]);assert state[2:]==after[2:]
    pred=a.predict(X);assert_array_equal(pred,b.predict(X));assert a.predict(np.empty((0,2))).shape==(0,)
    if cls.endswith('Classifier'):
        p=a.predict_proba(X);assert p.shape==(12,2);assert_allclose(p.sum(axis=1),1);assert np.isfinite(p).all()
        assert a.predict_proba(np.empty((0,2))).shape==(0,2)
    assert np.isfinite(a.score(X,y))
    with pytest.raises(ValueError):a.fit(X,y[:-1])
    assert_array_equal(a.predict(X),pred)
    X[:]=0;y[:]=y[0]
    assert_array_equal(a.predict(original),pred)


@pytest.mark.parametrize('name,cls',SPECS)
@pytest.mark.parametrize('bad_X,bad_y',[
    ([],[]),([[0],[1]],[0]),([0,1],[0,1]),([[],[]],[0,1]),([[np.nan],[1]],[0,1]),
    ([[np.inf],[1]],[0,1]),([[True],[False]],[0,1]),([[0],[1]],[[0],[1]]),([[0],[1]],[np.nan,1]),
])
def test_invalid_fitting_shapes_and_values(ensemble_support,name,cls,bad_X,bad_y):
    with pytest.raises((ValueError,TypeError)):model(ensemble_support,name,cls).fit(bad_X,bad_y)


@pytest.mark.parametrize('name,cls',SPECS)
def test_unfitted_and_wrong_query_shape(ensemble_support,name,cls):
    m=model(ensemble_support,name,cls)
    with pytest.raises(ValueError):m.predict([[0,1]])
    X=np.arange(24.).reshape(12,2);y=np.repeat(['a','b'],6) if cls.endswith('Classifier') else np.arange(12.)
    m.fit(X,y)
    for bad in ([1,2],[[0]],[[np.inf,0]]):
        with pytest.raises(ValueError):m.predict(bad)


@pytest.mark.parametrize('name,cls',[spec for spec in SPECS if spec[1].endswith('Classifier')])
@pytest.mark.parametrize('labels',[[0.,1.],[True,False],['a',1],['','a']])
def test_strict_labels(ensemble_support,name,cls,labels):
    with pytest.raises(ValueError):model(ensemble_support,name,cls).fit([[0],[1]],labels)


@pytest.mark.numerical
@pytest.mark.oracle
def test_weighted_tree_against_exhaustive_weighted_gini(ensemble_support):
    s=ensemble_support;tree=s.module_at('atlas_ensemble_tree',s.ROOT/'tree.py')
    X=np.arange(5.)[:,None];y=np.array([0,1,0,1,1]);w=np.array([.1,.2,.4,.1,.2])
    model=tree.WeightedTree(task='classification',max_depth=1).fit(X,y,w)
    def impurity(indices):
        counts=np.array([sum(w[i] for i in indices if y[i]==c) for c in (0,1)])
        return counts.sum()-sum(counts**2)/counts.sum()
    scores=[impurity(range(j))+impurity(range(j,5)) for j in range(1,5)]
    assert model.tree_.threshold==np.argmin(scores)+.5
    assert_allclose(model.tree_.value,[.5,.5])


@pytest.mark.numerical
@pytest.mark.reference
@pytest.mark.parametrize('task',['classification','regression'])
@pytest.mark.parametrize('seed',[15111,15112,15113])
def test_seeded_weighted_tree_external_oracle(ensemble_support,task,seed):
    from sklearn.tree import DecisionTreeClassifier,DecisionTreeRegressor
    s=ensemble_support;tree=s.module_at('atlas_ensemble_tree',s.ROOT/'tree.py')
    rng=np.random.default_rng(seed);X=rng.uniform(-2,2,(19,3));query=rng.uniform(-2,2,(11,3))
    y=(X[:,0]+X[:,1]>0).astype(int) if task=='classification' else X[:,0]+X[:,1]**2
    weight=rng.uniform(.1,2,19);weight[0]=0
    ours=tree.WeightedTree(task=task,max_depth=2).fit(X,y,weight)
    ref=(DecisionTreeClassifier if task=='classification' else DecisionTreeRegressor)(max_depth=2,random_state=0).fit(X,y,sample_weight=weight)
    # Equal training partitions can have tied split rules on different features;
    # off-training routing then legitimately differs (recorded seed 15113).
    positive=weight>0
    assert_allclose(ours.predict(X[positive]).astype(float),ref.predict(X[positive]).astype(float),atol=1e-11)
    assert np.isfinite(ours.predict(query).astype(float)).all()
    if task=='classification':
        assert_allclose(ours.predict_proba(X[positive]),ref.predict_proba(X[positive]),atol=1e-12)
        assert_allclose(ours.predict_proba(query).sum(axis=1),1)
    else:
        ours_loss=sum(weight[positive]*(y[positive]-ours.predict(X[positive]))**2)
        ref_loss=sum(weight[positive]*(y[positive]-ref.predict(X[positive]))**2)
        assert_allclose(ours_loss,ref_loss,atol=1e-11)
        assert np.all(ours.predict(query)>=y[positive].min()) and np.all(ours.predict(query)<=y[positive].max())


@pytest.mark.parametrize('name,cls',SPECS)
def test_resource_caps_and_hyperparameter_refit(ensemble_support,name,cls):
    m=model(ensemble_support,name,cls)
    for X,y in ((np.zeros((513,1)),np.zeros(513)),(np.zeros((2,33)),np.zeros(2))):
        with pytest.raises(ValueError):m.fit(X,y)
    if name not in ('voting-classifiers','stacking'):
        X=np.arange(24.).reshape(12,2);y=np.repeat(['a','b'],6) if cls.endswith('Classifier') else np.arange(12.)
        m.fit(X,y);before=m.predict(X);m.n_estimators=0
        with pytest.raises(ValueError):m.fit(X,y)
        assert_array_equal(m.predict(X),before)
