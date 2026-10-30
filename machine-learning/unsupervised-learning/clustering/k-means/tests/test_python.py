import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest

pytestmark = pytest.mark.ml


@pytest.mark.oracle
@pytest.mark.numerical
def test_exact_centers_inertia_transform_and_stationarity(clustering_support):
    X = np.array([[0.], [2.], [10.], [12.]])
    model = clustering_support.load('k-means').KMeans(2, init=[[0.], [12.]], n_init=1).fit(X)
    assert_allclose(model.cluster_centers_, [[1.], [11.]])
    assert model.inertia_ == pytest.approx(4)
    assert_array_equal(model.labels_, [0, 0, 1, 1])
    assert_array_equal(model.predict(X), model.labels_)
    assert_allclose(model.transform([[1.], [11.]]), [[0, 10], [10, 0]])
    assert model.score(X) == pytest.approx(-4)
    for j in range(2):
        assert_allclose(np.sum(X[model.labels_ == j]-model.cluster_centers_[j], axis=0), 0, atol=1e-13)


@pytest.mark.reference
@pytest.mark.parametrize('seed', [16011, 16012, 16013])
def test_aligned_lloyd_reference(clustering_support, seed):
    from sklearn.cluster import KMeans
    from sklearn.metrics import adjusted_rand_score
    rng = np.random.default_rng(seed)
    X = np.r_[rng.normal(-3, .2, (12, 2)), rng.normal(3, .2, (12, 2))]
    centers = X[[0, 12]]
    ours = clustering_support.load('k-means').KMeans(2, init=centers, n_init=1).fit(X)
    ref = KMeans(2, init=centers, n_init=1, algorithm='lloyd', tol=0, random_state=0).fit(X)
    assert adjusted_rand_score(ours.labels_, ref.labels_) == 1
    assert_allclose(ours.inertia_, ref.inertia_, rtol=1e-11)
    assert_allclose(np.sort(ours.cluster_centers_, axis=0), np.sort(ref.cluster_centers_, axis=0), atol=1e-12)


@pytest.mark.oracle
@pytest.mark.numerical
def test_empty_repair_tiny_targets_and_duplicate_contract(clustering_support):
    cls = clustering_support.load('k-means').KMeans
    repaired = cls(3, init=[[0.], [0.], [0.]], n_init=1).fit([[0.], [1.], [10.], [11.]])
    assert repaired.empty_cluster_repairs_ > 0
    assert len(set(repaired.labels_)) == 3
    tiny = cls(2, init=[[0.], [10e-200]], n_init=1).fit(np.array([[0.], [2.], [10.], [12.]])*1e-200)
    assert_array_equal(tiny.labels_, [0, 0, 1, 1])
    assert_allclose(tiny.cluster_centers_/1e-200, [[1.], [11.]], atol=1e-13)
    assert tiny.inertia_ == 0 and tiny.normalized_inertia_ > 0
    with pytest.raises(ValueError):
        cls(2).fit([[.1], [.1]])
    constant = cls(1).fit([[.1], [.1]])
    assert_array_equal(constant.cluster_centers_, [[.1]])


def test_nonconvergence_and_failed_refit_preserve_state(clustering_support):
    cls = clustering_support.load('k-means').KMeans
    model = cls(2, n_init=1).fit([[0], [1], [10], [11]])
    before = model.predict([[0], [11]])
    model.init = [[0.], [0.]];model.max_iter = 1
    with pytest.raises(clustering_support.ConvergenceError):
        model.fit([[0], [1], [2], [10], [11]])
    assert_array_equal(model.predict([[0], [11]]), before)


@pytest.mark.parametrize('kwargs', [{'n_clusters':0}, {'n_clusters':True}, {'n_init':0}, {'max_iter':0}, {'random_state':-1}])
def test_invalid_hyperparameters(clustering_support, kwargs):
    with pytest.raises(ValueError):
        clustering_support.load('k-means').KMeans(**kwargs)
