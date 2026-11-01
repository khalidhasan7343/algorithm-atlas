import itertools
import math
import numpy as np
import pytest
pytestmark = [pytest.mark.ml]


def toy(b13, **kwargs):
    return b13.load('hidden-markov-models-pos-tagging').HMMPOSTagger(**kwargs).fit([['dogs','run'],['cats','sleep'],['dogs','sleep']], [['N','V']]*3)


@pytest.mark.oracle
def test_hmm_pos_exact_supervised_counts_tables_and_decoding(b13):
    m = toy(b13)
    assert m.tags_ == ('N','V') and m.vocabulary_.tokens_ == ('<UNK>','cats','dogs','run','sleep')
    np.testing.assert_array_equal(m.initial_counts_, [3,0])
    np.testing.assert_array_equal(m.transition_counts_, [[0,3],[0,0]])
    np.testing.assert_array_equal(m.emission_counts_, [[0,1,2,0,0],[0,0,0,1,2]])
    np.testing.assert_allclose(m.model_.initial_, [.8,.2])
    np.testing.assert_allclose(m.model_.transition_, [[.2,.8],[.5,.5]])
    np.testing.assert_allclose(m.model_.emission_, [[1/8,2/8,3/8,1/8,1/8],[1/8,1/8,1/8,2/8,3/8]])
    assert m.tag(['dogs','run']) == ['N','V']
    np.testing.assert_allclose(m.decode(['dogs','run'])[1], math.log(.06))


@pytest.mark.oracle
@pytest.mark.parametrize('words', [['dogs'],['dogs','run'],['unknown','sleep'],['cats','dogs','run']])
def test_hmm_pos_exhaustive_path_likelihood_and_posterior(b13, words):
    m = toy(b13)
    symbols = m.vocabulary_.encode_tokens(words)
    paths = list(itertools.product(range(2), repeat=len(words)))
    probabilities = []
    for path in paths:
        value = m.model_.initial_[path[0]] * m.model_.emission_[path[0], symbols[0]]
        for t in range(1,len(words)):
            value *= m.model_.transition_[path[t-1],path[t]] * m.model_.emission_[path[t], symbols[t]]
        probabilities.append(value)
    best = paths[int(np.argmax(probabilities))]
    assert m.tag(words) == [m.tags_[i] for i in best]
    np.testing.assert_allclose(m.decode(words)[1], np.log(max(probabilities)))
    np.testing.assert_allclose(m.score(words), np.log(sum(probabilities)))
    expected = np.zeros((len(words),2))
    for path, probability in zip(paths, probabilities):
        for t, label in enumerate(path): expected[t,label] += probability/sum(probabilities)
    np.testing.assert_allclose(m.posterior(words), expected)


def test_hmm_pos_canonical_B11_identity_compatibility(b13):
    mod = b13.load('hidden-markov-models-pos-tagging');m=toy(b13)
    engine = b13.module('atlas_b11_hmm_for_b13', b13.ROOT.parent/'time-series/hidden-markov-models/python/solution.py')
    assert isinstance(m.model_, engine.CategoricalHMM)
    direct = engine.CategoricalHMM(2,5,initial=m.model_.initial_,transition=m.model_.transition_,emission=m.model_.emission_)
    obs=m.vocabulary_.encode_tokens(['dogs','unknown'])
    path,score=direct.decode(obs)
    assert m.tag(['dogs','unknown'])==[m.tags_[i] for i in path]
    assert score==m.decode(['dogs','unknown'])[1] and direct.score(obs)==m.score(['dogs','unknown'])


@pytest.mark.parametrize('lowercase',[True,False])
def test_hmm_pos_case_unicode_unknown_empty_boundaries_ownership(b13,lowercase):
    m=b13.load('hidden-markov-models-pos-tagging').HMMPOSTagger(lowercase=lowercase).fit([['Café','runs'],['CAFÉ']], [['N','V'],['N']])
    assert len(m.tag(['café','unseen']))==2
    assert m.tag([])==[] and m.decode([])==([],0.) and m.score([])==0 and m.posterior([]).shape==(0,2)
    assert m.transition_counts_.sum()==1 and m.initial_counts_.sum()==2
    before=m.vocabulary_.tokens_;m.tag_text('Unknown runs');assert before==m.vocabulary_.tokens_
    posterior=m.posterior(['runs']);posterior[:]=5;np.testing.assert_allclose(m.posterior(['runs']).sum(1),1)


def test_hmm_pos_evaluation_reproducibility_pruning_no_gold_leak(b13):
    a,b=toy(b13,min_count=2),toy(b13,min_count=2)
    np.testing.assert_array_equal(a.model_.emission_,b.model_.emission_)
    assert a.vocabulary_.tokens_==('<UNK>','dogs','sleep')
    assert a.evaluate([['dogs','sleep']],[['N','V']])==dict(correct=2,tokens=2,accuracy=1.)
    old=a.tag(['dogs','sleep']);a.evaluate([['dogs','sleep']],[['V','N']]);assert a.tag(['dogs','sleep'])==old
    assert a.evaluate([[]],[[]])['accuracy'] is None
    with pytest.raises(ValueError):a.evaluate([['dogs']],[['BAD']])


@pytest.mark.parametrize('kwargs',[{'alpha':0},{'alpha':float('inf')},{'max_size':17},{'max_size':True},{'min_count':0},{'lowercase':1}])
def test_hmm_pos_invalid_hyperparameters(b13,kwargs):
    with pytest.raises(ValueError):b13.load('hidden-markov-models-pos-tagging').HMMPOSTagger(**kwargs)


@pytest.mark.parametrize('sentences,tags', [([],[]),([[]],[[]]),([['a']],[[]]),([['a']],[[1]]),([['a b']],[['X']]),([['a']],[['']]),([['a']]*33,[['X']]*33),([['a']*65],[['X']*65]),([['a']]*9,[[str(i)] for i in range(9)])])
def test_hmm_pos_invalid_training_atomic(b13,sentences,tags):
    m=toy(b13);before=m.model_.emission_.copy()
    with pytest.raises(ValueError):m.fit(sentences,tags)
    np.testing.assert_array_equal(m.model_.emission_,before)


@pytest.mark.parametrize('words',[None,'dogs',[None],['a b'],['a']*65,['x'*129]])
def test_hmm_pos_invalid_query(b13,words):
    with pytest.raises(ValueError):toy(b13).tag(words)


def test_hmm_pos_unfitted_and_maximum_unknown_vocabulary(b13):
    cls=b13.load('hidden-markov-models-pos-tagging').HMMPOSTagger
    with pytest.raises(ValueError):cls().tag([])
    m=cls(max_size=1).fit([['a','b']],[['N','V']]);assert m.vocabulary_.tokens_==('<UNK>',)
    assert len(m.tag(['anything']))==1 and np.isfinite(m.score(['anything']))


@pytest.mark.oracle
def test_hmm_pos_unicode_casefold_preserves_training_token_identity(b13):
    cls=b13.load('hidden-markov-models-pos-tagging').HMMPOSTagger
    m=cls().fit([['İ','runs']],[['N','V']])
    assert m.vocabulary_.pretokenized_ and 'i\u0307' in m.vocabulary_.index_
    ids=m.vocabulary_.encode_tokens(['İ','runs'])
    assert ids[0]!=0
    np.testing.assert_array_equal(ids,m.vocabulary_.encode('İ runs'))
    np.testing.assert_array_equal(m.vocabulary_.counts_,m.emission_counts_.sum(axis=0))
    assert m.emission_counts_[m.tag_index_['N'],ids[0]]==1
    assert m.tag_text('İ runs')==m.tag(['İ','runs'])==['N','V']
