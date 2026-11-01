import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml

TOPIC='recurrent-neural-networks'
CLASS='RNNRegressor'

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
def test_forward_hand_one_and_multi_step_recurrence(b7):
    m=b7.load(TOPIC);p=dict(Wx=np.array([[.5]]),Wh=np.array([[.2]]),b=np.zeros(1),Wo=np.ones((1,1)),bo=np.zeros(1));X=np.array([[[1.],[2.]]])
    out,cache=m.forward(p,X);first=np.tanh(.5);second=np.tanh(1+.2*first)
    assert_allclose(cache[0][2],[[first]]);assert_allclose(out,[[second]])
