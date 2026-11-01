"""Compact fully connected residual block; explicit skip and residual adjoints."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b7_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)

def initialize(p,h,rng):
    return dict(W1=support.weight(rng,p,h),b1=np.zeros(h),W2=support.weight(rng,h,p),b2=np.zeros(p),Wout=support.weight(rng,p,1),bout=np.zeros(1))


def residual_add(X,residual):
    if X.shape!=residual.shape:raise ValueError('identity shortcut and residual shapes must match exactly')
    return X+residual


def forward(p,X):
    hidden=np.tanh(X@p['W1']+p['b1']);Z=residual_add(X,hidden@p['W2']+p['b2'])
    return Z@p['Wout']+p['bout'],(X,hidden,Z)


def backward(p,cache,delta):
    X,hidden,Z=cache;dZ=delta@p['Wout'].T;dH=(dZ@p['W2'].T)*(1-hidden**2)
    gradients=dict(Wout=Z.T@delta,bout=delta.sum(0),W2=hidden.T@dZ,b2=dZ.sum(0),W1=X.T@dH,b1=dH.sum(0))
    return gradients,dZ+dH@p['W1'].T


def loss_gradients(p,X,y):
    output,cache=forward(p,X);loss,delta=support.mse(output,y)
    return loss,backward(p,cache,delta)[0]


class ResidualRegressor(support.Settings):
    @support.numerical
    def fit(self,X,y):
        self._settings();X=support.tabular(X,fitting=True);y=support.targets(y,len(X));rng=np.random.default_rng(self.random_state)
        p=initialize(X.shape[1],self.hidden_dim,rng)
        p,info=self._train(p,X,y,lambda p,x,t,r:loss_gradients(p,x,t),rng)
        self.__dict__.update(info,parameters_=p,input_shape_=X.shape[1:]);return self

    @support.numerical
    def predict(self,X):
        X=self._query(X);return forward(self.parameters_,X)[0]


if __name__=='__main__':support.main(ResidualRegressor,'regression')
