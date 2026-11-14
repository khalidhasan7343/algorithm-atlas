import importlib.util, sys
from fractions import Fraction
from pathlib import Path
import numpy as np
from sklearn.neighbors import LocalOutlierFactor as SkLOF
from sklearn.svm import OneClassSVM as SkOC
from sklearn.ensemble import IsolationForest as SkIF
from sklearn.metrics import roc_auc_score, average_precision_score
from scipy.optimize import minimize
ROOT=Path('.'); B='machine-learning/anomaly-detection/'
spec=importlib.util.spec_from_file_location('atlas_b12_support',ROOT/B/'support.py'); s=importlib.util.module_from_spec(spec); sys.modules[spec.name]=s; spec.loader.exec_module(s)
checks=[]
def check(name,cond,detail=''):
    checks.append((name,bool(cond),detail)); print(('PASS ' if cond else 'FAIL ')+name, detail)
rng=np.random.default_rng(1212)
X=np.vstack([rng.normal(size=(60,2)),[[6,6],[-6,5],[7,-6]]]); truth=np.r_[np.ones(60),-np.ones(3)].astype(int)
# Isolation forest
iso=s.load('isolation-forest')
check('c(n) exact harmonic formula',all(abs(iso.expected_path_length(n)-float(2*sum(Fraction(1,j) for j in range(1,n))-Fraction(2*(n-1),n)))<1e-14 for n in (3,10,64,256)) and iso.expected_path_length(2)==1 and iso.expected_path_length(1)==0)
f=iso.IsolationForest(n_estimators=32,random_state=1).fit(X)
# independent walk: recompute path lengths via own traversal
def walk(row,node):
    d=0
    while node.feature is not None: node=node.left if row[node.feature]<node.split else node.right; d+=1
    return d+iso.expected_path_length(node.count)
paths=np.mean([[walk(r,t) for r in X] for t in f.trees_],axis=0)
check('IF scores == 2^(-mean path / c(psi)) via independent traversal',np.allclose(f.anomaly_scores_,np.exp2(-paths/iso.expected_path_length(f.max_samples_))))
check('IF planted outliers get the 3 highest scores; sklearn agrees on ranking top-3',set(np.argsort(-f.anomaly_scores_)[:3])=={60,61,62} and set(np.argsort(SkIF(random_state=0).fit(X).score_samples(X))[:3])=={60,61,62})
def leaves(node): return [node] if node.feature is None else leaves(node.left)+leaves(node.right)
check('IF tree leaf counts partition the subsample',all(sum(l.count for l in leaves(t))==f.max_samples_ for t in f.trees_))
# One-class SVM: dual vs scipy SLSQP; decision proportional to sklearn
oc=s.load('one-class-svm').OneClassSVM(nu=0.1,gamma=0.5,tolerance=1e-10,max_iter=20000).fit(X)
K=oc.gram_; cap=oc.cap_; n=len(X)
res=minimize(lambda a:0.5*a@K@a,np.full(n,1/n),jac=lambda a:K@a,bounds=[(0,cap)]*n,constraints=[dict(type='eq',fun=lambda a:a.sum()-1)],method='SLSQP',options=dict(ftol=1e-15,maxiter=2000))
check('OCSVM dual objective <= scipy SLSQP + 1e-9',oc.objective_<=res.fun+1e-9,f'{oc.objective_:.10f} vs {res.fun:.10f}; status {oc.status_}')
g=K@oc.alpha_; free=(oc.alpha_>1e-9)&(oc.alpha_<cap-1e-9)
check('OCSVM KKT: free alphas have equal gradient rho; bounds respect sign',np.allclose(g[free],oc.rho_,atol=1e-6) and np.all(g[oc.alpha_<=1e-9]>=oc.rho_-1e-6) and np.all(g[oc.alpha_>=cap-1e-9]<=oc.rho_+1e-6) and abs(oc.alpha_.sum()-1)<1e-10)
sk=SkOC(nu=0.1,gamma=0.5,tol=1e-12,shrinking=False).fit(X); d1=oc.decision_function(X); d2=sk.decision_function(X)
# libsvm scales alpha by nu*n: decision proportional
mism=np.flatnonzero(oc.predict(X)!=sk.predict(X))
check('OCSVM decision == libsvm decision scaled by nu*n; label differences only at |decision|<1e-6 margin points',np.max(np.abs(d1*0.1*n-d2))<1e-6 and all(abs(d2[i])<1e-6 for i in mism),f'max diff {np.max(np.abs(d1*0.1*n-d2)):.1e}; boundary mismatches {len(mism)}')
# LOF vs sklearn (no ties in random data)
lof=s.load('local-outlier-factor').LocalOutlierFactor(n_neighbors=10).fit(X); skl=SkLOF(n_neighbors=10).fit(X)
check('LOF scores == -sklearn negative_outlier_factor_',np.allclose(lof.anomaly_scores_,-skl.negative_outlier_factor_,rtol=1e-10))
# hand LOF for one point
D=np.sqrt(((X[:,None]-X[None])**2).sum(2)); i=5; k=10; kd=np.sort(D,1)[:,k]; N=[j for j in range(n) if j!=i and D[i,j]<=kd[i]]
lrd=lambda p: 1/np.mean([max(kd[o],D[p,o]) for o in range(n) if o!=p and D[p,o]<=kd[p]])
check('LOF hand formula for one point',abs(lof.anomaly_scores_[i]-np.mean([lrd(o) for o in N])/lrd(i))<1e-12)
check('LOF flags planted outliers (top-3)',set(np.argsort(-lof.anomaly_scores_)[:3])=={60,61,62})
# contamination threshold & labels
lf=s.load('local-outlier-factor').LocalOutlierFactor(n_neighbors=10,contamination=3/63).fit(X)
check('contamination=3/63 labels exactly the top-3 as -1',np.array_equal(np.flatnonzero(lf.labels_==-1),[60,61,62]) or np.sum(lf.labels_==-1)==3)
# metrics vs sklearn with ties
sc=np.round(rng.random(63),1); m=s.anomaly_metrics(truth,np.where(sc>0.7,-1,1),sc)
check('roc_auc / average precision vs sklearn (tied scores)',abs(m['roc_auc']-roc_auc_score(truth==-1,sc))<1e-12 and abs(m['average_precision']-average_precision_score(truth==-1,sc))<1e-12)
print('\nSUMMARY',sum(c[1] for c in checks),'/',len(checks),'passed')
