import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.oracle
def test_forward_reparameterization_kl_and_negative_elbo(b7):
    m=b7.load('variational-autoencoders');p=m.initialize(2,1,np.random.default_rng(19045));X=np.array([[.2,-.3],[.4,.1]]);eps=np.array([[.5],[-.2]])
    R,(mu,logvar,std,Z,noise)=m.forward(p,X,eps);assert_allclose(Z,mu+np.exp(.5*logvar)*eps)
    expected=.5*np.sum((R-X)**2)/2+.5*np.sum(mu**2+np.exp(logvar)-1-logvar)/2
    assert_allclose(m.loss_gradients(p,X,eps)[0],expected)
    for a in p.values():a[:]=0
    assert_allclose(m.loss_gradients(p,X,np.zeros((2,1)))[0],.5*np.sum(X**2)/2)

@pytest.mark.numerical
def test_finite_difference_reparameterized_all_parameters_fixed_noise(b7,gradients):
    m=b7.load('variational-autoencoders');rng=np.random.default_rng(19046);p=m.initialize(2,1,rng);X=rng.normal(0,.2,(2,2));noise=rng.normal(size=(2,1))
    loss,g=m.loss_gradients(p,X,noise);gradients(lambda q:m.loss_gradients(q,X,noise)[0],p,g)

@pytest.mark.numerical
def test_reproducibility_sampling_and_bounded_log_variance(b7):
    cls=b7.load('variational-autoencoders').VariationalAutoencoder;X=np.array([[-1.,-.5],[0,0],[1,.5],[.5,.25]])
    m=cls(epochs=50,batch_size=4,learning_rate=.03).fit(X);mu,lv=m.encode(X)
    assert mu.shape==lv.shape==(4,1) and np.all(abs(lv)<=5)
    assert_array_equal(m.sample(5,7),m.sample(5,7));assert m.sample(5).shape==(5,2)
    assert_array_equal(m.sample(5),cls(epochs=50,batch_size=4,learning_rate=.03).fit(X).sample(5))
    with pytest.raises(ValueError):cls(latent_dim=2).fit(X)
    with pytest.raises(ValueError):cls().sample(2)
