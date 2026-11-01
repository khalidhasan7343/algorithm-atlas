import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


@pytest.mark.oracle
def test_independent_advantage_actor_and_critic_updates(rl):
    m=rl.load('advantage-actor-critic').A2C(hidden=2)
    for p in (m.actor,m.critic):
        for v in p.values():v[:]=0
    m.critic['b2'][:]=.25
    al,cl,ag,cg=rl.load('advantage-actor-critic').loss_gradients(m.actor,m.critic,[[1.]],np.array([1]),[1.])
    assert_allclose(al,.75*np.log(2));assert_allclose(cl,.5*.75**2)
    assert_allclose(ag['b2'],[.375,-.375]);assert_allclose(cg['b2'],[-.75])


@pytest.mark.numerical
def test_finite_difference_actor_frozen_advantage_and_critic(rl,gradients):
    m=rl.load('advantage-actor-critic').A2C(inputs=2,hidden=3,seed=50)
    x=np.array([[.2,.4],[-.3,.1]]);a=np.array([0,1]);t=np.array([1.,-.2])
    al,cl,ag,cg=rl.load('advantage-actor-critic').loss_gradients(m.actor,m.critic,x,a,t)
    values=(np.tanh(x@m.critic['W1']+m.critic['b1'])@m.critic['W2']+m.critic['b2'])[:,0]
    advantage=t-values
    def independent_actor(p):
        z=np.tanh(x@p['W1']+p['b1'])@p['W2']+p['b2']
        return -np.mean((z[np.arange(2),a]-np.logaddexp(z[:,0],z[:,1]))*advantage)
    def independent_critic(p):
        v=(np.tanh(x@p['W1']+p['b1'])@p['W2']+p['b2'])[:,0]
        return .5*np.mean((v-t)**2)
    gradients(independent_actor,m.actor,ag);gradients(independent_critic,m.critic,cg)


@pytest.mark.parametrize('seed',[51,52,53])
def test_synchronous_training_and_reproducibility(rl,seed):
    cls=rl.load('advantage-actor-critic').A2C
    one=cls(seed=seed).train(iterations=200,max_steps=1,envs=2)
    two=cls(seed=seed).train(iterations=200,max_steps=1,envs=2)
    for p,q in ((one.actor,two.actor),(one.critic,two.critic)):
        for k in p:assert_array_equal(p[k],q[k])
    assert rl.evaluate(one,rl.Bandit)['mean_return']==1
    assert rl.forward(one.critic,[[1.]])[0][0,0]>.8


@pytest.mark.oracle
def test_n_step_return_truncation_bootstrap(rl):
    m=rl.load('advantage-actor-critic').A2C()
    m.critic['W2'][:]=0;m.critic['b2'][:]=2
    class Cut(rl.Bandit):
        def step(self,a):return np.ones(1),1.,False,True,{}
    x,a,target,total=rl.collect(m.actor,m.critic,Cut(),np.random.default_rng(5),1,.9)
    assert_allclose(target,[2.8]);assert total==1
    x,a,target,total=rl.collect(m.actor,m.critic,rl.Bandit(),np.random.default_rng(5),1,.9)
    assert_allclose(target,a.astype(float))
