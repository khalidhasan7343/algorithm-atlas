import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


@pytest.mark.oracle
def test_continuous_actor_bounds_and_critic_forward(rl):
    mod=rl.load('deep-deterministic-policy-gradient');m=mod.DDPG(inputs=2,action_dim=2,low=[-2,1],high=[3,4],hidden=3,seed=80)
    x=np.array([[.3,-.2],[-.5,.1]])
    raw=np.tanh(x@m.actor['W1']+m.actor['b1'])@m.actor['W2']+m.actor['b2']
    expected=np.array([.5,2.5])+np.array([2.5,1.5])*np.tanh(raw)
    actions,_=mod.actor_forward(m.actor,x,m.low,m.high);assert_allclose(actions,expected)
    joined=np.column_stack([x,actions]);q=np.tanh(joined@m.critic['W1']+m.critic['b1'])@m.critic['W2']+m.critic['b2']
    assert_allclose(rl.forward(m.critic,joined)[0],q)
    assert np.all(actions>=m.low) and np.all(actions<=m.high)


@pytest.mark.numerical
def test_finite_difference_deterministic_actor_through_fixed_critic(rl,gradients):
    mod=rl.load('deep-deterministic-policy-gradient');m=mod.DDPG(inputs=2,hidden=3,low=[-2],high=[3],seed=81)
    x=np.array([[.2,-.3],[.1,.5]])
    _,g=mod.actor_loss(m.actor,m.critic,x,m.low,m.high)
    def independent(p):
        raw=np.tanh(x@p['W1']+p['b1'])@p['W2']+p['b2'];a=.5+2.5*np.tanh(raw)
        joined=np.column_stack([x,a]);q=np.tanh(joined@m.critic['W1']+m.critic['b1'])@m.critic['W2']+m.critic['b2']
        return -q.mean()
    gradients(independent,m.actor,g)


@pytest.mark.numerical
def test_critic_finite_difference_fixed_td_target(rl,gradients):
    mod=rl.load('deep-deterministic-policy-gradient');m=mod.DDPG(hidden=3,seed=82)
    x=np.array([[.2],[-.4]]);a=np.array([[.3],[-.2]]);t=np.array([.7,-.1]);joined=np.column_stack([x,a])
    _,g=mod.critic_loss(m.critic,x,a,t)
    def independent(p):
        q=(np.tanh(joined@p['W1']+p['b1'])@p['W2']+p['b2'])[:,0]
        return .5*np.mean((q-t)**2)
    gradients(independent,m.critic,g)


@pytest.mark.oracle
def test_td_terminal_mask_truncation_and_soft_target_interpolation(rl):
    mod=rl.load('deep-deterministic-policy-gradient');m=mod.DDPG(seed=83)
    m.target_critic['W2'][:]=0;m.target_critic['b2'][:]=3
    t=mod.td_targets(m.target_actor,m.target_critic,np.array([[1.],[1.]]),np.array([1.,2.]),np.array([False,True]),.9,m.low,m.high)
    assert_allclose(t,[3.7,2])
    for tau in (0.,.2,1.):
        old=rl.copy(m.target_actor);online=rl.copy(m.actor)
        for v in online.values():v+=.5
        mod.soft_update(m.target_actor,online,tau)
        for k in old:assert_allclose(m.target_actor[k],tau*online[k]+(1-tau)*old[k])
        assert all(not np.shares_memory(m.target_actor[k],online[k]) for k in old)


def test_noise_seed_action_clipping_replay_and_parameter_updates(rl):
    mod=rl.load('deep-deterministic-policy-gradient');one=mod.DDPG(noise=2.,batch_size=2,seed=84);two=mod.DDPG(noise=2.,batch_size=2,seed=84)
    draws=np.array([one.action([1.]) for _ in range(50)]);other=np.array([two.action([1.]) for _ in range(50)])
    assert_array_equal(draws,other);assert np.max(abs(draws))==1
    deterministic=one.action([1.],False);assert_array_equal(deterministic,one.action([1.],False))
    old_actor=rl.copy(one.actor);old_critic=rl.copy(one.critic);old_target=rl.copy(one.target_actor)
    one.replay.add([.5],np.array([.1]),-.1,[.5],True);one.replay.add([-.5],np.array([-.2]),-.1,[-.5],True)
    one.step()
    for before,after in [(old_actor,one.actor),(old_critic,one.critic),(old_target,one.target_actor)]:
        assert any(not np.array_equal(before[k],after[k]) for k in before)


@pytest.mark.parametrize('seed',[85,86,87])
def test_tiny_continuous_control_training_and_reproducibility(rl,seed):
    cls=rl.load('deep-deterministic-policy-gradient').DDPG
    m=cls(seed=seed);before=rl.evaluate(m,rl.Continuous,episodes=100,seed=990)
    m.train(rl.Continuous(),episodes=2400,max_steps=1)
    after=rl.evaluate(m,rl.Continuous,episodes=100,seed=990)
    assert after['mean_return']>-.04 and after['mean_return']>before['mean_return']
    other=cls(seed=seed).train(rl.Continuous(),episodes=2400,max_steps=1)
    for k in m.actor:assert_array_equal(m.actor[k],other.actor[k])


@pytest.mark.parametrize('low,high',[([1],[1]),([2],[-1]),([np.nan],[1]),([],[])])
def test_invalid_action_bounds(rl,low,high):
    with pytest.raises(ValueError):rl.load('deep-deterministic-policy-gradient').DDPG(low=low,high=high)


def test_critic_warmup_preserves_actor_while_learning_from_uniform_actions(rl):
    m=rl.load('deep-deterministic-policy-gradient').DDPG(warmup_steps=128,batch_size=4,seed=88)
    actor,critic=rl.copy(m.actor),rl.copy(m.critic)
    m.train(rl.Continuous(),episodes=20)
    for k in actor:assert_array_equal(actor[k],m.actor[k])
    assert any(not np.array_equal(critic[k],m.critic[k]) for k in critic)
    assert np.std([row[1][0] for row in m.replay.data])>.4
