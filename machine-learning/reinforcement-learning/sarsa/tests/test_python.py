import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=[pytest.mark.ml,pytest.mark.oracle]


def test_on_policy_target_differs_from_q_learning(rl):
    q=rl.load('q-learning').QLearning(3,2,alpha=.5,gamma=.9)
    s=rl.load('sarsa').SARSA(3,2,alpha=.5,gamma=.9)
    q.q[1]=s.q[1]=[3,10]
    assert q.update(0,1,1,1)==5.
    assert s.update(0,1,1,1,0)==1.85
    assert s.update(0,0,1,1,None,True)==.5


def test_seeded_on_policy_learning(rl):
    models=[rl.load('sarsa').SARSA(3,2,epsilon=.1,seed=21).train(rl.Chain(),episodes=600) for _ in range(2)]
    assert_array_equal(models[0].q,models[1].q)
    assert_array_equal(models[0].policy()[:2],[1,1])
    assert np.mean(models[0].returns_[-100:])>.95
    # Constant exploration makes on-policy values differ from optimal-control values.
    assert models[0].q[0,1]<.9


def test_next_action_validation_and_zero_parameters(rl):
    m=rl.load('sarsa').SARSA(3,2,alpha=0,gamma=0)
    assert m.update(0,0,5,1,1)==0
    for a in (None,-1,2,True):
        with pytest.raises(ValueError):m.update(0,0,1,1,a)
    m.alpha=1
    assert m.update(0,0,5,1,1)==5


def test_actual_sampled_next_action_is_reused(rl):
    class Recording(rl.Chain):
        def step(self,a):
            seen.append(a)
            return super().step(a)
    m=rl.load('sarsa').SARSA(3,2,epsilon=1,seed=3)
    original=m.action;sampled=[];seen=[]
    def action(s,explore=True):
        a=original(s,explore);sampled.append(a);return a
    m.action=action
    m.train(Recording(),episodes=1,max_steps=8)
    assert seen==sampled[:len(seen)]


def test_truncation_uses_next_action(rl):
    m=rl.load('sarsa').SARSA(3,2,alpha=1,epsilon=0)
    m.q[0]=[0,1];m.q[1]=[2,3]
    m.train(rl.Chain(horizon=1),episodes=1,max_steps=1)
    assert_allclose(m.q[0,1],2.7)


def test_randomized_sarsa_oracle(rl):
    rng=np.random.default_rng(210)
    for _ in range(50):
        m=rl.load('sarsa').SARSA(3,2,alpha=.6,gamma=.8)
        m.q[:]=rng.normal(size=(3,2));old=m.q.copy();r=float(rng.normal());a=int(rng.integers(2))
        assert_allclose(m.update(0,1,r,1,a),old[0,1]+.6*(r+.8*old[1,a]-old[0,1]),atol=1e-14)
