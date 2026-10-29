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

tree=s.module_at('atlas_ensemble_tree',s.ROOT/'tree.py')


class _Stacking:
    def __init__(self, estimators=None, final_estimator=None, *, n_splits=3, random_state=0):
        self.estimators=estimators
        self.final_estimator=final_estimator
        self.n_splits=s.integer(n_splits,'n_splits',2,8)
        self.random_state=s.seed(random_state)

    @s.numerical
    def fit(self,X,y):
        X,encoded,classes,original=s.training(X,y,self._task)
        target=original if classes is not None else encoded
        splits=s.integer(self.n_splits,'n_splits',2,min(8,len(X)))
        rng=np.random.default_rng(s.seed(self.random_state))
        if classes is not None:
            if len(classes)>8 or any(np.sum(encoded==k)<splits for k in range(len(classes))):
                raise ValueError('stacking supports <=8 classes with at least n_splits observations/class')
            buckets=[[] for _ in range(splits)]
            for k in range(len(classes)):
                order=rng.permutation(np.flatnonzero(encoded==k))
                for fold,part in enumerate(np.array_split(order,splits)):buckets[fold].extend(part.tolist())
            folds=[np.sort(part) for part in map(np.array,buckets)]
        else:folds=[np.sort(part) for part in np.array_split(rng.permutation(len(X)),splits)]
        factories=self.estimators
        if factories is None:
            if classes is not None:
                factories=s.load('voting-classifiers').default_factories()
            else:
                factories=[lambda seed:s.regression.load('linear-regression').LinearRegression(),
                           lambda seed:tree.WeightedTree(max_depth=2,random_state=seed)]
        if not isinstance(factories,(tuple,list)) or not 1<=len(factories)<=8:raise ValueError('1..8 estimator factories required')
        final_factory=self.final_estimator
        if final_factory is None:
            final_factory=(lambda seed:s.classification.load('gaussian-naive-bayes').GaussianNaiveBayes(var_smoothing=1e-3)) if classes is not None else (lambda seed:s.regression.load('ridge-regression').RidgeRegression(alpha=1.0))
        width=len(classes) if classes is not None else 1
        oof=np.empty((len(X),len(factories)*width));seen=np.zeros(len(X),int)
        fold_models=[];instances=[];seeds=[]
        for held in folds:
            train=np.setdiff1d(np.arange(len(X)),held);local=[]
            for j,factory in enumerate(factories):
                seed=int(rng.integers(2**32));model=s.new_estimator(factory,seed)
                if any(model is previous for previous in instances):raise ValueError('factories must return independent unfitted instances')
                instances.append(model);seeds.append(seed)
                model.fit(X[train].copy(),target[train].copy())
                p=s.probability(model,X[held],classes) if classes is not None else s.regression_prediction(model,X[held])[:,None]
                oof[held,j*width:(j+1)*width]=p;local.append(model)
            seen[held]+=1;fold_models.append(local)
        if not np.all(seen==1):raise ValueError('each row must have exactly one held-out prediction')
        final=s.new_estimator(final_factory,int(rng.integers(2**32)))
        if any(final is previous for previous in instances):raise ValueError('independent meta estimator required')
        final.fit(oof.copy(),target.copy())
        if classes is not None:s.probability(final,oof[:1],classes)
        else:s.regression_prediction(final,oof[:1])
        models=[]
        for factory in factories:
            model=s.new_estimator(factory,int(rng.integers(2**32)))
            if model is final or any(model is previous for previous in instances+models):raise ValueError('independent refit estimators required')
            model.fit(X.copy(),target.copy());models.append(model)
        state=dict(n_features_in_=X.shape[1],estimators_=models,final_estimator_=final,
                   oof_predictions_=oof.copy(),fold_indices_=[v.copy() for v in folds],fold_estimators_=fold_models,
                   oof_counts_=seen,fold_estimator_seeds_=seeds)
        if classes is not None:state['classes_']=classes.copy()
        self.__dict__.update(state)
        return self

    @s.numerical
    def transform(self,X):
        X=self._check_X(X)
        if self._task=='classification':return np.hstack([s.probability(model,X,self.classes_) for model in self.estimators_])
        return np.column_stack([s.regression_prediction(model,X) for model in self.estimators_])


class StackingRegressor(_Stacking,s.Regressor):
    _task='regression'

    def predict(self,X):
        return s.regression_prediction(self.final_estimator_,self.transform(X)) if hasattr(self,'final_estimator_') else self._unfitted()

    @staticmethod
    def _unfitted():raise ValueError('fit must succeed before prediction')


class StackingClassifier(_Stacking,s.Classifier):
    _task='classification'

    def predict_proba(self,X):
        transformed=self.transform(X)
        return s.probability(self.final_estimator_,transformed,self.classes_)


if __name__=='__main__':
    s.main(StackingRegressor)
