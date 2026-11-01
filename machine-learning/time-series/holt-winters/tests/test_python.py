import numpy as np
from numpy.testing import assert_allclose
import pytest
pytestmark=pytest.mark.ml

@pytest.mark.oracle
def test_hand_states_and_seasonal_offsets(b11):
    y=[8.,12.,9.,14.,12.,17.,13.]
    model=b11.load('holt-winters').HoltWinters(2,.4,.3,.2,initial_level=10,initial_trend=1,initial_seasonal=[-2,2]).fit(y)
    l,b=10.,1.;seasons=[-2.,2.];states=[];pred=[]
    for i in range(2,len(y)):
        j=i%2;old=l;oldseason=seasons[j];pred.append(old+b+oldseason)
        l=.4*(y[i]-oldseason)+.6*(old+b)
        b=.3*(l-old)+.7*b
        seasons[j]=.2*(y[i]-l)+.8*oldseason
        states.append([l,b,*seasons])
    assert_allclose(model.states_,states,rtol=1e-14,atol=1e-14)
    assert np.isnan(model.fitted_values_[:2]).all()
    assert_allclose(model.fitted_values_[2:],pred)
    assert_allclose(model.forecast(6),[l+h*b+seasons[(len(y)+h-1)%2] for h in range(1,7)])

@pytest.mark.parametrize('period',[2,3,4,12])
@pytest.mark.parametrize('trend',[0.,.25])
def test_constant_trend_and_additive_seasonality(b11,period,trend):
    season=np.arange(period,dtype=float);season-=np.mean(season)
    t=np.arange(period*5);y=10+trend*t+season[t%period]
    m=b11.load('holt-winters').HoltWinters(period).fit(y)
    future=np.arange(len(y),len(y)+period*2+1)
    assert_allclose(m.forecast(len(future)),10+trend*future+season[future%period],atol=1e-12)
    assert_allclose(b11.load('holt-winters').HoltWinters(period).fit(np.full(period*3,7.)).forecast(3),7)

@pytest.mark.parametrize('kwargs',[dict(seasonal_period=1),dict(seasonal_period=13),dict(seasonal_period=2,alpha=-1),dict(seasonal_period=2,beta=1.1),dict(seasonal_period=2,gamma=np.nan)])
def test_invalid_parameters(b11,kwargs):
    with pytest.raises(ValueError):b11.load('holt-winters').HoltWinters(**kwargs)

def test_initialization_and_minimum_history(b11):
    cls=b11.load('holt-winters').HoltWinters
    for model,y in [(cls(2),[1,2,3]),(cls(2,initial_level=1),[1,2,3,4]),(cls(2,initial_level=1,initial_trend=0,initial_seasonal=[1,1]),[1,2,3,4])]:
        with pytest.raises(ValueError):model.fit(y)
