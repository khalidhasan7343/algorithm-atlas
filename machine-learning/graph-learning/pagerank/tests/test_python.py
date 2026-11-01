import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest

pytestmark = pytest.mark.ml


def stationary_oracle(A, damping, v):
    """Independent scalar construction and direct stationary linear solve."""
    n = len(A)
    transition = np.empty((n, n))
    for i in range(n):
        degree = sum(float(A[i][j]) for j in range(n))
        for j in range(n):
            transition[i, j] = float(A[i][j]) / degree if degree else v[j]
    return np.linalg.solve(np.eye(n) - damping * transition.T, (1 - damping) * np.array(v))


@pytest.mark.oracle
@pytest.mark.parametrize('A,v', [([[0]], [1.]), ([[1]], [1.]),
    ([[0, 1], [0, 0]], [.5, .5]), ([[0, 2], [3, 0]], [.2, .8]),
    ([[0, 1, 0], [0, 0, 1], [1, 0, 0]], [1/3]*3),
    ([[0, 1, 1], [1, 0, 1], [1, 1, 0]], [1/3]*3),
    ([[0, 1, 2, 0], [1, 0, 0, 0], [2, 0, 0, 0], [0, 0, 0, 0]], [.1, .2, .3, .4]),
    ([[0, 0], [0, 0]], [1., 0.])])
def test_stationary_linear_oracle_mass_and_residual(b9, A, v):
    model = b9.load('pagerank').PageRank(tolerance=1e-12, personalization=v).fit(A)
    assert model.converged_
    assert np.all(model.scores_ >= 0)
    assert_allclose(model.scores_.sum(), 1., atol=1e-14)
    assert_allclose(model.scores_, stationary_oracle(A, .85, v), atol=1e-12, rtol=0)
    assert_allclose(model.scores_, .85 * model.transition_matrix_.T @ model.scores_ + .15 * np.array(v), atol=1e-12)
    assert model.error_bound_ <= 1e-12


@pytest.mark.oracle
def test_two_node_hand_result_and_zero_damping(b9):
    PageRank = b9.load('pagerank').PageRank
    assert_allclose(PageRank(damping=.5).fit_transform([[0, 1], [0, 0]]), [.4, .6], atol=1e-10)
    m = PageRank(damping=0, personalization=[1., 0.]).fit([[0, 1], [0, 0]])
    assert_array_equal(m.scores_, [1., 0.])
    assert m.n_iter_ == 1 and m.residual_ == 0


@pytest.mark.numerical
def test_seeded_random_directed_weighted_graphs_and_row_scaling(b9):
    rng = np.random.default_rng(21001)
    for n in range(2, 10):
        A = rng.uniform(.01, 4., (n, n)) * (rng.random((n, n)) < .3)
        A[-1] = 0
        v = rng.dirichlet(np.ones(n))
        m = b9.load('pagerank').PageRank(personalization=v, tolerance=1e-12).fit(A)
        assert_allclose(m.scores_, stationary_oracle(A, .85, v), atol=1e-12, rtol=0)
        rescaled = b9.load('pagerank').PageRank(personalization=v, tolerance=1e-12).fit_transform(A * rng.uniform(.1, 3, (n, 1)))
        assert_allclose(rescaled, m.scores_, atol=1e-12)


@pytest.mark.oracle
def test_symmetric_star_cycle_and_node_permutation(b9):
    PageRank = b9.load('pagerank').PageRank
    A = np.zeros((5, 5)); A[0, 1:] = 1; A[1:, 0] = 1
    scores = PageRank().fit_transform(A)
    assert_allclose(scores[1:], scores[1])
    assert scores[0] > scores[1]
    order = np.array([3, 0, 4, 1, 2])
    assert_allclose(PageRank().fit_transform(A[np.ix_(order, order)]), scores[order], atol=1e-12)
    cycle = np.eye(4, k=1) + np.eye(4, k=-3)
    assert_allclose(PageRank().fit_transform(cycle), np.full(4, .25))


def test_budget_nonconvergence_and_diagnostics(b9):
    m = b9.load('pagerank').PageRank(max_iter=1, tolerance=1e-14).fit([[0, 1], [0, 0]])
    assert not m.converged_ and m.n_iter_ == 1 and m.optimization_status_ == 'iteration-budget'
    assert m.error_bound_ > 1e-14


@pytest.mark.parametrize('settings', [dict(damping=x) for x in (-.1, 1, True, np.nan, np.inf)] +
    [dict(tolerance=x) for x in (0, 1e-15, True, np.nan)] +
    [dict(max_iter=x) for x in (0, 100001, True, 1.5)])
def test_invalid_hyperparameters(b9, settings):
    with pytest.raises(ValueError):
        b9.load('pagerank').PageRank(**settings)


@pytest.mark.parametrize('A', [[], [[0, 1]], [[0, -1], [0, 0]], [[np.nan]], [[np.inf]], [[True]], [['1']], np.zeros((33,33)), [[1e7]], [[1j]]])
def test_invalid_graph(b9, A):
    with pytest.raises(ValueError):
        b9.load('pagerank').PageRank().fit(A)


@pytest.mark.parametrize('v', [[0, 0], [1, 1], [-1, 2], [np.nan, 1], [1], [[.5, .5]], [True, False]])
def test_invalid_personalization(b9, v):
    with pytest.raises(ValueError):
        b9.load('pagerank').PageRank(personalization=v).fit([[0, 1], [0, 0]])


def test_copying_reproducibility_and_atomic_failed_refit(b9):
    A = np.array([[0., 1], [0, 0]]); before = A.copy()
    PageRank = b9.load('pagerank').PageRank
    m = PageRank(); result = m.fit_transform(A)
    assert_array_equal(A, before)
    assert_array_equal(result, PageRank().fit_transform(A))
    result[:] = 0
    assert m.scores_.sum() > .99
    old = m.scores_.copy()
    with pytest.raises(ValueError):
        m.fit([])
    assert_array_equal(m.scores_, old)
