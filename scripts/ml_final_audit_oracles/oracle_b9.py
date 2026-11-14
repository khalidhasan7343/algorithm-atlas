import importlib.util, sys
from pathlib import Path
import numpy as np
ROOT=Path('.'); B='machine-learning/graph-learning/'
spec=importlib.util.spec_from_file_location('atlas_b9_support',ROOT/B/'support.py'); sup=importlib.util.module_from_spec(spec); sys.modules[spec.name]=sup; spec.loader.exec_module(sup)
checks=[]
def check(name,cond,detail=''):
    checks.append((name,bool(cond),detail)); print(('PASS ' if cond else 'FAIL ')+name, detail)
rng=np.random.default_rng(99); h=1e-6
# PageRank: linear system oracle r = (1-d) (I - d P^T)^-1 v with dangling rows -> v
A=(rng.random((7,7))<0.35).astype(float)*rng.integers(1,4,(7,7)); A[3]=0  # dangling node 3
pr=sup.load('pagerank').PageRank(damping=0.85,tolerance=1e-13).fit(A)
deg=A.sum(1); P=np.where(deg[:,None]>0,A/np.where(deg[:,None]>0,deg[:,None],1),1/7)
r=np.linalg.solve(np.eye(7)-0.85*P.T,(1-0.85)*np.full(7,1/7)); r/=r.sum()
check('PageRank == exact linear-system stationary vector',np.allclose(pr.scores_,r,atol=1e-11) and abs(pr.scores_.sum()-1)<1e-12 and pr.converged_ and list(pr.dangling_nodes_)==[3],f'max diff {np.max(np.abs(pr.scores_-r)):.1e}')
# personalized
v=np.array([.5,.5,0,0,0,0,0]); prp=sup.load('pagerank').PageRank(damping=0.6,personalization=v,tolerance=1e-13).fit(A)
Pp=np.where(deg[:,None]>0,P,v); rp=np.linalg.solve(np.eye(7)-0.6*Pp.T,0.4*v); rp/=rp.sum()
check('Personalized PageRank == linear system with dangling -> v',np.allclose(prp.scores_,rp,atol=1e-11))
# 2-node hand: A=[[0,1],[1,0]] -> uniform 0.5
check('PageRank two-cycle hand = [0.5,0.5]',np.allclose(sup.load('pagerank').PageRank().fit([[0,1],[1,0]]).scores_,[.5,.5]))
# node2vec transition hand: path 0-1-2 plus 1-3, previous=0 current=1: to 0: 1/p, to 2: 1/q (not adjacent to 0), to 3: 1/q
nv=sup.load('node2vec'); G=np.zeros((4,4)); 
for i,j in [(0,1),(1,2),(1,3),(0,3)]: G[i,j]=G[j,i]=1
model=nv.Node2Vec(p=2.,q=0.5); probs=model.transition_probabilities(G,1,previous=0)
w=np.array([1/2,0,1/0.5,1.0]); w/=w.sum()  # node3 adjacent to prev 0 -> weight 1
check('node2vec 2nd-order transition biases (1/p return, 1 common, 1/q outward)',np.allclose(probs,w),f'{probs} vs {w}')
# SGNS loss hand + FD
U=rng.normal(size=(5,3)); V=rng.normal(size=(5,3)); pairs=np.array([[0,1],[2,3],[1,4],[0,2]]); neg=np.array([[3,4],[0,1],[2,2],[4,1]])
L,G_=nv.sgns_loss_gradients(U,V,pairs,neg)
hand=np.mean([np.log1p(np.exp(-U[c]@V[o]))+sum(np.log1p(np.exp(U[c]@V[k])) for k in neg[i]) for i,(c,o) in enumerate(pairs)])
check('SGNS loss hand formula',abs(L-hand)<1e-12)
fdU=np.zeros_like(U); fdV=np.zeros_like(V)
for idx in np.ndindex(U.shape):
    Up=U.copy();Up[idx]+=h;Um=U.copy();Um[idx]-=h;fdU[idx]=(nv.sgns_loss_gradients(Up,V,pairs,neg)[0]-nv.sgns_loss_gradients(Um,V,pairs,neg)[0])/(2*h)
    Vp=V.copy();Vp[idx]+=h;Vm=V.copy();Vm[idx]-=h;fdV[idx]=(nv.sgns_loss_gradients(U,Vp,pairs,neg)[0]-nv.sgns_loss_gradients(U,Vm,pairs,neg)[0])/(2*h)
check('SGNS gradients finite difference (with repeated negative indices)',np.allclose(G_['input'],fdU,atol=1e-7) and np.allclose(G_['output'],fdV,atol=1e-7))
# context pairs hand: walk [0,1,2,3], window 1 -> (0,1),(1,0),(1,2),(2,1),(2,3),(3,2)
cp=nv.context_pairs([[0,1,2,3]],1); check('context_pairs window=1 exact ordered pairs',sorted(map(tuple,cp.tolist()))==[(0,1),(1,0),(1,2),(2,1),(2,3),(3,2)])
fit=nv.Node2Vec(epochs=30,random_state=0).fit(G); check('node2vec training loss decreases on fixed sample',fit.loss_history_[-1]<fit.loss_history_[0])
# GCN: masked CE FD gradient and normalization
gc=sup.load('graph-convolutional-networks'); S=gc.normalize_adjacency(G,True); Dh=np.diag(1/np.sqrt((G+np.eye(4)).sum(1)))
check('GCN normalization == D^-1/2(A+I)D^-1/2 (reuses B7)',np.allclose(S,Dh@(G+np.eye(4))@Dh))
X=rng.normal(size=(4,3)); y=np.array([0,1,-1,1]); p=gc.initialize(3,4,2,0)
L,G_=gc.loss_gradients(p,X,S,y,None,0.1)
def fd(f,p):
    g={}
    for k,v in p.items():
        g[k]=np.zeros_like(v)
        for idx in np.ndindex(v.shape):
            q=dict(p);vp=v.copy();vp[idx]+=h;q[k]=vp;fp=f(q);vm=v.copy();vm[idx]-=h;q[k]=vm;fm=f(q);g[k][idx]=(fp-fm)/(2*h)
    return g
num=fd(lambda q:gc.loss_gradients(q,X,S,y,None,0.1)[0],p)
check('GCN masked cross-entropy + L2 gradient finite difference',max(np.max(np.abs(G_[k]-num[k])) for k in G_)<1e-7)
logits,_=gc.forward(p,X,S); pr_=np.exp(logits-logits.max(1,keepdims=True)); pr_/=pr_.sum(1,keepdims=True)
hand=-np.mean([np.log(pr_[i,y[i]]) for i in (0,1,3)])+0.05*(np.sum(p['W1']**2)+np.sum(p['W2']**2))
check('GCN masked CE loss hand (unknown label -1 excluded)',abs(L-hand)<1e-12)
# unselected known labels don't affect gradient
y2=y.copy(); y2[2]=0; mask=np.array([True,True,False,True]); L2,G2=gc.loss_gradients(p,X,S,y2,mask,0.1)
check('GCN train_mask excludes known-but-unselected labels',abs(L-L2)<1e-14 and all(np.allclose(G_[k],G2[k]) for k in G_))
clf=gc.GCNClassifier(epochs=100).fit(G,X,y); check('GCN classifier fits and predicts classes 0..C-1',set(clf.predict(G,X).tolist())<= {0,1} and clf.loss_history_[-1]<clf.loss_history_[0])
print('\nSUMMARY',sum(c[1] for c in checks),'/',len(checks),'passed')
