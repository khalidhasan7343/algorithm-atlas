import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.numerical
@pytest.mark.reference
def test_stable_sigmoid_softmax_bce_extreme_reference(b7):
    from scipy.special import expit,logsumexp
    X=np.array([[-1e6,0,1e6],[1000,1001,999.]])
    assert_allclose(b7.sigmoid(X),expit(X),atol=1e-16)
    assert_allclose(b7.softmax(X),np.exp(X-logsumexp(X,axis=-1,keepdims=True)),rtol=1e-10,atol=1e-13)
    assert_allclose(b7.softmax(X).sum(-1),1)
    loss,g=b7.bce(np.array([[-1e6],[1e6]]),np.array([[1.],[0.]]));assert loss==1e6
    assert_allclose(g,[[-.5],[.5]])

@pytest.mark.oracle
@pytest.mark.numerical
def test_backprop_update_clipping_owned_blocks_and_zero_gradient(b7):
    p={'a':np.array([1.,2.]),'b':np.array([3.])};g={'a':np.array([3.,4.])}
    updated,norm=b7.step(p,g,.2,2.);assert norm==5;assert_allclose(updated['a'],[.76,1.68]);assert_array_equal(updated['b'],p['b']);assert_array_equal(p['a'],[1,2])
    unchanged,norm=b7.step(p,{'a':np.zeros(2)},.2,2);assert norm==0;assert_array_equal(unchanged['a'],p['a'])
    with pytest.raises(ValueError):b7.step(p,{'a':np.ones(3)},.1,5)
    with pytest.raises(ValueError):b7.step(p,{'missing':np.ones(1)},.1,5)
    with pytest.raises(ValueError):b7.step(p,{'a':np.array([np.nan,1])},.1,5)

@pytest.mark.oracle
def test_exact_minibatch_parameter_update_and_no_global_rng_mutation(b7):
    params={'w':np.array([1.])};X=np.array([[1.],[2.]]);y=np.zeros((2,1));state=np.random.get_state()
    def objective(p,x,t,rng):return float(np.mean((x*p['w']-t)**2)),{'w':np.mean(2*x*(x*p['w']-t),axis=0)}
    p,info=b7.train(params,X,y,objective,epochs=1,learning_rate=.1,batch_size=2,rng=np.random.default_rng(0),gradient_clip=100,shuffle=False)
    assert_allclose(p['w'],[.5]);assert info['n_updates_']==1 and not info['converged_']
    now=np.random.get_state();assert state[0]==now[0] and state[2:]==now[2:];assert_array_equal(state[1],now[1])
    with pytest.raises(ValueError):
        b7.train(params,np.ones((128,1)),np.zeros((128,1)),objective,epochs=100,batch_size=1,learning_rate=.1,rng=np.random.default_rng(0),gradient_clip=5)
