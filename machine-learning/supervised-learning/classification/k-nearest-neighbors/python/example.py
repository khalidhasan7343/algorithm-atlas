"""Reproduce the canonical lesson example."""
from solution import KNearestNeighbors


if __name__ == "__main__":
    X = [[-1.0], [1.0], [1.0], [3.0]]
    y = ["z", "a", "b", "a"]
    model = KNearestNeighbors(n_neighbors=2).fit(X, y)
    print(model.predict([[1.0]]).tolist())
