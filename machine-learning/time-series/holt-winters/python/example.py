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
m=s.load('holt-winters')

def main():
    t=np.arange(20);y=10+.25*t+np.array([-1.,1.])[t%2]
    model=m.HoltWinters(2).fit(y)
    print(json.dumps(dict(level=round(model.level_,8),trend=round(model.trend_,8),seasonal=np.round(model.seasonal_,8).tolist(),forecast=np.round(model.forecast(4),8).tolist(),index=model.forecast_index(4).tolist(),status=model.status_)))

if __name__=='__main__':main()
