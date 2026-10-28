"""Reproduce the canonical lesson example."""
from solution import SupportVectorMachine


if __name__ == "__main__":
    X = [[-2.0], [-1.0], [1.0], [2.0]]
    y = [-1, -1, 1, 1]
    model = SupportVectorMachine().fit(X, y)
    print(model.predict([[-3.0], [3.0]]).tolist())
