"""Deterministic worked example; run from any working directory."""
import json
from solution import TSNE

if __name__ == '__main__':
    payload = {'X': [[0], [1], [3], [7]], 'parameters': {'n_components': 2, 'perplexity': 2, 'max_iter': 30, 'random_state': 0}}
    model = TSNE(**payload['parameters'])
    result = model.fit_transform(payload['X'], payload.get('y'))
    output = dict(embedding=result.tolist())
    if hasattr(model, 'optimization_status_'):
        output['optimization_status'] = model.optimization_status_
    print(json.dumps(output, allow_nan=False))
