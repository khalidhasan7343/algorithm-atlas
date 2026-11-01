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
m=s.load('one-class-svm')

def main():
    X=np.array([[-1.],[-.7],[-.3],[0.],[.2],[.6],[1.]])
    model=m.OneClassSVM(.3,gamma=.8,tolerance=1e-8).fit(X)
    query=np.array([[0.],[.5],[4.]])
    print(json.dumps(dict(training=X.tolist(),kernel='rbf',nu=.3,gamma=model.gamma_,status=model.status_,converged=model.converged_,iterations=model.n_iter_,support=model.support_.tolist(),alpha=np.round(model.alpha_,8).tolist(),rho=round(model.rho_,8),objective=round(model.objective_,8),kkt_residual=round(model.kkt_residual_,12),feasibility=round(model.feasibility_residual_,12),query=query.tolist(),decisions=np.round(model.decision_function(query),8).tolist(),labels=model.predict(query).tolist())))

if __name__=='__main__':main()
