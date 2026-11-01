import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.oracle
def test_forward_hand_convolution_shapes_and_bias(b7):
    m=b7.load('convolutional-neural-networks');X=np.arange(1,10,dtype=float).reshape(1,1,3,3);K=np.array([[[[1.,0.],[0.,-1.]]]])
    out,cache=m.convolution(X,K,np.array([2.]));assert_allclose(out,[[[[-2,-2],[-2,-2]]]])
    dx,dK,db=m.convolution_backward(np.ones_like(out),cache)
    assert_allclose(dK,[[[[12,16],[24,28]]]]);assert_allclose(db,[4]);assert dx.shape==X.shape

@pytest.mark.reference
@pytest.mark.parametrize('stride,padding',[(1,0),(2,1)])
def test_scipy_multichannel_stride_padding_reference(b7,stride,padding):
    from scipy.signal import correlate2d
    m=b7.load('convolutional-neural-networks');rng=np.random.default_rng(19011);X=rng.normal(size=(2,2,3,3));K=rng.normal(size=(2,2,2,2));b=np.array([.1,-.2])
    actual,_=m.convolution(X,K,b,stride,padding);expected=np.empty_like(actual)
    for n in range(2):
        for f in range(2):
            expected[n,f]=sum(correlate2d(np.pad(X[n,c],padding),K[f,c],mode='valid')[::stride,::stride] for c in range(2))+b[f]
    assert_allclose(actual,expected,atol=1e-12)

@pytest.mark.numerical
@pytest.mark.parametrize('stride,padding',[(1,0),(2,1)])
def test_finite_difference_network_all_parameters(b7,gradients,stride,padding):
    m=b7.load('convolutional-neural-networks');rng=np.random.default_rng(19012);X=rng.normal(size=(2,2,3,3))*.2;y=np.array([[.1],[-.2]])
    p=m.initialize((2,3,3),2,2,stride,padding,rng);loss,g=m.loss_gradients(p,X,y,stride,padding)
    gradients(lambda q:m.loss_gradients(q,X,y,stride,padding)[0],p,g)

@pytest.mark.numerical
def test_convolution_input_backprop_finite_difference(b7,gradients):
    m=b7.load('convolutional-neural-networks');rng=np.random.default_rng(19013);X=rng.normal(size=(1,1,3,3));K=rng.normal(size=(1,1,2,2));b=np.zeros(1)
    output,cache=m.convolution(X,K,b,2,1);up=rng.normal(size=output.shape);dx,_,_=m.convolution_backward(up,cache)
    gradients(lambda q:np.sum(m.convolution(q['X'],K,b,2,1)[0]*up),{'X':X},{'X':dx})

def test_reproducibility_tiny_image_regression_and_shape_errors(b7):
    cls=b7.load('convolutional-neural-networks').CNNRegressor;X=np.linspace(-1,1,32).reshape(8,1,2,2);y=X.mean(axis=(1,2,3))[:,None]
    m=cls(filters=1,epochs=100,learning_rate=.1,batch_size=8).fit(X,y);assert m.loss_history_[-1]<m.loss_history_[0]*.2
    assert_array_equal(m.predict(X),cls(filters=1,epochs=100,learning_rate=.1,batch_size=8).fit(X,y).predict(X))
    with pytest.raises(ValueError):m.predict(np.zeros((2,1,3,3)))
    with pytest.raises(ValueError):cls(kernel_size=3).fit(np.ones((2,1,1,1)),[[0],[1]])
    with pytest.raises(ValueError):cls().predict(X)

@pytest.mark.parametrize('kwargs',[{'filters':0},{'kernel_size':4},{'stride':0},{'padding':2}])
def test_invalid_convolution_architecture(b7,kwargs):
    with pytest.raises(ValueError):b7.load('convolutional-neural-networks').CNNRegressor(**kwargs)
