"""Exact fuzzy-neighbor UMAP with dense, smoothed full cross-entropy descent."""
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

def fuzzy_graph(X,k):
    n=len(X);distances=np.sqrt(support.squared_distances(X))
    np.fill_diagonal(distances,np.inf)
    indices=np.argsort(distances,axis=1,kind='stable')[:,:k]
    nearest=np.take_along_axis(distances,indices,axis=1)
    rho=np.zeros(n);sigma=np.zeros(n);saturated=np.zeros(n,dtype=bool)
    directed=np.zeros((n,n));target=np.log2(k)
    for i,row in enumerate(nearest):
        positive=row[row>0];rho[i]=positive[0] if len(positive) else 0.
        delta=np.maximum(row-rho[i],0)
        floor=1e-12*max(float(row.mean()),1e-12)
        lower=floor;upper=max(float(row.max()),floor)
        if np.exp(-delta/floor).sum()>=target:
            width=floor;saturated[i]=True
        else:
            while np.exp(-delta/upper).sum()<target:upper*=2
            for _ in range(100):
                width=(lower+upper)/2;mass=np.exp(-delta/width).sum()
                if abs(mass-target)<=1e-8:break
                if mass>target:upper=width
                else:lower=width
            else:raise support.ConvergenceError('UMAP local-scale calibration exhausted')
        sigma[i]=width;directed[i,indices[i]]=np.exp(-delta/width)
    graph=directed+directed.T-directed*directed.T
    return graph,dict(knn_indices_=indices,knn_distances_=nearest,rho_=rho,sigmas_=sigma,
                      directed_memberships_=directed,saturated_rows_=saturated)


def cross_entropy_gradient(Y,graph,a=1.,epsilon=1e-6):
    n=len(Y);gradient=np.zeros_like(Y);loss=0.
    for i in range(n-1):
        difference=Y[i]-Y[i+1:];z=np.sum(difference*difference,axis=1)+epsilon
        w=graph[i,i+1:];q=1/(1+a*z)
        # Cross-entropy minus graph entropy (constant), using stable logs.
        terms=w*np.log1p(a*z)+(1-w)*np.log1p(1/(a*z))
        positive=w>0;less=w<1
        terms[positive]+=w[positive]*np.log(w[positive])
        terms[less]+=(1-w[less])*np.log1p(-w[less])
        loss+=float(terms.sum())
        pair=2*((w-q)/z)[:,None]*difference
        gradient[i]+=pair.sum(axis=0);gradient[i+1:]-=pair
    return loss,gradient


class UMAP:
    def __init__(self,n_components=2,n_neighbors=5,a=1.,max_iter=300,learning_rate=1.,tol=1e-6,random_state=0):
        self.n_components,self.n_neighbors,self.a=n_components,n_neighbors,a
        self.max_iter,self.learning_rate,self.tol,self.random_state=max_iter,learning_rate,tol,random_state
        self._parameters()

    def _parameters(self):
        support.integer(self.n_components,'n_components',1,3)
        support.integer(self.n_neighbors,'n_neighbors',2,127)
        support.scalar(self.a,'a',1e-3,1e3)
        support.integer(self.max_iter,'max_iter',1,5000)
        support.scalar(self.learning_rate,'learning_rate',1e-6,100)
        support.scalar(self.tol,'tol',1e-12,1e-2)
        support.integer(self.random_state,'random_state',0,2**32-1)

    @support.numerical
    def fit(self,X,y=None):
        self._parameters();X=support.features(X,fitting=True,max_samples=128)
        if len(X)<3 or self.n_neighbors>=len(X):raise ValueError('UMAP requires 2<=neighbors<n, n>=3')
        A,mean=support.centered(X);scale=support.uniform_scale(A);A/=scale
        graph,graph_state=fuzzy_graph(A,self.n_neighbors)
        initial=np.random.default_rng(self.random_state).normal(0,1,(len(X),self.n_components))
        embedding,diagnostics=support.optimize(initial,lambda Y:cross_entropy_gradient(Y,graph,self.a),self.max_iter,self.learning_rate,self.tol)
        self.__dict__.update(graph_state,**diagnostics,n_features_in_=X.shape[1],embedding_=embedding,
                            graph_=graph,distance_scale_=scale,cross_entropy_=diagnostics['objective_history_'][-1])
        return self

    def fit_transform(self,X,y=None):return self.fit(X,y).embedding_.copy()

if __name__ == '__main__':support.main(UMAP)
