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
m=s.load('sarima')

def main():
    rng=np.random.default_rng(2311);y=rng.normal(0,.1,80)
    for t in range(4,len(y)):y[t]+=.6*y[t-4]
    model=m.SARIMA((0,0,0),(1,0,0,4),include_intercept=False).fit(y)
    print(json.dumps(dict(seasonal_order=[1,0,0,4],status=model.status_,converged=model.converged_,iterations=model.n_iter_,seasonal_ar=np.round(model.params_['seasonal_ar'],8).tolist(),forecast=np.round(model.forecast(6),8).tolist(),index=model.forecast_index(6).tolist())))

if __name__=='__main__':main()
