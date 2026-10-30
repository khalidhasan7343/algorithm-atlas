"""Deterministic worked example; run from any working directory."""
import json
from solution import SVD

if __name__ == '__main__':
    payload = {'X': [[3, 0, 0], [0, 1, 0], [0, 0, 2]], 'parameters': {'n_components': 2}}
    model = SVD(**payload['parameters'])
    result = model.fit_transform(payload['X'], payload.get('y'))
    output = dict(embedding=result.tolist())
    if hasattr(model, 'optimization_status_'):
        output['optimization_status'] = model.optimization_status_
    print(json.dumps(output, allow_nan=False))
