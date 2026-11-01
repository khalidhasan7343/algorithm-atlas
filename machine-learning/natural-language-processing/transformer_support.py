"""Small token Transformers with an explicitly frozen backbone and trained head.

This is architecture teaching, not end-to-end or pretrained language modeling.
The approved B7 canonical owns the unchanged layer-normalization primitive.
"""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec = importlib.util.spec_from_file_location('atlas_b13_support', Path(__file__).with_name('support.py'))
s = sys.modules.get(_spec.name)
if s is None:
    s = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = s
    _spec.loader.exec_module(s)
_b7 = s.module('atlas_b7_transformer_for_b13', Path(__file__).parents[1]/'deep-learning/transformers/python/solution.py')
layer_norm = _b7.layer_norm
PAD, UNK, BOS, EOS, MASK = range(5)


class NumericalError(FloatingPointError):
    """A finite mathematical operation exceeded the supported numerical domain."""


def token_batch(value, vocab_size, max_length):
    if isinstance(value,(list,tuple)) and any(isinstance(x,(bool,np.bool_)) for x in np.asarray(value,dtype=object).flat):
        raise ValueError('boolean values cannot be token IDs, including mixed sequences')
    a = np.asarray(value)
    if a.ndim != 2 or a.dtype.kind not in 'iu' or not 1 <= a.shape[0] <= 16 or not 1 <= a.shape[1] <= max_length:
        raise ValueError('integer token IDs need shape (1..16,1..context_limit)')
    if np.any(a < 0) or np.any(a >= vocab_size):
        raise ValueError('token ID outside the configured vocabulary')
    valid = a != PAD
    if not np.all(valid.any(axis=1)) or np.any((~valid[:, :-1]) & valid[:, 1:]):
        raise ValueError('nonempty sequences with right padding only are required')
    return a.astype(np.int64, copy=True)


def _finite(value, name):
    a = np.asarray(value)
    if a.size > 8192:
        raise ValueError(name+' exceeds the 8192-element numerical workspace limit')
    if a.dtype.kind not in 'iuf' or not np.isfinite(a).all() or np.any(np.abs(a) > 1e6):
        raise ValueError(name+' must be finite real values of magnitude <=1e6')
    return np.array(a, dtype=float, copy=True)


def attention(Q, K, V, heads, valid, *, causal=False):
    """Scaled multi-head self-attention; padding queries return zero rows."""
    Q, K, V = [_finite(x, name) for x, name in ((Q,'Q'), (K,'K'), (V,'V'))]
    if Q.ndim != 3 or Q.shape != K.shape or Q.shape != V.shape:
        raise ValueError('Q,K,V must have identical (batch,length,width) shapes')
    batch, length, width = Q.shape
    heads = s.integer(heads,'heads',1,4)
    causal = s.boolean(causal,'causal')
    if not 1 <= batch <= 16 or not 1 <= length <= 32 or not 2 <= width <= 16 or width % heads:
        raise ValueError('attention dimensions exceed bounds or heads do not divide width')
    valid = np.asarray(valid)
    if valid.shape != (batch,length) or valid.dtype.kind != 'b':
        raise ValueError('valid must be a boolean key/query mask of shape (batch,length)')
    allowed = np.broadcast_to(valid[:,None,None,:], (batch,heads,length,length)).copy()
    if causal:
        allowed &= np.arange(length)[None,None,:,None] >= np.arange(length)[None,None,None,:]
    if np.any(~allowed.any(axis=-1)):
        raise ValueError('all-masked attention rows are undefined')
    size = width//heads
    q,k,v = [x.reshape(batch,length,heads,size).transpose(0,2,1,3) for x in (Q,K,V)]
    scores = q @ k.transpose(0,1,3,2)/np.sqrt(size)
    scores = np.where(allowed,scores,-np.inf)
    weights = np.exp(scores-np.max(scores,axis=-1,keepdims=True))
    weights /= weights.sum(axis=-1,keepdims=True)
    weights *= valid[:,None,:,None]
    result = (weights @ v).transpose(0,2,1,3).reshape(batch,length,width)
    if not np.isfinite(result).all():
        raise NumericalError('attention produced nonfinite values')
    return result, weights.copy()


def gelu(value):
    """The documented tanh approximation to GELU; backbone is frozen."""
    return .5*value*(1+np.tanh(np.sqrt(2/np.pi)*(value+.044715*value**3)))


def block(parameters, X, heads, valid, *, causal):
    Q,K,V = [X @ parameters['W'+name]+parameters['b'+name] for name in ('q','k','v')]
    context, weights = attention(Q,K,V,heads,valid,causal=causal)
    H = layer_norm(X+context @ parameters['Wa']+parameters['ba'],parameters['g1'],parameters['n1'])[0]
    F = gelu(H @ parameters['W1']+parameters['b1'])
    Z = layer_norm(H+F @ parameters['W2']+parameters['b2'],parameters['g2'],parameters['n2'])[0]
    return Z*valid[:,:,None], weights


def head_loss_gradients(hidden, targets, selected, weight, bias):
    """Mean selected-token CE and gradients of exactly the two trained groups."""
    hidden = _finite(hidden,'hidden')
    weight, bias = _finite(weight,'head_weight'), _finite(bias,'head_bias')
    if hidden.ndim != 3 or not 1 <= hidden.shape[0] <= 16 or not 1 <= hidden.shape[1] <= 32 or weight.ndim != 2 or not 2 <= weight.shape[0] <= 16 or not 6 <= weight.shape[1] <= 128 or bias.shape != (weight.shape[1],) or hidden.shape[-1] != weight.shape[0]:
        raise ValueError('head shape mismatch')
    targets, selected = np.asarray(targets), np.asarray(selected)
    if targets.shape != hidden.shape[:2] or targets.dtype.kind not in 'iu' or selected.shape != targets.shape or selected.dtype.kind != 'b' or np.any(targets < 0) or np.any(targets >= weight.shape[1]):
        raise ValueError('head targets/mask must match hidden positions and vocabulary')
    rows = hidden[selected]
    labels = targets[selected]
    if not len(rows):
        raise ValueError('at least one target position is required')
    logits = rows @ weight+bias
    shifted = logits-logits.max(axis=1,keepdims=True)
    logp = shifted-np.log(np.exp(shifted).sum(axis=1,keepdims=True))
    loss = -float(logp[np.arange(len(rows)),labels].mean())
    delta = np.exp(logp)
    delta[np.arange(len(rows)),labels] -= 1
    delta /= len(rows)
    gradients = dict(head_weight=rows.T @ delta,head_bias=delta.sum(axis=0))
    if not np.isfinite(loss) or not all(np.isfinite(x).all() for x in gradients.values()):
        raise NumericalError('head objective/gradient became nonfinite')
    return loss, gradients


class TokenTransformer:
    """Parameter-form learned embeddings/blocks, frozen in this educational scope."""
    trainable_parameters_ = ('head_weight','head_bias')

    def __init__(self,vocab_size,*,d_model=8,heads=2,ff_dim=16,layers=1,max_length=32,random_state=0):
        self.vocab_size = s.integer(vocab_size,'vocab_size',6,128)
        self.d_model = s.integer(d_model,'d_model',2,16)
        self.heads = s.integer(heads,'heads',1,4)
        self.ff_dim = s.integer(ff_dim,'ff_dim',2,32)
        self.layers = s.integer(layers,'layers',1,3)
        self.max_length = s.integer(max_length,'max_length',1,32)
        self.random_state = s.integer(random_state,'random_state',0,2**32-1)
        if self.d_model % self.heads:
            raise ValueError('heads must divide d_model')
        rng = np.random.default_rng(self.random_state)
        d,f = self.d_model,self.ff_dim
        token = rng.normal(0,.08,(self.vocab_size,d)); token[PAD] = 0
        self.backbone_ = dict(token=token,position=rng.normal(0,.03,(self.max_length,d)),blocks=[])
        for _ in range(self.layers):
            p = {name:rng.normal(0,1/np.sqrt(d),(d,d)) for name in ('Wq','Wk','Wv','Wa')}
            p.update({name:np.zeros(d) for name in ('bq','bk','bv','ba','n1','n2','b2')})
            p.update(g1=np.ones(d),g2=np.ones(d),W1=rng.normal(0,1/np.sqrt(d),(d,f)),b1=np.zeros(f),W2=rng.normal(0,1/np.sqrt(f),(f,d)))
            self.backbone_['blocks'].append(p)
        self.head_weight_ = rng.normal(0,.02,(d,self.vocab_size))
        self.head_bias_ = np.zeros(self.vocab_size)
        self._initial_head = self.head_weight_.copy(),self.head_bias_.copy()
        self.status_,self.converged_,self.n_iter_ = 'initialized',None,0

    def _batch(self,ids,extra=0):
        return token_batch(ids,self.vocab_size,self.max_length+extra)

    def encode(self,ids,*,return_attention=False):
        return_attention = s.boolean(return_attention,'return_attention')
        ids = self._batch(ids)
        valid = ids != PAD
        hidden = (self.backbone_['token'][ids]+self.backbone_['position'][None,:ids.shape[1]])*valid[:,:,None]
        weights = []
        for p in self.backbone_['blocks']:
            hidden,prob = block(p,hidden,self.heads,valid,causal=self.causal)
            if return_attention:
                weights.append(prob)
        if not np.isfinite(hidden).all():
            raise NumericalError('contextual representation became nonfinite')
        return (hidden.copy(),tuple(weights)) if return_attention else hidden.copy()

    def _head(self,hidden):
        W,b = _finite(self.head_weight_,'head_weight'),_finite(self.head_bias_,'head_bias')
        if W.shape != (self.d_model,self.vocab_size) or b.shape != (self.vocab_size,):
            raise ValueError('head shape mismatch')
        output = hidden @ W+b
        if not np.isfinite(output).all():
            raise NumericalError('token logits became nonfinite')
        return output

    def _train_head(self,hidden,targets,selected,*,epochs,learning_rate):
        epochs = s.integer(epochs,'epochs',1,500)
        learning_rate = s.scalar(learning_rate,'learning_rate',1e-6,1.)
        if epochs*int(selected.sum())*self.d_model*self.vocab_size > 2e7:
            raise ValueError('head training work budget exceeded')
        W,b = [x.copy() for x in self._initial_head]
        history = [head_loss_gradients(hidden,targets,selected,W,b)[0]]
        for _ in range(epochs):
            _,g = head_loss_gradients(hidden,targets,selected,W,b)
            W -= learning_rate*g['head_weight']; b -= learning_rate*g['head_bias']
            if not np.isfinite(W).all() or not np.isfinite(b).all() or np.any(np.abs(W)>1e6) or np.any(np.abs(b)>1e6):
                raise NumericalError('head update exceeded finite parameter domain')
            history.append(head_loss_gradients(hidden,targets,selected,W,b)[0])
        self.head_weight_,self.head_bias_ = W,b
        self.loss_history_ = np.array(history)
        self.status_,self.converged_,self.n_iter_ = 'epoch-budget',None,epochs
        return self
