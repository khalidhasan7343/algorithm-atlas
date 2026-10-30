"""Fixed small numerical example; no work runs during import."""
import importlib.util
import json
from pathlib import Path
import sys


def main():
    spec = importlib.util.spec_from_file_location('atlas_example_gaussian_mixture_models', Path(__file__).with_name('solution.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    data = {'X': [[-3.1], [-3], [-2.9], [2.9], [3], [3.1]], 'parameters': {'n_components': 2, 'means_init': [[-3], [3]], 'reg_covar': 0.001, 'random_state': 0}}
    model = module.GaussianMixture(**data['parameters']).fit(data['X'])
    print(json.dumps(dict(labels=model.labels_.tolist()), allow_nan=False))


if __name__ == '__main__':
    main()
