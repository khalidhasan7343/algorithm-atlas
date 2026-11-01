import numpy as np
from numpy.testing import assert_array_equal
import pytest
pytestmark=pytest.mark.ml


def run(b10,topic,fun):
    if topic=='genetic-algorithms':return b10.load(topic).GeneticAlgorithm(population_size=4).minimize(fun,3,max_generations=2)
    return b10.load(topic).SimulatedAnnealing().minimize(fun,[0,1,0],max_iter=3)


@pytest.mark.parametrize('topic',['genetic-algorithms','simulated-annealing'])
def test_private_rng_and_result_ownership(b10,topic):
    state=np.random.get_state();a=run(b10,topic,lambda x:float(x.sum()))
    after=np.random.get_state();assert state[0]==after[0] and state[2:]==after[2:]
    assert_array_equal(state[1],after[1])
    expected=a.x.copy();a.x[:]=7;a.history[:]=7
    b=run(b10,topic,lambda x:float(x.sum()));assert_array_equal(b.x,expected)


@pytest.mark.parametrize('topic',['genetic-algorithms','simulated-annealing'])
@pytest.mark.parametrize('value',[True,np.array([1.]),complex(1,0)])
def test_objective_must_be_real_scalar(b10,topic,value):
    with pytest.raises(ValueError):run(b10,topic,lambda x:value)


@pytest.mark.parametrize('topic',['genetic-algorithms','simulated-annealing'])
def test_callback_cannot_mutate_candidate(b10,topic):
    def invalid(x):x[0]=9;return 0.
    with pytest.raises(ValueError):run(b10,topic,invalid)
