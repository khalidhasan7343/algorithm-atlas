"""Small executed least-squares example; the optimizer performs every update."""
import json
import numpy as np
from solution import MiniBatchGradientDescent


def main():
    X=np.array([[1.,0],[0,1],[1,1],[1,-1],[2,1],[-1,2]])
    y=X@np.array([1.,-2.])
    def fun(x):return float(np.mean((X@x-y)**2)/2)
    def gradient(x,indices):return X[indices].T@(X[indices]@x-y[indices])/len(indices)
    model=MiniBatchGradientDescent(learning_rate=.1,random_state=22,batch_size=2)
    result=model.minimize(fun,gradient,[3.,1.],n_samples=len(X),max_epochs=100)
    print(json.dumps(dict(initial=[3.,1.],learning_rate=.1,x=result.x.round(8).tolist(),
        analytical=[1.,-2.],objective=round(result.fun,12),iterations=result.n_iter,
        updates=result.diagnostics['n_updates'],objective_evaluations=result.nfev,
        gradient_evaluations=result.diagnostics['njev'],status=result.status,converged=result.converged),sort_keys=True))


if __name__=='__main__':main()
