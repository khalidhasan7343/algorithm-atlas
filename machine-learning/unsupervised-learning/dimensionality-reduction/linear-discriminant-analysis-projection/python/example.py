"""Deterministic worked example; run from any working directory."""
import json
from solution import LDAProjection

if __name__ == '__main__':
    payload = {'X': [[-2, -1], [-2, 1], [2, -1], [2, 1]], 'parameters': {'n_components': 1, 'reg': 0.1}, 'y': [0, 0, 1, 1]}
    model = LDAProjection(**payload['parameters'])
    result = model.fit_transform(payload['X'], payload.get('y'))
    output = dict(embedding=result.tolist())
    if hasattr(model, 'optimization_status_'):
        output['optimization_status'] = model.optimization_status_
    print(json.dumps(output, allow_nan=False))
