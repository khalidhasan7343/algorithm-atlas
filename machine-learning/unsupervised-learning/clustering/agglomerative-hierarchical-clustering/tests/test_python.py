import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest

pytestmark = pytest.mark.ml


@pytest.mark.reference
@pytest.mark.parametrize('linkage', ['single', 'complete', 'average', 'ward'])
def test_linkage_heights_against_scipy(clustering_support, linkage):
    from scipy.cluster.hierarchy import linkage as reference
    X = np.array([[0.], [1.3], [5.1], [9.4], [15.6]])
    model = clustering_support.load('agglomerative-hierarchical-clustering').AgglomerativeClustering(2, linkage=linkage).fit(X)
    ref = reference(X, method=linkage, metric='euclidean')
    assert_allclose(model.distances_, ref[:, 2], atol=1e-12)
    assert_array_equal(model.counts_, ref[:, 3].astype(int))
    assert model.children_.shape == (4, 2)


@pytest.mark.oracle
@pytest.mark.numerical
def test_ward_sse_identity_and_tiny_scale(clustering_support):
    cls = clustering_support.load('agglomerative-hierarchical-clustering').AgglomerativeClustering
    X = np.array([[0.], [2.], [10.], [12.]])
    model = cls(2).fit(X)
    assert_array_equal(model.labels_, [0, 0, 1, 1])
    assert_allclose(model.distances_, [2., 2., np.sqrt(200)])
    tiny = cls(2).fit(X*1e-200)
    assert_array_equal(tiny.labels_, model.labels_)
    assert_allclose(tiny.distances_/1e-200, model.distances_, atol=1e-12)


@pytest.mark.parametrize('linkage', ['single', 'complete', 'average', 'ward'])
def test_singleton_duplicate_ties_and_cuts(clustering_support, linkage):
    cls = clustering_support.load('agglomerative-hierarchical-clustering').AgglomerativeClustering
    one = cls(1, linkage=linkage).fit([[.1]])
    assert one.children_.shape == (0, 2) and one.labels_.tolist() == [0]
    repeated = cls(2, linkage=linkage).fit([[1], [1], [1]])
    assert_array_equal(repeated.distances_, [0, 0])
    assert len(set(repeated.labels_)) == 2
    all_leaves = cls(3, linkage=linkage).fit([[0], [1], [2]])
    assert_array_equal(all_leaves.labels_, [0, 1, 2])


@pytest.mark.parametrize('kwargs', [{'n_clusters':0}, {'n_clusters':True}, {'linkage':'centroid'}])
def test_invalid_hyperparameters(clustering_support, kwargs):
    with pytest.raises(ValueError):
        clustering_support.load('agglomerative-hierarchical-clustering').AgglomerativeClustering(**kwargs)


@pytest.mark.oracle
def test_tied_single_linkage_has_valid_full_hierarchy(clustering_support):
    from scipy.cluster.hierarchy import linkage
    X = np.array([[0.], [1.], [5.], [9.], [13.2]])
    model = clustering_support.load('agglomerative-hierarchical-clustering').AgglomerativeClustering(2, linkage='single').fit(X)
    assert_allclose(model.distances_, linkage(X, method='single')[:, 2])
    membership = {i: {i} for i in range(len(X))}
    for j, (left, right) in enumerate(model.children_):
        assert not membership[left] & membership[right]
        joined = membership[left] | membership[right]
        assert len(joined) == model.counts_[j]
        membership[len(X)+j] = joined
    assert membership[2*len(X)-2] == set(range(len(X)))
