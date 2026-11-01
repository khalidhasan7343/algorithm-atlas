"""adamw; see its lesson for objective,stopping and resource contracts."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b10_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)

class AdamW(support.load('adam').Adam):
    """Canonical Adam moments plus decoupled masked shrinkage of the OLD parameters."""
    def __init__(self,learning_rate=.001,beta1=.9,beta2=.999,epsilon=1e-8,weight_decay=.01,decay_mask=None):
        self.weight_decay=weight_decay
        self.decay_mask=None if decay_mask is None else np.array(decay_mask,copy=True)
        super().__init__(learning_rate,beta1,beta2,epsilon)

    def _settings(self):
        super()._settings();support.real(self.weight_decay,'weight_decay',0.,1.)
        if self.learning_rate*self.weight_decay>1:
            raise ValueError('bounded shrinkage requires learning_rate*weight_decay<=1')
        if self.decay_mask is not None and (self.decay_mask.ndim!=1 or self.decay_mask.dtype.kind!='b' or not 1<=len(self.decay_mask)<=32):
            raise ValueError('decay_mask must be a boolean vector of length1..32')

    def minimize(self,fun,gradient,x0,*,max_iter=1000,tolerance=1e-8):
        # Dimension-dependent validation must also run when the first gradient is zero.
        self._settings()
        x=support.vector(x0)
        if self.decay_mask is not None and self.decay_mask.shape!=x.shape:
            raise ValueError('decay_mask must match parameter shape')
        return super().minimize(fun,gradient,x,max_iter=max_iter,tolerance=tolerance)

    def gradient_stopping(self):
        return self.weight_decay==0 or (self.decay_mask is not None and not np.any(self.decay_mask))

    def _candidate(self,x,g,state):
        mask=np.ones(len(x),dtype=bool) if self.decay_mask is None else self.decay_mask
        if mask.shape!=x.shape:raise ValueError('decay_mask must match parameter shape')
        candidate,new_state=super()._candidate(x,g,state)
        return candidate-self.learning_rate*self.weight_decay*mask*x,new_state
