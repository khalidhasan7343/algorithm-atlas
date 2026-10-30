"""Cross-canonical array, state, resource and numerical contracts."""
import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml

TOPICS=['singular-value-decomposition','principal-component-analysis','linear-discriminant-analysis-projection','independent-component-analysis','t-sne','umap','vanilla-autoencoders']


def model(b5,name):
    classes=['SVD','PCA','LDAProjection','FastICA','TSNE','UMAP','Autoencoder']
    kwargs=dict(n_components=1)
    if name=='linear-discriminant-analysis-projection':kwargs['reg']=.1
    if name=='t-sne':kwargs.update(perplexity=2,max_iter=5)
    if name=='umap':kwargs.update(n_neighbors=2,max_iter=5)
    if name=='vanilla-autoencoders':kwargs=dict(latent_dim=1,max_iter=5)
    return getattr(b5.load(name),classes[TOPICS.index(name)])(**kwargs)


@pytest.mark.parametrize('name',TOPICS)
@pytest.mark.parametrize('X',[[],[1,2],[[float('nan'),0],[1,2]],[[0,float('inf')],[1,2]],[[True,False],[False,True]],[['1','2'],['3','4']],[[1+1j,0],[0,1]],[[1e13,0],[0,1]]])
def test_reject_unsupported_arrays(b5,name,X):
    with pytest.raises(ValueError):model(b5,name).fit(X,[0,1])


@pytest.mark.parametrize('name',TOPICS)
def test_input_copy_local_rng_atomic_state_and_changed_parameters(b5,name):
    rng=np.random.default_rng(17040);X=rng.normal(size=(12,3));original=X.copy();y=np.repeat([0,1],6)
    global_state=np.random.get_state();m=model(b5,name).fit(X,y)
    assert_array_equal(X,original);new_state=np.random.get_state()
    assert global_state[0]==new_state[0] and global_state[2:]==new_state[2:];assert_array_equal(global_state[1],new_state[1])
    if hasattr(m,'transform'):
        expected=m.transform(X);X[:]=123
        assert_allclose(m.transform(original),expected)
        assert m.transform(np.empty((0,3))).shape==(0,1)
        with pytest.raises(ValueError):m.transform([[1,2]])
        with pytest.raises(ValueError):model(b5,name).transform(original)
    else:expected=m.embedding_.copy()
    attribute='latent_dim' if name=='vanilla-autoencoders' else 'n_components'
    setattr(m,attribute,True)
    with pytest.raises(ValueError):m.fit(original,y)
    if hasattr(m,'transform'):assert_allclose(m.transform(original),expected)
    else:assert_array_equal(m.embedding_,expected)


@pytest.mark.numerical
@pytest.mark.parametrize('shape,rank', [((19,5),1),((19,5),3),((5,13),2),((8,8),4)])
def test_jacobi_random_low_rank_reconstruction_subspaces(b5,shape,rank):
    rng=np.random.default_rng(17041);X=rng.normal(size=(shape[0],rank))@rng.normal(size=(rank,shape[1]))
    m=b5.load('singular-value-decomposition').SVD().fit(X)
    assert_allclose((m.left_singular_vectors_*m.singular_values_)@m.components_,X,atol=3e-10)
    assert_allclose(m.left_singular_vectors_.T@m.left_singular_vectors_,np.eye(min(shape)),atol=3e-10)
    assert_allclose(m.components_@m.components_.T,np.eye(min(shape)),atol=3e-10)
    assert np.count_nonzero(m.singular_values_)==rank


@pytest.mark.numerical
@pytest.mark.parametrize('name',['singular-value-decomposition','principal-component-analysis'])
def test_large_valid_projection_round_trip_and_latent_validation(b5,name):
    X=np.array([[-1.,-1.],[1.,1.]])*1e12
    m=model(b5,name).fit(X);Z=m.transform(X)
    assert abs(Z).max()>1e12
    assert_allclose(m.inverse_transform(Z),X,rtol=1e-12)
    for bad in [[[float('inf')]],[[True]],[[1,2]]]:
        with pytest.raises(ValueError):m.inverse_transform(bad)


@pytest.mark.numerical
def test_uniform_scale_laws_and_lda_constant_regularized(b5):
    X=np.random.default_rng(17042).normal(size=(15,3));y=np.repeat([0,1,2],5)
    for name in ['singular-value-decomposition','principal-component-analysis','linear-discriminant-analysis-projection','independent-component-analysis']:
        left=model(b5,name).fit(X,y);right=model(b5,name).fit(X*1e-100,y)
        A=left.components_.T;B=right.components_.T
        Q=np.linalg.qr(A)[0];R=np.linalg.qr(B)[0]
        assert_allclose(Q@Q.T,R@R.T,atol=1e-10)
    m=b5.load('linear-discriminant-analysis-projection').LDAProjection(reg=.1).fit(np.ones((4,2)),[0,0,1,1])
    assert_allclose(m.transform(np.ones((4,2))),0)


@pytest.mark.parametrize('name',TOPICS)
def test_resource_limits(b5,name):
    m=model(b5,name)
    with pytest.raises(ValueError):m.fit(np.zeros((513,2)))
    with pytest.raises(ValueError):m.fit(np.zeros((5,33)))
    if name in ('t-sne','umap'):
        with pytest.raises(ValueError):m.fit(np.zeros((129,2)))
