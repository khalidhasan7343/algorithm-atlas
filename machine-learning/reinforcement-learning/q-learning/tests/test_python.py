import importlib.util
from pathlib import Path
import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest

pytestmark = [pytest.mark.ml, pytest.mark.oracle]


@pytest.mark.parametrize('alpha,gamma,terminal,expected', [(.5,.9,False,5.),(.5,.9,True,.5),(0.,.9,False,0.),(.5,0.,False,.5)])
def test_bellman_update(rl, alpha, gamma, terminal, expected):
    model = rl.load('q-learning').QLearning(3,2,alpha=alpha,gamma=gamma)
    model.q[1] = [3,10]
    assert model.update(0,1,1,1,terminal) == expected


def test_exact_mdp_bellman_oracle_and_seeded_training(rl):
    path = Path(__file__).resolve().parents[2]/'tests/oracles.py'
    spec=importlib.util.spec_from_file_location('b8_test_oracle',path)
    oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
    p,r,term=oracle.chain_model();v,q=oracle.value_iteration(p,r,term,.9)
    assert_allclose(v,[.9,1,0])
    models=[rl.load('q-learning').QLearning(3,2,alpha=.2,gamma=.9,epsilon=.3,seed=seed).train(rl.Chain(),episodes=1000) for seed in (11,12,13)]
    for model in models:
        assert_allclose(model.q[:2],q[:2],atol=2e-4)
        assert_array_equal(model.policy()[:2],[1,1])
        residual=np.max(abs(model.q[:2]-np.sum(p*(r+.9*model.q.max(1)[None,None,:]*(~term)[None,None,:]),2)[:2]))
        assert residual<2e-4
    again=rl.load('q-learning').QLearning(3,2,alpha=.2,gamma=.9,epsilon=.3,seed=11).train(rl.Chain(),episodes=1000)
    assert_array_equal(again.q,models[0].q)


def test_epsilon_exploration_and_ties(rl):
    model=rl.load('q-learning').QLearning(2,2,epsilon=0,seed=6)
    assert model.action(0)==0
    model.epsilon=1
    picks=[model.action(0) for _ in range(1000)]
    assert 400<sum(picks)<600
    model.q[0]=[1,2]
    assert model.action(0,False)==1


@pytest.mark.parametrize('s,a,r,next_s,term', [(-1,0,0,1,False),(0,2,0,1,False),(0,0,np.nan,1,False),(0,0,0,3,False),(True,0,0,1,False),(0,0,0,1,1)])
def test_invalid_transition(rl,s,a,r,next_s,term):
    model=rl.load('q-learning').QLearning(3,2)
    with pytest.raises(ValueError):model.update(s,a,r,next_s,term)


def test_truncation_bootstrap_not_terminal(rl):
    model=rl.load('q-learning').QLearning(3,2,alpha=1,epsilon=0)
    model.q[0]=[0,1];model.q[1]=[2,3]
    model.train(rl.Chain(horizon=1),episodes=1,max_steps=1)
    assert model.q[0,1]==2.7


def test_randomized_analytical_bellman(rl):
    rng=np.random.default_rng(20)
    for _ in range(50):
        model=rl.load('q-learning').QLearning(3,2,alpha=.3,gamma=.7)
        model.q[:]=rng.normal(size=(3,2));old=model.q.copy();r=float(rng.normal())
        expected=old[0,1]+.3*(r+.7*max(old[1])-old[0,1])
        assert_allclose(model.update(0,1,r,1),expected,atol=1e-14)
