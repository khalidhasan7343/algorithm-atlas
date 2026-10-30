"""Deterministic worked example; run from any working directory."""
import json
from solution import PCA

if __name__ == '__main__':
    payload = {'X': [[8, 20], [10, 21], [12, 20], [10, 19]], 'parameters': {'n_components': 1}}
    model = PCA(**payload['parameters'])
    result = model.fit_transform(payload['X'], payload.get('y'))
    output = dict(embedding=result.tolist())
    if hasattr(model, 'optimization_status_'):
        output['optimization_status'] = model.optimization_status_
    print(json.dumps(output, allow_nan=False))
