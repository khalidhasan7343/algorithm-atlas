import math
import numpy as np
from numpy.testing import assert_allclose
import pytest

pytestmark = pytest.mark.ml


def fixture_parameters():
    return {'W_in': np.array([[.2, -.1], [.3, .4], [-.2, .5]]),
            'W_out': np.array([[.1, .6], [-.4, .2], [.5, -.3]])}


def scalar_objective(p, pairs, negatives):
    total = 0.
    for (center, context), noise in zip(pairs, negatives):
        z = float(sum(a*b for a, b in zip(p['W_in'][center], p['W_out'][context])))
        total += math.log1p(math.exp(-z))
        for n in noise:
            z = float(sum(a*b for a, b in zip(p['W_in'][center], p['W_out'][n])))
            total += math.log1p(math.exp(z))
    return total/len(pairs)


@pytest.mark.oracle
@pytest.mark.parametrize('window,expected', [
    (1, [[0,1],[1,0],[1,2],[2,1],[3,4],[4,3]]),
    (2, [[0,1],[0,2],[1,0],[1,2],[2,0],[2,1],[3,4],[4,3]]),
])
def test_exact_context_pairs_and_sentence_boundaries(b13, window, expected):
    m = b13.load('word2vec')
    assert m.context_pairs([[0,1,2], [], [3,4]], window).tolist() == expected
    assert m.context_pairs([[1], [2]], window).shape == (0, 2)


@pytest.mark.oracle
def test_noise_distribution_and_replacement_sampling(b13):
    m = b13.load('word2vec')
    assert_allclose(m.noise_distribution([0,1,16]), [0,1/9,8/9], atol=1e-15)
    draws = m.sample_negatives([0,1,16], 7000, 5, 22)
    assert draws.shape == (7000,5) and not np.any(draws == 0)
    assert abs(np.mean(draws == 1)-1/9) < .01
    assert np.any(np.all(draws == draws[:, :1], axis=1))
    assert_allclose(draws, m.sample_negatives([0,1,16], 7000, 5, 22), atol=0, rtol=0)
    # A single-word noise law necessarily collides with any positive context ID0.
    assert_allclose(m.sample_negatives([5], 2, 2, 0), 0, atol=0)


@pytest.mark.oracle
@pytest.mark.numerical
def test_sgns_independent_loss_and_gradients_every_parameter_group(b13):
    m = b13.load('word2vec')
    p = fixture_parameters()
    pairs = np.array([[0,1],[0,1],[1,2]])
    negatives = np.array([[1,1],[2,1],[0,2]])
    loss, gradients = m.sgns_loss_gradients(p, pairs, negatives)
    assert_allclose(loss, scalar_objective(p, pairs, negatives), atol=2e-15)
    for name in ('W_in','W_out'):
        for index in np.ndindex(p[name].shape):
            plus = {k:v.copy() for k,v in p.items()}
            minus = {k:v.copy() for k,v in p.items()}
            plus[name][index] += 1e-6
            minus[name][index] -= 1e-6
            finite_difference = (scalar_objective(plus,pairs,negatives)-scalar_objective(minus,pairs,negatives))/2e-6
            assert_allclose(gradients[name][index], finite_difference, rtol=2e-6, atol=3e-9)


@pytest.mark.oracle
def test_zero_logits_exact_loss_and_duplicate_accumulation(b13):
    m = b13.load('word2vec')
    p = {'W_in':np.array([[1.],[2.]]), 'W_out':np.zeros((2,1))}
    loss, g = m.sgns_loss_gradients(p, [[0,1],[0,1]], [[1,1],[1,1]])
    assert_allclose(loss, 3*math.log(2), atol=1e-15)
    assert_allclose(g['W_in'], 0, atol=0)
    assert_allclose(g['W_out'], [[0.],[.5]], atol=0)


@pytest.mark.numerical
@pytest.mark.parametrize('magnitude',[100.,10000.,1e6])
def test_extreme_logits_are_stable(b13, magnitude):
    m = b13.load('word2vec')
    p = {'W_in':np.array([[magnitude],[-magnitude]]), 'W_out':np.array([[magnitude],[-magnitude]])}
    with np.errstate(over='raise', invalid='raise', divide='raise'):
        loss,g = m.sgns_loss_gradients(p, [[0,1],[1,0]], [[0,1],[1,0]])
    assert np.isfinite(loss) and all(np.isfinite(v).all() for v in g.values())


@pytest.mark.oracle
def test_exact_one_gradient_update(b13):
    m = b13.load('word2vec').Word2Vec(dimension=2, epochs=1, window=1,
              negative_samples=2, learning_rate=.01, random_state=12, gradient_clip=100.)
    m.fit(['a b a'])
    p, expected = m.initial_parameters_, {k:np.zeros_like(v) for k,v in m.initial_parameters_.items()}
    for (i,j), noise in zip(m.pairs_,m.negative_ids_):
        z = float(p['W_in'][i]@p['W_out'][j])
        factor = (1/(1+math.exp(-z))-1)/len(m.pairs_)
        expected['W_in'][i] += factor*p['W_out'][j]
        expected['W_out'][j] += factor*p['W_in'][i]
        for n in noise:
            z = float(p['W_in'][i]@p['W_out'][n])
            factor = 1/(1+math.exp(-z))/len(m.pairs_)
            expected['W_in'][i] += factor*p['W_out'][n]
            expected['W_out'][n] += factor*p['W_in'][i]
    for name in p:
        assert_allclose(m.parameters_[name], p[name]-.01*expected[name], atol=1e-15)
    assert m.n_updates_ == 1


@pytest.mark.parametrize('seed',[21,22,23])
def test_tiny_corpus_learning_and_reproducibility(b13,seed):
    cls = b13.load('word2vec').Word2Vec
    texts = ['red fox runs','red fox jumps','blue bird flies','blue bird sings']
    a = cls(4, epochs=80, random_state=seed).fit(texts)
    b = cls(4, epochs=80, random_state=seed).fit(texts)
    assert a.loss_history_[-1] < a.loss_history_[0]-.01
    assert np.all(np.diff(a.loss_history_) <= 1e-14)
    for name in a.parameters_:
        assert np.linalg.norm(a.parameters_[name]-a.initial_parameters_[name]) > .01
        assert_allclose(a.parameters_[name],b.parameters_[name],atol=0,rtol=0)
    assert_allclose(a.negative_ids_,b.negative_ids_,atol=0,rtol=0)
    assert_allclose(a.loss_history_,b.loss_history_,atol=0,rtol=0)
    assert a.embeddings_.shape == (len(a.vocab_),4)
    assert a.optimization_status_ == 'iteration-budget' and not a.converged_


def test_unknown_unicode_case_pruning_ownership_and_atomic_refit(b13):
    cls = b13.load('word2vec').Word2Vec
    m = cls(2, epochs=4).fit(['CAFÉ café bird !','bird café'])
    assert_allclose(m.embedding('CAFÉ'),m.embedding('cafe\u0301'),atol=0)
    assert_allclose(m.embedding('missing'),[0.,0.],atol=0)
    before, vocabulary = m.get_embeddings(), dict(m.vocabulary_)
    out = m.get_embeddings();out[:] = 100
    assert_allclose(m.get_embeddings(),before,atol=0)
    assert_allclose(m.get_embeddings(combine=True),m.parameters_['W_in']+m.parameters_['W_out'])
    for bad in [[],[''],['a'],['a','b'],[None],['a '*129]]:
        with pytest.raises(ValueError):m.fit(bad)
        assert m.vocabulary_ == vocabulary
        assert_allclose(m.get_embeddings(),before,atol=0)
    pruned = cls(2,min_count=2,epochs=4).fit(['a b a','a rare'])
    assert pruned.vocab_.counts_[0] == 2 and pruned.vocab_.encode('unseen')[0] == 0
    assert 'rare' not in pruned.vocabulary_


@pytest.mark.parametrize('kwargs',[{'dimension':0},{'dimension':17},{'dimension':True},{'window':0},{'window':5},
    {'negative_samples':0},{'negative_samples':9},{'epochs':0},{'epochs':201},{'learning_rate':0},
    {'learning_rate':np.nan},{'random_state':-1},{'min_count':0},{'max_size':129},
    {'lowercase':1},{'gradient_clip':0}])
def test_invalid_hyperparameters(b13,kwargs):
    with pytest.raises(ValueError):b13.load('word2vec').Word2Vec(**kwargs)


@pytest.mark.parametrize('case',range(12))
def test_invalid_pure_function_inputs(b13,case):
    m = b13.load('word2vec');p=fixture_parameters();pairs=[[0,1]];noise=[[2]]
    calls = [lambda:m.context_pairs([[0,True]]),lambda:m.context_pairs([[-1]]),
             lambda:m.context_pairs([[128]]),lambda:m.context_pairs([],1),
             lambda:m.noise_distribution([0,0]),lambda:m.noise_distribution([1.,2.]),
             lambda:m.sample_negatives([1],0),lambda:m.sgns_loss_gradients(p,[[3,0]],noise),
             lambda:m.sgns_loss_gradients(p,pairs,[[-1]]),lambda:m.sgns_loss_gradients(p,[[0.,1.]],noise),
             lambda:m.sgns_loss_gradients({'W_in':np.full((2,2),np.nan),'W_out':np.ones((2,2))},pairs,noise),
             lambda:m.sgns_loss_gradients({'W_in':np.ones((3,2)),'W_out':np.ones((2,2))},pairs,noise)]
    with pytest.raises(ValueError):calls[case]()


def test_unfitted_invalid_lookup_and_resource_bounds(b13):
    cls = b13.load('word2vec').Word2Vec
    with pytest.raises(ValueError):cls().embedding('x')
    with pytest.raises(ValueError):cls().get_embeddings()
    m = cls(2,epochs=2).fit(['a b'])
    for word in ['', 'a b', None]:
        with pytest.raises(ValueError):m.embedding(word)
    with pytest.raises(ValueError):m.get_embeddings(combine=1)
    corpus = [' '.join(f'w{i}' for i in range(128))]*8
    with pytest.raises(ValueError,match='work budget'):
        cls(16,window=4,negative_samples=8,epochs=200).fit(corpus)
