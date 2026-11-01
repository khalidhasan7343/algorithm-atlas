"""Binary one-bit Metropolis search with geometric cooling and best-state retention."""
import importlib.util
import math
from pathlib import Path
import sys

import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b10_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)


def metropolis_probability(delta,temperature):
    delta=support.real(delta,'delta',-2e100,2e100)
    temperature=support.real(temperature,'temperature',1e-12,1e6)
    return 1. if delta<=0 else math.exp(-delta/temperature)


class SimulatedAnnealing:
    def __init__(self,initial_temperature=1.,cooling=.95,minimum_temperature=1e-12,random_state=0):
        self.initial_temperature,self.cooling=initial_temperature,cooling
        self.minimum_temperature,self.random_state=minimum_temperature,random_state
        self._settings()

    def _settings(self):
        support.real(self.initial_temperature,'initial_temperature',1e-8,1e6)
        support.real(self.cooling,'cooling',1e-3,1.)
        support.real(self.minimum_temperature,'minimum_temperature',1e-12,self.initial_temperature)
        support.integer(self.random_state,'random_state',0,2**32-1)

    @support.numerical
    def minimize(self,fun,x0,*,max_iter=1000,target_value=None):
        self._settings();support.integer(max_iter,'max_iter',1,10000)
        if target_value is not None:target_value=support.real(target_value,'target_value',-1e100,1e100)
        current=support.bits(x0);value=support.objective(fun,current)
        best=current.copy();best_value=value;rng=np.random.default_rng(self.random_state)
        history=[best_value];current_values=[value];trajectory=[current.copy()];accepted=[];temperatures=[]
        status='iteration-budget';converged=bool(target_value is not None and best_value<=target_value)
        log_floor=math.log(self.minimum_temperature)
        while len(accepted)<max_iter and not converged:
            log_temperature=math.log(self.initial_temperature)+len(accepted)*math.log(self.cooling)
            if log_temperature<=log_floor:
                status='temperature-floor';break
            temperature=math.exp(log_temperature)
            proposal=current.copy();index=int(rng.integers(len(current)));proposal[index]^=1
            candidate_value=support.objective(fun,proposal);delta=candidate_value-value
            accept=delta<=0
            if not accept:
                u=float(rng.random())
                accept=bool(u==0 or math.log(u)<-delta/temperature)
            if accept:
                current,value=proposal,candidate_value
                if value<best_value:best,best_value=current.copy(),value
            accepted.append(bool(accept));temperatures.append(temperature)
            history.append(best_value);current_values.append(value);trajectory.append(current.copy())
            converged=bool(target_value is not None and best_value<=target_value)
        if converged:status='target-reached'
        return support.OptimizationResult(best.copy(),best_value,len(accepted),len(accepted)+1,status,converged,np.array(history),
            dict(current_x=current.copy(),current_fun=value,current_history=np.array(current_values),trajectory=np.array(trajectory),
                 accepted=np.array(accepted,dtype=bool),temperatures=np.array(temperatures),target_value=target_value))
