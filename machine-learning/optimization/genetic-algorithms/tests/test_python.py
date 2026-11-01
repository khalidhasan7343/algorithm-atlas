import itertools
import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


@pytest.mark.oracle
def test_tournament_probabilities_by_exhaustive_subsets_and_ties(b10):
    m=b10.load('genetic-algorithms');fitness=np.array([-2.,0,3,5]);wins=np.zeros(4)
    for contestants in itertools.combinations(range(4),2):wins[m.tournament_selection(fitness,contestants)]+=1
    assert_allclose(wins/wins.sum(),[.5,1/3,1/6,0.])
    assert m.tournament_selection([3.,1,1,0],[2,1])==1


@pytest.mark.oracle
def test_uniform_crossover_and_bit_mutation_exact_operators(b10):
    m=b10.load('genetic-algorithms');a=np.array([0,0,0]);b=np.array([1,1,1])
    first,second=m.uniform_crossover(a,b,[True,False,True])
    assert_array_equal(first,[0,1,0]);assert_array_equal(second,[1,0,1])
    assert_array_equal(m.bit_flip_mutation(first,[True,True,True]),[1,0,1])
    assert_array_equal(m.bit_flip_mutation(first,[False,False,False]),first)
    assert_array_equal(a,[0,0,0]);assert_array_equal(b,[1,1,1])


@pytest.mark.oracle
def test_one_generation_independent_selection_variation_and_evaluation_counts(b10):
    P=np.array([[0,0,0],[1,0,1],[1,1,0],[0,1,1]]);before=P.copy();weights=np.array([1.,-2,3])
    fitness=P@weights;seed=22030;rng=np.random.default_rng(seed)
    expected=[P[int(np.argmin(fitness))].copy()]
    while len(expected)<4:
        parents=[]
        for _ in range(2):
            choices=rng.permutation(4)[:2];winner=min(choices,key=lambda i:(fitness[i],int(i)))
            parents.append(P[winner])
        rng.random()  # The crossover Bernoulli draw,with probability1.
        mask=rng.random(3)<.5
        children=([parents[0][j] if mask[j] else parents[1][j] for j in range(3)],
                  [parents[1][j] if mask[j] else parents[0][j] for j in range(3)])
        for child in children:
            if len(expected)==4:break
            changes=rng.random(3)<1.
            expected.append(np.array([1-bit if changes[j] else bit for j,bit in enumerate(child)]))
    solver=b10.load('genetic-algorithms').GeneticAlgorithm(population_size=4,crossover_rate=1,mutation_rate=1,random_state=seed)
    result=solver.minimize(lambda x:float(x@weights),3,initial_population=P,max_generations=1)
    assert_array_equal(result.diagnostics['population'],expected);assert_array_equal(P,before)
    assert_allclose(result.diagnostics['fitness'],np.array(expected)@weights)
    assert result.nfev==7 and result.n_iter==1 and not result.converged
    assert result.history[-1]<=result.history[0]


@pytest.mark.oracle
def test_exhaustive_tiny_domain_oracle_and_initial_target(b10):
    P=np.array(list(itertools.product((0,1),repeat=4)));target=np.array([1,0,1,1])
    f=lambda x:int(np.count_nonzero(x!=target));oracle=min(f(x) for x in P)
    r=b10.load('genetic-algorithms').GeneticAlgorithm(population_size=16).minimize(f,4,initial_population=P,target_value=oracle)
    assert r.converged and r.status=='target-reached' and r.n_iter==0 and r.nfev==16
    assert r.fun==oracle;assert_array_equal(r.x,target)


@pytest.mark.parametrize('seed',[21,22,23])
def test_seeded_search_binary_population_elitism_and_repeated_calls(b10,seed):
    target=np.array([1,0,1,1,0,0,1,0]);f=lambda x:int(np.count_nonzero(x!=target))
    solver=b10.load('genetic-algorithms').GeneticAlgorithm(population_size=12,mutation_rate=.1,random_state=seed)
    state=np.random.get_state();a=solver.minimize(f,8,max_generations=30);b=solver.minimize(f,8,max_generations=30)
    assert_array_equal(a.x,b.x);assert_array_equal(a.history,b.history);assert_array_equal(np.random.get_state()[1],state[1])
    assert a.diagnostics['population'].shape==(12,8)
    assert np.isin(a.diagnostics['population'],[0,1]).all() and np.all(np.diff(a.history)<=0)
    assert a.fun==f(a.x) and a.fun<=a.history[0] and a.nfev==12+30*11
    assert not a.converged and a.status=='generation-budget'


def test_stagnation_is_not_a_global_convergence_claim(b10):
    r=b10.load('genetic-algorithms').GeneticAlgorithm(population_size=4).minimize(lambda x:0.,3,max_generations=20,stagnation_generations=2)
    assert r.n_iter==2 and r.nfev==10 and not r.converged and r.status=='stagnation'


@pytest.mark.oracle
def test_zero_variation_cannot_invent_new_genotypes(b10):
    population=np.array([[0,0,0],[1,0,1],[1,1,0],[0,1,1]])
    m=b10.load('genetic-algorithms').GeneticAlgorithm(population_size=4,crossover_rate=0,mutation_rate=0)
    r=m.minimize(lambda x:float(x@[1.,-2.,3.]),3,initial_population=population,max_generations=3)
    assert all(any(np.array_equal(row,old) for old in population) for row in r.diagnostics['population'])
    assert_allclose(r.history,r.history[0]);assert r.nfev==13 and not r.converged


@pytest.mark.parametrize('settings',[dict(population_size=1),dict(population_size=65),dict(tournament_size=1),dict(tournament_size=17),
    dict(elite_count=0),dict(elite_count=16),dict(crossover_rate=-1),dict(mutation_rate=1.1),dict(mutation_rate=True),dict(random_state=-1)])
def test_invalid_settings(b10,settings):
    with pytest.raises(ValueError):b10.load('genetic-algorithms').GeneticAlgorithm(**settings)


@pytest.mark.parametrize('population',[[],[[0,1]],[[0.,1.],[1.,0.]],[[0,2],[0,1]],[[True],[False]]])
def test_invalid_initial_populations(b10,population):
    with pytest.raises(ValueError):b10.load('genetic-algorithms').GeneticAlgorithm(population_size=2).minimize(lambda x:0.,2,initial_population=population)


def test_resource_budget_rejects_before_fitness_evaluation(b10):
    calls=[]
    with pytest.raises(ValueError):b10.load('genetic-algorithms').GeneticAlgorithm(population_size=64).minimize(lambda x:calls.append(1) or 0.,32,max_generations=1000)
    assert calls==[]


def test_nonfinite_fitness_and_invalid_helpers(b10):
    m=b10.load('genetic-algorithms')
    with pytest.raises(b10.NumericalError):m.GeneticAlgorithm().minimize(lambda x:float('nan'),3)
    with pytest.raises(ValueError):m.tournament_selection([0.,1.],[0,0])
    with pytest.raises(ValueError):m.tournament_selection([0.,np.inf],[0,1])
    with pytest.raises(ValueError):m.uniform_crossover([0,1],[1,0],[1,0])
    with pytest.raises(ValueError):m.bit_flip_mutation([0,1],[True])
