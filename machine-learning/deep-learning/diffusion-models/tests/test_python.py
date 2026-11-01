import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.oracle
def test_forward_schedule_noising_moments_and_reverse_step(b7):
    m=b7.load('diffusion-models');beta,alpha,bar,var=m.schedule(3,.1,.3)
    assert_allclose(beta,[.1,.2,.3]);assert_allclose(bar,[.9,.72,.504]);assert var[0]==0
    X=np.array([[2.],[-1.]]);eps=np.array([[.5],[-.5]]);t=np.array([0,2])
    assert_allclose(m.q_sample(X,t,eps,bar),np.sqrt(bar[t])[:,None]*X+np.sqrt(1-bar[t])[:,None]*eps)
    assert_allclose(m.q_sample(X,t,np.zeros_like(X),bar),np.sqrt(bar[t])[:,None]*X)
    expected=(X-beta[1]/np.sqrt(1-bar[1])*eps)/np.sqrt(alpha[1]);assert_allclose(m.reverse_mean(X,1,eps,beta,alpha,bar),expected)
    assert np.all(var>=0) and np.all(var<=beta)

@pytest.mark.numerical
def test_finite_difference_denoiser_fixed_timesteps_noise(b7,gradients):
    m=b7.load('diffusion-models');rng=np.random.default_rng(19053);p=m.initialize(2,3,rng);X=rng.normal(0,.2,(2,2));t=np.array([0,2]);eps=rng.normal(size=(2,2))
    value,g=m.loss_gradients(p,X,t,eps,3);gradients(lambda q:m.loss_gradients(q,X,t,eps,3)[0],p,g)

@pytest.mark.numerical
def test_reproducibility_sampling_finite_and_schedule_errors(b7):
    cls=b7.load('diffusion-models').DiffusionModel;X=np.array([[-1.,-.5],[0,0],[1,.5],[.5,.2]])
    m=cls(epochs=20,batch_size=4,n_steps=4).fit(X);assert m.sample(3).shape==(3,2) and np.isfinite(m.sample(3)).all()
    assert_array_equal(m.sample(4,7),m.sample(4,7));assert_array_equal(m.sample(4),cls(epochs=20,batch_size=4,n_steps=4).fit(X).sample(4))
    for kwargs in [{'n_steps':1},{'beta_start':0},{'beta_end':1},{'beta_start':.3,'beta_end':.1}]:
        with pytest.raises(ValueError):cls(**kwargs)
    with pytest.raises(ValueError):cls().sample(1)

def test_timestep_indexing_rejects_wraparound_and_broadcasting(b7):
    m=b7.load('diffusion-models');beta,alpha,bar,var=m.schedule(3,.1,.3);X=np.ones((2,1))
    for t in [np.array([-1,0]),np.array([0,3]),np.array([0.,1.]),np.array([0])]:
        with pytest.raises(ValueError):m.q_sample(X,t,np.zeros_like(X),bar)
    with pytest.raises(ValueError):m.q_sample(X,np.array([0,1]),np.zeros((2,2)),bar)
    with pytest.raises(ValueError):m.reverse_mean(X,-1,X,beta,alpha,bar)
