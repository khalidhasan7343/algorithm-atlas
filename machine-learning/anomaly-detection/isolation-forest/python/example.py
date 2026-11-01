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
m=s.load('isolation-forest')

def main():
    X=np.array([[-.2,0.],[.1,.1],[0.,-.1],[.2,0.],[-.1,.2],[.1,-.2],[4.,4.],[5.,4.]])
    model=m.IsolationForest(16,max_samples=8,contamination=.25,random_state=24).fit(X)
    roots=[dict(feature=t.feature,split=round(t.split,6),count=t.count,left=t.left.count,right=t.right.count) for t in model.trees_[:3]]
    print(json.dumps(dict(training=X.tolist(),roots=roots,scores=np.round(model.anomaly_scores_,8).tolist(),threshold=round(model.threshold_,8),decisions=np.round(model.decision_function(X),8).tolist(),labels=model.predict(X).tolist(),status=model.status_)))

if __name__=='__main__':main()
