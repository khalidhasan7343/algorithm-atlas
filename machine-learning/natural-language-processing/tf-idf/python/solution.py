import importlib.util
from pathlib import Path
import sys
import numpy as np
_spec=importlib.util.spec_from_file_location('atlas_b13_support',Path(__file__).resolve().parents[2]/'support.py')
s=sys.modules.get(_spec.name)
if s is None:
    s=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=s;_spec.loader.exec_module(s)

class TFIDF:
    """Raw TF, smoothed log IDF, optional row L2 normalization."""
    def __init__(self,*,norm='l2',lowercase=True,min_count=1,max_features=127):
        if not (norm is None or isinstance(norm,str) and norm=='l2'):raise ValueError("norm must be None or 'l2'")
        self.norm=norm;self.lowercase=s.boolean(lowercase,'lowercase')
        self.min_count=s.integer(min_count,'min_count',1,2048)
        self.max_features=s.integer(max_features,'max_features',1,127)

    def fit(self,texts):
        bow=s.load('bag-of-words').BagOfWords(lowercase=self.lowercase,min_count=self.min_count,max_features=self.max_features)
        counts=bow.fit_transform(texts);df=(counts>0).sum(axis=0)
        idf=np.log((1+len(texts))/(1+df))+1
        self.bow_=bow;self.document_frequency_=df.copy();self.idf_=idf
        self.n_documents_=len(texts);self.vocabulary_=dict(bow.vocabulary_);self.feature_names_=bow.feature_names_
        return self

    def transform(self,texts):
        s.ready(self);weights=self.bow_.transform(texts)*self.idf_
        if self.norm=='l2':
            norm=np.sqrt(np.sum(weights**2,axis=1,keepdims=True))
            weights=np.divide(weights,norm,out=np.zeros_like(weights),where=norm>0)
        return weights

    def fit_transform(self,texts):return self.fit(texts).transform(texts)
