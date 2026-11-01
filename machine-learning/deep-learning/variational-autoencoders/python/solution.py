"""Linear-Gaussian VAE: bounded smooth log variance, reparameterization, KL and explicit gradients."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b7_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)

def initialize(p,k,rng):
    return dict(Wmu=support.weight(rng,p,k),bmu=np.zeros(k),Wvar=support.weight(rng,p,k)*.05,bvar=np.zeros(k),Wd=support.weight(rng,k,p),bd=np.zeros(p))


def encode(p,X):
    mu=X@p['Wmu']+p['bmu'];raw=X@p['Wvar']+p['bvar'];return mu,5*np.tanh(raw)


def forward(p,X,noise):
    mu,logvar=encode(p,X);std=np.exp(.5*logvar);Z=mu+std*noise
    return Z@p['Wd']+p['bd'],(mu,logvar,std,Z,noise)


def loss_gradients(p,X,noise):
    R,(mu,logvar,std,Z,noise)=forward(p,X,noise);n=len(X);residual=R-X
    reconstruction=.5*np.sum(residual**2)/n
    kl=.5*np.sum(mu**2+np.exp(logvar)-1-logvar)/n
    dR=residual/n;dZ=dR@p['Wd'].T;dmu=dZ+mu/n
    dlogvar=.5*dZ*std*noise+.5*(np.exp(logvar)-1)/n
    draw=dlogvar*5*(1-(logvar/5)**2)
    return float(reconstruction+kl),dict(Wd=Z.T@dR,bd=dR.sum(0),Wmu=X.T@dmu,bmu=dmu.sum(0),Wvar=X.T@draw,bvar=draw.sum(0))


class VariationalAutoencoder(support.Settings):
    def __init__(self,latent_dim=1,**kwargs):
        self.latent_dim=latent_dim;super().__init__(hidden_dim=latent_dim,**kwargs)

    @support.numerical
    def fit(self,X):
        self._settings();support.integer(self.latent_dim,'latent_dim',1,15);X=support.tabular(X,fitting=True)
        if self.latent_dim>=X.shape[1]:raise ValueError('latent_dim must be smaller than p')
        A,mean,scale=support.normalize(X);rng=np.random.default_rng(self.random_state);p=initialize(X.shape[1],self.latent_dim,rng)
        p,info=self._train(p,A,None,lambda p,x,y,r:loss_gradients(p,x,r.normal(size=(len(x),self.latent_dim))),rng)
        self.__dict__.update(info,parameters_=p,input_shape_=X.shape[1:],mean_=mean,scale_=scale,latent_dim_=self.latent_dim);return self

    @support.numerical
    def encode(self,X):
        X=self._query(X);return encode(self.parameters_,(X-self.mean_)/self.scale_)

    def transform(self,X):return self.encode(X)[0]

    @support.numerical
    def inverse_transform(self,Z):
        if not hasattr(self,'parameters_'):raise ValueError('fit required')
        Z=support.latent(Z,self.latent_dim_)
        return (Z@self.parameters_['Wd']+self.parameters_['bd'])*self.scale_+self.mean_

    def reconstruct(self,X):return self.inverse_transform(self.transform(X))

    @support.numerical
    def sample(self,n_samples,random_state=0):
        if not hasattr(self,'parameters_'):raise ValueError('fit required')
        support.integer(n_samples,'n_samples',1,128);support.integer(random_state,'random_state',0,2**32-1)
        rng=np.random.default_rng(random_state);Z=rng.normal(size=(n_samples,self.latent_dim_))
        R=Z@self.parameters_['Wd']+self.parameters_['bd']+rng.normal(size=(n_samples,self.input_shape_[0]))
        return R*self.scale_+self.mean_


if __name__=='__main__':support.main(VariationalAutoencoder,'vae')
