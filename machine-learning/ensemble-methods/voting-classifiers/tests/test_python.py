import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


class Fixed:
    def __init__(self,label,classes,p):self.label=label;self.order=classes;self.p=p
    def fit(self,X,y):self.classes_=np.array(self.order);return self
    def predict(self,X):return np.full(len(X),self.label)
    def predict_proba(self,X):return np.tile(self.p,(len(X),1))


@pytest.mark.oracle
@pytest.mark.parametrize('voting',['hard','soft'])
def test_reordered_classes_weighting_and_ties(ensemble_support,voting):
    factories=[lambda seed:Fixed('z',['z','a'],[.75,.25]),lambda seed:Fixed('a',['a','z'],[.75,.25])]
    model=ensemble_support.load('voting-classifiers').VotingClassifier(factories,voting=voting,weights=[1,3]).fit([[0],[1]],['a','z'])
    expected=[.75,.25] if voting=='hard' else [.625,.375]
    assert_allclose(model.predict_proba([[9]]),[expected]);assert_array_equal(model.predict([[9]]),['a'])
    assert_array_equal(model.classes_,['a','z'])
    assert len({id(m) for m in model.estimators_})==2
    tied=ensemble_support.load('voting-classifiers').VotingClassifier(factories,voting=voting).fit([[0],[1]],['a','z'])
    assert_allclose(tied.predict_proba([[9]]),[[.5,.5]])
    assert_array_equal(tied.predict([[9]]),['a'])


@pytest.mark.reference
@pytest.mark.parametrize('voting',['hard','soft'])
def test_sklearn_aligned_trees(ensemble_support,voting):
    from sklearn.ensemble import VotingClassifier
    from sklearn.tree import DecisionTreeClassifier
    s=ensemble_support;tree=s.module_at('atlas_ensemble_tree',s.ROOT/'tree.py');X=np.arange(15.)[:,None];y=np.repeat(['a','b','c'],5)
    factories=[lambda seed:tree.WeightedTree(task='classification',max_depth=1,random_state=seed),lambda seed:tree.WeightedTree(task='classification',max_depth=2,random_state=seed)]
    model=s.load('voting-classifiers').VotingClassifier(factories,voting=voting,weights=[1,2]).fit(X,y)
    ref=VotingClassifier([('a',DecisionTreeClassifier(max_depth=1,random_state=0)),('b',DecisionTreeClassifier(max_depth=2,random_state=0))],voting=voting,weights=[1,2]).fit(X,y)
    assert_array_equal(model.predict(X),ref.predict(X))
    if voting=='soft':assert_allclose(model.predict_proba(X),ref.predict_proba(X))


@pytest.mark.parametrize('weights',[[0,0],[-1,2],[np.inf,1],[1],[True,False]])
def test_invalid_weights(ensemble_support,weights):
    with pytest.raises(ValueError):ensemble_support.load('voting-classifiers').VotingClassifier(weights=weights).fit([[0],[1]],[0,1])


def test_missing_probability_contract_and_bad_probabilities(ensemble_support):
    class Hard:
        def fit(self,X,y):return self
        def predict(self,X):return np.zeros(len(X),int)
    cls=ensemble_support.load('voting-classifiers').VotingClassifier
    with pytest.raises(ValueError):cls([lambda seed:Hard()],voting='soft').fit([[0],[1]],[0,1])
    for p in ([.1,.1],[-1,2],[np.nan,1]):
        with pytest.raises(ValueError):cls([lambda seed:Fixed('a',['a','b'],p)],voting='soft').fit([[0],[1]],['a','b'])


def test_invalid_factories_and_zero_weight_does_not_skip_contract(ensemble_support):
    cls=ensemble_support.load('voting-classifiers').VotingClassifier
    for factories in ([],[1],tuple(range(9))):
        with pytest.raises(ValueError):cls(factories).fit([[0],[1]],[0,1])
    # Even a zero-weight estimator must satisfy the declared protocol.
    with pytest.raises(ValueError):cls([lambda seed:object(),lambda seed:object()],weights=[0,1]).fit([[0],[1]],[0,1])
