"""Reproduce the canonical lesson example."""
from solution import CARTClassifier


if __name__ == "__main__":
    X = [[0.0], [1.0], [2.0], [3.0]]
    y = ["a", "a", "b", "b"]
    model = CARTClassifier(max_depth=1).fit(X, y)
    print(model.predict([[0.5], [2.5]]).tolist())
