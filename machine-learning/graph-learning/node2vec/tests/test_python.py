import math

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest

pytestmark = pytest.mark.ml


def graph(n, edges):
    A = np.zeros((n, n))
    for i, j, w in edges:
        A[i, j] = A[j, i] = w
    return A


def transition_oracle(A, t, v, p, q):
    # Independent BFS distances rather than the implementation's adjacency branch.
    distances = {t:0}; queue = [t]
    for u in queue:
        for x in range(len(A)):
            if A[u, x] > 0 and x not in distances:
                distances[x] = distances[u] + 1; queue.append(x)
    weights = [A[v, x] * ({0:1/p, 1:1, 2:1/q}[distances[x]]) if A[v, x] > 0 else 0. for x in range(len(A))]
    return np.array(weights) / sum(weights)


@pytest.mark.oracle
@pytest.mark.parametrize('p,q', [(1, 1), (.25, 1), (1, .25), (4, 3)])
def test_exact_first_and_second_order_weighted_bias(b9, p, q):
    A = graph(4, [(0,1,2), (1,2,3), (0,2,1), (1,3,4)])
    m = b9.load('node2vec').Node2Vec(p=p, q=q)
    assert_allclose(m.transition_probabilities(A, 1), [2/9, 0, 3/9, 4/9])
    actual = m.transition_probabilities(A, 1, previous=0)
    assert_allclose(actual, transition_oracle(A, 0, 1, p, q))
    assert_allclose(actual.sum(), 1)
    assert actual[1] == 0


@pytest.mark.oracle
def test_seeded_random_transition_oracles(b9):
    rng = np.random.default_rng(21002)
    for n in range(3, 9):
        upper = np.triu(rng.uniform(.1, 3, (n, n)) * (rng.random((n,n)) < .5), 1)
        A = upper + upper.T
        m = b9.load('node2vec').Node2Vec(p=.4, q=2.)
        for t, v in zip(*np.nonzero(A)):
            assert_allclose(m.transition_probabilities(A, int(v), int(t)), transition_oracle(A, int(t), int(v), .4, 2.))


def test_walk_bounds_isolates_dead_ends_and_seed_reproducibility(b9):
    A = graph(4, [(0,1,1), (1,2,1)])
    m = b9.load('node2vec').Node2Vec(walk_length=5, num_walks=3, random_state=21003)
    walks = m.generate_walks(A)
    assert walks == m.generate_walks(A)
    assert len(walks) == 12
    assert sum(w == [3] for w in walks) == 3
    assert_array_equal(m.transition_probabilities(A,3), np.zeros(4))
    for w in walks:
        assert 1 <= len(w) <= 5
        assert all(A[a,b] > 0 for a,b in zip(w,w[1:]))
    assert all(len(w) == 1 for w in b9.load('node2vec').Node2Vec(walk_length=1).generate_walks(A))


@pytest.mark.oracle
def test_context_window_exact_order_boundaries_and_revisits(b9):
    make = b9.load('node2vec').context_pairs
    assert_array_equal(make([[0,1,2]],1), [[0,1],[1,0],[1,2],[2,1]])
    assert_array_equal(make([[0,1,2]],2), [[0,1],[0,2],[1,0],[1,2],[2,0],[2,1]])
    assert_array_equal(make([[0,0]],1), [[0,0],[0,0]])
    assert make([[0]],1).shape == (0,2)
    for bad in ([[[]]], [[-1]], [[32]], [list(range(65))]):
        with pytest.raises(ValueError):
            make(bad,1)


def loop_loss(U, V, pairs, negatives):
    total = 0.
    for (center,context), negative in zip(pairs, negatives):
        positive = sum(float(x)*float(y) for x,y in zip(U[center],V[context]))
        total += math.log1p(math.exp(-positive))
        for node in negative:
            score = sum(float(x)*float(y) for x,y in zip(U[center],V[node]))
            total += math.log1p(math.exp(score))
    return total / len(pairs)


@pytest.mark.oracle
@pytest.mark.numerical
def test_sgns_independent_loss_and_all_finite_difference_gradients_with_collisions(b9):
    rng = np.random.default_rng(21004)
    U,V = rng.normal(0,.2,(3,2)), rng.normal(0,.2,(3,2))
    pairs = np.array([[0,1],[0,1],[1,0],[2,2]])
    negatives = np.array([[1,0],[2,1],[0,0],[2,1]])
    loss,g = b9.load('node2vec').sgns_loss_gradients(U,V,pairs,negatives)
    assert_allclose(loss, loop_loss(U,V,pairs,negatives), atol=1e-14)
    for name,array in [('input',U),('output',V)]:
        for index in np.ndindex(array.shape):
            old = array[index]; array[index] = old+1e-6
            plus = loop_loss(U,V,pairs,negatives)
            array[index] = old-1e-6
            minus = loop_loss(U,V,pairs,negatives)
            array[index] = old
            assert_allclose(g[name][index], (plus-minus)/2e-6, atol=2e-9, rtol=2e-6)


@pytest.mark.oracle
def test_hand_sgns_loss_and_gradient(b9):
    loss,g = b9.load('node2vec').sgns_loss_gradients([[1.],[0.]], [[0.],[0.]], [[0,1]], [[0]])
    assert_allclose(loss, 2*math.log(2))
    assert_allclose(g['input'], [[0.],[0.]])
    assert_allclose(g['output'], [[.5],[-.5]])


@pytest.mark.numerical
def test_extreme_logits_and_tiny_weight_scale_stay_finite(b9):
    m = b9.load('node2vec')
    loss,g = m.sgns_loss_gradients([[1e6],[-1e6]], [[-1e6],[1e6]], [[0,0],[1,1]], [[1],[0]])
    assert np.isfinite(loss) and all(np.isfinite(x).all() for x in g.values())
    A = np.array([[0.,1e-320,0],[1e-320,0,1e-320],[0,1e-320,0]])
    assert_allclose(m.Node2Vec(p=1000,q=.001).transition_probabilities(A,1,0), [.001/(.001+1000),0,1000/(.001+1000)])


@pytest.mark.parametrize('kind', ['path','cycle','star','communities','disconnected'])
def test_genuine_training_parameter_updates_and_fixed_noise(b9, kind):
    edges = [(0,1,1),(1,2,1),(2,3,1)]
    if kind == 'cycle':edges += [(3,0,1)]
    elif kind == 'star':edges = [(0,1,1),(0,2,1),(0,3,1)]
    elif kind == 'communities':edges = [(0,1,1),(1,2,1),(0,2,1),(3,4,1),(4,5,1),(3,5,1),(2,3,.1)]
    elif kind == 'disconnected':edges = [(0,1,1),(2,3,1)]
    A = graph(6,edges)
    m = b9.load('node2vec').Node2Vec(epochs=80, random_state=21005).fit(A)
    assert m.embeddings_.shape == (6,4) and np.isfinite(m.embeddings_).all()
    assert m.loss_history_[-1] < m.loss_history_[0] - 1e-5
    assert np.linalg.norm(m.embeddings_ - m.initial_embeddings_) > 1e-3
    assert m.n_updates_ == 80 and not m.converged_ and m.optimization_status_ == 'epoch-budget'
    assert m.walks_ == m.generate_walks(A)
    counts = np.bincount(m.positive_pairs_[:,1], minlength=6) ** .75
    assert_allclose(m.noise_distribution_,counts/counts.sum())
    final,_ = b9.load('node2vec').sgns_loss_gradients(m.embeddings_,m.context_embeddings_,m.positive_pairs_,m.negative_indices_)
    assert_allclose(final,m.loss_history_[-1])
    for isolated in np.flatnonzero(A.sum(1)==0):
        assert_array_equal(m.embeddings_[isolated],m.initial_embeddings_[isolated])


def test_deterministic_fit_local_rng_ownership_and_failed_refit(b9):
    A = graph(3,[(0,1,1),(1,2,2)]);before=A.copy()
    np.random.seed(21006);state=np.random.get_state()
    m = b9.load('node2vec').Node2Vec(epochs=5).fit(A)
    actual=m.transform();other=b9.load('node2vec').Node2Vec(epochs=5).fit(A)
    assert_array_equal(actual,other.embeddings_)
    assert_array_equal(np.random.get_state()[1],state[1]);assert_array_equal(A,before)
    result=m.transform([2,0]);result[:]=0;assert_array_equal(m.transform(),actual)
    with pytest.raises(ValueError):m.fit(np.zeros((3,3)))
    assert_array_equal(m.transform(),actual)
    with pytest.raises(ValueError):b9.load('node2vec').Node2Vec().transform()
    for bad in ([-1],[3],[True],[1.],[[1]]):
        with pytest.raises(ValueError):m.transform(bad)


@pytest.mark.parametrize('settings', [dict(p=0),dict(q=np.nan),dict(p=True),dict(dimensions=0),
    dict(walk_length=65),dict(num_walks=21),dict(window_size=0),dict(negative_samples=9),
    dict(epochs=501),dict(random_state=-1),dict(learning_rate=np.inf),dict(gradient_clip=0)])
def test_invalid_settings(b9,settings):
    with pytest.raises(ValueError):b9.load('node2vec').Node2Vec(**settings)


@pytest.mark.parametrize('A', [[],[[0,1],[0,0]],[[1]],[[0,-1],[-1,0]],[[np.nan]],[[True]],np.zeros((33,33))])
def test_unsupported_graphs(b9,A):
    with pytest.raises(ValueError):b9.load('node2vec').Node2Vec().generate_walks(A)


def test_budget_and_transition_index_validation(b9):
    Node2Vec=b9.load('node2vec').Node2Vec
    with pytest.raises(ValueError):Node2Vec(epochs=500,dimensions=16,negative_samples=8).fit(np.ones((32,32))-np.eye(32))
    with pytest.raises(ValueError):Node2Vec().fit([[0]])
    A=graph(3,[(0,1,1)])
    for current,previous in [(3,None),(True,None),(0,2),(0,0)]:
        with pytest.raises(ValueError):Node2Vec().transition_probabilities(A,current,previous)


@pytest.mark.parametrize('pairs,negatives', [([],[]),([[0,2]],[[0]]),([[0,1]],[[2]]),([[0,1]],[[]]),([[0,1]],[[True]]),([[0.,1.]],[[0]])])
def test_invalid_training_indices(b9,pairs,negatives):
    with pytest.raises(ValueError):b9.load('node2vec').sgns_loss_gradients(np.zeros((2,1)),np.zeros((2,1)),pairs,negatives)
