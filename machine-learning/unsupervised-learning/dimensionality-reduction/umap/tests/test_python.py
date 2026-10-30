import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.oracle
@pytest.mark.numerical
def test_exact_knn_local_connectivity_union_and_tiny_graph(b5):
    module=b5.load('umap');X=np.array([[0.],[1.],[3.],[7.]])
    G,state=module.fuzzy_graph(X,2);D=state['directed_memberships_']
    assert_array_equal(state['knn_indices_'],[[1,2],[0,2],[1,0],[2,1]])
    assert_allclose(state['rho_'],[1,1,2,4])
    assert_allclose(np.diag(G),0);assert_allclose(G,G.T)
    assert np.all((D>=0)&(D<=1)) and np.all((G>=0)&(G<=1))
    for i in range(4):
        for j in range(4):assert_allclose(G[i,j],D[i,j]+D[j,i]-D[i,j]*D[j,i])
    assert_allclose(G,[[0,1,0,0],[1,0,1,0],[0,1,0,1],[0,0,1,0]])

@pytest.mark.reference
@pytest.mark.parametrize('seed',[17025,17026,17027])
def test_independent_sklearn_knn_scipy_local_scale_oracle(b5,seed):
    from sklearn.neighbors import NearestNeighbors
    from scipy.optimize import brentq
    X=np.random.default_rng(seed).normal(size=(12,3));k=4
    distances,indices=NearestNeighbors(n_neighbors=k+1).fit(X).kneighbors(X)
    distances,indices=distances[:,1:],indices[:,1:]
    G,state=b5.load('umap').fuzzy_graph(X,k)
    assert_array_equal(state['knn_indices_'],indices);assert_allclose(state['knn_distances_'],distances,atol=1e-13)
    D=np.zeros((len(X),len(X)))
    for i,row in enumerate(distances):
        rho=row[0];delta=np.maximum(row-rho,0)
        sigma=brentq(lambda width:np.exp(-delta/width).sum()-np.log2(k),1e-12,100,xtol=1e-14)
        D[i,indices[i]]=np.exp(-delta/sigma)
    assert_allclose(G,D+D.T-D*D.T,atol=3e-8)

@pytest.mark.oracle
@pytest.mark.numerical
def test_dense_cross_entropy_gradient_and_attraction_repulsion(b5):
    module=b5.load('umap');Y=np.array([[0.,0.],[1.,0.],[0.,2.]])
    G=np.array([[0,.8,0],[.8,0,.2],[0,.2,0]])
    loss,g=module.cross_entropy_gradient(Y,G,a=1.3);expected=0.
    for i in range(3):
        for j in range(i+1,3):
            q=1/(1+1.3*(sum((Y[i]-Y[j])**2)+1e-6));w=G[i,j]
            expected+=w*np.log(w/q) if w else 0
            expected+=(1-w)*np.log((1-w)/(1-q)) if w<1 else 0
    assert_allclose(loss,expected,atol=1e-12)
    numeric=np.empty_like(Y)
    for index in np.ndindex(Y.shape):
        plus=Y.copy();minus=Y.copy();plus[index]+=1e-6;minus[index]-=1e-6
        numeric[index]=(module.cross_entropy_gradient(plus,G,1.3)[0]-module.cross_entropy_gradient(minus,G,1.3)[0])/2e-6
    assert_allclose(g,numeric,atol=3e-9,rtol=1e-6);assert_allclose(g.sum(0),0,atol=1e-14)
    pair=np.array([[0.,0.],[1.,0.]])
    assert module.cross_entropy_gradient(pair,np.array([[0,1.],[1.,0]]))[1][0,0]<0
    assert module.cross_entropy_gradient(pair,np.zeros((2,2)))[1][0,0]>0

@pytest.mark.numerical
@pytest.mark.parametrize('X',[np.zeros((5,2)),[[0,0],[0,0],[0,0],[10,10],[10,10],[10,10]]])
def test_duplicates_disconnected_finite_and_deterministic(b5,X):
    cls=b5.load('umap').UMAP;m=cls(n_neighbors=2,max_iter=30).fit(X)
    assert np.isfinite(m.embedding_).all();assert np.all(np.diff(m.objective_history_)<=1e-10)
    assert m.n_iter_<=30;assert m.saturated_rows_.any()
    assert_array_equal(m.embedding_,cls(n_neighbors=2,max_iter=30).fit_transform(X))
    assert not hasattr(m,'transform')
    if len(X)==6:assert_allclose(m.graph_[:3,3:],0)

@pytest.mark.parametrize('kwargs',[{'n_neighbors':1},{'n_components':0},{'a':0},{'max_iter':0},{'random_state':-1}])
def test_invalid_parameters(b5,kwargs):
    with pytest.raises(ValueError):b5.load('umap').UMAP(**kwargs)

def test_neighbor_sample_bound_and_finite_budget_status(b5):
    cls=b5.load('umap').UMAP
    with pytest.raises(ValueError):cls(n_neighbors=4).fit(np.eye(4))
    m=cls(n_neighbors=2,max_iter=1,tol=1e-12).fit([[0],[1],[3],[10]])
    assert not m.converged_ and m.optimization_status_=='budget-exhausted' and m.n_iter_==1
