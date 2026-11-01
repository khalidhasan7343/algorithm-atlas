import numpy as np
import pytest
pytestmark=[pytest.mark.ml]

@pytest.mark.oracle
def test_exact_df_idf_tf_hand_oracle(b13):
 m=b13.load('tf-idf').TFIDF(norm=None);out=m.fit_transform(['a a b','b c',''])
 assert m.feature_names_==('a','b','c')
 np.testing.assert_array_equal(m.document_frequency_,[1,2,1])
 idf=np.array([np.log(2)+1,np.log(4/3)+1,np.log(2)+1])
 np.testing.assert_allclose(m.idf_,idf)
 np.testing.assert_allclose(out,[[2*idf[0],idf[1],0],[0,idf[1],idf[2]],[0,0,0]])
 old=m.idf_.copy();np.testing.assert_allclose(m.transform(['c new']),[[0,0,idf[2]]]);np.testing.assert_array_equal(old,m.idf_)

@pytest.mark.parametrize('norm',[None,'l2'])
def test_normalization_zero_common_and_duplicate_documents(b13,norm):
 m=b13.load('tf-idf').TFIDF(norm=norm);x=m.fit_transform(['a a b','a a b',''])
 np.testing.assert_array_equal(x[0],x[1]);assert not x[2].any()
 if norm:np.testing.assert_allclose(np.linalg.norm(x[:2],axis=1),1)
 assert m.fit_transform(['','']).shape==(2,0)

@pytest.mark.reference
@pytest.mark.oracle
def test_aligned_sklearn_vectorizer(b13):
 from sklearn.feature_extraction.text import TfidfVectorizer
 texts=['Cat cat dog!','dog.', '']
 m=b13.load('tf-idf').TFIDF();actual=m.fit_transform(texts)
 ref=TfidfVectorizer(tokenizer=b13.tokenize,token_pattern=None,lowercase=False,norm='l2',smooth_idf=True).fit(texts)
 assert tuple(ref.get_feature_names_out())==m.feature_names_
 np.testing.assert_allclose(actual,ref.transform(texts).toarray())

@pytest.mark.parametrize('texts',[[],None,['a '*129],[None]])
def test_invalid_atomic_refit(b13,texts):
 m=b13.load('tf-idf').TFIDF().fit(['old'])
 with pytest.raises(ValueError):m.fit(texts)
 assert m.feature_names_==('old',)

@pytest.mark.parametrize('kwargs',[{'norm':'l1'},{'norm':np.array(['l2'])},{'lowercase':1},{'min_count':False},{'max_features':128}])
def test_invalid_settings(b13,kwargs):
 with pytest.raises(ValueError):b13.load('tf-idf').TFIDF(**kwargs)

def test_unfitted_and_canonical_bow_reuse(b13):
 m=b13.load('tf-idf').TFIDF()
 with pytest.raises(ValueError):m.transform(['x'])
 m.fit(['a b']);assert isinstance(m.bow_,b13.load('bag-of-words').BagOfWords)
