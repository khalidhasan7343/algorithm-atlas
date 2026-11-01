import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


def helper(b13):return b13.load('bert').t


@pytest.mark.oracle
@pytest.mark.parametrize('causal',[False,True])
@pytest.mark.parametrize('heads',[1,2])
def test_attention_independent_scalar_oracle_masking_heads(b13,causal,heads):
 t=helper(b13);Q=np.array([[[1.,0.,.2,.3],[0.,1.,-.1,.2],[1.,1.,.3,.4],[0.,0.,0.,0.]]])
 K=Q*.7;V=Q+.2;valid=np.array([[True,True,True,False]])
 out,prob=t.attention(Q,K,V,heads,valid,causal=causal)
 expected=np.zeros_like(out);expected_prob=np.zeros_like(prob);width=4//heads
 for step in range(3):
  candidates=list(range(step+1)) if causal else [0,1,2]
  for h in range(heads):
   scores=[]
   for j in candidates:scores.append(sum(Q[0,step,h*width+i]*K[0,j,h*width+i] for i in range(width))/np.sqrt(width))
   weights=np.array([np.exp(s-max(scores)) for s in scores]);weights/=sum(weights)
   for j,w in zip(candidates,weights):
    expected_prob[0,h,step,j]=w
    for i in range(width):expected[0,step,h*width+i]+=w*V[0,j,h*width+i]
 assert_allclose(out,expected,atol=1e-13);assert_allclose(prob,expected_prob,atol=1e-13)
 changed=V.copy();changed[:,3]=10000
 assert_array_equal(out,t.attention(Q,K,changed,heads,valid,causal=causal)[0])


@pytest.mark.oracle
def test_entire_block_manual_attention_residual_norm_and_gelu(b13):
 t=helper(b13);m=b13.load('bert').BERT(8,d_model=2,heads=1,ff_dim=2)
 p=m.backbone_['blocks'][0];X=np.array([[[.2,-.1],[.7,.4]]]);valid=np.ones((1,2),bool)
 q,k,v=[X[0]@p['W'+n]+p['b'+n] for n in ('q','k','v')]
 C=np.empty_like(v)
 for i in range(2):
  scores=np.array([sum(q[i]*k[j])/np.sqrt(2) for j in range(2)])
  weights=np.exp(scores-max(scores));weights/=sum(weights);C[i]=sum(weights[j]*v[j] for j in range(2))
 def norm(A,g,b):
  rows=[]
  for row in A:
   mean=sum(row)/len(row);variance=sum((x-mean)**2 for x in row)/len(row)
   rows.append([(x-mean)/np.sqrt(variance+1e-5)*scale+shift for x,scale,shift in zip(row,g,b)])
  return np.array(rows)
 H=norm(X[0]+C@p['Wa']+p['ba'],p['g1'],p['n1'])
 Z=H@p['W1']+p['b1'];F=np.array([[.5*x*(1+np.tanh(np.sqrt(2/np.pi)*(x+.044715*x**3))) for x in row] for row in Z])
 expected=norm(H+F@p['W2']+p['b2'],p['g2'],p['n2'])
 assert_allclose(t.block(p,X,1,valid,causal=False)[0][0],expected,atol=1e-13)
 assert t.layer_norm is t._b7.layer_norm


@pytest.mark.numerical
def test_attention_extreme_logits_and_all_masked_domain(b13):
 t=helper(b13);Q=np.array([[[1e6,-1e6],[-1e6,1e6]]]);valid=np.ones((1,2),bool)
 out,prob=t.attention(Q,Q,np.ones_like(Q),1,valid)
 assert_allclose(out,1);assert_allclose(prob.sum(-1),1);assert np.isfinite(prob).all()
 for mask in (np.zeros((1,2),bool),np.array([[False,True]])):
  with pytest.raises(ValueError,match='all-masked'):t.attention(Q,Q,Q,1,mask,causal=True)


@pytest.mark.parametrize('change',['shape','boolean','floatmask','wrongmask','heads','causal','nonfinite'])
def test_invalid_attention_contracts(b13,change):
 t=helper(b13);Q=np.ones((1,2,4));K=Q.copy();V=Q.copy();valid=np.ones((1,2),bool);heads=2;causal=False
 if change=='shape':K=np.ones((1,3,4))
 if change=='boolean':Q=np.ones((1,2,4),bool)
 if change=='floatmask':valid=valid.astype(float)
 if change=='wrongmask':valid=np.ones((1,3),bool)
 if change=='heads':heads=3
 if change=='causal':causal=1
 if change=='nonfinite':Q[0,0,0]=np.nan
 with pytest.raises(ValueError):t.attention(Q,K,V,heads,valid,causal=causal)


@pytest.mark.parametrize('topic',['bert','gpt'])
@pytest.mark.parametrize('settings',[{'vocab_size':5},{'vocab_size':129},{'d_model':1},{'d_model':17},{'d_model':3,'heads':2},{'heads':True},{'layers':0},{'layers':4},{'ff_dim':1},{'ff_dim':33},{'max_length':0},{'max_length':33},{'random_state':True}])
def test_architecture_invalid_bounds(b13,topic,settings):
 cls=getattr(b13.load(topic),topic.upper())
 args={'vocab_size':9};args.update(settings)
 with pytest.raises(ValueError):cls(**args)


@pytest.mark.numerical
@pytest.mark.parametrize('topic',['bert','gpt'])
def test_reproducible_initialization_shapes_and_owned_outputs(b13,topic):
 cls=getattr(b13.load(topic),topic.upper());a=cls(10,d_model=8,heads=4,layers=2,random_state=19);b=cls(10,d_model=8,heads=4,layers=2,random_state=19)
 ids=np.array([[2,5,6,3],[2,7,3,0]])
 assert_array_equal(a.logits(ids),b.logits(ids))
 h,p=a.encode(ids,return_attention=True)
 assert h.shape==(2,4,8) and a.logits(ids).shape==(2,4,10) and len(p)==2
 assert a.backbone_['token'].shape==(10,8) and a.backbone_['position'].shape==(32,8)
 h[:]=100;p[0][:]=100
 assert not np.any(a.encode(ids)==100)
 assert all(not np.any(x==100) for x in a.encode(ids,return_attention=True)[1])


@pytest.mark.numerical
def test_stable_head_extreme_bias_and_validation(b13):
 t=helper(b13);hidden=np.array([[[.2,.5],[.7,-.2]]]);targets=np.array([[5,6]]);selected=np.array([[True,False]])
 W=np.zeros((2,8));bias=np.array([1e6,-1e6,0,0,0,0,0,0.])
 loss,g=t.head_loss_gradients(hidden,targets,selected,W,bias)
 assert loss==1e6 and np.isfinite(g['head_weight']).all()
 for labels,mask in ((np.array([[-1,6]]),selected),(targets,np.zeros((1,2),bool)),(targets,np.ones((1,2))), (targets[:,:1],selected)):
  with pytest.raises(ValueError):t.head_loss_gradients(hidden,labels,mask,W,bias)


def test_reserved_id_contract_and_backbone_reuse(b13):
 a=b13.load('bert');b=b13.load('gpt')
 assert (a.PAD,a.UNK,a.BOS,a.EOS,a.MASK)==(0,1,2,3,4)
 assert a.t is b.t
 # Shared text vocabulary has a different UNK ID: adapting known IDs is explicit.
 vocab=b13.Vocabulary().fit(['cat dog']);encoded=vocab.encode('cat unseen')
 adapted=np.where(encoded==0,a.UNK,encoded+4)
 assert_array_equal(adapted,[5,1])


@pytest.mark.parametrize('shape',[(17,2,2),(1,33,2),(0,2,2),(1,0,2)])
def test_public_head_batch_and_length_work_bounds(b13,shape):
 t=helper(b13);h=np.ones(shape);targets=np.zeros(shape[:2],dtype=int);selected=np.ones(shape[:2],bool)
 with pytest.raises(ValueError):t.head_loss_gradients(h,targets,selected,np.zeros((2,8)),np.zeros(8))


def test_oversized_float_workspace_is_rejected_before_copy(b13,monkeypatch):
 t=helper(b13);oversized=np.ones((1,33,256));real_array=np.array
 def guarded_array(value,*args,**kwargs):
  if getattr(value,'size',0)>8192:raise AssertionError('oversized numerical copy attempted')
  return real_array(value,*args,**kwargs)
 with monkeypatch.context() as patch:
  patch.setattr(t.np,'array',guarded_array)
  with pytest.raises(ValueError,match='workspace limit'):t._finite(oversized,'oversized')
  with pytest.raises(ValueError,match='workspace limit'):t.attention(oversized,oversized,oversized,1,np.ones((1,33),bool))
  with pytest.raises(ValueError,match='workspace limit'):t.head_loss_gradients(oversized,np.zeros((1,33),int),np.ones((1,33),bool),np.zeros((16,8)),np.zeros(8))
