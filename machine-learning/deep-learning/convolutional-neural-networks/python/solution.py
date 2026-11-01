"""NCHW cross-correlation CNN with explicit kernel/input adjoints and tanh head."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b7_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)

def convolution(X,K,b,stride=1,padding=0):
    n,c,h,w=X.shape;f,channels,k,_=K.shape
    if channels!=c or K.shape[2]!=K.shape[3]:raise ValueError('kernel channel/square shape mismatch')
    oh=(h+2*padding-k)//stride+1;ow=(w+2*padding-k)//stride+1
    if min(oh,ow)<1:raise ValueError('kernel larger than padded image')
    padded=np.pad(X,((0,0),(0,0),(padding,padding),(padding,padding)))
    out=np.empty((n,f,oh,ow))
    for i in range(oh):
        for j in range(ow):
            patch=padded[:,:,i*stride:i*stride+k,j*stride:j*stride+k]
            out[:,:,i,j]=np.einsum('nckl,fckl->nf',patch,K)+b
    return out,(padded,K,stride,padding,X.shape)


def convolution_backward(delta,cache):
    padded,K,stride,padding,shape=cache;k=K.shape[2]
    dx=np.zeros_like(padded);dK=np.zeros_like(K);db=delta.sum(axis=(0,2,3))
    for i in range(delta.shape[2]):
        for j in range(delta.shape[3]):
            patch=padded[:,:,i*stride:i*stride+k,j*stride:j*stride+k]
            dK+=np.einsum('nf,nckl->fckl',delta[:,:,i,j],patch)
            dx[:,:,i*stride:i*stride+k,j*stride:j*stride+k]+=np.einsum('nf,fckl->nckl',delta[:,:,i,j],K)
    return dx[:,:,padding:padding+shape[2],padding:padding+shape[3]],dK,db


def initialize(shape,filters,kernel,stride,padding,rng):
    c,h,w=shape;oh=(h+2*padding-kernel)//stride+1;ow=(w+2*padding-kernel)//stride+1
    if min(oh,ow)<1:raise ValueError('invalid convolution output dimensions')
    return dict(K=rng.normal(0,1/np.sqrt(c*kernel**2),(filters,c,kernel,kernel)),b=np.zeros(filters),
                W=support.weight(rng,filters*oh*ow,1),o=np.zeros(1))


def forward(p,X,stride=1,padding=0):
    C,cache=convolution(X,p['K'],p['b'],stride,padding);A=np.tanh(C)
    flat=A.reshape(len(X),p['W'].shape[0]);return flat@p['W']+p['o'],(A,flat,cache)


def loss_gradients(p,X,y,stride=1,padding=0):
    output,(A,flat,cache)=forward(p,X,stride,padding);loss,delta=support.mse(output,y)
    dA=(delta@p['W'].T).reshape(A.shape)*(1-A**2)
    _,dK,db=convolution_backward(dA,cache)
    return loss,dict(K=dK,b=db,W=flat.T@delta,o=delta.sum(0))


class CNNRegressor(support.Settings):
    def __init__(self,filters=2,kernel_size=2,stride=1,padding=0,**kwargs):
        if "hidden_dim" in kwargs:raise ValueError("CNN uses filters; hidden_dim unsupported")
        self.filters,self.kernel_size,self.stride,self.padding=filters,kernel_size,stride,padding
        super().__init__(**kwargs);self._architecture()

    def _architecture(self):
        support.integer(self.filters,'filters',1,4);support.integer(self.kernel_size,'kernel_size',1,3)
        support.integer(self.stride,'stride',1,2);support.integer(self.padding,'padding',0,1)

    @support.numerical
    def fit(self,X,y):
        self._settings();self._architecture();X=support.images(X,fitting=True);y=support.targets(y,len(X))
        rng=np.random.default_rng(self.random_state);p=initialize(X.shape[1:],self.filters,self.kernel_size,self.stride,self.padding,rng)
        p,info=self._train(p,X,y,lambda p,x,t,r:loss_gradients(p,x,t,self.stride,self.padding),rng)
        self.__dict__.update(info,parameters_=p,input_shape_=X.shape[1:],stride_=self.stride,padding_=self.padding)
        return self

    @support.numerical
    def predict(self,X):
        X=self._query(X,support.images);return forward(self.parameters_,X,self.stride_,self.padding_)[0]


if __name__=='__main__':support.main(CNNRegressor,'cnn')
