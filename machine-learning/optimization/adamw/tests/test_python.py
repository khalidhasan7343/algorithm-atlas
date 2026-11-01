import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


@pytest.mark.oracle
def test_decoupled_old_parameter_decay_and_bias_mask(b10):
    Adam=b10.load('adam').Adam;AdamW=b10.load('adamw').AdamW
    plain=Adam(.1,.8,.6,.25);decayed=AdamW(.1,.8,.6,.25,.2,[True,False])
    x=np.array([1.,-2.]);g=np.array([2.,-4.])
    expected=plain.step(x,g)-.1*.2*np.array([1.,0.])*x
    actual=decayed.step(x,g);assert_allclose(actual,expected,atol=1e-15)
    for key in ('first_moment','second_moment'):assert_array_equal(decayed.get_state()[key],plain.get_state()[key])
    coupled=Adam(.1,.8,.6,.25).step(x,g+.2*x)
    assert not np.allclose(actual,coupled)


@pytest.mark.oracle
def test_zero_task_gradient_decay_does_not_falsely_converge(b10):
    model=b10.load('adamw').AdamW(learning_rate=.1,weight_decay=.2)
    r=model.minimize(lambda x:0.,lambda x:np.zeros_like(x),[2.],max_iter=3)
    assert_allclose(r.x,[2*.98**3],atol=1e-15)
    assert not r.converged and r.status=='iteration-budget' and r.n_iter==3
    assert r.diagnostics['gradient_norm']==0 and not r.diagnostics['gradient_stopping_enabled']


@pytest.mark.oracle
def test_zero_or_inactive_decay_matches_adam(b10):
    for settings in (dict(weight_decay=0),dict(weight_decay=.1,decay_mask=[False,False])):
        a=b10.load('adam').Adam(.1);w=b10.load('adamw').AdamW(.1,**settings);x=np.array([1.,-2.]);z=x.copy()
        for g in ([2.,-4.],[-1.,3.],[0.,0.]):
            x=a.step(x,g);z=w.step(z,g);assert_array_equal(x,z)
        assert w.gradient_stopping()


def test_decay_mask_copy_shape_and_failed_update_are_transactional(b10):
    mask=np.array([True,False]);m=b10.load('adamw').AdamW(decay_mask=mask);mask[:]=False
    assert_array_equal(m.decay_mask,[True,False])
    with pytest.raises(ValueError):m.step([1.],[2.])
    assert m.get_state()=={'t':0}


@pytest.mark.parametrize('settings',[dict(weight_decay=-1),dict(weight_decay=True),dict(learning_rate=10,weight_decay=.2),dict(decay_mask=[1,0]),dict(decay_mask=[]),dict(decay_mask=[[True]])])
def test_invalid_settings(b10,settings):
    with pytest.raises(ValueError):b10.load('adamw').AdamW(**settings)


@pytest.mark.parametrize('mask,decay',[([False],.1),([False],0.),([True],0.),([False,False,False],.1)])
def test_stationary_minimize_rejects_wrong_mask_before_callbacks_atomically(b10,mask,decay):
    model=b10.load('adamw').AdamW(decay_mask=mask,weight_decay=decay)
    model.step(np.ones(len(mask)),np.ones(len(mask)))
    state=model.get_state();calls=[]
    def objective(x):calls.append('objective');return 0.
    def gradient(x):calls.append('gradient');return np.zeros_like(x)
    with pytest.raises(ValueError):model.minimize(objective,gradient,[1.,2.])
    assert calls==[]
    after=model.get_state()
    assert state['t']==after['t']
    for name in ('first_moment','second_moment'):assert_array_equal(state[name],after[name])
