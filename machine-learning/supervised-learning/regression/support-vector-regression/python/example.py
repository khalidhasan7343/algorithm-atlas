"""Reproduce the numerical example in the canonical lesson."""
import numpy as np
from solution import SupportVectorRegression


if __name__ == "__main__":
    X = [[-1.0], [0.0], [1.0]]
    y = [-1.0, 0.0, 1.0]
    model = SupportVectorRegression(C=10.0, epsilon=0.1, kernel="linear", tol=1e-9).fit(X, y)
    print(np.round(model.predict([[2.0]]), 6).tolist())
