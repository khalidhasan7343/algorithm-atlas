"""Reproduce the canonical lesson example."""
from solution import MultinomialNaiveBayes


if __name__ == "__main__":
    X = [[3.0, 0.0], [2.0, 1.0], [0.0, 3.0], [1.0, 2.0]]
    y = ["left", "left", "right", "right"]
    model = MultinomialNaiveBayes().fit(X, y)
    print(model.predict([[2.0, 0.0], [0.0, 2.0]]).tolist())
