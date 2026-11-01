import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml

CASES=[('batch-gradient-descent','BatchGradientDescent'),('stochastic-gradient-descent','StochasticGradientDescent'),
       ('mini-batch-gradient-descent','MiniBatchGradientDescent'),('momentum','Momentum'),('rmsprop','RMSProp'),('adam','Adam'),('adamw','AdamW')]


def model(b10,case,**settings):
    topic,name=case
    if topic=='adamw':settings=dict(weight_decay=0,**settings)
    return getattr(b10.load(topic),name)(**settings)


def run(b10,m,fun,gradient,x0,**settings):
    if isinstance(m,b10.SampledOptimizer):
        return m.minimize(fun,lambda x,i:gradient(x),x0,n_samples=4,max_epochs=2,**settings)
    return m.minimize(fun,gradient,x0,max_iter=2,**settings)


def same(a,b):
    assert a.keys()==b.keys()
    for key in a:
        if isinstance(a[key],np.ndarray):assert_array_equal(a[key],b[key])
        else:assert a[key]==b[key]


@pytest.mark.parametrize('case',CASES)
@pytest.mark.parametrize('rate',[0,-1,True,float('nan'),10**1000])
def test_invalid_learning_rates(b10,case,rate):
    with pytest.raises(ValueError):model(b10,case,learning_rate=rate)


@pytest.mark.parametrize('case',CASES)
@pytest.mark.parametrize('value',[float('nan'),float('inf')])
def test_nonfinite_gradients_are_rejected_without_state_advance(b10,case,value):
    m=model(b10,case);m.step([1.],[2.]);before=m.get_state()
    with pytest.raises(b10.NumericalError):m.step([1.],[value])
    same(m.get_state(),before)


@pytest.mark.parametrize('case',CASES)
def test_state_copy_reset_and_shape_lock(b10,case):
    m=model(b10,case);m.step([1.,-2.],[2.,-1.]);before=m.get_state();changed=m.get_state()
    changed['t']=999
    for value in changed.values():
        if isinstance(value,np.ndarray):value[:]=777
    same(m.get_state(),before)
    with pytest.raises(ValueError):m.step([1.],[1.])
    same(m.get_state(),before)
    m.reset();assert m.get_state()=={'t':0}
    assert m.step([1.],[1.]).shape==(1,)


@pytest.mark.parametrize('case',CASES)
def test_failed_run_does_not_commit_partial_updates(b10,case):
    m=model(b10,case);m.step([1.],[2.]);before=m.get_state();calls=[]
    def f(x):
        calls.append(1)
        return float(x@x) if len(calls)==1 else float('nan')
    with pytest.raises(b10.NumericalError):run(b10,m,f,lambda x:np.ones_like(x),[1.])
    assert len(calls)==2;same(m.get_state(),before)


@pytest.mark.parametrize('case',CASES)
def test_repeated_minimize_runs_reset_state_and_own_results(b10,case):
    m=model(b10,case);x=np.array([2.,-1.]);before=x.copy()
    f=lambda z:float(z@z)/2;g=lambda z:z
    a=run(b10,m,f,g,x);state=m.get_state();b=run(b10,m,f,g,x)
    assert_array_equal(a.x,b.x);assert_array_equal(a.history,b.history);same(m.get_state(),state)
    assert_array_equal(x,before);a.x[:]=777;a.diagnostics['state']['t']=777
    same(m.get_state(),state)


@pytest.mark.parametrize('case',CASES)
def test_tiny_step_is_not_mistaken_for_stationarity(b10,case):
    m=model(b10,case,learning_rate=1e-8)
    r=run(b10,m,lambda x:float(x[0]),lambda x:np.ones(1),[0.],tolerance=1e-4)
    assert not r.converged and r.n_iter==2 and r.diagnostics['gradient_norm']==1.


@pytest.mark.parametrize('case',CASES)
def test_callback_inputs_are_readonly_copies(b10,case):
    x=np.array([1.]);m=model(b10,case)
    def bad_objective(argument):argument[0]=777;return 0.
    with pytest.raises(ValueError):run(b10,m,bad_objective,lambda x:x,x)
    assert_array_equal(x,[1.]);assert m.get_state()=={'t':0}


@pytest.mark.parametrize('case',CASES)
def test_numerically_invalid_proposal_is_atomic(b10,case):
    m=model(b10,case);before=m.get_state()
    with pytest.raises(b10.NumericalError):m.step([1e6],[-1e12])
    same(m.get_state(),before)
