import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest

pytestmark = pytest.mark.ml


@pytest.mark.oracle
@pytest.mark.numerical
def test_modes_fixed_point_merge_and_query_noise(clustering_support):
    X = np.array([[0.], [.1], [5.], [5.1]])
    model = clustering_support.load('mean-shift').MeanShift(bandwidth=.3, tol=1e-8, cluster_all=False).fit(X)
    assert_allclose(model.cluster_centers_, [[5.05], [.05]], atol=1e-13)
    assert_array_equal(model.labels_, [1, 1, 0, 0])
    assert_array_equal(model.predict([[0], [5], [20]]), [1, 0, -1])
    for center in model.candidate_centers_:
        distance = np.sqrt(np.sum((X-center)**2, axis=1))
        assert_allclose(center, X[distance <= .3].mean(axis=0), atol=1e-13)
    assert len(model.cluster_centers_) == 2
    assert_allclose(model.candidate_support_, 2)


@pytest.mark.reference
@pytest.mark.parametrize('seed', [16035, 16036])
def test_aligned_flat_kernel_reference(clustering_support, seed):
    from sklearn.cluster import MeanShift
    from sklearn.metrics import adjusted_rand_score
    rng = np.random.default_rng(seed)
    X = np.r_[rng.normal(-3, .02, (10, 1)), rng.normal(3, .02, (10, 1))]
    ours = clustering_support.load('mean-shift').MeanShift(bandwidth=.5).fit(X)
    ref = MeanShift(bandwidth=.5, bin_seeding=False, cluster_all=True, max_iter=300).fit(X)
    assert adjusted_rand_score(ours.labels_, ref.labels_) == 1
    assert_allclose(np.sort(ours.cluster_centers_, axis=0), np.sort(ref.cluster_centers_, axis=0), atol=1e-12)


@pytest.mark.numerical
def test_constant_tiny_and_offset_scales(clustering_support):
    cls = clustering_support.load('mean-shift').MeanShift
    constant = cls(bandwidth=1).fit([[.1], [.1]])
    assert_array_equal(constant.cluster_centers_, [[.1]])
    tiny = cls(bandwidth=1e-200).fit([[0.], [.1e-200], [5e-200]])
    assert_allclose(np.sort(tiny.cluster_centers_[:, 0])/1e-200, [.05, 5], atol=1e-12)
    offset = cls(bandwidth=10).fit([[1e12], [1e12-2]])
    assert_array_equal(offset.cluster_centers_, [[1e12-1]])
    assert constant.predict(np.empty((0, 1))).shape == (0,)


def test_nonconvergence_and_failed_refit(clustering_support):
    cls = clustering_support.load('mean-shift').MeanShift
    model = cls(bandwidth=1).fit([[0], [.1]])
    before = model.predict([[0]])
    model.max_iter = 1
    with pytest.raises(clustering_support.ConvergenceError):
        model.fit([[0], [.1]])
    assert_array_equal(model.predict([[0]]), before)


@pytest.mark.parametrize('kwargs', [{'bandwidth':0}, {'bandwidth':np.inf}, {'tol':0}, {'tol':2}, {'max_iter':0}, {'cluster_all':1}])
def test_invalid_hyperparameters(clustering_support, kwargs):
    with pytest.raises(ValueError):
        clustering_support.load('mean-shift').MeanShift(**kwargs)


@pytest.mark.oracle
@pytest.mark.numerical
def test_one_shift_matches_epanechnikov_density_gradient(clustering_support):
    X = np.array([[0.], [.2], [.05]])
    model = clustering_support.load('mean-shift').MeanShift(bandwidth=1, tol=1, max_iter=1).fit(X)
    location = .05
    epsilon = 1e-6
    def density(point):
        return sum(max(0, 1-(float(row[0])-point)**2) for row in X)
    numerical_gradient = (density(location+epsilon)-density(location-epsilon))/(2*epsilon)
    observed_shift = float(model.candidate_centers_[2, 0])-location
    assert_allclose(numerical_gradient, 2*len(X)*observed_shift, atol=1e-9)
