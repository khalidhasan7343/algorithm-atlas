import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


@pytest.mark.oracle
def test_neural_forward_selected_q_td_targets_and_terminal_mask(rl):
    m=rl.load('deep-q-networks');p=rl.initialize(1,2,np.random.default_rng(2),2)
    x=np.array([[.2],[.5]]);h=np.tanh(x@p['W1']+p['b1']);q=h@p['W2']+p['b2']
    assert_allclose(rl.forward(p,x)[0],q)
    y=m.td_targets(p,x,np.array([2.,3.]),np.array([False,True]),.7)
    assert_allclose(y,[2+.7*max(q[0]),3])
    loss,g=m.loss_gradients(p,x,np.array([1,0]),y)
    residual=np.array([q[0,1],q[1,0]])-y
    assert_allclose(loss,.5*np.mean(residual**2))
    assert g['W2'].shape==(2,2)


@pytest.mark.numerical
def test_finite_difference_fixed_td_targets_all_parameters(rl,gradients):
    m=rl.load('deep-q-networks');p=rl.initialize(2,2,np.random.default_rng(8),3)
    x=np.array([[.3,-.2],[-.1,.4]]);a=np.array([1,0]);y=np.array([.6,-.2])
    _,g=m.loss_gradients(p,x,a,y)
    def independent(q):
        hidden=np.tanh(x@q['W1']+q['b1']);values=hidden@q['W2']+q['b2']
        return .5*np.mean((values[np.arange(2),a]-y)**2)
    gradients(independent,p,g)


def test_replay_fifo_sampling_ownership_and_underflow(rl):
    replay=rl.Replay(3);x=np.array([1.])
    for i in range(4):replay.add(x,0,float(i),x,False,True)
    x[:]=99
    assert len(replay.data)==3 and replay.data[0][2]==1
    assert replay.data[0][0][0]==1
    one=replay.sample(3,np.random.default_rng(5));two=replay.sample(3,np.random.default_rng(5))
    for a,b in zip(one,two):assert_array_equal(a,b)
    one[0][:]=50;assert replay.data[0][0][0]==1
    with pytest.raises(ValueError):replay.sample(4,np.random.default_rng(0))
    with pytest.raises(ValueError):rl.Replay().sample(1,np.random.default_rng(0))


def test_target_snapshot_and_synchronization_gradient_application(rl):
    m=rl.load('deep-q-networks').DQN(batch_size=1,target_interval=2,seed=5)
    old=rl.copy(m.target)
    assert all(not np.shares_memory(m.target[k],m.online[k]) for k in old)
    m.replay.add([1.],1,1.,[1.],True)
    m.step()
    for k in old:assert_array_equal(m.target[k],old[k])
    assert any(not np.array_equal(m.online[k],old[k]) for k in old)
    m.step()
    for k in old:assert_array_equal(m.target[k],m.online[k])


@pytest.mark.parametrize('seed',[31,32,33])
def test_seeded_training_separate_greedy_evaluation(rl,seed):
    cls=rl.load('deep-q-networks').DQN
    m=cls(seed=seed).train(rl.Bandit(),episodes=250,max_steps=1)
    other=cls(seed=seed).train(rl.Bandit(),episodes=250,max_steps=1)
    for k in m.online:assert_array_equal(m.online[k],other.online[k])
    assert rl.evaluate(m,rl.Bandit,episodes=20)['mean_return']==1
    assert_allclose(rl.forward(m.online,[[1.]])[0][0],[0,1],atol=.04)


def test_nonterminal_truncation_td_target_is_fixed(rl):
    m=rl.load('deep-q-networks');p=rl.initialize(1,2,np.random.default_rng(2))
    p['b2'][:]=[2,3];p['W2'][:]=0
    y=m.td_targets(p,[[1.]],np.array([1.]),np.array([False]),.9)
    assert_allclose(y,[3.7])
    old=rl.copy(p);m.loss_gradients(p,[[1.]],np.array([0]),y)
    for k in p:assert_array_equal(p[k],old[k])


@pytest.mark.parametrize('bad',[-1,2,True])
def test_invalid_neural_action(rl,bad):
    m=rl.load('deep-q-networks');p=rl.initialize(1,2,np.random.default_rng(0))
    with pytest.raises(ValueError):m.loss_gradients(p,[[1.]],np.array([bad]),[1.])
