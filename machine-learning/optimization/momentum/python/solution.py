"""momentum; see its lesson for objective,stopping and resource contracts."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b10_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)

class Momentum(support.FirstOrderOptimizer):
    """Heavy-ball accumulation v=beta*v+g,no Nesterov or EMA(1-beta) scaling."""
    def __init__(self,learning_rate=.1,beta=.9):
        self.beta=beta
        super().__init__(learning_rate)

    def _settings(self):
        super()._settings();support.real(self.beta,'beta',0.,1.,open_high=True)

    def _initial_state(self,dimension):
        return dict(t=0,velocity=np.zeros(dimension))

    def _candidate(self,x,g,state):
        state['velocity']=self.beta*state['velocity']+g
        return x-self.learning_rate*state['velocity'],state
