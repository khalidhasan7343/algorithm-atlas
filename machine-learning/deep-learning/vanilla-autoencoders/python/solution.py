"""Canonical B5/B7 NumPy bottleneck autoencoder with explicit MSE backprop."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_support_path = Path(__file__).resolve().parents[3]/'unsupervised-learning/dimensionality-reduction/support.py'
_spec = importlib.util.spec_from_file_location('atlas_b5_support', _support_path)
support = sys.modules.get(_spec.name)
if support is None:
    support = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = support
    _spec.loader.exec_module(support)

def initialize_parameters(p,k,seed):
    rng=np.random.default_rng(seed);bound=np.sqrt(6/(p+k))
    return np.concatenate([rng.uniform(-bound,bound,(p,k)).ravel(),np.zeros(k),
                           rng.uniform(-bound,bound,(k,p)).ravel(),np.zeros(p)])


def unpack(theta,p,k):
    first=p*k;second=first+k;third=second+k*p
    return theta[:first].reshape(p,k),theta[first:second],theta[second:third].reshape(k,p),theta[third:]


def forward(theta,X,p,k,activation):
    W1,b1,W2,b2=unpack(theta,p,k)
    preactivation=X@W1+b1
    Z=np.tanh(preactivation) if activation=='tanh' else preactivation
    return Z,Z@W2+b2


def loss_gradient(theta,X,p,k,activation='tanh'):
    W1,b1,W2,b2=unpack(theta,p,k)
    Z,reconstruction=forward(theta,X,p,k,activation)
    residual=reconstruction-X;loss=float(np.mean(residual**2))
    delta=2*residual/X.size
    grad_W2=Z.T@delta;grad_b2=delta.sum(0)
    hidden=delta@W2.T
    if activation=='tanh':hidden*=1-Z*Z
    grad_W1=X.T@hidden;grad_b1=hidden.sum(0)
    return loss,np.concatenate([grad_W1.ravel(),grad_b1,grad_W2.ravel(),grad_b2])


class Autoencoder(support.Projection):
    def __init__(self,latent_dim=1,activation='tanh',max_iter=500,learning_rate=1.,tol=1e-6,random_state=0):
        self.latent_dim,self.activation,self.max_iter=latent_dim,activation,max_iter
        self.learning_rate,self.tol,self.random_state=learning_rate,tol,random_state
        self._parameters()

    def _parameters(self):
        support.integer(self.latent_dim,'latent_dim',1,31)
        if not isinstance(self.activation,str) or self.activation not in ('tanh','linear'):
            raise ValueError('activation must be tanh or linear')
        support.integer(self.max_iter,'max_iter',1,5000)
        support.scalar(self.learning_rate,'learning_rate',1e-6,100)
        support.scalar(self.tol,'tol',1e-12,1e-2)
        support.integer(self.random_state,'random_state',0,2**32-1)

    @support.numerical
    def fit(self,X,y=None):
        self._parameters();X=support.features(X,fitting=True)
        n,p=X.shape;k=self.latent_dim
        if n<2 or k>=p:raise ValueError('autoencoder requires n>=2 and 1<=latent_dim<p')
        A,mean=support.centered(X);scale=support.uniform_scale(A);A/=scale
        initial=initialize_parameters(p,k,self.random_state)
        theta,diagnostics=support.optimize(initial,lambda t:loss_gradient(t,A,p,k,self.activation),
            self.max_iter,self.learning_rate,self.tol)
        W1,b1,W2,b2=unpack(theta,p,k)
        self.__dict__.update(diagnostics,n_features_in_=p,mean_=mean,scale_=scale,
            parameters_=theta.copy(),encoder_weights_=W1.copy(),encoder_bias_=b1.copy(),
            decoder_weights_=W2.copy(),decoder_bias_=b2.copy(),activation_=self.activation,
            latent_dim_=k,reconstruction_loss_=diagnostics['objective_history_'][-1])
        return self

    @support.numerical
    def transform(self,X):
        A=(self._query(X)-self.mean_)/self.scale_
        preactivation=A@self.encoder_weights_+self.encoder_bias_
        return np.tanh(preactivation) if self.activation_=='tanh' else preactivation

    @support.numerical
    def inverse_transform(self,Z):
        self._query(np.empty((0,getattr(self,'n_features_in_',1))))
        Z=support.latent_features(Z,self.latent_dim_)
        return (Z@self.decoder_weights_+self.decoder_bias_)*self.scale_+self.mean_

    def reconstruct(self,X):return self.inverse_transform(self.transform(X))

if __name__ == '__main__':support.main(Autoencoder)
