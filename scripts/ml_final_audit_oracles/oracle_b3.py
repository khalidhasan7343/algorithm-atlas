import importlib.util, sys
from pathlib import Path
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor as SkGBR, AdaBoostClassifier as SkAda
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
ROOT=Path('.')
def load(path):
    spec=importlib.util.spec_from_file_location(path.replace('/','_').replace('-','_'),ROOT/path/'python/solution.py')
    m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m
B='machine-learning/ensemble-methods/'
checks=[]
def check(name,cond,detail=''):
    checks.append((name,bool(cond),detail)); print(('PASS ' if cond else 'FAIL ')+name, detail)
rng=np.random.default_rng(303)
X=rng.normal(size=(40,3)); y=np.sin(X[:,0])+X[:,1]**2+0.1*rng.normal(size=40); yc=(X[:,0]+X[:,1]>0).astype(int)
# GBM vs sklearn squared error, same depth/lr; deterministic unique continuous splits
g=load(B+'gradient-boosting-machine').GradientBoostingRegressor(n_estimators=15,learning_rate=0.3,max_depth=2).fit(X,y)
sk=SkGBR(n_estimators=15,learning_rate=0.3,max_depth=2,random_state=0).fit(X,y)
check('GBM predictions vs sklearn',np.allclose(g.predict(X),sk.predict(X),atol=1e-10),f'{np.max(np.abs(g.predict(X)-sk.predict(X))):.1e}')
check('GBM train loss monotone nonincreasing',np.all(np.diff(g.train_loss_)<=1e-12))
# XGBoost: hand Newton check on a tiny dataset, lambda=0,gamma=0 depth1 lr1 equals one GBM stump
xg=load(B+'xgboost').XGBoostRegressor(n_estimators=1,learning_rate=1.0,max_depth=1,reg_lambda=0.0).fit(X,y)
gb=load(B+'gradient-boosting-machine').GradientBoostingRegressor(n_estimators=1,learning_rate=1.0,max_depth=1).fit(X,y)
check('XGBoost lambda=0 stump == GBM stump',np.allclose(xg.predict(X),gb.predict(X),atol=1e-12))
# hand: with lambda=2 the leaf is -G/(H+2) = sum(r)/(n+2) and gain formula
xg2=load(B+'xgboost').XGBoostRegressor(n_estimators=1,learning_rate=1.0,max_depth=1,reg_lambda=2.0).fit(X,y)
root=xg2.estimators_[0]; r=y-y.mean(); L=X[:,root.feature]<=root.threshold
check('XGBoost leaf values = sum(residual)/(n+lambda)',abs(root.left.value-r[L].sum()/(L.sum()+2))<1e-12 and abs(root.right.value-r[~L].sum()/((~L).sum()+2))<1e-12)
gain=0.5*(r[L].sum()**2/(L.sum()+2)+r[~L].sum()**2/((~L).sum()+2)-r.sum()**2/(40+2))
check('XGBoost gain formula',abs(root.gain-gain)<1e-10)
# brute force: this split is the max-gain split over all features/thresholds
best=-np.inf
for f in range(3):
    s=np.unique(X[:,f])
    for a,b in zip(s[:-1],s[1:]):
        m=X[:,f]<=(a+b)/2; gg=0.5*(r[m].sum()**2/(m.sum()+2)+r[~m].sum()**2/((~m).sum()+2)-r.sum()**2/42); best=max(best,gg)
check('XGBoost split is global max gain',abs(best-root.gain)<1e-10)
# AdaBoost SAMME vs sklearn with stumps (sklearn >=1.6 uses SAMME)
ad=load(B+'adaboost').AdaBoostClassifier(n_estimators=8,max_depth=1).fit(X,yc)
ska=SkAda(estimator=DecisionTreeClassifier(max_depth=1),n_estimators=8,random_state=0).fit(X,yc)
check('AdaBoost estimator weights & errors vs sklearn SAMME',np.allclose(ad.estimator_weights_,ska.estimator_weights_[:len(ad.estimator_weights_)],atol=1e-8) and np.allclose(ad.estimator_errors_,ska.estimator_errors_[:len(ad.estimator_errors_)],atol=1e-10),f'{ad.estimator_weights_[:3]} {ska.estimator_weights_[:3]}')
check('AdaBoost predictions vs sklearn',np.array_equal(ad.predict(X),ska.predict(X)))
# hand check of first round: alpha = log((1-e)/e)+log(K-1)
e=ad.estimator_errors_[0]; check('AdaBoost alpha_1 hand formula',abs(ad.estimator_weights_[0]-(np.log((1-e)/e)+np.log(1)))<1e-12)
# weight update hand check round 2
w1=ad.sample_weight_history_[1]; w0=ad.sample_weight_history_[0]; wrong=ad.estimators_[0].predict(X)!=yc
w_hand=w0*np.exp(ad.estimator_weights_[0]*wrong); w_hand/=w_hand.sum()
check('AdaBoost weight update hand formula',np.allclose(w1,w_hand,atol=1e-14))
# Bagging: each base tree equals sklearn tree fit on the recorded bootstrap sample (regression, no feature subsampling)
bg=load(B+'bagging').BaggingRegressor(n_estimators=4,max_depth=3).fit(X,y)
ok=True
for m,idx in zip(bg.estimators_,bg.estimators_samples_):
    ref=DecisionTreeRegressor(max_depth=3,random_state=0).fit(X[idx],y[idx])
    # sklearn breaks equal-gain ties by a random feature order; training SSE must agree exactly.
    ok&=abs(((m.predict(X[idx])-y[idx])**2).sum()-((ref.predict(X[idx])-y[idx])**2).sum())<1e-9
check('Bagging base trees reach the same optimal training SSE as sklearn trees on recorded bootstrap cohorts',ok)
check('Bagging prediction == mean of base predictions',np.allclose(bg.predict(X),np.mean([m.predict(X) for m in bg.estimators_],axis=0)))
bgo=load(B+'bagging').BaggingRegressor(n_estimators=6,max_depth=3,oob_score=True).fit(X,y)
# OOB hand: average base predictions over trees where row absent
oob=np.full(40,np.nan)
for i in range(40):
    preds=[m.predict(X[i:i+1])[0] for m,idx in zip(bgo.estimators_,bgo.estimators_samples_) if i not in idx]
    if preds: oob[i]=np.mean(preds)
check('Bagging OOB prediction hand computation',np.allclose(np.nan_to_num(oob,nan=-9),np.nan_to_num(bgo.oob_prediction_,nan=-9),atol=1e-12))
# Random forest: feature subsets of size sqrt(p) at each node
rf=load(B+'random-forest').RandomForestClassifier(n_estimators=5,max_features='sqrt').fit(X,yc)
def nodes(n):
    if n is None or n.feature is None: return []
    return [n]+nodes(n.left)+nodes(n.right)
all_nodes=[nd for m in rf.estimators_ for nd in nodes(m.tree_)]
check('RF every split uses feature from its sampled candidate subset of size sqrt(p)',all(len(nd.candidates)==1 and nd.feature in nd.candidates for nd in all_nodes) and len(all_nodes)>0)
# Stacking regression: OOF rows exclude own fold; verify OOF predictions equal refit on train folds via sklearn LinearRegression
st=load(B+'stacking').StackingRegressor(estimators=[lambda s: load(B.replace('ensemble-methods/','supervised-learning/regression/')+'linear-regression').LinearRegression()],n_splits=4).fit(X,y)
from sklearn.linear_model import LinearRegression as SkLin
ok=True
for held in st.fold_indices_:
    tr=np.setdiff1d(np.arange(40),held); ok&=np.allclose(st.oof_predictions_[held,0],SkLin().fit(X[tr],y[tr]).predict(X[held]),atol=1e-10)
check('Stacking OOF predictions reproduce fold-wise sklearn fits (no leakage)',ok)
# Voting hard: majority of base predictions
vt=load(B+'voting-classifiers').VotingClassifier(voting='hard').fit(X,yc)
votes=np.zeros((40,2))
for m in vt.estimators_: votes[np.arange(40),m.predict(X)]+=0.5
check('Voting hard == normalized vote counts',np.allclose(vt.predict_proba(X),votes))
# CatBoost: ordered target statistics hand check
cb=load(B+'catboost').CatBoostRegressor(categorical_features=(0,),n_estimators=2,max_depth=1).fit([['a',1.0],['b',2.0],['a',3.0],['a',4.0],['b',5.0]],[1.0,2,3,4,5])
raw=np.array(['a','b','a','a','b']); yy=np.array([1.0,2,3,4,5]); order=cb.permutation_
exp=np.empty(5); run={}
for i in order:
    c,m=run.get(raw[i],(0,0.0)); exp[i]=(m+cb.prior_weight_*cb.prior_)/(c+cb.prior_weight_); run[raw[i]]=(c+1,m+yy[i])
check('CatBoost ordered TS excludes own/future targets',np.allclose(cb.ordered_features_[:,0],exp))
print('\nSUMMARY',sum(c[1] for c in checks),'/',len(checks),'passed')
