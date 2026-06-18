"""
Unit tests for backtester.py
"""

import pytest
from backend.analytics.backtester import run_backtest, calculate_accuracy_metrics


def test_backtest_loads_dataset():
    """run_backtest should load and process dataset"""
    result = run_backtest()

    assert result["test_count"] > 0
    assert "mape" in result
    assert "within_20pct" in result
    assert "bias" in result
    assert "model_grade" in result


def test_mape_is_positive():
    """MAPE should be a positive number"""
    result = run_backtest()

    assert isinstance(result["mape"], (int, float))
    assert result["mape"] >= 0


def test_within_20pct_is_0_to_1():
    """within_20pct should be between 0 and 1"""
    result = run_backtest()

    assert isinstance(result["within_20pct"], (int, float))
    assert 0 <= result["within_20pct"] <= 1


def test_bias_can_be_positive_or_negative():
    """Bias can be positive (over-predict) or negative (under-predict)"""
    result = run_backtest()

    assert isinstance(result["bias"], (int, float))
    # No constraint on sign


def test_model_grade_is_valid():
    """Model grade should be A, B, C, or D"""
    result = run_backtest()

    assert result["model_grade"] in ["A", "B", "C", "D"]


def test_grade_thresholds():
    """Verify grade assignment thresholds"""
    # MAPE < 15 → A
    # MAPE < 25 → B
    # MAPE < 35 → C
    # MAPE ≥ 35 → D

    result = run_backtest()
    mape = result["mape"]

    if mape < 15:
        assert result["model_grade"] == "A"
    elif mape < 25:
        assert result["model_grade"] == "B"
    elif mape < 35:
        assert result["model_grade"] == "C"
    else:
        assert result["model_grade"] == "D"


def test_accuracy_metrics_basic():
    """calculate_accuracy_metrics should return dict with required keys"""
    predictions = [100, 200, 300]
    actuals = [100, 180, 320]

    result = calculate_accuracy_metrics(predictions, actuals)

    assert "mape" in result
    assert "within_20pct" in result
    assert "bias" in result


def test_mape_calculation():
    """Test MAPE calculation with known values"""
    predictions = [100]
    actuals = [100]

    result = calculate_accuracy_metrics(predictions, actuals)
    # 0% error = 0 MAPE
    assert result["mape"] == 0


def test_within_20pct_count():
    """Test within_20pct calculation"""
    predictions = [100, 100]
    actuals = [100, 150]  # First is 0% error, second is 33% error

    result = calculate_accuracy_metrics(predictions, actuals)
    # 1 out of 2 within 20% = 0.5
    assert result["within_20pct"] == 0.5


def test_bias_positive_overprediction():
    """Test bias with overprediction"""
    predictions = [120]
    actuals = [100]

    result = calculate_accuracy_metrics(predictions, actuals)
    # Bias should be positive (over-predicting)
    assert result["bias"] > 0


def test_bias_negative_underprediction():
    """Test bias with underprediction"""
    predictions = [80]
    actuals = [100]

    result = calculate_accuracy_metrics(predictions, actuals)
    # Bias should be negative (under-predicting)
    assert result["bias"] < 0


def test_empty_lists_handled():
    """Empty prediction/actual lists should be handled gracefully"""
    predictions = []
    actuals = []

    result = calculate_accuracy_metrics(predictions, actuals)

    assert result["mape"] == 0
    assert result["within_20pct"] == 0
    assert result["bias"] == 0


def test_break_even_accuracy_in_result(base_path=None):
    """Result should include break_even_accuracy metrics"""
    result = run_backtest()

    assert "break_even_accuracy" in result
    assert "mape" in result["break_even_accuracy"]
    assert "within_3_months" in result["break_even_accuracy"]


def test_revenue_accuracy_in_result():
    """Result should include revenue_accuracy metrics"""
    result = run_backtest()

    assert "revenue_accuracy" in result
    assert "mape" in result["revenue_accuracy"]
    assert "within_20pct" in result["revenue_accuracy"]


def test_survival_accuracy_in_result():
    """Result should include survival_accuracy metric"""
    result = run_backtest()

    assert "survival_accuracy" in result
    assert 0 <= result["survival_accuracy"] <= 1
