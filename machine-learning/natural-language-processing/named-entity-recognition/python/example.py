import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec = importlib.util.spec_from_file_location('atlas_b13_support', Path(__file__).resolve().parents[2] / 'support.py')
s = sys.modules.get(_spec.name)
if s is None:
    s = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = s
    _spec.loader.exec_module(s)

import json
sentences = [['John','visits','Paris'],['Mary','visits','Rome'],['New','York','shines']]
labels = [['B-PER','O','B-LOC'],['B-PER','O','B-LOC'],['B-LOC','I-LOC','O']]
m = s.load('named-entity-recognition').NERTagger(max_iter=80).fit(sentences, labels)
print(json.dumps(dict(training=sentences, gold=labels, baseline='BIO feature CRF', features=len(m.feature_names_), initial_loss=round(float(m.model_.loss_history_[0]),6), final_loss=round(float(m.model_.loss_history_[-1]),6), query=m.predict_text('John visits Paris'), unknown_query=m.predict_text('Alice visits Rome'), training_metrics=m.evaluate(sentences,labels))))
