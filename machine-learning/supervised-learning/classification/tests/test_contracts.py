import importlib.util
from pathlib import Path
import sys

import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest

if 'atlas_classification_support' not in sys.modules:
    spec=importlib.util.spec_from_file_location('atlas_classification_support',Path(__file__).parents[1]/'support.py');module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
support=sys.modules['atlas_classification_support']
CASES=[('logistic-regression','LogisticRegression',{}),('k-nearest-neighbors','KNearestNeighbors',{'n_neighbors':1}),('gaussian-naive-bayes','GaussianNaiveBayes',{}),('multinomial-naive-bayes','MultinomialNaiveBayes',{}),('bernoulli-naive-bayes','BernoulliNaiveBayes',{}),('support-vector-machines','SupportVectorMachine',{}),('cart-decision-trees','CARTClassifier',{}),('id3-decision-trees','ID3Classifier',{}),('c4-5-decision-trees','C45Classifier',{'categorical_features':[0,1]}),('linear-discriminant-analysis','LinearDiscriminantAnalysis',{}),('quadratic-discriminant-analysis','QuadraticDiscriminantAnalysis',{})]
pytestmark=pytest.mark.ml


@pytest.fixture(params=CASES,ids=[c[0] for c in CASES])
def estimator(request):
    topic,name,parameters=request.param
    return lambda:getattr(support.load(topic),name)(**parameters)


@pytest.mark.parametrize('X,y',[([[np.nan]],[0]),([[np.inf]],[0]),([[0]],[np.nan]),([[0]],[True]),([[0]],[.5]),([[0],[1]],[1,'1']),([[0]],[2**64]),([[0]],[b'a']),([[0]],['']),([[0]],['a'*257]),([[0],[1]],[[0],[1]]),([[0]],[0,1]),(np.empty((2,0)),[0,1]),([0,1],[0,1]),([[True]],[0]),([[1j]],[0]),([['1']],[0]),([[1e13]],[0])])
def test_shared_invalid_data_never_creates_fitted_state(estimator,X,y):
    model=estimator()
    with pytest.raises(ValueError):model.fit(X,y)
    with pytest.raises(ValueError):model.predict([[0]])


@pytest.mark.numerical
@pytest.mark.parametrize('labels',[[-9,-9,7,7],['negative','negative','positive','positive']])
def test_original_labels_determinism_owned_input_probability_order_and_failure_state(estimator,labels):
    X=np.array([[0.,0],[0,1],[1,0],[1,1]]);y=np.array(labels);saved=X.copy(),y.copy();rng_before=np.random.get_state()
    model=estimator();assert model.fit(X,y) is model
    repeated=estimator().fit(X,y);query=X.copy();prediction=model.predict(query)
    assert_array_equal(prediction,repeated.predict(query));assert_array_equal(model.classes_,sorted(set(labels)))
    assert prediction.shape==(4,) and set(prediction)<=set(labels)
    assert model.score(query,y)==pytest.approx(float(np.mean(prediction==y)))
    if hasattr(model,'predict_proba'):
        probability=model.predict_proba(query);assert probability.shape==(4,2)
        assert np.isfinite(probability).all() and np.all((probability>=0)&(probability<=1))
        assert_allclose(probability.sum(axis=1),1,atol=1e-12)
        assert_allclose(probability,repeated.predict_proba(query),atol=0,rtol=0)
        assert model.predict_proba(np.empty((0,2))).shape==(0,2)
    with pytest.raises(ValueError):model.fit([[np.nan,0]],[labels[0]])
    assert_array_equal(model.predict(query),prediction)
    X[:]=99;y[:]=labels[-1];assert_array_equal(model.predict(query),prediction)
    assert_array_equal(saved[0],query)
    assert model.predict(np.empty((0,2))).shape==(0,)
    for bad in ([[0]],[[np.inf,0]],[[True,False]],[[0,1,2]]):
        with pytest.raises(ValueError):model.predict(bad)
    rng_after=np.random.get_state();assert rng_before[0]==rng_after[0] and rng_before[2:]==rng_after[2:];assert_array_equal(rng_before[1],rng_after[1])
