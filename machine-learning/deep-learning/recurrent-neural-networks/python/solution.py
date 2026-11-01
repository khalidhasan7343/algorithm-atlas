"""Vanilla tanh recurrent regression with full reverse-time shared-weight gradients."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b7_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)

def initialize(p,h,rng):
    return dict(Wx=support.weight(rng,p,h),Wh=support.weight(rng,h,h),b=np.zeros(h),Wo=support.weight(rng,h,1),bo=np.zeros(1))


def forward(p,X):
    h=np.zeros((len(X),len(p['b'])));cache=[]
    for t in range(X.shape[1]):
        previous=h;h=np.tanh(X[:,t]@p['Wx']+previous@p['Wh']+p['b']);cache.append((X[:,t],previous,h))
    return h@p['Wo']+p['bo'],cache


def backward(p,cache,delta):
    g={k:np.zeros_like(v) for k,v in p.items()};g['Wo']=cache[-1][2].T@delta;g['bo']=delta.sum(0)
    dh=delta@p['Wo'].T;dx=[]
    for x,previous,h in reversed(cache):
        dz=dh*(1-h**2);g['Wx']+=x.T@dz;g['Wh']+=previous.T@dz;g['b']+=dz.sum(0)
        dx.append(dz@p['Wx'].T);dh=dz@p['Wh'].T
    return g,np.stack(dx[::-1],axis=1)


def loss_gradients(p,X,y):
    output,cache=forward(p,X);loss,delta=support.mse(output,y);return loss,backward(p,cache,delta)[0]


class RNNRegressor(support.Settings):
    @support.numerical
    def fit(self,X,y):
        self._settings();X=support.sequence(X,fitting=True);y=support.targets(y,len(X));rng=np.random.default_rng(self.random_state)
        p=initialize(X.shape[2],self.hidden_dim,rng)
        p,info=self._train(p,X,y,lambda p,x,t,r:loss_gradients(p,x,t),rng)
        self.__dict__.update(info,parameters_=p,input_shape_=X.shape[1:]);return self

    @support.numerical
    def predict(self,X):
        X=self._query(X,support.sequence);return forward(self.parameters_,X)[0]


if __name__=='__main__':support.main(RNNRegressor,'sequence')
