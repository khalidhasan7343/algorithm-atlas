import math

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest

pytestmark = pytest.mark.ml


def normalized_oracle(A, loops=True):
    n = len(A)
    augmented = [[float(A[i][j]) + int(loops and i==j) for j in range(n)] for i in range(n)]
    degrees = [sum(row) for row in augmented]
    return np.array([[augmented[i][j]/math.sqrt(degrees[i]*degrees[j]) if degrees[i]*degrees[j] else 0.
                      for j in range(n)] for i in range(n)])


@pytest.mark.oracle
@pytest.mark.parametrize('loops', [True,False])
def test_independent_normalization_degrees_weights_and_isolate(b9,loops):
    A=np.array([[0.,2,0,0],[2,0,1,0],[0,1,0,0],[0,0,0,0]])
    actual=b9.load('graph-convolutional-networks').normalize_adjacency(A,loops)
    assert_allclose(actual,normalized_oracle(A,loops),atol=1e-15)
    assert actual[3,3] == int(loops)
    assert_allclose(actual,actual.T,atol=1e-15)
    assert_array_equal(A,np.array([[0.,2,0,0],[2,0,1,0],[0,1,0,0],[0,0,0,0]]))


def forward_oracle(p,X,S):
    # Separate direct equations; never call production forward/activation helpers.
    hidden=np.array([[math.tanh(sum(float((S@X)[i,k])*float(p['W1'][k,j]) for k in range(X.shape[1]))+p['b1'][j])
                      for j in range(len(p['b1']))] for i in range(len(X))])
    return S@hidden@p['W2']+p['b2']


def loss_oracle(p,X,S,y,mask,l2):
    logits=forward_oracle(p,X,S)
    selected=[]
    for i in range(len(X)):
        if mask[i]:
            row=logits[i]-max(logits[i])
            selected.append(math.log(sum(math.exp(float(v)) for v in row))-float(row[y[i]]))
    return sum(selected)/len(selected)+l2/2*sum(float(v*v) for key in ('W1','W2') for v in p[key].ravel())


@pytest.mark.oracle
def test_hand_two_layer_forward_features_and_graph_dependence(b9):
    m=b9.load('graph-convolutional-networks')
    A=np.array([[0.,1,0],[1,0,0],[0,0,0]])
    S=normalized_oracle(A);X=np.array([[1.],[3.],[5.]])
    p=dict(W1=np.ones((1,1)),b1=np.zeros(1),W2=np.array([[1.,-1.]]),b2=np.zeros(2))
    out,_=m.forward(p,X,S)
    assert_allclose(out,[[math.tanh(2),-math.tanh(2)],[math.tanh(2),-math.tanh(2)],[math.tanh(5),-math.tanh(5)]])
    assert_allclose(out,forward_oracle(p,X,S),atol=1e-15)
    without,_=m.forward(p,X,np.eye(3))
    assert np.linalg.norm(out-without)>1e-3


@pytest.mark.numerical
@pytest.mark.oracle
@pytest.mark.parametrize('l2', [0.,.13])
def test_masked_cross_entropy_and_all_finite_difference_gradients(b9,l2):
    m=b9.load('graph-convolutional-networks');rng=np.random.default_rng(21010)
    A=np.array([[0.,1,0,0],[1,0,2,0],[0,2,0,0],[0,0,0,0]])
    S=normalized_oracle(A);X=rng.normal(0,.2,(4,2));p=m.initialize(2,3,2,21010)
    y=np.array([0,-1,1,-1]);mask=np.array([True,False,True,False])
    loss,g=m.loss_gradients(p,X,S,y,mask,l2)
    assert_allclose(loss,loss_oracle(p,X,S,y,mask,l2),atol=1e-14)
    for key,array in p.items():
        for index in np.ndindex(array.shape):
            old=array[index];array[index]=old+1e-6;plus=loss_oracle(p,X,S,y,mask,l2)
            array[index]=old-1e-6;minus=loss_oracle(p,X,S,y,mask,l2);array[index]=old
            assert_allclose(g[key][index],(plus-minus)/2e-6,atol=3e-9,rtol=2e-5)


def dataset():
    A=np.zeros((6,6))
    for i,j,w in [(0,1,1),(0,2,1),(1,2,1),(2,3,.1),(3,4,1),(3,5,1),(4,5,1)]:A[i,j]=A[j,i]=w
    X=np.array([[1.,0],[1,.2],[.8,.1],[0,1],[.1,.8],[.2,1]])
    return A,X,np.array([0,-1,-1,1,-1,-1])


def test_semi_supervised_training_predictions_and_fitted_shapes(b9):
    m=b9.load('graph-convolutional-networks');A,X,y=dataset()
    model=m.GCNClassifier(epochs=200,learning_rate=.2,random_state=21011).fit(A,X,y)
    assert model.loss_history_[-1]<model.loss_history_[0]*.25
    assert_array_equal(model.predict(A,X),[0,0,0,1,1,1])
    probabilities=model.predict_proba(A,X)
    assert probabilities.shape==(6,2) and np.isfinite(probabilities).all()
    assert_allclose(probabilities.sum(axis=1),1.,atol=1e-14)
    assert np.all(probabilities>=0)
    assert model.n_updates_==200 and model.loss_history_.shape==(201,)
    assert not model.converged_ and model.optimization_status_=='epoch-budget'
    assert model.predict_proba([[0]],[[.2,.3]]).shape==(1,2)


@pytest.mark.oracle
def test_unselected_labels_do_not_leak_into_training(b9):
    A,X,y=dataset();mask=y>=0
    model=b9.load('graph-convolutional-networks').GCNClassifier(epochs=10).fit(A,X,y,mask)
    alternate=np.array([0,1,0,1,1,0])
    other=b9.load('graph-convolutional-networks').GCNClassifier(epochs=10).fit(A,X,alternate,mask)
    for key in model.parameters_:assert_array_equal(model.parameters_[key],other.parameters_[key])
    assert_array_equal(model.loss_history_,other.loss_history_)


@pytest.mark.oracle
def test_seeded_random_node_permutation_equivariance(b9):
    rng=np.random.default_rng(21012);m=b9.load('graph-convolutional-networks')
    for n in range(3,9):
        upper=np.triu(rng.uniform(.1,3,(n,n))*(rng.random((n,n))<.4),1)
        A=upper+upper.T;X=rng.normal(0,.2,(n,3));p=m.initialize(3,4,2,21012)
        order=rng.permutation(n)
        out=m.forward(p,X,m.normalize_adjacency(A))[0]
        other=m.forward(p,X[order],m.normalize_adjacency(A[np.ix_(order,order)]))[0]
        assert_allclose(other,out[order],atol=1e-13,rtol=0)
    A,X,y=dataset();model=m.GCNClassifier(epochs=30).fit(A,X,y);order=np.array([4,1,5,0,3,2])
    assert_allclose(model.predict_proba(A[np.ix_(order,order)],X[order]),model.predict_proba(A,X)[order],atol=1e-13)
    retrained=m.GCNClassifier(epochs=30).fit(A[np.ix_(order,order)],X[order],y[order])
    assert_allclose(retrained.predict_proba(A[np.ix_(order,order)],X[order]),model.predict_proba(A,X)[order],atol=1e-12)


@pytest.mark.oracle
def test_b7_normalization_and_existing_message_pass_compatibility(b9):
    m=b9.load('graph-convolutional-networks');old=b9.b7_gnn();A,X,y=dataset()
    S=m.normalize_adjacency(A);assert_array_equal(S,old.normalize_adjacency(A,6,True))
    p=m.initialize(2,3,2,21013)
    # Existing low-level B7 matrix propagation is dimension-generic; B7's fitted
    # estimator remains its original scalar regressor and is not modified.
    assert_allclose(m.forward(p,X,S)[0],old.forward(p,X,S)[0],atol=1e-15)


@pytest.mark.numerical
def test_extreme_valid_logits_softmax_and_loss_are_finite(b9):
    m=b9.load('graph-convolutional-networks')
    p=dict(W1=np.array([[1e6,-1e6]]),b1=np.zeros(2),W2=np.array([[1e6,-1e6],[-1e6,1e6]]),b2=np.zeros(2))
    X=np.array([[1e6],[-1e6]]);S=np.eye(2)
    with np.errstate(over='raise',invalid='raise'):
        loss,g=m.loss_gradients(p,X,S,[1,0])
    assert np.isfinite(loss) and all(np.isfinite(v).all() for v in g.values())


def test_copying_seeded_fit_atomic_refit_and_fitted_loop_convention(b9):
    A,X,y=dataset();copies=[a.copy() for a in (A,X,y)];m=b9.load('graph-convolutional-networks')
    model=m.GCNClassifier(epochs=5,random_state=7).fit(A,X,y)
    other=m.GCNClassifier(epochs=5,random_state=7).fit(A,X,y)
    for key in model.parameters_:assert_array_equal(model.parameters_[key],other.parameters_[key])
    old=model.predict_proba(A,X)
    for a,b in zip((A,X,y),copies):assert_array_equal(a,b)
    with pytest.raises(ValueError):model.fit(A,X,[-1]*6)
    assert_array_equal(model.predict_proba(A,X),old)
    model.self_loops=False
    assert_array_equal(model.predict_proba(A,X),old)
    with pytest.raises(ValueError):m.GCNClassifier().predict(A,X)
    with pytest.raises(ValueError):model.predict(A,np.ones((6,3)))


@pytest.mark.parametrize('settings', [dict(hidden_dim=0),dict(epochs=2001),dict(epochs=True),dict(learning_rate=0),
    dict(random_state=-1),dict(self_loops=1),dict(l2=-1),dict(l2=np.nan),dict(gradient_clip=np.inf)])
def test_invalid_settings(b9,settings):
    with pytest.raises(ValueError):b9.load('graph-convolutional-networks').GCNClassifier(**settings)


@pytest.mark.parametrize('A', [[],[[0,1],[0,0]],[[1,0],[0,0]],[[0,-1],[-1,0]],[[np.nan]],[[True]],np.zeros((33,33))])
def test_invalid_graphs(b9,A):
    with pytest.raises(ValueError):b9.load('graph-convolutional-networks').normalize_adjacency(A)


@pytest.mark.parametrize('labels,mask', [([0,0],None),([1,2],None),([0.,1.],None),([True,False],None),([-1,-1],None),
    ([0,1],[False,False]),([0,-1],[True,True]),([0,1],[1,0]),([0,1],[[True],[True]]),([0,1,0],None)])
def test_invalid_training_labels_and_masks(b9,labels,mask):
    with pytest.raises(ValueError):b9.load('graph-convolutional-networks').GCNClassifier().fit([[0,1],[1,0]],[[1.],[2.]],labels,mask)


@pytest.mark.parametrize('X', [[[1.]],[[1.,2.],[1.]],[[np.inf],[1]],[[True],[False]],np.zeros((2,17)),[[1e7],[0]]])
def test_invalid_features(b9,X):
    with pytest.raises(ValueError):b9.load('graph-convolutional-networks').GCNClassifier().fit([[0,1],[1,0]],X,[0,1])
