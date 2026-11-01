import importlib.util
from pathlib import Path
import sys
import numpy as np
_spec=importlib.util.spec_from_file_location('atlas_b13_support',Path(__file__).resolve().parents[2]/'support.py')
s=sys.modules.get(_spec.name)
if s is None:
    s=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=s;_spec.loader.exec_module(s)

class BagOfWords:
    """Raw or binary counts of retained training terms; unknowns ignored."""
    def __init__(self,*,lowercase=True,min_count=1,max_features=127,binary=False):
        self.lowercase=s.boolean(lowercase,'lowercase')
        self.min_count=s.integer(min_count,'min_count',1,2048)
        self.max_features=s.integer(max_features,'max_features',1,127)
        self.binary=s.boolean(binary,'binary')

    def fit(self,texts):
        vocab=s.Vocabulary(lowercase=self.lowercase,min_count=self.min_count,max_size=self.max_features+1).fit(texts)
        self.vocab_=vocab;self.feature_names_=tuple(vocab.tokens_[1:])
        self.vocabulary_={word:i for i,word in enumerate(self.feature_names_)}
        return self

    def transform(self,texts):
        s.ready(self);s.corpus(texts,lowercase=self.lowercase)
        out=np.zeros((len(texts),len(self.feature_names_)),dtype=np.int64)
        for i,text in enumerate(texts):
            ids=self.vocab_.encode(text);out[i]=np.bincount(ids,minlength=len(self.vocab_))[1:]
        return (out>0).astype(np.int64) if self.binary else out

    def fit_transform(self,texts):return self.fit(texts).transform(texts)
