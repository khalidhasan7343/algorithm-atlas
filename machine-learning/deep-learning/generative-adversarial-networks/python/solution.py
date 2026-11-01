"""Non-saturating logistic GAN with separate generator/discriminator gradients and updates."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b7_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)

def initialize(p,h,z,rng):
    return dict(gW=support.weight(rng,z,h),gb=np.zeros(h),gO=support.weight(rng,h,p),go=np.zeros(p),
                dW=support.weight(rng,p,h),db=np.zeros(h),dO=support.weight(rng,h,1),do=np.zeros(1))


def generator(p,Z):
    H=np.tanh(Z@p['gW']+p['gb']);return H@p['gO']+p['go'],H


def discriminator(p,X):
    H=np.tanh(X@p['dW']+p['db']);return H@p['dO']+p['do'],H


def discriminator_gradients(p,real,Z):
    fake,_=generator(p,Z);lr,hr=discriminator(p,real);lf,hf=discriminator(p,fake)
    real_loss,dr=support.bce(lr,np.ones_like(lr));fake_loss,df=support.bce(lf,np.zeros_like(lf))
    ar=(dr@p['dO'].T)*(1-hr**2);af=(df@p['dO'].T)*(1-hf**2)
    return real_loss+fake_loss,dict(dW=real.T@ar+fake.T@af,db=ar.sum(0)+af.sum(0),dO=hr.T@dr+hf.T@df,do=dr.sum(0)+df.sum(0))


def generator_gradients(p,Z):
    fake,hg=generator(p,Z);logits,hd=discriminator(p,fake);loss,delta=support.bce(logits,np.ones_like(logits))
    d_fake=((delta@p['dO'].T)*(1-hd**2))@p['dW'].T
    d_hidden=(d_fake@p['gO'].T)*(1-hg**2)
    return loss,dict(gW=Z.T@d_hidden,gb=d_hidden.sum(0),gO=hg.T@d_fake,go=d_fake.sum(0))


class GAN(support.Settings):
    def __init__(self,latent_dim=2,**kwargs):
        self.latent_dim=latent_dim;super().__init__(**kwargs);support.integer(latent_dim,'latent_dim',1,8)

    @support.numerical
    def fit(self,X):
        self._settings();support.integer(self.latent_dim,'latent_dim',1,8);X=support.tabular(X,fitting=True)
        if 2*self.epochs*((len(X)+self.batch_size-1)//self.batch_size)>10000:raise ValueError('update budget exceeded')
        A,mean,scale=support.normalize(X);rng=np.random.default_rng(self.random_state);p=initialize(X.shape[1],self.hidden_dim,self.latent_dim,rng)
        dhistory=[];ghistory=[];largest=0.;updates=0
        for _ in range(self.epochs):
            order=rng.permutation(len(A));dtotal=gtotal=0.
            for start in range(0,len(A),self.batch_size):
                batch=A[order[start:start+self.batch_size]];Z=rng.normal(size=(len(batch),self.latent_dim))
                dl,dg=discriminator_gradients(p,batch,Z);p,dnorm=support.step(p,dg,self.learning_rate,self.gradient_clip)
                Z=rng.normal(size=(len(batch),self.latent_dim));gl,gg=generator_gradients(p,Z);p,gnorm=support.step(p,gg,self.learning_rate,self.gradient_clip)
                if not np.isfinite(dl+gl):raise ValueError('nonfinite adversarial objective')
                largest=max(largest,dnorm,gnorm);updates+=2;dtotal+=dl*len(batch);gtotal+=gl*len(batch)
            dhistory.append(dtotal/len(A));ghistory.append(gtotal/len(A))
        self.__dict__.update(parameters_=support.copy_parameters(p),input_shape_=X.shape[1:],mean_=mean,scale_=scale,latent_dim_=self.latent_dim,
            loss_history_=np.array(ghistory),discriminator_history_=np.array(dhistory),n_iter_=self.epochs,n_updates_=updates,max_gradient_norm_=largest,
            optimization_status_='fixed-budget-completed',converged_=False)
        return self

    @support.numerical
    def sample(self,n_samples,random_state=0):
        if not hasattr(self,'parameters_'):raise ValueError('fit required')
        support.integer(n_samples,'n_samples',1,128);support.integer(random_state,'random_state',0,2**32-1)
        Z=np.random.default_rng(random_state).normal(size=(n_samples,self.latent_dim_))
        return generator(self.parameters_,Z)[0]*self.scale_+self.mean_

    @support.numerical
    def discriminate(self,X):
        X=self._query(X);return support.sigmoid(discriminator(self.parameters_,(X-self.mean_)/self.scale_)[0]).ravel()


if __name__=='__main__':support.main(GAN,'generative')
