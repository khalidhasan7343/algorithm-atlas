import numpy as np
from numpy.testing import assert_allclose,assert_array_equal
import pytest
pytestmark=pytest.mark.ml


@pytest.mark.oracle
def test_two_heavy_ball_steps_and_zero_gradient_inertia(b10):
    m=b10.load('momentum').Momentum(.1,.8)
    x=m.step([1.,-2.],[2.,-4.]);assert_allclose(x,[.8,-1.6])
    x=m.step(x,[-1.,3.]);assert_allclose(x,[.74,-1.58])
    assert_allclose(m.get_state()['velocity'],[.6,-.2]);assert m.get_state()['t']==2
    x=m.step(x,[0.,0.]);assert_allclose(x,[.692,-1.564])


@pytest.mark.oracle
def test_beta_zero_matches_plain_gd(b10):
    m=b10.load('momentum').Momentum(.1,0);gd=b10.load('batch-gradient-descent').BatchGradientDescent(.1)
    a=b=np.array([2.,-3.])
    for g in ([1.,2.],[-2.,1.],[0.,0.]):
        a=m.step(a,g);b=gd.step(b,g);assert_array_equal(a,b)


def test_spd_convergence_without_monotonicity_assumption(b10,objectives):
    A=np.diag([2.,4.]);f,g=objectives.quadratic(A,[2.,-8.])
    r=b10.load('momentum').Momentum(.1,.7).minimize(f,g,[3.,1.],max_iter=500)
    assert r.converged;assert_allclose(r.x,[1.,-2.],atol=1e-8)


@pytest.mark.parametrize('beta',[-1,1,True,np.nan])
def test_invalid_beta(b10,beta):
    with pytest.raises(ValueError):b10.load('momentum').Momentum(beta=beta)
