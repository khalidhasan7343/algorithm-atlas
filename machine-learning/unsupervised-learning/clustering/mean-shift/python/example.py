"""Fixed small numerical example; no work runs during import."""
import importlib.util
import json
from pathlib import Path
import sys


def main():
    spec = importlib.util.spec_from_file_location('atlas_example_mean_shift', Path(__file__).with_name('solution.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    data = {'X': [[0], [0.1], [5], [5.1]], 'parameters': {'bandwidth': 0.3, 'tol': 1e-08}}
    model = module.MeanShift(**data['parameters']).fit(data['X'])
    print(json.dumps(dict(labels=model.labels_.tolist()), allow_nan=False))


if __name__ == '__main__':
    main()
