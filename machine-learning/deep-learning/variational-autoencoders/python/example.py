"""Small fixed-seed educational example; run from any working directory."""
import json
from solution import VariationalAutoencoder

if __name__=='__main__':
    payload={'X': [[-1, -0.5], [-0.3, -0.15], [0.3, 0.15], [1, 0.5]], 'parameters': {'latent_dim': 1, 'epochs': 40, 'learning_rate': 0.03, 'batch_size': 4}}
    model=VariationalAutoencoder(**payload['parameters'])
    model.fit(payload['X'])
    output=dict(loss_initial=float(model.loss_history_[0]),loss_final=float(model.loss_history_[-1]),optimization_status=model.optimization_status_)
    output.update(embedding=model.transform(payload['X']).tolist(),reconstruction=model.reconstruct(payload['X']).tolist())
    output['sample']=model.sample(payload.get('n_samples',3),random_state=0).tolist()
    print(json.dumps(output,allow_nan=False))
