"""LSTM with separate cell/hidden adjoints and input,forget,output,candidate gates."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b7_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)

def initialize(p,h,rng):
    b=np.zeros(4*h);b[h:2*h]=1.
    return dict(Wx=support.weight(rng,p,4*h),Wh=support.weight(rng,h,4*h),b=b,Wo=support.weight(rng,h,1),bo=np.zeros(1))


def forward(p,X):
    h=np.zeros((len(X),p['Wh'].shape[0]));c=np.zeros_like(h);cache=[]
    for t in range(X.shape[1]):
        previous,old_cell=h,c;parts=np.split(X[:,t]@p['Wx']+previous@p['Wh']+p['b'],4,axis=1)
        i,f,o=[support.sigmoid(a) for a in parts[:3]];candidate=np.tanh(parts[3])
        c=f*old_cell+i*candidate;h=o*np.tanh(c)
        cache.append((X[:,t],previous,old_cell,i,f,o,candidate,c,h))
    return h@p['Wo']+p['bo'],cache


def backward(p,cache,delta):
    g={k:np.zeros_like(v) for k,v in p.items()};g['Wo']=cache[-1][-1].T@delta;g['bo']=delta.sum(0)
    dh=delta@p['Wo'].T;dc=np.zeros_like(dh);dx=[]
    for x,previous,old_cell,i,f,o,candidate,c,h in reversed(cache):
        tanh_c=np.tanh(c);dc=dc+dh*o*(1-tanh_c**2)
        di=dc*candidate;df=dc*old_cell;do=dh*tanh_c;dg=dc*i
        dz=np.concatenate([di*i*(1-i),df*f*(1-f),do*o*(1-o),dg*(1-candidate**2)],axis=1)
        g['Wx']+=x.T@dz;g['Wh']+=previous.T@dz;g['b']+=dz.sum(0)
        dx.append(dz@p['Wx'].T);dh=dz@p['Wh'].T;dc=dc*f
    return g,np.stack(dx[::-1],axis=1)


def loss_gradients(p,X,y):
    output,cache=forward(p,X);loss,delta=support.mse(output,y);return loss,backward(p,cache,delta)[0]


class LSTMRegressor(support.Settings):
    @support.numerical
    def fit(self,X,y):
        self._settings();X=support.sequence(X,fitting=True);y=support.targets(y,len(X));rng=np.random.default_rng(self.random_state)
        p=initialize(X.shape[2],self.hidden_dim,rng)
        p,info=self._train(p,X,y,lambda p,x,t,r:loss_gradients(p,x,t),rng)
        self.__dict__.update(info,parameters_=p,input_shape_=X.shape[1:]);return self

    @support.numerical
    def predict(self,X):
        X=self._query(X,support.sequence);return forward(self.parameters_,X)[0]


if __name__=='__main__':support.main(LSTMRegressor,'sequence')
