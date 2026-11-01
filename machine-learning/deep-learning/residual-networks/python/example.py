"""Small fixed-seed educational example; run from any working directory."""
import json
from solution import ResidualRegressor

if __name__=='__main__':
    payload={'X': [[-1, -0.5], [-0.2, -0.1], [0.3, 0.1], [1, 0.5]], 'y': [[-1.5], [-0.3], [0.4], [1.5]], 'parameters': {'hidden_dim': 3, 'epochs': 80, 'batch_size': 4}}
    model=ResidualRegressor(**payload['parameters'])
    model.fit(payload['X'],payload['y'])
    output=dict(loss_initial=float(model.loss_history_[0]),loss_final=float(model.loss_history_[-1]),optimization_status=model.optimization_status_)
    output['prediction']=model.predict(payload['X']).tolist()
    print(json.dumps(output,allow_nan=False))
