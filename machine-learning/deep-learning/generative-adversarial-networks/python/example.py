"""Small fixed-seed educational example; run from any working directory."""
import json
from solution import GAN

if __name__=='__main__':
    payload={'X': [[-1], [-0.8], [0.8], [1]], 'parameters': {'latent_dim': 1, 'hidden_dim': 4, 'epochs': 30, 'learning_rate': 0.05, 'batch_size': 4}}
    model=GAN(**payload['parameters'])
    model.fit(payload['X'])
    output=dict(loss_initial=float(model.loss_history_[0]),loss_final=float(model.loss_history_[-1]),optimization_status=model.optimization_status_)
    output['sample']=model.sample(payload.get('n_samples',3),random_state=0).tolist()
    print(json.dumps(output,allow_nan=False))
