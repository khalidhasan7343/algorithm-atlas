"""Small deterministic local example; no network access."""
import importlib.util
from pathlib import Path
import sys
import json
import numpy as np
spec=importlib.util.spec_from_file_location('atlas_b11_support',Path(__file__).resolve().parents[2]/'support.py')
s=sys.modules.get(spec.name)
if s is None:
    s=importlib.util.module_from_spec(spec);sys.modules[spec.name]=s;spec.loader.exec_module(s)
m=s.load('exponential-smoothing')

def main():
    model=m.ExponentialSmoothing(.5,0).fit([2.,4.,8.])
    print(json.dumps(dict(levels=model.levels_.tolist(),fitted=model.fitted_values_.tolist(),forecast=model.forecast(3).tolist(),index=model.forecast_index(3).tolist(),status=model.status_)))

if __name__=='__main__':main()
