"""Reproduce the numerical example in the canonical lesson."""
import numpy as np
from solution import DecisionTreeRegression


if __name__ == "__main__":
    X = [[0.0], [1.0], [2.0], [3.0]]
    y = [1.0, 1.0, 5.0, 5.0]
    model = DecisionTreeRegression(max_depth=1).fit(X, y)
    print(np.round(model.predict([[0.5], [2.5]]), 6).tolist())
