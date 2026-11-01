import importlib.util
from pathlib import Path
import numpy as np
from numpy.testing import assert_allclose
import pytest
pytestmark=pytest.mark.ml


@pytest.mark.numerical
@pytest.mark.oracle
@pytest.mark.parametrize('n',[1,2,4])
def test_quadratic_independent_gradient_and_hessian(objectives,n):
    rng=np.random.default_rng(22010+n);M=rng.normal(0,.3,(n,n));A=M.T@M+np.eye(n);b=rng.normal(size=n);x=rng.normal(size=n)
    f,g=objectives.quadratic(A,b)
    assert_allclose(g(x),objectives.finite_gradient(f,x),atol=2e-9,rtol=1e-7)
    H=np.column_stack([(g(x+1e-6*np.eye(n)[i])-g(x-1e-6*np.eye(n)[i]))/2e-6 for i in range(n)])
    assert_allclose(H,A,atol=1e-9,rtol=1e-7)


@pytest.mark.numerical
@pytest.mark.parametrize('x',[[-.8,1.2],[.5,.1],[1.,1.]])
def test_rosenbrock_independent_gradient_and_hessian(objectives,x):
    x=np.array(x);g=objectives.rosenbrock_gradient
    assert_allclose(g(x),objectives.finite_gradient(objectives.rosenbrock,x),atol=5e-8,rtol=2e-7)
    H=np.column_stack([(g(x+1e-6*np.eye(2)[i])-g(x-1e-6*np.eye(2)[i]))/2e-6 for i in range(2)])
    assert_allclose(H,objectives.rosenbrock_hessian(x),atol=2e-7,rtol=2e-7)


@pytest.mark.oracle
def test_approved_b1_gradient_and_unpenalized_bias_compatibility(b10):
    root=Path(__file__).resolve().parents[2]
    path=root/'supervised-learning/regression/linear-regression/python/solution.py'
    spec=importlib.util.spec_from_file_location('atlas_b10_preserved_b1_linear',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    X=np.array([[-1.,0],[0,1],[1,0],[0,-1],[1,1],[-1,-1]])
    y=X@np.array([1.,-2.])+.5
    def fun(x):return module.loss_gradient(X,y,x[:-1],x[-1])[0]
    def gradient(x):
        _,g,b=module.loss_gradient(X,y,x[:-1],x[-1]);return np.r_[g,b]
    result=b10.load('batch-gradient-descent').BatchGradientDescent(.2).minimize(fun,gradient,[0.,0.,0.],max_iter=1000)
    assert result.converged
    reference=module.LinearRegression().fit(X,y)
    assert_allclose(result.x,np.r_[reference.coef_,reference.intercept_],atol=2e-8)
