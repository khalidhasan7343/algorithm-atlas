import math
import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


@pytest.mark.oracle
def test_uncentered_uncorrected_ema_and_epsilon_placement(b10):
    m=b10.load('rmsprop').RMSProp(.1,.9,.25);x=np.array([1.,-2.]);v=[0.,0.]
    for gradients in ([2.,-4.],[-1.,3.]):
        expected=[]
        for j,g in enumerate(gradients):
            v[j]=.9*v[j]+.1*g*g
            expected.append(x[j]-.1*g/(math.sqrt(v[j])+.25))
        x=m.step(x,gradients);assert_allclose(x,expected,atol=1e-15)
        assert_allclose(m.get_state()['squared_average'],v)
        assert np.all(m.get_state()['squared_average']>=0)


@pytest.mark.numerical
def test_zero_and_tiny_gradients_are_finite(b10):
    m=b10.load('rmsprop').RMSProp(epsilon=1e-12)
    assert_array_equal(m.step([1.,-2.],[0.,0.]),[1.,-2.])
    x=m.step([1.,-2.],[1e-300,-1e-300]);assert np.isfinite(x).all()


@pytest.mark.oracle
def test_beta_zero_is_current_square_not_bias_corrected_average(b10):
    m=b10.load('rmsprop').RMSProp(.2,0,.1)
    assert_allclose(m.step([1.,1.],[2.,-4.]),[1-.4/2.1,1+.8/4.1])
    assert_allclose(m.get_state()['squared_average'],[4.,16.])


@pytest.mark.parametrize('settings',[dict(beta=1),dict(beta=-1),dict(epsilon=0),dict(epsilon=np.nan),dict(epsilon=True)])
def test_invalid_settings(b10,settings):
    with pytest.raises(ValueError):b10.load('rmsprop').RMSProp(**settings)
