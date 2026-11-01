import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.oracle
@pytest.mark.numerical
def test_known_covariance_projection_reconstruction(b5):
    X=np.array([[-2.,0.],[0.,1.],[2.,0.],[0.,-1.]])+[10,20]
    m=b5.load('principal-component-analysis').PCA(1).fit(X)
    assert_allclose(m.mean_,[10,20]);assert_allclose(m.explained_variance_,[8/3])
    assert_allclose(m.explained_variance_ratio_,[.8]);assert_allclose(abs(m.components_[0]),[1,0])
    assert_allclose(m.transform(X).ravel(),[-2,0,2,0])
    assert_allclose(np.linalg.norm(X-m.inverse_transform(m.transform(X)))**2,2)

@pytest.mark.reference
@pytest.mark.parametrize('seed',[17005,17006,17007])
def test_sklearn_and_numpy_subspaces(b5,seed):
    from sklearn.decomposition import PCA
    X=np.random.default_rng(seed).normal(size=(30,4))*[3,2,1,.1]
    m=b5.load('principal-component-analysis').PCA(2).fit(X);ref=PCA(2,svd_solver='full').fit(X)
    assert_allclose(m.components_.T@m.components_,ref.components_.T@ref.components_,atol=1e-10)
    assert_allclose(m.explained_variance_,ref.explained_variance_,rtol=1e-10)
    assert_allclose(m.explained_variance_ratio_,ref.explained_variance_ratio_,atol=1e-12)
    _,s,V=np.linalg.svd(X-X.mean(0),full_matrices=False)
    assert_allclose(m.singular_values_,s[:2],rtol=1e-10)
    assert_allclose(m.components_@m.components_.T,np.eye(2),atol=1e-11)

@pytest.mark.numerical
@pytest.mark.parametrize('X',[np.ones((4,3))*.1,[[1.,2.,0.],[2.,4.,0.],[3.,6.,0.]],np.array([[0.,0.],[1.,2.],[2.,1.]])*1e-200])
def test_constant_rank_deficient_and_tiny(b5,X):
    X=np.asarray(X);m=b5.load('principal-component-analysis').PCA(min(X.shape)).fit(X)
    assert np.isfinite(m.explained_variance_ratio_).all()
    assert_allclose(m.inverse_transform(m.transform(X)),X,atol=max(np.max(abs(X))*1e-11,1e-210))
    if np.all(X==X[0]):assert_allclose(m.explained_variance_ratio_,0)
    else:assert_allclose(m.explained_variance_ratio_.sum(),1)

def test_pca_dimension_validation(b5):
    cls=b5.load('principal-component-analysis').PCA
    with pytest.raises(ValueError):cls(2).fit([[1.,2.]])
    with pytest.raises(ValueError):cls(3).fit([[1.,2.],[2.,3.]])
    with pytest.raises(ValueError):cls(True)


@pytest.mark.oracle
@pytest.mark.numerical
def test_valid_raw_boundary_centering_does_not_reapply_input_cap(b5):
    X=np.array([[-1e12],[1e12],[1e12]])
    m=b5.load('principal-component-analysis').PCA(1).fit(X)
    assert_allclose(m.mean_,[1e12/3],rtol=1e-14)
    assert_allclose(m.explained_variance_,[4e24/3],rtol=1e-13)
    assert_allclose(m.singular_values_,[np.sqrt(8e24/3)],rtol=1e-13)
    assert_allclose(m.explained_variance_ratio_,[1.])
    assert_allclose(m.inverse_transform(m.transform(X)),X,atol=1e-3,rtol=1e-14)


@pytest.mark.oracle
@pytest.mark.reference
@pytest.mark.parametrize('shift',[[0.,0.],[.05e12,-.1e12]])
def test_centered_internal_scaling_translated_multidimensional_numpy_oracle(b5,shift):
    X=np.array([[-.9,-.7],[.7,.4],[.8,.6],[.9,.8]])*1e12+shift
    assert np.max(abs(X))<=1e12
    assert np.max(abs(X-X.mean(0)))>1e12
    m=b5.load('principal-component-analysis').PCA(2).fit(X)
    centered=X-X.mean(0);_,singular,V=np.linalg.svd(centered,full_matrices=False)
    assert_allclose(m.mean_,X.mean(0),rtol=1e-14,atol=1e-3)
    assert_allclose(m.singular_values_,singular,rtol=1e-12,atol=1e-3)
    assert_allclose(m.explained_variance_,singular**2/(len(X)-1),rtol=1e-12)
    assert_allclose(m.components_.T@m.components_,V.T@V,atol=1e-12)
    assert_allclose(m.inverse_transform(m.transform(X)),X,rtol=1e-13,atol=1e-3)
