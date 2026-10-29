import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


@pytest.mark.oracle
@pytest.mark.numerical
def test_newton_leaf_and_regularized_gain_hand_calculation(ensemble_support):
    cls=ensemble_support.load('xgboost').XGBoostRegressor
    X=np.arange(4.)[:,None];y=np.array([0.,0.,4.,4.])
    model=cls(n_estimators=1,learning_rate=.5,max_depth=1,reg_lambda=2,gamma=.25).fit(X,y)
    root=model.estimators_[0]
    # F0=2, g=[2,2,-2,-2], Hleaf=2, lambda=2 => leaf +/-1.
    assert root.feature==0 and root.threshold==1.5
    assert_allclose([root.left.value,root.right.value],[-1,1])
    assert_allclose(root.gain,.5*(16/4+16/4)-.25)
    assert_allclose(model.predict(X),[1.5,1.5,2.5,2.5])
    assert_allclose(root.gradient_sum,0);assert root.hessian_sum==4
    blocked=cls(n_estimators=1,gamma=100).fit(X,y)
    assert blocked.estimators_[0].feature is None
    child_block=cls(n_estimators=1,min_child_weight=3).fit(X,y)
    assert child_block.estimators_[0].feature is None


@pytest.mark.oracle
@pytest.mark.numerical
def test_second_derivative_and_all_split_objectives(ensemble_support):
    rng=np.random.default_rng(15031);X=rng.normal(size=(9,2));y=rng.normal(size=9)
    model=ensemble_support.load('xgboost').XGBoostRegressor(n_estimators=1,max_depth=1,reg_lambda=.7,gamma=.1).fit(X,y)
    gradient=np.full(9,y.mean())-y
    options=[]
    for j in range(2):
        values=np.unique(X[:,j])
        for a,b in zip(values[:-1],values[1:]):
            threshold=(a+b)/2;mask=X[:,j]<=threshold
            G1=sum(gradient[mask]);G2=sum(gradient[~mask]);H1=sum(mask);H2=sum(~mask)
            gain=.5*(G1**2/(H1+.7)+G2**2/(H2+.7)-sum(gradient)**2/(9+.7))-.1
            options.append((gain,j,threshold))
    expected=max(options);root=model.estimators_[0]
    if expected[0]>0:assert_allclose(root.gain,expected[0]);assert root.feature==expected[1];assert_allclose(root.threshold,expected[2])
    f=np.array([.2,-.7]);target=np.array([1.,2.]);eps=1e-3
    L=lambda f:float(np.sum((f-target)**2)/2)
    for i in range(2):
        step=eps*np.eye(2)[i]
        assert_allclose((L(f+step)-L(f-step))/(2*eps),f[i]-target[i],atol=1e-9)
        assert_allclose((L(f+step)-2*L(f)+L(f-step))/eps**2,1,atol=1e-8)


@pytest.mark.oracle
def test_sampling_stage_and_lambda_zero_agree_with_gbm(ensemble_support):
    rng=np.random.default_rng(15032);X=rng.normal(size=(16,3));y=X[:,0]*2+X[:,1]
    cls=ensemble_support.load('xgboost').XGBoostRegressor
    a=cls(n_estimators=3,subsample=.6,colsample_bytree=.5,random_state=17).fit(X,y)
    b=cls(n_estimators=3,subsample=.6,colsample_bytree=.5,random_state=17).fit(X,y)
    for rows,cols in zip(a.estimators_samples_,a.estimators_features_):assert len(rows)==10 and len(set(rows))==10 and len(cols)==2
    assert_allclose(a.predict(X),b.predict(X));assert_allclose(list(a.staged_predict(X))[-1],a.predict(X))
    plain=cls(n_estimators=3,reg_lambda=0,gamma=0,learning_rate=.3).fit(X,y)
    reference=ensemble_support.load('gradient-boosting-machine').GradientBoostingRegressor(n_estimators=3,learning_rate=.3).fit(X,y)
    assert_allclose(plain.predict(X),reference.predict(X),atol=1e-12)


@pytest.mark.numerical
def test_large_finite_data_constant_and_regularization(ensemble_support):
    cls=ensemble_support.load('xgboost').XGBoostRegressor
    X=np.array([[-1e12],[-1.],[1.],[1e12]]);y=np.array([-1e11,-2e10,2e10,1e11])
    model=cls(n_estimators=5).fit(X,y);assert np.isfinite(model.predict(X)).all()
    const=cls().fit(X,[.1]*4);assert len(const.estimators_)==0;assert_array_equal(const.predict(X),[.1]*4)
    small=cls(n_estimators=1,reg_lambda=0).fit(X,y);large=cls(n_estimators=1,reg_lambda=100).fit(X,y)
    assert np.linalg.norm(large.predict(X)) < np.linalg.norm(small.predict(X))


@pytest.mark.parametrize('kwargs',[{'gamma':-1},{'reg_lambda':-1},{'min_child_weight':-1},{'subsample':0},{'colsample_bytree':2},{'learning_rate':0},{'max_depth':7}])
def test_invalid_hyperparameters(ensemble_support,kwargs):
    with pytest.raises(ValueError):ensemble_support.load('xgboost').XGBoostRegressor(**kwargs)


@pytest.mark.reference
def test_zero_regularization_against_external_gradient_boosting(ensemble_support):
    from sklearn.ensemble import GradientBoostingRegressor
    X=np.arange(19.)[:,None];y=np.sin(X[:,0])+.2*X[:,0]
    ours=ensemble_support.load('xgboost').XGBoostRegressor(n_estimators=4,max_depth=2,reg_lambda=0,gamma=0,learning_rate=.2).fit(X,y)
    ref=GradientBoostingRegressor(n_estimators=4,max_depth=2,learning_rate=.2,random_state=0).fit(X,y)
    assert_allclose(ours.predict(X),ref.predict(X),atol=1e-12)
