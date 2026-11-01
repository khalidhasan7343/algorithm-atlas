import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml

TOPIC='long-short-term-memory'
CLASS='LSTMRegressor'

@pytest.mark.numerical
@pytest.mark.parametrize('length',[1,3])
def test_finite_difference_bptt_all_parameters(b7,gradients,length):
    m=b7.load(TOPIC);rng=np.random.default_rng(19021);p=m.initialize(2,2,rng);X=rng.normal(size=(2,length,2))*.2;y=np.array([[.1],[-.2]])
    loss,g=m.loss_gradients(p,X,y);gradients(lambda q:m.loss_gradients(q,X,y)[0],p,g)
    out,cache=m.forward(p,X);_,delta=b7.mse(out,y);_,dx=m.backward(p,cache,delta)
    gradients(lambda q:b7.mse(m.forward(p,q['X'])[0],y)[0],{'X':X},{'X':dx})

@pytest.mark.numerical
def test_reproducibility_short_sequence_training(b7):
    cls=getattr(b7.load(TOPIC),CLASS);rng=np.random.default_rng(19022);X=rng.normal(0,.2,(8,3,1));y=X.sum(1)
    m=cls(hidden_dim=3,epochs=160,learning_rate=.2,batch_size=8).fit(X,y)
    assert m.loss_history_[-1]<m.loss_history_[0]*.8
    assert_array_equal(m.predict(X),cls(hidden_dim=3,epochs=160,learning_rate=.2,batch_size=8).fit(X,y).predict(X))
    with pytest.raises(ValueError):m.predict(np.zeros((1,2,1)))
    with pytest.raises(ValueError):cls().predict(X)
    for invalid in [np.zeros((2,17,1)),np.zeros((2,0,1)),np.ones((2,2)),np.full((2,2,1),np.nan)]:
        with pytest.raises(ValueError):cls().fit(invalid,[[0],[1]])

@pytest.mark.oracle
def test_forward_one_step_gates_cell_hidden(b7):
    m=b7.load(TOPIC);p=m.initialize(1,1,np.random.default_rng(0))
    for value in p.values():value[:]=0
    p['b'][3]=np.arctanh(.4);p['Wo'][:]=1
    out,cache=m.forward(p,np.zeros((1,1,1)));x,h,c,i,f,o,g,new_c,new_h=cache[0]
    assert_allclose(i,.5);assert_allclose(f,.5);assert_allclose(o,.5);assert_allclose(g,.4)
    assert_allclose(new_c,.2);assert_allclose(new_h,.5*np.tanh(.2));assert_allclose(out,new_h)
