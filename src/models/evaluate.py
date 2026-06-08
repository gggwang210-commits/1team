"""Model evaluation helpers for the MVP.

This starter file will calculate Accuracy, Log Loss, Brier Score, and summary
reports in a later implementation step.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASELINE_METRICS_PATH = PROJECT_ROOT / "reports" / "baseline_metrics.csv"


def load_baseline_metrics(metrics_path: str | Path = BASELINE_METRICS_PATH) -> pd.DataFrame:
    """Load saved baseline evaluation metrics."""

    metrics_path = Path(metrics_path)
    # Check first so new users get a clear next step instead of a pandas error.
    if not metrics_path.exists():
        raise FileNotFoundError(
            "Missing reports/baseline_metrics.csv. "
            "Run the baseline training/evaluation pipeline first."
        )

    return pd.read_csv(metrics_path)


# TODO: Implement baseline evaluation metrics and reporting.
