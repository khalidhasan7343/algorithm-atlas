"""Tiny DDPM with explicit forward schedule, epsilon network, loss and posterior reverse sampling."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b7_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)

def schedule(n_steps,beta_start,beta_end):
    support.integer(n_steps,'n_steps',2,64);support.scalar(beta_start,'beta_start',1e-6,.5);support.scalar(beta_end,'beta_end',1e-6,.5)
    if beta_start>beta_end:raise ValueError('beta_start<=beta_end required')
    beta=np.linspace(beta_start,beta_end,n_steps);alpha=1-beta;bar=np.cumprod(alpha)
    previous=np.r_[1.,bar[:-1]];variance=beta*(1-previous)/(1-bar)
    return beta,alpha,bar,variance


def q_sample(X,t,noise,bar):
    t=np.asarray(t)
    if t.ndim!=1 or len(t)!=len(X) or t.dtype.kind not in 'iu' or np.any(t<0) or np.any(t>=len(bar)):
        raise ValueError('t must be valid nonnegative integer timestep vector')
    if noise.shape!=X.shape:raise ValueError('noise and clean shapes must match')
    return np.sqrt(bar[t])[:,None]*X+np.sqrt(1-bar[t])[:,None]*noise


def initialize(p,h,rng):
    return dict(W1=support.weight(rng,p+1,h),b1=np.zeros(h),W2=support.weight(rng,h,p),b2=np.zeros(p))


def predict_noise(p,X,t,n_steps):
    combined=np.column_stack([X,t/(n_steps-1)]);H=np.tanh(combined@p['W1']+p['b1'])
    return H@p['W2']+p['b2'],(combined,H)


def loss_gradients(p,noised,t,noise,n_steps):
    prediction,(combined,H)=predict_noise(p,noised,t,n_steps);loss,delta=support.mse(prediction,noise)
    dh=(delta@p['W2'].T)*(1-H**2)
    return loss,dict(W1=combined.T@dh,b1=dh.sum(0),W2=H.T@delta,b2=delta.sum(0))


def reverse_mean(X,t,predicted,beta,alpha,bar):
    support.integer(t,'t',0,len(beta)-1)
    if predicted.shape!=X.shape:raise ValueError('predicted noise shape mismatch')
    return (X-beta[t]/np.sqrt(1-bar[t])*predicted)/np.sqrt(alpha[t])


class DiffusionModel(support.Settings):
    def __init__(self,n_steps=8,beta_start=.05,beta_end=.2,**kwargs):
        self.n_steps,self.beta_start,self.beta_end=n_steps,beta_start,beta_end;super().__init__(**kwargs);schedule(n_steps,beta_start,beta_end)

    @support.numerical
    def fit(self,X):
        self._settings();beta,alpha,bar,variance=schedule(self.n_steps,self.beta_start,self.beta_end);X=support.tabular(X,fitting=True)
        A,mean,scale=support.normalize(X);rng=np.random.default_rng(self.random_state);p=initialize(X.shape[1],self.hidden_dim,rng)
        def objective(p,x,y,r):
            t=r.integers(self.n_steps,size=len(x));noise=r.normal(size=x.shape)
            return loss_gradients(p,q_sample(x,t,noise,bar),t,noise,self.n_steps)
        p,info=self._train(p,A,None,objective,rng)
        self.__dict__.update(info,parameters_=p,input_shape_=X.shape[1:],mean_=mean,scale_=scale,beta_=beta,alpha_=alpha,alpha_bar_=bar,posterior_variance_=variance,n_steps_=self.n_steps)
        return self

    @support.numerical
    def sample(self,n_samples,random_state=0):
        if not hasattr(self,'parameters_'):raise ValueError('fit required')
        support.integer(n_samples,'n_samples',1,128);support.integer(random_state,'random_state',0,2**32-1)
        rng=np.random.default_rng(random_state);X=rng.normal(size=(n_samples,self.input_shape_[0]))
        for t in range(self.n_steps_-1,-1,-1):
            predicted,_=predict_noise(self.parameters_,X,np.full(n_samples,t),self.n_steps_)
            X=reverse_mean(X,t,predicted,self.beta_,self.alpha_,self.alpha_bar_)
            if t>0:X+=np.sqrt(self.posterior_variance_[t])*rng.normal(size=X.shape)
        return X*self.scale_+self.mean_


if __name__=='__main__':support.main(DiffusionModel,'generative')
