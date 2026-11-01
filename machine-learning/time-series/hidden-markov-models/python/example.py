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
m=s.load('hidden-markov-models')

def main():
    model=m.CategoricalHMM(2,2,initial=[.6,.4],transition=[[.7,.3],[.2,.8]],emission=[[.8,.2],[.3,.7]])
    obs=[0,1,1,0,1];before=model.score(obs);path,path_logp=model.decode(obs);posterior=model.infer(obs)
    model.fit([obs,[1,1,0,0,1]],max_iter=25)
    print(json.dumps(dict(initial_log_likelihood=round(before,8),viterbi=path.tolist(),path_log_probability=round(path_logp,8),posterior=np.round(posterior['gamma'],8).tolist(),training_log_likelihood_before=round(float(model.log_likelihood_history_[0]),8),training_log_likelihood_after=round(float(model.log_likelihood_history_[-1]),8),iterations=model.n_iter_,status=model.status_,converged=model.converged_)))

if __name__=='__main__':main()
