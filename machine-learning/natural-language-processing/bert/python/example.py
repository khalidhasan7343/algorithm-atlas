import importlib.util
from pathlib import Path
import sys,json
import numpy as np
spec=importlib.util.spec_from_file_location('atlas_b13_support',Path(__file__).resolve().parents[2]/'support.py')
s=sys.modules.get(spec.name)
if s is None:
    s=importlib.util.module_from_spec(spec);sys.modules[spec.name]=s;spec.loader.exec_module(s)
m=s.load('bert')

texts=['cat runs','cat sleeps']
vocab=s.Vocabulary().fit(texts)
ids=np.array([[m.BOS,*np.where((a:=vocab.encode(text))==0,m.UNK,a+4).tolist(),m.EOS] for text in texts])
selected=np.zeros(ids.shape,dtype=bool);selected[:,1]=True
model=m.BERT(len(vocab)+4,d_model=4,heads=2,ff_dim=8,layers=2,random_state=11)
model.fit(ids,selected,epochs=100,learning_rate=.1)
inference=ids.copy();inference[selected]=m.MASK
prediction=model.predict_masked(inference,selected)
print(json.dumps(dict(training=texts,ordinary_ids={w:i+4 for w,i in vocab.index_.items() if i},input_ids=ids.tolist(),inference_ids=inference.tolist(),loss_start=float(model.loss_history_[0]),loss_final=float(model.loss_history_[-1]),predicted_ids=prediction.tolist(),predicted_tokens=[vocab.tokens_[i-4] if i>=5 else '<special>' for i in prediction],context_shape=list(model.encode(inference).shape),trained_parameters=list(model.trainable_parameters_),backbone='frozen random initialization')))
