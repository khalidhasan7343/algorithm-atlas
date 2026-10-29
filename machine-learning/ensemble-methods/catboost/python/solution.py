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

from dataclasses import dataclass


@dataclass(frozen=True)
class ObliviousTree:
    splits: tuple
    values: np.ndarray

    def predict(self, X):
        codes = np.zeros(len(X), dtype=int)
        for feature, threshold in self.splits:
            codes = 2*codes+(X[:, feature] > threshold)
        return self.values[codes]


def _oblivious(X, y, depth):
    """Greedy symmetric squared-error tree; each level shares one split."""
    codes = np.zeros(len(X), dtype=int);splits = []
    center = float(y[0]) if np.all(y == y[0]) else float(y.mean())
    scale = float(np.max(np.abs(y-center)))
    target = (y-center)/scale if scale else np.zeros(len(y))
    def objective(partition, size):
        score = 0.0
        for leaf in range(size):
            values = target[partition == leaf]
            if len(values):score += float(np.sum((values-values.mean())**2))
        return score
    previous = objective(codes,1)
    for level in range(depth):
        best = None
        for feature in range(X.shape[1]):
            values = np.unique(X[:, feature])
            for lower, upper in zip(values[:-1], values[1:]):
                threshold = float(lower+(upper-lower)/2)
                if threshold >= upper:threshold = float(lower)
                partition = 2*codes+(X[:, feature] > threshold)
                error = objective(partition,2**(level+1))
                tolerance = 32*np.finfo(float).eps*max(previous,np.finfo(float).tiny)
                if error < previous-tolerance and (best is None or error < best[0]-tolerance):
                    best = error, feature, threshold, partition
        if best is None:break
        previous, feature, threshold, codes = best;splits.append((feature,threshold))
    values = np.zeros(2**len(splits))
    for leaf in range(len(values)):
        subset = y[codes == leaf]
        # Empty symmetric cells get zero update, never an undefined mean.
        if len(subset):values[leaf] = subset[0] if np.all(subset == subset[0]) else subset.mean()
    return ObliviousTree(tuple(splits),values)


class CatBoostRegressor(s.Regressor):
    """Naive ordered boosting (CatBoost paper Algorithm 1), ordered TS, symmetric trees.

    Each prefix has independent trees; no shared-structure approximation. Squared
    loss only. O(T*n) prefix trees deliberately trade speed for an auditable oracle.
    """
    def __init__(self, *, categorical_features=(), n_estimators=8, learning_rate=.1,
                 max_depth=2, prior=0.0, prior_weight=1.0, random_state=0):
        self.categorical_features = categorical_features
        self.n_estimators = s.integer(n_estimators, 'n_estimators', 1, 16)
        self.learning_rate = s.scalar(learning_rate, 'learning_rate', high=1, positive=True)
        self.max_depth = s.integer(max_depth, 'max_depth', 1, 3)
        self.prior = s.scalar(prior, 'prior', low=-1e12)
        self.prior_weight = s.scalar(prior_weight, 'prior_weight', high=1e6, positive=True)
        self.random_state = s.seed(random_state)

    @staticmethod
    def _raw(X, columns, *, fitting=False, expected=None):
        a = np.asarray(X, dtype=object)
        if a.ndim != 2 or not 1 <= a.shape[1] <= 8 or len(a) > (64 if fitting else 4096) or (fitting and len(a) == 0):
            raise ValueError('CatBoost supports n<=64 fitting/4096 prediction and 1..8 columns')
        if expected is not None and a.shape[1] != expected:raise ValueError('feature count differs')
        if not isinstance(columns, (tuple,list)) or any(type(j) is not int or not 0 <= j < a.shape[1] for j in columns) or len(set(columns)) != len(columns):
            raise ValueError('categorical_features must be unique native column indices')
        for j in range(a.shape[1]):
            values = a[:,j].tolist()
            if j in columns:
                strings = all(isinstance(v,str) and 1 <= len(v) <= 256 for v in values)
                ints = all(isinstance(v,(int,np.integer)) and not isinstance(v,(bool,np.bool_)) and -(2**63) <= int(v) < 2**63 for v in values)
                if not (strings or ints):raise ValueError('each categorical column needs homogeneous nonempty strings or int64 codes')
            else:
                if any(not isinstance(v,(int,float,np.integer,np.floating)) or isinstance(v,(bool,np.bool_)) for v in values):raise ValueError('numeric columns require real numbers')
                numeric = np.asarray(values,dtype=float)
                if not np.isfinite(numeric).all() or np.any(np.abs(numeric)>1e12):raise ValueError('numeric columns must be finite with magnitude<=1e12')
        return a.copy()

    @s.numerical
    def fit(self, X, y):
        raw = self._raw(X,self.categorical_features,fitting=True)
        columns = tuple(self.categorical_features);y = s.regression.targets(y,len(raw))
        total = s.integer(self.n_estimators,'n_estimators',1,16)
        rate = s.scalar(self.learning_rate,'learning_rate',high=1,positive=True)
        depth = s.integer(self.max_depth,'max_depth',1,3)
        prior = s.scalar(self.prior,'prior',low=-1e12)
        weight = s.scalar(self.prior_weight,'prior_weight',high=1e6,positive=True)
        order = np.random.default_rng(s.seed(self.random_state)).permutation(len(raw))
        transformed = np.empty(raw.shape,dtype=float);statistics = {}
        for j in range(raw.shape[1]):
            if j not in columns:transformed[:,j] = np.asarray(raw[:,j],dtype=float);continue
            running = {}
            for i in order:
                value = raw[i,j];count, mass = running.get(value,(0,0.0))
                transformed[i,j] = (mass+weight*prior)/(count+weight)
                running[value] = count+1,mass+y[i]
            statistics[j] = running
        X = transformed[order];target = y[order];n = len(X)
        # Prefix j predicts all positions, but is trained only on ranks < j.
        prefix_prediction = np.full((n+1,n),prior)
        prefixes = [[] for _ in range(n+1)];residual_history=[]
        for _ in range(total):
            residual = target-prefix_prediction[np.arange(n),np.arange(n)]
            residual_history.append(residual.copy())
            for length in range(1,n+1):
                model = _oblivious(X[:length],residual[:length],depth)
                prefixes[length].append(model)
                prefix_prediction[length] += rate*model.predict(X)
            s.finite(prefix_prediction,'prefix predictions')
        self.__dict__.update(n_features_in_=raw.shape[1], categorical_features_=columns,
            categorical_families_={j:('str' if isinstance(raw[0,j],str) else 'int') for j in columns},
            prior_=prior, prior_weight_=weight, learning_rate_=rate, permutation_=order.copy(),
            ordered_features_=transformed.copy(), target_statistics_=statistics,
            prefix_estimators_=prefixes, estimators_=prefixes[n],
            ordered_residuals_=np.array(residual_history), prefix_training_predictions_=prefix_prediction.copy())
        return self

    def transform(self, X):
        if not hasattr(self,'n_features_in_'):raise ValueError('fit must succeed before transformation')
        raw = self._raw(X,self.categorical_features_,expected=self.n_features_in_)
        out = np.empty(raw.shape,dtype=float)
        for j in range(raw.shape[1]):
            if j not in self.categorical_features_:out[:,j]=np.asarray(raw[:,j],dtype=float);continue
            if len(raw) and ('str' if isinstance(raw[0,j],str) else 'int') != self.categorical_families_[j]:
                raise ValueError('categorical label family differs from training')
            for i,value in enumerate(raw[:,j]):
                count,mass = self.target_statistics_[j].get(value,(0,0.0))
                out[i,j]=(mass+self.prior_weight_*self.prior_)/(count+self.prior_weight_)
        return s.finite(out)

    def staged_predict(self, X):
        X=self.transform(X);prediction=np.full(len(X),self.prior_)
        for model in self.estimators_:
            prediction += self.learning_rate_*model.predict(X)
            yield s.finite(prediction.copy())

    @s.numerical
    def predict(self, X):
        X=self.transform(X);prediction=np.full(len(X),self.prior_)
        for model in self.estimators_:
            prediction += self.learning_rate_*model.predict(X)
        return s.finite(prediction)


if __name__=='__main__':
    s.main(CatBoostRegressor)
