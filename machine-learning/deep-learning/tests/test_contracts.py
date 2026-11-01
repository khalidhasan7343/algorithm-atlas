"""Shared B7 shape/state/resource contracts; approved vanilla AE has its own unchanged suite."""
import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml

CLASSES={'multilayer-perceptron':'MLPClassifier','convolutional-neural-networks':'CNNRegressor','residual-networks':'ResidualRegressor','recurrent-neural-networks':'RNNRegressor','long-short-term-memory':'LSTMRegressor','gated-recurrent-units':'GRURegressor','transformers':'TransformerRegressor','denoising-autoencoders':'DenoisingAutoencoder','sparse-autoencoders':'SparseAutoencoder','variational-autoencoders':'VariationalAutoencoder','generative-adversarial-networks':'GAN','diffusion-models':'DiffusionModel','graph-neural-networks':'GCNRegressor'}
SEQUENCES={'recurrent-neural-networks','long-short-term-memory','gated-recurrent-units','transformers'}
GENERATIVE={'denoising-autoencoders','sparse-autoencoders','variational-autoencoders','generative-adversarial-networks','diffusion-models'}


def setup(b7,name):
    kwargs=dict(epochs=3,learning_rate=.05)
    if name not in {'convolutional-neural-networks','denoising-autoencoders','sparse-autoencoders','variational-autoencoders'}:kwargs['hidden_dim']=2
    if name!='graph-neural-networks':kwargs['batch_size']=4
    if name=='convolutional-neural-networks':X=np.linspace(-.4,.4,16).reshape(4,1,2,2)
    elif name in SEQUENCES:X=np.linspace(-.4,.4,24).reshape(4,3,2)
    else:X=np.array([[-.4,-.2],[-.1,0],[.2,.1],[.4,.2]])
    y=np.array([0,0,1,1]) if name=='multilayer-perceptron' else np.array([[-.3],[-.1],[.1],[.3]])
    A=np.array([[0.,1,0,0],[1,0,1,0],[0,1,0,0],[0,0,0,0]])
    return getattr(b7.load(name),CLASSES[name])(**kwargs),X,y,A


def fit(model,name,X,y,A):
    if name=='graph-neural-networks':return model.fit(X,y,A)
    if name in GENERATIVE:return model.fit(X)
    return model.fit(X,y)


def inference(model,name,X,A):
    if name=='graph-neural-networks':return model.predict(X,A)
    if name in {'generative-adversarial-networks','diffusion-models'}:return model.sample(3,7)
    if name in GENERATIVE:return model.reconstruct(X)
    return model.predict(X)


@pytest.mark.parametrize('name',CLASSES)
@pytest.mark.parametrize('defect',['nan','inf','bool','empty','wrong-rank','oversized'])
def test_invalid_array_domains_and_shapes(b7,name,defect):
    m,X,y,A=setup(b7,name)
    if defect=='nan':X[:]=np.nan
    elif defect=='inf':X[:]=np.inf
    elif defect=='bool':X=np.ones(X.shape,dtype=bool)
    elif defect=='empty':X=X[:0]
    elif defect=='wrong-rank':X=X.ravel()
    else:X[:]=1e7
    with pytest.raises(ValueError):fit(m,name,X,y,A)


@pytest.mark.parametrize('name',CLASSES)
def test_reproducibility_copy_rng_and_atomic_refit(b7,name):
    m,X,y,A=setup(b7,name);before=X.copy();labels=y.copy();graph=A.copy();state=np.random.get_state()
    fit(m,name,X,y,A);expected=inference(m,name,X,A)
    assert_array_equal(X,before);assert_array_equal(y,labels);assert_array_equal(A,graph)
    new=np.random.get_state();assert state[0]==new[0] and state[2:]==new[2:];assert_array_equal(state[1],new[1])
    other,_,_,_=setup(b7,name);fit(other,name,X,y,A);assert_array_equal(inference(other,name,X,A),expected)
    m.learning_rate=0
    with pytest.raises(ValueError):fit(m,name,X,y,A)
    assert_array_equal(inference(m,name,X,A),expected)
    assert m.optimization_status_=='fixed-budget-completed' and not m.converged_


@pytest.mark.numerical
@pytest.mark.parametrize('name',CLASSES)
def test_constant_duplicate_inputs_and_nonfinite_state_detection(b7,name):
    m,X,y,A=setup(b7,name);X[:]=.1;fit(m,name,X,y,A)
    assert np.isfinite(inference(m,name,X,A)).all()
    key=next(iter(m.parameters_));m.parameters_[key][:]=np.nan
    with pytest.raises(ValueError):inference(m,name,X,A)


@pytest.mark.parametrize('name',CLASSES)
def test_invalid_epoch_batch_seed_clip_parameters(b7,name):
    m,X,y,A=setup(b7,name)
    for attr,value in [('epochs',0),('random_state',True),('gradient_clip',0)]:
        m,_,_,_=setup(b7,name);setattr(m,attr,value)
        with pytest.raises(ValueError):fit(m,name,X,y,A)
    if name!='graph-neural-networks':
        m,_,_,_=setup(b7,name);m.batch_size=0
        with pytest.raises(ValueError):fit(m,name,X,y,A)


@pytest.mark.numerical
def test_vae_latent_units_and_invalid_latent_shapes(b7):
    m=b7.load('variational-autoencoders').VariationalAutoencoder(epochs=2).fit([[0,0],[1,2],[2,1]])
    assert np.isfinite(m.inverse_transform([[1e10]])).all()
    for bad in [[[float('nan')]],[[1,2]],[True]]:
        with pytest.raises(ValueError):m.inverse_transform(bad)

@pytest.mark.parametrize('name',[name for name in CLASSES if name not in GENERATIVE])
def test_supervised_target_shapes_never_broadcast(b7,name):
    m,X,y,A=setup(b7,name)
    invalid=[None,[[0]],np.zeros((len(X),2))]
    invalid.append(np.zeros((len(X),1)) if name=='multilayer-perceptron' else np.zeros(len(X)))
    for target in invalid:
        with pytest.raises(ValueError):fit(m,name,X,target,A)
