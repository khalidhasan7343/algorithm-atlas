import numpy as np
from numpy.testing import assert_allclose
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.oracle
@pytest.mark.parametrize('values,fraction,expected',[([1,2,3,4],.5,2.5),([1,2,3,4],.25,3.25),([1,1,1,1],.25,1),([1,np.inf],.5,np.inf),([np.inf,np.inf],.5,np.inf)])
def test_linear_quantiles_and_extended_ties(b12,values,fraction,expected):
    assert b12.training_threshold(values,fraction,1.5)==expected
    result=b12.decision_from_anomaly(values,expected)
    assert not np.isnan(result).any()
    if np.isinf(expected):assert_allclose(result[np.isinf(values)],0)

@pytest.mark.parametrize('fraction',[0.,-1.,.51,True,np.nan,np.inf,'bad',None])
def test_invalid_contamination(b12,fraction):
    with pytest.raises(ValueError):b12.contamination(fraction)

@pytest.mark.oracle
def test_metric_ties_orientation_confusion_and_undefined(b12):
    result=b12.anomaly_metrics([1,-1,1,-1],[1,-1,-1,1],[.1,.9,.9,.2])
    assert result['confusion_matrix']==[[1,1],[1,1]]
    assert_allclose([result['precision'],result['recall'],result['f1'],result['roc_auc'],result['average_precision']],[.5,.5,.5,.625,7/12])
    no_positive=b12.anomaly_metrics([1,1],[1,1],[0.,0.]);assert no_positive['precision'] is None and no_positive['recall'] is None and no_positive['f1'] is None and no_positive['roc_auc'] is None and no_positive['average_precision'] is None
    infinite=b12.anomaly_metrics([1,-1],[1,-1],[0,np.inf]);assert infinite['roc_auc']==infinite['average_precision']==1

@pytest.mark.reference
@pytest.mark.parametrize('seed',[0,1,2])
def test_metrics_match_independent_sklearn_with_tied_scores(b12,seed):
    from sklearn.metrics import roc_auc_score,average_precision_score,confusion_matrix
    rng=np.random.default_rng(seed);actual=rng.choice([-1,1],40);predicted=rng.choice([-1,1],40);scores=rng.integers(0,5,40).astype(float)
    metrics=b12.anomaly_metrics(actual,predicted,scores)
    assert_allclose(metrics['roc_auc'],roc_auc_score(actual==-1,scores),atol=1e-15)
    assert_allclose(metrics['average_precision'],average_precision_score(actual==-1,scores),atol=1e-15)
    assert metrics['confusion_matrix']==confusion_matrix(actual,predicted,labels=[1,-1]).tolist()

@pytest.mark.parametrize('X',[[],[1.,2.],np.empty((0,2)),[[np.nan]],[[np.inf]],[[True]],[['1']],np.ones((257,1)),np.ones((2,33)),[[1e13]]])
def test_feature_validation_and_if_failed_fit_atomicity(b12,X):
    cls=b12.load('isolation-forest').IsolationForest;model=cls(2).fit([[0.],[1.],[2.]])
    before=model.anomaly_scores([[0.],[1.]])
    with pytest.raises(ValueError):model.fit(X)
    assert_allclose(model.anomaly_scores([[0.],[1.]]),before)

@pytest.mark.oracle
@pytest.mark.numerical
def test_approved_distance_and_kernel_reuse_matches_independent_math(b12):
    X=np.array([[1e10,1e10],[1e10+1,1e10+2],[1e10+3,1e10-1]])
    distances=b12.b4.pairwise(X)
    expected=np.array([[0,np.sqrt(5),np.sqrt(10)],[np.sqrt(5),0,np.sqrt(13)],[np.sqrt(10),np.sqrt(13),0]])
    assert_allclose(distances,expected,atol=1e-14)
    assert_allclose(b12.kernel(X,X,.2),np.exp(-.2*expected**2),atol=1e-15)

@pytest.fixture(params=['isolation-forest','one-class-svm','local-outlier-factor'])
def detector_factory(request,b12):
    factories={'isolation-forest':lambda:b12.load('isolation-forest').IsolationForest(3),
               'one-class-svm':lambda:b12.load('one-class-svm').OneClassSVM(.3),
               'local-outlier-factor':lambda:b12.load('local-outlier-factor').LocalOutlierFactor(1)}
    return request.param,factories[request.param]

@pytest.mark.parametrize('bad',[[],[1,2],np.empty((0,2)),[[np.nan]],[[np.inf]],[[True]],np.ones((257,1)),np.ones((2,33)),[[1e13]]])
def test_all_detector_invalid_feature_contracts_preserve_fitted_state(b12,detector_factory,bad):
    topic,factory=detector_factory;X=np.array([[0.],[1.],[2.],[4.]])
    model=factory().fit(X);before=model.anomaly_scores() if topic=='local-outlier-factor' else model.anomaly_scores(X)
    with pytest.raises(ValueError):model.fit(bad)
    actual=model.anomaly_scores() if topic=='local-outlier-factor' else model.anomaly_scores(X)
    assert_allclose(actual,before,atol=0,rtol=0)

@pytest.mark.parametrize('features',[1,2,32])
def test_high_dimensional_constant_columns_and_owned_training_data(b12,detector_factory,features):
    topic,factory=detector_factory;X=np.random.default_rng(244).normal(size=(12,features));X[:,0]=3.
    original=X.copy();model=factory().fit(X);expected=model.anomaly_scores_.copy();X[:]=100
    actual=model.anomaly_scores() if topic=='local-outlier-factor' else model.anomaly_scores(original)
    assert_allclose(actual,expected,atol=1e-13)
    assert not np.isnan(actual).any()

@pytest.mark.parametrize('fraction',[1e-12,.1,.5])
def test_training_only_contamination_threshold_and_boundary_ties(b12,fraction):
    X=np.array([[0.],[1.],[2.],[3.],[10.]])
    for model in (b12.load('isolation-forest').IsolationForest(12,contamination=fraction),b12.load('local-outlier-factor').LocalOutlierFactor(2,contamination=fraction)):
        model.fit(X)
        assert_allclose(model.threshold_,np.quantile(model.anomaly_scores_,1-fraction,method='linear'),atol=1e-14)
        if isinstance(model,b12.load('isolation-forest').IsolationForest):
            before=model.threshold_;model.predict([[1e12]]);assert model.threshold_==before

@pytest.mark.parametrize('actual,predicted,scores',[([],[],[]),([1],[-1,-1],[0.]),([0],[1],[0.]),([True],[1],[0.]),([1],[1],[np.nan]),([1],[1],[-np.inf])])
def test_invalid_metric_inputs(b12,actual,predicted,scores):
    with pytest.raises(ValueError):b12.anomaly_metrics(actual,predicted,scores)

def test_svm_work_guard_and_default_gamma(b12):
    cls=b12.load('one-class-svm').OneClassSVM
    with pytest.raises(ValueError):cls(max_iter=20000).fit(np.ones((256,1)))
    model=cls().fit(np.ones((4,2)));assert model.gamma_==.5
