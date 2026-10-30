import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest

pytestmark = pytest.mark.ml


@pytest.mark.oracle
@pytest.mark.numerical
def test_one_component_m_step_likelihood_and_information_criteria(clustering_support):
    from scipy.stats import multivariate_normal
    X = np.array([[0., 1.], [1., 3.], [3., 2.], [4., 5.]])
    regularization = .1
    model = clustering_support.load('gaussian-mixture-models').GaussianMixture(1, reg_covar=regularization).fit(X)
    mean = X.mean(axis=0)
    covariance = sum(np.outer(row-mean, row-mean) for row in X)/len(X)+regularization*np.eye(2)
    assert_allclose(model.means_, [mean], atol=1e-13)
    assert_allclose(model.covariances_, [covariance], atol=1e-13)
    expected = multivariate_normal.logpdf(X, mean=mean, cov=covariance)
    assert_allclose(model.score_samples(X), expected, atol=1e-12)
    assert_allclose(model.score(X), expected.mean())
    assert_allclose(model.lower_bound_, expected.mean())
    assert_allclose(model.predict_proba(X), np.ones((4, 1)))
    assert_allclose(model.aic(X), -2*expected.sum()+2*5)
    assert_allclose(model.bic(X), -2*expected.sum()+np.log(4)*5)


@pytest.mark.reference
@pytest.mark.parametrize('seed', [16041, 16042, 16043])
def test_full_covariance_em_aligned_reference(clustering_support, seed):
    from sklearn.mixture import GaussianMixture
    from sklearn.metrics import adjusted_rand_score
    rng = np.random.default_rng(seed)
    X = np.r_[rng.normal(-3, .15, (18, 2)), rng.normal(3, .15, (18, 2))]
    means = np.array([[-3., -3.], [3., 3.]])
    regularization = 1e-5
    ours = clustering_support.load('gaussian-mixture-models').GaussianMixture(2, means_init=means, reg_covar=regularization, tol=1e-8).fit(X)
    covariance = np.cov(X, rowvar=False, bias=True)+regularization*np.eye(2)
    ref = GaussianMixture(2, covariance_type='full', means_init=means, weights_init=np.full(2, .5),
                          precisions_init=np.repeat(np.linalg.inv(covariance)[None], 2, axis=0),
                          reg_covar=regularization, tol=1e-8, max_iter=300, n_init=1, random_state=0).fit(X)
    assert adjusted_rand_score(ours.labels_, ref.predict(X)) == 1
    assert_allclose(ours.means_, ref.means_, atol=1e-7)
    assert_allclose(ours.covariances_, ref.covariances_, atol=1e-7)
    assert_allclose(ours.score_samples(X), ref.score_samples(X), atol=1e-6)
    assert_allclose(ours.predict_proba(X), ref.predict_proba(X), atol=1e-7)
    assert np.all(np.diff(ours.log_likelihood_history_) >= -1e-8)


@pytest.mark.oracle
@pytest.mark.numerical
def test_responsibilities_against_independent_scipy_density(clustering_support):
    from scipy.stats import multivariate_normal
    X = np.array([[-2.2], [-2.], [-1.8], [1.8], [2.], [2.2]])
    model = clustering_support.load('gaussian-mixture-models').GaussianMixture(2, means_init=[[-2.], [2.]], reg_covar=.01).fit(X)
    query = np.array([[-2.], [0.], [2.]])
    joint = np.column_stack([w*multivariate_normal.pdf(query, mean=mu, cov=cov) for w, mu, cov in zip(model.weights_, model.means_, model.covariances_)])
    assert_allclose(model.predict_proba(query), joint/joint.sum(axis=1, keepdims=True), atol=1e-12)
    assert_allclose(model.score_samples(query), np.log(joint.sum(axis=1)), atol=1e-12)


@pytest.mark.numerical
def test_duplicates_high_dimension_tiny_and_large_finite_data(clustering_support):
    cls = clustering_support.load('gaussian-mixture-models').GaussianMixture
    repeated = cls(2).fit([[.1], [.1], [.1], [.1]])
    assert_array_equal(repeated.means_, [[.1], [.1]])
    assert_allclose(repeated.predict_proba([[.1]]), [[.5, .5]])
    assert_array_equal(repeated.labels_, [0, 0, 0, 0])
    rng = np.random.default_rng(16044)
    high = cls(1, reg_covar=.1).fit(rng.normal(size=(8, 16)))
    assert np.isfinite(high.covariances_).all()
    large_X = rng.normal(size=(20, 2))*1e8
    large = cls(1).fit(large_X)
    assert np.isfinite(large.score_samples(large_X)).all()
    tiny = cls(1).fit([[0.], [1e-200]])
    assert np.isfinite(tiny.score_samples([[0.]])).all()
    assert repeated.predict(np.empty((0, 1))).shape == (0,)
    assert repeated.predict_proba(np.empty((0, 1))).shape == (0, 2)
    with pytest.raises(ValueError):repeated.score(np.empty((0, 1)))


def test_nonconvergence_collapse_and_transactional_refit(clustering_support):
    cls = clustering_support.load('gaussian-mixture-models').GaussianMixture
    with pytest.raises(clustering_support.ConvergenceError):
        cls(2, means_init=[[-.5], [.5]], max_iter=1, tol=1e-15).fit([[-1.], [-.2], [.4], [1.3]])
    model = cls(2, means_init=[[-3.], [3.]]).fit([[-3.1], [-3.], [-2.9], [2.9], [3.], [3.1]])
    before = model.predict([[-3.], [3.]])
    model.means_init = [[0.], [1e12]]
    with pytest.raises(clustering_support.ConvergenceError, match='collapsed'):
        model.fit([[0.], [.01], [.02]])
    assert_array_equal(model.predict([[-3.], [3.]]), before)
    with pytest.raises(clustering_support.ConvergenceError, match='covariance'):
        cls(1, reg_covar=1e-12).fit([[0., 0.], [1e12, 1e12]])


@pytest.mark.parametrize('kwargs', [{'n_components':0}, {'n_components':True}, {'reg_covar':0}, {'tol':0}, {'max_iter':0}, {'n_init':0}, {'random_state':-1}])
def test_invalid_hyperparameters(clustering_support, kwargs):
    with pytest.raises(ValueError):
        clustering_support.load('gaussian-mixture-models').GaussianMixture(**kwargs)


@pytest.mark.oracle
@pytest.mark.numerical
def test_uniform_feature_scale_maps_covariance_floor_and_density_units(clustering_support):
    cls = clustering_support.load('gaussian-mixture-models').GaussianMixture
    X = np.array([[-2.2], [-2.], [-1.8], [1.8], [2.], [2.2]])
    a = cls(2, means_init=[[-2.], [2.]], reg_covar=.01).fit(X)
    b = cls(2, means_init=[[-20.], [20.]], reg_covar=1.).fit(10*X)
    assert_allclose(b.means_, 10*a.means_, atol=1e-10)
    assert_allclose(b.covariances_, 100*a.covariances_, atol=1e-10)
    assert_allclose(b.predict_proba(10*X), a.predict_proba(X), atol=1e-12)
    assert_allclose(b.score_samples(10*X), a.score_samples(X)-np.log(10), atol=1e-10)


@pytest.mark.oracle
@pytest.mark.numerical
def test_huge_negative_equal_log_scores_still_normalize_responsibilities(clustering_support):
    model = clustering_support.load('gaussian-mixture-models').GaussianMixture(2).fit([[.1], [.1], [.1], [.1]])
    # Adding log(2) to a score near -5e29 rounds away in float64. Direct
    # shifted-exponential division must still return half mass per component.
    assert_allclose(model.predict_proba([[1e12]]), [[.5, .5]], atol=0, rtol=0)
    assert np.isfinite(model.score_samples([[1e12]])).all()
