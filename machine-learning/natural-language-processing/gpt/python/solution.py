"""GPT-style causal token decoder with a frozen backbone and trained vocabulary head."""
import importlib.util
from pathlib import Path
import sys
import numpy as np
_spec=importlib.util.spec_from_file_location('atlas_b13_transformer',Path(__file__).resolve().parents[2]/'transformer_support.py')
t=sys.modules.get(_spec.name)
if t is None:
    t=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=t;_spec.loader.exec_module(t)
PAD,UNK,BOS,EOS,MASK=t.PAD,t.UNK,t.BOS,t.EOS,t.MASK


class GPT(t.TokenTransformer):
    """A real causal Transformer; optimization updates head weights and bias only."""
    causal=True

    def logits(self,ids):
        return self._head(self.encode(ids))

    def _next_token(self,sequences):
        ids=self._batch(sequences,extra=1)
        if ids.shape[1]<2 or np.any(np.sum(ids!=PAD,axis=1)<2):
            raise ValueError('each training sequence needs at least two nonpadding tokens')
        inputs,targets=ids[:,:-1],ids[:,1:]
        return inputs,targets,targets!=PAD

    def loss_gradients(self,sequences):
        inputs,targets,selected=self._next_token(sequences)
        return t.head_loss_gradients(self.encode(inputs),targets,selected,self.head_weight_,self.head_bias_)

    def fit(self,sequences,*,epochs=100,learning_rate=.1):
        inputs,targets,selected=self._next_token(sequences)
        return self._train_head(self.encode(inputs),targets,selected,epochs=epochs,learning_rate=learning_rate)

    def generate(self,prefix,*,max_new_tokens=8,temperature=1.,random_state=0):
        original_prefix=prefix
        prefix=np.asarray(prefix)
        if prefix.ndim!=1:raise ValueError('prefix must be one integer token sequence')
        ids=self._batch([original_prefix])[0]
        if np.any(ids==PAD):raise ValueError('generation prefix cannot contain PAD')
        count=t.s.integer(max_new_tokens,'max_new_tokens',0,32)
        temperature=t.s.scalar(temperature,'temperature',1e-6,100.)
        seed=t.s.integer(random_state,'random_state',0,2**32-1)
        if len(ids)+count>self.max_length:raise ValueError('prefix plus generation budget exceeds context length')
        result=ids.tolist();rng=np.random.default_rng(seed)
        legal=np.array([i for i in range(self.vocab_size) if i not in (PAD,BOS,MASK)])
        for _ in range(count):
            if result[-1]==EOS:break
            logits=self.logits(np.array([result]))[0,-1,legal]/temperature
            prob=np.exp(logits-logits.max());prob/=prob.sum()
            result.append(int(rng.choice(legal,p=prob)))
        return np.array(result,dtype=np.int64)
