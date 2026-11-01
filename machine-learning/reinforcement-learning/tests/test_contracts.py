"""Environment, resource, numerical, exploration and cross-algorithm contracts."""
import importlib.util
from pathlib import Path
import threading
import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest

pytestmark=pytest.mark.ml


@pytest.mark.parametrize('factory',['Chain','Bandit','Continuous'])
def test_environment_reset_terminal_observation_reward_and_post_done(rl,factory):
    env=getattr(rl,factory)()
    with pytest.raises(ValueError):env.step(np.array([0.]) if factory=='Continuous' else 1)
    first=env.reset(seed=101);second=env.reset(seed=101);assert_array_equal(first,second)
    if factory=='Chain':
        assert env.step(1)==(1,0.,False,False,{})
        result=env.step(1);assert result==(2,1.,True,False,{})
    elif factory=='Bandit':
        obs,r,t,cut,_=env.step(1);assert_array_equal(obs,[1.]);assert (r,t,cut)==(1.,True,False)
    else:
        obs,r,t,cut,_=env.step(np.array([first[0]/2]));assert r==0 and t and not cut
        assert obs.shape==(1,)
    with pytest.raises(ValueError):env.step(np.array([0.]) if factory=='Continuous' else 1)
    env.reset(seed=101)


def test_environment_time_limit_and_invalid_actions(rl):
    env=rl.Chain(horizon=1);env.reset();assert env.step(0)==(0,0.,False,True,{})
    for factory,bad in [(rl.Chain,-1),(rl.Bandit,2),(rl.Continuous,np.array([1.01])),(rl.Continuous,np.array([np.nan]))]:
        env=factory();env.reset(seed=2)
        with pytest.raises(ValueError):env.step(bad)


@pytest.mark.oracle
def test_stochastic_finite_mdp_seed_reset_and_exact_oracle(rl):
    spec=importlib.util.spec_from_file_location('b8_oracle_contract',Path(__file__).with_name('oracles.py'))
    oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
    p,r,terminal=oracle.chain_model();p[0,1]=[.5,.5,0]
    v,q=oracle.value_iteration(p,r,terminal,.9)
    assert_allclose(v,[.45/.55,1,0],atol=1e-11)
    assert_allclose(q.max(1),v,atol=1e-11)
    class Stochastic(rl.Chain):
        def reset(self,seed=None):
            self.rng=np.random.default_rng(seed);return super().reset(seed)
        def step(self,action):
            if not self.done and self.state==0 and action==1 and self.rng.random()<.5:
                return super().step(0)
            return super().step(action)
    env=Stochastic();sequences=[]
    for _ in range(2):
        env.reset(seed=3);rows=[]
        while not env.done:rows.append(env.step(1))
        sequences.append(rows)
    assert sequences[0]==sequences[1]
    m=rl.load('q-learning').QLearning(3,2,alpha=.05,epsilon=.2,seed=102).train(Stochastic(),episodes=1500,max_steps=16)
    assert_array_equal(m.policy()[:2],[1,1])
    assert np.mean(m.returns_[-100:])>.95


@pytest.mark.parametrize('topic,cls',[('deep-q-networks','DQN'),('reinforce-policy-gradient','REINFORCE'),('advantage-actor-critic','A2C'),('asynchronous-advantage-actor-critic','A3C'),('proximal-policy-optimization','PPO'),('deep-deterministic-policy-gradient','DDPG')])
@pytest.mark.parametrize('bad',[np.nan,np.inf,True,'1',complex(1,0)])
def test_nonfinite_or_nonreal_observations_rejected(rl,topic,cls,bad):
    model=getattr(rl.load(topic),cls)()
    with pytest.raises(ValueError):model.action([bad])


@pytest.mark.parametrize('topic,cls',[('q-learning','QLearning'),('sarsa','SARSA')])
@pytest.mark.parametrize('settings',[dict(alpha=-.1),dict(gamma=1.1),dict(epsilon=np.nan),dict(n_states=0),dict(n_actions=True),dict(seed=-1)])
def test_tabular_invalid_settings(rl,topic,cls,settings):
    args=dict(n_states=3,n_actions=2);args.update(settings)
    with pytest.raises(ValueError):getattr(rl.load(topic),cls)(**args)


@pytest.mark.parametrize('topic,cls',[('deep-q-networks','DQN'),('reinforce-policy-gradient','REINFORCE'),('advantage-actor-critic','A2C'),('asynchronous-advantage-actor-critic','A3C'),('proximal-policy-optimization','PPO'),('deep-deterministic-policy-gradient','DDPG')])
def test_invalid_learning_discount_dimension_and_nonfinite_model(rl,topic,cls):
    constructor=getattr(rl.load(topic),cls)
    for settings in [dict(learning_rate=0),dict(learning_rate=np.nan),dict(gamma=-.1),dict(gamma=1.1),dict(hidden=33),dict(inputs=0),dict(seed=True)]:
        with pytest.raises(ValueError):constructor(**settings)
    model=constructor();p=model.online if cls=='DQN' else model.actor;p['W1'][0,0]=np.nan
    with pytest.raises(ValueError):model.action([1.])


@pytest.mark.numerical
def test_gradient_norm_clipping_and_atomic_invalid_update(rl):
    p=dict(w=np.array([1.,2.]));g=dict(w=np.array([3.,4.]))
    rl.apply(p,g,.1,max_norm=1)
    assert_allclose(p['w'],[.94,1.92])
    before=rl.copy(p)
    with pytest.raises(ValueError):rl.apply(p,dict(w=np.array([np.nan,1.])),.1)
    assert_array_equal(p['w'],before['w'])
    with pytest.raises(ValueError):rl.apply(p,dict(w=np.ones(3)),.1)


@pytest.mark.numerical
def test_extreme_logits_empty_trajectories_and_invalid_flags(rl):
    assert_allclose(np.exp(rl.log_softmax([[1e6,1e6]])).sum(1),[1.])
    for values in ([],[np.nan],[np.inf]):
        with pytest.raises(ValueError):rl.returns(values,.9)
    for flags in ([0],[1],[np.nan],[]):
        with pytest.raises(ValueError):rl.flags(flags,1)


def test_all_training_resource_guards(rl):
    for topic,cls in [('q-learning','QLearning'),('sarsa','SARSA')]:
        model=getattr(rl.load(topic),cls)(3,2)
        with pytest.raises(ValueError):model.train(rl.Chain(),episodes=5001)
        with pytest.raises(ValueError):model.train(rl.Chain(),episodes=1000,max_steps=256)
    for topic,cls in [('deep-q-networks','DQN'),('reinforce-policy-gradient','REINFORCE'),('deep-deterministic-policy-gradient','DDPG')]:
        with pytest.raises(ValueError):getattr(rl.load(topic),cls)().train(rl.Bandit(),episodes=5001)
    with pytest.raises(ValueError):rl.load('advantage-actor-critic').A2C().train(iterations=5000,max_steps=256,envs=8)
    with pytest.raises(ValueError):rl.load('asynchronous-advantage-actor-critic').A3C().train(workers=9)
    with pytest.raises(ValueError):rl.load('proximal-policy-optimization').PPO().train(iterations=5000,epochs=32,max_steps=1)
    assert not any(t.name.startswith('atlas-a3c-') for t in threading.enumerate())


def test_vector_chain_multistep_neural_training_and_bootstrap(rl):
    class VectorChain(rl.Chain):
        observation_dim=3
        def reset(self,seed=None):return np.eye(3)[super().reset(seed)]
        def step(self,a):
            s,r,t,c,i=super().step(a);return np.eye(3)[s],r,t,c,i
    m=rl.load('deep-q-networks').DQN(inputs=3,seed=103,batch_size=8,epsilon=.3).train(VectorChain(),episodes=300,max_steps=16)
    assert rl.evaluate(m,VectorChain,episodes=20)['mean_return']==1
    assert len(m.replay.data)<=m.replay.capacity


@pytest.mark.numerical
def test_reinforce_variable_length_episodic_sum_no_implicit_length_scaling(rl):
    p=rl.initialize(1,2,np.random.default_rng(3),2)
    for v in p.values():v[:]=0
    m=rl.load('reinforce-policy-gradient')
    loss,g=m.loss_gradients(p,[[1.],[1.]],np.array([1,1]),[1.,1.],1.)
    assert_allclose(loss,2*np.log(2));assert_allclose(g['b2'],[1.,-1.])
