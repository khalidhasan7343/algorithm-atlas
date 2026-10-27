"""Reproduce the numerical example in the canonical lesson."""
import numpy as np
from solution import LassoRegression


if __name__ == "__main__":
    X = [[-1.0], [0.0], [1.0]]
    y = [-2.0, 0.0, 2.0]
    model = LassoRegression(alpha=1.0 / 3.0).fit(X, y)
    print(np.round(model.predict([[2.0]]), 6).tolist())
