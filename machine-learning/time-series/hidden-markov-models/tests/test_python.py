from itertools import product
import numpy as np
from numpy.testing import assert_allclose
import pytest
pytestmark=pytest.mark.ml

PI=np.array([.6,.4]);A=np.array([[.7,.3],[.2,.8]]);B=np.array([[.8,.2],[.3,.7]])

def model(b11):return b11.load('hidden-markov-models').CategoricalHMM(2,2,initial=PI,transition=A,emission=B)

def enumerate_joint(obs,pi=PI,a=A,b=B):
    paths=list(product(range(len(pi)),repeat=len(obs)));weights=[]
    for states in paths:
        value=pi[states[0]]*b[states[0],obs[0]]
        for t in range(1,len(obs)):value*=a[states[t-1],states[t]]*b[states[t],obs[t]]
        weights.append(value)
    return paths,np.array(weights)

@pytest.mark.oracle
@pytest.mark.parametrize('obs',[[0],[1],[0,1],[1,0],[0,0,1],[1,0,1,1]])
def test_exact_enumeration_forward_backward_gamma_xi_and_viterbi(b11,obs):
    m=model(b11);paths,weights=enumerate_joint(obs);total=weights.sum();posterior=m.infer(obs)
    assert_allclose(m.score(obs),np.log(total),atol=1e-14)
    assert_allclose(np.exp(posterior['log_forward'][-1]).sum(),total,atol=1e-14)
    assert_allclose(np.sum(PI*B[:,obs[0]]*np.exp(posterior['log_backward'][0])),total,atol=1e-14)
    gamma=np.zeros((len(obs),2));xi=np.zeros((len(obs)-1,2,2))
    for path,w in zip(paths,weights/total):
        for t,state in enumerate(path):gamma[t,state]+=w
        for t in range(len(obs)-1):xi[t,path[t],path[t+1]]+=w
    assert_allclose(posterior['gamma'],gamma,atol=1e-14)
    assert_allclose(posterior['xi'],xi,atol=1e-14)
    assert_allclose(gamma.sum(axis=1),1,atol=1e-14)
    if len(obs)>1:
        assert_allclose(xi.sum(axis=2),gamma[:-1],atol=1e-14)
        assert_allclose(xi.sum(axis=1),gamma[1:],atol=1e-14)
    best,value=m.decode(obs);reference=int(np.argmax(weights))
    assert tuple(best)==paths[reference]
    assert_allclose(value,np.log(weights[reference]),atol=1e-14)

@pytest.mark.oracle
def test_one_baum_welch_update_matches_exhaustive_expected_counts(b11):
    sequences=[[0,1,1],[1,0,1,0]];first=np.zeros(2);trans=np.zeros((2,2));emit=np.zeros((2,2))
    for obs in sequences:
        paths,weights=enumerate_joint(obs)
        for path,w in zip(paths,weights/weights.sum()):
            first[path[0]]+=w
            for t,state in enumerate(path):emit[state,obs[t]]+=w
            for t in range(len(obs)-1):trans[path[t],path[t+1]]+=w
    m=model(b11).fit(sequences,max_iter=1,tolerance=1e-12)
    assert_allclose(m.initial_,first/first.sum(),atol=2e-15)
    assert_allclose(m.transition_,trans/trans.sum(axis=1,keepdims=True),atol=2e-15)
    assert_allclose(m.emission_,emit/emit.sum(axis=1,keepdims=True),atol=2e-15)
    assert len(m.log_likelihood_history_)==2
    assert_allclose(m.log_likelihood_history_[0],sum(np.log(enumerate_joint(obs)[1].sum()) for obs in sequences),atol=1e-14)

@pytest.mark.oracle
def test_singleton_sequences_never_create_boundary_transitions(b11):
    m=model(b11);before=m.transition_.copy();m.fit([[0],[1]],max_iter=1)
    assert_allclose(m.transition_,before,atol=0,rtol=0)

@pytest.mark.numerical
def test_long_tiny_probability_sequence_remains_finite_in_log_space(b11):
    cls=b11.load('hidden-markov-models').CategoricalHMM
    m=cls(1,2,initial=[1.],transition=[[1.]],emission=[[1e-200,1-1e-200]])
    obs=np.zeros(2000,dtype=int);score=m.score(obs)
    assert np.isfinite(score) and score < -1e5
    assert_allclose(score,len(obs)*np.log(1e-200),rtol=1e-12)
    posterior=m.infer(obs);assert_allclose(posterior['gamma'],1);assert_allclose(posterior['xi'],1)
    path,value=m.decode(obs);assert_allclose(path,0);assert_allclose(value,score)

@pytest.mark.numerical
def test_impossible_sequence_status_and_failed_training_atomicity(b11):
    module=b11.load('hidden-markov-models');m=module.CategoricalHMM(1,2,initial=[1.],transition=[[1.]],emission=[[1.,0.]])
    assert m.score([1])==-np.inf
    for call in (m.infer,m.decode):
        with pytest.raises(module.ImpossibleSequenceError):call([1])
    before=[m.initial_.copy(),m.transition_.copy(),m.emission_.copy()]
    with pytest.raises(module.ImpossibleSequenceError):m.fit([[1]])
    for expected,actual in zip(before,[m.initial_,m.transition_,m.emission_]):assert_allclose(actual,expected,rtol=0,atol=0)

@pytest.mark.oracle
def test_unreachable_state_rows_are_retained_not_arbitrarily_replaced(b11):
    cls=b11.load('hidden-markov-models').CategoricalHMM
    m=cls(2,2,initial=[1.,0.],transition=[[1.,0.],[.4,.6]],emission=[[.5,.5],[.1,.9]])
    p=m.infer([0,1,1]);assert_allclose(p['gamma'][:,1],0)
    m.fit([[0,1,1]],max_iter=2)
    assert_allclose(m.transition_[1],[.4,.6],atol=0,rtol=0);assert_allclose(m.emission_[1],[.1,.9],atol=0,rtol=0)

@pytest.mark.parametrize('seed',[21,22,23])
def test_seeded_multisequence_em_monotonicity_reproducibility_and_budget(b11,seed):
    rng=np.random.default_rng(seed);sequences=[]
    for length in (35,40):
        state=int(rng.choice(2,p=PI));obs=[]
        for t in range(length):obs.append(int(rng.choice(2,p=B[state])));state=int(rng.choice(2,p=A[state]))
        sequences.append(obs)
    cls=b11.load('hidden-markov-models').CategoricalHMM
    a=cls(2,2,random_state=seed).fit(sequences,max_iter=12,tolerance=1e-10)
    b=cls(2,2,random_state=seed).fit(sequences,max_iter=12,tolerance=1e-10)
    assert np.all(np.diff(a.log_likelihood_history_)>=-1e-9)
    assert a.log_likelihood_history_[-1]>=a.log_likelihood_history_[0]
    for part in ('initial_','transition_','emission_','log_likelihood_history_'):assert_allclose(getattr(a,part),getattr(b,part),atol=0,rtol=0)
    assert_allclose(a.initial_.sum(),1);assert_allclose(a.transition_.sum(axis=1),1);assert_allclose(a.emission_.sum(axis=1),1)
    one=cls(2,2,random_state=seed).fit(sequences,max_iter=1,tolerance=1e-12)
    assert not one.converged_ and one.status_=='iteration-budget'


def test_one_state_one_symbol_exact_convergence_and_ties(b11):
    cls=b11.load('hidden-markov-models').CategoricalHMM;m=cls(1,1).fit([[0,0,0]])
    assert m.converged_ and m.score([0,0])==0
    uniform=cls(2,1,initial=[.5,.5],transition=[[.5,.5],[.5,.5]],emission=[[1.],[1.]])
    assert_allclose(uniform.decode([0,0,0])[0],[0,0,0])

@pytest.mark.parametrize('kwargs',[dict(n_states=0,n_symbols=2),dict(n_states=9,n_symbols=2),dict(n_states=True,n_symbols=2),dict(n_states=2,n_symbols=0),dict(n_states=2,n_symbols=17),dict(n_states=2,n_symbols=2,random_state=-1),dict(n_states=2,n_symbols=2,initial=[.5,.5])])
def test_invalid_model_sizes_seeds_partial_parameters(b11,kwargs):
    with pytest.raises(ValueError):b11.load('hidden-markov-models').CategoricalHMM(**kwargs)

@pytest.mark.parametrize('field,bad',[('initial',[.2,.2]),('initial',[1.1,-.1]),('initial',[np.nan,.4]),('transition',[[1,0],[0,0]]),('transition',[[1,0]]),('emission',[[.5,.5],[np.inf,0]]),('emission',[[True,False],[True,False]])])
def test_invalid_probability_models(b11,field,bad):
    kwargs=dict(initial=PI,transition=A,emission=B);kwargs[field]=bad
    with pytest.raises(ValueError):b11.load('hidden-markov-models').CategoricalHMM(2,2,**kwargs)

@pytest.mark.parametrize('observations',[[],[2],[-1],[True],[0.],[np.nan],[[0,1]],np.zeros(2049,dtype=int)])
def test_invalid_observation_sequences(b11,observations):
    m=model(b11)
    for method in (m.score,m.forward,m.backward,m.infer,m.decode):
        with pytest.raises(ValueError):method(observations)


def test_input_ownership_and_invalid_training_work_bounds(b11):
    pi=PI.copy();a=A.copy();b=B.copy();m=b11.load('hidden-markov-models').CategoricalHMM(2,2,initial=pi,transition=a,emission=b);before=m.score([0,1]);pi[:]=0;a[:]=0;b[:]=0
    assert m.score([0,1])==before
    for data,kwargs in [([],{}),([0,1],{}),([[0]]*17,{}),([np.zeros(2048,dtype=int)]*3,{}),([[0,1]],dict(max_iter=0)),([[0,1]],dict(tolerance=np.nan))]:
        with pytest.raises(ValueError):m.fit(data,**kwargs)
    large=b11.load('hidden-markov-models').CategoricalHMM(8,2)
    with pytest.raises(ValueError):large.fit([np.zeros(2048,dtype=int)]*2,max_iter=200)
