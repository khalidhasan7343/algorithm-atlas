import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml

TOPIC='denoising-autoencoders'
CLASS='DenoisingAutoencoder'

@pytest.mark.numerical
def test_finite_difference_modified_reconstruction_objective(b7,gradients):
    m=b7.load(TOPIC);theta=m.vanilla.initialize_parameters(2,1,19041);X=np.array([[.2,-.3],[.4,.1]]);target=X+np.array([[.1,-.1],[-.1,.1]])
    loss,g=m.loss_gradients(theta,X,target,1)
    gradients(lambda p:m.loss_gradients(p['theta'],X,target,1)[0],{'theta':theta},{'theta':g})

@pytest.mark.numerical
def test_reproducibility_training_shapes_and_invalid_variant(b7):
    cls=getattr(b7.load(TOPIC),CLASS);v=np.linspace(-1,1,20);X=np.column_stack([v,.5*v]);kwargs=dict(epochs=180,learning_rate=.2,batch_size=20,random_state=19042)
    m=cls(**kwargs).fit(X);assert np.isfinite(m.reconstruct(X)).all() and m.transform(X).shape==(20,1)
    assert m.loss_history_[-1]<m.loss_history_[0]
    assert_array_equal(m.parameters_['theta'],cls(**kwargs).fit(X).parameters_['theta'])
    with pytest.raises(ValueError):cls(latent_dim=2).fit(X)
    with pytest.raises(ValueError):cls(**{'noise_std':-.1})
    with pytest.raises(ValueError):cls().transform(X)

@pytest.mark.oracle
def test_corruption_uses_clean_targets_not_noisy_inputs(b7):
    m=b7.load(TOPIC);clean=np.array([[.2,-.3],[.4,.1]]);noise=np.array([[.1,.2],[-.2,.1]]);corrupted=clean+noise;theta=m.vanilla.initialize_parameters(2,1,19044)
    _,R=m.vanilla.forward(theta,corrupted,2,1,'tanh');loss,_=m.loss_gradients(theta,corrupted,clean,1)
    assert_allclose(loss,np.mean((R-clean)**2));assert abs(loss-np.mean((R-corrupted)**2))>1e-5
    rng1=np.random.default_rng(7);rng2=np.random.default_rng(7)
    assert_array_equal(m.corrupt(clean,.1,rng1),m.corrupt(clean,.1,rng2))

@pytest.mark.numerical
def test_controlled_denoising_improves_noisy_clean_error(b7):
    cls=b7.load(TOPIC).DenoisingAutoencoder;v=np.linspace(-1,1,40);clean=np.column_stack([v,.5*v]);noise=np.random.default_rng(19047).normal(0,.2,clean.shape);noisy=clean+noise
    model=cls(epochs=400,learning_rate=.2,batch_size=40,noise_std=.2).fit(clean)
    assert np.mean((model.reconstruct(noisy)-clean)**2)<np.mean(noise**2)*.8
