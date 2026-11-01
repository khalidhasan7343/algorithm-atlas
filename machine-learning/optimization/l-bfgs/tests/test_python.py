import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


@pytest.mark.oracle
@pytest.mark.parametrize('count',[0,1,3,5])
def test_two_loop_matches_independent_dense_inverse_bfgs(b10,count):
    rng=np.random.default_rng(22020);M=rng.normal(size=(4,4));A=M.T@M+np.eye(4);pairs=[]
    for _ in range(count):
        s=rng.normal(size=4);pairs.append((s,A@s))
    g=rng.normal(size=4)
    gamma=float(pairs[-1][0]@pairs[-1][1])/float(pairs[-1][1]@pairs[-1][1]) if pairs else 1.
    H=gamma*np.eye(4)
    for s,y in pairs:
        rho=1/float(s@y);left=np.eye(4)-rho*np.outer(s,y)
        H=left@H@left.T+rho*np.outer(s,s)
    actual=b10.load('l-bfgs').inverse_hessian_product(g,pairs)
    assert_allclose(actual,H@g,atol=2e-13,rtol=2e-12)


@pytest.mark.oracle
@pytest.mark.parametrize('memory',[1,3,8])
def test_spd_optimum_wolfe_conditions_and_memory_bound(b10,objectives,memory):
    rng=np.random.default_rng(22021);M=rng.normal(0,.3,(5,5));A=M.T@M+np.eye(5);b=rng.normal(size=5)
    f,g=objectives.quadratic(A,b);solver=b10.load('l-bfgs').LBFGS(history_size=memory)
    r=solver.minimize(f,g,np.ones(5),max_iter=200)
    assert r.converged;assert_allclose(r.x,np.linalg.solve(A,b),atol=2e-8,rtol=0)
    assert len(r.diagnostics['curvature_pairs'])<=memory
    assert len(r.diagnostics['wolfe_steps'])==r.n_iter
    assert r.nfev==r.diagnostics['njev']==r.diagnostics['line_search_trials']+1
    for index,step in enumerate(r.diagnostics['wolfe_steps']):
        a=step['step_size'];before=step['slope_before']
        start=r.diagnostics['trajectory'][index];end=r.diagnostics['trajectory'][index+1]
        direction=(end-start)/a
        assert_allclose(step['value_before'],f(start),atol=1e-13)
        assert_allclose(step['value_after'],f(end),atol=1e-13)
        assert_allclose(before,g(start)@direction,atol=1e-12,rtol=2e-7)
        assert_allclose(step['slope_after'],g(end)@direction,atol=1e-12,rtol=2e-7)
        assert before<0
        assert step['value_after']<=step['value_before']+solver.c1*a*before+1e-13
        assert abs(step['slope_after'])<=-solver.c2*before+1e-13
    for s,y in r.diagnostics['curvature_pairs']:
        assert s@y>0
        assert_allclose(y,A@s,atol=1e-14,rtol=1e-6)


@pytest.mark.reference
def test_rosenbrock_independent_scipy_reference(b10,objectives):
    from scipy.optimize import minimize
    r=b10.load('l-bfgs').LBFGS(history_size=5).minimize(objectives.rosenbrock,objectives.rosenbrock_gradient,[-1.2,1.],max_iter=400)
    oracle=minimize(objectives.rosenbrock,[-1.2,1.],jac=objectives.rosenbrock_gradient,method='BFGS',options={'gtol':1e-9})
    assert r.converged and r.fun<1e-14
    assert_allclose(r.x,[1.,1.],atol=2e-7)
    assert_allclose(r.x,oracle.x,atol=2e-7)


@pytest.mark.numerical
def test_singular_psd_quadratic_needs_no_hessian_inverse(b10,objectives,monkeypatch):
    def forbidden(*args,**kwargs):raise AssertionError('Hessian inverse must not be formed')
    monkeypatch.setattr(np.linalg,'inv',forbidden)
    f,g=objectives.quadratic(np.diag([2.,0.]),[2.,0.])
    r=b10.load('l-bfgs').LBFGS().minimize(f,g,[3.,7.])
    assert r.converged;assert_allclose(r.x,[1.,7.],atol=1e-10)


@pytest.mark.numerical
def test_ill_conditioned_problem_is_bounded_and_status_honest(b10,objectives):
    f,g=objectives.quadratic(np.diag([1e-4,1e4]),[1e-4,1e4])
    r=b10.load('l-bfgs').LBFGS().minimize(f,g,[3.,-2.],max_iter=100)
    assert np.isfinite(r.x).all() and np.isfinite(r.fun) and r.n_iter<=100
    assert r.converged==(r.diagnostics['gradient_norm']<=1e-8)
    assert r.status in ('gradient-tolerance','iteration-budget','line-search-failed')


def test_line_search_failure_does_not_accept_bad_step(b10,objectives):
    f,g=objectives.quadratic([[100.]],[0.]);x=np.array([1.])
    r=b10.load('l-bfgs').LBFGS(max_line_search=1).minimize(f,g,x)
    assert not r.converged and r.status=='line-search-failed' and r.n_iter==0
    assert_array_equal(r.x,x);assert r.nfev==r.diagnostics['njev']==2


def test_initial_stationarity_and_repeated_calls_are_fresh(b10):
    solver=b10.load('l-bfgs').LBFGS();f=lambda x:float(x@x)/2;g=lambda x:x
    stationary=solver.minimize(f,g,[0.,0.]);assert stationary.converged and stationary.n_iter==0 and stationary.nfev==1
    a=solver.minimize(f,g,[2.,-1.]);b=solver.minimize(f,g,[2.,-1.])
    assert_array_equal(a.x,b.x);assert_array_equal(a.history,b.history)


@pytest.mark.parametrize('pair',[([1.],[-1.]),([1.],[0.]),([0.],[1.]),([1.],[np.nan]),([1.,2.],[1.,2.])])
def test_bad_curvature_pairs_rejected(b10,pair):
    with pytest.raises(ValueError):b10.load('l-bfgs').inverse_hessian_product([1.],[pair])


@pytest.mark.parametrize('settings',[dict(history_size=0),dict(history_size=21),dict(max_line_search=0),dict(c1=0),dict(c2=1),dict(c1=.9,c2=.1),dict(initial_step=0),dict(initial_step=2,max_step=1)])
def test_invalid_settings(b10,settings):
    with pytest.raises(ValueError):b10.load('l-bfgs').LBFGS(**settings)


def test_limits_callback_failures_and_mutation_guard(b10):
    solver=b10.load('l-bfgs').LBFGS();f=lambda x:float(x@x);g=lambda x:2*x
    with pytest.raises(ValueError):solver.minimize(f,g,[1.],max_iter=2000)
    with pytest.raises(ValueError):solver.minimize(f,lambda x:np.array([[1.]]),[1.])
    with pytest.raises(b10.NumericalError):solver.minimize(lambda x:float('inf'),g,[1.])
    x=np.array([1.]);before=x.copy()
    def bad(z):z[0]=99;return 0.
    with pytest.raises(ValueError):solver.minimize(bad,g,x)
    assert_array_equal(x,before)
