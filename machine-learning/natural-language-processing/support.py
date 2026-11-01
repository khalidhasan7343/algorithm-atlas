"""Bounded, deterministic B13 text contracts; no fitted state shared across models."""
from collections import Counter
import importlib.util
from pathlib import Path
import re
import sys
import unicodedata
import numpy as np

ROOT = Path(__file__).resolve().parent
TOPICS = ('bag-of-words','tf-idf','word2vec','glove','bert','gpt','hidden-markov-models-pos-tagging','named-entity-recognition','conditional-random-fields','n-gram-language-models','cyk-parsing')


def load(topic):
    if topic not in TOPICS:
        raise ValueError('unknown B13 canonical')
    return module('atlas_b13_'+topic.replace('-','_'), ROOT/topic/'python/solution.py')


def module(name, path):
    cached = sys.modules.get(name)
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    try:
        spec.loader.exec_module(result)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return result


def integer(value, name, low, high):
    if isinstance(value, (bool,np.bool_)) or not isinstance(value,(int,np.integer)) or not low <= value <= high:
        raise ValueError(f'{name} must be integer in [{low},{high}]')
    return int(value)


def scalar(value, name, low, high):
    if isinstance(value,(bool,np.bool_)) or not isinstance(value,(int,float,np.integer,np.floating)) or not np.isfinite(value) or not low <= value <= high:
        raise ValueError(f'{name} must be finite in [{low},{high}]')
    return float(value)


def boolean(value,name):
    if not isinstance(value,(bool,np.bool_)):
        raise ValueError(name+' must be boolean')
    return bool(value)


def tokenize(text, *, lowercase=True):
    """NFC + optional casefold; Unicode word runs, individual punctuation tokens."""
    lowercase=boolean(lowercase,'lowercase')
    if not isinstance(text,str) or len(text)>4096:
        raise ValueError('text must be a string of at most4096 code points')
    text=unicodedata.normalize('NFC',text)
    if lowercase:text=text.casefold()
    tokens=re.findall(r'\w+|[^\w\s]',text,flags=re.UNICODE)
    if len(tokens)>128 or any(len(t)>128 for t in tokens):
        raise ValueError('at most128 tokens per text and128 code points per token')
    return tokens


def corpus(texts, *, lowercase=True):
    if not isinstance(texts,(list,tuple)) or not 1 <= len(texts) <= 64:
        raise ValueError('corpus requires1..64 independent strings')
    data=[tokenize(t,lowercase=lowercase) for t in texts]
    if sum(map(len,data))>2048:
        raise ValueError('corpus exceeds2048 tokens')
    return data


class Vocabulary:
    """Reserved UNK at0; retained training words have lexicographic indices."""
    def __init__(self, *, min_count=1,max_size=128,lowercase=True):
        self.min_count=integer(min_count,'min_count',1,2048)
        self.max_size=integer(max_size,'max_size',1,128)
        self.lowercase=boolean(lowercase,'lowercase')

    def _fit_documents(self,documents,*,pretokenized):
        counts=Counter(t for doc in documents for t in doc)
        retained=sorted((t for t,n in counts.items() if n>=self.min_count),key=lambda t:(-counts[t],t))[:self.max_size-1]
        words=sorted(retained)
        tokens=('<UNK>',*words)
        index={t:i for i,t in enumerate(tokens)}
        encoded=[[index.get(t,0) for t in doc] for doc in documents]
        mapped_counts=np.bincount([i for doc in encoded for i in doc],minlength=len(tokens))
        self.tokens_,self.index_=tokens,index
        self.vocabulary_=dict(index);self.counts_=mapped_counts
        self.pretokenized_=pretokenized
        return self

    def fit(self,texts):
        return self._fit_documents(corpus(texts,lowercase=self.lowercase),pretokenized=False)

    def _normalize_tokens(self,tokens):
        if not isinstance(tokens,(list,tuple)) or len(tokens)>128:
            raise ValueError('at most128 token strings required')
        result=[]
        for token in tokens:
            if not isinstance(token,str) or not token or len(token)>128:
                raise ValueError('bounded nonempty token strings required')
            token=unicodedata.normalize('NFC',token)
            if tokenize(token,lowercase=False)!=[token]:
                raise ValueError('each supplied token must be one original-case tokenizer unit')
            normalized=token.casefold() if self.lowercase else token
            if len(normalized)>128:
                raise ValueError('normalized token exceeds128 code points')
            result.append(normalized)
        return result

    def fit_tokens(self,sentences):
        """Preserve supplied sentence/token boundaries while normalizing each unit."""
        if not isinstance(sentences,(list,tuple)) or not 1<=len(sentences)<=64:
            raise ValueError('1..64 tokenized sentences required')
        data=[self._normalize_tokens(row) for row in sentences]
        if sum(map(len,data))>2048:raise ValueError('corpus exceeds2048 tokens')
        return self._fit_documents(data,pretokenized=True)

    def encode(self,text):
        if not hasattr(self,'index_'):raise ValueError('fit vocabulary first')
        units=self._normalize_tokens(tokenize(text,lowercase=False)) if self.pretokenized_ else tokenize(text,lowercase=self.lowercase)
        return np.array([self.index_.get(t,0) for t in units],dtype=np.int64)

    def encode_tokens(self,tokens):
        if not hasattr(self,'index_'):raise ValueError('fit vocabulary first')
        normalized=self._normalize_tokens(tokens)
        if not self.pretokenized_ and any(tokenize(t,lowercase=False)!=[t] for t in normalized):
            raise ValueError('casefold changes token boundaries;use fit_tokens for tokenized input')
        return np.array([self.index_.get(t,0) for t in normalized],dtype=np.int64)

    def __len__(self):
        if not hasattr(self,'tokens_'):raise ValueError('fit vocabulary first')
        return len(self.tokens_)


def finite_matrix(value,name,*,rows=128,cols=128):
    a=np.asarray(value)
    if a.ndim!=2 or not 1<=a.shape[0]<=rows or not 1<=a.shape[1]<=cols or a.dtype.kind not in 'iuf':
        raise ValueError(name+' must be a bounded real matrix')
    a=np.array(a,dtype=float,copy=True)
    if not np.isfinite(a).all() or np.max(np.abs(a))>1e6:
        raise ValueError(name+' values must be finite with magnitude<=1e6')
    return a


def ready(model,attribute='vocabulary_'):
    if not hasattr(model,attribute):raise ValueError('fit model first')


def logsumexp(value,axis=None):
    # Canonical B11 owns the already approved stable inference primitive.
    hmm=module('atlas_b11_hmm_for_b13',ROOT.parent/'time-series/hidden-markov-models/python/solution.py')
    return hmm.logsumexp(value,axis=axis)
