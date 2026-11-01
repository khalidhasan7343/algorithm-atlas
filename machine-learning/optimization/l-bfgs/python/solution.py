"""Unconstrained limited-memory BFGS with bounded strong-Wolfe bracket/zoom search."""
import importlib.util
from pathlib import Path
import sys

import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b10_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)


def _positive_curvature(s,y):
    product=float(s@y)
    return bool(product>1e-20 and product>1e-10*support.norm(s)*support.norm(y))


def _two_loop(g,pairs):
    q=g.copy();coefficients=[]
    for s,y in reversed(pairs):
        rho=1/float(s@y);alpha=rho*float(s@q)
        q-=alpha*y;coefficients.append(alpha)
    scale=float(pairs[-1][0]@pairs[-1][1])/float(pairs[-1][1]@pairs[-1][1]) if pairs else 1.
    result=scale*q
    for (s,y),alpha in zip(pairs,reversed(coefficients)):
        beta=float(y@result)/float(s@y)
        result+=s*(alpha-beta)
    if not np.isfinite(result).all():
        raise support.NumericalError('nonfinite inverse-curvature product')
    return result


@support.numerical
def inverse_hessian_product(gradient,pairs):
    """Public mathematical inspection helper; requires usable positive-curvature pairs."""
    g=support.vector(gradient,'gradient',output=True)
    if not isinstance(pairs,(list,tuple)) or len(pairs)>20:
        raise ValueError('at most20 explicit(s,y) pairs required')
    checked=[]
    for pair in pairs:
        if not isinstance(pair,(list,tuple)) or len(pair)!=2:
            raise ValueError('each history pair must contain s and y')
        vectors=[]
        for value,limit in zip(pair,(2e6,2e12)):
            a=np.asarray(value)
            if a.shape!=g.shape or a.dtype.kind not in 'iuf':
                raise ValueError('curvature vectors must match gradient shape')
            a=np.array(a,dtype=float,copy=True)
            if not np.isfinite(a).all() or np.any(np.abs(a)>limit):
                raise ValueError('curvature vector outside finite numerical bounds')
            vectors.append(a)
        s,y=vectors
        if not _positive_curvature(s,y):raise ValueError('usable positive curvature required')
        checked.append((s,y))
    with np.errstate(over='raise',divide='raise',invalid='raise'):
        return _two_loop(g,checked)


class LBFGS:
    """Fresh limited-memory solve per call; not L-BFGS-B or a constraint solver."""

    def __init__(self,history_size=5,c1=1e-4,c2=.9,max_line_search=40,initial_step=1.,max_step=1e6):
        self.history_size,self.c1,self.c2=history_size,c1,c2
        self.max_line_search,self.initial_step,self.max_step=max_line_search,initial_step,max_step
        self._settings()

    def _settings(self):
        support.integer(self.history_size,'history_size',1,20)
        support.integer(self.max_line_search,'max_line_search',1,80)
        support.real(self.c1,'c1',0.,1.,open_low=True,open_high=True)
        support.real(self.c2,'c2',0.,1.,open_low=True,open_high=True)
        if not self.c1<self.c2:raise ValueError('strong Wolfe requires0<c1<c2<1')
        support.real(self.max_step,'max_step',1e-8,1e6)
        support.real(self.initial_step,'initial_step',1e-8,self.max_step)

    def _line_search(self,fun,gradient,x,value,g,direction):
        slope=float(g@direction);used=nfev=njev=0
        def trial(alpha):
            nonlocal used,nfev,njev
            used+=1
            if np.any(np.abs(direction)>(1e6+np.abs(x))/alpha):
                return None
            candidate=x+alpha*direction
            if not np.isfinite(candidate).all() or np.any(np.abs(candidate)>1e6):
                return None  # Explicit resource-domain rejection; no callback value fabricated.
            new_value=support.objective(fun,candidate);nfev+=1
            new_g=support.derivative(gradient,candidate);njev+=1
            return candidate,new_value,new_g,float(new_g@direction),alpha
        def zoom(lo,hi,phi_lo):
            while used<self.max_line_search:
                if abs(hi-lo)<=1e-14*max(1.,abs(lo),abs(hi)):return None
                alpha=(lo+hi)/2;point=trial(alpha)
                if point is None:
                    hi=alpha;continue
                _,phi,_,dphi,_=point
                if phi>value+self.c1*alpha*slope or phi>=phi_lo:
                    hi=alpha
                else:
                    if abs(dphi)<=-self.c2*slope:return point
                    if dphi*(hi-lo)>=0:hi=lo
                    lo=alpha;phi_lo=phi
            return None
        previous=0.;phi_previous=value;alpha=float(self.initial_step);accepted=None
        while used<self.max_line_search:
            point=trial(alpha)
            if point is None:
                accepted=zoom(previous,alpha,phi_previous);break
            _,phi,_,dphi,_=point
            if phi>value+self.c1*alpha*slope or (previous>0 and phi>=phi_previous):
                accepted=zoom(previous,alpha,phi_previous);break
            if abs(dphi)<=-self.c2*slope:
                accepted=point;break
            if dphi>=0:
                accepted=zoom(alpha,previous,phi);break
            previous=alpha;phi_previous=phi
            next_alpha=min(2*alpha,float(self.max_step))
            if next_alpha==alpha:break
            alpha=next_alpha
        return accepted,nfev,njev,used

    @support.numerical
    def minimize(self,fun,gradient,x0,*,max_iter=200,tolerance=1e-8):
        self._settings();support.integer(max_iter,'max_iter',1,2000)
        support.real(tolerance,'tolerance',1e-12,1.)
        if max_iter*self.max_line_search>20000:raise ValueError('line-search trial budget exceeds20000')
        x=support.vector(x0);value=support.objective(fun,x);g=support.derivative(gradient,x)
        nfev=njev=1;history=[value];trajectory=[x.copy()];pairs=[];wolfe=[]
        iterations=skipped=resets=total_trials=0;status='iteration-budget'
        while iterations<max_iter and support.norm(g)>tolerance:
            with np.errstate(over='raise',divide='raise',invalid='raise'):
                direction=-_two_loop(g,pairs)
                slope=float(g@direction)
            if slope>=0:
                pairs=[];direction=-g;resets+=1;slope=-float(g@g)
            point,nf,ng,trials=self._line_search(fun,gradient,x,value,g,direction)
            nfev+=nf;njev+=ng;total_trials+=trials
            if point is None:
                status='line-search-failed';break
            new_x,new_value,new_g,new_slope,alpha=point
            s=new_x-x;y=new_g-g
            if _positive_curvature(s,y):
                pairs.append((s.copy(),y.copy()));pairs=pairs[-int(self.history_size):]
            else:skipped+=1
            wolfe.append(dict(step_size=alpha,value_before=value,value_after=new_value,
                              slope_before=slope,slope_after=new_slope))
            x,value,g=new_x,new_value,new_g
            iterations+=1;history.append(value);trajectory.append(x.copy())
        converged=bool(support.norm(g)<=tolerance)
        if converged:status='gradient-tolerance'
        return support.OptimizationResult(x.copy(),value,iterations,nfev,status,converged,np.array(history),
            dict(n_updates=iterations,njev=njev,gradient_norm=support.norm(g),trajectory=np.array(trajectory),
                 curvature_pairs=tuple((s.copy(),y.copy()) for s,y in pairs),wolfe_steps=tuple(wolfe),
                 skipped_curvature_updates=skipped,memory_resets=resets,line_search_trials=total_trials))
