import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.oracle
@pytest.mark.numerical
def test_probability_normalization_perplexity_and_kl(b5):
    module=b5.load('t-sne');X=np.array([[0.],[1.],[3.],[7.]])
    P,C,beta=module.joint_probabilities(X,2.)
    assert_allclose(C.sum(1),1);assert_allclose(P,P.T);assert_allclose(P.sum(),1)
    assert_allclose(np.diag(P),0)
    for i in range(4):
        indices=np.arange(4)!=i;d=(X[indices,0]-X[i,0])**2
        v=np.exp(-(d-d.min())*beta[i]);v/=v.sum()
        assert_allclose(C[i,indices],v,atol=1e-13)
        assert_allclose(np.exp(-np.sum(v[v>0]*np.log(v[v>0]))),2,rtol=2e-7)
    Y=np.array([[0.,0.],[1.,0.],[0.,2.],[1.,3.]])
    Q=np.zeros((4,4))
    for i in range(4):
        for j in range(4):
            if i!=j:Q[i,j]=1/(1+sum((Y[i]-Y[j])**2))
    Q/=Q.sum();mask=P>0
    expected=sum(P[mask]*np.log(P[mask]/Q[mask]))
    assert_allclose(module.kl_gradient(Y,P)[0],expected,atol=1e-13)

@pytest.mark.oracle
@pytest.mark.numerical
def test_finite_difference_gradient_translation_rotation(b5):
    module=b5.load('t-sne');rng=np.random.default_rng(17021)
    P,_,_=module.joint_probabilities(rng.normal(size=(6,3)),3)
    Y=rng.normal(size=(6,2));loss,g=module.kl_gradient(Y,P);numerical=np.empty_like(Y)
    for index in np.ndindex(Y.shape):
        plus=Y.copy();minus=Y.copy();plus[index]+=1e-6;minus[index]-=1e-6
        numerical[index]=(module.kl_gradient(plus,P)[0]-module.kl_gradient(minus,P)[0])/2e-6
    assert_allclose(g,numerical,atol=3e-9,rtol=1e-6)
    assert_allclose(g.sum(0),0,atol=1e-14)
    R=np.array([[0,-1],[1,0]])
    assert_allclose(module.kl_gradient(Y@R+10,P)[0],loss,atol=1e-13)

@pytest.mark.reference
def test_sklearn_joint_probability_reference(b5):
    from sklearn.manifold._t_sne import _joint_probabilities
    from scipy.spatial.distance import pdist,squareform
    X=np.random.default_rng(17022).normal(size=(10,3));D=squareform(pdist(X,'sqeuclidean'))
    ref=squareform(_joint_probabilities(D,4.,0));ours,_,_=b5.load('t-sne').joint_probabilities(X,4.)
    # sklearn's float32 binary search uses looser entropy stopping.
    assert_allclose(ours,ref,atol=4e-7,rtol=2e-4)

@pytest.mark.parametrize('seed',[17023,17024])
def test_determinism_objective_descent_bounded_budget(b5,seed):
    X=np.random.default_rng(seed).normal(size=(12,3));cls=b5.load('t-sne').TSNE
    m=cls(perplexity=3,max_iter=50,random_state=seed).fit(X)
    assert_array_equal(m.embedding_,cls(perplexity=3,max_iter=50,random_state=seed).fit_transform(X))
    assert np.isfinite(m.embedding_).all() and np.all(np.diff(m.objective_history_)<=1e-12)
    assert m.kl_divergence_<m.objective_history_[0]
    assert m.n_iter_<=50 and m.optimization_status_ in ('gradient-tolerance','budget-exhausted')
    assert not hasattr(m,'transform')

@pytest.mark.numerical
def test_duplicate_constant_and_impossible_perplexities(b5):
    cls=b5.load('t-sne').TSNE
    m=cls(perplexity=3,max_iter=10).fit(np.ones((4,2)))
    assert_allclose(m.joint_probabilities_,(np.ones((4,4))-np.eye(4))/12)
    with pytest.raises(ValueError):cls(perplexity=1).fit(np.ones((4,2)))
    with pytest.raises(ValueError):cls(perplexity=4).fit(np.ones((4,2)))
    with pytest.raises(ValueError):cls(perplexity=1).fit([[0],[1]])

@pytest.mark.parametrize('kwargs',[{'perplexity':0},{'max_iter':0},{'n_components':4},{'random_state':None},{'learning_rate':float('inf')}])
def test_invalid_parameters(b5,kwargs):
    with pytest.raises(ValueError):b5.load('t-sne').TSNE(**kwargs)
