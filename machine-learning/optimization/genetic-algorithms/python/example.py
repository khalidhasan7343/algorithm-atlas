"""Executed binary search with a known Hamming target; no derivative is used."""
import json
import numpy as np
from solution import GeneticAlgorithm


def main():
    target=np.array([1,0,1,1,0,0,1,0,1,0,1,0])
    def fun(x):return int(np.count_nonzero(x!=target))
    result=GeneticAlgorithm(population_size=12,mutation_rate=.1,random_state=22).minimize(fun,len(target),max_generations=200,target_value=0)
    print(json.dumps(dict(seed=22,known_target_value=0,initial_best=float(result.history[0]),
        x=result.x.tolist(),objective=result.fun,iterations=result.n_iter,objective_evaluations=result.nfev,
        status=result.status,converged=result.converged),sort_keys=True))


if __name__=='__main__':main()
