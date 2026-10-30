"""Deterministic worked example; run from any working directory."""
import json
from solution import FastICA

if __name__ == '__main__':
    payload = {'X': [[-1.5, -1.8], [-0.5, 1.2], [0.5, -1.2], [1.5, 1.8]], 'parameters': {'n_components': 2, 'random_state': 0}}
    model = FastICA(**payload['parameters'])
    result = model.fit_transform(payload['X'], payload.get('y'))
    output = dict(embedding=result.tolist())
    if hasattr(model, 'optimization_status_'):
        output['optimization_status'] = model.optimization_status_
    print(json.dumps(output, allow_nan=False))
