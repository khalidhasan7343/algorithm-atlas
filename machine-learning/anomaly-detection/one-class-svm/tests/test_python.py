from itertools import product
import numpy as np
from numpy.testing import assert_allclose
import pytest
pytestmark=pytest.mark.ml


def projection_oracle(values,cap):
    # Independent exhaustive face minimization,not monotone-root clipping.
    v=np.asarray(values,dtype=float);best=None;cost=np.inf
    for states in product((0,1,2),repeat=len(v)):
        a=np.zeros(len(v));a[np.array(states)==1]=cap;free=np.flatnonzero(np.array(states)==2)
        if len(free):
            shift=(v[free].sum()+a.sum()-1)/len(free);a[free]=v[free]-shift
        elif abs(a.sum()-1)>1e-12:continue
        if np.min(a)<-1e-12 or np.max(a)>cap+1e-12:continue
        loss=np.sum((a-v)**2)
        if loss<cost:best,cost=a.copy(),loss
    assert best is not None
    return best

@pytest.mark.oracle
@pytest.mark.parametrize('values,cap',[([.3,-.2,2.,.1],.4),([-1.,.5,1.],.6),([2.,-1.],1.),([0.,0.,0.],1/3),([.1,.2,.3],2.)])
def test_capped_simplex_projection_independent_face_oracle(b12,values,cap):
    module=b12.load('one-class-svm');actual=module.project_capped_simplex(values,cap)
    assert_allclose(actual,projection_oracle(values,cap),atol=2e-13)
    assert_allclose(actual.sum(),1,atol=1e-12)
    assert np.min(actual)>=0 and np.max(actual)<=cap+1e-14
    assert_allclose(module.project_capped_simplex(np.array(values)+10,cap),actual,atol=2e-13)

@pytest.mark.parametrize('values,cap',[([],1),([1,2],.4),([np.nan,0],1),([True,False],1),([101,0],1),([[1,2]],1),([0,1],np.inf)])
def test_invalid_projection_inputs(b12,values,cap):
    with pytest.raises(ValueError):b12.load('one-class-svm').project_capped_simplex(values,cap)

@pytest.mark.oracle
@pytest.mark.numerical
@pytest.mark.parametrize('gamma',[1e-12,.5,1e12])
def test_hand_gram_symmetry_psd_and_kernel_underflow(b12,gamma):
    X=np.array([[0.,0.],[1.,0.],[0.,2.]])
    model=b12.load('one-class-svm').OneClassSVM(gamma=gamma).fit(X)
    distance2=np.array([[0,1,4],[1,0,5],[4,5,0]],dtype=float)
    with np.errstate(under='ignore'):expected=np.exp(-gamma*distance2)
    assert_allclose(model.gram_,expected,atol=1e-15)
    assert_allclose(model.gram_,model.gram_.T,atol=0,rtol=0)
    assert_allclose(np.diag(model.gram_),1)
    assert np.linalg.eigvalsh(model.gram_).min()>=-1e-12

@pytest.mark.oracle
@pytest.mark.parametrize('nu',[1e-4,.2,.7,1.])
def test_analytic_symmetric_dual_and_feasibility(b12,nu):
    X=np.array([[-1.],[1.]])
    model=b12.load('one-class-svm').OneClassSVM(nu,gamma=.5,tolerance=1e-10).fit(X)
    assert model.converged_,model.status_
    assert_allclose(model.alpha_,[.5,.5],atol=1e-12)
    assert_allclose(model.objective_,(1+np.exp(-2))/4,atol=1e-12)
    assert model.feasibility_residual_<1e-10 and model.kkt_residual_<1e-10 and model.pair_gap_<1e-10
    assert model.primal_dual_gap_>=-1e-12
    assert_allclose(model.rho_,(1+np.exp(-2))/2,atol=1e-12)

@pytest.mark.oracle
def test_nu_one_no_free_support_uses_valid_finite_rho_endpoint(b12):
    X=np.array([[0.],[1.],[3.]])
    model=b12.load('one-class-svm').OneClassSVM(1.,gamma=.5,tolerance=1e-10).fit(X)
    K=np.exp(-.5*(X-X.T)**2);g=K@np.full(3,1/3)
    assert_allclose(model.alpha_,1/3,atol=0,rtol=0)
    assert_allclose(model.rho_,g.max(),atol=1e-15)
    assert len(model.free_support_)==0
    assert model.rho_bounds_[1]==np.inf and np.isfinite(model.rho_)
    assert model.converged_ and model.kkt_residual_<=1e-12
    assert_allclose(model.decision_function(X),g-g.max(),atol=1e-14)

@pytest.mark.oracle
def test_no_free_support_finite_kkt_interval(b12):
    X=np.array([[-1.],[-.2],[.2],[1.]])
    model=b12.load('one-class-svm').OneClassSVM(.5,gamma=.1,tolerance=1e-10).fit(X)
    assert model.converged_,model.status_
    assert len(model.free_support_)==0
    low,high=model.rho_bounds_;assert low<=model.rho_<=high
    assert_allclose(model.alpha_,[.5,0,0,.5],atol=1e-12)
    assert_allclose(model.rho_,(low+high)/2,atol=1e-15)
    assert model.primal_dual_gap_<1e-10

@pytest.mark.oracle
@pytest.mark.parametrize('seed',[0,1,2])
def test_dual_objective_constraints_and_independent_kkt_certificate(b12,seed):
    X=np.random.default_rng(seed).normal(size=(25,2))
    model=b12.load('one-class-svm').OneClassSVM(.3,gamma=.7,tolerance=1e-8).fit(X)
    assert model.converged_,model.status_
    a,K,C=model.alpha_,model.gram_,model.cap_;g=K@a;rho=model.rho_
    assert abs(a.sum()-1)<1e-10 and a.min()>=-1e-12 and a.max()<=C+1e-12
    assert np.all(model.feasibility_history_<=1e-10)
    assert np.all(np.diff(model.objective_history_)<=1e-10)
    zero=a<1e-9;upper=a>C-1e-9;free=~(zero|upper)
    assert np.all(g[zero]>=rho-2e-8);assert np.all(g[upper]<=rho+2e-8)
    assert_allclose(g[free],rho,atol=2e-8)
    q=float(a@K@a);primal=q/2+C*np.maximum(rho-g,0).sum()-rho
    assert_allclose(model.objective_,q/2,atol=1e-12)
    assert_allclose(model.primal_dual_gap_,primal+q/2,atol=1e-12)
    assert_allclose(model.decision_function(X),g-rho,atol=1e-13)
    assert_allclose(model.anomaly_scores(X),-model.score_samples(X),atol=0,rtol=0)
    assert_allclose(model.dual_coef_[0],a[model.support_],atol=0,rtol=0)

@pytest.mark.reference
@pytest.mark.parametrize('nu',[.1,.4,.8])
def test_independent_scipy_dual_and_scaled_sklearn_decision(b12,nu):
    from scipy.optimize import minimize
    from sklearn.svm import OneClassSVM
    rng=np.random.default_rng(242);X=rng.normal(size=(16,2));query=rng.normal(size=(12,2));gamma=.6
    model=b12.load('one-class-svm').OneClassSVM(nu,gamma=gamma,tolerance=1e-9,max_iter=20000).fit(X)
    K=np.exp(-gamma*np.sum((X[:,None,:]-X[None,:,:])**2,axis=2));C=1/(nu*len(X))
    reference=minimize(lambda a:float(a@K@a/2),np.full(len(X),1/len(X)),jac=lambda a:K@a,bounds=[(0,C)]*len(X),constraints={'type':'eq','fun':lambda a:a.sum()-1,'jac':lambda a:np.ones(len(X))},method='SLSQP',options={'ftol':1e-13,'maxiter':2000})
    assert reference.success,reference.message
    assert model.converged_,model.status_
    assert_allclose(model.objective_,reference.fun,atol=2e-9)
    # LIBSVM's sklearn wrapper draws a global seed even for this deterministic
    # reference fit. Isolate only the external oracle; production remains guarded.
    saved=np.random.get_state()
    try:library=OneClassSVM(nu=nu,gamma=gamma,tol=1e-9,shrinking=False).fit(X)
    finally:np.random.set_state(saved)
    expected=library.decision_function(query)/(nu*len(X))
    assert_allclose(model.decision_function(query),expected,atol=2e-6,rtol=2e-5)
    confident=np.abs(expected)>1e-5
    assert_allclose(model.predict(query)[confident],library.predict(query)[confident])

@pytest.mark.parametrize('nu',[1e-4,.3,1.])
def test_duplicates_identical_singletons_and_seedless_reproducibility(b12,nu):
    cls=b12.load('one-class-svm').OneClassSVM
    model=cls(nu).fit(np.ones((8,3)))
    assert model.converged_;assert_allclose(model.predict(np.ones((8,3))),1)
    assert_allclose(model.decision_function(np.ones((8,3))),0,atol=0,rtol=0)
    one=cls(nu).fit([[3.]])
    assert one.predict([[3.]])[0]==1 and one.predict([[10.]])[0]==-1
    X=np.array([[0.],[0.],[1.],[1.],[3.]])
    assert_allclose(cls(nu).fit(X).alpha_,cls(nu).fit(X).alpha_,atol=0,rtol=0)

@pytest.mark.parametrize('kwargs',[dict(nu=0),dict(nu=1.1),dict(nu=1e-5),dict(nu=True),dict(gamma=0),dict(gamma=np.nan),dict(gamma='scale'),dict(kernel='linear'),dict(max_iter=0),dict(tolerance=0)])
def test_invalid_parameters(b12,kwargs):
    with pytest.raises(ValueError):b12.load('one-class-svm').OneClassSVM(**kwargs)

def test_unfitted_ownership_atomicity_and_honest_nonconvergence(b12):
    cls=b12.load('one-class-svm').OneClassSVM
    with pytest.raises(ValueError):cls().predict([[1.]])
    X=np.random.default_rng(243).normal(size=(30,2));model=cls(.3,max_iter=1,tolerance=1e-12).fit(X)
    assert not model.converged_ and model.status_=='iteration-budget'
    assert model.kkt_residual_>1e-12 or model.pair_gap_>1e-12
    before=model.decision_function(X)
    with pytest.raises(ValueError):model.fit([[np.nan,1.]])
    assert_allclose(model.decision_function(X),before,atol=0,rtol=0)
    original=X.copy();fitted=cls().fit(X);X[:]=100
    assert_allclose(fitted.X_fit_,original,atol=0,rtol=0)
    assert fitted.predict(np.empty((0,2))).shape==(0,)
