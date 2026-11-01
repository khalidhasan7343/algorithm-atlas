"""Small deterministic local example; no network access."""
import importlib.util
from pathlib import Path
import sys
import json
import numpy as np
spec=importlib.util.spec_from_file_location('atlas_b12_support',Path(__file__).resolve().parents[2]/'support.py')
s=sys.modules.get(spec.name)
if s is None:
    s=importlib.util.module_from_spec(spec);sys.modules[spec.name]=s;spec.loader.exec_module(s)
m=s.load('local-outlier-factor')

def main():
    X=np.array([[-11.],[-10.],[0.],[10.]])
    model=m.LocalOutlierFactor(1,contamination='auto').fit(X)
    print(json.dumps(dict(training=X.tolist(),neighbors=[v.tolist() for v in model.neighborhoods_],k_distance=model.k_distances_.tolist(),mean_reach=model.mean_reachability_.tolist(),density=model.lrd_.tolist(),lof=np.round(model.anomaly_scores(),8).tolist(),threshold=model.threshold_,decisions=np.round(model.decision_function(),8).tolist(),labels=model.predict().tolist(),status=model.status_)))

if __name__=='__main__':main()
