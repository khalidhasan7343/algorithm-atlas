"""Executed nonlinear Rosenbrock diagnostic; no external optimizer in core."""
import json
import numpy as np
from solution import LBFGS


def main():
    def fun(x):return float((1-x[0])**2+100*(x[1]-x[0]**2)**2)
    def gradient(x):return np.array([2*(x[0]-1)-400*x[0]*(x[1]-x[0]**2),200*(x[1]-x[0]**2)])
    result=LBFGS(history_size=5).minimize(fun,gradient,[-1.2,1.],max_iter=200)
    print(json.dumps(dict(initial=[-1.2,1.],history_size=5,x=result.x.round(8).tolist(),analytical=[1.,1.],
        objective=round(result.fun,12),iterations=result.n_iter,objective_evaluations=result.nfev,
        gradient_evaluations=result.diagnostics['njev'],gradient_norm=round(result.diagnostics['gradient_norm'],10),
        status=result.status,converged=result.converged),sort_keys=True))


if __name__=='__main__':main()
