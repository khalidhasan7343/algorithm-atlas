"""Reproduce the canonical lesson example."""
from solution import GaussianNaiveBayes


if __name__ == "__main__":
    X = [[0.0], [1.0], [5.0], [6.0]]
    y = ["a", "a", "b", "b"]
    model = GaussianNaiveBayes().fit(X, y)
    print(model.predict([[0.0], [6.0]]).tolist())
