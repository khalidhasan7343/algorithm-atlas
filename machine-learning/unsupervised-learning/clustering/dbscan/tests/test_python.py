import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest

pytestmark = pytest.mark.ml


@pytest.mark.oracle
def test_self_neighbors_core_border_and_noise(clustering_support):
    model = clustering_support.load('dbscan').DBSCAN(eps=.2, min_samples=2).fit([[0], [.1], [5], [5.1], [10]])
    assert_array_equal(model.labels_, [0, 0, 1, 1, -1])
    assert_array_equal(model.core_sample_indices_, [0, 1, 2, 3])
    assert_array_equal(model.neighbor_counts_, [2, 2, 2, 2, 1])
    assert model.n_clusters_ == 2


@pytest.mark.reference
@pytest.mark.parametrize('seed', [16024, 16025, 16026])
def test_reference_partition_and_core_indices(clustering_support, seed):
    from sklearn.cluster import DBSCAN
    from sklearn.metrics import adjusted_rand_score
    rng = np.random.default_rng(seed)
    X = np.r_[rng.normal(-2, .05, (9, 2)), rng.normal(2, .05, (9, 2)), [[10., 10.]]]
    ours = clustering_support.load('dbscan').DBSCAN(eps=.3, min_samples=4).fit(X)
    ref = DBSCAN(eps=.3, min_samples=4).fit(X)
    assert adjusted_rand_score(ours.labels_, ref.labels_) == 1
    assert_array_equal(ours.core_sample_indices_, ref.core_sample_indices_)


@pytest.mark.oracle
def test_previously_visited_noise_becomes_border_and_ambiguous_border_is_first_reached(clustering_support):
    cls = clustering_support.load('dbscan').DBSCAN
    first = cls(eps=.11, min_samples=3).fit([[0], [.1], [.2]])
    assert first.core_sample_indices_.tolist() == [1]
    assert_array_equal(first.labels_, [0, 0, 0])
    X = np.array([[-.25], [-.26], [-.24], [-.15], [.15], [.24], [.25], [.26], [0.]])
    model = cls(eps=.16, min_samples=4).fit(X)
    assert 8 not in model.core_sample_indices_
    assert model.labels_[8] == model.labels_[0]
    assert model.labels_[0] != model.labels_[7]


@pytest.mark.numerical
def test_tiny_scale_boundary_duplicates_and_all_noise(clustering_support):
    cls = clustering_support.load('dbscan').DBSCAN
    tiny = cls(eps=2e-200, min_samples=2).fit(np.array([[0.], [1.], [10.]])*1e-200)
    assert_array_equal(tiny.labels_, [0, 0, -1])
    duplicate = cls(eps=1e-200, min_samples=3).fit([[.1], [.1], [.1]])
    assert_array_equal(duplicate.labels_, [0, 0, 0])
    no_core = cls(min_samples=512).fit([[0], [1]])
    assert no_core.n_clusters_ == 0 and no_core.components_.shape == (0, 1)
    assert_array_equal(no_core.labels_, [-1, -1])
    self_only = cls(eps=.1, min_samples=1).fit([[0], [1]])
    assert_array_equal(self_only.labels_, [0, 1])


@pytest.mark.parametrize('kwargs', [{'eps':0}, {'eps':np.nan}, {'eps':True}, {'min_samples':0}, {'min_samples':True}, {'min_samples':513}])
def test_invalid_parameters(clustering_support, kwargs):
    with pytest.raises(ValueError):
        clustering_support.load('dbscan').DBSCAN(**kwargs)
