import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.oracle
@pytest.mark.reference
def test_forward_attention_scaling_masks_heads_and_positions(b7):
    m=b7.load('transformers');Q=np.array([[[1.,0.,.2,.3],[0.,1.,-.1,.2],[1.,1.,.3,.4]]]);K=Q*.7;V=Q+.2
    out,cache=m.attention(Q,K,V,2,True);q,k,v,prob,mask=cache
    assert prob.shape==(1,2,3,3);assert_allclose(prob.sum(-1),1);assert_allclose(prob[:,:,0,1:],0)
    expected=np.empty_like(out)
    for t in range(3):
        for h in range(2):
            scores=np.array([Q[0,t,h*2:h*2+2]@K[0,j,h*2:h*2+2]/np.sqrt(2) for j in range(t+1)])
            weights=np.exp(scores-scores.max());weights/=weights.sum()
            expected[0,t,h*2:h*2+2]=weights@V[0,:t+1,h*2:h*2+2]
    assert_allclose(out,expected,atol=1e-13)
    changed=V.copy();changed[:,2]+=100
    assert_allclose(m.attention(Q,K,changed,2,True)[0][:,:2],out[:,:2])
    positions=m.positional(3,4);assert_allclose(positions[0],[0,1,0,1]);assert not np.allclose(positions[0],positions[1])

@pytest.mark.numerical
def test_layer_norm_forward_and_all_adjoints(b7,gradients):
    m=b7.load('transformers');X=np.array([[[.2,-.3,.8],[.1,.5,-.2]]]);gamma=np.array([1.,.9,1.1]);beta=np.array([.1,0,-.2]);up=np.arange(6.).reshape(X.shape)/5
    out,cache=m.layer_norm(X,gamma,beta);dx,dg,db=m.layer_norm_backward(up,cache)
    expected=(X-X.mean(-1,keepdims=True))/np.sqrt(X.var(-1,keepdims=True)+1e-5)*gamma+beta;assert_allclose(out,expected)
    gradients(lambda p:np.sum(m.layer_norm(p['X'],p['g'],p['b'])[0]*up),dict(X=X,g=gamma,b=beta),dict(X=dx,g=dg,b=db))

@pytest.mark.numerical
@pytest.mark.parametrize('heads,causal',[(1,False),(2,True)])
@pytest.mark.parametrize('length',[1,3])
def test_finite_difference_full_transformer(b7,gradients,heads,causal,length):
    m=b7.load('transformers');rng=np.random.default_rng(19031);p=m.initialize(2,4,3,rng);X=rng.normal(0,.2,(2,length,2));y=np.array([[.1],[-.2]])
    loss,g=m.loss_gradients(p,X,y,heads,causal);gradients(lambda q:m.loss_gradients(q,X,y,heads,causal)[0],p,g,atol=4e-6)

@pytest.mark.numerical
def test_reproducibility_training_and_invalid_heads(b7):
    cls=b7.load('transformers').TransformerRegressor;rng=np.random.default_rng(19032);X=rng.normal(0,.2,(6,3,1));y=X[:,-1]
    m=cls(epochs=80,learning_rate=.03,batch_size=6).fit(X,y);assert m.loss_history_[-1]<m.loss_history_[0]
    assert_array_equal(m.predict(X),cls(epochs=80,learning_rate=.03,batch_size=6).fit(X,y).predict(X))
    with pytest.raises(ValueError):cls(d_model=3,heads=2)
    with pytest.raises(ValueError):cls(causal=1)
    with pytest.raises(ValueError):cls().predict(X)
