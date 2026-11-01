import numpy as np
from numpy.testing import assert_allclose
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.oracle
def test_exact_multiplicative_lag_polynomials(b11):
    model=b11.load('sarima').SARIMA((1,0,1),(1,0,1,4))
    ar,ma=model.lag_polynomials(dict(ar=[.4],ma=[.2],seasonal_ar=[.5],seasonal_ma=[-.3]))
    assert_allclose(ar,[1,-.4,0,0,-.5,.2],atol=0,rtol=0)
    assert_allclose(ma,[1,.2,0,0,-.3,-.06],atol=1e-16)

@pytest.mark.oracle
@pytest.mark.parametrize('kind',['ar','ma','mixed'])
def test_independent_seasonal_innovation_and_multistep_recursion(b11,kind):
    y=np.random.default_rng(235).normal(size=40);params=dict(intercept=.1)
    if kind=='ar':order=(0,0,0);season=(1,0,0,3);params.update(seasonal_ar=[.6]);ar={3:.6};ma={}
    elif kind=='ma':order=(0,0,0);season=(0,0,1,3);params.update(seasonal_ma=[.4]);ar={};ma={3:.4}
    else:order=(1,0,1);season=(1,0,1,3);params.update(ar=[.4],ma=[.2],seasonal_ar=[.5],seasonal_ma=[.3]);ar={1:.4,3:.5,4:-.2};ma={1:.2,3:.3,4:.06}
    model=b11.load('sarima').SARIMA(order,season).filter(y,params)
    burn=max([0,*ar,*ma]);errors=[0.]*len(y)
    for t in range(burn,len(y)):errors[t]=y[t]-.1-sum(a*y[t-lag] for lag,a in ar.items())-sum(a*errors[t-lag] for lag,a in ma.items())
    assert_allclose(model.innovations_,errors,atol=2e-15)
    expected=[];history=list(y)
    for _ in range(8):
        value=.1+sum(a*history[-lag] for lag,a in ar.items())+sum(a*errors[-lag] for lag,a in ma.items());history.append(value);errors.append(0.);expected.append(value)
    assert_allclose(model.forecast(8),expected,atol=2e-15)

@pytest.mark.parametrize('order',[(0,0,0),(1,0,1),(1,1,1)])
def test_zero_seasonal_orders_reduce_to_arima(b11,order):
    y=np.random.default_rng(236).normal(size=40)
    a=b11.load('arima').ARIMA(order).fit(y);b=b11.load('sarima').SARIMA(order,(0,0,0,4)).fit(y)
    assert_allclose(a.forecast(6),b.forecast(6),atol=1e-12)
    assert_allclose(a.innovations_,b.innovations_,atol=1e-12);assert a.status_==b.status_

@pytest.mark.oracle
@pytest.mark.parametrize('period',[2,3,4,12])
def test_seasonal_difference_inversion_and_seasonal_ar_estimation(b11,period):
    n=period*8;t=np.arange(n);y=2*(t//period)+np.arange(period)[t%period]
    model=b11.load('sarima').SARIMA((0,0,0),(0,1,0,period)).fit(y)
    future=np.arange(n,n+period*2+1)
    assert_allclose(model.forecast(len(future)),2*(future//period)+np.arange(period)[future%period],atol=1e-10)
    rng=np.random.default_rng(237+period);y=rng.normal(0,.1,150)
    for i in range(period,len(y)):y[i]+=.55*y[i-period]
    fitted=b11.load('sarima').SARIMA((0,0,0),(1,0,0,period),include_intercept=False,tolerance=1e-9).fit(y)
    reference=float(y[period:]@y[:-period]/(y[:-period]@y[:-period]))
    assert_allclose(fitted.params_['seasonal_ar'],[reference],atol=1e-6)

@pytest.mark.numerical
@pytest.mark.oracle
@pytest.mark.parametrize('season',[(1,0,0,3),(0,1,1,4),(1,1,1,3)])
def test_seasonal_css_polynomial_gradient_independent_finite_difference(b11,season):
    y=np.random.default_rng(238).normal(size=60);model=b11.load('sarima').SARIMA((1,1,1),season)
    k=3+season[0]+season[2];u=np.linspace(-.2,.2,k);_,gradient=model.css_objective_gradient(y,u);expected=[]
    for j in range(k):
        step=np.eye(k)[j]*1e-6;expected.append((model.css_objective_gradient(y,u+step)[0]-model.css_objective_gradient(y,u-step)[0])/2e-6)
    assert_allclose(gradient,expected,atol=2e-8,rtol=2e-7)

@pytest.mark.parametrize('season',[(0,0,0,1),(0,0,0,13),(2,0,0,4),(0,2,0,4),(0,0,2,4),(1,0,0)])
def test_invalid_seasonal_configuration(b11,season):
    with pytest.raises(ValueError):b11.load('sarima').SARIMA(seasonal_order=season)

def test_combined_seasonal_nonseasonal_inverse_and_insufficient_history(b11):
    cls=b11.load('sarima').SARIMA;t=np.arange(60.);y=t*t
    model=cls((0,1,0),(0,1,0,4)).fit(y)
    assert_allclose(model.forecast(8),np.arange(60.,68.)**2,atol=1e-9)
    with pytest.raises(ValueError):cls((2,2,2),(1,1,1,12)).fit(np.arange(30.))
