"""Reproduce the numerical example in the canonical lesson."""
import numpy as np
from solution import LinearRegression


if __name__ == "__main__":
    X = [[0.0], [1.0], [2.0]]
    y = [1.0, 3.0, 5.0]
    model = LinearRegression().fit(X, y)
    print(np.round(model.predict([[3.0]]), 6).tolist())
