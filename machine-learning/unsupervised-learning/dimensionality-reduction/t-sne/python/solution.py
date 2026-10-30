"""Exact dense t-SNE: perplexity search, Student-t KL and full gradient descent."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_support_path = Path(__file__).resolve().parents[2]/'support.py'
_spec = importlib.util.spec_from_file_location('atlas_b5_support', _support_path)
support = sys.modules.get(_spec.name)
if support is None:
    support = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = support
    _spec.loader.exec_module(support)

def joint_probabilities(X, perplexity):
    n = len(X); conditional = np.zeros((n,n)); betas = np.zeros(n)
    distances = support.squared_distances(X)
    target = np.log(perplexity)
    for i in range(n):
        mask = np.arange(n)!=i; d = distances[i,mask]; shifted = d-d.min()
        ties = np.count_nonzero(shifted==0)
        if perplexity < ties-1e-10:
            raise ValueError('perplexity below tied nearest-neighbor multiplicity')
        if perplexity == n-1:
            probabilities = np.full(n-1,1/(n-1)); beta = 0.
        else:
            lo, hi, beta = 0., np.inf, 1.
            for _ in range(128):
                weights = np.exp(-shifted*beta); probabilities = weights/weights.sum()
                positive = probabilities>0
                entropy = -np.sum(probabilities[positive]*np.log(probabilities[positive]))
                if abs(entropy-target)<=1e-7:break
                if entropy > target:
                    lo=beta;beta=(beta+hi)/2 if np.isfinite(hi) else beta*2
                else:
                    hi=beta;beta=(beta+lo)/2
            else:raise support.ConvergenceError('perplexity calibration did not resolve target')
        conditional[i,mask]=probabilities;betas[i]=beta
    return (conditional+conditional.T)/(2*n), conditional, betas


def kl_gradient(Y, P):
    distances = support.squared_distances(Y)
    numerator = 1/(1+distances); np.fill_diagonal(numerator,0)
    Q = numerator/numerator.sum()
    positive = P>0
    loss = float(np.sum(P[positive]*(np.log(P[positive])-np.log(Q[positive]))))
    weights = (P-Q)*numerator
    gradient = 4*(weights.sum(axis=1)[:,None]*Y-weights@Y)
    return loss, gradient


class TSNE:
    def __init__(self,n_components=2,perplexity=5.,max_iter=500,learning_rate=10.,tol=1e-8,random_state=0):
        self.n_components,self.perplexity,self.max_iter=n_components,perplexity,max_iter
        self.learning_rate,self.tol,self.random_state=learning_rate,tol,random_state
        self._parameters()

    def _parameters(self):
        support.integer(self.n_components,'n_components',1,3)
        support.scalar(self.perplexity,'perplexity',1,127)
        support.integer(self.max_iter,'max_iter',1,5000)
        support.scalar(self.learning_rate,'learning_rate',1e-6,100)
        support.scalar(self.tol,'tol',1e-12,1e-2)
        support.integer(self.random_state,'random_state',0,2**32-1)

    @support.numerical
    def fit(self,X,y=None):
        self._parameters();X=support.features(X,fitting=True,max_samples=128)
        if len(X)<3 or self.perplexity>len(X)-1:raise ValueError('t-SNE needs n>=3, perplexity<=n-1')
        A,mean=support.centered(X);scale=support.uniform_scale(A);A/=scale
        P,conditional,betas=joint_probabilities(A,self.perplexity)
        initial=np.random.default_rng(self.random_state).normal(0,1e-3,(len(X),self.n_components))
        embedding,diagnostics=support.optimize(initial,lambda Y:kl_gradient(Y,P),self.max_iter,self.learning_rate,self.tol)
        self.__dict__.update(diagnostics,n_features_in_=X.shape[1],embedding_=embedding,
            joint_probabilities_=P,conditional_probabilities_=conditional,precision_parameters_=betas,
            distance_scale_=scale,kl_divergence_=diagnostics['objective_history_'][-1])
        return self

    def fit_transform(self,X,y=None):
        return self.fit(X,y).embedding_.copy()

if __name__ == '__main__':support.main(TSNE)
