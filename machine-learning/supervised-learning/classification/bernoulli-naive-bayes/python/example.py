"""Reproduce the canonical lesson example."""
from solution import BernoulliNaiveBayes


if __name__ == "__main__":
    X = [[1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 1.0]]
    y = ["a", "a", "b", "b"]
    model = BernoulliNaiveBayes().fit(X, y)
    print(model.predict([[1.0, 0.0], [0.0, 1.0]]).tolist())
