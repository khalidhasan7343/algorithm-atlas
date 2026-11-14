"""Independent Phase26 B1 oracles (not using repository tests)."""
import importlib.util, sys
from pathlib import Path
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
ROOT=Path('.')
def load(path):
    spec=importlib.util.spec_from_file_location(path.replace('/','_').replace('-','_'),ROOT/path/'python/solution.py')
    m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m
B='machine-learning/supervised-learning/regression/'
checks=[]
def check(name,cond,detail=''):
    checks.append((name,bool(cond),detail)); print(('PASS ' if cond else 'FAIL ')+name, detail)
rng=np.random.default_rng(2026)
X=rng.normal(size=(40,4)); w=np.array([1.5,-2,0.5,0]); y=X@w+0.3+0.1*rng.normal(size=40); Q=rng.normal(size=(10,4))
# OLS: normal equations in long double
lr=load(B+'linear-regression').LinearRegression().fit(X,y)
A=np.column_stack((np.ones(40),X)).astype(np.longdouble); sol=np.linalg.solve((A.T@A).astype(float),(A.T@y.astype(np.longdouble)).astype(float))
check('OLS normal-equation agreement',np.allclose(lr.coef_,sol[1:],atol=1e-10) and abs(lr.intercept_-sol[0])<1e-10)
check('OLS residual orthogonality',np.allclose(X.T@(y-lr.predict(X)),0,atol=1e-10))
# Ridge: closed form on centered data, alpha convention = 1/2 RSS + alpha/2 ||w||^2  <=> sklearn Ridge(alpha)
for a in [0.3,5.0]:
    rr=load(B+'ridge-regression').RidgeRegression(alpha=a).fit(X,y)
    Xc=X-X.mean(0); yc=y-y.mean(); wr=np.linalg.solve(Xc.T@Xc+a*np.eye(4),Xc.T@yc)
    check(f'Ridge closed form alpha={a}',np.allclose(rr.coef_,wr,atol=1e-10) and np.allclose(rr.predict(Q),Ridge(alpha=a).fit(X,y).predict(Q),atol=1e-10))
# Lasso / ENet: compare objective to sklearn (same 1/(2n) convention) and check subgradient optimality independently
def enet_obj(w,b,l1,l2): r=X@w+b-y; return r@r/(2*len(y))+l1*np.abs(w).sum()+l2/2*w@w
for a in [0.05,0.5]:
    la=load(B+'lasso-regression').LassoRegression(alpha=a).fit(X,y); sk=Lasso(alpha=a,tol=1e-12,max_iter=100000).fit(X,y)
    check(f'Lasso objective <= sklearn+1e-10 alpha={a}',enet_obj(la.coef_,la.intercept_,a,0)<=enet_obj(sk.coef_,sk.intercept_,a,0)+1e-10,f'{enet_obj(la.coef_,la.intercept_,a,0):.12f} vs {enet_obj(sk.coef_,sk.intercept_,a,0):.12f}')
    g=X.T@(X@la.coef_+la.intercept_-y)/len(y)
    sub=all(abs(g[j]+a*np.sign(la.coef_[j]))<1e-6 if la.coef_[j]!=0 else abs(g[j])<=a+1e-6 for j in range(4))
    check(f'Lasso independent subgradient optimality alpha={a}',sub)
    en=load(B+'elastic-net').ElasticNetRegression(alpha=a,l1_ratio=0.3).fit(X,y); sk=ElasticNet(alpha=a,l1_ratio=0.3,tol=1e-12,max_iter=100000).fit(X,y)
    check(f'ENet objective <= sklearn+1e-10 alpha={a}',enet_obj(en.coef_,en.intercept_,a*0.3,a*0.7)<=enet_obj(sk.coef_,sk.intercept_,a*0.3,a*0.7)+1e-10)
# Polynomial: exact cubic recovery, independent expansion
pr=load(B+'polynomial-regression').PolynomialRegression(degree=3).fit(X[:,:2],y)
from sklearn.preprocessing import PolynomialFeatures
pf=PolynomialFeatures(3,include_bias=False).fit(X[:,:2])
# compare column sets regardless of order
mine=pr.transform(Q[:,:2]); ref=pf.transform(Q[:,:2])
check('Polynomial expansion matches sklearn column set',mine.shape==ref.shape and all(any(np.allclose(mine[:,i],ref[:,j]) for j in range(ref.shape[1])) for i in range(mine.shape[1])))
xx=rng.normal(size=(30,1)); yy=2*xx[:,0]**3-xx[:,0]+4
check('Polynomial exact cubic recovery',np.allclose(load(B+'polynomial-regression').PolynomialRegression(degree=3).fit(xx,yy).predict(xx),yy,atol=1e-9))
# Tree: exhaustive brute force depth-1 oracle on random data (distinct feature values)
Xt=rng.normal(size=(25,3)); yt=rng.normal(size=25)
tr=load(B+'decision-tree-regression').DecisionTreeRegression(max_depth=1).fit(Xt,yt)
best=None
for f in range(3):
    s=np.sort(Xt[:,f])
    for k in range(1,25):
        thr=(s[k-1]+s[k])/2; L=Xt[:,f]<=thr; sse=((yt[L]-yt[L].mean())**2).sum()+((yt[~L]-yt[~L].mean())**2).sum()
        if best is None or sse<best[0]-1e-12: best=(sse,f,thr)
check('Tree depth-1 brute-force split',tr.tree_.feature==best[1] and abs(tr.tree_.threshold-best[2])<1e-12, f'{tr.tree_.feature,tr.tree_.threshold} vs {best[1:]}')
skt=DecisionTreeRegressor(max_depth=4,random_state=0).fit(Xt,yt)
check('Tree depth-4 sklearn prediction agreement',np.allclose(tr.__class__(max_depth=4).fit(Xt,yt).predict(Xt),skt.predict(Xt),atol=1e-10))
# SVR: compare with libsvm at tight tol; verify independent KKT: for |beta_i|<C and beta_i!=0 -> residual = sign*eps
for kern in ['linear','rbf']:
    Xs=rng.normal(size=(30,2)); ys=np.sin(Xs[:,0])+0.1*Xs[:,1]
    svr=load(B+'support-vector-regression').SupportVectorRegression(C=2.0,epsilon=0.05,kernel=kern,gamma=0.5 if kern=='rbf' else None,tol=1e-9,max_iter=100000).fit(Xs,ys)
    ref=SVR(C=2.0,epsilon=0.05,kernel=kern,gamma=0.5 if kern=='rbf' else 'scale',tol=1e-10,shrinking=False).fit(Xs,ys) if kern=='rbf' else SVR(C=2.0,epsilon=0.05,kernel='linear',tol=1e-10,shrinking=False).fit(Xs,ys)
    check(f'SVR {kern} vs libsvm predictions',np.allclose(svr.predict(Xs),ref.predict(Xs),atol=5e-4),f'max diff {np.max(np.abs(svr.predict(Xs)-ref.predict(Xs))):.2e}; gap={svr.duality_gap_:.2e}')
    r=ys-svr.predict(Xs); b=svr.dual_coef_
    free=(np.abs(b)>1e-6)&(np.abs(b)<2.0-1e-6)
    check(f'SVR {kern} KKT: free SVs lie on tube boundary',np.allclose(np.abs(r[free]),0.05,atol=1e-5),f'{np.abs(r[free])[:5]}')
    check(f'SVR {kern} KKT: inside-tube points have beta=0',np.all(np.abs(b[np.abs(r)<0.05-1e-5])<1e-6))
    check(f'SVR {kern} sum beta = 0',abs(b.sum())<1e-8)
print('\nSUMMARY',sum(c[1] for c in checks),'/',len(checks),'passed')
