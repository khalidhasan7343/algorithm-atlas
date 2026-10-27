"""Reproduce the numerical example in the canonical lesson."""
import numpy as np
from solution import PolynomialRegression


if __name__ == "__main__":
    X = [[-2.0], [-1.0], [0.0], [1.0], [2.0]]
    y = [4.0, 1.0, 0.0, 1.0, 4.0]
    model = PolynomialRegression(degree=2).fit(X, y)
    print(np.round(model.predict([[3.0]]), 6).tolist())
