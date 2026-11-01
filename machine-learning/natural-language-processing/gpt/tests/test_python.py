import copy
import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


def model(b13,**kwargs):return b13.load('gpt').GPT(9,d_model=4,heads=2,ff_dim=5,**kwargs)


@pytest.mark.oracle
def test_shifted_next_token_alignment_and_cross_entropy(b13):
 m=model(b13);sequences=np.array([[2,5,6,3],[2,7,3,0]])
 logits=m.logits(sequences[:,:-1]);terms=[]
 for batch in range(2):
  for step in range(3):
   target=sequences[batch,step+1]
   if target!=0:
    row=logits[batch,step];terms.append(np.log(sum(np.exp(row-row.max())))+row.max()-row[target])
 assert_allclose(m.loss_gradients(sequences)[0],np.mean(terms),atol=1e-13)
 # Independently ensure the label is next token rather than self.
 current=[]
 for row,label in zip(logits[0],sequences[0,:-1]):current.append(np.log(sum(np.exp(row-row.max())))+row.max()-row[label])
 assert not np.isclose(m.loss_gradients(sequences[:1])[0],np.mean(current))


@pytest.mark.numerical
@pytest.mark.parametrize('layers',[1,2])
def test_finite_difference_every_head_parameter(b13,layers):
 m=model(b13,layers=layers);sequences=np.array([[2,5,6,3],[2,7,3,0]])
 _,g=m.loss_gradients(sequences);epsilon=1e-6
 for name in m.trainable_parameters_:
  p=getattr(m,name+'_')
  for index in np.ndindex(p.shape):
   old=p[index];p[index]=old+epsilon;plus=m.loss_gradients(sequences)[0]
   p[index]=old-epsilon;minus=m.loss_gradients(sequences)[0];p[index]=old
   assert_allclose(g[name][index],(plus-minus)/(2*epsilon),atol=3e-7,rtol=3e-5)


@pytest.mark.oracle
@pytest.mark.parametrize('layers',[1,3])
def test_future_tokens_cannot_affect_earlier_logits_and_causal_weights(b13,layers):
 m=model(b13,layers=layers);ids=np.array([[2,5,6,7]])
 changed=ids.copy();changed[0,2:]=[8,5]
 assert_array_equal(m.logits(ids)[:,:2],m.logits(changed)[:,:2])
 assert not np.allclose(m.logits(ids)[:,2:],m.logits(changed)[:,2:])
 _,weights=m.encode(ids,return_attention=True)
 for p in weights:
  assert_allclose(p.sum(-1),1)
  for step in range(4):assert_allclose(p[:,:,step,step+1:],0)


@pytest.mark.oracle
def test_right_padding_does_not_change_valid_logits_or_loss(b13):
 m=model(b13);ids=np.array([[2,5,6]])
 assert_allclose(m.logits(ids),m.logits([[2,5,6,0,0]])[:,:3],atol=1e-13)
 assert_allclose(m.loss_gradients([[2,5,6,3]])[0],m.loss_gradients([[2,5,6,3,0,0]])[0],atol=1e-13)
 _,p=m.encode([[2,5,6,0,0]],return_attention=True)
 assert_allclose(p[0][:,:,:,3:],0);assert_allclose(p[0][:,:,3:],0)


@pytest.mark.numerical
@pytest.mark.parametrize('seed',[0,17])
def test_tiny_corpus_head_learning_reproducibility_backbone_frozen(b13,seed):
 m=model(b13,random_state=seed);sequences=np.array([[2,5,6,5,6,3],[2,5,6,5,6,3]])
 before=copy.deepcopy(m.backbone_);initial=m.head_weight_.copy();m.fit(sequences,epochs=120,learning_rate=.1)
 assert m.loss_history_[-1]<.5*m.loss_history_[0];assert not np.array_equal(initial,m.head_weight_)
 assert m.trainable_parameters_==('head_weight','head_bias') and m.status_=='epoch-budget' and m.converged_ is None
 for name in ('token','position'):assert_array_equal(before[name],m.backbone_[name])
 for a,b in zip(before['blocks'],m.backbone_['blocks']):
  for name in a:assert_array_equal(a[name],b[name])
 other=model(b13,random_state=seed).fit(sequences,epochs=120,learning_rate=.1)
 assert_array_equal(m.head_weight_,other.head_weight_);assert_array_equal(m.loss_history_,other.loss_history_)


@pytest.mark.numerical
def test_exact_gradient_step_and_failed_refit_atomic(b13):
 m=model(b13);seq=np.array([[2,5,6,3]]);weight=m.head_weight_.copy();bias=m.head_bias_.copy();_,g=m.loss_gradients(seq)
 m.fit(seq,epochs=1,learning_rate=.03)
 assert_allclose(m.head_weight_,weight-.03*g['head_weight']);assert_allclose(m.head_bias_,bias-.03*g['head_bias'])
 before=m.head_weight_.copy()
 with pytest.raises(ValueError):m.fit(seq,learning_rate=float('nan'))
 assert_array_equal(before,m.head_weight_)


@pytest.mark.parametrize('seed',[0,4,88])
def test_generation_seed_bounded_special_filter_and_eos(b13,seed):
 m=model(b13);prefix=[2,5]
 a=m.generate(prefix,max_new_tokens=8,temperature=.7,random_state=seed)
 assert_array_equal(a,m.generate(prefix,max_new_tokens=8,temperature=.7,random_state=seed))
 assert_array_equal(a[:2],prefix);assert len(a)<=10
 assert not np.any(np.isin(a[2:],[0,2,4]))
 assert_array_equal(m.generate(prefix,max_new_tokens=0),prefix)
 assert_array_equal(m.generate([2,3],max_new_tokens=3),[2,3])
 m.head_weight_[:]=0;m.head_bias_[:]=-100;m.head_bias_[3]=100
 assert_array_equal(m.generate(prefix,max_new_tokens=8,random_state=seed),[2,5,3])


@pytest.mark.oracle
def test_generation_matches_independent_legal_distribution(b13):
 m=model(b13);m.head_weight_[:]=0;m.head_bias_=np.array([1e3,1.,1e3,2.,1e3,3.,4.,5.,6.])
 legal=np.array([1,3,5,6,7,8]);logits=m.head_bias_[legal]/.8
 weights=np.exp(logits-max(logits));weights/=sum(weights)
 expected=int(np.random.default_rng(42).choice(legal,p=weights))
 assert m.generate([2,5],max_new_tokens=1,temperature=.8,random_state=42)[-1]==expected


@pytest.mark.parametrize('kwargs',[{'temperature':0},{'temperature':float('inf')},{'temperature':True},{'max_new_tokens':-1},{'max_new_tokens':33},{'random_state':-1}])
def test_invalid_generation_settings(b13,kwargs):
 with pytest.raises(ValueError):model(b13).generate([2,5],**kwargs)


@pytest.mark.parametrize('prefix',[[],[0],[2,0],[2,-1],[2,9],[[2,5]],[2.,5.],[2,True]])
def test_invalid_generation_prefix(b13,prefix):
 with pytest.raises(ValueError):model(b13).generate(prefix,max_new_tokens=0)


@pytest.mark.parametrize('sequences',[[[2]],[[2,0,0]],[[2,5],[0,0]],[[2,0,5]],[[True,False]]])
def test_invalid_training_sequences(b13,sequences):
 with pytest.raises(ValueError):model(b13).loss_gradients(sequences)


def test_context_generation_and_training_work_budgets(b13):
 m=model(b13,max_length=3)
 with pytest.raises(ValueError):m.generate([2,5],max_new_tokens=2)
 assert np.isfinite(m.loss_gradients([[2,5,6,3]])[0])
 with pytest.raises(ValueError):m.loss_gradients([[2,5,6,7,3]])
 large=b13.load('gpt').GPT(128,d_model=16,heads=4)
 with pytest.raises(ValueError,match='budget'):large.fit(np.full((16,33),5),epochs=500)
