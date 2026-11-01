import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.oracle
def test_forward_identity_shortcut_and_backprop_both_paths(b7):
    m=b7.load('residual-networks');p=m.initialize(2,2,np.random.default_rng(19014));p['W1'][:]=0;p['b1'][:]=0;p['W2'][:]=0;p['b2'][:]=0;p['Wout'][:]=1;p['bout'][:]=0
    X=np.array([[1.,2.],[-1.,.5]]);out,cache=m.forward(p,X);assert_allclose(out,X.sum(1)[:,None])
    g,dx=m.backward(p,cache,np.ones((2,1)));assert_allclose(dx,np.ones_like(X))
    assert_allclose(g['Wout'],X.T@np.ones((2,1)))
    with pytest.raises(ValueError):m.residual_add(X,np.zeros((2,1)))

@pytest.mark.numerical
def test_finite_difference_residual_weights_and_input(b7,gradients):
    m=b7.load('residual-networks');rng=np.random.default_rng(19015);p=m.initialize(2,3,rng);X=rng.normal(size=(2,2));y=rng.normal(size=(2,1));loss,g=m.loss_gradients(p,X,y)
    gradients(lambda q:m.loss_gradients(q,X,y)[0],p,g)
    out,cache=m.forward(p,X);_,delta=b7.mse(out,y);_,dx=m.backward(p,cache,delta)
    gradients(lambda q:b7.mse(m.forward(p,q['X'])[0],y)[0],{'X':X},{'X':dx})

def test_reproducibility_training_and_inference(b7):
    cls=b7.load('residual-networks').ResidualRegressor;X=np.linspace(-1,1,20).reshape(10,2);y=X.sum(1)[:,None]
    m=cls(epochs=100,batch_size=10).fit(X,y);assert m.loss_history_[-1]<m.loss_history_[0]*.05
    assert_array_equal(m.predict(X),cls(epochs=100,batch_size=10).fit(X,y).predict(X))
    with pytest.raises(ValueError):cls().predict(X)
    assert m.predict(np.empty((0,2))).shape==(0,1)
