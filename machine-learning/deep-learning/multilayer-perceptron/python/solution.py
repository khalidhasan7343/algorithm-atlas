"""Binary tanh MLP with stable logit BCE and explicit chain-rule gradients."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b7_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)

def initialize(p,h,rng):
    return dict(W1=support.weight(rng,p,h),b1=np.zeros(h),W2=support.weight(rng,h,1),b2=np.zeros(1))


def forward(parameters,X):
    hidden=np.tanh(X@parameters['W1']+parameters['b1'])
    logits=hidden@parameters['W2']+parameters['b2']
    return logits,hidden


def loss_gradients(parameters,X,y):
    logits,hidden=forward(parameters,X);loss,delta=support.bce(logits,y)
    dh=(delta@parameters['W2'].T)*(1-hidden**2)
    return loss,dict(W1=X.T@dh,b1=dh.sum(0),W2=hidden.T@delta,b2=delta.sum(0))


class MLPClassifier(support.Settings):
    @support.numerical
    def fit(self,X,y):
        self._settings();X=support.tabular(X,fitting=True);y=support.targets(y,len(X),binary=True)
        rng=np.random.default_rng(self.random_state);params=initialize(X.shape[1],self.hidden_dim,rng)
        params,info=self._train(params,X,y,lambda p,x,t,r:loss_gradients(p,x,t),rng)
        self.__dict__.update(info,parameters_=params,input_shape_=X.shape[1:])
        return self

    @support.numerical
    def predict_proba(self,X):
        X=self._query(X);probability=support.sigmoid(forward(self.parameters_,X)[0]).ravel()
        return np.column_stack([1-probability,probability])

    def predict(self,X):return (self.predict_proba(X)[:,1]>=.5).astype(int)


if __name__=='__main__':support.main(MLPClassifier,'classifier')
