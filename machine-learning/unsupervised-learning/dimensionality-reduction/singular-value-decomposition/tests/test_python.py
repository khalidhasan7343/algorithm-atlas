import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.oracle
@pytest.mark.numerical
@pytest.mark.parametrize('X', [np.diag([3.,1.,2.]), [[1.,2.],[3.,4.],[5.,6.]], [[1.,2.,3.],[4.,5.,6.]], np.zeros((4,3)), [[1.,2.],[2.,4.],[3.,6.]], np.eye(3)])
def test_factorization_rank_and_orthogonality(b5,X):
    X=np.asarray(X);m=b5.load('singular-value-decomposition').SVD().fit(X)
    U,s,V=m.left_singular_vectors_,m.singular_values_,m.components_
    assert_allclose((U*s)@V,X,atol=2e-11)
    assert_allclose(U.T@U,np.eye(len(s)),atol=2e-11)
    assert_allclose(V@V.T,np.eye(len(s)),atol=2e-11)
    assert np.all(s>=0) and np.all(np.diff(s)<=0)
    assert_allclose(m.transform(X),U*s,atol=2e-11)
    assert_allclose(m.inverse_transform(m.transform(X)),X,atol=2e-11)

@pytest.mark.reference
@pytest.mark.parametrize('seed',[17001,17002,17003])
def test_numpy_reference_random_and_truncation(b5,seed):
    X=np.random.default_rng(seed).normal(size=(17,5));m=b5.load('singular-value-decomposition').SVD(2).fit(X)
    U,s,V=np.linalg.svd(X,full_matrices=False)
    assert_allclose(m.full_singular_values_,s,rtol=1e-10,atol=1e-12)
    assert_allclose(m.components_.T@m.components_,V[:2].T@V[:2],atol=1e-10)
    assert_allclose(np.linalg.norm(X-m.inverse_transform(m.transform(X)))**2,np.sum(s[2:]**2),rtol=1e-10)

@pytest.mark.numerical
@pytest.mark.parametrize('scale',[1e-200,1e12])
def test_scale_stability(b5,scale):
    X=np.array([[1.,2.],[3.,-1.],[0.,4.]])*scale/4
    m=b5.load('singular-value-decomposition').SVD().fit(X)
    assert_allclose((m.left_singular_vectors_*(m.singular_values_/scale))@m.components_,X/scale,atol=1e-11)

@pytest.mark.parametrize('kwargs',[{'n_components':True},{'n_components':0},{'tol':0},{'max_sweeps':0}])
def test_invalid_parameters(b5,kwargs):
    with pytest.raises(ValueError):b5.load('singular-value-decomposition').SVD(**kwargs)

def test_nonconvergence_atomic_state_and_repeated_subspace(b5):
    cls=b5.load('singular-value-decomposition').SVD;m=cls().fit(np.eye(3));before=m.components_.copy()
    m.max_sweeps=1
    with pytest.raises(b5.ConvergenceError):m.fit(np.random.default_rng(17004).normal(size=(7,3)))
    assert_array_equal(m.components_,before)
    repeated=cls().fit(np.diag([2.,2.,0.]))
    assert_allclose(repeated.components_[:2].T@repeated.components_[:2],np.diag([1,1,0]),atol=1e-12)
