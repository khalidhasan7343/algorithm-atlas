import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


class Mean:
    def fit(self,X,y):self.rows=set(X[:,0]);self.mean=float(np.mean(y));self.fit_X=X.copy();return self
    def predict(self,X):return np.full(len(X),self.mean)


class Prior:
    def fit(self,X,y):
        self.rows=set(X[:,0]);self.classes_=np.array(sorted(set(y),reverse=True));self.p=np.array([np.mean(y==c) for c in self.classes_]);return self
    def predict_proba(self,X):return np.tile(self.p,(len(X),1))
    def predict(self,X):return np.full(len(X),self.classes_[np.argmax(self.p)])


@pytest.mark.oracle
@pytest.mark.parametrize('task',['Classifier','Regressor'])
def test_out_of_fold_exclusion_and_full_refits(ensemble_support,task):
    X=np.arange(12.)[:,None];y=np.tile(['a','b'],6) if task=='Classifier' else np.arange(12.)**2
    factory=(lambda seed:Prior()) if task=='Classifier' else (lambda seed:Mean())
    cls=getattr(ensemble_support.load('stacking'),'Stacking'+task)
    model=cls([factory],n_splits=3,random_state=11).fit(X,y)
    assert_array_equal(model.oof_counts_,np.ones(12))
    for held,bases in zip(model.fold_indices_,model.fold_estimators_):
        base=bases[0];train=np.setdiff1d(np.arange(12),held)
        assert base.rows==set(train.astype(float));assert not base.rows & set(held.astype(float))
        if task=='Regressor':assert_allclose(model.oof_predictions_[held,0],y[train].mean())
        else:
            oracle=np.tile([np.mean(y[train]==c) for c in model.classes_],(len(held),1))
            assert_allclose(model.oof_predictions_[held],oracle)
    assert model.estimators_[0].rows==set(np.arange(12.))
    if task=='Classifier':assert_allclose(model.predict_proba([[20],[21]]).sum(axis=1),1)
    else:assert np.isfinite(model.predict([[20],[21]])).all()


@pytest.mark.reference
def test_regression_against_identical_explicit_folds(ensemble_support):
    from sklearn.ensemble import StackingRegressor
    from sklearn.linear_model import LinearRegression,Ridge
    from sklearn.tree import DecisionTreeRegressor
    s=ensemble_support;tree=s.module_at('atlas_ensemble_tree',s.ROOT/'tree.py');X=np.arange(18.)[:,None];y=.3*X[:,0]+np.sin(X[:,0])
    factories=[lambda seed:s.regression.load('linear-regression').LinearRegression(),lambda seed:tree.WeightedTree(max_depth=2,random_state=seed)]
    model=s.load('stacking').StackingRegressor(factories,n_splits=3,random_state=5).fit(X,y)
    cv=[(np.setdiff1d(np.arange(18),held),held) for held in model.fold_indices_]
    ref=StackingRegressor([('linear',LinearRegression()),('tree',DecisionTreeRegressor(max_depth=2,random_state=0))],final_estimator=Ridge(alpha=1),cv=cv).fit(X,y)
    assert_allclose(model.predict(X),ref.predict(X),atol=1e-10)


@pytest.mark.numerical
def test_stratified_minority_boundaries_and_default_models(ensemble_support):
    cls=ensemble_support.load('stacking').StackingClassifier
    with pytest.raises(ValueError):cls(n_splits=3).fit([[0],[1],[2],[3]],['a','a','a','b'])
    model=cls(n_splits=2).fit(np.arange(8.)[:,None],['a']*6+['b']*2)
    for held in model.fold_indices_:assert sum(np.array(['a']*6+['b']*2)[held]=='b')==1
    assert np.isfinite(model.predict_proba([[2],[7]])).all()


@pytest.mark.parametrize('kwargs',[{'n_splits':1},{'n_splits':9},{'n_splits':True},{'random_state':-1}])
def test_invalid_parameters(ensemble_support,kwargs):
    with pytest.raises(ValueError):ensemble_support.load('stacking').StackingRegressor(**kwargs)


def test_factory_reuse_is_rejected(ensemble_support):
    shared=Mean()
    with pytest.raises(ValueError):ensemble_support.load('stacking').StackingRegressor([lambda seed:shared]).fit(np.arange(6.)[:,None],np.arange(6.))
