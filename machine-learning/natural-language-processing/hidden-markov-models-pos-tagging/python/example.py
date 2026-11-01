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
m = s.load('hidden-markov-models-pos-tagging').HMMPOSTagger()
training = [['dogs', 'run'], ['cats', 'sleep'], ['dogs', 'sleep']]
m.fit(training, [['N', 'V']]*3)
query = ['unknown', 'sleep']
print(json.dumps(dict(training=training, tags=m.tags_, vocabulary=m.vocabulary_.tokens_, initial=m.model_.initial_.tolist(), transition=m.model_.transition_.tolist(), query=query, predicted=m.tag(query), best_joint_log_probability=round(m.decode(query)[1], 6), observation_log_likelihood=round(m.score(query), 6), posterior=m.posterior(query).round(6).tolist(), training_accuracy=m.evaluate(training,[['N','V']]*3)['accuracy'])))
