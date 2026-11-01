"""stochastic-gradient-descent; see its lesson for objective,stopping and resource contracts."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b10_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)

class StochasticGradientDescent(support.SampledOptimizer):
    """Random-reshuffling SGD; one selected observation per update."""
    def __init__(self,learning_rate=.01,random_state=0):
        self.random_state=random_state
        super().__init__(learning_rate)

    def _candidate(self,x,g,state):
        return x-self.learning_rate*g,state

    def _batches(self,n,rng):
        return tuple(np.array([index],dtype=int) for index in rng.permutation(n))
