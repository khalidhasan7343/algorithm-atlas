import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


@pytest.mark.oracle
def test_exact_reshuffled_single_observation_updates(b10):
    target=np.array([-1.,2.,4.]);seed=22002;eta=.1
    def fun(x):return float(np.mean((x[0]-target)**2)/2)
    def grad(x,indices):return np.array([np.mean(x[0]-target[indices])])
    r=b10.load('stochastic-gradient-descent').StochasticGradientDescent(eta,seed).minimize(fun,grad,[.3],n_samples=3,max_epochs=2,tolerance=1e-12)
    rng=np.random.default_rng(seed);x=.3;expected=[x];order=[]
    for _ in range(2):
        for i in rng.permutation(3):
            x=x-eta*(x-target[i]);expected.append(x);order.append([i])
    assert_allclose(r.diagnostics['trajectory'][:,0],expected,atol=1e-15)
    assert_array_equal(np.array(r.diagnostics['batch_history']),order)
    assert r.n_iter==2 and r.diagnostics['n_updates']==6 and r.nfev==3 and r.diagnostics['njev']==9


@pytest.mark.oracle
def test_zero_sample_gradient_does_not_replace_full_gradient_stop(b10):
    target=np.array([0.,2.])
    m=b10.load('stochastic-gradient-descent').StochasticGradientDescent(.1,0)
    r=m.minimize(lambda x:float(np.mean((x[0]-target)**2)/2),lambda x,i:np.array([np.mean(x[0]-target[i])]),[0.],n_samples=2,max_epochs=1,tolerance=1e-12)
    assert r.diagnostics['n_updates']==2 and not r.converged and r.status=='epoch-budget'


def test_seeded_fit_and_local_rng_state(b10):
    m=b10.load('stochastic-gradient-descent').StochasticGradientDescent(.2,22)
    fun=lambda x:float(np.sum((x-2)**2)/2);grad=lambda x,i:x-2
    state=np.random.get_state();a=m.minimize(fun,grad,[0.,1.],n_samples=3,max_epochs=50)
    b=m.minimize(fun,grad,[0.,1.],n_samples=3,max_epochs=50)
    assert a.converged;assert_allclose(a.x,[2.,2.],atol=1e-8)
    assert_array_equal(a.x,b.x);assert_array_equal(np.random.get_state()[1],state[1])
    for start in range(0,len(a.diagnostics['batch_history']),3):
        assert sorted(int(z[0]) for z in a.diagnostics['batch_history'][start:start+3])==[0,1,2]


@pytest.mark.parametrize('settings',[dict(random_state=-1),dict(random_state=True),dict(learning_rate=0),dict(learning_rate=np.inf)])
def test_invalid_settings(b10,settings):
    with pytest.raises(ValueError):b10.load('stochastic-gradient-descent').StochasticGradientDescent(**settings)


@pytest.mark.parametrize('n,epochs',[(0,1),(257,1),(True,1),(256,1000),(2,0)])
def test_sampling_budget_and_counts_validation(b10,n,epochs):
    with pytest.raises(ValueError):b10.load('stochastic-gradient-descent').StochasticGradientDescent().minimize(lambda x:0.,lambda x,i:x,[1.],n_samples=n,max_epochs=epochs)


def test_stationary_initialization_uses_full_gradient_only(b10):
    calls=[]
    def grad(x,i):calls.append(i.copy());return x.copy()
    r=b10.load('stochastic-gradient-descent').StochasticGradientDescent().minimize(lambda x:float(x@x)/2,grad,[0.],n_samples=4)
    assert r.converged and r.n_iter==r.diagnostics['n_updates']==0 and r.nfev==1
    assert_array_equal(calls,[np.arange(4)])
