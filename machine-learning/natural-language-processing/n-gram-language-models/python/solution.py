import importlib.util
from pathlib import Path
import sys
import numpy as np
_spec=importlib.util.spec_from_file_location('atlas_b13_support',Path(__file__).resolve().parents[2]/'support.py')
s=sys.modules.get(_spec.name)
if s is None:
    s=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=s;_spec.loader.exec_module(s)

from collections import Counter
import math

class NGramLanguageModel:
    """Fixed-order add-k counts; sentence log likelihood scores tokens plus EOS."""
    BOS='<BOS>';EOS='<EOS>';UNK='<UNK>'
    def __init__(self,order=2,*,k=1.,min_count=1,max_size=127,lowercase=True):
        self.order=s.integer(order,'order',1,5);self.k=s.scalar(k,'k',1e-8,100.)
        self.min_count=s.integer(min_count,'min_count',1,2048)
        self.max_size=s.integer(max_size,'max_size',1,127);self.lowercase=s.boolean(lowercase,'lowercase')

    def fit(self,texts):
        s.corpus(texts,lowercase=self.lowercase)
        vocab=s.Vocabulary(min_count=self.min_count,max_size=self.max_size,lowercase=self.lowercase).fit(texts)
        counts,contexts=Counter(),Counter()
        for text in texts:
            seq=[self.BOS]*(self.order-1)+[vocab.tokens_[i] for i in vocab.encode(text)]+[self.EOS]
            for t in range(self.order-1,len(seq)):
                context=tuple(seq[t-self.order+1:t]) if self.order>1 else ()
                counts[context+(seq[t],)]+=1;contexts[context]+=1
        self.vocabulary_=vocab;self.tokens_=(*vocab.tokens_,self.EOS)
        self.counts_=counts;self.context_counts_=contexts
        return self

    def _word(self,word,*,context=False):
        if not isinstance(word,str):raise ValueError('token must be string')
        if context and word==self.BOS:return word
        if word in (self.UNK,self.EOS):return word
        tokens=s.tokenize(word,lowercase=self.lowercase)
        if len(tokens)!=1:raise ValueError('one token required')
        return tokens[0] if tokens[0] in self.vocabulary_.index_ else self.UNK

    def distribution(self,context=()):
        s.ready(self)
        if not isinstance(context,(list,tuple)) or len(context)!=self.order-1:
            raise ValueError('context must have order-1 tokens')
        context=tuple(self._word(w,context=True) for w in context)
        denominator=self.context_counts_[context]+self.k*len(self.tokens_)
        return np.array([(self.counts_[context+(w,)]+self.k)/denominator for w in self.tokens_])

    def probability(self,word,context=()):
        s.ready(self);word=self._word(word)
        return float(self.distribution(context)[self.tokens_.index(word)])

    def log_probability(self,text):
        s.ready(self);seq=[self.BOS]*(self.order-1)+[self.vocabulary_.tokens_[i] for i in self.vocabulary_.encode(text)]+[self.EOS]
        total=0.
        for t in range(self.order-1,len(seq)):
            context=seq[t-self.order+1:t] if self.order>1 else ()
            total+=math.log(self.probability(seq[t],context))
        return total

    def perplexity(self,text):
        size=len(s.tokenize(text,lowercase=self.lowercase))+1
        return math.exp(-self.log_probability(text)/size)

    def predict_next(self,context=()):
        s.ready(self);return self.tokens_[int(np.argmax(self.distribution(context)))]

    def generate(self,*,max_tokens=16,random_state=0):
        s.ready(self);limit=s.integer(max_tokens,'max_tokens',0,128)
        seed=s.integer(random_state,'random_state',0,2**32-1);rng=np.random.default_rng(seed)
        context=[self.BOS]*(self.order-1);result=[]
        for _ in range(limit):
            word=self.tokens_[int(rng.choice(len(self.tokens_),p=self.distribution(context)))]
            if word==self.EOS:break
            result.append(word)
            if self.order>1:context=(context+[word])[-(self.order-1):]
        return result
