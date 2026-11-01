import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


@pytest.mark.oracle
def test_ratio_clipping_both_advantage_signs_and_logp_derivative(rl):
    m=rl.load('proximal-policy-optimization')
    ratio=np.array([1.3,.7,1.3,.7]);adv=np.array([2,2,-2,-2.])
    loss,dlogp,actual=m.surrogate(np.log(.5*ratio),np.log(np.full(4,.5)),adv,.2)
    assert_allclose(actual,ratio)
    assert_allclose(loss,-np.mean([2.4,1.4,-2.6,-1.6]))
    assert_allclose(dlogp,[0,-1.4/4,2.6/4,0])


@pytest.mark.numerical
@pytest.mark.parametrize('ratios',[[1.1,.9],[1.4,.6],[.7,1.4]])
def test_finite_difference_clipped_actor_away_from_boundaries(rl,gradients,ratios):
    m=rl.load('proximal-policy-optimization');p=rl.initialize(2,2,np.random.default_rng(70),2)
    x=np.array([[.2,-.3],[.4,.1]]);a=np.array([0,1]);adv=np.array([.8,-.4])
    z=rl.forward(p,x)[0];old=rl.log_softmax(z)[np.arange(2),a]-np.log(ratios)
    _,g,_=m.loss_gradients(p,x,a,old,adv)
    def independent(q):
        z=np.tanh(x@q['W1']+q['b1'])@q['W2']+q['b2']
        log=z[np.arange(2),a]-np.logaddexp(z[:,0],z[:,1]);r=np.exp(log-old)
        return -np.mean(np.minimum(r*adv,np.clip(r,.8,1.2)*adv))
    gradients(independent,p,g)


@pytest.mark.numerical
def test_critic_finite_difference(rl,gradients):
    p=rl.initialize(2,1,np.random.default_rng(71),2);x=np.array([[.2,.1],[-.3,.5]]);t=np.array([.7,-.2])
    _,g=rl.value_loss(p,x,t)
    def independent(q):
        v=(np.tanh(x@q['W1']+q['b1'])@q['W2']+q['b2'])[:,0]
        return .5*np.mean((v-t)**2)
    gradients(independent,p,g)


def test_old_policy_snapshot_persists_across_epochs_minibatches(rl):
    m=rl.load('proximal-policy-optimization').PPO(seed=72)
    before=rl.copy(m.actor)
    m.train(iterations=1,max_steps=1,rollout_episodes=4,epochs=3,batch_size=2)
    assert m.updates_==6
    for k in before:assert_array_equal(m.old_actor_[k],before[k])
    z=np.tanh(m.rollout_observations_@before['W1']+before['b1'])@before['W2']+before['b2']
    expected=z[np.arange(4),m.rollout_actions_]-np.logaddexp(z[:,0],z[:,1])
    assert_allclose(m.old_log_probs_,expected)
    assert any(not np.array_equal(m.actor[k],before[k]) for k in before)


@pytest.mark.parametrize('seed',[73,74,75])
def test_seeded_bounded_ppo_training(rl,seed):
    cls=rl.load('proximal-policy-optimization').PPO
    one=cls(seed=seed).train(iterations=35,max_steps=1)
    two=cls(seed=seed).train(iterations=35,max_steps=1)
    for k in one.actor:assert_array_equal(one.actor[k],two.actor[k])
    assert rl.evaluate(one,rl.Bandit)['mean_return']==1
    assert np.exp(rl.log_softmax(rl.forward(one.actor,[[1.]])[0]))[0,1]>.95


def test_invalid_surrogate_inputs(rl):
    m=rl.load('proximal-policy-optimization')
    for args in [([.1],[-1],[1],.2),([-1],[-1],[1],0),([-1],[-1],[np.nan],.2),([],[],[],.2)]:
        with pytest.raises(ValueError):m.surrogate(*args)
