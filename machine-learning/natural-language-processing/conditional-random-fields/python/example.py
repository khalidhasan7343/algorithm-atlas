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
x = np.eye(2)
y = ['A', 'B']
m = s.load('conditional-random-fields').LinearChainCRF(['A', 'B'], 2, max_iter=80)
initial = m.log_partition(x)
m.fit([x], [y])
print(json.dumps(dict(features=x.tolist(), gold=y, initial_log_partition=round(initial, 6), initial_loss=round(float(m.loss_history_[0]), 6), final_regularized_loss=round(float(m.loss_history_[-1]), 6), status=m.status_, updates=m.n_iter_, predicted=m.predict(x), conditional_probability=round(float(np.exp(m.log_probability(x,y))), 6), token_marginals=m.infer(x)['token_marginals'].round(6).tolist(), trainable_groups=list(m.parameters_))))
