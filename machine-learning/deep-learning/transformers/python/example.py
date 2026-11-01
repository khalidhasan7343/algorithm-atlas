"""Small fixed-seed educational example; run from any working directory."""
import json
from solution import TransformerRegressor

if __name__=='__main__':
    payload={'X': [[[-0.4], [-0.2]], [[-0.2], [0.1]], [[0.1], [0.3]], [[0.4], [0.2]]], 'y': [[-0.2], [0.1], [0.3], [0.2]], 'parameters': {'d_model': 4, 'heads': 2, 'hidden_dim': 4, 'epochs': 50, 'learning_rate': 0.03, 'batch_size': 4}}
    model=TransformerRegressor(**payload['parameters'])
    model.fit(payload['X'],payload['y'])
    output=dict(loss_initial=float(model.loss_history_[0]),loss_final=float(model.loss_history_[-1]),optimization_status=model.optimization_status_)
    output['prediction']=model.predict(payload['X']).tolist()
    print(json.dumps(output,allow_nan=False))
