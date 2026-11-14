import importlib.util, sys
from pathlib import Path
import numpy as np
ROOT=Path('.'); B='machine-learning/deep-learning/'
sys.path.insert(0,str(ROOT))
def load(name):
    spec=importlib.util.spec_from_file_location('o7_'+name.replace('-','_'),ROOT/B/name/'python/solution.py')
    m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m
checks=[]
def check(name,cond,detail=''):
    checks.append((name,bool(cond),detail)); print(('PASS ' if cond else 'FAIL ')+name, detail)
rng=np.random.default_rng(77); h=1e-6
def fd_dict(f,p):
    g={}
    for k,v in p.items():
        g[k]=np.zeros_like(v)
        for idx in np.ndindex(v.shape):
            q=dict(p); vp=v.copy(); vp[idx]+=h; q[k]=vp; fp=f(q)
            vm=v.copy(); vm[idx]-=h; q[k]=vm; fm=f(q)
            g[k][idx]=(fp-fm)/(2*h)
    return g
def compare(name,analytic,numeric,tol=1e-6):
    worst=max(np.max(np.abs(analytic[k]-numeric[k])) for k in analytic); check(f'{name} finite-difference gradient',worst<tol,f'max |diff| {worst:.1e}')
# MLP
m=load('multilayer-perceptron'); X=rng.normal(size=(6,3)); y=rng.integers(0,2,size=(6,1)).astype(float); p=m.initialize(3,4,rng)
compare('MLP',m.loss_gradients(p,X,y)[1],fd_dict(lambda q:m.loss_gradients(q,X,y)[0],p))
# CNN
c=load('convolutional-neural-networks'); Xi=rng.normal(size=(4,2,5,5)); yi=rng.normal(size=(4,1))
for stride,pad in [(1,0),(2,1)]:
    p=c.initialize((2,5,5),2,3,stride,pad,rng); compare(f'CNN stride={stride} pad={pad}',c.loss_gradients(p,Xi,yi,stride,pad)[1],fd_dict(lambda q:c.loss_gradients(q,Xi,yi,stride,pad)[0],p))
# conv vs scipy correlate2d
from scipy.signal import correlate2d
p=c.initialize((2,5,5),2,3,1,0,rng); out,_=c.convolution(Xi,p['K'],p['b'],1,0)
ref=np.array([[sum(correlate2d(Xi[n,ch],p['K'][f,ch],mode='valid') for ch in range(2))+p['b'][f] for f in range(2)] for n in range(4)])
check('CNN cross-correlation == scipy.correlate2d',np.allclose(out,ref,atol=1e-12))
# RNN LSTM GRU
Xs=rng.normal(size=(5,4,3)); ys=rng.normal(size=(5,1))
for name in ['recurrent-neural-networks','long-short-term-memory','gated-recurrent-units']:
    mod=load(name); p=mod.initialize(3,4,rng); compare(name,mod.loss_gradients(p,Xs,ys)[1],fd_dict(lambda q:mod.loss_gradients(q,Xs,ys)[0],p))
# dx gradient for LSTM via backward (input adjoint)
mod=load('long-short-term-memory'); p=mod.initialize(3,4,rng); out,cache=mod.forward(p,Xs); loss,delta=__import__('importlib').import_module('o7_long_short_term_memory').support.mse(out,ys); _,dx=mod.backward(p,cache,delta)
fdx=np.zeros_like(Xs)
for idx in np.ndindex(Xs.shape):
    Xp=Xs.copy(); Xp[idx]+=h; Xm=Xs.copy(); Xm[idx]-=h; sup=mod.support
    fdx[idx]=(sup.mse(mod.forward(p,Xp)[0],ys)[0]-sup.mse(mod.forward(p,Xm)[0],ys)[0])/(2*h)
check('LSTM input adjoint dx finite difference',np.allclose(dx,fdx,atol=1e-6))
# Transformer
t=load('transformers'); p=t.initialize(3,4,5,rng)
for heads,causal in [(1,True),(2,False),(2,True)]:
    compare(f'Transformer heads={heads} causal={causal}',t.loss_gradients(p,Xs,ys,heads,causal)[1],fd_dict(lambda q:t.loss_gradients(q,Xs,ys,heads,causal)[0],p),tol=5e-6)
# causal mask: perturbing future inputs must not change earlier positions' attention output
E=rng.normal(size=(2,4,4)); out1,_=t.attention(E,E,E,2,True); E2=E.copy(); E2[:,3]+=1.0; out2,_=t.attention(E2,E2,E2,2,True)
check('Transformer causal attention: positions 0..2 unaffected by position 3',np.allclose(out1[:,:3],out2[:,:3]) and not np.allclose(out1[:,3],out2[:,3]))
# attention row-stochastic
_,(q,k,v,prob,mask)=t.attention(E,E,E,2,True); check('attention probabilities row-stochastic & masked zeros',np.allclose(prob.sum(-1),1) and np.all(prob[...,mask]==0))
# layer norm backward FD
g0,b0=rng.normal(size=4)+1,rng.normal(size=4); Z0=rng.normal(size=(2,3,4)); W=rng.normal(size=(2,3,4))
f=lambda Z,g,b: np.sum(W*t.layer_norm(Z,g,b)[0]); dz,dg,db=t.layer_norm_backward(W,t.layer_norm(Z0,g0,b0)[1])
fz=np.zeros_like(Z0)
for idx in np.ndindex(Z0.shape):
    Zp=Z0.copy();Zp[idx]+=h;Zm=Z0.copy();Zm[idx]-=h;fz[idx]=(f(Zp,g0,b0)-f(Zm,g0,b0))/(2*h)
fg=np.array([(f(Z0,g0+h*np.eye(4)[j],b0)-f(Z0,g0-h*np.eye(4)[j],b0))/(2*h) for j in range(4)])
check('LayerNorm backward finite difference (x, gamma, beta)',np.allclose(dz,fz,atol=1e-6) and np.allclose(dg,fg,atol=1e-6) and np.allclose(db,W.sum((0,1))))
# ResNet
r=load('residual-networks'); Xt=rng.normal(size=(6,3)); p=r.initialize(3,4,rng)
yr=rng.normal(size=(6,1)); compare('ResNet',r.loss_gradients(p,Xt,yr)[1],fd_dict(lambda q:r.loss_gradients(q,Xt,yr)[0],p))
# Vanilla AE (theta vector)
va=load('vanilla-autoencoders'); theta=va.initialize_parameters(3,2,0); L,G=va.loss_gradient(theta,Xt,3,2,'tanh')
fdv=np.array([(va.loss_gradient(theta+h*np.eye(len(theta))[i],Xt,3,2,'tanh')[0]-va.loss_gradient(theta-h*np.eye(len(theta))[i],Xt,3,2,'tanh')[0])/(2*h) for i in range(len(theta))])
check('Vanilla AE finite-difference gradient',np.allclose(G,fdv,atol=1e-6))
# Sparse AE (L1 away from kinks) and Denoising AE
sa=load('sparse-autoencoders'); L,G=sa.loss_gradients(theta,Xt,Xt,2,0.05)
fds=np.array([(sa.loss_gradients(theta+h*np.eye(len(theta))[i],Xt,Xt,2,0.05)[0]-sa.loss_gradients(theta-h*np.eye(len(theta))[i],Xt,Xt,2,0.05)[0])/(2*h) for i in range(len(theta))])
check('Sparse AE finite-difference gradient (L1 term away from kinks)',np.allclose(G,fds,atol=1e-6))
da=load('denoising-autoencoders'); Xn=Xt+0.1*rng.normal(size=Xt.shape); L,G=da.loss_gradients(theta,Xn,Xt,2)
fdd=np.array([(da.loss_gradients(theta+h*np.eye(len(theta))[i],Xn,Xt,2)[0]-da.loss_gradients(theta-h*np.eye(len(theta))[i],Xn,Xt,2)[0])/(2*h) for i in range(len(theta))])
check('Denoising AE finite-difference gradient (corrupted input, clean target)',np.allclose(G,fdd,atol=1e-6))
# VAE with fixed noise
ve=load('variational-autoencoders'); p=ve.initialize(3,2,rng); noise=rng.normal(size=(6,2))
compare('VAE (fixed reparameterization noise)',ve.loss_gradients(p,Xt,noise)[1],fd_dict(lambda q:ve.loss_gradients(q,Xt,noise)[0],p))
mu,lv=ve.encode(p,Xt); kl=0.5*np.sum(mu**2+np.exp(lv)-1-lv)/6; R=ve.forward(p,Xt,noise)[0]
check('VAE loss == 0.5||R-X||²/n + analytic Gaussian KL',abs(ve.loss_gradients(p,Xt,noise)[0]-(0.5*np.sum((R-Xt)**2)/6+kl))<1e-12)
# GAN
ga=load('generative-adversarial-networks'); p=ga.initialize(3,4,2,rng); Z=rng.normal(size=(6,2))
dl,dg=ga.discriminator_gradients(p,Xt,Z); fdg=fd_dict(lambda q:ga.discriminator_gradients(q,Xt,Z)[0],p)
check('GAN discriminator-parameter gradient FD (generator held fixed by design)',all(np.allclose(dg[k],fdg[k],atol=1e-6) for k in dg) and set(dg)=={'dW','db','dO','do'})
fake,_=ga.generator(p,Z); lr_,_=ga.discriminator(p,Xt); lf_,_=ga.discriminator(p,fake)
check('GAN discriminator loss == -mean log D(x) - mean log(1-D(G(z)))',abs(dl-(np.mean(np.log1p(np.exp(-lr_)))+np.mean(np.log1p(np.exp(lf_)))))<1e-12)
gl,gg=ga.generator_gradients(p,Z); fgg=fd_dict(lambda q:ga.generator_gradients(q,Z)[0],p)
check('GAN generator gradient FD (non-saturating loss)',all(np.allclose(gg[k],fgg[k],atol=1e-6) for k in gg))
# Diffusion
df=load('diffusion-models'); beta,alpha,bar,var=df.schedule(8,0.05,0.2)
check('DDPM schedule identities',np.allclose(bar,np.cumprod(1-beta)) and np.allclose(var[1:],beta[1:]*(1-bar[:-1])/(1-bar[1:])) and var[0]==0)
p=df.initialize(3,4,rng); tt=rng.integers(8,size=6); eps=rng.normal(size=(6,3)); xn=df.q_sample(Xt,tt,eps,bar)
check('DDPM q_sample marginal: mean sqrt(abar)x, std sqrt(1-abar)',np.allclose(xn,np.sqrt(bar[tt])[:,None]*Xt+np.sqrt(1-bar[tt])[:,None]*eps))
compare('DDPM epsilon-network',df.loss_gradients(p,xn,tt,eps,8)[1],fd_dict(lambda q:df.loss_gradients(q,xn,tt,eps,8)[0],p))
x0=rng.normal(size=(2,3)); predicted=rng.normal(size=(2,3)); tstep=3
check('DDPM reverse mean formula',np.allclose(df.reverse_mean(x0,tstep,predicted,beta,alpha,bar),(x0-beta[tstep]/np.sqrt(1-bar[tstep])*predicted)/np.sqrt(alpha[tstep])))
# GCN
gn=load('graph-neural-networks'); A=np.zeros((6,6)); 
for i,j in [(0,1),(1,2),(2,3),(3,4),(4,5),(0,5)]: A[i,j]=A[j,i]=1
Sn=gn.normalize_adjacency(A,6); Dh=np.diag(1/np.sqrt((A+np.eye(6)).sum(1)))
check('GCN normalized adjacency == D^-1/2 (A+I) D^-1/2',np.allclose(Sn,Dh@(A+np.eye(6))@Dh))
p=gn.initialize(3,4,rng); compare('GCN',gn.loss_gradients(p,Xt,yr,Sn)[1],fd_dict(lambda q:gn.loss_gradients(q,Xt,yr,Sn)[0],p))
# training determinism & no global RNG mutation
state=np.random.get_state()[1].copy(); m1=m.MLPClassifier(epochs=5).fit(X,y.ravel().astype(int)); m2=m.MLPClassifier(epochs=5).fit(X,y.ravel().astype(int))
check('MLP seeded training deterministic & global RNG untouched',all(np.array_equal(m1.parameters_[k],m2.parameters_[k]) for k in m1.parameters_) and np.array_equal(state,np.random.get_state()[1]))
print('\nSUMMARY',sum(c[1] for c in checks),'/',len(checks),'passed')
