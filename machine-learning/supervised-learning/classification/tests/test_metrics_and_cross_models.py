from pathlib import Path
import importlib.util
import sys

import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
from sklearn.metrics import accuracy_score,confusion_matrix,precision_recall_fscore_support,log_loss as reference_log_loss

BASE=Path(__file__).parents[1]
spec=importlib.util.spec_from_file_location('classification_metrics_tests',BASE/'metrics.py');metrics=importlib.util.module_from_spec(spec);spec.loader.exec_module(metrics)
support=sys.modules['atlas_classification_support']
pytestmark=pytest.mark.ml


@pytest.mark.numerical
def test_hand_metrics_positive_class_orientation_zero_division_and_log_loss():
    result=metrics.classification_report(['a','a','b','b'],['a','b','b','b'])
    assert result['confusion_matrix']==[[1,1],[0,2]] and result['accuracy']==.75
    assert result['binary']['positive_label']=='b';assert_allclose([result['binary'][k] for k in ('precision','recall','f1')],[2/3,1,4/5])
    absent=metrics.classification_report([0,0],[0,0],classes=[0,1]);assert absent['per_class'][1]['f1']==0
    assert absent['macro']['recall']==.5 and absent['weighted']['recall']==1
    assert_allclose(metrics.log_loss([0,1],[[.8,.2],[.1,.9]],[0,1]),-(np.log(.8)+np.log(.9))/2)
    assert_allclose(metrics.log_loss([1],[[1.,0.]],[0,1]),-np.log(1e-15))


@pytest.mark.reference
def test_seeded_multiclass_metrics_against_independent_reference():
    rng=np.random.default_rng(14911)
    for classes in ([-4,2,9],['a','b','c']):
        y=np.array(classes)[rng.integers(0,3,50)];p=np.array(classes)[rng.integers(0,3,50)]
        report=metrics.classification_report(y,p,classes=classes)
        assert_allclose(report['accuracy'],accuracy_score(y,p));assert_array_equal(report['confusion_matrix'],confusion_matrix(y,p,labels=classes))
        for average in ('macro','weighted'):
            expected=precision_recall_fscore_support(y,p,labels=classes,average=average,zero_division=0)[:3]
            assert_allclose([report[average][k] for k in ('precision','recall','f1')],expected,atol=1e-14)
        probabilities=rng.uniform(.1,1,size=(50,3));probabilities/=probabilities.sum(axis=1,keepdims=True)
        assert_allclose(metrics.log_loss(y,probabilities,classes),reference_log_loss(y,probabilities,labels=classes),atol=1e-14)


@pytest.mark.parametrize('probabilities',[[[.2,.2]],[[-.1,1.1]],[[np.nan,1]],[[True,False]],[[.2,.3,.5]],[.5,.5]])
def test_invalid_probability_contract(probabilities):
    with pytest.raises(ValueError):metrics.log_loss([0],probabilities,[0,1])


def test_label_order_and_metric_domain_errors():
    with pytest.raises(ValueError):metrics.log_loss([0],[[.2,.8]],[1,0])
    with pytest.raises(ValueError):metrics.classification_report([0],[1],classes=[0])
    with pytest.raises(ValueError):metrics.classification_report([0],[1],positive_label=True)
    with pytest.raises(ValueError):metrics.classification_report([0,1,2],[0,1,2],positive_label=1)


@pytest.mark.numerical
def test_logistic_and_linear_svm_separable_geometry_without_probability_equivalence():
    X=np.array([[-2.,0],[-1,0],[1,0],[2,0]]);y=['a','a','b','b']
    logistic=support.load('logistic-regression').LogisticRegression(alpha=.1).fit(X,y)
    svm=support.load('support-vector-machines').SupportVectorMachine(tol=1e-9).fit(X,y)
    assert_array_equal(logistic.predict(X),y);assert_array_equal(svm.predict(X),y)
    assert logistic.coef_[0]>0 and svm.coef_[0]>0
    assert not hasattr(svm,'predict_proba')


@pytest.mark.numerical
def test_shared_covariance_lda_qda_boundaries_but_different_covariance_normalization():
    X=[[-3.],[-1.],[1.],[3.]];y=[0,0,1,1];query=[[-5.],[-.1],[.1],[5.]]
    lda=support.load('linear-discriminant-analysis').LinearDiscriminantAnalysis(reg=0).fit(X,y)
    qda=support.load('quadratic-discriminant-analysis').QuadraticDiscriminantAnalysis(reg_param=0).fit(X,y)
    assert_array_equal(lda.predict(query),qda.predict(query))
    assert_allclose(lda.covariance_,[[1]]);assert_allclose(qda.covariance_,[[[2]],[[2]]])
    assert not np.allclose(lda.predict_proba(query),qda.predict_proba(query))


@pytest.mark.numerical
def test_id3_gain_and_c45_ratio_choose_different_justified_features():
    X=np.column_stack((np.arange(8),[0]*4+[1]*4));y=[0]*4+[1]*4
    id3=support.load('id3-decision-trees').ID3Classifier().fit(X,y)
    c45=support.load('c4-5-decision-trees').C45Classifier(categorical_features=[0,1]).fit(X,y)
    assert id3.tree_.feature==0 and c45.tree_.feature==1
    assert_array_equal(id3.predict(X),y);assert_array_equal(c45.predict(X),y)
