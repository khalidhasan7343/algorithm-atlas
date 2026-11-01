"""Reset-before-matrix GRU: h=z*h_previous+(1-z)*candidate; explicit BPTT."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b7_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)

def initialize(p,h,rng):
    result={}
    for gate in ('r','z','g'):
        result['W'+gate]=support.weight(rng,p,h);result['U'+gate]=support.weight(rng,h,h);result['b'+gate]=np.zeros(h)
    result.update(Wo=support.weight(rng,h,1),bo=np.zeros(1));return result


def forward(p,X):
    h=np.zeros((len(X),len(p['br'])));cache=[]
    for t in range(X.shape[1]):
        previous=h;x=X[:,t]
        r=support.sigmoid(x@p['Wr']+previous@p['Ur']+p['br'])
        z=support.sigmoid(x@p['Wz']+previous@p['Uz']+p['bz'])
        candidate=np.tanh(x@p['Wg']+(r*previous)@p['Ug']+p['bg'])
        h=z*previous+(1-z)*candidate;cache.append((x,previous,r,z,candidate,h))
    return h@p['Wo']+p['bo'],cache


def backward(p,cache,delta):
    g={k:np.zeros_like(v) for k,v in p.items()};g['Wo']=cache[-1][-1].T@delta;g['bo']=delta.sum(0)
    dh=delta@p['Wo'].T;dx=[]
    for x,previous,r,z,candidate,h in reversed(cache):
        da_g=dh*(1-z)*(1-candidate**2);da_z=dh*(previous-candidate)*z*(1-z)
        reset_product=da_g@p['Ug'].T;da_r=reset_product*previous*r*(1-r)
        g['Wg']+=x.T@da_g;g['Ug']+=(r*previous).T@da_g;g['bg']+=da_g.sum(0)
        for gate,da in [('r',da_r),('z',da_z)]:
            g['W'+gate]+=x.T@da;g['U'+gate]+=previous.T@da;g['b'+gate]+=da.sum(0)
        dx.append(da_g@p['Wg'].T+da_r@p['Wr'].T+da_z@p['Wz'].T)
        dh=dh*z+reset_product*r+da_r@p['Ur'].T+da_z@p['Uz'].T
    return g,np.stack(dx[::-1],axis=1)


def loss_gradients(p,X,y):
    output,cache=forward(p,X);loss,delta=support.mse(output,y);return loss,backward(p,cache,delta)[0]


class GRURegressor(support.Settings):
    @support.numerical
    def fit(self,X,y):
        self._settings();X=support.sequence(X,fitting=True);y=support.targets(y,len(X));rng=np.random.default_rng(self.random_state)
        p=initialize(X.shape[2],self.hidden_dim,rng)
        p,info=self._train(p,X,y,lambda p,x,t,r:loss_gradients(p,x,t),rng)
        self.__dict__.update(info,parameters_=p,input_shape_=X.shape[1:]);return self

    @support.numerical
    def predict(self,X):
        X=self._query(X,support.sequence);return forward(self.parameters_,X)[0]


if __name__=='__main__':support.main(GRURegressor,'sequence')
