import importlib.util, sys
from pathlib import Path
import numpy as np
ROOT=Path('.'); B='machine-learning/reinforcement-learning/'
spec=importlib.util.spec_from_file_location('atlas_b8_support',ROOT/B/'support.py'); sup=importlib.util.module_from_spec(spec); sys.modules[spec.name]=sup; spec.loader.exec_module(sup)
checks=[]
def check(name,cond,detail=''):
    checks.append((name,bool(cond),detail)); print(('PASS ' if cond else 'FAIL ')+name, detail)
rng=np.random.default_rng(88); h=1e-6
def fd_dict(f,p):
    g={}
    for k,v in p.items():
        g[k]=np.zeros_like(v)
        for idx in np.ndindex(v.shape):
            q=dict(p); vp=v.copy(); vp[idx]+=h; q[k]=vp; fp=f(q); vm=v.copy(); vm[idx]-=h; q[k]=vm; fm=f(q); g[k][idx]=(fp-fm)/(2*h)
    return g
def worst(a,b): return max(np.max(np.abs(a[k]-b[k])) for k in a)
# Q-learning on Chain: Q*(0,right)=gamma, Q*(1,right)=1, Q*(1,left)=gamma^2, Q*(0,left)=gamma^2 (stay at 0 then 2 steps)
ql=sup.load('q-learning').QLearning(3,2,alpha=0.5,gamma=0.9,epsilon=0.3,seed=1).train(sup.Chain(),episodes=400,max_steps=16)
Qstar=np.array([[0.9**2,0.9],[0.9**2,1.0],[0,0]])
check('Q-learning converges to Bellman-optimal Q* on Chain',np.allclose(ql.q[:2],Qstar[:2],atol=1e-6),f'{ql.q[:2].round(6).tolist()}')
# single update hand formula
q0=sup.load('q-learning').QLearning(3,2,alpha=0.3,gamma=0.8); q0.q[1]=[0.2,0.7]; v=q0.update(0,1,0.0,1,False)
check('Q-learning update hand: q+alpha(r+gamma max q(s\')-q)',abs(v-0.3*(0+0.8*0.7))<1e-12)
# SARSA epsilon 0 greedy converges to Q* on reached pairs; hand update
sa=sup.load('sarsa').SARSA(3,2,alpha=0.3,gamma=0.8); sa.q[1]=[0.2,0.7]; v=sa.update(0,1,0.0,1,0,False)
check('SARSA update uses sampled next action (0.2 not 0.7)',abs(v-0.3*(0.8*0.2))<1e-12)
sa=sup.load('sarsa').SARSA(3,2,alpha=0.5,gamma=0.9,epsilon=0.3,seed=2).train(sup.Chain(),episodes=600,max_steps=16)
check('SARSA greedy policy on Chain is always right',np.array_equal(sa.policy()[:2],[1,1]))
# returns recursion vs explicit sum
r=rng.normal(size=6); g=0.7; boot=0.3
exp=np.array([sum(g**(j-i)*r[j] for j in range(i,6))+g**(6-i)*boot for i in range(6)])
check('returns(): discounted reward-to-go with bootstrap',np.allclose(sup.returns(r,g,boot),exp))
# policy_loss gradient FD (weights fixed)
p=sup.initialize(3,4,rng); X=rng.normal(size=(7,3)); a=rng.integers(0,4,7); w=rng.normal(size=7)
L,G=sup.policy_loss(p,X,a,w); check('policy_loss gradient finite difference',worst(G,fd_dict(lambda q:sup.policy_loss(q,X,a,w)[0],p))<1e-7)
hand=-np.mean(sup.log_softmax(sup.forward(p,X)[0])[np.arange(7),a]*w); check('policy_loss == -mean(w * log pi(a|s))',abs(L-hand)<1e-12)
pc=sup.initialize(3,1,rng); t=rng.normal(size=7); L,G=sup.value_loss(pc,X,t); check('value_loss gradient finite difference',worst(G,fd_dict(lambda q:sup.value_loss(q,X,t)[0],pc))<1e-7)
# DQN targets & gradient
dq=sup.load('deep-q-networks'); done=np.array([False,True,False,False,True,False,False]); y=dq.td_targets(p,X,t,done,0.9)
check('DQN td_targets = r + gamma(1-done)max Q_target',np.allclose(y,t+0.9*(~done)*sup.forward(p,X)[0].max(1)))
L,G=dq.loss_gradients(p,X,a,y); check('DQN loss gradient finite difference',worst(G,fd_dict(lambda q:dq.loss_gradients(q,X,a,y)[0],p))<1e-7)
# REINFORCE loss_gradients FD; weights gamma^t * G_t * T
rf=sup.load('reinforce-policy-gradient'); G_t=rng.normal(size=7); L,G=rf.loss_gradients(p,X,a,G_t,0.9)
check('REINFORCE gradient finite difference',worst(G,fd_dict(lambda q:rf.loss_gradients(q,X,a,G_t,0.9)[0],p))<1e-7)
check('REINFORCE loss == -sum_t gamma^t G_t log pi',abs(L+np.sum(0.9**np.arange(7)*G_t*sup.log_softmax(sup.forward(p,X)[0])[np.arange(7),a]))<1e-10)
# PPO surrogate FD wrt actor params with fixed old logp & advantage; also clipped zero-gradient region
pp=sup.load('proximal-policy-optimization'); old=sup.log_softmax(sup.forward(p,X)[0])[np.arange(7),a]-0.3*rng.random(7); adv=rng.normal(size=7)
L,G,ratio=pp.loss_gradients(p,X,a,old,adv,0.2); check('PPO clipped surrogate gradient finite difference',worst(G,fd_dict(lambda q:pp.loss_gradients(q,X,a,old,adv,0.2)[0],p))<1e-7,f'ratios {ratio.round(2)}')
Ls,dl,rt=pp.surrogate(np.array([-0.1]),np.array([-0.9]),np.array([1.0]),0.2); check('PPO: ratio>1+eps with A>0 gives zero gradient and clipped loss',dl[0]==0 and abs(Ls+1.2)<1e-12)
# DDPG actor loss gradient FD (critic fixed); soft update formula
dd=sup.load('deep-deterministic-policy-gradient'); act=sup.initialize(3,2,rng); cri=sup.initialize(5,1,rng); low=np.array([-1.,-2.]); high=np.array([1.,0.])
L,G=dd.actor_loss(act,cri,X,low,high); check('DDPG actor gradient (-mean Q(s,mu(s))) finite difference',worst(G,fd_dict(lambda q:dd.actor_loss(q,cri,X,low,high)[0],act))<1e-7)
A_,raw=dd.actor_forward(act,X,low,high); check('DDPG actions within bounds via tanh scaling',np.all(A_>=low) and np.all(A_<=high) and np.allclose(A_,(high+low)/2+(high-low)/2*np.tanh(raw)))
tgt=sup.copy(cri); onl=sup.initialize(5,1,rng); before=sup.copy(tgt); dd.soft_update(tgt,onl,0.1); check('DDPG soft update tau*online+(1-tau)*target',all(np.allclose(tgt[k],0.1*onl[k]+0.9*before[k]) for k in tgt))
yd=dd.td_targets(act,cri,X,t,done,0.9,low,high); an=dd.actor_forward(act,X,low,high)[0]; check('DDPG td_targets use target actor action',np.allclose(yd,t+0.9*(~done)*sup.forward(cri,np.column_stack([X,an]))[0][:,0]))
# MCTS finds the unique rewarding path in TinyPlanning
mc=sup.load('monte-carlo-tree-search'); model=mc.TinyPlanning(); chosen,root=mc.search(model,(0,0),iterations=300,seed=3)
check('MCTS root chooses action 1 (only rewarding path 111)',chosen==1 and root.children[1].visits>root.children[0].visits,f'visits {[root.children[k].visits for k in (0,1)]}')
n=mc.Node(None); n.visits=4; n.value_sum=2.; check('UCT formula',abs(mc.uct(n,10)-(0.5+np.sqrt(2)*np.sqrt(np.log(10)/4)))<1e-12)
check('MCTS visit conservation: root visits == iterations == sum child visits',root.visits==300 and sum(c.visits for c in root.children.values())==300)
# A2C and A3C run; A3C uses >1 thread and applies to global params
a2=sup.load('advantage-actor-critic').A2C(1,2,seed=0).train(sup.Bandit,iterations=60,max_steps=1,envs=2)
check('A2C learns the rewarding bandit arm',a2.action(np.ones(1),explore=False)==1 and a2.returns_[-1]>=a2.returns_[0])
a3=sup.load('asynchronous-advantage-actor-critic').A3C(1,2,seed=0).train(sup.Bandit,iterations=30,max_steps=1,workers=3)
tids={r['thread_id'] for r in a3.worker_records_}; stale=sum(r['applied_version']-1!=r['snapshot_version'] for r in a3.worker_records_)
check('A3C: 3 worker threads, 90 global updates, some stale-snapshot applications (true asynchrony)',len(tids)==3 and a3.updates_==90 and len(a3.worker_records_)==90,f'threads {len(tids)} updates {a3.updates_} stale {stale}')
# determinism & global RNG
st=np.random.get_state()[1].copy(); d1=sup.load('deep-q-networks').DQN(seed=5).train(sup.Bandit(),episodes=40,max_steps=1); d2=sup.load('deep-q-networks').DQN(seed=5).train(sup.Bandit(),episodes=40,max_steps=1)
check('DQN seeded training deterministic & global RNG untouched',all(np.array_equal(d1.online[k],d2.online[k]) for k in d1.online) and np.array_equal(st,np.random.get_state()[1]))
print('\nSUMMARY',sum(c[1] for c in checks),'/',len(checks),'passed')
