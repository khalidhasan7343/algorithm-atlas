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
m=s.load('prophet')

def main():
    t=np.arange(56.);y=3+.1*t+.2*np.maximum(t-24,0)+np.sin(2*np.pi*t/7)
    model=m.Prophet(changepoints=(24,),seasonalities=((7,1),),regularization=.01).fit(y)
    parts=model.forecast_components(4)
    print(json.dumps(dict(status=model.status_,converged=model.converged_,design_rank=model.design_rank_,objective=round(model.objective_,8),forecast=np.round(parts['total'],8).tolist(),trend=np.round(parts['trend'],8).tolist(),seasonal=np.round(parts['seasonal'],8).tolist(),index=model.forecast_index(4).tolist())))

if __name__=='__main__':main()
