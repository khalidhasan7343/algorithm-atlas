import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.oracle
@pytest.mark.numerical
def test_analytical_scatter_and_direction(b5):
    X=np.array([[-2.,-1.],[-2.,1.],[2.,-1.],[2.,1.]])
    m=b5.load('linear-discriminant-analysis-projection').LDAProjection(1,reg=.1).fit(X,[0,0,1,1])
    assert_allclose(m.mean_,[0,0]);assert_allclose(m.within_scatter_,[[0,0],[0,4]])
    assert_allclose(m.between_scatter_,[[16,0],[0,0]])
    assert_allclose(m.components_,[[1,0]]);assert_allclose(m.transform(X).ravel(),[-2,-2,2,2])
    for value,row in zip(m.eigenvalues_,m.components_):
        assert_allclose(m.normalized_between_scatter_@row,value*m.regularized_within_scatter_@row,atol=1e-12)

@pytest.mark.reference
@pytest.mark.parametrize('seed',[17011,17012,17013])
def test_multiclass_scipy_and_sklearn_subspaces(b5,seed):
    from scipy.linalg import eigh
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    rng=np.random.default_rng(seed);X=rng.normal(size=(60,4))+np.repeat([[0,0,0,0],[3,1,0,0],[0,3,1,0]],20,axis=0);y=np.repeat(['a','b','c'],20)
    m=b5.load('linear-discriminant-analysis-projection').LDAProjection(2).fit(X,y)
    Sw=np.zeros((4,4));Sb=np.zeros((4,4));mean=X.mean(0)
    for c in np.unique(y):
        g=X[y==c];d=g-g.mean(0);Sw+=d.T@d;v=g.mean(0)-mean;Sb+=len(g)*np.outer(v,v)
    assert_allclose(m.within_scatter_,Sw,atol=1e-12);assert_allclose(m.between_scatter_,Sb,atol=1e-12)
    w,V=eigh(Sb,Sw);Q=np.linalg.qr(V[:,-2:])[0];ours=np.linalg.qr(m.components_.T)[0]
    assert_allclose(ours@ours.T,Q@Q.T,atol=1e-10)
    ref=LinearDiscriminantAnalysis(solver='eigen',n_components=2).fit(X,y)
    R=np.linalg.qr(ref.scalings_[:,:2])[0];assert_allclose(ours@ours.T,R@R.T,atol=1e-10)
    assert m.transform(X).shape==(60,2)

@pytest.mark.parametrize('y',[[0,0,0,0],[0,1],[0,True,1,1],[[0],[0],[1],[1]],[0.,0.,1.,1.]])
def test_invalid_labels(b5,y):
    with pytest.raises(ValueError):b5.load('linear-discriminant-analysis-projection').LDAProjection(reg=.1).fit(np.eye(4,2),y)

@pytest.mark.numerical
def test_singular_regularization_and_dimension_bounds(b5):
    cls=b5.load('linear-discriminant-analysis-projection').LDAProjection;X=[[0,0],[0,0],[1,1],[1,1]];y=[0,0,1,1]
    with pytest.raises(ValueError):cls().fit(X,y)
    m=cls(reg=.1).fit(X,y);assert np.isfinite(m.transform(X)).all()
    with pytest.raises(ValueError):cls(2,reg=.1).fit(X,y)
    with pytest.raises(ValueError):cls(reg=-1)
