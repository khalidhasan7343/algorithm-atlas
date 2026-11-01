"""BERT-style bidirectional MLM encoder with a frozen backbone and trained head."""
import importlib.util
from pathlib import Path
import sys
import numpy as np
_spec=importlib.util.spec_from_file_location('atlas_b13_transformer',Path(__file__).resolve().parents[2]/'transformer_support.py')
t=sys.modules.get(_spec.name)
if t is None:
    t=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=t;_spec.loader.exec_module(t)
PAD,UNK,BOS,EOS,MASK=t.PAD,t.UNK,t.BOS,t.EOS,t.MASK


class BERT(t.TokenTransformer):
    """All selected ordinary targets become MASK; only the vocabulary head trains."""
    causal=False

    def select_mask(self,ids,*,fraction=.15,random_state=0):
        ids=self._batch(ids)
        fraction=t.s.scalar(fraction,'fraction',1e-6,1.)
        seed=t.s.integer(random_state,'random_state',0,2**32-1)
        candidates=np.flatnonzero(ids>=5)
        if not len(candidates):raise ValueError('MLM requires at least one ordinary token')
        count=max(1,int(np.ceil(fraction*len(candidates))))
        chosen=np.random.default_rng(seed).choice(candidates,size=count,replace=False)
        result=np.zeros(ids.shape,dtype=bool);result.flat[chosen]=True
        return result

    def _mlm(self,ids,selected_mask,*,allow_mask=False):
        ids=self._batch(ids);selected=np.asarray(selected_mask)
        if selected.shape!=ids.shape or selected.dtype.kind!='b' or not selected.any() or np.any(selected & ~((ids>=5) | ((ids==MASK) if allow_mask else False))):
            raise ValueError('MLM selection needs ordinary targets, or MASK for inference only')
        corrupted=ids.copy();corrupted[selected]=MASK
        return ids,selected.copy(),corrupted

    def logits(self,ids,selected_mask=None):
        if selected_mask is not None:ids=self._mlm(ids,selected_mask,allow_mask=True)[2]
        return self._head(self.encode(ids))

    def loss_gradients(self,ids,selected_mask):
        targets,selected,corrupted=self._mlm(ids,selected_mask)
        return t.head_loss_gradients(self.encode(corrupted),targets,selected,self.head_weight_,self.head_bias_)

    def fit(self,ids,selected_mask,*,epochs=100,learning_rate=.1):
        targets,selected,corrupted=self._mlm(ids,selected_mask)
        return self._train_head(self.encode(corrupted),targets,selected,epochs=epochs,learning_rate=learning_rate)

    def predict_masked(self,ids,selected_mask):
        _,selected,_=self._mlm(ids,selected_mask,allow_mask=True)
        return np.argmax(self.logits(ids,selected_mask)[selected],axis=-1)
