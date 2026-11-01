import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


@pytest.mark.oracle
def test_exact_update_and_copying(b10):
    x=np.array([2.,-3.]);g=np.array([4.,-2.]);before=x.copy()
    m=b10.load('batch-gradient-descent').BatchGradientDescent(learning_rate=.25)
    assert_allclose(m.step(x,g),[1.,-2.5]);assert_array_equal(x,before)
    assert m.get_state()=={'t':1}


@pytest.mark.oracle
def test_diagonal_closed_form_trajectory_and_counts(b10,objectives):
    A=np.diag([2.,3.]);star=np.array([1.,-2.]);fun,g=objectives.quadratic(A,A@star)
    x0=np.array([3.,4.]);m=b10.load('batch-gradient-descent').BatchGradientDescent(.1)
    r=m.minimize(fun,g,x0,max_iter=5,tolerance=1e-12)
    expected=np.array([star+(1-.1*np.diag(A))**k*(x0-star) for k in range(6)])
    assert_allclose(r.diagnostics['trajectory'],expected,atol=1e-14)
    assert_allclose(r.history,[fun(x) for x in expected])
    assert np.all(np.diff(r.history)<0)
    assert r.n_iter==5 and r.nfev==6 and r.diagnostics['njev']==6
    assert not r.converged and r.status=='iteration-budget'


@pytest.mark.parametrize('n',[1,2,4,8])
@pytest.mark.oracle
def test_seeded_spd_analytical_optimum(b10,objectives,n):
    rng=np.random.default_rng(22001+n);M=rng.normal(size=(n,n));A=M.T@M+np.eye(n);b=rng.normal(size=n)
    fun,g=objectives.quadratic(A,b);m=b10.load('batch-gradient-descent').BatchGradientDescent(1/np.linalg.eigvalsh(A)[-1])
    r=m.minimize(fun,g,np.zeros(n),max_iter=1500)
    assert r.converged and r.status=='gradient-tolerance'
    assert_allclose(r.x,np.linalg.solve(A,b),atol=1e-8,rtol=0)


def test_initial_stationarity_repeated_runs_and_state_reset(b10):
    m=b10.load('batch-gradient-descent').BatchGradientDescent(.2)
    m.step([1.],[2.]);r=m.minimize(lambda x:float(x@x),lambda x:2*x,[0.])
    assert r.n_iter==0 and r.nfev==1 and r.converged and m.get_state()=={'t':0}
    a=m.minimize(lambda x:float(x@x),lambda x:2*x,[1.],max_iter=2)
    b=m.minimize(lambda x:float(x@x),lambda x:2*x,[1.],max_iter=2)
    assert_array_equal(a.x,b.x);assert_array_equal(a.history,b.history)


def test_large_step_does_not_claim_objective_decrease_or_convergence(b10):
    r=b10.load('batch-gradient-descent').BatchGradientDescent(2.).minimize(lambda x:float(x@x),lambda x:2*x,[1.],max_iter=1)
    assert r.fun>r.history[0] and not r.converged and r.n_iter==1


@pytest.mark.parametrize('x0',[[],[[1.]], [np.nan], [True], ['1'],np.zeros(33)])
def test_invalid_parameters(b10,x0):
    with pytest.raises(ValueError):b10.load('batch-gradient-descent').BatchGradientDescent().minimize(lambda x:0.,lambda x:x,x0)


@pytest.mark.parametrize('gradient',[lambda x:np.array([1.,2.]),lambda x:np.array([[1.]]),lambda x:np.array(['1'])])
def test_no_gradient_broadcasting(b10,gradient):
    with pytest.raises(ValueError):b10.load('batch-gradient-descent').BatchGradientDescent().minimize(lambda x:0.,gradient,[1.])


def test_numerical_callback_failure_keeps_prior_state(b10):
    m=b10.load('batch-gradient-descent').BatchGradientDescent();m.step([1.],[2.]);old=m.get_state()
    with pytest.raises(b10.NumericalError):m.minimize(lambda x:float('nan'),lambda x:x,[1.])
    assert m.get_state()==old
    with pytest.raises(b10.NumericalError):m.step([1.],[float('inf')])
    assert m.get_state()==old
