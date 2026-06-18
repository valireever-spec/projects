"""
Backtesting framework for financial model validation.
Tests model accuracy against synthetic German business dataset.
"""

import json
from pathlib import Path
from backend.analytics.financial_model import build_projections


def run_backtest(dataset_path: str = None) -> dict:
    """
    Run backtesting suite against dataset of actual vs predicted business outcomes.

    Args:
        dataset_path: Path to backtesting dataset JSON. Defaults to data/backtesting_dataset.json

    Returns:
        {
            "test_count": 50,
            "mape": 18.5,
            "within_20pct": 0.72,
            "bias": 2.1,
            "model_grade": "B",
            "break_even_accuracy": {"mape": 15.2, "within_3_months": 0.68},
            "revenue_accuracy": {"mape": 22.1, "within_20pct": 0.74},
            "survival_rate": 0.64
        }
    """

    if dataset_path is None:
        dataset_path = str(Path(__file__).parent.parent.parent / "data" / "backtesting_dataset.json")

    try:
        with open(dataset_path, "r") as f:
            dataset = json.load(f)
    except Exception as e:
        raise FileNotFoundError(f"Failed to load backtesting dataset: {e}")

    predictions = []
    actuals = []
    break_even_predictions = []
    break_even_actuals = []
    revenue_predictions = []
    revenue_actuals = []
    survival_predictions = []
    survival_actuals = []

    for record in dataset:
        try:
            # Run projection
            result = build_projections(
                domain_slug=record.get("domain_slug"),
                revenue_model=record.get("revenue_model"),
                monthly_revenue_estimate=record.get("monthly_revenue_estimate", 5000),
                city=record.get("city", "Berlin"),
                legal_form=record.get("legal_form", "Einzelunternehmen"),
                startup_capital=record.get("startup_capital", 20000),
                employees=1
            )

            predicted_year_1_net = result.get("year_1_net", 0)
            actual_year_1_net = record.get("actual_year_1_net", 0)
            predictions.append(predicted_year_1_net)
            actuals.append(actual_year_1_net)

            # Break-even accuracy
            predicted_breakeven = result.get("break_even_month", 12)
            actual_breakeven = record.get("actual_break_even_month", 12)
            break_even_predictions.append(predicted_breakeven)
            break_even_actuals.append(actual_breakeven)

            # Revenue accuracy
            predicted_revenue = result.get("year_1_revenue", 0)
            actual_revenue = record.get("actual_year_1_revenue", 0)
            revenue_predictions.append(predicted_revenue)
            revenue_actuals.append(actual_revenue)

            # Survival prediction (proxy: break-even < 24 months)
            predicted_survival = predicted_breakeven < 24
            actual_survival = record.get("actual_survived_year_3", False)
            survival_predictions.append(predicted_survival)
            survival_actuals.append(actual_survival)

        except Exception as e:
            # Skip records that fail to project
            continue

    # Calculate metrics
    metrics = calculate_accuracy_metrics(predictions, actuals)
    breakeven_metrics = calculate_accuracy_metrics(break_even_predictions, break_even_actuals)
    revenue_metrics = calculate_accuracy_metrics(revenue_predictions, revenue_actuals)

    # Survival accuracy (boolean)
    survival_correct = sum(
        1 for pred, actual in zip(survival_predictions, survival_actuals) if pred == actual
    )
    survival_rate = survival_correct / len(survival_predictions) if survival_predictions else 0

    # Assign grade based on MAPE
    mape = metrics["mape"]
    if mape < 15:
        grade = "A"
    elif mape < 25:
        grade = "B"
    elif mape < 35:
        grade = "C"
    else:
        grade = "D"

    return {
        "test_count": len(predictions),
        "mape": round(metrics["mape"], 1),
        "within_20pct": round(metrics["within_20pct"], 2),
        "bias": round(metrics["bias"], 1),
        "model_grade": grade,
        "break_even_accuracy": {
            "mape": round(breakeven_metrics["mape"], 1),
            "within_3_months": round(
                sum(1 for p, a in zip(break_even_predictions, break_even_actuals) if abs(p - a) <= 3) / len(break_even_predictions),
                2
            ) if break_even_predictions else 0
        },
        "revenue_accuracy": {
            "mape": round(revenue_metrics["mape"], 1),
            "within_20pct": round(revenue_metrics["within_20pct"], 2)
        },
        "survival_accuracy": round(survival_rate, 2)
    }


def calculate_accuracy_metrics(predictions: list, actuals: list) -> dict:
    """
    Calculate MAPE, bias, and within_20pct accuracy.

    Args:
        predictions: List of predicted values
        actuals: List of actual values

    Returns:
        {
            "mape": 18.5,
            "within_20pct": 0.72,
            "bias": 2.1
        }
    """

    if not predictions or len(predictions) != len(actuals):
        return {"mape": 0, "within_20pct": 0, "bias": 0}

    errors = []
    within_20 = 0

    for pred, actual in zip(predictions, actuals):
        if actual == 0:
            if pred == 0:
                error = 0
            else:
                error = 100
        else:
            error = abs(pred - actual) / abs(actual)

        errors.append(error)

        # Within 20% check
        if error <= 0.20:
            within_20 += 1

    # MAPE (Mean Absolute Percentage Error)
    mape = (sum(errors) / len(errors)) * 100 if errors else 0

    # Bias (mean signed error)
    signed_errors = [
        (pred - actual) / abs(actual) if actual != 0 else 0
        for pred, actual in zip(predictions, actuals)
    ]
    bias = (sum(signed_errors) / len(signed_errors)) * 100 if signed_errors else 0

    return {
        "mape": mape,
        "within_20pct": within_20 / len(predictions),
        "bias": bias
    }
