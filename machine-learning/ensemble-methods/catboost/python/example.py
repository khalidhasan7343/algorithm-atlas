"""Small fixed educational example; runs only when explicitly invoked."""
import importlib.util
import json
from pathlib import Path
import sys


def main():
    spec = importlib.util.spec_from_file_location('atlas_example_catboost', Path(__file__).with_name('solution.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    payload = {'X': [['a', 0], ['a', 1], ['b', 2], ['b', 3]], 'y': [0, 0, 4, 4], 'predict': [['a', 0], ['b', 3]], 'parameters': {'categorical_features': [0], 'n_estimators': 1, 'learning_rate': 1, 'max_depth': 1, 'random_state': 0}}
    model = module.CatBoostRegressor(**payload['parameters']).fit(payload['X'], payload['y'])
    print(json.dumps(dict(predictions=model.predict(payload['predict']).tolist()), allow_nan=False))


if __name__ == '__main__':
    main()
