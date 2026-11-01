import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


@pytest.mark.oracle
def test_mean_gradient_tail_batch_and_exact_update_order(b10):
    X=np.array([[1.,0],[0,1],[1,1],[2,-1],[-1,2]]);y=np.array([1.,-1,2,.5,3]);seed=22003
    fun=lambda x:float(np.mean((X@x-y)**2)/2)
    grad=lambda x,i:X[i].T@(X[i]@x-y[i])/len(i)
    m=b10.load('mini-batch-gradient-descent').MiniBatchGradientDescent(.05,2,seed)
    r=m.minimize(fun,grad,[.3,-.2],n_samples=5,max_epochs=1,tolerance=1e-12)
    permutation=np.random.default_rng(seed).permutation(5);x=np.array([.3,-.2]);expected=[x.copy()]
    for start in range(0,5,2):
        selected=permutation[start:start+2]
        g=sum((X[j]*(float(X[j]@x)-y[j]) for j in selected),start=np.zeros(2))/len(selected)
        x=x-.05*g;expected.append(x.copy())
    assert_allclose(r.diagnostics['trajectory'],expected,atol=1e-15)
    assert [len(i) for i in r.diagnostics['batch_history']]==[2,2,1]
    assert_array_equal(np.concatenate(r.diagnostics['batch_history']),permutation)
    assert r.nfev==2 and r.diagnostics['njev']==5 and r.diagnostics['n_updates']==3


@pytest.mark.oracle
def test_batch_one_matches_sgd_and_full_batch_matches_batch_gd(b10):
    targets=np.array([1.,2.,3.,4.]);fun=lambda x:float(np.mean((x[0]-targets)**2)/2)
    grad=lambda x,i:np.array([np.mean(x[0]-targets[i])])
    for size,topic in [(1,'stochastic-gradient-descent'),(4,'batch-gradient-descent')]:
        m=b10.load('mini-batch-gradient-descent').MiniBatchGradientDescent(.1,size,22)
        r=m.minimize(fun,grad,[0.],n_samples=4,max_epochs=5,tolerance=1e-12)
        if size==1:other=b10.load(topic).StochasticGradientDescent(.1,22).minimize(fun,grad,[0.],n_samples=4,max_epochs=5,tolerance=1e-12)
        else:other=b10.load(topic).BatchGradientDescent(.1).minimize(fun,lambda x:grad(x,np.arange(4)),[0.],max_iter=5,tolerance=1e-12)
        assert_allclose(r.x,other.x,atol=1e-15)


def test_repeated_runs_reset_sampling_and_do_not_mutate_inputs(b10):
    x=np.array([1.,-1.]);before=x.copy();m=b10.load('mini-batch-gradient-descent').MiniBatchGradientDescent(.2,2,21)
    fun=lambda z:float(z@z)/2;grad=lambda z,i:z
    a=m.minimize(fun,grad,x,n_samples=6,max_epochs=20)
    b=m.minimize(fun,grad,x,n_samples=6,max_epochs=20)
    assert_array_equal(a.x,b.x);assert_array_equal(x,before)
    assert_array_equal(np.concatenate(a.diagnostics['batch_history']),np.concatenate(b.diagnostics['batch_history']))


@pytest.mark.parametrize('size',[0,True,257,1.5])
def test_invalid_batch_size(b10,size):
    with pytest.raises(ValueError):b10.load('mini-batch-gradient-descent').MiniBatchGradientDescent(batch_size=size)


def test_batch_size_may_not_exceed_sample_count(b10):
    with pytest.raises(ValueError):b10.load('mini-batch-gradient-descent').MiniBatchGradientDescent(batch_size=4).minimize(lambda x:0.,lambda x,i:x,[0.],n_samples=3)
