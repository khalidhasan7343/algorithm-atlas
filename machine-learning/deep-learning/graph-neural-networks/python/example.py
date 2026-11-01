"""Small fixed-seed educational example; run from any working directory."""
import json
from solution import GCNRegressor

if __name__=='__main__':
    payload={'X': [[1, 0], [0, 1], [1, 1], [0.5, 0.2]], 'y': [[1], [1], [2], [0.7]], 'adjacency': [[0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 0]], 'parameters': {'hidden_dim': 3, 'epochs': 100}}
    model=GCNRegressor(**payload['parameters'])
    model.fit(payload['X'],payload['y'],payload['adjacency'])
    output=dict(loss_initial=float(model.loss_history_[0]),loss_final=float(model.loss_history_[-1]),optimization_status=model.optimization_status_)
    output['prediction']=model.predict(payload['X'],payload['adjacency']).tolist()
    print(json.dumps(output,allow_nan=False))
