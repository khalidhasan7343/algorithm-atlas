import itertools,math
import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


@pytest.mark.oracle
@pytest.mark.parametrize('delta,T,expected',[(0.,1.,1.),(-2.,.1,1.),(math.log(2),1.,.5),(2.,2.,math.exp(-1))])
def test_exact_metropolis_probability(b10,delta,T,expected):
    assert_allclose(b10.load('simulated-annealing').metropolis_probability(delta,T),expected,atol=1e-15)


@pytest.mark.oracle
def test_finite_chain_transition_normalization_and_gibbs_detailed_balance(b10):
    states=list(itertools.product((0,1),repeat=2));weights=np.array([1.,2.]);values=np.array([x@weights for x in np.array(states)])
    transition=np.zeros((4,4));m=b10.load('simulated-annealing')
    for i,state in enumerate(states):
        for bit in range(2):
            candidate=list(state);candidate[bit]=1-candidate[bit];j=states.index(tuple(candidate));delta=values[j]-values[i]
            expected=1. if delta<=0 else math.exp(-float(delta))
            actual=m.metropolis_probability(float(delta),1.);assert_allclose(actual,expected)
            transition[i,j]+=.5*actual
        transition[i,i]=1-transition[i].sum()
    gibbs=np.exp(-values);gibbs/=gibbs.sum()
    assert_allclose(transition.sum(1),1.);assert np.all(transition>=0)
    assert_allclose(gibbs@transition,gibbs,atol=1e-15)
    assert_allclose(gibbs[:,None]*transition,(gibbs[:,None]*transition).T,atol=1e-15)


@pytest.mark.oracle
def test_exact_seeded_metropolis_chain_current_and_best(b10):
    seed=22031;weights=np.array([1.,2.,-3.]);x=np.array([0,1,1]);before=x.copy();rng=np.random.default_rng(seed)
    current=x.copy();value=float(current@weights);best=value;path=[current.copy()];values=[value];history=[value];flags=[]
    for _ in range(20):
        candidate=current.copy();i=int(rng.integers(3));candidate[i]=1-candidate[i]
        new=float(candidate@weights);delta=new-value;accept=delta<=0
        if not accept:
            u=float(rng.random());accept=u==0 or math.log(u)<-delta/3.
        if accept:current=candidate;value=new;best=min(best,value)
        flags.append(accept);path.append(current.copy());values.append(value);history.append(best)
    r=b10.load('simulated-annealing').SimulatedAnnealing(initial_temperature=3,cooling=1,random_state=seed).minimize(lambda z:float(z@weights),x,max_iter=20)
    assert_array_equal(r.diagnostics['trajectory'],path);assert_array_equal(r.diagnostics['accepted'],flags)
    assert_array_equal(r.diagnostics['current_history'],values);assert_array_equal(r.history,history);assert_array_equal(x,before)
    assert np.any(np.diff(values)>0) and np.all(np.diff(r.history)<=0)
    assert r.fun==min(history) and r.nfev==21 and r.n_iter==20 and not r.converged


def test_temperature_floor_and_zero_step_target(b10):
    cls=b10.load('simulated-annealing').SimulatedAnnealing
    r=cls(initial_temperature=1,cooling=.5,minimum_temperature=.25).minimize(lambda x:float(x.sum()),[0,0],max_iter=20)
    assert r.n_iter==2 and r.nfev==3 and r.status=='temperature-floor' and not r.converged
    assert_allclose(r.diagnostics['temperatures'],[1.,.5])
    r=cls().minimize(lambda x:float(x.sum()),[0,0],target_value=0.)
    assert r.converged and r.status=='target-reached' and r.n_iter==0 and r.nfev==1
    r=cls(initial_temperature=1,minimum_temperature=1).minimize(lambda x:0.,[0])
    assert not r.converged and r.status=='temperature-floor' and r.n_iter==0 and r.nfev==1


@pytest.mark.numerical
def test_extreme_worsening_move_uses_finite_log_acceptance(b10):
    m=b10.load('simulated-annealing')
    assert m.metropolis_probability(1e100,1e-12)==0.
    r=m.SimulatedAnnealing(initial_temperature=1e-8).minimize(lambda x:float(x[0])*1e100,[0],max_iter=1)
    assert_array_equal(r.x,[0]);assert not r.diagnostics['accepted'][0]


@pytest.mark.parametrize('seed',[21,22,23])
def test_seeded_repeated_search_and_exhaustive_best_bound(b10,seed):
    target=np.array([1,0,1,1]);f=lambda x:int(np.count_nonzero(x!=target));oracle=min(f(np.array(x)) for x in itertools.product((0,1),repeat=4))
    solver=b10.load('simulated-annealing').SimulatedAnnealing(random_state=seed)
    a=solver.minimize(f,[0,1,0,0],max_iter=100);b=solver.minimize(f,[0,1,0,0],max_iter=100)
    assert_array_equal(a.x,b.x);assert_array_equal(a.diagnostics['trajectory'],b.diagnostics['trajectory'])
    assert oracle<=a.fun<=f(np.array([0,1,0,0])) and np.isin(a.x,[0,1]).all()
    assert a.fun==f(a.x) and np.all(np.diff(a.history)<=0)


@pytest.mark.parametrize('settings',[dict(initial_temperature=0),dict(initial_temperature=True),dict(cooling=0),dict(cooling=1.1),
    dict(minimum_temperature=0),dict(initial_temperature=.1,minimum_temperature=1),dict(random_state=-1)])
def test_invalid_settings(b10,settings):
    with pytest.raises(ValueError):b10.load('simulated-annealing').SimulatedAnnealing(**settings)


@pytest.mark.parametrize('bits',[[],[[0,1]],[0.,1.],[-1,0],[0,2],['0','1'],np.zeros(33,dtype=int)])
def test_invalid_binary_initial_state(b10,bits):
    with pytest.raises(ValueError):b10.load('simulated-annealing').SimulatedAnnealing().minimize(lambda x:0.,bits)


def test_callback_failure_and_invalid_temperature_probability(b10):
    m=b10.load('simulated-annealing');x=np.array([True,False]);before=x.copy()
    with pytest.raises(b10.NumericalError):m.SimulatedAnnealing().minimize(lambda x:float('inf'),x)
    assert_array_equal(x,before)
    with pytest.raises(ValueError):m.metropolis_probability(1.,0.)
    with pytest.raises(ValueError):m.SimulatedAnnealing().minimize(lambda x:0.,[0],max_iter=10001)
