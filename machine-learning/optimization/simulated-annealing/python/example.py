"""Executed binary search with a known Hamming target; no derivative is used."""
import json
import numpy as np
from solution import SimulatedAnnealing


def main():
    target=np.array([1,0,1,1,0,0,1,0,1,0,1,0])
    def fun(x):return int(np.count_nonzero(x!=target))
    result=SimulatedAnnealing(initial_temperature=1,cooling=.95,random_state=22).minimize(fun,np.zeros(len(target),dtype=int),max_iter=1000,target_value=0)
    print(json.dumps(dict(seed=22,known_target_value=0,initial_best=float(result.history[0]),
        x=result.x.tolist(),objective=result.fun,iterations=result.n_iter,objective_evaluations=result.nfev,
        status=result.status,converged=result.converged),sort_keys=True))


if __name__=='__main__':main()
