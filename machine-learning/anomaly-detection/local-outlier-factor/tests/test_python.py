import math
import numpy as np
from numpy.testing import assert_allclose
import pytest
pytestmark=pytest.mark.ml


def independent_lof(X,k):
    rows=[list(row) for row in X];n=len(rows)
    distance=[[math.sqrt(sum((a-b)**2 for a,b in zip(rows[i],rows[j]))) for j in range(n)] for i in range(n)]
    kdist=[sorted(distance[i][j] for j in range(n) if j!=i)[k-1] for i in range(n)]
    neighbors=[[j for j in range(n) if j!=i and distance[i][j]<=kdist[i]] for i in range(n)]
    reach=[[max(kdist[j],distance[i][j]) for j in neighbors[i]] for i in range(n)]
    mean=[sum(v)/len(v) for v in reach]
    result=[]
    for i in range(n):
        if mean[i]==0:result.append(1.)
        elif any(mean[j]==0 for j in neighbors[i]):result.append(np.inf)
        else:result.append(sum(mean[i]/mean[j] for j in neighbors[i])/len(neighbors[i]))
    return np.array(distance),np.array(kdist),neighbors,reach,np.array(mean),np.array(result)

@pytest.mark.oracle
@pytest.mark.parametrize('X,k',[([[-11.],[-10.],[0.],[10.]],1),([[0.],[1.],[2.],[10.]],2),([[0.,0.],[1.,0.],[0.,1.],[1.,1.],[4.,4.]],2),([[0.],[0.],[1.],[2.]],1),([[0.],[1.]],1)])
def test_independent_distance_neighborhood_reachability_density_and_lof(b12,X,k):
    expected=independent_lof(X,k);model=b12.load('local-outlier-factor').LocalOutlierFactor(k).fit(X)
    assert_allclose(model.distance_matrix_,expected[0],atol=1e-14)
    assert_allclose(model.k_distances_,expected[1],atol=1e-14)
    for actual,wanted in zip(model.neighborhoods_,expected[2]):assert actual.tolist()==wanted
    for actual,wanted in zip(model.reachability_distances_,expected[3]):assert_allclose(actual,wanted,atol=1e-14)
    assert_allclose(model.mean_reachability_,expected[4],atol=1e-14)
    assert_allclose(model.anomaly_scores(),expected[5],atol=2e-14)
    finite=expected[4]>0
    assert_allclose(model.lrd_[finite],1/expected[4][finite],atol=1e-14)
    if X==[[-11.],[-10.],[0.],[10.]]:
        assert model.neighborhoods_[2].tolist()==[1,3]
        assert_allclose(model.anomaly_scores(),[1.,1.,5.5,1.],atol=1e-14)

@pytest.mark.oracle
@pytest.mark.parametrize('k',[1,3,5])
def test_all_identical_duplicate_limit_is_one(b12,k):
    model=b12.load('local-outlier-factor').LocalOutlierFactor(k,contamination=.5).fit(np.ones((6,2)))
    assert model.zero_reachability_.all() and np.isposinf(model.lrd_).all()
    assert_allclose(model.anomaly_scores(),1,atol=0,rtol=0)
    assert_allclose(model.predict(),1)
    assert all(len(neighbors)==5 for neighbors in model.neighborhoods_)

@pytest.mark.numerical
@pytest.mark.oracle
@pytest.mark.parametrize('contamination,expected_labels',[('auto',[1,1,-1]),(.5,[1,1,-1]),(.25,[1,1,1])])
def test_structural_infinite_lof_and_extended_quantile_ties(b12,contamination,expected_labels):
    model=b12.load('local-outlier-factor').LocalOutlierFactor(1,contamination=contamination).fit([[0.],[0.],[3.]])
    assert_allclose(model.anomaly_scores()[:2],1)
    assert model.anomaly_scores()[-1]==np.inf
    assert not np.isnan(model.decision_function()).any()
    assert model.predict().tolist()==expected_labels
    if contamination==.25:
        assert model.threshold_==np.inf
        assert_allclose(model.decision_function(),[np.inf,np.inf,0])

@pytest.mark.numerical
@pytest.mark.parametrize('scale',[1e-200,1e-310])
def test_tiny_scale_log_density_avoids_infinity_ratio_errors(b12,scale):
    X=np.array([[0.],[1.],[2.],[5.]])
    reference=b12.load('local-outlier-factor').LocalOutlierFactor(1).fit(X)
    model=b12.load('local-outlier-factor').LocalOutlierFactor(1).fit(X*scale)
    assert not model.zero_reachability_.any()
    assert np.isfinite(model.log_lrd_).all()
    assert_allclose(model.anomaly_scores(),reference.anomaly_scores(),rtol=2e-12,atol=2e-12)
    if scale==1e-310:assert model.density_representation_overflow_.any()

@pytest.mark.numerical
def test_unrepresentable_finite_lof_is_explicit_error_and_fit_atomic(b12):
    cls=b12.load('local-outlier-factor').LocalOutlierFactor;model=cls(1).fit([[0.],[1.],[2.]])
    before=model.anomaly_scores()
    with pytest.raises(b12.NumericalError):model.fit([[0.],[1e-310],[1e12]])
    assert_allclose(model.anomaly_scores(),before,atol=0,rtol=0)

@pytest.mark.parametrize('seed',[21,22,23])
def test_two_density_clusters_and_isolated_point(b12,seed):
    rng=np.random.default_rng(seed);X=np.r_[rng.normal(0,.05,(30,2)),rng.normal(3,.3,(30,2)),[[12.,12.]]]
    m=b12.load('local-outlier-factor').LocalOutlierFactor(5,contamination=.05).fit(X)
    assert m.anomaly_scores()[-1]>np.quantile(m.anomaly_scores()[:-1],.95)
    assert m.predict()[-1]==-1
    assert_allclose(m.fit_predict(X),m.labels_)

@pytest.mark.reference
@pytest.mark.parametrize('seed',[0,1,2])
def test_sklearn_lof_only_matching_nontied_regular_scale_semantics(b12,seed):
    from sklearn.neighbors import LocalOutlierFactor
    X=np.random.default_rng(seed).normal(size=(35,3));k=5
    model=b12.load('local-outlier-factor').LocalOutlierFactor(k,contamination=.2).fit(X)
    reference=LocalOutlierFactor(n_neighbors=k,contamination=.2,novelty=False).fit(X)
    assert all(len(v)==k for v in model.neighborhoods_)
    assert_allclose(model.anomaly_scores(),-reference.negative_outlier_factor_,rtol=2e-8,atol=2e-8)
    assert_allclose(model.predict(),reference.fit_predict(X))

@pytest.mark.parametrize('kwargs',[dict(n_neighbors=0),dict(n_neighbors=True),dict(n_neighbors=256),dict(metric='manhattan'),dict(contamination=0),dict(contamination=.51)])
def test_invalid_parameters(b12,kwargs):
    with pytest.raises(ValueError):b12.load('local-outlier-factor').LocalOutlierFactor(**kwargs)

def test_small_data_invalid_neighborhood_and_unsupported_novelty(b12):
    cls=b12.load('local-outlier-factor').LocalOutlierFactor
    with pytest.raises(ValueError):cls(1).fit([[0.]])
    with pytest.raises(ValueError):cls(3).fit([[0.],[1.],[2.]])
    with pytest.raises(ValueError):cls(1).predict()
    model=cls(1).fit([[0.],[1.],[3.]])
    for method in (model.predict,model.score_samples,model.anomaly_scores,model.decision_function):
        with pytest.raises(ValueError):method([[0.]])

@pytest.mark.oracle
def test_permutation_translation_scale_and_feature_permutation(b12):
    X=np.array([[0.,0.],[1.,0.],[0.,1.],[2.,2.],[5.,5.]])
    cls=b12.load('local-outlier-factor').LocalOutlierFactor;a=cls(2).fit(X).anomaly_scores()
    order=np.array([4,1,3,0,2]);b=cls(2).fit(X[order]).anomaly_scores()
    assert_allclose(b,a[order],atol=1e-13)
    assert_allclose(cls(2).fit(10*X+100).anomaly_scores(),a,atol=1e-13)
    assert_allclose(cls(2).fit(X[:,::-1]).anomaly_scores(),a,atol=1e-13)
