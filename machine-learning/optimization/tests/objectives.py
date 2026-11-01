"""Independent test-only objectives; none is a new catalog canonical."""
import numpy as np


def quadratic(A,b):
    A=np.array(A,dtype=float);b=np.array(b,dtype=float)
    return (lambda x:float(.5*x@A@x-b@x), lambda x:A@x-b)


def rosenbrock(x):
    return float((1-x[0])**2+100*(x[1]-x[0]**2)**2)


def rosenbrock_gradient(x):
    return np.array([2*(x[0]-1)-400*x[0]*(x[1]-x[0]**2),200*(x[1]-x[0]**2)])


def rosenbrock_hessian(x):
    return np.array([[2-400*x[1]+1200*x[0]**2,-400*x[0]],[-400*x[0],200.]])


def finite_gradient(fun,x,h=1e-6):
    result=np.empty_like(x,dtype=float)
    for i in range(len(x)):
        delta=np.zeros_like(x,dtype=float);delta[i]=h
        result[i]=(fun(x+delta)-fun(x-delta))/(2*h)
    return result
