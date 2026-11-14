import importlib.util, sys
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression as SkLR
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as SkLDA, QuadraticDiscriminantAnalysis as SkQDA
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
ROOT=Path('.')
def load(path):
    spec=importlib.util.spec_from_file_location(path.replace('/','_').replace('-','_'),ROOT/path/'python/solution.py')
    m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m
B='machine-learning/supervised-learning/classification/'
checks=[]
def check(name,cond,detail=''):
    checks.append((name,bool(cond),detail)); print(('PASS ' if cond else 'FAIL ')+name, detail)
rng=np.random.default_rng(26)
X=rng.normal(size=(60,3)); yb=(X@[1,-1,0.5]+0.2*rng.normal(size=60)>0).astype(int); Q=rng.normal(size=(15,3))
ym=rng.integers(0,3,size=60); X[ym==1]+=1.5; X[ym==2]-=1.5
# Logistic: alpha = 1/(n C); compare to sklearn lbfgs tight tol; also independent gradient at optimum
alpha=0.1; lr=load(B+'logistic-regression').LogisticRegression(alpha=alpha,tol=1e-10).fit(X,yb)
sk=SkLR(C=1/(60*alpha),tol=1e-12,max_iter=10000).fit(X,yb)
check('Logistic coef vs sklearn (C=1/(n*alpha))',np.allclose(lr.coef_,sk.coef_[0],atol=1e-5) and abs(lr.intercept_-sk.intercept_[0])<1e-5,f'{lr.coef_} {sk.coef_[0]}')
p=1/(1+np.exp(-(X@lr.coef_+lr.intercept_))); g=X.T@(p-yb)/60+alpha*lr.coef_
check('Logistic independent gradient ~0',np.max(np.abs(g))<1e-8 and abs((p-yb).mean())<1e-8)
h=1e-6; f=lambda w,b: np.mean(np.log1p(np.exp(-(2*yb-1)*(X@w+b))))+alpha/2*w@w
w0=rng.normal(size=3); b0=0.3; L,gw,gb=load(B+'logistic-regression').loss_gradient(X,yb,w0,b0,alpha)
fd=[(f(w0+h*np.eye(3)[j],b0)-f(w0-h*np.eye(3)[j],b0))/(2*h) for j in range(3)]
check('Logistic finite-difference gradient',np.allclose(gw,fd,atol=1e-6) and abs(gb-(f(w0,b0+h)-f(w0,b0-h))/(2*h))<1e-6)
# GNB: epsilon = smoothing*max(1,max var); data var>1 so equals sklearn
Xg=X*2
gnb=load(B+'gaussian-naive-bayes').GaussianNaiveBayes().fit(Xg,ym); skg=GaussianNB().fit(Xg,ym)
check('GaussianNB predict_proba vs sklearn',np.allclose(gnb.predict_proba(Q*2),skg.predict_proba(Q*2),atol=1e-9) and np.array_equal(gnb.predict(Q*2),skg.predict(Q*2)))
# hand-computed GNB log density
k=0; x=Q[0]*2; ll=np.log(gnb.class_prior_[k])+sum(-0.5*np.log(2*np.pi*gnb.var_[k][j])-0.5*(x[j]-gnb.theta_[k][j])**2/gnb.var_[k][j] for j in range(3))
check('GaussianNB hand joint log-likelihood',abs(gnb.decision_function(Q[:1]*2)[0,0]-ll)<1e-10)
# MNB / BNB
Xc=rng.integers(0,5,size=(60,4)).astype(float)
mnb=load(B+'multinomial-naive-bayes').MultinomialNaiveBayes(alpha=0.7).fit(Xc,ym); skm=MultinomialNB(alpha=0.7).fit(Xc,ym)
check('MultinomialNB log probs vs sklearn',np.allclose(mnb.feature_log_prob_,skm.feature_log_prob_,atol=1e-12) and np.allclose(mnb.predict_proba(Xc[:10]),skm.predict_proba(Xc[:10]),atol=1e-10))
bnb=load(B+'bernoulli-naive-bayes').BernoulliNaiveBayes(alpha=0.5,binarize=1.0).fit(Xc,ym); skb=BernoulliNB(alpha=0.5,binarize=1.0).fit(Xc,ym)
check('BernoulliNB vs sklearn',np.allclose(bnb.predict_proba(Xc[:10]),skb.predict_proba(Xc[:10]),atol=1e-10))
# KNN vs sklearn brute (random data has no ties)
knn=load(B+'k-nearest-neighbors').KNearestNeighbors(n_neighbors=5).fit(X,ym); skk=KNeighborsClassifier(5,algorithm='brute').fit(X,ym)
d,i=knn.kneighbors(Q); d2,i2=skk.kneighbors(Q)
check('KNN neighbors & distances vs sklearn',np.array_equal(i,i2) and np.allclose(d,d2) and np.allclose(knn.predict_proba(Q),skk.predict_proba(Q)))
# LDA: compare with sklearn lsqr solver (same pooled prior-weighted covariance) with reg -> tiny
lda=load(B+'linear-discriminant-analysis').LinearDiscriminantAnalysis(reg=0.0).fit(X,ym); skl=SkLDA(solver='lsqr').fit(X,ym)
check('LDA predict_proba vs sklearn(lsqr)',np.allclose(lda.predict_proba(Q),skl.predict_proba(Q),atol=1e-8))
# hand: pooled covariance
Sw=sum((np.mean(ym==k))*np.cov(X[ym==k].T,bias=True) for k in range(3))
check('LDA pooled covariance matches hand formula',np.allclose(lda.covariance_,Sw,atol=1e-12))
qda=load(B+'quadratic-discriminant-analysis').QuadraticDiscriminantAnalysis(reg_param=0.1).fit(X,ym); skq=SkQDA(reg_param=0.1).fit(X,ym)
check('QDA predict_proba vs sklearn',np.allclose(qda.predict_proba(Q),skq.predict_proba(Q),atol=1e-8))
# SVM linear vs libsvm
svm=load(B+'support-vector-machines').SupportVectorMachine(C=0.5,tol=1e-9,max_iter=100000).fit(X,yb); sks=SVC(C=0.5,kernel='linear',tol=1e-12,shrinking=False).fit(X,yb)
check('SVM linear coef/intercept vs libsvm',np.allclose(svm.coef_,sks.coef_[0],atol=1e-4) and abs(svm.intercept_-sks.intercept_[0])<1e-3,f'{svm.coef_} {sks.coef_[0]} gap={svm.duality_gap_:.1e}')
# independent primal objective check: svm primal <= libsvm primal + tol
prim=lambda w,b: 0.5*w@w+0.5*np.maximum(0,1-(2*yb-1)*(X@w+b)).sum()
check('SVM primal objective <= libsvm primal + 1e-6',prim(svm.coef_,svm.intercept_)<=prim(sks.coef_[0],sks.intercept_[0])+1e-6,f'{prim(svm.coef_,svm.intercept_):.9f} vs {prim(sks.coef_[0],sks.intercept_[0]):.9f}')
# CART vs sklearn
cart=load(B+'cart-decision-trees').CARTClassifier(max_depth=3).fit(X,ym); skc=DecisionTreeClassifier(max_depth=3,random_state=0).fit(X,ym)
check('CART depth-3 proba vs sklearn',np.allclose(cart.predict_proba(Q),skc.predict_proba(Q),atol=1e-12))
# ID3 on the classic Quinlan weather dataset: root must be Outlook (gain 0.247), leaves Overcast pure
outlook=[0,0,1,2,2,2,1,0,0,2,0,1,1,2]; temp=[0,0,0,1,2,2,2,1,2,1,1,1,0,1]; hum=[0,0,0,0,1,1,1,0,1,1,1,0,1,0]; wind=[0,1,0,0,0,1,1,0,0,0,1,1,0,1]
play=['N','N','Y','Y','Y','N','Y','N','Y','Y','Y','Y','Y','N']
W=np.array([outlook,temp,hum,wind],dtype=float).T
id3=load(B+'id3-decision-trees').ID3Classifier().fit(W,play)
check('ID3 weather root=Outlook gain 0.2467',id3.tree_.feature==0 and abs(id3.tree_.gain-0.24675)<1e-4,f'{id3.tree_.feature} {id3.tree_.gain:.5f}')
check('ID3 weather training accuracy 1',id3.score(W,play)==1.0)
c45=load(B+'c4-5-decision-trees').C45Classifier(categorical_features=[0,1,2,3]).fit(W,play)
# gain ratios: outlook .247/1.577=.156, hum .152/1=.152, wind .048/.985=.049, temp .029/1.557=.019 -> outlook
check('C4.5 weather categorical root=Outlook ratio 0.156',c45.tree_.feature==0 and abs(c45.tree_.gain_ratio-0.1564)<1e-3,f'{c45.tree_.feature} {c45.tree_.gain_ratio:.4f}')
# metrics vs sklearn
from sklearn.metrics import precision_recall_fscore_support, log_loss as skll
mm=importlib.util.spec_from_file_location('m',ROOT/B/'metrics.py'); mod=importlib.util.module_from_spec(mm); mm.loader.exec_module(mod)
rep=mod.classification_report(ym,cart.predict(X)); p_,r_,f_,s_=precision_recall_fscore_support(ym,cart.predict(X),zero_division=0)
check('classification_report vs sklearn',np.allclose([c['precision'] for c in rep['per_class']],p_) and np.allclose([c['f1'] for c in rep['per_class']],f_) and np.allclose(rep['macro']['f1'],f_.mean()))
check('log_loss vs sklearn',abs(mod.log_loss(ym,gnb.predict_proba(Xg),[0,1,2])-skll(ym,gnb.predict_proba(Xg),labels=[0,1,2]))<1e-9)
print('\nSUMMARY',sum(c[1] for c in checks),'/',len(checks),'passed')
