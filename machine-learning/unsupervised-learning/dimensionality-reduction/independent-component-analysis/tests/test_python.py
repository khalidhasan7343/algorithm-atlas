import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest
pytestmark=pytest.mark.ml

def sources(seed):
    rng=np.random.default_rng(seed)
    S=np.column_stack([rng.uniform(-1,1,500),rng.laplace(size=500)])
    S-=S.mean(0);S/=S.std(0)
    return S,S@np.array([[1.,.5],[.3,1.5]]).T

@pytest.mark.oracle
@pytest.mark.numerical
@pytest.mark.parametrize('seed',[17014,17015,17016])
def test_source_recovery_whitening_and_reconstruction(b5,seed):
    S,X=sources(seed);m=b5.load('independent-component-analysis').FastICA(tol=1e-8,random_state=seed).fit(X)
    Z=m.transform(X);white=(X-m.mean_)@m.whitening_.T
    assert_allclose(white.T@white/len(X),np.eye(2),atol=1e-12)
    assert_allclose(Z.mean(0),0,atol=1e-12);assert_allclose(Z.T@Z/len(X),np.eye(2),atol=1e-11)
    C=abs(np.corrcoef(S.T,Z.T)[:2,2:]);assert max(min(C[0,0],C[1,1]),min(C[0,1],C[1,0]))>.97
    assert_allclose(m.inverse_transform(Z),X,atol=1e-11)
    assert m.converged_ and m.n_iter_<=1000

@pytest.mark.reference
def test_sklearn_permutation_sign_scale_invariant(b5):
    from sklearn.decomposition import FastICA
    _,X=sources(17017);ours=b5.load('independent-component-analysis').FastICA(tol=1e-8).fit_transform(X)
    ref=FastICA(n_components=2,algorithm='parallel',whiten='unit-variance',fun='logcosh',tol=1e-8,max_iter=1000,random_state=0).fit_transform(X)
    C=abs(np.corrcoef(ours.T,ref.T)[:2,2:]);assert max(min(C[0,0],C[1,1]),min(C[0,1],C[1,0]))>.999

@pytest.mark.numerical
def test_rank_deficiency_constant_and_near_degenerate(b5):
    cls=b5.load('independent-component-analysis').FastICA
    with pytest.raises(ValueError):cls().fit(np.ones((5,2)))
    with pytest.raises(ValueError):cls().fit([[1,2],[2,4],[3,6]])
    _,X=sources(17018);X[:,1]=X[:,0]+1e-8*X[:,1]
    with pytest.raises(ValueError):cls().fit(X)
    one=cls(1).fit(np.linspace(-1,1,20)[:,None]);assert one.transform([[0]]).shape==(1,1)

def test_seed_nonconvergence_and_atomic_refit(b5):
    cls=b5.load('independent-component-analysis').FastICA;_,X=sources(17019)
    m=cls().fit(X);assert_array_equal(m.transform(X),cls().fit_transform(X));old=m.components_.copy()
    m.max_iter=1;m.tol=1e-12
    with pytest.raises(b5.ConvergenceError):m.fit(X)
    assert_array_equal(m.components_,old)

@pytest.mark.parametrize('kwargs',[{'tol':0},{'max_iter':0},{'random_state':True},{'n_components':0}])
def test_invalid_parameters(b5,kwargs):
    with pytest.raises(ValueError):b5.load('independent-component-analysis').FastICA(**kwargs)
