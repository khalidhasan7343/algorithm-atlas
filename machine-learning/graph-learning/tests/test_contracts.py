import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest

pytestmark=pytest.mark.ml


@pytest.mark.parametrize('value',[True,1.,-1,2**40])
@pytest.mark.parametrize('topic',['node2vec','graph-convolutional-networks'])
def test_invalid_rng_seed_boundaries(b9,topic,value):
    cls=b9.load(topic).Node2Vec if topic=='node2vec' else b9.load(topic).GCNClassifier
    with pytest.raises(ValueError):cls(random_state=value)


@pytest.mark.parametrize('value',[10**1000,complex(1,0),np.array([.5]),'0.5'])
def test_non_scalar_or_unrepresentable_real_hyperparameters(b9,value):
    with pytest.raises(ValueError):b9.load('pagerank').PageRank(damping=value)
    with pytest.raises(ValueError):b9.load('node2vec').Node2Vec(p=value)
    with pytest.raises(ValueError):b9.load('graph-convolutional-networks').GCNClassifier(l2=value)


def test_all_algorithms_preserve_global_rng_and_readonly_inputs(b9):
    A=np.array([[0.,1],[1,0]]);A.flags.writeable=False
    X=np.array([[1.,0],[0,1]]);X.flags.writeable=False
    state=np.random.get_state()
    b9.load('pagerank').PageRank().fit(A)
    b9.load('node2vec').Node2Vec(epochs=2).fit(A)
    b9.load('graph-convolutional-networks').GCNClassifier(epochs=2).fit(A,X,[0,1])
    after=np.random.get_state()
    assert after[0]==state[0] and after[2:]==state[2:]
    assert_array_equal(after[1],state[1]);assert_array_equal(A,[[0,1],[1,0]])


def test_node2vec_budget_rejected_before_walk_generation(b9,monkeypatch):
    model=b9.load('node2vec').Node2Vec(num_walks=20,walk_length=64,window_size=8)
    def unexpected(*args):raise AssertionError('walks must not be allocated before budget check')
    monkeypatch.setattr(model,'_walks',unexpected)
    with pytest.raises(ValueError):model.fit(np.ones((32,32))-np.eye(32))


@pytest.mark.oracle
def test_transition_distribution_node_permutation_equivariance(b9):
    A=np.array([[0.,2,1,0],[2,0,3,4],[1,3,0,0],[0,4,0,0]])
    order=np.array([3,0,2,1]);inverse=np.argsort(order)
    model=b9.load('node2vec').Node2Vec(p=.25,q=3.)
    original=model.transition_probabilities(A,1,0)
    permuted=model.transition_probabilities(A[np.ix_(order,order)],int(inverse[1]),int(inverse[0]))
    assert_allclose(permuted,original[order],atol=1e-15)


@pytest.mark.numerical
def test_maximum_graph_weights_and_near_one_damping(b9):
    model=b9.load('pagerank').PageRank(damping=np.nextafter(1.,0.),max_iter=1)
    result=model.fit_transform(np.full((32,32),1e6))
    assert_allclose(result,np.full(32,1/32),atol=1e-15)
    assert np.isfinite(model.error_bound_) and model.converged_


@pytest.mark.parametrize('topic',['node2vec','graph-convolutional-networks'])
def test_parameter_update_budget_and_clipping_are_real(b9,topic):
    A=np.array([[0.,1],[1,0]])
    if topic=='node2vec':model=b9.load(topic).Node2Vec(epochs=2,gradient_clip=1e-6).fit(A)
    else:model=b9.load(topic).GCNClassifier(epochs=2,gradient_clip=1e-6).fit(A,[[1.],[2.]],[0,1])
    assert model.n_updates_==2 and len(model.loss_history_)==3 and np.isfinite(model.loss_history_).all()
    assert all(np.isfinite(v).all() for v in model.parameters_.values())
