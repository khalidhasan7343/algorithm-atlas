"""Small fixed educational example; runs only when explicitly invoked."""
import importlib.util
import json
from pathlib import Path
import sys


def main():
    spec = importlib.util.spec_from_file_location('atlas_example_voting_classifiers', Path(__file__).with_name('solution.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    payload = {'X': [[0], [1], [2], [3]], 'y': ['cold', 'cold', 'warm', 'warm'], 'predict': [[0], [3]], 'parameters': {'voting': 'soft', 'random_state': 0}}
    model = module.VotingClassifier(**payload['parameters']).fit(payload['X'], payload['y'])
    print(json.dumps(dict(predictions=model.predict(payload['predict']).tolist()), allow_nan=False))


if __name__ == '__main__':
    main()
