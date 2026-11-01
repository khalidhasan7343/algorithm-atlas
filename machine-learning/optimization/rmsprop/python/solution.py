"""rmsprop; see its lesson for objective,stopping and resource contracts."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b10_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)

class RMSProp(support.FirstOrderOptimizer):
    """Uncentered,uncorrected squared-gradient EMA; epsilon outside sqrt."""
    def __init__(self,learning_rate=.01,beta=.9,epsilon=1e-8):
        self.beta,self.epsilon=beta,epsilon
        super().__init__(learning_rate)

    def _settings(self):
        super()._settings();support.real(self.beta,'beta',0.,1.,open_high=True)
        support.real(self.epsilon,'epsilon',1e-12,1.)

    def _initial_state(self,dimension):
        return dict(t=0,squared_average=np.zeros(dimension))

    def _candidate(self,x,g,state):
        state['squared_average']=self.beta*state['squared_average']+(1-self.beta)*g*g
        return x-self.learning_rate*g/(np.sqrt(state['squared_average'])+self.epsilon),state
