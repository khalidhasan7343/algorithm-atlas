import importlib.util, sys, itertools
from pathlib import Path
import numpy as np
ROOT=Path('.'); B='machine-learning/time-series/'
spec=importlib.util.spec_from_file_location('atlas_b11_support',ROOT/B/'support.py'); s=importlib.util.module_from_spec(spec); sys.modules[spec.name]=s; spec.loader.exec_module(s)
checks=[]
def check(name,cond,detail=''):
    checks.append((name,bool(cond),detail)); print(('PASS ' if cond else 'FAIL ')+name, detail)
rng=np.random.default_rng(1111)
# SES hand
y=np.array([3.,5,4,6,8]); es=s.load('exponential-smoothing').ExponentialSmoothing(alpha=0.4).fit(y)
lvl=3.; fitted=[]
for v in y: fitted.append(lvl); lvl=0.4*v+0.6*lvl
check('SES recursion hand & flat forecast',np.allclose(es.fitted_values_,fitted) and np.allclose(es.forecast(3),lvl))
# Holt-Winters hand recursion with explicit initial states
m=4; yy=np.array([10,14,8,12, 12,16,10,14, 14,18,12,16.]); hw=s.load('holt-winters').HoltWinters(m,alpha=0.5,beta=0.3,gamma=0.2,initial_level=11.,initial_trend=0.5,initial_seasonal=[-1.,3,-3,1]).fit(yy)
L,T,S_=11.,0.5,np.array([-1.,3,-3,1]); fit=[np.nan]*m
for t in range(m,12):
    k=t%m; old_s,old_L=S_[k],L; fit.append(L+T+old_s); L=0.5*(yy[t]-old_s)+0.5*(L+T); T=0.3*(L-old_L)+0.7*T; S_[k]=0.2*(yy[t]-L)+0.8*old_s
check('Holt-Winters additive recursion hand',np.allclose(hw.fitted_values_[m:],fit[m:]) and np.allclose(hw.forecast(5),[L+(h+1)*T+S_[(12+h)%m] for h in range(5)]))
hw2=s.load('holt-winters').HoltWinters(m).fit(yy); check('Holt-Winters default initial seasonals sum to zero',abs(hw2.states_[0][2:].sum()-0)<1 and np.isclose(np.sum(yy[:m]-(np.mean(yy[:m])+hw2.states_[0][1]*0+ (np.mean(yy[m:2*m])-np.mean(yy[:m]))/m*(np.arange(m)-(m-1)/2))),0,atol=1e-9))
# differencing exactness
yd=rng.normal(size=20).cumsum(); z,tr=s.difference(yd,[4,1]); check('difference [4,1] exact',np.allclose(z,np.diff(yd[4:]-yd[:-4])))
fut=rng.normal(size=5); rec=s.inverse_difference(fut,tr)
# brute inverse: undo lag-1 then lag-4
w=list(yd[4:]-yd[:-4]); 
for v in fut: w.append(w[-1]+v)
lvl=list(yd); 
for v in w[len(yd)-4:]: lvl.append(lvl[-4]+v)
check('inverse_difference exactly inverts stacked operators',np.allclose(rec,lvl[len(yd):]))
# ARIMA AR(1) CSS == OLS on lagged values; forecast recursion
phi=0.6; e=rng.normal(size=200); x=np.zeros(200)
for t in range(1,200): x[t]=1.0+phi*x[t-1]+e[t]
ar=s.load('arima').ARIMA((1,0,0),tolerance=1e-10).fit(x)
Xl=np.column_stack((np.ones(199),x[:-1])); beta=np.linalg.lstsq(Xl,x[1:],rcond=None)[0]
check('ARIMA AR(1) CSS == OLS (intercept, phi)',abs(ar.params_['intercept']-beta[0])<1e-5 and abs(ar.params_['ar'][0]-beta[1])<1e-5,f"{ar.params_['intercept']:.6f},{ar.params_['ar'][0]:.6f} vs {beta}")
f=ar.forecast(3); c,p=ar.params_['intercept'],ar.params_['ar'][0]; h1=c+p*x[-1]; h2=c+p*h1; h3=c+p*h2
check('ARIMA AR(1) multistep forecast recursion',np.allclose(f,[h1,h2,h3],atol=1e-9))
# MA(1) innovations hand via filter with fixed params
ma=s.load('arima').ARIMA((0,0,1)).filter(x,dict(intercept=1.0,ma=[0.5])); z=x/ma.normalization_scale_; eps=np.zeros(200)
for t in range(1,200): eps[t]=z[t]-1.0/ma.normalization_scale_-0.5*eps[t-1]
check('ARIMA MA(1) innovation recursion hand',np.allclose(ma.innovations_[1:],eps[1:]*ma.normalization_scale_))
# CSS gradient finite difference (unconstrained params)
am=s.load('arima').ARIMA((2,0,1)); u=np.array([0.3,0.4,-0.2,0.1]); L,G=am.css_objective_gradient(x,u); h=1e-6
fd=[(am.css_objective_gradient(x,u+h*np.eye(4)[i])[0]-am.css_objective_gradient(x,u-h*np.eye(4)[i])[0])/(2*h) for i in range(4)]
check('ARIMA(2,0,1) CSS analytic gradient finite difference',np.allclose(G,fd,atol=1e-6),f'{np.max(np.abs(G-fd)):.1e}')
# SARIMA lag polynomial product
sa=s.load('sarima').SARIMA((1,0,1),(1,0,1,4)); arp,map_=sa.lag_polynomials(dict(intercept=0.,ar=[0.5],ma=[0.3],seasonal_ar=[0.4],seasonal_ma=[0.2]))
check('SARIMA multiplicative lag polynomials == convolution',np.allclose(arp,np.convolve([1,-0.5],[1,0,0,0,-0.4])) and np.allclose(map_,np.convolve([1,0.3],[1,0,0,0,0.2])))
sm=s.load('sarima').SARIMA((1,0,0),(1,0,0,4)); u=np.array([0.1,0.3,0.2]); L,G=sm.css_objective_gradient(x,u)
fd=[(sm.css_objective_gradient(x,u+h*np.eye(3)[i])[0]-sm.css_objective_gradient(x,u-h*np.eye(3)[i])[0])/(2*h) for i in range(3)]
check('SARIMA CSS gradient finite difference',np.allclose(G,fd,atol=1e-6))
# Prophet: ridge normal equations hand
yp=np.sin(2*np.pi*np.arange(40)/7)+0.05*np.arange(40)+rng.normal(scale=0.1,size=40); pr=s.load('prophet').Prophet(changepoints=(15.,),seasonalities=((7.,2),),regularization=0.05).fit(yp)
D=pr.design_matrix_; mask=pr.penalty_mask_; coef=np.linalg.solve(D.T@D+40*0.05*np.diag(mask),D.T@yp)
check('Prophet coefficients == ridge normal equations (unpenalized intercept/slope)',np.allclose(pr.coef_,coef,atol=1e-9) and np.allclose(pr.fitted_values_,D@coef))
check('Prophet components sum to total; future design continues time',np.allclose(pr.components_['trend']+pr.components_['seasonal'],pr.components_['total']) and np.allclose(pr.forecast(3),pr._design(np.arange(40,43),40)@pr.coef_))
# HMM: brute-force enumeration
hm=s.load('hidden-markov-models'); H=hm.CategoricalHMM(2,3,initial=[0.6,0.4],transition=[[0.7,0.3],[0.2,0.8]],emission=[[0.5,0.4,0.1],[0.1,0.3,0.6]]); obs=np.array([0,1,2,2,1])
pi=np.array([0.6,0.4]);A=np.array([[0.7,0.3],[0.2,0.8]]);E=np.array([[0.5,0.4,0.1],[0.1,0.3,0.6]])
paths=list(itertools.product(range(2),repeat=5)); probs=np.array([pi[p[0]]*E[p[0],obs[0]]*np.prod([A[p[t-1],p[t]]*E[p[t],obs[t]] for t in range(1,5)]) for p in paths])
check('HMM forward log-likelihood == brute-force path sum',abs(np.exp(H.score(obs))-probs.sum())<1e-14)
post=H.infer(obs); gam=np.array([[probs[[i for i,p in enumerate(paths) if p[t]==k]].sum() for k in range(2)] for t in range(5)])/probs.sum()
check('HMM posterior gamma == brute force',np.allclose(post['gamma'],gam,atol=1e-13))
xi=np.array([[[probs[[i for i,p in enumerate(paths) if p[t]==a and p[t+1]==b]].sum() for b in range(2)] for a in range(2)] for t in range(4)])/probs.sum()
check('HMM xi == brute force',np.allclose(post['xi'],xi,atol=1e-13))
path,val=H.decode(obs); best=paths[int(np.argmax(probs))]
check('HMM Viterbi == argmax path (brute force)',tuple(path)==best and abs(np.exp(val)-probs.max())<1e-14)
# Baum-Welch one iteration == expected-count re-estimation
H1=hm.CategoricalHMM(2,3,initial=pi,transition=A,emission=E); H1.fit([obs],max_iter=1,tolerance=1e-12)
tA=xi.sum(0); tA/=tA.sum(1,keepdims=True); tE=np.array([[gam[obs==k,st].sum() for k in range(3)] for st in range(2)]); tE/=tE.sum(1,keepdims=True)
check('Baum-Welch one step == expected counts (pi,A,E)',np.allclose(H1.initial_,gam[0]) and np.allclose(H1.transition_,tA) and np.allclose(H1.emission_,tE))
H2=hm.CategoricalHMM(2,3,random_state=3).fit([obs,np.array([2,2,1,0]),np.array([1,1,0,0,2])],max_iter=50); check('Baum-Welch log-likelihood monotone',np.all(np.diff(H2.log_likelihood_history_)>=-1e-10))
# backtest no leakage: training stops at origin
rec=s.backtest(lambda: s.load('exponential-smoothing').ExponentialSmoothing(0.5),yd,initial=10,horizon_size=2,step=3)
check('backtest origins chronological, train_stop==test_start',all(r['train_stop']==r['test_start'] and r['test_stop']==r['test_start']+2 for r in rec) and [r['train_stop'] for r in rec]==[10,13,16])
# metrics hand
mt=s.forecast_metrics([1,2,4],[1.5,2,3],training=[1,2,3,4,5]); check('forecast metrics hand (MAE, RMSE, sMAPE, MASE)',abs(mt['mae']-0.5)<1e-12 and abs(mt['rmse']-np.sqrt((0.25+0+1)/3))<1e-12 and abs(mt['mase']-0.5/1.0)<1e-12 and abs(mt['smape']-100*np.mean([1/2.5,0,2/7]))<1e-9)
print('\nSUMMARY',sum(c[1] for c in checks),'/',len(checks),'passed')
