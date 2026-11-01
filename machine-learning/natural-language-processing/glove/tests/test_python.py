import math
import numpy as np
from numpy.testing import assert_allclose
import pytest

pytestmark = pytest.mark.ml


def fixture_parameters():
    return {'W':np.array([[.2,-.1],[.3,.4]]),'C':np.array([[.1,.6],[-.4,.2]]),
            'b':np.array([.03,-.02]),'c':np.array([.04,-.05])}


def scalar_objective(p,X,x_max,alpha):
    loss=0.
    for i in range(len(X)):
        for j in range(len(X)):
            if X[i,j]>0:
                weight=min((float(X[i,j])/x_max)**alpha,1.)
                residual=sum(a*b for a,b in zip(p['W'][i],p['C'][j]))+p['b'][i]+p['c'][j]-math.log(float(X[i,j]))
                loss+=weight*residual*residual
    return loss


@pytest.mark.oracle
@pytest.mark.parametrize('symmetric,expected',[(True,[[0,1,.5],[1,0,1],[.5,1,0]]),
                                              (False,[[0,0,0],[1,0,0],[.5,1,0]])])
def test_hand_inverse_distance_cooccurrence_and_boundaries(b13,symmetric,expected):
    m=b13.load('glove')
    assert_allclose(m.cooccurrence_matrix([[0,1,2],[],[1]],3,window=2,symmetric=symmetric),expected,atol=0)
    assert_allclose(m.cooccurrence_matrix([[0],[1]],3),0,atol=0)
    assert_allclose(m.cooccurrence_matrix([[0,0]],1),[[2.]],atol=0)


@pytest.mark.oracle
def test_weighting_function_exact_values(b13):
    assert_allclose(b13.load('glove').weighting([0,1,4,16],x_max=4,alpha=.5),[0,.5,1,1],atol=0)


@pytest.mark.oracle
@pytest.mark.numerical
def test_independent_objective_and_all_four_gradient_groups(b13):
    m=b13.load('glove');p=fixture_parameters();X=np.array([[1.,2.],[.5,0.]])
    loss,gradient=m.glove_loss_gradients(p,X,x_max=2,alpha=.75)
    assert_allclose(loss,scalar_objective(p,X,2,.75),atol=1e-15)
    for name in ('W','C','b','c'):
        for index in np.ndindex(p[name].shape):
            plus={k:v.copy() for k,v in p.items()};minus={k:v.copy() for k,v in p.items()}
            plus[name][index]+=1e-6;minus[name][index]-=1e-6
            finite_difference=(scalar_objective(plus,X,2,.75)-scalar_objective(minus,X,2,.75))/2e-6
            assert_allclose(gradient[name][index],finite_difference,rtol=2e-6,atol=2e-9)


@pytest.mark.oracle
def test_unobserved_cells_are_excluded_and_positive_count_one_is_valid(b13):
    m=b13.load('glove');p={k:np.zeros_like(v) for k,v in fixture_parameters().items()}
    with np.errstate(divide='raise',invalid='raise'):
        loss,g=m.glove_loss_gradients(p,[[0,1],[0,0]])
    assert loss==0 and all(np.all(v==0) for v in g.values())
    loss,g=m.glove_loss_gradients(p,[[0,2],[0,0]],x_max=1)
    assert_allclose(loss,math.log(2)**2,atol=1e-15)
    assert_allclose(g['b'],[-2*math.log(2),0],atol=1e-15)
    assert_allclose(g['c'],[0,-2*math.log(2)],atol=1e-15)


@pytest.mark.oracle
def test_exact_one_parameter_update_without_clipping(b13):
    m=b13.load('glove').GloVe(2,epochs=1,window=1,learning_rate=.001,random_state=12,gradient_clip=100.)
    m.fit(['a b a'])
    p=m.initial_parameters_;g={k:np.zeros_like(v) for k,v in p.items()};X=m.cooccurrences_
    for i in range(len(X)):
        for j in range(len(X)):
            if X[i,j]:
                w=min((float(X[i,j])/m.x_max)**m.alpha,1.)
                residual=float(p['W'][i]@p['C'][j])+p['b'][i]+p['c'][j]-math.log(float(X[i,j]))
                delta=2*w*residual
                g['W'][i]+=delta*p['C'][j];g['C'][j]+=delta*p['W'][i]
                g['b'][i]+=delta;g['c'][j]+=delta
    for name in p:
        assert_allclose(m.parameters_[name],p[name]-.001*g[name],atol=1e-15)
    assert m.n_updates_==1


@pytest.mark.parametrize('seed',[21,22,23])
def test_genuine_tiny_corpus_training_and_reproducibility(b13,seed):
    cls=b13.load('glove').GloVe
    texts=['red fox runs','red fox jumps','blue bird flies','blue bird sings']
    a=cls(4,epochs=80,random_state=seed).fit(texts);b=cls(4,epochs=80,random_state=seed).fit(texts)
    assert a.loss_history_[-1]<a.loss_history_[0]-.01
    assert np.all(np.diff(a.loss_history_)<=1e-14)
    assert a.embeddings_.shape==(len(a.vocab_),4)
    for name in a.parameters_:
        assert np.linalg.norm(a.parameters_[name]-a.initial_parameters_[name])>.001
        assert_allclose(a.parameters_[name],b.parameters_[name],atol=0,rtol=0)
    assert_allclose(a.loss_history_,b.loss_history_,atol=0,rtol=0)
    assert not a.converged_ and a.optimization_status_=='iteration-budget'


@pytest.mark.numerical
@pytest.mark.parametrize('count',[1e-12,1.,1e6])
def test_stable_positive_log_counts_and_finite_large_parameters(b13,count):
    m=b13.load('glove');p=fixture_parameters()
    p['W'][:]=1e4;p['C'][:]=-1e4
    with np.errstate(over='raise',invalid='raise',divide='raise'):
        loss,g=m.glove_loss_gradients(p,[[0,count],[count,0]])
    assert np.isfinite(loss) and all(np.isfinite(v).all() for v in g.values())


def test_unicode_unknowns_pruning_owned_vectors_and_atomic_refit(b13):
    cls=b13.load('glove').GloVe;m=cls(2,epochs=3).fit(['CAFÉ café bird !','bird café'])
    assert_allclose(m.embedding('CAFÉ'),m.embedding('cafe\u0301'),atol=0)
    assert_allclose(m.embedding('missing'),0,atol=0)
    before=m.get_embeddings();mapping=dict(m.vocabulary_)
    output=m.get_embeddings();output[:]=123
    assert_allclose(m.get_embeddings(),before,atol=0)
    assert_allclose(m.get_embeddings(combine=False),m.parameters_['W'],atol=0)
    for bad in [[],[''],['a'],['a','b'],[None],['a '*129]]:
        with pytest.raises(ValueError):m.fit(bad)
        assert m.vocabulary_==mapping
        assert_allclose(m.get_embeddings(),before,atol=0)
    pruned=cls(2,min_count=2,epochs=3).fit(['a b a','a rare'])
    assert pruned.vocab_.counts_[0]==2 and 'rare' not in pruned.vocabulary_


@pytest.mark.parametrize('kwargs',[{'dimension':0},{'dimension':17},{'dimension':True},{'window':0},{'window':5},
    {'symmetric':1},{'x_max':0},{'x_max':np.inf},{'alpha':0},{'alpha':1.1},
    {'epochs':0},{'epochs':201},{'learning_rate':0},{'learning_rate':np.nan},
    {'random_state':-1},{'min_count':0},{'max_size':129},{'lowercase':1},{'gradient_clip':0}])
def test_invalid_hyperparameters(b13,kwargs):
    with pytest.raises(ValueError):b13.load('glove').GloVe(**kwargs)


@pytest.mark.parametrize('case',range(15))
def test_invalid_pure_function_inputs(b13,case):
    m=b13.load('glove');p=fixture_parameters()
    calls=[lambda:m.cooccurrence_matrix([],2),lambda:m.cooccurrence_matrix([[2]],2),
        lambda:m.cooccurrence_matrix([[True]],2),lambda:m.cooccurrence_matrix([[1.]],2),
        lambda:m.cooccurrence_matrix([[1]],2,symmetric=1),lambda:m.weighting([-1]),
        lambda:m.weighting([np.nan]),lambda:m.weighting([1e-310]),lambda:m.weighting([1],alpha=0),
        lambda:m.glove_loss_gradients(p,[[0,-1],[1,0]]),lambda:m.glove_loss_gradients(p,np.zeros((2,2))),
        lambda:m.glove_loss_gradients(p,np.ones((3,3))),
        lambda:m.glove_loss_gradients(dict(p,W=np.full((2,2),np.inf)),np.ones((2,2))),
        lambda:m.glove_loss_gradients(dict(p,b=np.array([1.])),np.ones((2,2))),
        lambda:m.glove_loss_gradients(dict(p,C=np.ones((2,3))),np.ones((2,2)))]
    with pytest.raises(ValueError):calls[case]()


def test_unfitted_lookup_input_bounds_and_dense_work_cap(b13):
    cls=b13.load('glove').GloVe
    with pytest.raises(ValueError):cls().get_embeddings()
    with pytest.raises(ValueError):cls().embedding('a')
    m=cls(2,epochs=2).fit(['a b'])
    for word in ['', 'a b', None]:
        with pytest.raises(ValueError):m.embedding(word)
    with pytest.raises(ValueError):m.get_embeddings(combine=1)
    corpus=[' '.join(f'w{i}' for i in range(128))]
    with pytest.raises(ValueError,match='work budget'):cls(16,epochs=200).fit(corpus)
