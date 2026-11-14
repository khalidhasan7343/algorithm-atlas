import importlib.util, sys
from pathlib import Path
import numpy as np
from sklearn.decomposition import PCA as SkPCA, FastICA as SkICA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as SkLDA
ROOT=Path('.')
def load(path):
    spec=importlib.util.spec_from_file_location(path.replace('/','_').replace('-','_'),ROOT/path/'python/solution.py')
    m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m
B='machine-learning/unsupervised-learning/dimensionality-reduction/'
checks=[]
def check(name,cond,detail=''):
    checks.append((name,bool(cond),detail)); print(('PASS ' if cond else 'FAIL ')+name, detail)
rng=np.random.default_rng(55)
X=rng.normal(size=(30,5))@rng.normal(size=(5,5))+rng.normal(size=5)*3
# SVD vs numpy
sv=load(B+'singular-value-decomposition').SVD().fit(X); U,s,Vt=np.linalg.svd(X,full_matrices=False)
check('SVD singular values vs numpy',np.allclose(sv.full_singular_values_,s,rtol=1e-12,atol=1e-12))
check('SVD reconstruction U S V^T == X',np.allclose(sv.left_singular_vectors_*sv.singular_values_@sv.components_,X,atol=1e-10))
check('SVD orthonormal U and V',np.allclose(sv.left_singular_vectors_.T@sv.left_singular_vectors_,np.eye(5),atol=1e-12) and np.allclose(sv.components_@sv.components_.T,np.eye(5),atol=1e-12))
# wide matrix and rank-deficient
Xw=rng.normal(size=(4,7)); svw=load(B+'singular-value-decomposition').SVD().fit(Xw)
check('SVD wide matrix reconstruction',np.allclose(svw.left_singular_vectors_*svw.singular_values_@svw.components_,Xw,atol=1e-10) and np.allclose(svw.full_singular_values_,np.linalg.svd(Xw,compute_uv=False)))
Xr=np.column_stack((X[:,0],X[:,0]*2,X[:,1])); svr=load(B+'singular-value-decomposition').SVD().fit(Xr)
check('SVD rank-deficient: zero singular value, orthonormal completed U',svr.full_singular_values_[-1]==0 and np.allclose(svr.left_singular_vectors_.T@svr.left_singular_vectors_,np.eye(3),atol=1e-10))
# PCA vs sklearn
pc=load(B+'principal-component-analysis').PCA(3).fit(X); sp=SkPCA(3).fit(X)
check('PCA explained variance & ratio vs sklearn',np.allclose(pc.explained_variance_,sp.explained_variance_,rtol=1e-10) and np.allclose(pc.explained_variance_ratio_,sp.explained_variance_ratio_,rtol=1e-10))
check('PCA components equal up to sign & projections equal up to sign',np.allclose(np.abs(pc.components_@sp.components_.T),np.eye(3),atol=1e-8) and np.allclose(np.abs(pc.transform(X)),np.abs(sp.transform(X)),atol=1e-8))
check('PCA inverse_transform of full rank recovers X',np.allclose(load(B+'principal-component-analysis').PCA(5).fit(X).inverse_transform(load(B+'principal-component-analysis').PCA(5).fit(X).transform(X)),X,atol=1e-9))
# LDA projection vs sklearn eigen solver directions (compare spans)
y=np.repeat([0,1,2],10); Xl=X.copy(); Xl[y==1]+=2; Xl[y==2,0]-=3
ld=load(B+'linear-discriminant-analysis-projection').LDAProjection(2).fit(Xl,y); sl=SkLDA(solver='eigen',n_components=2).fit(Xl,y)
# generalized eigenproblem Sb w = lambda Sw w independently
Sw=sum(((Xl[y==k]-Xl[y==k].mean(0)).T@(Xl[y==k]-Xl[y==k].mean(0))) for k in range(3)); mu=Xl.mean(0); Sb=sum(10*np.outer(Xl[y==k].mean(0)-mu,Xl[y==k].mean(0)-mu) for k in range(3))
from scipy.linalg import eigh
vals,vecs=eigh(Sb,Sw); W=vecs[:,::-1][:,:2]
def same_span(A,Bm): 
    Q1,_=np.linalg.qr(A); Q2,_=np.linalg.qr(Bm); return np.allclose(Q1@Q1.T,Q2@Q2.T,atol=1e-8)
check('LDA projection span == scipy generalized eigenvectors span',same_span(ld.components_.T,W))
check('LDA eigenvalues == generalized eigenvalues',np.allclose(ld.eigenvalues_,vals[::-1][:2],rtol=1e-8))
check('LDA projection directions proportional to sklearn eigen scalings',same_span(ld.components_.T,sl.scalings_[:,:2]))
# ICA: recover independent sources (sign/permutation)
t=np.linspace(0,8,200); Ssrc=np.column_stack((np.sin(2*t),np.sign(np.sin(3*t)),(t%1)*2-1)); A=np.array([[1,1,1],[0.5,2,1.0],[1.5,1.0,2.0]]); Xm=Ssrc@A.T
ic=load(B+'independent-component-analysis').FastICA(3,random_state=1).fit(Xm); Sest=ic.transform(Xm)
C=np.corrcoef(Sest.T,Ssrc.T)[:3,3:]; 
check('ICA recovers sources (|corr|>0.99 permutation)',np.allclose(np.sort(np.abs(C).max(1)),[1,1,1],atol=0.01),f'{np.abs(C).max(1)}')
check('ICA unmixed components are whitened (unit cov)',np.allclose(np.cov(Sest.T,bias=True),np.eye(3),atol=1e-6))
check('ICA inverse_transform recovers X',np.allclose(ic.inverse_transform(Sest),Xm,atol=1e-8))
# t-SNE: finite-difference gradient of KL; perplexity calibration
ts=load(B+'t-sne'); Xt=rng.normal(size=(12,3)); P,cond,betas=ts.joint_probabilities(Xt,4.0)
check('t-SNE conditional rows have perplexity 4',np.allclose([np.exp(-np.sum(r[r>0]*np.log(r[r>0]))) for r in cond],4.0,atol=1e-5))
check('t-SNE joint P symmetric, sums to 1',np.allclose(P,P.T) and abs(P.sum()-1)<1e-12 and np.all(np.diag(P)==0))
Y=rng.normal(size=(12,2)); L,G=ts.kl_gradient(Y,P); h=1e-6; fd=np.zeros_like(Y)
for i in range(12):
    for j in range(2):
        E=np.zeros_like(Y); E[i,j]=h; fd[i,j]=(ts.kl_gradient(Y+E,P)[0]-ts.kl_gradient(Y-E,P)[0])/(2*h)
check('t-SNE KL gradient finite difference',np.allclose(G,fd,atol=1e-6),f'max {np.max(np.abs(G-fd)):.1e}')
# hand KL: compare loss to explicit formula
D=((Y[:,None]-Y[None])**2).sum(2); num=1/(1+D); np.fill_diagonal(num,0); Q=num/num.sum(); m=P>0
check('t-SNE KL loss hand formula',abs(L-np.sum(P[m]*np.log(P[m]/Q[m])))<1e-12)
# UMAP: sigma calibration, symmetric graph, gradient FD
um=load(B+'umap'); g,st=um.fuzzy_graph(Xt,4)
check('UMAP sigma calibration: sum exp(-(d-rho)/sigma) = log2(k)',all(abs(np.exp(-np.maximum(st['knn_distances_'][i]-st['rho_'][i],0)/st['sigmas_'][i]).sum()-2.0)<1e-6 for i in range(12) if not st['saturated_rows_'][i]))
check('UMAP graph symmetric fuzzy union in [0,1]',np.allclose(g,g.T) and g.min()>=0 and g.max()<=1 and np.allclose(g,st['directed_memberships_']+st['directed_memberships_'].T-st['directed_memberships_']*st['directed_memberships_'].T))
L,G=um.cross_entropy_gradient(Y,g); fd=np.zeros_like(Y)
for i in range(12):
    for j in range(2):
        E=np.zeros_like(Y); E[i,j]=h; fd[i,j]=(um.cross_entropy_gradient(Y+E,g)[0]-um.cross_entropy_gradient(Y-E,g)[0])/(2*h)
check('UMAP cross-entropy gradient finite difference',np.allclose(G,fd,atol=1e-5,rtol=1e-5),f'max {np.max(np.abs(G-fd)):.1e}')
# optimize(): objective history nonincreasing for both
tsm=ts.TSNE(perplexity=4.0,max_iter=50).fit(Xt); umm=um.UMAP(n_neighbors=4,max_iter=50).fit(Xt)
check('t-SNE / UMAP Armijo descent histories nonincreasing',np.all(np.diff(tsm.objective_history_)<=1e-12) and np.all(np.diff(umm.objective_history_)<=1e-12) and tsm.optimization_status_ in ('budget-exhausted','gradient-tolerance'))
print('\nSUMMARY',sum(c[1] for c in checks),'/',len(checks),'passed')
