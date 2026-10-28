"""Independent numerical scoring checks added during the B1 completion audit."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest
from sklearn.metrics import mean_absolute_error, mean_squared_error, root_mean_squared_error, r2_score

spec = importlib.util.spec_from_file_location("regression_metric_audit", Path(__file__).parents[1]/"support.py")
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)

pytestmark = [pytest.mark.ml, pytest.mark.numerical]


def test_nonconstant_r2_does_not_square_tiny_targets_before_taking_ratio():
    # Same ratio as [2,4,6] versus [1,3,5]: 1 - 3/8 = 5/8.
    assert support.r2([2e-200, 4e-200, 6e-200], [1e-200, 3e-200, 5e-200]) == pytest.approx(.625)


@pytest.mark.parametrize("level", [0.1, 1e-200])
def test_constant_target_convention_uses_actual_equality(level):
    assert support.r2([level]*3, [0.0]*3) == 0
    assert support.r2([level]*3, [level]*3) == 1


def test_finite_mean_squared_error_survives_overflowing_individual_square():
    prediction = np.zeros(2048)
    prediction[0] = 1e155
    # Its square overflows, but dividing before the final square is representable.
    expected = (1e155/np.sqrt(2048.0))**2
    assert support.mse(np.zeros(2048), prediction) == pytest.approx(expected)


@pytest.mark.reference
def test_seeded_metric_values_match_independent_reference_at_resolved_scale():
    rng = np.random.default_rng(13311)
    for n in (1, 7, 41):
        y = rng.normal(size=n)
        prediction = y + rng.normal(scale=.3, size=n)
        result = support.regression_metrics(y, prediction)
        assert result["mse"] == pytest.approx(mean_squared_error(y, prediction), rel=1e-13)
        assert result["rmse"] == pytest.approx(root_mean_squared_error(y, prediction), rel=1e-13)
        assert result["mae"] == pytest.approx(mean_absolute_error(y, prediction), rel=1e-13)
        if n > 1:
            assert result["r2"] == pytest.approx(r2_score(y, prediction), rel=1e-12, abs=1e-14)
        else:
            assert result["r2"] == 0  # documented single-observation constant convention


def test_rmse_keeps_tiny_units_when_final_mse_cannot_be_represented():
    with np.errstate(all="raise"):
        result = support.regression_metrics([2e-200, 4e-200, 6e-200], [1e-200, 3e-200, 5e-200])
    assert result["mse"] == 0
    assert result["rmse"] == pytest.approx(1e-200, rel=1e-13, abs=0)
    assert result["mae"] == pytest.approx(1e-200, rel=1e-13, abs=0)
    assert result["r2"] == pytest.approx(.625)


def test_large_finite_rmse_mae_and_explicit_unrepresentable_mse():
    assert support.rmse([0., 0., 0., 0.], [1e308, 0., 0., 0.]) == pytest.approx(5e307)
    assert support.mae([0., 0., 0., 0.], [1e308, 0., 0., 0.]) == pytest.approx(2.5e307)
    with pytest.raises(ValueError, match="numerical"):
        support.mse([0., 0.], [1e308, 1e308])


@pytest.mark.parametrize("name,cls", [("linear-regression", "LinearRegression"), ("ridge-regression", "RidgeRegression"),
    ("lasso-regression", "LassoRegression"), ("elastic-net", "ElasticNetRegression"),
    ("polynomial-regression", "PolynomialRegression"), ("support-vector-regression", "SupportVectorRegression"),
    ("decision-tree-regression", "DecisionTreeRegression")])
def test_every_estimator_score_obeys_tiny_constant_target_convention(name, cls):
    X = [[-1.], [0.], [1.]]
    model = getattr(support.load(name), cls)().fit(X, [0., 0., 0.])
    assert model.score(X, [1e-200]*3) == 0


@pytest.mark.parametrize("metric", [support.mse, support.rmse, support.mae, support.r2, support.regression_metrics])
@pytest.mark.parametrize("y,prediction", [([], []), ([[1], [2]], [1, 2]), ([1], [[1]]),
    ([1], [np.nan]), ([1], [np.inf]), ([1], [True]), ([1], ["1"]), ([1], [1j]), ([1, 2], [1])])
def test_metric_input_domains_are_explicit(metric, y, prediction):
    with pytest.raises(ValueError):
        metric(y, prediction)
