"""Executed anisotropic quadratic example; a budget status is not convergence."""
import json
import numpy as np
from solution import Adam


def main():
    A=np.diag([2.,4.]);b=np.array([2.,-8.])
    def fun(x):return float(.5*x@A@x-b@x)
    def gradient(x):return A@x-b
    model=Adam(learning_rate=.05)
    result=model.minimize(fun,gradient,[3.,1.],max_iter=1000)
    print(json.dumps(dict(initial=[3.,1.],learning_rate=model.learning_rate,x=result.x.round(8).tolist(),
        task_optimum=[1.,-2.],objective=round(result.fun,12),iterations=result.n_iter,
        updates=result.diagnostics['n_updates'],objective_evaluations=result.nfev,
        gradient_norm=round(result.diagnostics['gradient_norm'],10),status=result.status,converged=result.converged),sort_keys=True))


if __name__=='__main__':main()
