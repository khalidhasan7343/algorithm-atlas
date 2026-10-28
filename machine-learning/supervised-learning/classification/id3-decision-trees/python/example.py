"""Reproduce the canonical lesson example."""
from solution import ID3Classifier


if __name__ == "__main__":
    X = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
    y = ["no", "no", "yes", "yes"]
    model = ID3Classifier().fit(X, y)
    print(model.predict([[0.0, 1.0], [1.0, 0.0]]).tolist())
