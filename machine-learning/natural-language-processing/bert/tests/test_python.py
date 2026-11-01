import copy
import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


def model(b13,**kwargs):return b13.load('bert').BERT(9,d_model=4,heads=2,ff_dim=5,**kwargs)


@pytest.mark.oracle
def test_mlm_cross_entropy_and_head_gradients_hand(b13):
 m=model(b13);ids=np.array([[2,5,6,3],[2,7,3,0]]);selected=np.array([[False,True,False,False],[False,True,False,False]])
 corrupted=ids.copy();corrupted[selected]=4
 hidden=m.encode(corrupted);logits=hidden[selected]@m.head_weight_+m.head_bias_
 losses=[];dw=np.zeros_like(m.head_weight_);db=np.zeros_like(m.head_bias_)
 for row,label,h in zip(logits,ids[selected],hidden[selected]):
  exp=np.array([np.exp(v-max(row)) for v in row]);prob=exp/sum(exp)
  losses.append(np.log(sum(exp))+max(row)-row[label]);prob[label]-=1
  dw+=np.outer(h,prob)/2;db+=prob/2
 loss,g=m.loss_gradients(ids,selected)
 assert_allclose(loss,np.mean(losses),atol=1e-13);assert_allclose(g['head_weight'],dw,atol=1e-13);assert_allclose(g['head_bias'],db,atol=1e-13)
 assert m.trainable_parameters_==('head_weight','head_bias')


@pytest.mark.numerical
@pytest.mark.parametrize('layers',[1,2])
def test_finite_difference_every_trainable_head_coordinate(b13,layers):
 m=model(b13,layers=layers);ids=np.array([[2,5,6,3]]);selected=np.array([[False,True,True,False]])
 _,g=m.loss_gradients(ids,selected);epsilon=1e-6
 for name in m.trainable_parameters_:
  p=getattr(m,name+'_')
  for index in np.ndindex(p.shape):
   old=p[index];p[index]=old+epsilon;plus=m.loss_gradients(ids,selected)[0]
   p[index]=old-epsilon;minus=m.loss_gradients(ids,selected)[0];p[index]=old
   assert_allclose(g[name][index],(plus-minus)/(2*epsilon),atol=3e-7,rtol=3e-5)


@pytest.mark.oracle
def test_masking_never_exposes_selected_gold_embeddings(b13):
 m=model(b13);ids=np.array([[2,5,6,3]]);selected=np.array([[False,True,False,False]])
 changed=ids.copy();changed[0,1]=7
 assert_array_equal(m.logits(ids,selected),m.logits(changed,selected))
 # Changing an unselected context token does affect the prediction.
 changed=ids.copy();changed[0,2]=8
 assert not np.allclose(m.logits(ids,selected)[0,1],m.logits(changed,selected)[0,1])
 # The target is still the original selected token, not MASK.
 assert m.loss_gradients(ids,selected)[0]!=m.loss_gradients(np.array([[2,7,6,3]]),selected)[0]


@pytest.mark.parametrize('seed',[0,7,99])
def test_selection_is_seeded_ordinary_only_and_exact_count(b13,seed):
 m=model(b13);ids=np.array([[2,5,6,7,3,0],[2,8,6,5,3,0]])
 mask=m.select_mask(ids,fraction=.5,random_state=seed)
 assert mask.dtype==bool and mask.sum()==3 and not np.any(mask & (ids<5))
 assert_array_equal(mask,m.select_mask(ids,fraction=.5,random_state=seed))
 assert m.select_mask(ids,fraction=1).sum()==6


@pytest.mark.oracle
@pytest.mark.parametrize('layers',[1,3])
def test_bidirectional_future_intervention_and_padding_invariance(b13,layers):
 m=model(b13,layers=layers);ids=np.array([[2,5,6]])
 changed=ids.copy();changed[0,2]=8
 assert not np.allclose(m.logits(ids)[0,0],m.logits(changed)[0,0])
 padded=np.array([[2,5,6,0,0]])
 assert_allclose(m.encode(ids),m.encode(padded)[:,:3],atol=1e-13)
 assert_allclose(m.encode(padded)[:,3:],0)
 hidden,weights=m.encode(padded,return_attention=True)
 assert hidden.shape==(1,5,4) and len(weights)==layers
 for prob in weights:
  assert_allclose(prob[:,:,:3].sum(-1),1);assert_allclose(prob[:,:,:,3:],0);assert_allclose(prob[:,:,3:],0)
  assert np.all(prob[:,:,0,1:3]>0)
 # Even an arbitrary padding embedding cannot influence active outputs.
 m.backbone_['token'][0]=1e5
 assert_allclose(m.encode(ids),m.encode(padded)[:,:3],atol=1e-13)


@pytest.mark.numerical
@pytest.mark.parametrize('seed',[0,21])
def test_genuine_head_learning_frozen_backbone_repeated_fit_and_rng(b13,seed):
 m=model(b13,random_state=seed);ids=np.array([[2,5,6,3],[2,5,7,3]])
 selected=np.array([[False,True,False,False],[False,True,False,False]])
 before=copy.deepcopy(m.backbone_);w=m.head_weight_.copy();m.fit(ids,selected,epochs=80,learning_rate=.1)
 assert m.loss_history_[-1]<.2*m.loss_history_[0];assert not np.array_equal(w,m.head_weight_)
 assert_array_equal(m.predict_masked(ids,selected),[5,5])
 assert m.status_=='epoch-budget' and m.converged_ is None and m.n_iter_==80
 for name in ('token','position'):assert_array_equal(before[name],m.backbone_[name])
 for a,b in zip(before['blocks'],m.backbone_['blocks']):
  for name in a:assert_array_equal(a[name],b[name])
 expected=m.head_weight_.copy();m.fit(ids,selected,epochs=80,learning_rate=.1);assert_array_equal(expected,m.head_weight_)
 other=model(b13,random_state=seed).fit(ids,selected,epochs=80,learning_rate=.1)
 assert_array_equal(m.head_weight_,other.head_weight_)


@pytest.mark.numerical
def test_exact_first_gradient_update_and_atomic_invalid_fit(b13):
 m=model(b13);ids=np.array([[2,5,6,3]]);mask=np.array([[False,True,False,False]])
 before=m.head_weight_.copy();bias=m.head_bias_.copy();_,g=m.loss_gradients(ids,mask)
 m.fit(ids,mask,epochs=1,learning_rate=.07)
 assert_allclose(m.head_weight_,before-.07*g['head_weight']);assert_allclose(m.head_bias_,bias-.07*g['head_bias'])
 saved=m.head_weight_.copy()
 with pytest.raises(ValueError):m.fit(ids,mask,epochs=0)
 assert_array_equal(saved,m.head_weight_)
 out=m.encode(ids);out[:]=100;assert not np.array_equal(out,m.encode(ids))


@pytest.mark.parametrize('ids',[[],[[]],[[True,False]],[[2,True]],[[1.,2.]],[[2,-1]],[[2,9]],[[0,0]],[[2,0,5]],np.ones((17,2),int),np.ones((1,33),int)])
def test_invalid_token_shapes_ids_and_padding(b13,ids):
 with pytest.raises(ValueError):model(b13).encode(ids)


@pytest.mark.parametrize('mask',[[[0,1,0,0]],[[True]],[[False,False,False,False]],[[True,False,False,False]],[[False,False,False,True]]])
def test_invalid_mlm_selection(b13,mask):
 with pytest.raises(ValueError):model(b13).loss_gradients([[2,5,6,3]],mask)


@pytest.mark.parametrize('kwargs',[{'fraction':0},{'fraction':2},{'random_state':True}])
def test_invalid_mask_selection_settings(b13,kwargs):
 with pytest.raises(ValueError):model(b13).select_mask([[2,5,3]],**kwargs)


def test_no_ordinary_targets_and_training_work_bound(b13):
 m=model(b13)
 with pytest.raises(ValueError):m.select_mask([[2,3]])
 large=b13.load('bert').BERT(128,d_model=16,heads=4)
 ids=np.full((16,32),5);mask=np.ones_like(ids,dtype=bool)
 with pytest.raises(ValueError,match='budget'):large.fit(ids,mask,epochs=500)


@pytest.mark.oracle
def test_actual_masked_inference_needs_no_gold_target(b13):
 m=model(b13);ids=np.array([[2,4,6,3]]);selected=np.array([[False,True,False,False]])
 assert_array_equal(m.predict_masked(ids,selected),np.argmax(m.logits(ids)[selected],axis=-1))
 with pytest.raises(ValueError):m.loss_gradients(ids,selected)
