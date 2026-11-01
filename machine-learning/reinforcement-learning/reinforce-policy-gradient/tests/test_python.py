import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


@pytest.mark.oracle
def test_returns_logsoftmax_and_analytic_logit_gradient(rl):
    assert_allclose(rl.returns([1,2,3],.5),[2.75,3.5,3])
    m=rl.load('reinforce-policy-gradient');p=rl.initialize(1,2,np.random.default_rng(10),2)
    p['W2'][:]=0;p['b2'][:]=0
    loss,g=m.loss_gradients(p,[[1.]],np.array([1]),[2.])
    assert_allclose(loss,2*np.log(2));assert_allclose(g['b2'],[1,-1])
    logs=rl.log_softmax([[1e6,-1e6]])
    assert np.isfinite(logs).all();assert_allclose(np.exp(logs).sum(),1)


@pytest.mark.numerical
def test_finite_difference_discounted_episodic_policy_gradient(rl,gradients):
    m=rl.load('reinforce-policy-gradient');p=rl.initialize(2,2,np.random.default_rng(41),3)
    x=np.array([[.3,.1],[-.4,.2]]);a=np.array([0,1]);ret=np.array([1.2,.7])
    _,g=m.loss_gradients(p,x,a,ret,.8)
    def independent(q):
        logits=np.tanh(x@q['W1']+q['b1'])@q['W2']+q['b2']
        normalizer=np.logaddexp(logits[:,0],logits[:,1])
        return -np.sum((logits[np.arange(2),a]-normalizer)*ret*np.array([1,.8]))
    gradients(independent,p,g)


@pytest.mark.parametrize('seed',[41,42,43])
def test_seeded_training_sampling_and_separate_evaluation(rl,seed):
    cls=rl.load('reinforce-policy-gradient').REINFORCE
    models=[cls(seed=seed).train(rl.Bandit(),episodes=200,max_steps=1) for _ in range(2)]
    for k in models[0].actor:assert_array_equal(models[0].actor[k],models[1].actor[k])
    assert rl.evaluate(models[0],rl.Bandit)['mean_return']==1
    prob=np.exp(rl.log_softmax(rl.forward(models[0].actor,[[1.]])[0]))[0,1]
    assert prob>.95
    assert all(a in (0,1) for a in [models[0].action([1.]) for _ in range(20)])


def test_requires_complete_terminal_trajectories(rl):
    class Cut(rl.Bandit):
        def step(self,a):return np.ones(1),1.,False,True,{}
    m=rl.load('reinforce-policy-gradient').REINFORCE()
    with pytest.raises(ValueError,match='complete terminal'):m.train(Cut(),episodes=1)
    with pytest.raises(ValueError):rl.returns([],.9)
    with pytest.raises(ValueError):rl.policy_loss(m.actor,[[1.]],np.array([-1]),[1.])


def test_sampling_uniform_and_global_rng_unchanged(rl):
    m=rl.load('reinforce-policy-gradient').REINFORCE(seed=2)
    m.actor['W2'][:]=0;m.actor['b2'][:]=0
    before=np.random.get_state()
    counts=sum(m.action([1.]) for _ in range(1000))
    after=np.random.get_state()
    assert 400<counts<600
    assert_array_equal(before[1],after[1])
