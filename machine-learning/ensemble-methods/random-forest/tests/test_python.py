import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest

pytestmark=pytest.mark.ml


@pytest.mark.oracle
@pytest.mark.parametrize('task',['Classifier','Regressor'])
def test_feature_subsets_and_aggregation(ensemble_support,task):
    s=ensemble_support;rng=np.random.default_rng(15002);X=rng.normal(size=(28,4));y=(X[:,0]>0).astype(int) if task=='Classifier' else X[:,0]+X[:,1]**2
    model=getattr(s.load('random-forest'),'RandomForest'+task)(n_estimators=5,max_features=2,max_depth=3,random_state=7,oob_score=True).fit(X,y)
    subsets=[]
    def visit(node):
        if node.candidates:assert len(node.candidates)==2;subsets.append(node.candidates)
        if node.feature is not None:
            assert node.feature in node.candidates;visit(node.left);visit(node.right)
    for tree in model.estimators_:visit(tree.tree_)
    assert len(set(subsets))>1
    if task=='Regressor':assert_allclose(model.predict(X),np.mean([t.predict(X) for t in model.estimators_],axis=0))
    else:
        oracle=np.zeros((len(X),len(model.classes_)))
        for t in model.estimators_:
            for j,c in enumerate(t.classes_):oracle[:,np.where(model.classes_==c)[0][0]]+=t.predict_proba(X)[:,j]/5
        assert_allclose(model.predict_proba(X),oracle)


@pytest.mark.reference
@pytest.mark.parametrize('task',['Classifier','Regressor'])
def test_single_tree_aligned_reference(ensemble_support,task):
    from sklearn.tree import DecisionTreeClassifier,DecisionTreeRegressor
    X=np.arange(12.)[:,None];y=np.repeat([0,1,2],4) if task=='Classifier' else np.repeat([1.,4.,8.],4)
    # Compare a single actual bootstrap tree using exactly its sampled cohort.
    cls=getattr(ensemble_support.load('random-forest'),'RandomForest'+task)
    model=cls(n_estimators=1,max_features=None,max_depth=2,random_state=12).fit(X,y)
    indices=model.estimators_samples_[0]
    ref=(DecisionTreeClassifier if task=='Classifier' else DecisionTreeRegressor)(max_depth=2,random_state=0).fit(X[indices],y[indices])
    assert_allclose(model.predict(X).astype(float),ref.predict(X).astype(float))


@pytest.mark.numerical
@pytest.mark.parametrize('task',['Classifier','Regressor'])
def test_constant_features_duplicate_pure_targets(ensemble_support,task):
    model=getattr(ensemble_support.load('random-forest'),'RandomForest'+task)(n_estimators=3).fit(np.ones((5,2)),['same']*5 if task=='Classifier' else [1e-200]*5)
    if task=='Classifier':assert_array_equal(model.predict([[1,1]]),['same']);assert_allclose(model.predict_proba([[1,1]]),[[1]])
    else:assert_allclose(model.predict([[1,1]]),[1e-200],atol=0)


@pytest.mark.parametrize('features',[0,4,True,'log2',.5])
def test_bad_features(ensemble_support,features):
    with pytest.raises(ValueError):ensemble_support.load('random-forest').RandomForestClassifier(max_features=features).fit([[0,1],[1,0]],[0,1])
