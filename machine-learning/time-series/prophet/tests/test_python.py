import importlib.util
from pathlib import Path
import sys
import numpy as np
from numpy.testing import assert_allclose
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.oracle
@pytest.mark.parametrize('penalty',[0.,.1,2.])
def test_independent_design_normal_equations_components_and_objective(b11,penalty):
    n=60;t=np.arange(n,dtype=float);cp=[18.,35.];periods=[(7.,2),(13.,1)]
    # Independent explicit columns: no production basis helper used as oracle.
    X=np.column_stack([np.ones(n),t/(n-1),np.maximum(t-18,0)/(n-1),np.maximum(t-35,0)/(n-1),np.sin(2*np.pi*t/7),np.cos(2*np.pi*t/7),np.sin(4*np.pi*t/7),np.cos(4*np.pi*t/7),np.sin(2*np.pi*t/13),np.cos(2*np.pi*t/13)])
    truth=np.array([3,4,8,-5,1.2,.3,-.4,.7,.5,-.1]);y=X@truth+.03*np.random.default_rng(239).normal(size=n)
    model=b11.load('prophet').Prophet(changepoints=cp,seasonalities=periods,regularization=penalty).fit(y)
    D=np.diag([0,0,*([1]*8)]);coef=np.linalg.solve(X.T@X+n*penalty*D,X.T@y)
    assert_allclose(model.design_matrix_,X,atol=1e-15)
    assert_allclose(model.coef_,coef,atol=1e-10,rtol=1e-10)
    assert_allclose(model.components_['trend'],X[:,:4]@coef[:4],atol=1e-11)
    assert_allclose(model.components_['seasonal'],X[:,4:]@coef[4:],atol=1e-11)
    assert_allclose(model.fitted_values_,model.components_['trend']+model.components_['seasonal'])
    assert_allclose(model.objective_,np.mean((X@coef-y)**2)/2+penalty*np.sum(coef[2:]**2)/2,atol=1e-12)
    assert model.converged_

@pytest.mark.oracle
@pytest.mark.parametrize('cp',[(),(15.,)])
def test_linear_piecewise_trend_and_future_extrapolation(b11,cp):
    t=np.arange(40.);y=4+.2*t+(.6*np.maximum(t-15,0) if cp else 0)
    model=b11.load('prophet').Prophet(changepoints=cp,seasonalities=(),regularization=0).fit(y)
    future=np.arange(40.,48.);expected=4+.2*future+(.6*np.maximum(future-15,0) if cp else 0)
    assert_allclose(model.forecast(8),expected,atol=1e-11)
    assert_allclose(model.forecast_index(8),future)

@pytest.mark.oracle
def test_fourier_forecast_components_and_training_only_time_scale(b11):
    t=np.arange(42.);y=2+.1*t+1.5*np.sin(2*np.pi*t/7)-.3*np.cos(2*np.pi*t/7)
    cls=b11.load('prophet').Prophet
    a=cls(seasonalities=((7,1),),regularization=0).fit(y,timestamps=1e9+2*t)
    b=cls(seasonalities=((7,1),),regularization=0).fit(y,timestamps=t)
    future=np.arange(42.,48.);assert_allclose(a.forecast(6),2+.1*future+1.5*np.sin(2*np.pi*future/7)-.3*np.cos(2*np.pi*future/7),atol=1e-11)
    assert_allclose(a.forecast(6),b.forecast(6),atol=1e-12)
    assert_allclose(a.forecast_index(6),1e9+2*future)
    assert_allclose(a.forecast_components(6)['total'],a.forecast(6))

@pytest.mark.numerical
def test_singular_design_has_honest_rank_and_finite_minimum_norm(b11):
    model=b11.load('prophet').Prophet(seasonalities=((2,2),),regularization=0).fit(np.ones(12))
    assert model.design_rank_<len(model.coef_)
    assert np.isfinite(model.forecast(4)).all();assert_allclose(model.forecast(4),1,atol=1e-12)

@pytest.mark.oracle
def test_approved_b10_optimizer_matches_same_declared_ridge_objective(b11):
    t=np.arange(36.);y=3+.2*t+np.sin(2*np.pi*t/7)
    model=b11.load('prophet').Prophet(changepoints=(12,),seasonalities=((7,1),),regularization=.2).fit(y)
    X=model.design_matrix_;mask=np.array([0,0,1,1,1]);n=len(y)
    def fun(w):return float(np.mean((X@w-y)**2)/2+.1*np.sum(mask*w*w))
    def grad(w):return X.T@(X@w-y)/n+.2*mask*w
    # Remove the irreducible constant noise energy analytically; keep the same
    # minimizer and tolerance without near-optimum objective cancellation.
    H=X.T@X/n+.2*np.diag(mask)
    reference=np.linalg.solve(H,X.T@y/n)
    def centered(w):
        v=w-reference;return float(v@H@v/2)
    def centered_gradient(w):return H@(w-reference)
    assert_allclose(centered_gradient(np.zeros(5)),grad(np.zeros(5)),atol=1e-14)
    arima=b11.load('arima');result=arima._b10().load('l-bfgs').LBFGS().minimize(centered,centered_gradient,np.zeros(5),max_iter=200,tolerance=1e-9)
    assert result.converged,result.status
    assert_allclose(result.x,model.coef_,atol=2e-7)
    assert_allclose(fun(result.x),model.objective_,atol=1e-12)

@pytest.mark.parametrize('kwargs',[dict(changepoints=[-1]),dict(changepoints=[2,2]),dict(changepoints=[3,2]),dict(changepoints=[np.nan]),dict(changepoints='x'),dict(seasonalities=[(0,1)]),dict(seasonalities=[(7,0)]),dict(seasonalities=[(7,1),(7,2)]),dict(seasonalities=[(7,8)]*5),dict(regularization=-1),dict(regularization=np.nan)])
def test_invalid_specification(b11,kwargs):
    with pytest.raises(ValueError):b11.load('prophet').Prophet(**kwargs)

def test_changepoints_must_be_training_interior_and_failed_fit_is_atomic(b11):
    cls=b11.load('prophet').Prophet;m=cls(changepoints=(4,)).fit(np.arange(12.));before=m.forecast(3)
    with pytest.raises(ValueError):m.fit(np.arange(4.))
    assert_allclose(m.forecast(3),before)
    with pytest.raises(ValueError):cls().fit([1.])
