"""Executed tiny-objective observations; no universal convergence/speed ranking."""
import importlib.util
import json
from pathlib import Path
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('atlas_b10_support',ROOT/'machine-learning/optimization/support.py')
support=sys.modules.get(spec.name)
if support is None:
    support=importlib.util.module_from_spec(spec);sys.modules[spec.name]=support;spec.loader.exec_module(support)


def main():
    X=np.array([[1.,0],[0,1],[1,1],[1,-1],[2,1],[-1,2]])
    y=X@np.array([1.,-2.])+np.array([.1,-.2,.2,0,.1,-.1])
    def f(x):return float(np.mean((X@x-y)**2)/2)
    def g(x):return X.T@(X@x-y)/len(X)
    def sample_g(x,i):return X[i].T@(X[i]@x-y[i])/len(i)
    optimum=np.linalg.lstsq(X,y,rcond=None)[0];minimum=f(optimum);rows=[]
    models=[('batch-gradient-descent',support.load('batch-gradient-descent').BatchGradientDescent(.1)),
            ('momentum',support.load('momentum').Momentum(.1,.8)),
            ('rmsprop',support.load('rmsprop').RMSProp(.01)),
            ('adam',support.load('adam').Adam(.05)),
            ('adamw',support.load('adamw').AdamW(.05,weight_decay=.02,decay_mask=[True,False])),
            ('l-bfgs',support.load('l-bfgs').LBFGS())]
    for topic,model in models:
        start=time.perf_counter();r=model.minimize(f,g,[3.,1.],max_iter=200 if topic=='l-bfgs' else 1000)
        rows.append(dict(topic=topic,x=r.x.tolist(),objective=r.fun,gap_to_task_optimum=r.fun-minimum,
                         iterations=r.n_iter,nfev=r.nfev,status=r.status,converged=r.converged,
                         gradient_norm=r.diagnostics['gradient_norm'],elapsed_seconds=time.perf_counter()-start))
    stochastic=[]
    for seed in (21,22,23):
        for topic,model in [('stochastic-gradient-descent',support.load('stochastic-gradient-descent').StochasticGradientDescent(.05,seed)),
                            ('mini-batch-gradient-descent',support.load('mini-batch-gradient-descent').MiniBatchGradientDescent(.1,2,seed))]:
            r=model.minimize(f,sample_g,[3.,1.],n_samples=len(X),max_epochs=50)
            stochastic.append(dict(topic=topic,seed=seed,objective=r.fun,gap_to_task_optimum=r.fun-minimum,
                                   gradient_norm=r.diagnostics['gradient_norm'],status=r.status,converged=r.converged,
                                   epochs=r.n_iter,updates=r.diagnostics['n_updates']))
        target=np.array([1,0,1,1,0,0,1,0,1,0,1,0]);fitness=lambda x:int(np.count_nonzero(x!=target))
        for topic,model in [('genetic-algorithms',support.load('genetic-algorithms').GeneticAlgorithm(population_size=12,mutation_rate=.1,random_state=seed)),
                            ('simulated-annealing',support.load('simulated-annealing').SimulatedAnnealing(random_state=seed))]:
            r=model.minimize(fitness,12,max_generations=80,target_value=0) if topic=='genetic-algorithms' else model.minimize(fitness,np.zeros(12,dtype=int),max_iter=300,target_value=0)
            stochastic.append(dict(topic=topic,seed=seed,initial_best=float(r.history[0]),objective=r.fun,
                                   iterations=r.n_iter,nfev=r.nfev,status=r.status,converged=r.converged))
    data=dict(description='One noisy small least-squares objective and one12-bit Hamming target; all declared seeds/outcomes retained.',
              analytic_task_optimum=optimum.tolist(),analytic_task_minimum=minimum,continuous=rows,stochastic=stochastic,
              limits='Observed objective progress is not global convergence. AdamW reports raw task loss,not a coupled L2 objective. Constant-rate sampled methods can exhaust budgets on noisy data. Binary target flags certify only the explicit known threshold. Times are measured teaching runs,not comparative benchmarks.')
    (ROOT/'docs/optimization-evidence/educational-training-results.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data))


if __name__=='__main__':main()
