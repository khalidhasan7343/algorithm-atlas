import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.oracle
@pytest.mark.numerical
@pytest.mark.parametrize('activation',['tanh','linear'])
def test_forward_manual_backprop_and_finite_differences(b5,activation):
    module=b5.load('vanilla-autoencoders');X=np.array([[.2,-.3],[.4,.1],[-.5,.2]])
    theta=np.array([.2,-.4,.1,.3,-.2,.05,-.1]) # W1(2,1), b1, W2(1,2), b2
    W1=theta[:2,None];b1=theta[2:3];W2=theta[3:5][None,:];b2=theta[5:]
    hidden=X@W1+b1;Z=np.tanh(hidden) if activation=='tanh' else hidden
    R=Z@W2+b2;delta=2*(R-X)/X.size
    hidden_delta=delta@W2.T
    if activation=='tanh':hidden_delta*=1-Z**2
    expected=np.r_[(X.T@hidden_delta).ravel(),hidden_delta.sum(0),(Z.T@delta).ravel(),delta.sum(0)]
    loss,grad=module.loss_gradient(theta,X,2,1,activation)
    assert_allclose(loss,np.sum((R-X)**2)/6);assert_allclose(grad,expected,atol=1e-14)
    numeric=[]
    for j in range(len(theta)):
        plus=theta.copy();minus=theta.copy();plus[j]+=1e-6;minus[j]-=1e-6
        numeric.append((module.loss_gradient(plus,X,2,1,activation)[0]-module.loss_gradient(minus,X,2,1,activation)[0])/2e-6)
    assert_allclose(grad,numeric,atol=1e-10,rtol=1e-6)
    actualZ,actualR=module.forward(theta,X,2,1,activation)
    assert_allclose(actualZ,Z);assert_allclose(actualR,R)

@pytest.mark.reference
def test_scipy_independent_gradient_oracle(b5):
    from scipy.optimize import check_grad
    module=b5.load('vanilla-autoencoders');X=np.random.default_rng(17031).normal(size=(4,3))
    theta=module.initialize_parameters(3,2,17031)
    # Independent loss expression, not the implementation's loss helper.
    def loss(t):
        Z=np.tanh(X@t[:6].reshape(3,2)+t[6:8]);R=Z@t[8:14].reshape(2,3)+t[14:]
        return np.mean((R-X)**2)
    assert check_grad(loss,lambda t:module.loss_gradient(t,X,3,2)[1],theta)<2e-6

@pytest.mark.oracle
@pytest.mark.numerical
def test_single_parameter_update_exact_and_budget_status(b5):
    module=b5.load('vanilla-autoencoders');X=np.array([[-1.,-.5],[0,0],[1,.5]])
    initial=module.initialize_parameters(2,1,0);_,gradient=module.loss_gradient(initial,X,2,1)
    m=module.Autoencoder(max_iter=1,learning_rate=.01,tol=1e-12).fit(X)
    assert_allclose(m.parameters_,initial-.01*gradient,atol=1e-14)
    assert m.n_iter_==1 and not m.converged_ and m.optimization_status_=='budget-exhausted'

@pytest.mark.numerical
@pytest.mark.parametrize('activation',['tanh','linear'])
def test_controlled_training_loss_shapes_and_reconstruction(b5,activation):
    module=b5.load('vanilla-autoencoders');v=np.linspace(-1,1,30);X=np.column_stack([v,.5*v])
    m=module.Autoencoder(activation=activation,max_iter=700).fit(X)
    assert m.transform(X).shape==(30,1) and m.reconstruct(X).shape==X.shape
    assert m.reconstruction_loss_<m.objective_history_[0]*.03
    assert np.all(np.diff(m.objective_history_)<=1e-12)
    assert np.mean((m.reconstruct(X)-X)**2)<.003
    assert_array_equal(m.parameters_,module.Autoencoder(activation=activation,max_iter=700).fit(X).parameters_)
    assert_array_equal(m.reconstruct(X),m.inverse_transform(m.transform(X)))

@pytest.mark.numerical
@pytest.mark.parametrize('scale',[.1,1e-200,1e12])
def test_constant_features_duplicate_training_and_scale(b5,scale):
    cls=b5.load('vanilla-autoencoders').Autoencoder;X=np.ones((5,3))*scale
    m=cls().fit(X);assert_allclose(m.reconstruct(X),X,atol=0,rtol=1e-14)
    assert m.converged_ and m.reconstruction_loss_==0
    Z=np.array([[0.,0.],[1.,.5],[1.,.5],[-1.,-.5]])*scale
    other=cls(max_iter=20).fit(Z);assert np.isfinite(other.transform(Z)).all()

@pytest.mark.parametrize('kwargs',[{'latent_dim':0},{'latent_dim':True},{'activation':'relu'},{'activation':[]},{'max_iter':0},{'learning_rate':0},{'random_state':-1}])
def test_invalid_parameters(b5,kwargs):
    with pytest.raises(ValueError):b5.load('vanilla-autoencoders').Autoencoder(**kwargs)

def test_strict_bottleneck_and_atomic_refit(b5):
    cls=b5.load('vanilla-autoencoders').Autoencoder
    with pytest.raises(ValueError):cls(2).fit(np.eye(3,2))
    m=cls(max_iter=5).fit(np.eye(3,2));before=m.parameters_.copy();m.activation='unsupported'
    with pytest.raises(ValueError):m.fit(np.eye(3,2))
    assert_array_equal(m.parameters_,before)
    # Changing training settings cannot alter stored inference activation.
    assert_allclose(m.transform(np.eye(3,2)),np.tanh(((np.eye(3,2)-m.mean_)/m.scale_)@m.encoder_weights_+m.encoder_bias_))
