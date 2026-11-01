import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.oracle
def test_forward_losses_and_update_ownership(b7):
    m=b7.load('generative-adversarial-networks');rng=np.random.default_rng(19051);p=m.initialize(1,2,1,rng);real=np.array([[-.2],[.4]]);Z=np.array([[-.5],[.3]])
    fake,_=m.generator(p,Z);real_logits,_=m.discriminator(p,real);fake_logits,_=m.discriminator(p,fake)
    dl,dg=m.discriminator_gradients(p,real,Z);gl,gg=m.generator_gradients(p,Z)
    assert_allclose(dl,np.mean(np.logaddexp(0,-real_logits))+np.mean(np.logaddexp(0,fake_logits)))
    assert_allclose(gl,np.mean(np.logaddexp(0,-fake_logits)))
    assert set(dg)=={'dW','db','dO','do'} and set(gg)=={'gW','gb','gO','go'}
    updated,_=b7.step(p,dg,.1,5)
    for key in gg:assert_array_equal(updated[key],p[key])
    updated,_=b7.step(p,gg,.1,5)
    for key in dg:assert_array_equal(updated[key],p[key])

@pytest.mark.numerical
def test_finite_difference_generator_discriminator_fixed_noise(b7,gradients):
    m=b7.load('generative-adversarial-networks');rng=np.random.default_rng(19052);p=m.initialize(2,2,1,rng);real=rng.normal(0,.2,(2,2));Z=rng.normal(size=(2,1))
    for which in ['generator','discriminator']:
        value,g=m.generator_gradients(p,Z) if which=='generator' else m.discriminator_gradients(p,real,Z)
        subset={key:p[key] for key in g}
        def function(q):
            combined=dict(p,**q)
            return m.generator_gradients(combined,Z)[0] if which=='generator' else m.discriminator_gradients(combined,real,Z)[0]
        gradients(function,subset,g)

@pytest.mark.numerical
def test_reproducibility_low_dimensional_training_and_sampling(b7):
    cls=b7.load('generative-adversarial-networks').GAN;X=np.array([[-1.],[-.8],[.8],[1.]])
    m=cls(latent_dim=1,epochs=20,batch_size=4).fit(X)
    assert m.n_updates_==40 and np.isfinite(m.discriminator_history_).all()
    assert_array_equal(m.sample(4,7),m.sample(4,7));assert_array_equal(m.sample(4),cls(latent_dim=1,epochs=20,batch_size=4).fit(X).sample(4))
    assert np.all((m.discriminate(X)>=0)&(m.discriminate(X)<=1))
    with pytest.raises(ValueError):cls().sample(2)
