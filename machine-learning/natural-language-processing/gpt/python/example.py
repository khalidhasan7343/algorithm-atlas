import importlib.util
from pathlib import Path
import sys,json
import numpy as np
spec=importlib.util.spec_from_file_location('atlas_b13_support',Path(__file__).resolve().parents[2]/'support.py')
s=sys.modules.get(spec.name)
if s is None:
    s=importlib.util.module_from_spec(spec);sys.modules[spec.name]=s;spec.loader.exec_module(s)
m=s.load('gpt')

texts=['red blue red blue','red blue red blue']
vocab=s.Vocabulary().fit(texts)
ids=np.array([[m.BOS,*np.where((a:=vocab.encode(text))==0,m.UNK,a+4).tolist(),m.EOS] for text in texts])
model=m.GPT(len(vocab)+4,d_model=8,heads=2,ff_dim=12,layers=1,random_state=13)
model.fit(ids,epochs=160,learning_rate=.1)
prefix=[m.BOS,int(ids[0,1])]
generated=model.generate(prefix,max_new_tokens=6,temperature=.4,random_state=17)
special={m.UNK:'<UNK>',m.BOS:'<BOS>',m.EOS:'<EOS>',m.MASK:'<MASK>',m.PAD:'<PAD>'}
print(json.dumps(dict(training=texts,ordinary_ids={w:i+4 for w,i in vocab.index_.items() if i},training_ids=ids.tolist(),scored_next_tokens=int(np.sum(ids[:,1:]!=m.PAD)),loss_start=float(model.loss_history_[0]),loss_final=float(model.loss_history_[-1]),prefix=prefix,generated_ids=generated.tolist(),generated_tokens=[vocab.tokens_[i-4] if i>=5 else special[i] for i in generated],trained_parameters=list(model.trainable_parameters_),backbone='frozen random initialization')))
