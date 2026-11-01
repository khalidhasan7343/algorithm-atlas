import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml

TOPIC='sparse-autoencoders'
CLASS='SparseAutoencoder'

@pytest.mark.numerical
def test_finite_difference_modified_reconstruction_objective(b7,gradients):
    m=b7.load(TOPIC);theta=m.vanilla.initialize_parameters(2,1,19041);X=np.array([[.2,-.3],[.4,.1]]);target=X+np.array([[.1,-.1],[-.1,.1]])
    loss,g=m.loss_gradients(theta,X,target,1,.1)
    gradients(lambda p:m.loss_gradients(p['theta'],X,target,1,.1)[0],{'theta':theta},{'theta':g})

@pytest.mark.numerical
def test_reproducibility_training_shapes_and_invalid_variant(b7):
    cls=getattr(b7.load(TOPIC),CLASS);v=np.linspace(-1,1,20);X=np.column_stack([v,.5*v]);kwargs=dict(epochs=180,learning_rate=.2,batch_size=20,random_state=19042)
    m=cls(**kwargs).fit(X);assert np.isfinite(m.reconstruct(X)).all() and m.transform(X).shape==(20,1)
    assert m.loss_history_[-1]<m.loss_history_[0]
    assert_array_equal(m.parameters_['theta'],cls(**kwargs).fit(X).parameters_['theta'])
    with pytest.raises(ValueError):cls(latent_dim=2).fit(X)
    with pytest.raises(ValueError):cls(**{'sparsity':-.1})
    with pytest.raises(ValueError):cls().transform(X)

@pytest.mark.oracle
def test_explicit_l1_penalty_and_gradient_strength(b7):
    m=b7.load(TOPIC);X=np.array([[.2,-.3],[.4,.1]]);theta=m.vanilla.initialize_parameters(2,1,19043);Z,_=m.vanilla.forward(theta,X,2,1,'tanh')
    plain,g0=m.loss_gradients(theta,X,X,1,0.);sparse,g1=m.loss_gradients(theta,X,X,1,.2)
    assert_allclose(sparse-plain,.2*np.mean(abs(Z)));assert np.linalg.norm(g1-g0)>0
    # Decoder gradients do not contain the activation penalty directly.
    assert_allclose(g1[3:],g0[3:])

@pytest.mark.numerical
def test_controlled_sparsity_strength_reduces_activation(b7):
    cls=b7.load(TOPIC).SparseAutoencoder;v=np.linspace(-1,1,30);X=np.column_stack([v,.5*v]);kwargs=dict(epochs=180,batch_size=30,learning_rate=.2,random_state=19048)
    plain=cls(sparsity=0.,**kwargs).fit(X);sparse=cls(sparsity=.2,**kwargs).fit(X)
    assert np.mean(abs(sparse.transform(X)))<np.mean(abs(plain.transform(X)))
