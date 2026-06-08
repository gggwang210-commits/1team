"""Create a beginner-friendly model evaluation report.

This script reads the baseline metrics saved by the training/evaluation step and
turns them into a Markdown report that teammates can read in GitHub or any text
editor.
"""

from pathlib import Path

import pandas as pd


# Keep file paths in one place so they are easy to update later.
BASELINE_METRICS_PATH = Path("reports/baseline_metrics.csv")
MODEL_EVALUATION_REPORT_PATH = Path("reports/model_evaluation.md")


# Human-readable explanations for common model evaluation metrics.
METRIC_EXPLANATIONS = {
    "Accuracy": (
        "Accuracy is the share of predictions the model got correct. "
        "Higher is usually better."
    ),
    "Log Loss": (
        "Log Loss checks how confident and correct the model's predicted probabilities are. "
        "Lower is better."
    ),
    "Brier Score": (
        "Brier Score measures how close predicted probabilities are to the true outcomes. "
        "Lower is better."
    ),
}


def load_metrics(path: Path) -> pd.DataFrame:
    """Load baseline metrics from a CSV file.

    Args:
        path: Location of the CSV file that contains model metrics.

    Returns:
        A pandas DataFrame containing the metrics.

    Raises:
        FileNotFoundError: If the expected metrics file does not exist.
    """
    # Check the file first so beginners get a clear error instead of a pandas
    # stack trace that can be hard to understand.
    if not path.exists():
        raise FileNotFoundError(
            "Could not find the baseline metrics file at "
            f"'{BASELINE_METRICS_PATH}'. Please run the baseline evaluation step "
            "first so this CSV is created."
        )

    # pandas reads the CSV into a table-like DataFrame for easy reporting.
    return pd.read_csv(path)


def _metrics_table_to_markdown(metrics_df: pd.DataFrame) -> str:
    """Convert metrics to a Markdown table, with a safe fallback."""
    # DataFrame.to_markdown needs the optional 'tabulate' package. If that
    # package is not installed, fall back to a plain text table so the report
    # can still be created.
    try:
        return metrics_df.to_markdown(index=False)
    except ImportError:
        return "```\n" + metrics_df.to_string(index=False) + "\n```"


def summarize_performance(metrics_df: pd.DataFrame) -> str:
    """Create a beginner-friendly Markdown summary of model performance.

    Args:
        metrics_df: DataFrame loaded from the baseline metrics CSV.

    Returns:
        Markdown text that includes the raw metrics table and simple notes.
    """
    # Start with a clear title and a short explanation of what the report shows.
    report_sections = [
        "# Model Evaluation Report",
        "",
        "This report summarizes the baseline model metrics from "
        f"`{BASELINE_METRICS_PATH}`.",
        "",
        "## Metrics Table",
        "",
        _metrics_table_to_markdown(metrics_df),
        "",
        "## Beginner-Friendly Interpretation",
        "",
    ]

    # Normalize column names so we can detect common metrics even if spacing or
    # capitalization is slightly different, such as 'log_loss' vs 'Log Loss'.
    normalized_columns = {
        column.strip().lower().replace("_", " "): column
        for column in metrics_df.columns
    }

    found_metric = False
    for metric_name, explanation in METRIC_EXPLANATIONS.items():
        normalized_metric_name = metric_name.lower()
        if normalized_metric_name in normalized_columns:
            found_metric = True
            original_column = normalized_columns[normalized_metric_name]
            values = metrics_df[original_column].dropna().tolist()
            latest_value = values[-1] if values else "No value available"
            report_sections.append(
                f"- **{metric_name}**: {explanation} Current value: `{latest_value}`."
            )

    # If common metric columns are missing, keep the raw table and explain what
    # happened instead of failing. This makes the script useful during early
    # project iterations when the CSV format may still be changing.
    if not found_metric:
        expected_columns = ", ".join(METRIC_EXPLANATIONS.keys())
        report_sections.append(
            "- Note: The expected metric columns were not found. Expected one or "
            f"more of: {expected_columns}. The raw metrics table is still shown above."
        )

    report_sections.extend(
        [
            "",
            "## How to Read This Report",
            "",
            "- Use this baseline as the comparison point for future model improvements.",
            "- When improving the model, compare the same metrics before and "
            "after changes.",
            "- For Accuracy, higher usually means better classification performance.",
            "- For Log Loss and Brier Score, lower usually means better "
            "probability estimates.",
            "",
        ]
    )

    # Join every section with new lines to produce one Markdown document.
    return "\n".join(report_sections)


def save_markdown_report(markdown: str, output_path: Path) -> None:
    """Save Markdown text to a file.

    Args:
        markdown: Complete Markdown report text.
        output_path: File path where the report should be written.
    """
    # Create the reports folder if it does not exist yet.
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write text with UTF-8 so symbols and non-English text are handled safely.
    output_path.write_text(markdown, encoding="utf-8")


def main() -> None:
    """Load metrics, build the report, and save it to the reports folder."""
    # Step 1: Read the baseline metrics CSV.
    metrics_df = load_metrics(BASELINE_METRICS_PATH)

    # Step 2: Convert the metrics table into a beginner-friendly Markdown report.
    markdown_report = summarize_performance(metrics_df)

    # Step 3: Save the report so teammates can review it later.
    save_markdown_report(markdown_report, MODEL_EVALUATION_REPORT_PATH)


if __name__ == "__main__":
    main()
