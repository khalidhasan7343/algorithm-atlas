import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest

pytestmark = pytest.mark.ml


def two_cliques():
    W = np.zeros((6, 6))
    W[:3, :3] = 1;W[3:, 3:] = 1
    np.fill_diagonal(W, 0)
    return W


@pytest.mark.oracle
@pytest.mark.numerical
def test_normalized_eigenproblem_projector_and_cut(clustering_support):
    W = two_cliques()
    model = clustering_support.load('spectral-clustering').SpectralClustering(2, affinity='precomputed', random_state=0).fit(W)
    assert_array_equal(model.labels_, [0, 0, 0, 1, 1, 1])
    assert model.n_connected_components_ == 2
    assert_allclose(model.degree_, 2)
    assert_allclose(model.eigenvalues_, [1, 1], atol=1e-12)
    assert_allclose(model.eigenvectors_.T @ model.eigenvectors_, np.eye(2), atol=1e-12)
    expected_projector = np.zeros((6, 6));expected_projector[:3, :3] = 1/3;expected_projector[3:, 3:] = 1/3
    assert_allclose(model.eigenvectors_ @ model.eigenvectors_.T, expected_projector, atol=1e-12)
    assert_allclose(model.normalized_affinity_ @ model.eigenvectors_, model.eigenvectors_*model.eigenvalues_, atol=1e-12)
    assert_allclose(np.sum(model.embedding_**2, axis=1), 1, atol=1e-12)
    assert model.normalized_cut_ == pytest.approx(0)


@pytest.mark.reference
def test_strong_precomputed_partition_against_sklearn(clustering_support):
    from sklearn.cluster import SpectralClustering
    from sklearn.metrics import adjusted_rand_score
    W = two_cliques()
    W[:3, 3:] = .001;W[3:, :3] = .001
    ours = clustering_support.load('spectral-clustering').SpectralClustering(2, affinity='precomputed', random_state=0).fit(W)
    ref = SpectralClustering(2, affinity='precomputed', assign_labels='kmeans', n_init=10, random_state=0).fit(W)
    assert adjusted_rand_score(ours.labels_, ref.labels_) == 1
    # Our Ng-Jordan-Weiss row-normalized embedding is not claimed equal to
    # every library's discretization or degree-rescaled eigenvector convention.
    assert ours.normalized_cut_ > 0


@pytest.mark.reference
@pytest.mark.numerical
def test_rbf_affinity_and_subspace_against_scipy(clustering_support):
    from scipy.linalg import eigh
    X = np.array([[-2., -.1], [-1.8, .1], [-2.1, .2], [2., 0.], [2.2, .2], [1.9, -.2]])
    model = clustering_support.load('spectral-clustering').SpectralClustering(2, gamma=.5).fit(X)
    D2 = np.sum((X[:, None]-X[None, :])**2, axis=2)
    W = np.exp(-.5*D2);np.fill_diagonal(W, 0)
    assert_allclose(model.affinity_matrix_, W, atol=1e-14)
    degree = W.sum(axis=1)
    normalized = W/np.sqrt(np.outer(degree, degree))
    eigenvalues, eigenvectors = eigh(normalized)
    U = eigenvectors[:, -2:]
    assert_allclose(model.eigenvectors_ @ model.eigenvectors_.T, U @ U.T, atol=1e-11)
    assert_array_equal(model.labels_, [0, 0, 0, 1, 1, 1])


@pytest.mark.numerical
def test_tiny_uniform_affinity_scaling_and_isolated_nodes(clustering_support):
    cls = clustering_support.load('spectral-clustering').SpectralClustering
    W = two_cliques()
    a = cls(2, affinity='precomputed').fit(W)
    b = cls(2, affinity='precomputed').fit(W*1e-200)
    assert_array_equal(a.labels_, b.labels_)
    assert_allclose(a.normalized_affinity_, b.normalized_affinity_, atol=1e-12)
    with pytest.raises(ValueError, match='disconnected'):
        cls(1, affinity='precomputed').fit(W)
    W[0, :] = 0;W[:, 0] = 0
    with pytest.raises(ValueError, match='isolated'):
        cls(2, affinity='precomputed').fit(W)
    with pytest.raises(ValueError, match='isolated'):
        cls(2, gamma=1e12).fit([[0.], [1.], [2.]])


@pytest.mark.parametrize('matrix', [[[1, 1], [1, 0]], [[0, 1], [0, 0]], [[0, -1], [-1, 0]], [[0, np.nan], [np.nan, 0]], [[0, 1, 1], [1, 0, 1]], [[False, True], [True, False]]])
def test_invalid_affinities(clustering_support, matrix):
    with pytest.raises(ValueError):
        clustering_support.load('spectral-clustering').SpectralClustering(2, affinity='precomputed').fit(matrix)


@pytest.mark.parametrize('kwargs', [{'n_clusters':0}, {'affinity':'nearest_neighbors'}, {'gamma':0}, {'n_init':0}, {'random_state':-1}])
def test_bad_hyperparameters(clustering_support, kwargs):
    with pytest.raises(ValueError):
        clustering_support.load('spectral-clustering').SpectralClustering(**kwargs)


@pytest.mark.oracle
@pytest.mark.numerical
def test_rbf_scale_requires_inverse_squared_gamma_mapping(clustering_support):
    cls = clustering_support.load('spectral-clustering').SpectralClustering
    X = np.array([[-2.], [-1.8], [-2.1], [2.], [2.2], [1.9]])
    a = cls(2, gamma=.5).fit(X)
    b = cls(2, gamma=.005).fit(10*X)
    assert_allclose(a.affinity_matrix_, b.affinity_matrix_, atol=1e-14)
    assert_array_equal(a.labels_, b.labels_)
    assert_allclose(a.normalized_cut_, b.normalized_cut_, atol=1e-12)
