"""Reproduce the canonical lesson example."""
from solution import C45Classifier


if __name__ == "__main__":
    X = [[0.0, 0.0], [0.0, 1.0], [1.0, 2.0], [1.0, 3.0]]
    y = ["no", "no", "yes", "yes"]
    model = C45Classifier(categorical_features=[0]).fit(X, y)
    print(model.predict([[0.0, 99.0], [1.0, -1.0], [2.0, 2.0]]).tolist())
