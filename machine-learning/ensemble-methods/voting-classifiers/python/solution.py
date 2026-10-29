import importlib.util
from pathlib import Path
import sys

import numpy as np

if 'atlas_ensemble_support' not in sys.modules:
    _spec = importlib.util.spec_from_file_location('atlas_ensemble_support', Path(__file__).resolve().parents[2]/'support.py')
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = _module
    _spec.loader.exec_module(_module)
s = sys.modules['atlas_ensemble_support']

tree = s.module_at('atlas_ensemble_tree',s.ROOT/'tree.py')


def default_factories():
    return [lambda seed:tree.WeightedTree(task='classification',max_depth=1,random_state=seed),
            lambda seed:s.classification.load('gaussian-naive-bayes').GaussianNaiveBayes(var_smoothing=1e-3)]


class VotingClassifier(s.Classifier):
    """Fresh factory-based estimators; hard votes or aligned soft probabilities."""
    def __init__(self, estimators=None, *, voting='hard', weights=None, random_state=0):
        self.estimators = estimators
        if voting not in ('hard','soft'):raise ValueError('voting must be hard or soft')
        self.voting = voting
        self.weights = weights
        self.random_state = s.seed(random_state)

    @s.numerical
    def fit(self,X,y):
        X,_,classes,original = s.training(X,y,'classification')
        if self.voting not in ('hard','soft'):raise ValueError('voting must be hard or soft')
        factories = default_factories() if self.estimators is None else self.estimators
        if not isinstance(factories,(tuple,list)) or not 1 <= len(factories) <= 8:
            raise ValueError('1..8 seed-taking estimator factories required')
        weight = s.weights(self.weights,len(factories))
        rng = np.random.default_rng(s.seed(self.random_state));models=[]
        for factory in factories:
            model = s.new_estimator(factory,int(rng.integers(2**32)))
            if any(model is other for other in models):raise ValueError('independent estimators required')
            model.fit(X.copy(),original.copy())
            if self.voting=='soft':s.probability(model,X[:1],classes)
            else:s.label_votes(model,X[:1],classes)
            models.append(model)
        self.__dict__.update(n_features_in_=X.shape[1],classes_=classes.copy(),estimators_=models,
                             weights_=weight,voting_=self.voting)
        return self

    @s.numerical
    def predict_proba(self,X):
        X = self._check_X(X);out=np.zeros((len(X),len(self.classes_)))
        for weight,model in zip(self.weights_,self.estimators_):
            p=s.probability(model,X,self.classes_) if self.voting_=='soft' else s.label_votes(model,X,self.classes_)
            out += weight*p
        return out


if __name__=='__main__':
    s.main(VotingClassifier)
