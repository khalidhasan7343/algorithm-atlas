import numpy as np
import pytest
pytestmark=[pytest.mark.ml]

@pytest.mark.oracle
def test_exact_hand_counts_unknown_and_training_boundaries(b13):
 m=b13.load('bag-of-words').BagOfWords().fit(['Cat cat dog','DOG!',''])
 assert m.feature_names_==('!','cat','dog')
 np.testing.assert_array_equal(m.transform(['Cat cat dog','DOG!','']),[[0,2,1],[1,0,1],[0,0,0]])
 np.testing.assert_array_equal(m.transform(['cat unseen']),[[0,1,0]])
 assert 'unseen' not in m.vocabulary_

@pytest.mark.parametrize('binary',[True,False])
def test_binary_and_empty_documents(b13,binary):
 m=b13.load('bag-of-words').BagOfWords(binary=binary)
 np.testing.assert_array_equal(m.fit_transform(['a a','']),[[1 if binary else 2],[0]])
 assert m.fit_transform(['','']).shape==(2,0)

@pytest.mark.parametrize('lowercase',[True,False])
def test_case_unicode_deterministic_vocabulary(b13,lowercase):
 c=b13.load('bag-of-words').BagOfWords
 a=c(lowercase=lowercase).fit(['Café café','Z a']);b=c(lowercase=lowercase).fit(['Z a','Café café'])
 assert a.feature_names_==b.feature_names_;assert len(a.feature_names_)==(3 if lowercase else 4)

@pytest.mark.parametrize('texts',[[],None,'abc',[1],['a '*129]])
def test_invalid_inputs_atomic_refit(b13,texts):
 m=b13.load('bag-of-words').BagOfWords().fit(['old'])
 with pytest.raises(ValueError):m.fit(texts)
 assert m.feature_names_==('old',)

@pytest.mark.parametrize('kwargs',[{'binary':1},{'max_features':0},{'max_features':128},{'min_count':0},{'lowercase':None}])
def test_invalid_hyperparameters(b13,kwargs):
 with pytest.raises(ValueError):b13.load('bag-of-words').BagOfWords(**kwargs)

def test_unfitted_owned_outputs_and_frequency(b13):
 m=b13.load('bag-of-words').BagOfWords(min_count=2)
 with pytest.raises(ValueError):m.transform(['x'])
 m.fit(['x x rare']);a=m.transform(['x']);a[:]=-100
 np.testing.assert_array_equal(m.transform(['x']),[[1]])
