"""Small fixed-seed educational example; run from any working directory."""
import json
from solution import CNNRegressor

if __name__=='__main__':
    payload={'X': [[[[-1, -0.5], [0, 0.5]]], [[[-0.5, 0], [0.5, 1]]], [[[0, 0.5], [1, 0.5]]], [[[0.5, 1], [0.5, 0]]]], 'y': [[-0.25], [0.25], [0.5], [0.5]], 'parameters': {'filters': 2, 'epochs': 50, 'batch_size': 4}}
    model=CNNRegressor(**payload['parameters'])
    model.fit(payload['X'],payload['y'])
    output=dict(loss_initial=float(model.loss_history_[0]),loss_final=float(model.loss_history_[-1]),optimization_status=model.optimization_status_)
    output['prediction']=model.predict(payload['X']).tolist()
    print(json.dumps(output,allow_nan=False))
