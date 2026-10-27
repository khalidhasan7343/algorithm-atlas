"""Small held-out regression experiment; no downloads or performance ranking.

Run from any directory with the repository's ML runtime dependencies installed.
Hyperparameters are fixed before generating/evaluating the test targets. Metrics
are an illustration on one synthetic response, not a model-selection protocol.
"""
import importlib.util
import json
from pathlib import Path
import time

import numpy as np

_spec = importlib.util.spec_from_file_location("regression_experiment_support", Path(__file__).parents[1] / "support.py")
support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(support)

CASES = [
    ("linear-regression", "LinearRegression", {}),
    ("ridge-regression", "RidgeRegression", {"alpha": 1.0}),
    ("polynomial-regression", "PolynomialRegression", {"degree": 2}),
    ("lasso-regression", "LassoRegression", {"alpha": 0.02}),
    ("elastic-net", "ElasticNetRegression", {"alpha": 0.04, "l1_ratio": 0.5}),
    ("support-vector-regression", "SupportVectorRegression",
     {"C": 5.0, "epsilon": 0.05, "kernel": "rbf", "gamma": 0.5, "max_iter": 30000}),
    ("decision-tree-regression", "DecisionTreeRegression", {"max_depth": 4, "min_samples_leaf": 3}),
]


def metrics(y, prediction):
    return dict(mse=support.mse(y, prediction), mae=float(np.mean(np.abs(y-prediction))),
                r2=support.r2(y, prediction))


def main():
    rng = np.random.default_rng(13027)
    train = rng.uniform(-2, 2, size=(48, 2))
    test = rng.uniform(-2, 2, size=(24, 2))

    def response(X):
        return 1 + 0.8*X[:, 0] - 0.3*X[:, 1] + 0.25*X[:, 0]**2 + rng.normal(0, 0.08, len(X))

    y_train, y_test = response(train), response(test)
    mean, scale = train.mean(axis=0), train.std(axis=0)
    X_train, X_test = (train-mean)/scale, (test-mean)/scale
    results = []
    for topic, name, parameters in CASES:
        started = time.perf_counter()
        model = getattr(support.load(topic), name)(**parameters).fit(X_train, y_train)
        elapsed = time.perf_counter()-started
        results.append(dict(algorithm=topic, parameters=parameters, fit_seconds=elapsed,
                            train=metrics(y_train, model.predict(X_train)),
                            held_out=metrics(y_test, model.predict(X_test)),
                            n_iter=getattr(model, "n_iter_", None),
                            duality_gap=getattr(model, "duality_gap_", None),
                            kkt_violation=getattr(model, "kkt_violation_", None),
                            tree_depth=getattr(model, "depth_", None), tree_leaves=getattr(model, "n_leaves_", None)))
    print(json.dumps(dict(seed=13027, train_samples=48, held_out_samples=24, features=2,
                          response="1 + .8*x0 - .3*x1 + .25*x0**2 + Normal(0,.08)",
                          preprocessing=dict(fitted_on="training rows only", mean=mean.tolist(), scale=scale.tolist()),
                          hyperparameter_selection="Fixed in source; no tuning on held-out targets",
                          evaluation="One synthetic split; timings observational, no superiority claim",
                          results=results), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
