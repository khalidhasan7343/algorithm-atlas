import importlib.util, sys, itertools, math
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
ROOT=Path('.'); B='machine-learning/natural-language-processing/'
spec=importlib.util.spec_from_file_location('atlas_b13_support',ROOT/B/'support.py'); s=importlib.util.module_from_spec(spec); sys.modules[spec.name]=s; spec.loader.exec_module(s)
checks=[]
def check(name,cond,detail=''):
    checks.append((name,bool(cond),detail)); print(('PASS ' if cond else 'FAIL ')+name, detail)
rng=np.random.default_rng(1313); h=1e-6
docs=['the cat sat on the mat','the dog sat','cats and dogs play']
bow=s.load('bag-of-words').BagOfWords().fit(docs); M=bow.transform(docs)
check('BoW hand counts ("the" twice in doc0)',M[0,bow.vocabulary_['the']]==2 and M[1,bow.vocabulary_['sat']]==1 and M[2,bow.vocabulary_['the']]==0 and M.sum()==13)
tf=s.load('tf-idf').TFIDF().fit(docs); W=tf.transform(docs)
sk=TfidfVectorizer(token_pattern=r'\w+').fit(docs); W2=sk.transform(docs).toarray()
order=[sk.vocabulary_[w] for w in tf.feature_names_]
check('TF-IDF == sklearn TfidfVectorizer (smooth idf, l2)',np.allclose(W,W2[:,order],atol=1e-12))
check('TF-IDF idf hand: log((1+N)/(1+df))+1',abs(tf.idf_[tf.vocabulary_['the']]-(math.log(4/3)+1))<1e-12)
# N-gram add-k hand
ng=s.load('n-gram-language-models').NGramLanguageModel(order=2,k=1.).fit(docs)
V=len(ng.tokens_); c_the_cat=1; c_the=ng.context_counts_[('the',)]
check('bigram P(cat|the) == (1+1)/(C(the)+V)',abs(ng.probability('cat',('the',))-(c_the_cat+1)/(c_the+V))<1e-12 and abs(ng.distribution(('the',)).sum()-1)<1e-12)
lp=ng.log_probability('the cat'); hand=math.log(ng.probability('the',(ng.BOS,)))+math.log(ng.probability('cat',('the',)))+math.log(ng.probability(ng.EOS,('cat',)))
check('bigram sentence log-probability includes BOS context and EOS',abs(lp-hand)<1e-12)
# word2vec SGNS FD
w2=s.load('word2vec'); p={'W_in':rng.normal(size=(6,3)),'W_out':rng.normal(size=(6,3))}; pairs=np.array([[0,1],[1,2],[3,4],[0,5]]); neg=np.array([[2,3],[0,0],[5,1],[4,4]])
L,G=w2.sgns_loss_gradients(p,pairs,neg); ok=True
for k in p:
    for idx in np.ndindex(p[k].shape):
        q={kk:v.copy() for kk,v in p.items()}; q[k][idx]+=h; fp=w2.sgns_loss_gradients(q,pairs,neg)[0]; q[k][idx]-=2*h; fm=w2.sgns_loss_gradients(q,pairs,neg)[0]; ok&=abs((fp-fm)/(2*h)-G[k][idx])<1e-6
check('Word2Vec SGNS gradient finite difference',ok)
cp=w2.context_pairs([np.array([0,1,2])],1); check('Word2Vec context pairs window 1',sorted(map(tuple,cp.tolist()))==[(0,1),(1,0),(1,2),(2,1)])
# GloVe cooccurrence hand & FD
gl=s.load('glove'); Xc=gl.cooccurrence_matrix([np.array([0,1,2])],3,window=2); 
check('GloVe cooccurrence inverse-distance weights',Xc[0,1]==1 and Xc[0,2]==0.5 and Xc[1,0]==1 and np.allclose(Xc,Xc.T))
pg={'W':rng.normal(size=(3,2)),'C':rng.normal(size=(3,2)),'b':rng.normal(size=3),'c':rng.normal(size=3)}; L,G=gl.glove_loss_gradients(pg,Xc)
i,j=np.nonzero(Xc); hand=sum(min((Xc[a,b]/10)**0.75,1)*(pg['W'][a]@pg['C'][b]+pg['b'][a]+pg['c'][b]-math.log(Xc[a,b]))**2 for a,b in zip(i,j))
check('GloVe loss hand formula',abs(L-hand)<1e-12)
ok=True
for k in pg:
    for idx in np.ndindex(pg[k].shape):
        q={kk:v.copy() for kk,v in pg.items()}; q[k][idx]+=h; fp=gl.glove_loss_gradients(q,Xc)[0]; q[k][idx]-=2*h; fm=gl.glove_loss_gradients(q,Xc)[0]; ok&=abs((fp-fm)/(2*h)-G[k][idx])<1e-6
check('GloVe gradient finite difference (all four groups)',ok)
# BERT bidirectional vs GPT causal
bert=s.load('bert').BERT(12,d_model=4,heads=2,layers=1,random_state=0); gpt=s.load('gpt').GPT(12,d_model=4,heads=2,layers=1,random_state=0)
ids=np.array([[2,5,6,7,8,3]]); ids2=ids.copy(); ids2[0,4]=9
check('BERT bidirectional: changing token 4 changes representation of token 1',not np.allclose(bert.encode(ids)[0,1],bert.encode(ids2)[0,1]))
check('GPT causal: changing token 4 leaves logits at positions 0..3 unchanged',np.allclose(gpt.logits(ids)[0,:4],gpt.logits(ids2)[0,:4]) and not np.allclose(gpt.logits(ids)[0,4],gpt.logits(ids2)[0,4]))
_,att=gpt.encode(ids,return_attention=True); check('GPT attention weights lower-triangular & rows sum 1',np.allclose(np.triu(att[0][0,0],1),0) and np.allclose(att[0][0,0].sum(1),1))
# head gradient FD (BERT), targets shifted (GPT)
mask=np.array([[False,True,False,True,False,False]]); L,G=bert.loss_gradients(ids,mask); W0=bert.head_weight_.copy(); ok=True
for idx in list(np.ndindex(W0.shape))[:20]:
    bert.head_weight_=W0.copy(); bert.head_weight_[idx]+=h; fp=bert.loss_gradients(ids,mask)[0]; bert.head_weight_[idx]-=2*h; fm=bert.loss_gradients(ids,mask)[0]; ok&=abs((fp-fm)/(2*h)-G['head_weight'][idx])<1e-6
bert.head_weight_=W0; check('BERT head gradient finite difference',ok)
inp,tgt,sel=gpt._next_token(ids); check('GPT next-token targets are inputs shifted by one',np.array_equal(inp[0],ids[0,:-1]) and np.array_equal(tgt[0],ids[0,1:]))
# HMM POS: supervised counts hand and Viterbi vs brute force
pos=s.load('hidden-markov-models-pos-tagging').HMMPOSTagger(alpha=0.1).fit([['the','dog','runs'],['a','cat','runs'],['the','cat','sleeps']],[['D','N','V'],['D','N','V'],['D','N','V']])
check('HMM POS transition counts D->N 3, N->V 3',pos.transition_counts_[pos.tag_index_['D'],pos.tag_index_['N']]==3 and pos.transition_counts_[pos.tag_index_['N'],pos.tag_index_['V']]==3)
words=['a','dog','sleeps']; obs=pos.vocabulary_.encode_tokens(words); m=pos.model_
paths=list(itertools.product(range(3),repeat=3)); lp=[math.log(m.initial_[q[0]])+math.log(m.emission_[q[0],obs[0]])+sum(math.log(m.transition_[q[t-1],q[t]])+math.log(m.emission_[q[t],obs[t]]) for t in range(1,3)) for q in paths]
check('HMM POS Viterbi == brute-force best path',[pos.tags_[i] for i in paths[int(np.argmax(lp))]]==pos.tag(words)==['D','N','V'])
# CRF: brute force partition, gradient FD, Viterbi
crf=s.load('conditional-random-fields').LinearChainCRF(['A','B','C'],4,l2=0.)
p={k:rng.normal(size=v.shape)*0.5 for k,v in crf.parameters_.items()}; crf.parameters_=p; x=rng.normal(size=(5,4))
score=lambda y: p['start'][y[0]]+p['end'][y[-1]]+sum((x@p['emission'])[t,y[t]] for t in range(5))+sum(p['transition'][y[t-1],y[t]] for t in range(1,5))
allp=list(itertools.product(range(3),repeat=5)); Z=math.log(sum(math.exp(score(y)) for y in allp))
check('CRF log partition == brute force over 3^5 paths',abs(crf.log_partition(x)-Z)<1e-10)
y=['A','B','B','C','A']; yi=[0,1,1,2,0]; check('CRF log P(y|x) == score - logZ (brute)',abs(crf.log_probability(x,y)-(score(yi)-Z))<1e-10)
best=max(allp,key=score); path,sc=crf.decode(x); check('CRF Viterbi == brute-force argmax',tuple(path)==best and abs(sc-score(best))<1e-10)
L,G=crf.loss_gradients(x,y); ok=True
for k in p:
    for idx in np.ndindex(p[k].shape):
        q={kk:v.copy() for kk,v in p.items()}; q[k][idx]+=h; crf.parameters_=q; fp=crf.loss_gradients(x,y)[0]; q[k][idx]-=2*h; fm=crf.loss_gradients(x,y)[0]; ok&=abs((fp-fm)/(2*h)-G[k][idx])<1e-6
crf.parameters_=p; check('CRF NLL gradient finite difference (emission, transition, start, end)',ok)
info=crf.infer(x); check('CRF token marginals == brute-force posterior',np.allclose(info['token_marginals'][2],[sum(math.exp(score(q)-Z) for q in allp if q[2]==k) for k in range(3)],atol=1e-10))
# NER spans
ner=s.load('named-entity-recognition'); check('NER BIO span extraction hand',ner.extract_spans(['B-PER','I-PER','O','B-LOC','B-LOC','I-LOC'])==[('PER',0,2),('LOC',3,4),('LOC',4,6)])
try: ner.extract_spans(['O','I-PER']); bad=False
except ValueError: bad=True
check('NER rejects I- without B-',bad)
# CYK vs brute-force derivation enumeration (bounded depth)
cyk=s.load('cyk-parsing'); G=[('S',('NP','VP')),('NP',('Det','N')),('VP',('V','NP')),('VP',('sleeps',)),('Det',('the',)),('N',('dog',)),('N',('cat',)),('V',('sees',))]
parser=cyk.CYKParser('S',G)
def language(maxlen):
    # BFS derivations from S producing terminal strings up to maxlen
    out=set(); frontier=[('S',)]; seen=set()
    nts={l for l,_ in G}
    while frontier:
        sf=frontier.pop()
        if sf in seen or len(sf)>maxlen: continue
        seen.add(sf)
        if all(x not in nts for x in sf): out.add(sf); continue
        i=next(k for k,x in enumerate(sf) if x in nts)
        for l,r in G:
            if l==sf[i]: frontier.append(sf[:i]+r+sf[i+1:])
    return out
lang=language(5); cand=set(itertools.chain.from_iterable(itertools.product(['the','dog','cat','sees','sleeps'],repeat=n) for n in range(1,6)))
check('CYK recognize == brute-force derivation language (all strings up to length 5)',all(parser.recognize(list(c))==(c in lang) for c in cand) and len(lang)>0,f'{len(lang)} sentences')
tree=parser.parse(['the','dog','sees','the','cat']); check('CYK parse tree yields the sentence',tree is not None and [w for w in str(tree.to_tuple()).replace('(','').replace(')','').replace("'",'').replace(',','').split() if w in ('the','dog','sees','cat')]==['the','dog','sees','the','cat'])
print('\nSUMMARY',sum(c[1] for c in checks),'/',len(checks),'passed')
