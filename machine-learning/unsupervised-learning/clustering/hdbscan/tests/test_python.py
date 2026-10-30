import itertools
import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest

pytestmark = pytest.mark.ml


@pytest.mark.oracle
@pytest.mark.numerical
def test_hand_computed_condensation_density_and_membership(clustering_support):
    X = np.array([[0.], [.1], [.2], [5.], [5.1], [5.2], [12.]])
    model = clustering_support.load('hdbscan').HDBSCAN(min_cluster_size=3, min_samples=2).fit(X)
    assert_array_equal(model.labels_, [0, 0, 0, 1, 1, 1, -1])
    assert_allclose(model.probabilities_, [1, 1, 1, 1, 1, 1, 0], atol=1e-13)
    assert_allclose(model.core_distances_, [.1, .1, .1, .1, .1, .1, 6.8], atol=1e-13)
    assert len(model.minimum_spanning_tree_) == 6
    assert model.single_linkage_tree_[-1, 3] == 7
    assert model.distance_scale_ == 12
    for cluster in model.selected_clusters_:
        assert_allclose(model.cluster_births_[cluster], 12/4.8, atol=1e-12)
        assert_allclose(model.cluster_stabilities_[cluster], 3*(12/.1-12/4.8), atol=1e-9)
    # Sum edge mass times lifetime independently, without the selection helper.
    for cluster, birth in model.cluster_births_.items():
        rows = model.condensed_tree_[model.condensed_tree_['parent'] == cluster]
        expected = sum(int(row['child_size'])*(row['lambda_val']-birth) for row in rows)
        assert_allclose(model.cluster_stabilities_[cluster], expected, atol=1e-10)


@pytest.mark.reference
@pytest.mark.parametrize('seed', [16031, 16032, 16033])
def test_reference_core_distances_mst_partition_and_probabilities(clustering_support, seed):
    from scipy.sparse.csgraph import minimum_spanning_tree
    from sklearn.cluster import HDBSCAN
    from sklearn.metrics import adjusted_rand_score
    rng = np.random.default_rng(seed)
    X = np.r_[rng.normal(-3, .02, (10, 2)), rng.normal(3, .02, (10, 2)), [[15., 15.]]]
    ours = clustering_support.load('hdbscan').HDBSCAN(min_cluster_size=6, min_samples=4).fit(X)
    ref = HDBSCAN(min_cluster_size=6, min_samples=4, metric='euclidean', algorithm='brute', copy=True, cluster_selection_method='eom', allow_single_cluster=False).fit(X)
    D = np.sqrt(np.sum((X[:, None]-X[None, :])**2, axis=2))
    core = np.sort(D, axis=1)[:, 3]
    reach = np.maximum(np.maximum(D, core[:, None]), core[None, :])
    assert_allclose(ours.core_distances_, core, atol=1e-12)
    assert_allclose(ours.mutual_reachability_, reach, atol=1e-12)
    np.fill_diagonal(reach, 0)
    assert_allclose(ours.minimum_spanning_tree_[:, 2].sum(), minimum_spanning_tree(reach).sum(), atol=1e-11)
    assert adjusted_rand_score(ours.labels_, ref.labels_) == 1
    assert_allclose(ours.probabilities_, ref.probabilities_, atol=1e-10, rtol=1e-8)


@pytest.mark.oracle
def test_eom_against_exhaustive_disjoint_cluster_subsets(clustering_support):
    rng = np.random.default_rng(16034)
    X = np.r_[rng.normal(-2, .15, (5, 1)), rng.normal(2, .15, (5, 1)), [[10.]]]
    model = clustering_support.load('hdbscan').HDBSCAN(min_cluster_size=2, min_samples=2).fit(X)
    clusters = [c for c in model.cluster_stabilities_ if c != len(X)]
    assert len(clusters) <= 12
    best = 0.0
    for bits in itertools.product((False, True), repeat=len(clusters)):
        selected = [c for c, keep in zip(clusters, bits) if keep]
        members = [set(model.cluster_members_[c]) for c in selected]
        if any(A & B for i, A in enumerate(members) for B in members[i+1:]):
            continue
        score = sum(model.cluster_stabilities_[c] for c in selected)
        best = max(best, score)
    assert_allclose(sum(model.cluster_stabilities_[c] for c in model.selected_clusters_), best)


@pytest.mark.numerical
def test_duplicate_infinite_density_root_exclusion_and_tiny_scale(clustering_support):
    cls = clustering_support.load('hdbscan').HDBSCAN
    duplicate_groups = cls(min_cluster_size=3, min_samples=2).fit([[0], [0], [0], [1], [1], [1]])
    assert_array_equal(duplicate_groups.labels_, [0, 0, 0, 1, 1, 1])
    assert_allclose(duplicate_groups.probabilities_, 1)
    assert not any(np.isnan(v) for v in duplicate_groups.cluster_stabilities_.values())
    all_same = cls(min_cluster_size=2).fit([[1], [1], [1]])
    assert_array_equal(all_same.labels_, [-1, -1, -1])
    X = np.array([[0.], [.1], [.2], [5.], [5.1], [5.2], [12.]])
    a = cls(min_cluster_size=3, min_samples=2).fit(X)
    b = cls(min_cluster_size=3, min_samples=2).fit(X*1e-200)
    assert_array_equal(a.labels_, b.labels_)
    assert_allclose(a.probabilities_, b.probabilities_, atol=1e-12)
    assert_allclose(a.minimum_spanning_tree_[:, 2], b.minimum_spanning_tree_[:, 2]/1e-200, atol=1e-12)


@pytest.mark.parametrize('kwargs', [{'min_cluster_size':1}, {'min_cluster_size':True}, {'min_cluster_size':257}])
def test_invalid_constructor_parameters(clustering_support, kwargs):
    with pytest.raises(ValueError):
        clustering_support.load('hdbscan').HDBSCAN(**kwargs)


@pytest.mark.parametrize('minimum', [0, True, 4])
def test_invalid_support_relative_to_data(clustering_support, minimum):
    with pytest.raises(ValueError):
        clustering_support.load('hdbscan').HDBSCAN(min_cluster_size=2, min_samples=minimum).fit([[0], [1], [2]])
