import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest

pytestmark = pytest.mark.ml
SPECS = [
    ('k-means', 'KMeans', {'n_clusters':2, 'n_init':2}),
    ('agglomerative-hierarchical-clustering', 'AgglomerativeClustering', {'n_clusters':2}),
    ('divisive-hierarchical-clustering', 'DivisiveClustering', {'n_clusters':2}),
    ('dbscan', 'DBSCAN', {'eps':.3, 'min_samples':3}),
    ('hdbscan', 'HDBSCAN', {'min_cluster_size':3, 'min_samples':2}),
    ('mean-shift', 'MeanShift', {'bandwidth':.3}),
    ('gaussian-mixture-models', 'GaussianMixture', {'n_components':2, 'means_init':[[-2., -2.], [2., 2.]], 'reg_covar':.001}),
    ('spectral-clustering', 'SpectralClustering', {'n_clusters':2, 'gamma':.5}),
]


def model(s, slug, name, kwargs):
    return getattr(s.load(slug), name)(**kwargs)


def cohort():
    rng = np.random.default_rng(16100)
    return np.r_[rng.normal(-2, .03, (6, 2)), rng.normal(2, .03, (6, 2))]


@pytest.mark.parametrize('slug,name,kwargs', SPECS)
def test_copy_global_state_determinism_and_failed_refit(clustering_support, slug, name, kwargs):
    X = cohort();original = X.copy()
    old_rng = np.random.get_state()
    try:
        np.random.seed(387)
        state = np.random.get_state()
        a = model(clustering_support, slug, name, kwargs).fit(X)
        b = model(clustering_support, slug, name, kwargs).fit(X)
        after = np.random.get_state()
        assert state[0] == after[0];assert_array_equal(state[1], after[1]);assert state[2:] == after[2:]
        assert_array_equal(X, original)
        assert_array_equal(a.labels_, b.labels_)
        labels = a.labels_.copy()
        with pytest.raises((ValueError, TypeError)):
            a.fit([[np.nan, 0], [1, 2]])
        assert_array_equal(a.labels_, labels)
        if hasattr(a, 'predict'):
            query = original[:2].copy()
            expected = a.predict(query)
            assert a.predict(np.empty((0, 2))).shape == (0,)
            query[:] = 0
            assert_array_equal(a.predict(original[:2]), expected)
        else:
            assert not hasattr(a, 'transform')
        X[:] = 0
        assert_array_equal(a.labels_, labels)
        returned = a.fit_predict(original)
        returned[:] = -5
        assert np.all(a.labels_ >= -1)
    finally:
        np.random.set_state(old_rng)


@pytest.mark.parametrize('slug,name,kwargs', SPECS)
@pytest.mark.parametrize('bad', [[], [0, 1], [[], []], [[np.nan], [1]], [[np.inf], [1]], [[True], [False]], [['0'], ['1']], [[1+1j], [2]]])
def test_invalid_arrays(clustering_support, slug, name, kwargs, bad):
    with pytest.raises((ValueError, TypeError)):
        model(clustering_support, slug, name, kwargs).fit(bad)


@pytest.mark.parametrize('slug,name,kwargs', SPECS)
def test_resource_caps_and_unsupported_targets(clustering_support, slug, name, kwargs):
    m = model(clustering_support, slug, name, kwargs)
    for X in (np.zeros((513, 1)), np.zeros((2, 33))):
        with pytest.raises(ValueError):m.fit(X)
    with pytest.raises(TypeError):m.fit(cohort(), np.zeros(12))
    with pytest.raises(TypeError):m.fit(cohort(), sample_weight=np.ones(12))


@pytest.mark.parametrize('slug,name,kwargs', [v for v in SPECS if v[1] in ('KMeans', 'MeanShift', 'GaussianMixture')])
def test_unfitted_and_wrong_query_feature_count(clustering_support, slug, name, kwargs):
    m = model(clustering_support, slug, name, kwargs)
    with pytest.raises(ValueError):m.predict([[0, 1]])
    m.fit(cohort())
    for X in ([0, 1], [[0]], [[np.inf, 0]]):
        with pytest.raises(ValueError):m.predict(X)


@pytest.mark.parametrize('slug,name,kwargs', SPECS)
def test_mutated_hyperparameter_is_revalidated(clustering_support, slug, name, kwargs):
    m = model(clustering_support, slug, name, kwargs).fit(cohort())
    before = m.labels_.copy()
    field, value = ('n_clusters', 0) if hasattr(m, 'n_clusters') else ('eps', 0) if slug == 'dbscan' else ('min_cluster_size', 1) if slug == 'hdbscan' else ('bandwidth', 0) if slug == 'mean-shift' else ('reg_covar', 0)
    setattr(m, field, value)
    with pytest.raises(ValueError):m.fit(cohort())
    assert_array_equal(m.labels_, before)
