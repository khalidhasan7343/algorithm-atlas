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
m=s.load('arima')

def main():
    rng=np.random.default_rng(2310);increments=.25+rng.normal(0,.08,60);y=np.cumsum(increments)
    model=m.ARIMA((1,1,1),max_iter=200).fit(y)
    print(json.dumps(dict(order=[1,1,1],status=model.status_,converged=model.converged_,iterations=model.n_iter_,intercept=round(model.params_['intercept'],8),ar=np.round(model.params_['ar'],8).tolist(),ma=np.round(model.params_['ma'],8).tolist(),forecast=np.round(model.forecast(4),8).tolist(),index=model.forecast_index(4).tolist())))

if __name__=='__main__':main()
