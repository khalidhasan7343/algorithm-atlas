import math
from decimal import Decimal,localcontext
import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


@pytest.mark.oracle
def test_two_bias_corrected_steps_and_exact_state(b10):
    model=b10.load('adam').Adam(.1,.8,.6,.25);x=np.array([1.,-2.]);m=np.zeros(2);v=np.zeros(2)
    for t,g in enumerate(([2.,-4.],[-1.,3.]),1):
        g=np.array(g);m=.8*m+.2*g;v=.6*v+.4*g*g
        expected=x-.1*(m/(1-.8**t))/(np.sqrt(v/(1-.6**t))+.25)
        x=model.step(x,g);assert_allclose(x,expected,atol=1e-15)
        state=model.get_state();assert state['t']==t
        assert_allclose(state['first_moment'],m);assert_allclose(state['second_moment'],v)


@pytest.mark.oracle
def test_first_step_epsilon_outside_sqrt_and_no_uncorrected_moments(b10):
    actual=b10.load('adam').Adam(.2,.9,.999,.25).step([1.,1.],[2.,-4.])
    assert_allclose(actual,[1-.4/2.25,1+.8/4.25],atol=1e-15)


@pytest.mark.numerical
def test_near_one_beta_bias_correction_against_decimal(b10):
    beta=float(np.nextafter(1.,0.));model=b10.load('adam').Adam(.01,beta,beta,1e-8)
    x=model.step([1.],[2.])
    assert_allclose(x,[1-.02/(2+1e-8)],atol=1e-15)
    with localcontext() as ctx:
        ctx.prec=60
        expected=1-Decimal.from_float(beta)**10000
        assert_allclose(b10.bias_correction(beta,10000),float(expected),rtol=2e-15)


def test_zero_gradient_still_decays_existing_moment_state(b10):
    model=b10.load('adam').Adam(.1,.8,.6,.1);x=model.step([1.],[2.]);old=x.copy()
    x=model.step(x,[0.]);assert x[0]<old[0]
    assert_allclose(model.get_state()['first_moment'],[.32])
    assert_allclose(model.get_state()['second_moment'],[.96])


@pytest.mark.parametrize('settings',[dict(beta1=1),dict(beta2=1),dict(beta1=True),dict(beta2=-1),dict(epsilon=0)])
def test_invalid_settings(b10,settings):
    with pytest.raises(ValueError):b10.load('adam').Adam(**settings)
