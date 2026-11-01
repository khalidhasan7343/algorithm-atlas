import threading
import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


def test_actual_concurrency_local_environments_snapshots_and_global_updates(rl):
    barrier=threading.Barrier(2,timeout=3)
    seen=[];closed=[];lock=threading.Lock()
    class Overlap(rl.Bandit):
        def step(self,a):
            with lock:seen.append((id(self),threading.get_ident()))
            barrier.wait()
            return super().step(a)
        def close(self):
            with lock:closed.append(id(self))
    m=rl.load('asynchronous-advantage-actor-critic').A3C(seed=61)
    before=rl.copy(m.actor)
    m.train(Overlap,iterations=1,max_steps=1,workers=2,timeout=8)
    assert m.workers_created_==2 and m.workers_alive_==0 and m.updates_==2
    assert len({x[0] for x in seen})==2 and len({x[1] for x in seen})==2
    assert sorted(closed)==sorted(x[0] for x in seen)
    assert {row['snapshot_version'] for row in m.worker_records_}=={0}
    assert [row['applied_version'] for row in m.worker_records_]==[1,2]
    assert len(set(m.worker_seeds_))==2
    assert any(not np.array_equal(before[k],m.actor[k]) for k in before)


@pytest.mark.numerical
def test_finite_difference_worker_gradients_independent_losses(rl,gradients):
    m=rl.load('asynchronous-advantage-actor-critic').A3C(inputs=2,hidden=2,seed=62)
    x=np.array([[.2,-.1],[.5,.3]]);a=np.array([1,0]);target=np.array([.8,-.3])
    _,_,ag,cg=rl.load('asynchronous-advantage-actor-critic').loss_gradients(m.actor,m.critic,x,a,target)
    values=(np.tanh(x@m.critic['W1']+m.critic['b1'])@m.critic['W2']+m.critic['b2'])[:,0];adv=target-values
    def actor(p):
        z=np.tanh(x@p['W1']+p['b1'])@p['W2']+p['b2']
        return -np.mean((z[np.arange(2),a]-np.logaddexp(z[:,0],z[:,1]))*adv)
    def critic(p):
        z=(np.tanh(x@p['W1']+p['b1'])@p['W2']+p['b2'])[:,0]
        return .5*np.mean((z-target)**2)
    gradients(actor,m.actor,ag);gradients(critic,m.critic,cg)


def test_single_worker_deterministic_diagnostic_exact_global_application(rl):
    cls=rl.load('asynchronous-advantage-actor-critic').A3C
    one=cls(seed=63).train(iterations=100,max_steps=1,workers=1)
    two=cls(seed=63).train(iterations=100,max_steps=1,workers=1)
    for p,q in ((one.actor,two.actor),(one.critic,two.critic)):
        for k in p:assert_array_equal(p[k],q[k])
    assert one.returns_==two.returns_ and one.workers_alive_==0
    assert rl.evaluate(one,rl.Bandit)['mean_return']==1


def test_one_worker_exact_gradient_step_oracle(rl):
    m=rl.load('asynchronous-advantage-actor-critic').A3C(hidden=2,seed=64,learning_rate=.1)
    for p in (m.actor,m.critic):
        for v in p.values():v[:]=0
    class Reward(rl.Bandit):
        def step(self,a):return np.ones(1),1.,True,False,{}
    m.train(Reward,iterations=1,max_steps=1,workers=1)
    assert_allclose(m.critic['b2'],[.1])
    assert_allclose(sorted(m.actor['b2']),[-.05,.05])


@pytest.mark.parametrize('failure',['factory','rollout','close'])
def test_worker_exception_propagation_and_clean_shutdown(rl,failure):
    closed=[]
    class Broken(rl.Bandit):
        def step(self,a):
            if failure=='rollout':raise ValueError('worker diagnostic')
            return super().step(a)
        def close(self):
            closed.append(1)
            if failure=='close':raise ValueError('close diagnostic')
    def factory():
        if failure=='factory':raise ValueError('factory diagnostic')
        return Broken()
    m=rl.load('asynchronous-advantage-actor-critic').A3C(seed=65)
    with pytest.raises(RuntimeError,match='worker') as error:m.train(factory,iterations=2,max_steps=1,workers=2,timeout=3)
    assert isinstance(error.value.__cause__,ValueError) and m.workers_alive_==0
    assert not any(t.name.startswith('atlas-a3c-') for t in threading.enumerate())
    if failure!='factory':assert len(closed)==2


def test_bounded_multiworker_learning_invariants(rl):
    m=rl.load('asynchronous-advantage-actor-critic').A3C(seed=66).train(iterations=100,max_steps=1,workers=3)
    assert m.updates_==300 and m.workers_alive_==0
    assert {row['worker'] for row in m.worker_records_}=={0,1,2}
    assert all(row['snapshot_version']<row['applied_version'] for row in m.worker_records_)
    assert all(row['trajectory_length']==1 for row in m.worker_records_)
    assert rl.evaluate(m,rl.Bandit)['mean_return']==1
