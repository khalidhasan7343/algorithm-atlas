import numpy as np
from numpy.testing import assert_allclose
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.oracle
def test_ar1_estimation_matches_independent_ols_and_analytic_forecast(b11):
    rng=np.random.default_rng(231);y=np.zeros(220)
    for t in range(1,len(y)):y[t]=.2+.6*y[t-1]+rng.normal(0,.1)
    model=b11.load('arima').ARIMA((1,0,0),tolerance=1e-9).fit(y)
    coef=np.linalg.lstsq(np.c_[np.ones(len(y)-1),y[:-1]],y[1:],rcond=None)[0]
    assert model.converged_,model.status_
    assert_allclose([model.params_['intercept'],model.params_['ar'][0]],coef,atol=2e-7)
    expected=[];last=y[-1]
    for _ in range(5):last=coef[0]+coef[1]*last;expected.append(last)
    assert_allclose(model.forecast(5),expected,atol=1e-7)

@pytest.mark.oracle
@pytest.mark.parametrize('d',[0,1,2])
def test_white_noise_mean_random_walk_drift_and_second_differences(b11,d):
    cls=b11.load('arima').ARIMA
    y=np.arange(1.,25.)**d if d else np.array([1.,3.,2.,6.,4.,7.,2.,4.,1.,3.])
    model=cls((0,d,0)).fit(y)
    expected=np.full(4,np.mean(y)) if d==0 else np.arange(25.,29.)**d
    assert_allclose(model.forecast(4),expected,atol=1e-10)
    if d==1:
        bare=cls((0,1,0),include_intercept=False).fit(y)
        assert_allclose(bare.forecast(4),y[-1]);assert bare.status_=='no-free-parameters'

@pytest.mark.oracle
@pytest.mark.parametrize('order,params',[((0,0,1),dict(ma=[.4],intercept=.1)),((1,0,1),dict(ar=[.5],ma=[-.3],intercept=.2)),((2,0,2),dict(ar=[.4,-.2],ma=[.3,.1],intercept=-.1))])
def test_innovations_use_errors_and_zero_future_shocks(b11,order,params):
    y=np.array([.3,-.2,.6,.1,-.5,.8,.4,.2,-.1,.7,.3,.9])
    model=b11.load('arima').ARIMA(order).filter(y,params)
    p,_,q=order;c=params['intercept'];ar=params.get('ar',[]);ma=params.get('ma',[]);burn=max(p,q);errors=[0.]*len(y)
    for t in range(burn,len(y)):
        errors[t]=y[t]-c-sum(ar[j]*y[t-j-1] for j in range(p))-sum(ma[j]*errors[t-j-1] for j in range(q))
    assert_allclose(model.innovations_,errors,atol=2e-15)
    assert np.isnan(model.fitted_values_[:burn]).all()
    assert_allclose(model.fitted_values_[burn:],y[burn:]-errors[burn:])
    future=[];history=list(y)
    for _ in range(5):
        value=c+sum(ar[j]*history[-j-1] for j in range(p))+sum(ma[j]*errors[-j-1] for j in range(q))
        future.append(value);history.append(value);errors.append(0.)
    assert_allclose(model.forecast(5),future,atol=2e-15)
    assert model.converged_ is None

@pytest.mark.numerical
@pytest.mark.oracle
@pytest.mark.parametrize('order',[(0,0,0),(1,0,0),(0,0,1),(2,0,2),(1,1,1),(1,2,1)])
def test_analytic_css_gradient_independent_finite_difference(b11,order):
    y=np.random.default_rng(232).normal(size=45);model=b11.load('arima').ARIMA(order)
    k=1+order[0]+order[2];u=np.linspace(-.2,.3,k);value,analytic=model.css_objective_gradient(y,u)
    expected=[]
    for j in range(k):
        step=np.eye(k)[j]*1e-6
        expected.append((model.css_objective_gradient(y,u+step)[0]-model.css_objective_gradient(y,u-step)[0])/2e-6)
    assert_allclose(analytic,expected,atol=2e-8,rtol=2e-7)
    assert np.isfinite(value)

@pytest.mark.oracle
def test_ma1_css_estimation_independent_scalar_search(b11):
    noise=np.random.default_rng(233).normal(0,.2,180);y=noise.copy();y[1:]+=.45*noise[:-1]
    def raw_css(theta):
        error=0.;total=0.
        for t in range(1,len(y)):
            error=y[t]-theta*error;total+=error*error
        return total/(2*(len(y)-1))
    left,right=-.949,.949
    for _ in range(100):
        a=left+(right-left)/3;b=right-(right-left)/3
        if raw_css(a)<raw_css(b):right=b
        else:left=a
    optimum=(left+right)/2
    model=b11.load('arima').ARIMA((0,0,1),include_intercept=False,tolerance=1e-9).fit(y)
    assert model.converged_,model.status_
    assert_allclose(model.params_['ma'],[optimum],atol=1e-6)
    assert_allclose(model.objective_*model.normalization_scale_**2,raw_css(optimum),atol=1e-12)

@pytest.mark.parametrize('order',[(-1,0,0),(3,0,0),(0,3,0),(0,0,3),(True,0,0),(1,0),(1.,0,0)])
def test_invalid_orders(b11,order):
    with pytest.raises(ValueError):b11.load('arima').ARIMA(order)

@pytest.mark.parametrize('parameters',[dict(ar=[1.2]),dict(ar=[np.nan]),dict(ar=[.2,.3]),dict(ar=[.2],unknown=1)])
def test_reject_unstable_or_malformed_parameters(b11,parameters):
    with pytest.raises(ValueError):b11.load('arima').ARIMA((1,0,0)).filter(np.arange(12.),parameters)

def test_minimum_history_constant_series_and_honest_budget(b11):
    cls=b11.load('arima').ARIMA
    with pytest.raises(ValueError):cls((2,2,2)).fit(np.arange(10.))
    model=cls((1,0,1)).fit(np.zeros(30));assert_allclose(model.forecast(3),0)
    model=cls((1,0,1),max_iter=1,tolerance=1e-12).fit(np.random.default_rng(234).normal(size=35))
    assert model.status_=='iteration-budget' and not model.converged_
