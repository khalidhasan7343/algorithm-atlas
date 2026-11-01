import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.oracle
def test_forward_normalized_aggregation_self_loops_isolates(b7):
    m=b7.load('graph-neural-networks');A=np.array([[0.,1,0],[1,0,0],[0,0,0]]);X=np.array([[1.],[2.],[4.]])
    S=m.normalize_adjacency(A,3,True);assert_allclose(S,[[.5,.5,0],[.5,.5,0],[0,0,1]])
    p=dict(W1=np.ones((1,1)),b1=np.zeros(1),W2=np.ones((1,1)),b2=np.zeros(1))
    out,_=m.forward(p,X,S);assert_allclose(out,S@np.tanh(S@X))
    without=m.normalize_adjacency(A,3,False);assert_allclose(without[2],0)
    assert_allclose(m.forward(p,X,without)[0][2],0)

@pytest.mark.numerical
def test_finite_difference_all_message_passing_parameters(b7,gradients):
    m=b7.load('graph-neural-networks');rng=np.random.default_rng(19061);p=m.initialize(2,3,rng);X=rng.normal(0,.2,(3,2));y=rng.normal(0,.2,(3,1));S=m.normalize_adjacency([[0,1,0],[1,0,1],[0,1,0]],3)
    loss,g=m.loss_gradients(p,X,y,S);gradients(lambda q:m.loss_gradients(q,X,y,S)[0],p,g)

@pytest.mark.oracle
def test_node_permutation_equivariance_and_training_reproducibility(b7):
    m=b7.load('graph-neural-networks');X=np.array([[1.,0],[0,1],[1,1],[.5,.2]]);A=np.array([[0.,1,0,0],[1,0,1,0],[0,1,0,0],[0,0,0,0]]);y=X.sum(1)[:,None]
    model=m.GCNRegressor(epochs=100).fit(X,y,A);order=np.array([2,0,3,1])
    assert_allclose(model.predict(X[order],A[np.ix_(order,order)]),model.predict(X,A)[order],atol=1e-12)
    assert_array_equal(model.predict(X,A),m.GCNRegressor(epochs=100).fit(X,y,A).predict(X,A))
    assert model.loss_history_[-1]<model.loss_history_[0]
    with pytest.raises(ValueError):m.GCNRegressor().predict(X,A)

@pytest.mark.parametrize('A',[[[0,1],[0,0]],[[1,0],[0,0]],[[0,-1],[-1,0]],[[0,float('nan')],[0,0]],[[0]]])
def test_invalid_adjacency(b7,A):
    with pytest.raises(ValueError):b7.load('graph-neural-networks').GCNRegressor().fit([[1],[2]],[[0],[1]],A)
