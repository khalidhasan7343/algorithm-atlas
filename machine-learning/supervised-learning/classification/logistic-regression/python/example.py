"""Reproduce the canonical lesson example."""
from solution import LogisticRegression


if __name__ == "__main__":
    X = [[-2.0], [-1.0], [1.0], [2.0]]
    y = ["cold", "cold", "warm", "warm"]
    model = LogisticRegression(alpha=0.1).fit(X, y)
    print(model.predict([[-3.0], [3.0]]).tolist())
