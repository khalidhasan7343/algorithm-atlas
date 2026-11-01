import numpy as np
from numpy.testing import assert_allclose
import pytest
pytestmark = pytest.mark.ml

@pytest.mark.oracle
def test_exact_recursion_and_multistep(b11):
    model = b11.load('exponential-smoothing').ExponentialSmoothing(.5, 0).fit([2.,4.,8.])
    assert_allclose(model.levels_, [1,2.5,5.25], rtol=0, atol=0)
    assert_allclose(model.fitted_values_, [0,1,2.5], rtol=0, atol=0)
    assert_allclose(model.forecast(4), [5.25]*4)
    assert_allclose(model.forecast_index(4), [3,4,5,6])

@pytest.mark.parametrize('alpha',[0.,1e-12,.3,1.])
def test_constant_and_boundary_coefficients(b11,alpha):
    model = b11.load('exponential-smoothing').ExponentialSmoothing(alpha).fit([7.,7.,7.])
    assert_allclose(model.forecast(3), 7)
    if alpha == 1:
        assert b11.load('exponential-smoothing').ExponentialSmoothing(alpha).fit([1,3,9]).forecast(1)[0] == 9

@pytest.mark.parametrize('alpha',[-.1,1.1,np.nan,np.inf,True,'x'])
def test_invalid_alpha(b11,alpha):
    with pytest.raises(ValueError):b11.load('exponential-smoothing').ExponentialSmoothing(alpha)

def test_single_observation_and_trend_diagnostic(b11):
    cls=b11.load('exponential-smoothing').ExponentialSmoothing
    assert cls().fit([4]).forecast(1)[0]==4
    model=cls(.5).fit(np.arange(20.))
    assert model.forecast(3)[0]<19
    assert_allclose(np.diff(model.forecast(3)),0)
