"""Deterministic worked example; run from any working directory."""
import json
from solution import Autoencoder

if __name__ == '__main__':
    payload = {'X': [[-1, -0.5], [0, 0], [1, 0.5]], 'parameters': {'latent_dim': 1, 'max_iter': 30, 'random_state': 0}}
    model = Autoencoder(**payload['parameters'])
    result = model.fit_transform(payload['X'], payload.get('y'))
    output = dict(embedding=result.tolist())
    if hasattr(model, 'optimization_status_'):
        output['optimization_status'] = model.optimization_status_
    print(json.dumps(output, allow_nan=False))
