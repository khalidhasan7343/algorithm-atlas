import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


@pytest.mark.oracle
@pytest.mark.numerical
def test_ordered_statistics_exclude_own_and_future_targets(ensemble_support):
    cls=ensemble_support.load('catboost').CatBoostRegressor
    X=[['a',0],['a',1],['b',2],['a',3]];y=np.array([2.,4.,8.,6.])
    model=cls(categorical_features=[0],prior=1,prior_weight=2,n_estimators=2,random_state=4).fit(X,y)
    order=np.random.default_rng(4).permutation(4);assert_array_equal(model.permutation_,order)
    for rank,i in enumerate(order):
        preceding=[j for j in order[:rank] if X[j][0]==X[i][0]]
        expected=(sum(y[j] for j in preceding)+2)/(len(preceding)+2)
        assert_allclose(model.ordered_features_[i,0],expected)
        altered=y.copy();altered[order[rank:]]+=10
        other=cls(categorical_features=[0],prior=1,prior_weight=2,n_estimators=2,random_state=4).fit(X,altered)
        assert_allclose(other.ordered_features_[i],model.ordered_features_[i])
        # Prefix model at rank i excludes current/future targets, including structure.
        for a,b in zip(model.prefix_estimators_[rank],other.prefix_estimators_[rank]):
            assert a.splits==b.splits;assert_allclose(a.values,b.values)
    assert_allclose(model.transform([['a',7],['new',9]])[:,0],[(2+4+6+2)/5,1])


@pytest.mark.oracle
@pytest.mark.numerical
def test_prefix_rounds_by_independent_constant_models(ensemble_support):
    cls=ensemble_support.load('catboost').CatBoostRegressor
    X=np.ones((3,1));y=np.array([1.,3.,5.]);rate=.2;prior=.5
    model=cls(n_estimators=3,learning_rate=rate,prior=prior,random_state=8).fit(X,y)
    target=y[model.permutation_];M=np.full((4,3),prior)
    for t in range(3):
        residual=np.array([target[i]-M[i,i] for i in range(3)])
        assert_allclose(model.ordered_residuals_[t],residual)
        for prefix in range(1,4):M[prefix]+=rate*sum(residual[:prefix])/prefix
    assert_allclose(model.prefix_training_predictions_,M)
    assert_allclose(model.predict([[1],[4]]),[M[3,0]]*2)
    assert_allclose(list(model.staged_predict([[1]]))[-1],model.predict([[1]]))


@pytest.mark.oracle
def test_symmetric_tree_enumeration_and_empty_cells(ensemble_support):
    module=ensemble_support.load('catboost');X=np.array([[0,0],[0,1],[1,0],[1,1.]],float);y=np.array([0.,1.,2.,4.])
    model=module.CatBoostRegressor(n_estimators=1,max_depth=2,learning_rate=1,random_state=0).fit(X,y)
    full=model.estimators_[0];assert len(full.splits)==2
    assert_allclose(full.predict(X),y)
    # Independent root split SSE enumeration, no internal scoring helper.
    scores=[]
    for j in range(2):
        left=y[X[:,j]==0];right=y[X[:,j]==1]
        scores.append(sum((left-left.mean())**2)+sum((right-right.mean())**2))
    assert full.splits[0][0]==int(np.argmin(scores))
    assert np.isfinite(full.values).all()


@pytest.mark.numerical
def test_categories_families_limits_and_numeric_extremes(ensemble_support):
    cls=ensemble_support.load('catboost').CatBoostRegressor
    model=cls(categorical_features=[0],n_estimators=2).fit([['a',-1e12],['b',1e12]],[1e10,-1e10])
    assert np.isfinite(model.predict([['new',0]])).all()
    with pytest.raises(ValueError):model.predict([[1,0]])
    with pytest.raises(ValueError):cls().fit(np.zeros((65,1)),np.zeros(65))
    with pytest.raises(ValueError):cls().fit(np.zeros((2,9)),[0,1])
    with pytest.raises(ValueError):cls(categorical_features=[0]).fit([['a'],[1]],[0,1])
    with pytest.raises(ValueError):cls(categorical_features=[0,0]).fit([['a'],['b']],[0,1])
    with pytest.raises(ValueError):cls().fit([[np.nan]],[1])
    with pytest.raises(ValueError):cls().fit([[True]],[1])


@pytest.mark.parametrize('kwargs',[{'n_estimators':17},{'max_depth':4},{'learning_rate':0},{'prior_weight':0},{'prior':np.inf},{'random_state':-1}])
def test_invalid_parameters(ensemble_support,kwargs):
    with pytest.raises(ValueError):ensemble_support.load('catboost').CatBoostRegressor(**kwargs)
