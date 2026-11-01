"""Gaussian-corruption denoising autoencoder: explicit modified objective/backprop; one shared vanilla canonical."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b7_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)

vanilla=support.load('vanilla-autoencoders')


def corrupt(X,noise_std,rng):
    support.scalar(noise_std,'noise_std',0,1)
    return X+rng.normal(0,noise_std,X.shape)


def loss_gradients(theta,X,target,k):
    p=X.shape[1];W1,b1,W2,b2=vanilla.unpack(theta,p,k)
    Z,R=vanilla.forward(theta,X,p,k,'tanh');loss,delta=support.mse(R,target)
    hidden_delta=(delta@W2.T)*(1-Z**2)
    gradient=np.concatenate([(X.T@hidden_delta).ravel(),hidden_delta.sum(0),(Z.T@delta).ravel(),delta.sum(0)])
    return loss,gradient


class DenoisingAutoencoder(support.Settings):
    def __init__(self,latent_dim=1,noise_std=.1,**kwargs):
        self.latent_dim,self.noise_std=latent_dim,noise_std
        super().__init__(hidden_dim=latent_dim,**kwargs);self._architecture()

    def _architecture(self):
        support.integer(self.latent_dim,'latent_dim',1,15);support.scalar(self.noise_std,'noise_std',0,1)

    @support.numerical
    def fit(self,X):
        self._settings();self._architecture();X=support.tabular(X,fitting=True);k=self.latent_dim
        if k>=X.shape[1]:raise ValueError('strict bottleneck requires latent_dim<p')
        A,mean,scale=support.normalize(X);rng=np.random.default_rng(self.random_state)
        parameters={'theta':vanilla.initialize_parameters(X.shape[1],k,self.random_state)}
        def objective(p,x,target,rng):
            x=corrupt(x,self.noise_std,rng)
            loss,g=loss_gradients(p['theta'],x,target,k)
            return loss,{'theta':g}
        parameters,info=self._train(parameters,A,A,objective,rng)
        self.__dict__.update(info,parameters_=parameters,input_shape_=X.shape[1:],mean_=mean,scale_=scale,latent_dim_=k)
        return self

    @support.numerical
    def transform(self,X):
        X=self._query(X);A=(X-self.mean_)/self.scale_
        return vanilla.forward(self.parameters_['theta'],A,X.shape[1],self.latent_dim_,'tanh')[0]

    @support.numerical
    def inverse_transform(self,Z):
        if not hasattr(self,'parameters_'):raise ValueError('fit required')
        Z=support.array(Z,shape=(self.latent_dim_,));_,_,W2,b2=vanilla.unpack(self.parameters_['theta'],self.input_shape_[0],self.latent_dim_)
        return (Z@W2+b2)*self.scale_+self.mean_

    def reconstruct(self,X):return self.inverse_transform(self.transform(X))


if __name__=='__main__':support.main(DenoisingAutoencoder,'ae')
