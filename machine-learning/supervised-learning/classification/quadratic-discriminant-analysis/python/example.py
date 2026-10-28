"""Reproduce the canonical lesson example."""
from solution import QuadraticDiscriminantAnalysis


if __name__ == "__main__":
    X = [[-2.0], [-1.0], [1.0], [2.0]]
    y = ["left", "left", "right", "right"]
    model = QuadraticDiscriminantAnalysis().fit(X, y)
    print(model.predict([[-3.0], [3.0]]).tolist())
