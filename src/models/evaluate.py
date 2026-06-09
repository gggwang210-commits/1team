"""Create a human-readable MVP model evaluation report.

The training step writes machine-readable metrics to ``reports/baseline_metrics.csv``.
This module turns those metrics into ``reports/model_evaluation.md`` so teammates
can quickly understand the current baseline model quality and limitations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

# Keeping project paths centralized makes the data flow easier to follow:
# training -> baseline_metrics.csv -> markdown evaluation summary.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = PROJECT_ROOT / "reports"
BASELINE_METRICS_PATH = REPORTS_DIR / "baseline_metrics.csv"
PREDICTION_TABLE_PATH = REPORTS_DIR / "prediction_table.csv"
EVALUATION_REPORT_PATH = REPORTS_DIR / "model_evaluation.md"

REQUIRED_METRIC_COLUMNS = ("accuracy", "macro_f1")
OPTIONAL_SPLIT_COLUMN = "split_method"
OPTIONAL_MODEL_COLUMN = "model"
OPTIONAL_FEATURE_SET_COLUMN = "feature_set"


def read_required_csv(path: Path, description: str) -> pd.DataFrame:
    """Read a required CSV file and raise clear errors for common failures."""
    if not path.exists():
        raise FileNotFoundError(
            f"Required {description} file is missing: {path}. "
            "Run the baseline training step before model evaluation."
        )

    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"Required {description} file is empty: {path}.")
    return df


def read_optional_csv(path: Path) -> pd.DataFrame | None:
    """Read an optional CSV file when it exists; otherwise continue safely."""
    if not path.exists():
        return None

    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"Optional prediction table exists but is empty: {path}.")
    return df


def validate_metrics(metrics_df: pd.DataFrame) -> None:
    """Ensure the metrics table contains values needed for MVP evaluation."""
    missing_columns = [
        column for column in REQUIRED_METRIC_COLUMNS if column not in metrics_df.columns
    ]
    if missing_columns:
        raise ValueError(
            "baseline_metrics.csv is missing required column(s): "
            f"{', '.join(missing_columns)}. Expected Accuracy and Macro F1 metrics."
        )

    for column in REQUIRED_METRIC_COLUMNS:
        if metrics_df[column].isna().any():
            raise ValueError(
                f"baseline_metrics.csv contains missing values in '{column}'."
            )


def get_best_metric_row(metrics_df: pd.DataFrame) -> pd.Series:
    """Select the strongest baseline row using Macro F1 first, then Accuracy.

    Macro F1 is prioritized because Win/Draw/Loss classes can be imbalanced; it
    gives each class equal weight instead of letting the most common class hide
    poor minority-class performance.
    """
    sortable_metrics = metrics_df.copy()
    sortable_metrics["accuracy"] = pd.to_numeric(sortable_metrics["accuracy"])
    sortable_metrics["macro_f1"] = pd.to_numeric(sortable_metrics["macro_f1"])
    sorted_metrics = sortable_metrics.sort_values(
        by=["macro_f1", "accuracy"], ascending=False
    )
    return sorted_metrics.iloc[0]


def format_metric(value: Any) -> str:
    """Format metric values consistently for non-technical report readers."""
    return f"{float(value):.4f}"


def build_metrics_table(metrics_df: pd.DataFrame) -> str:
    """Build a compact markdown table with model, Accuracy, and Macro F1."""
    display_columns = [
        column
        for column in (
            OPTIONAL_MODEL_COLUMN,
            OPTIONAL_FEATURE_SET_COLUMN,
            *REQUIRED_METRIC_COLUMNS,
        )
        if column in metrics_df.columns
    ]
    display_df = metrics_df[display_columns].copy()

    for column in REQUIRED_METRIC_COLUMNS:
        display_df[column] = display_df[column].map(format_metric)

    # Avoid pandas.to_markdown so the script does not require the optional
    # ``tabulate`` package in lightweight MVP environments.
    headers = [column.replace("_", " ").title() for column in display_columns]
    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"
    body_rows = [
        "| " + " | ".join(str(row[column]) for column in display_columns) + " |"
        for _, row in display_df.iterrows()
    ]
    return "\n".join([header_row, separator_row, *body_rows])


def build_prediction_summary(prediction_df: pd.DataFrame | None) -> str:
    """Summarize the optional prediction output without making claims from it."""
    if prediction_df is None:
        return (
            "## Prediction Table\n\n"
            "`reports/prediction_table.csv` was not found, so no prediction-table "
            "summary was included. This file is optional for evaluation.\n"
        )

    return (
        "## Prediction Table\n\n"
        f"- Source: `reports/prediction_table.csv`\n"
        f"- Rows: {len(prediction_df)}\n"
        f"- Columns: {', '.join(prediction_df.columns)}\n"
    )


def build_markdown_report(
    metrics_df: pd.DataFrame,
    prediction_df: pd.DataFrame | None,
) -> str:
    """Create the final markdown report content."""
    validate_metrics(metrics_df)
    best_row = get_best_metric_row(metrics_df)

    model_label = best_row.get(OPTIONAL_MODEL_COLUMN, "Best baseline row")
    feature_set = best_row.get(OPTIONAL_FEATURE_SET_COLUMN)
    split_method = best_row.get(OPTIONAL_SPLIT_COLUMN)

    feature_set_line = ""
    if pd.notna(feature_set):
        feature_set_line = f"- Feature set: `{feature_set}`\n"

    split_section = ""
    if pd.notna(split_method):
        split_section = f"\n## Split Method\n\n- `{split_method}`\n"

    return (
        "# Model Evaluation Summary\n\n"
        "This report summarizes the MVP baseline model metrics produced by "
        "`reports/baseline_metrics.csv`.\n\n"
        "## Best Baseline Metrics\n\n"
        f"- Model: `{model_label}`\n"
        f"{feature_set_line}"
        f"- Accuracy: **{format_metric(best_row['accuracy'])}**\n"
        f"- Macro F1: **{format_metric(best_row['macro_f1'])}**\n"
        f"{split_section}\n"
        "## All Baseline Metrics\n\n"
        f"{build_metrics_table(metrics_df)}\n\n"
        f"{build_prediction_summary(prediction_df)}\n"
        "## Limitations\n\n"
        "These MVP metrics are preliminary and depend on dataset quality, "
        "feature coverage, labeling consistency, and the representativeness of "
        "the train/test split. The `with_team_identifiers` feature set can "
        "overstate performance on tiny demo data because team-name columns may "
        "encourage memorization. Metrics should not be treated as production-ready "
        "performance claims or as a substitute for deeper validation and data "
        "governance review.\n"
    )


def write_evaluation_report(
    metrics_path: Path = BASELINE_METRICS_PATH,
    prediction_table_path: Path = PREDICTION_TABLE_PATH,
    output_path: Path = EVALUATION_REPORT_PATH,
) -> Path:
    """Read evaluation inputs and write ``model_evaluation.md``."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    metrics_df = read_required_csv(metrics_path, "baseline metrics")
    prediction_df = read_optional_csv(prediction_table_path)
    markdown = build_markdown_report(metrics_df, prediction_df)

    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def main() -> None:
    """Run the MVP model evaluation report workflow."""
    output_path = write_evaluation_report()
    print(f"Model evaluation report saved to: {output_path}")


if __name__ == "__main__":
    main()
