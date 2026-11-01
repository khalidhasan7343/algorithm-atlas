"""One post-norm Transformer encoder block with multi-head masked attention and explicit adjoints."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b7_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)

def positional(length,width):
    positions=np.arange(length)[:,None];dimensions=np.arange(width)[None,:]
    angles=positions/(10000**(2*(dimensions//2)/width))
    return np.where(dimensions%2==0,np.sin(angles),np.cos(angles))


def layer_norm(X,gamma,beta):
    centered=X-X.mean(axis=-1,keepdims=True);inv=1/np.sqrt(np.mean(centered**2,axis=-1,keepdims=True)+1e-5)
    normalized=centered*inv
    return normalized*gamma+beta,(normalized,inv,gamma)


def layer_norm_backward(delta,cache):
    normalized,inv,gamma=cache;g=delta*gamma
    dx=inv*(g-g.mean(axis=-1,keepdims=True)-normalized*np.mean(g*normalized,axis=-1,keepdims=True))
    axes=tuple(range(delta.ndim-1))
    return dx,np.sum(delta*normalized,axis=axes),np.sum(delta,axis=axes)


def attention(Q,K,V,heads,causal):
    n,t,d=Q.shape;size=d//heads
    q,k,v=[a.reshape(n,t,heads,size).transpose(0,2,1,3) for a in (Q,K,V)]
    scores=q@k.transpose(0,1,3,2)/np.sqrt(size)
    mask=np.triu(np.ones((t,t),dtype=bool),1) if causal else np.zeros((t,t),dtype=bool)
    scores=np.where(mask,-np.inf,scores);prob=support.softmax(scores)
    out=(prob@v).transpose(0,2,1,3).reshape(n,t,d)
    return out,(q,k,v,prob,mask)


def attention_backward(delta,cache):
    q,k,v,prob,mask=cache;n,h,t,size=q.shape
    dc=delta.reshape(n,t,h,size).transpose(0,2,1,3)
    dv=prob.transpose(0,1,3,2)@dc;dp=dc@v.transpose(0,1,3,2)
    ds=prob*(dp-np.sum(dp*prob,axis=-1,keepdims=True));ds=np.where(mask,0,ds)
    dq=ds@k/np.sqrt(size);dk=ds.transpose(0,1,3,2)@q/np.sqrt(size)
    return tuple(a.transpose(0,2,1,3).reshape(n,t,h*size) for a in (dq,dk,dv))


def initialize(p,d,f,rng):
    result=dict(Win=support.weight(rng,p,d),bin=np.zeros(d),Wa=support.weight(rng,d,d),ba=np.zeros(d),
        W1=support.weight(rng,d,f),b1=np.zeros(f),W2=support.weight(rng,f,d),b2=np.zeros(d),
        g1=np.ones(d),n1=np.zeros(d),g2=np.ones(d),n2=np.zeros(d),Wo=support.weight(rng,d,1),bo=np.zeros(1))
    for name in ('q','k','v'):result['W'+name]=support.weight(rng,d,d);result['b'+name]=np.zeros(d)
    return result


def forward(p,X,heads=1,causal=True):
    E=X@p['Win']+p['bin']+positional(X.shape[1],len(p['bin']))
    Q,K,V=[E@p['W'+name]+p['b'+name] for name in ('q','k','v')]
    C,att_cache=attention(Q,K,V,heads,causal)
    H,norm1=layer_norm(E+C@p['Wa']+p['ba'],p['g1'],p['n1'])
    F=np.tanh(H@p['W1']+p['b1'])
    Z,norm2=layer_norm(H+F@p['W2']+p['b2'],p['g2'],p['n2'])
    return Z[:,-1]@p['Wo']+p['bo'],(X,E,C,H,F,Z,att_cache,norm1,norm2)


def loss_gradients(p,X,y,heads=1,causal=True):
    output,cache=forward(p,X,heads,causal);loss,delta=support.mse(output,y)
    X,E,C,H,F,Z,att_cache,norm1,norm2=cache
    g=dict(Wo=Z[:,-1].T@delta,bo=delta.sum(0));dZ=np.zeros_like(Z);dZ[:,-1]=delta@p['Wo'].T
    dR,g['g2'],g['n2']=layer_norm_backward(dZ,norm2)
    g['W2']=np.einsum('ntf,ntd->fd',F,dR);g['b2']=dR.sum(axis=(0,1))
    dF=(dR@p['W2'].T)*(1-F**2);g['W1']=np.einsum('ntd,ntf->df',H,dF);g['b1']=dF.sum(axis=(0,1))
    dH=dR+dF@p['W1'].T;dA,g['g1'],g['n1']=layer_norm_backward(dH,norm1)
    g['Wa']=np.einsum('ntd,nte->de',C,dA);g['ba']=dA.sum(axis=(0,1))
    dQ,dK,dV=attention_backward(dA@p['Wa'].T,att_cache);dE=dA.copy()
    for name,direction in zip(('q','k','v'),(dQ,dK,dV)):
        g['W'+name]=np.einsum('ntd,nte->de',E,direction);g['b'+name]=direction.sum(axis=(0,1));dE+=direction@p['W'+name].T
    g['Win']=np.einsum('ntp,ntd->pd',X,dE);g['bin']=dE.sum(axis=(0,1))
    return loss,g


class TransformerRegressor(support.Settings):
    def __init__(self,d_model=4,heads=2,causal=True,**kwargs):
        self.d_model,self.heads,self.causal=d_model,heads,causal;super().__init__(**kwargs);self._architecture()

    def _architecture(self):
        support.integer(self.d_model,'d_model',2,8);support.integer(self.heads,'heads',1,4);support.boolean(self.causal,'causal')
        if self.d_model%self.heads:raise ValueError('d_model must be divisible by heads')

    @support.numerical
    def fit(self,X,y):
        self._settings();self._architecture();X=support.sequence(X,fitting=True);y=support.targets(y,len(X));rng=np.random.default_rng(self.random_state)
        p=initialize(X.shape[2],self.d_model,self.hidden_dim,rng)
        p,info=self._train(p,X,y,lambda p,x,t,r:loss_gradients(p,x,t,self.heads,self.causal),rng)
        self.__dict__.update(info,parameters_=p,input_shape_=X.shape[1:],heads_=self.heads,causal_=self.causal);return self

    @support.numerical
    def predict(self,X):
        X=self._query(X,support.sequence);return forward(self.parameters_,X,self.heads_,self.causal_)[0]


if __name__=='__main__':support.main(TransformerRegressor,'sequence')
