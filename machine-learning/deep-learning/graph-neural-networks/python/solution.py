"""Two-layer undirected normalized GCN message passing with full-graph analytic gradients."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b7_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)

def normalize_adjacency(adjacency,n,self_loops=True):
    support.boolean(self_loops,'self_loops')
    A=support.array(adjacency)
    if not 1<=n<=32 or A.shape!=(n,n) or np.any(A<0):raise ValueError('nonnegative square adjacency for<=32 nodes required')
    if not np.allclose(A,A.T,atol=1e-12,rtol=0):raise ValueError('undirected symmetric adjacency required')
    if np.any(np.diag(A)!=0):raise ValueError('input diagonal must be zero; self_loops controls added identity')
    A=(A+A.T)/2
    if self_loops:A+=np.eye(n)
    degrees=A.sum(1);inverse=np.zeros(n);positive=degrees>0;inverse[positive]=1/np.sqrt(degrees[positive])
    return inverse[:,None]*A*inverse[None,:]


def initialize(p,h,rng):
    return dict(W1=support.weight(rng,p,h),b1=np.zeros(h),W2=support.weight(rng,h,1),b2=np.zeros(1))


def forward(p,X,S):
    aggregated=S@X;H=np.tanh(aggregated@p['W1']+p['b1']);messages=S@H
    return messages@p['W2']+p['b2'],(aggregated,H,messages)


def loss_gradients(p,X,y,S):
    output,(aggregated,H,messages)=forward(p,X,S);loss,delta=support.mse(output,y)
    dH=(S.T@delta@p['W2'].T)*(1-H**2)
    return loss,dict(W1=aggregated.T@dH,b1=dH.sum(0),W2=messages.T@delta,b2=delta.sum(0))


class GCNRegressor:
    def __init__(self,hidden_dim=4,epochs=100,learning_rate=.1,random_state=0,gradient_clip=5.,self_loops=True):
        self.hidden_dim,self.epochs,self.learning_rate=hidden_dim,epochs,learning_rate
        self.random_state,self.gradient_clip,self.self_loops=random_state,gradient_clip,self_loops
        self._settings()

    def _settings(self):
        support.integer(self.hidden_dim,'hidden_dim',1,16);support.boolean(self.self_loops,'self_loops')
        support.options(self.epochs,self.learning_rate,1,self.random_state,self.gradient_clip)

    @support.numerical
    def fit(self,X,y,adjacency):
        self._settings();X=support.tabular(X,fitting=True);y=support.targets(y,len(X));S=normalize_adjacency(adjacency,len(X),self.self_loops)
        rng=np.random.default_rng(self.random_state);p=initialize(X.shape[1],self.hidden_dim,rng)
        p,info=support.train(p,X,y,lambda p,x,t,r:loss_gradients(p,x,t,S),epochs=self.epochs,learning_rate=self.learning_rate,batch_size=len(X),rng=rng,gradient_clip=self.gradient_clip,shuffle=False)
        self.__dict__.update(info,parameters_=p,input_shape_=X.shape[1:],self_loops_=self.self_loops,normalized_adjacency_=S,batch_size_=len(X));return self

    @support.numerical
    def predict(self,X,adjacency):
        if not hasattr(self,'parameters_'):raise ValueError('fit required')
        X=support.tabular(X,shape=self.input_shape_);S=normalize_adjacency(adjacency,len(X),self.self_loops_)
        return forward(self.parameters_,X,S)[0]


if __name__=='__main__':support.main(GCNRegressor,'gnn')
