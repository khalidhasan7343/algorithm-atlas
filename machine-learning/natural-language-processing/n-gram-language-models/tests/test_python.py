import math
import numpy as np
import pytest
pytestmark=[pytest.mark.ml]

@pytest.mark.oracle
def test_counts_probabilities_log_perplexity_hand(b13):
 m=b13.load('n-gram-language-models').NGramLanguageModel(2).fit(['a b','a a'])
 assert m.tokens_==('<UNK>','a','b','<EOS>')
 assert m.counts_[('<BOS>','a')]==2 and m.context_counts_[('a',)]==3
 np.testing.assert_allclose(m.distribution(['<BOS>']),[1/6,3/6,1/6,1/6])
 expected=math.log(3/6)+math.log(2/7)+math.log(2/5)
 np.testing.assert_allclose(m.log_probability('a b'),expected)
 np.testing.assert_allclose(m.perplexity('a b'),math.exp(-expected/3))

@pytest.mark.parametrize('order',[1,2,3,4,5])
@pytest.mark.parametrize('k',[.1,1.])
def test_general_order_normalization_boundaries_unknown(b13,order,k):
 m=b13.load('n-gram-language-models').NGramLanguageModel(order,k=k).fit(['a b','c'])
 np.testing.assert_allclose(m.distribution(['unseen']*(order-1)).sum(),1)
 assert m.probability('unseen',['<BOS>']*(order-1))>0
 assert m.log_probability('')<0 and math.isfinite(m.perplexity('unknown'))
 assert 'unknown' not in m.vocabulary_.index_
 assert m.counts_[tuple(['<BOS>']*(order-1)+['c'])]==1
 assert m.context_counts_.get(('b','c'),0)==0

@pytest.mark.parametrize('seed',[0,7,99])
def test_seeded_bounded_generation(b13,seed):
 m=b13.load('n-gram-language-models').NGramLanguageModel().fit(['a b a','b a b'])
 assert m.generate(random_state=seed,max_tokens=20)==m.generate(random_state=seed,max_tokens=20)
 assert m.generate(max_tokens=0)==[]

@pytest.mark.parametrize('kwargs',[{'order':0},{'order':6},{'order':True},{'k':0},{'k':float('nan')},{'min_count':0},{'max_size':128},{'lowercase':0}])
def test_invalid_hyperparameters(b13,kwargs):
 with pytest.raises(ValueError):b13.load('n-gram-language-models').NGramLanguageModel(**kwargs)

@pytest.mark.parametrize('context',[[],['a','b'],None,'a',[None]])
def test_invalid_context(b13,context):
 m=b13.load('n-gram-language-models').NGramLanguageModel().fit(['a'])
 with pytest.raises(ValueError):m.distribution(context)

def test_unfitted_empty_training_atomic_and_pruning(b13):
 m=b13.load('n-gram-language-models').NGramLanguageModel(min_count=2)
 with pytest.raises(ValueError):m.log_probability('a')
 m.fit(['rare rare x']);assert m.vocabulary_.tokens_==('<UNK>','rare')
 old=m.counts_.copy()
 with pytest.raises(ValueError):m.fit([])
 assert m.counts_==old
 for token in (np.array(['<UNK>']),np.array(['<EOS>']),None,True):
  with pytest.raises(ValueError):m.probability(token,['<BOS>'])
 with pytest.raises(ValueError):m.distribution([np.array(['<BOS>'])])
 z=b13.load('n-gram-language-models').NGramLanguageModel().fit([''])
 assert np.isfinite(z.perplexity(''))
