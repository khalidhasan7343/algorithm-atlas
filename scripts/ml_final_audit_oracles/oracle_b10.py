import importlib.util, sys, math
from pathlib import Path
import numpy as np
from scipy.optimize import minimize as spmin, rosen, rosen_der
ROOT=Path('.'); B='machine-learning/optimization/'
spec=importlib.util.spec_from_file_location('atlas_b10_support',ROOT/B/'support.py'); sup=importlib.util.module_from_spec(spec); sys.modules[spec.name]=sup; spec.loader.exec_module(sup)
checks=[]
def check(name,cond,detail=''):
    checks.append((name,bool(cond),detail)); print(('PASS ' if cond else 'FAIL ')+name, detail)
rng=np.random.default_rng(1010)
A=np.array([[3.,1],[1,2]]); b=np.array([1.,-1]); f=lambda x:0.5*x@A@x-b@x; g=lambda x:A@x-b; xstar=np.linalg.solve(A,b)
# batch GD: closed form x_{k+1}=x_k - lr g; check trajectory and convergence
gd=sup.load('batch-gradient-descent').BatchGradientDescent(learning_rate=0.2); res=gd.minimize(f,g,[0.,0.],max_iter=500,tolerance=1e-10)
x=np.zeros(2); traj=[x.copy()]
for _ in range(res.n_iter): x=x-0.2*g(x); traj.append(x.copy())
check('Batch GD trajectory == hand recursion & converges to A^-1 b',np.allclose(res.diagnostics['trajectory'],traj) and np.allclose(res.x,xstar,atol=1e-9) and res.converged)
# momentum heavy ball hand
mo=sup.load('momentum').Momentum(learning_rate=0.1,beta=0.9); x1=mo.step([1.,1.],g(np.array([1.,1]))); v=g(np.array([1.,1])); x2=mo.step(x1,g(x1)); v=0.9*v+g(x1)
check('Momentum two heavy-ball steps hand',np.allclose(x1,[1,1]-0.1*g(np.array([1.,1]))) and np.allclose(x2,x1-0.1*v))
# RMSProp hand
rp=sup.load('rmsprop').RMSProp(learning_rate=0.01,beta=0.9,epsilon=1e-8); g0=np.array([2.,-3]); x1=rp.step([0.,0.],g0); s=0.1*g0**2
check('RMSProp first step hand',np.allclose(x1,-0.01*g0/(np.sqrt(s)+1e-8)))
# Adam two steps hand (bias-corrected)
ad=sup.load('adam').Adam(learning_rate=0.1,beta1=0.9,beta2=0.999,epsilon=1e-8); x0=np.array([1.,2]); g1=g(x0); x1=ad.step(x0,g1)
m=0.1*g1; v=0.001*g1**2; mh=m/(1-0.9); vh=v/(1-0.999); e1=x0-0.1*mh/(np.sqrt(vh)+1e-8)
g2=g(x1); x2=ad.step(x1,g2); m=0.9*m+0.1*g2; v=0.999*v+0.001*g2**2; mh=m/(1-0.9**2); vh=v/(1-0.999**2); e2=x1-0.1*mh/(np.sqrt(vh)+1e-8)
check('Adam two bias-corrected steps hand',np.allclose(x1,e1) and np.allclose(x2,e2))
check('bias_correction(beta,t) == 1-beta^t to 1e-16 relative',all(abs(sup.bias_correction(bt,t)-(1-bt**t))<1e-16 for bt in (0.9,0.999) for t in (1,5,50)))
# AdamW: decoupled decay on OLD parameters, masked
aw=sup.load('adamw').AdamW(learning_rate=0.1,weight_decay=0.5,decay_mask=np.array([True,False])); x1w=aw.step(x0,g1)
check('AdamW == Adam step - lr*wd*mask*x_old',np.allclose(x1w,e1-0.1*0.5*np.array([1,0])*x0))
# SGD: exact single-observation reshuffled updates with recorded batches
sg=sup.load('stochastic-gradient-descent').StochasticGradientDescent(learning_rate=0.05,random_state=3)
X=rng.normal(size=(6,2)); y=X@[1,-2]; fs=lambda w: 0.5*np.mean((X@w-y)**2); gs=lambda w,idx: X[idx].T@(X[idx]@w-y[idx])/len(idx)
r=sg.minimize(fs,gs,[0.,0.],n_samples=6,max_epochs=3)
w=np.zeros(2); ok=True
for bt,xt in zip(r.diagnostics['batch_history'],r.diagnostics['trajectory'][1:]): w=w-0.05*gs(w,bt); ok&=np.allclose(w,xt)
check('SGD trajectory reproduces recorded single-observation batches',ok and all(len(bt)==1 for bt in r.diagnostics['batch_history']) and len(r.diagnostics['batch_history'])==18)
mb=sup.load('mini-batch-gradient-descent').MiniBatchGradientDescent(learning_rate=0.05,batch_size=4,random_state=3).minimize(fs,gs,[0.,0.],n_samples=6,max_epochs=2)
check('Mini-batch: disjoint shuffled batches of sizes 4,2 per epoch',[len(bt) for bt in mb.diagnostics['batch_history']]==[4,2,4,2] and all(sorted(np.concatenate(mb.diagnostics['batch_history'][2*e:2*e+2]).tolist())==list(range(6)) for e in range(2)))
# L-BFGS: two-loop == dense inverse BFGS; Rosenbrock vs scipy
lb=sup.load('l-bfgs'); pairs=[(rng.normal(size=3),None) for _ in range(3)]; pairs=[(s,s+0.3*rng.normal(size=3)) for s,_ in pairs]; pairs=[(s,y) for s,y in pairs if s@y>0]
gq=rng.normal(size=3); H=(pairs[-1][0]@pairs[-1][1])/(pairs[-1][1]@pairs[-1][1])*np.eye(3)
for s,y in pairs:
    rho=1/(s@y); V=np.eye(3)-rho*np.outer(y,s); H=V.T@H@V+rho*np.outer(s,s)
check('L-BFGS two-loop == dense recursive inverse-BFGS product',np.allclose(lb.inverse_hessian_product(gq,pairs),H@gq,atol=1e-10))
res=lb.LBFGS().minimize(rosen,rosen_der,[-1.2,1.],max_iter=500,tolerance=1e-9); ref=spmin(rosen,[-1.2,1.],jac=rosen_der,method='L-BFGS-B',options=dict(gtol=1e-12,ftol=1e-16))
check('L-BFGS Rosenbrock reaches [1,1] like scipy',np.allclose(res.x,[1,1],atol=1e-6) and np.allclose(ref.x,[1,1],atol=1e-5) and res.converged,f'ours {res.x} iters {res.n_iter}')
ws=res.diagnostics['wolfe_steps']; c1,c2=1e-4,0.9
check('L-BFGS every accepted step satisfies strong Wolfe',all(w['value_after']<=w['value_before']+c1*w['step_size']*w['slope_before']+1e-12 and abs(w['slope_after'])<=-c2*w['slope_before']+1e-12 for w in ws))
# SA: Metropolis probability & exact chain replay
sa=sup.load('simulated-annealing'); check('Metropolis probability exp(-delta/T), 1 for improvements',sa.metropolis_probability(-1,1)==1 and abs(sa.metropolis_probability(2.,0.5)-math.exp(-4))<1e-15)
fb=lambda bits: float(np.sum(bits))  # minimize ones
r=sa.SimulatedAnnealing(initial_temperature=1.,cooling=0.9,random_state=4).minimize(fb,[1,1,1,1,1,1],max_iter=200)
rr=np.random.default_rng(4); cur=np.ones(6,int); val=6.; ok=True
for k,(acc,T) in enumerate(zip(r.diagnostics['accepted'],r.diagnostics['temperatures'])):
    ok&=abs(T-0.9**k)<1e-12; prop=cur.copy(); i=int(rr.integers(6)); prop[i]^=1; d=fb(prop)-val; a=d<=0
    if not a: u=float(rr.random()); a=bool(u==0 or math.log(u)<-d/T)
    ok&=(a==acc)
    if a: cur,val=prop,fb(prop)
check('SA seeded Metropolis chain replay (temperatures, acceptances) exact',ok and r.fun==0.0,f'best {r.fun} status {r.status}')
# GA operators exact
ga=sup.load('genetic-algorithms'); check('GA tournament picks min fitness (ties -> lowest index)',ga.tournament_selection([3.,1.,1.,2.],[0,2,1])==1)
c1_,c2_=ga.uniform_crossover([1,1,1,1],[0,0,0,0],np.array([True,False,True,False])); check('GA uniform crossover exact',c1_.tolist()==[1,0,1,0] and c2_.tolist()==[0,1,0,1])
check('GA bit-flip mutation exact',ga.bit_flip_mutation([1,0,1],np.array([True,True,False])).tolist()==[0,1,1])
r=ga.GeneticAlgorithm(population_size=16,random_state=2).minimize(fb,8,max_generations=60,target_value=0.)
check('GA elitism: best never worsens; reaches target 0',np.all(np.diff(r.history)<=0) and r.fun==0.0 and r.status=='target-reached')
# no global RNG mutation
st=np.random.get_state()[1].copy(); ga.GeneticAlgorithm(random_state=7).minimize(fb,6,max_generations=5); sa.SimulatedAnnealing(random_state=7).minimize(fb,[1,0,1],max_iter=20)
check('GA/SA leave global RNG untouched',np.array_equal(st,np.random.get_state()[1]))
print('\nSUMMARY',sum(c[1] for c in checks),'/',len(checks),'passed')
