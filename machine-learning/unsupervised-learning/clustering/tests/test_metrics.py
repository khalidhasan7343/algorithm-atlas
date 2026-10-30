import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest

pytestmark = pytest.mark.ml


def metrics(s):
    return s.module_at('atlas_clustering_metrics', s.ROOT/'metrics.py')


@pytest.mark.oracle
@pytest.mark.numerical
def test_hand_computed_silhouette_singletons_noise_and_degenerate_cases(clustering_support):
    m = metrics(clustering_support)
    X = [[0.], [2.], [10.], [12.]];labels = [0, 0, 1, 1]
    # Within distance=2; between means are 11,9,9,11.
    expected = np.array([9/11, 7/9, 7/9, 9/11])
    assert_allclose(m.silhouette_samples(X, labels), expected)
    assert_allclose(m.silhouette_score(X, labels), expected.mean())
    noise = m.silhouette_samples([[0.], [2.], [10.], [12.], [100.]], [0, 0, 1, 1, -1])
    assert np.isnan(noise[-1]);assert_allclose(noise[:-1], expected)
    singleton = m.silhouette_samples([[0.], [2.], [10.]], [0, 0, 1])
    assert singleton[-1] == 0
    assert_allclose(m.silhouette_score(np.ones((4, 1)), labels), 0)
    report = m.clustering_report([[0.], [1.]], [-1, -1])
    assert report['silhouette'] is None and report['coverage'] == 0 and report['n_clusters'] == 0


@pytest.mark.reference
@pytest.mark.parametrize('seed', [16101, 16102, 16103])
def test_metric_references_and_label_permutation(clustering_support, seed):
    from sklearn.metrics import adjusted_rand_score, silhouette_samples
    m = metrics(clustering_support);rng = np.random.default_rng(seed)
    X = rng.normal(size=(12, 3));a = np.repeat([0, 1, 2], 4);b = rng.integers(-1, 3, 12)
    assert_allclose(m.adjusted_rand_index(a, b), adjusted_rand_score(a, b), atol=1e-13)
    assert_allclose(m.silhouette_samples(X, a), silhouette_samples(X, a), atol=1e-13)
    assert m.adjusted_rand_index(a, a*7+10) == 1
    assert m.adjusted_rand_index([5], [-1]) == 1


@pytest.mark.oracle
def test_adjusted_rand_pair_count(clustering_support):
    m = metrics(clustering_support)
    assert_allclose(m.adjusted_rand_index([0, 0, 1, 1], [0, 1, 0, 1]), -.5)
    assert m.adjusted_rand_index([0, 0, 0], [7, 7, 7]) == 1
    assert m.adjusted_rand_index([0, 1, 2], [7, 8, 9]) == 1


@pytest.mark.parametrize('prediction', [[], [True, False], [0., 1.], [[0], [1]], [0], ['a', 'b']])
def test_invalid_labels(clustering_support, prediction):
    with pytest.raises(ValueError):metrics(clustering_support).clustering_report([[0.], [1.]], prediction)


@pytest.mark.parametrize('prediction', [[0, 0], [0, 1], [-1, -1]])
def test_undefined_silhouette_is_explicit(clustering_support, prediction):
    with pytest.raises(ValueError):metrics(clustering_support).silhouette_score([[0.], [1.]], prediction)
