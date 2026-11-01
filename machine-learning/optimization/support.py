"""Bounded callback/result/state contracts; optimizer-specific mathematics is local."""
from dataclasses import dataclass
from functools import lru_cache
from functools import wraps
import copy
import importlib.util
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parent
TOPICS = ('batch-gradient-descent','stochastic-gradient-descent','mini-batch-gradient-descent',
          'momentum','rmsprop','adam','adamw','l-bfgs','genetic-algorithms','simulated-annealing')


class NumericalError(FloatingPointError):
    """A callback or update left the supported finite numerical domain."""


def numerical(function):
    @wraps(function)
    def checked(*args,**kwargs):
        try:
            with np.errstate(over='raise',divide='raise',invalid='raise'):
                return function(*args,**kwargs)
        except (FloatingPointError,OverflowError,np.linalg.LinAlgError) as error:
            raise NumericalError('unsupported optimizer numerical arithmetic') from error
    return checked


@dataclass
class OptimizationResult:
    x: np.ndarray
    fun: float
    n_iter: int
    nfev: int
    status: str
    converged: bool
    history: np.ndarray
    diagnostics: dict


def integer(value, name, low, high):
    if isinstance(value, (bool,np.bool_)) or not isinstance(value,(int,np.integer)) or not low <= value <= high:
        raise ValueError(f'{name} must be an integer in {low}..{high}')
    return int(value)


def real(value, name, low, high, *, open_low=False, open_high=False):
    if isinstance(value,(bool,np.bool_)) or not isinstance(value,(int,float,np.integer,np.floating)):
        raise ValueError(f'{name} must be a finite real scalar')
    try:
        value=float(value)
    except (OverflowError,ValueError) as error:
        raise ValueError(f'{name} must fit float64') from error
    if (not np.isfinite(value) or not low <= value <= high
            or (open_low and value==low) or (open_high and value==high)):
        raise ValueError(f'{name} outside supported range')
    return value


def vector(value, name='parameters', *, dimension=None, output=False):
    error_type=NumericalError if output else ValueError
    try:
        a=np.asarray(value)
    except (TypeError,ValueError) as error:
        raise ValueError(f'{name} must be a rectangular vector') from error
    if a.ndim!=1 or not 1<=len(a)<=32 or a.dtype.kind not in 'iuf':
        raise ValueError(f'{name} must be a real numeric vector of length1..32')
    if dimension is not None and a.shape!=(dimension,):
        raise ValueError(f'{name} shape differs from parameters')
    a=np.array(a,dtype=float,copy=True)
    limit=1e12 if name=='gradient' else 1e6
    if not np.isfinite(a).all() or np.any(np.abs(a)>limit):
        raise error_type(f'{name} must be finite with magnitude<={limit:g}')
    return a


def norm(a):
    largest=float(np.max(np.abs(a)))
    return largest*float(np.sqrt(np.sum((a/largest)**2))) if largest else 0.


def objective(fun,x):
    if not callable(fun):
        raise ValueError('objective must be callable')
    argument=x.copy();argument.flags.writeable=False
    try:
        with np.errstate(over='raise',divide='raise',invalid='raise'):
            value=fun(argument)
    except (FloatingPointError,OverflowError) as error:
        raise NumericalError('objective arithmetic failed') from error
    if isinstance(value,(bool,np.bool_)) or not isinstance(value,(int,float,np.integer,np.floating)):
        raise ValueError('objective must return one real scalar')
    try:
        value=float(value)
    except OverflowError as error:
        raise NumericalError('objective does not fit float64') from error
    if not np.isfinite(value) or abs(value)>1e100:
        raise NumericalError('objective must be finite with magnitude<=1e100')
    return value


def derivative(gradient,x,indices=None):
    if not callable(gradient):
        raise ValueError('gradient must be callable')
    argument=x.copy();argument.flags.writeable=False
    try:
        with np.errstate(over='raise',divide='raise',invalid='raise'):
            if indices is None:
                result=gradient(argument)
            else:
                selected=np.array(indices,dtype=int,copy=True);selected.flags.writeable=False
                result=gradient(argument,selected)
    except (FloatingPointError,OverflowError) as error:
        raise NumericalError('gradient arithmetic failed') from error
    return vector(result,'gradient',dimension=len(x),output=True)


def bias_correction(beta,step):
    return -math.expm1(step*math.log(beta)) if beta else 1.


class FirstOrderOptimizer:
    """Transactional stateful step and independent full-gradient minimize runs."""

    def __init__(self,learning_rate=.1):
        self.learning_rate=learning_rate
        self.reset()
        self._settings()

    def _settings(self):
        real(self.learning_rate,'learning_rate',1e-8,10.)

    def reset(self):
        self._dimension=None;self._state={'t':0}
        return self

    def get_state(self):
        return copy.deepcopy(self._state)

    def _initial_state(self,dimension):
        return {'t':0}

    def gradient_stopping(self):
        return True

    def step(self,parameters,gradient):
        self._settings();x=vector(parameters);g=vector(gradient,'gradient',dimension=len(x),output=True)
        if self._dimension is not None and self._dimension!=len(x):
            raise ValueError('reset optimizer before changing parameter dimension')
        state=self._initial_state(len(x)) if self._dimension is None else self.get_state()
        try:
            with np.errstate(over='raise',divide='raise',invalid='raise'):
                candidate,new_state=self._candidate(x,g,state)
        except (FloatingPointError,OverflowError) as error:
            raise NumericalError('optimizer update arithmetic failed') from error
        candidate=vector(candidate,output=True)
        new_state['t']=state['t']+1
        if any(isinstance(v,np.ndarray) and not np.isfinite(v).all() for v in new_state.values()):
            raise NumericalError('nonfinite optimizer state')
        self._dimension=len(x);self._state=copy.deepcopy(new_state)
        return candidate

    def minimize(self,fun,gradient,x0,*,max_iter=1000,tolerance=1e-8):
        self._settings();integer(max_iter,'max_iter',1,10000);real(tolerance,'tolerance',1e-12,1.)
        x=vector(x0);worker=copy.copy(self);worker.reset()
        value=objective(fun,x);g=derivative(gradient,x)
        history=[value];trajectory=[x.copy()];updates=0
        while updates<max_iter and not (worker.gradient_stopping() and norm(g)<=tolerance):
            x=worker.step(x,g);value=objective(fun,x);g=derivative(gradient,x)
            updates+=1;history.append(value);trajectory.append(x.copy())
        converged=bool(worker.gradient_stopping() and norm(g)<=tolerance)
        self._dimension=worker._dimension;self._state=worker.get_state()
        return OptimizationResult(x.copy(),value,updates,updates+1,
            'gradient-tolerance' if converged else 'iteration-budget',converged,np.array(history),
            dict(n_updates=updates,njev=updates+1,gradient_norm=norm(g),state=worker.get_state(),
                 trajectory=np.array(trajectory),gradient_stopping_enabled=worker.gradient_stopping()))


class SampledOptimizer(FirstOrderOptimizer):
    """Finite-sum epoch driver; each canonical supplies its actual batch selection."""

    def _settings(self):
        super()._settings();integer(self.random_state,'random_state',0,2**32-1)

    def minimize(self,fun,gradient,x0,*,n_samples,max_epochs=100,tolerance=1e-8):
        self._settings();n=integer(n_samples,'n_samples',1,256)
        integer(max_epochs,'max_epochs',1,1000);real(tolerance,'tolerance',1e-12,1.)
        if n*max_epochs>20000:
            raise ValueError('epoch/sample budget exceeds20000')
        self._validate_samples(n)
        x=vector(x0);worker=copy.copy(self);worker.reset();rng=np.random.default_rng(self.random_state)
        value=objective(fun,x);g=derivative(gradient,x,np.arange(n));njev=1
        history=[value];trajectory=[x.copy()];batches=[];epochs=updates=0
        while epochs<max_epochs and norm(g)>tolerance:
            for selected in worker._batches(n,rng):
                sample_gradient=derivative(gradient,x,selected);njev+=1
                x=worker.step(x,sample_gradient);updates+=1
                batches.append(np.array(selected,dtype=int,copy=True));trajectory.append(x.copy())
            value=objective(fun,x);g=derivative(gradient,x,np.arange(n));njev+=1
            epochs+=1;history.append(value)
        converged=bool(norm(g)<=tolerance)
        self._dimension=worker._dimension;self._state=worker.get_state()
        return OptimizationResult(x.copy(),value,epochs,epochs+1,
            'gradient-tolerance' if converged else 'epoch-budget',converged,np.array(history),
            dict(n_updates=updates,njev=njev,gradient_norm=norm(g),state=worker.get_state(),
                 trajectory=np.array(trajectory),batch_history=tuple(batches)))

    def _validate_samples(self,n):
        return None


def bits(value,name='bits',dimension=None):
    a=np.asarray(value)
    if a.ndim!=1 or not 1<=len(a)<=32 or a.dtype.kind not in 'biu' or np.any((a!=0)&(a!=1)):
        raise ValueError(f'{name}: binary integer/bool vector of length1..32 required')
    if dimension is not None and len(a)!=dimension:
        raise ValueError(f'{name}: bit-string dimension mismatch')
    return np.array(a,dtype=np.int64,copy=True)


@lru_cache(None)
def load(topic):
    if topic not in TOPICS:
        raise ValueError('unknown B10 canonical')
    name='atlas_b10_'+topic.replace('-','_')
    module=sys.modules.get(name)
    if module is None:
        spec=importlib.util.spec_from_file_location(name,ROOT/topic/'python/solution.py')
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module
