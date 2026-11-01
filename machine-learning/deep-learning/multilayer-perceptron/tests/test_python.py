import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.oracle
def test_forward_bce_and_backprop_manual(b7):
    m=b7.load('multilayer-perceptron');p=dict(W1=np.array([[.2,-.1],[.3,.4]]),b1=np.array([.1,-.2]),W2=np.array([[.5],[-.6]]),b2=np.array([.05]))
    X=np.array([[1.,2.],[-1.,.5]]);y=np.array([[1.],[0.]])
    Z=np.tanh(X@p['W1']+p['b1']);L=Z@p['W2']+p['b2'];q=1/(1+np.exp(-L));d=(q-y)/2;H=d@p['W2'].T*(1-Z**2)
    loss,g=m.loss_gradients(p,X,y)
    assert_allclose(m.forward(p,X)[0],L);assert_allclose(loss,-np.mean(y*np.log(q)+(1-y)*np.log(1-q)))
    assert_allclose(g['W1'],X.T@H);assert_allclose(g['b1'],H.sum(0));assert_allclose(g['W2'],Z.T@d);assert_allclose(g['b2'],d.sum(0))

@pytest.mark.numerical
@pytest.mark.oracle
def test_finite_difference_all_weights_biases(b7,gradients):
    m=b7.load('multilayer-perceptron');p=m.initialize(2,3,np.random.default_rng(19001));X=np.array([[.2,-.3],[.4,.1]]);y=np.array([[1.],[0.]])
    loss,g=m.loss_gradients(p,X,y);gradients(lambda q:m.loss_gradients(q,X,y)[0],p,g)

@pytest.mark.reference
def test_scipy_sigmoid_reference_and_extreme_logits(b7):
    from scipy.special import expit
    x=np.array([-1e6,-10.,0,10.,1e6]);assert_allclose(b7.sigmoid(x),expit(x),atol=1e-16)
    loss,g=b7.bce(x[:,None],np.array([[1.],[1.],[0.],[0.],[0.]]));assert np.isfinite(loss) and np.isfinite(g).all()

@pytest.mark.numerical
def test_reproducibility_xor_training_and_atomic_refit(b7):
    cls=b7.load('multilayer-perceptron').MLPClassifier;X=np.array([[-1.,-1.],[-1,1],[1,-1],[1,1]]);y=np.array([0,1,1,0])
    m=cls(hidden_dim=8,epochs=600,learning_rate=.5,batch_size=4,random_state=19002).fit(X,y)
    assert_array_equal(m.predict(X),y);assert m.loss_history_[-1]<.1
    other=cls(hidden_dim=8,epochs=600,learning_rate=.5,batch_size=4,random_state=19002).fit(X,y)
    for key in m.parameters_:assert_array_equal(m.parameters_[key],other.parameters_[key])
    old=m.predict_proba(X);m.learning_rate=0
    with pytest.raises(ValueError):m.fit(X,y)
    assert_allclose(m.predict_proba(X),old)

def test_separable_and_before_fit_shapes(b7):
    cls=b7.load('multilayer-perceptron').MLPClassifier
    with pytest.raises(ValueError):cls().predict([[0,1]])
    X=np.array([[-2.],[-1.],[1.],[2.]]);m=cls(epochs=150).fit(X,[0,0,1,1]);assert_array_equal(m.predict(X),[0,0,1,1])
    assert m.predict_proba(np.empty((0,1))).shape==(0,2)
    with pytest.raises(ValueError):m.predict([[1,2]])

@pytest.mark.parametrize('kwargs',[{'hidden_dim':0},{'epochs':0},{'learning_rate':float('nan')},{'batch_size':True},{'random_state':-1},{'gradient_clip':0}])
def test_invalid_architecture_training_parameters(b7,kwargs):
    with pytest.raises(ValueError):b7.load('multilayer-perceptron').MLPClassifier(**kwargs)

@pytest.mark.parametrize('y',[[0,2],[True,False],[[0],[1]],[0],[0.,1.]])
def test_invalid_binary_targets(b7,y):
    with pytest.raises(ValueError):b7.load('multilayer-perceptron').MLPClassifier().fit([[0],[1]],y)
