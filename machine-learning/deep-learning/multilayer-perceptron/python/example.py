"""Small fixed-seed educational example; run from any working directory."""
import json
from solution import MLPClassifier

if __name__=='__main__':
    payload={'X': [[-1, -1], [-1, 1], [1, -1], [1, 1]], 'y': [0, 1, 1, 0], 'parameters': {'hidden_dim': 8, 'epochs': 600, 'learning_rate': 0.5, 'batch_size': 4, 'random_state': 19002}}
    model=MLPClassifier(**payload['parameters'])
    model.fit(payload['X'],payload['y'])
    output=dict(loss_initial=float(model.loss_history_[0]),loss_final=float(model.loss_history_[-1]),optimization_status=model.optimization_status_)
    output['prediction']=model.predict(payload['X']).tolist()
    print(json.dumps(output,allow_nan=False))
