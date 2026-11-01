"""mini-batch-gradient-descent; see its lesson for objective,stopping and resource contracts."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b10_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)

class MiniBatchGradientDescent(support.SampledOptimizer):
    """Shuffled disjoint mean-gradient batches,including a smaller final batch."""
    def __init__(self,learning_rate=.05,batch_size=4,random_state=0):
        self.batch_size=batch_size;self.random_state=random_state
        super().__init__(learning_rate)

    def _settings(self):
        super()._settings();support.integer(self.batch_size,'batch_size',1,256)

    def _validate_samples(self,n):
        if self.batch_size>n:raise ValueError('batch_size cannot exceed n_samples')

    def _candidate(self,x,g,state):
        return x-self.learning_rate*g,state

    def _batches(self,n,rng):
        order=rng.permutation(n)
        return tuple(order[start:start+int(self.batch_size)].copy() for start in range(0,n,int(self.batch_size)))
