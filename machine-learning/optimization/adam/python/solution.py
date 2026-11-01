"""adam; see its lesson for objective,stopping and resource contracts."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b10_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)

class Adam(support.FirstOrderOptimizer):
    """Bias-corrected first/second moments; no weight decay,AMSGrad or schedule."""
    def __init__(self,learning_rate=.001,beta1=.9,beta2=.999,epsilon=1e-8):
        self.beta1,self.beta2,self.epsilon=beta1,beta2,epsilon
        super().__init__(learning_rate)

    def _settings(self):
        super()._settings()
        support.real(self.beta1,'beta1',0.,1.,open_high=True)
        support.real(self.beta2,'beta2',0.,1.,open_high=True)
        support.real(self.epsilon,'epsilon',1e-12,1.)

    def _initial_state(self,dimension):
        return dict(t=0,first_moment=np.zeros(dimension),second_moment=np.zeros(dimension))

    def _candidate(self,x,g,state):
        t=state['t']+1
        m=self.beta1*state['first_moment']+(1-self.beta1)*g
        v=self.beta2*state['second_moment']+(1-self.beta2)*g*g
        corrected_m=m/support.bias_correction(self.beta1,t)
        corrected_v=v/support.bias_correction(self.beta2,t)
        candidate=x-self.learning_rate*corrected_m/(np.sqrt(corrected_v)+self.epsilon)
        return candidate,dict(t=state['t'],first_moment=m,second_moment=v)
