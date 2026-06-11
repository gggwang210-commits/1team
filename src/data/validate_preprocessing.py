"""Validate preprocessing outputs before model training or simulation.

This script is a preprocessing gate. It verifies that the basic data-building and
feature-engineering outputs are present, readable, non-empty, and safe enough to
use in later modeling/simulation steps.

It does not train models and does not create model artifacts.

Default behavior validates both paths:
- Korea MVP: data/processed/matches.csv and data/processed/features.csv
- Global expansion: data/processed/matches_global.csv and data/processed/features_global.csv

Generated outputs:
- reports/preprocessing_validation.md
- reports/preprocessing_validation.csv
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"

KOREA_MATCHES_PATH = PROCESSED_DIR / "matches.csv"
KOREA_FEATURES_PATH = PROCESSED_DIR / "features.csv"
GLOBAL_MATCHES_PATH = PROCESSED_DIR / "matches_global.csv"
GLOBAL_FEATURES_PATH = PROCESSED_DIR / "features_global.csv"

VALIDATION_MD_PATH = REPORTS_DIR / "preprocessing_validation.md"
VALIDATION_CSV_PATH = REPORTS_DIR / "preprocessing_validation.csv"

KOREA_TEAM_NAME = "Korea Republic"
TARGET_COLUMN = "target_result"
KOREA_TARGET_COLUMN = "target_result_korea_perspective"
SOURCE_TARGET_COLUMN = "source_target_column"
SOURCE_TARGET_SCOPE = "source_target_scope"
ALLOWED_TARGET_VALUES = {"Win", "Draw", "Loss"}
SCORE_COLUMNS = {"home_score", "away_score"}


def _read_csv(path: Path) -> pd.DataFrame:
    """Read a CSV with a friendly error if the file is missing or unreadable."""
    if not path.exists():
        raise FileNotFoundError(f"Required preprocessing output not found: {path}")
    try:
        return pd.read_csv(path)
    except Exception as exc:  # pragma: no cover - user-facing defensive message
        raise ValueError(f"Failed to read CSV file: {path}. Error: {exc}") from exc


def _format_markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    """Return a small dependency-free Markdown table."""
    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join("---" for _ in headers) + " |"
    data_rows = ["| " + " | ".join(str(value) for value in row) + " |" for row in rows]
    return "\n".join([header_row, separator_row, *data_rows])


def _add_result(
    results: list[dict[str, Any]],
    scope: str,
    artifact: str,
    check_name: str,
    passed: bool,
    detail: str,
) -> None:
    """Append one validation result row."""
    results.append(
        {
            "scope": scope,
            "artifact": artifact,
            "check_name": check_name,
            "status": "PASS" if passed else "FAIL",
            "detail": detail,
        }
    )


def _check_required_columns(
    df: pd.DataFrame,
    required_columns: set[str],
    scope: str,
    artifact: str,
    results: list[dict[str, Any]],
) -> None:
    missing = sorted(required_columns - set(df.columns))
    _add_result(
        results,
        scope,
        artifact,
        "required_columns",
        not missing,
        "All required columns are present." if not missing else f"Missing columns: {missing}",
    )


def _check_non_empty(
    df: pd.DataFrame,
    scope: str,
    artifact: str,
    results: list[dict[str, Any]],
) -> None:
    _add_result(
        results,
        scope,
        artifact,
        "non_empty",
        not df.empty,
        f"Rows: {len(df)}, Columns: {len(df.columns)}",
    )


def _check_no_missing(
    df: pd.DataFrame,
    columns: list[str],
    scope: str,
    artifact: str,
    results: list[dict[str, Any]],
) -> None:
    available_columns = [column for column in columns if column in df.columns]
    missing_counts = {
        column: int(df[column].isna().sum())
        for column in available_columns
        if int(df[column].isna().sum()) > 0
    }
    _add_result(
        results,
        scope,
        artifact,
        "no_missing_required_values",
        not missing_counts,
        "No missing values in required columns."
        if not missing_counts
        else f"Missing counts: {missing_counts}",
    )


def _check_duplicate_rows(
    df: pd.DataFrame,
    scope: str,
    artifact: str,
    results: list[dict[str, Any]],
) -> None:
    duplicate_count = int(df.duplicated().sum())
    _add_result(
        results,
        scope,
        artifact,
        "no_duplicate_rows",
        duplicate_count == 0,
        f"Duplicate rows: {duplicate_count}",
    )


def _check_target_values(
    df: pd.DataFrame,
    target_column: str,
    scope: str,
    artifact: str,
    results: list[dict[str, Any]],
) -> None:
    if target_column not in df.columns:
        _add_result(results, scope, artifact, f"{target_column}_values", False, "Target column is missing.")
        return

    observed = set(df[target_column].dropna().astype(str).str.strip().unique())
    invalid = sorted(observed - ALLOWED_TARGET_VALUES)
    _add_result(
        results,
        scope,
        artifact,
        f"{target_column}_values",
        not invalid,
        f"Observed values: {sorted(observed)}" if not invalid else f"Invalid target values: {invalid}",
    )


def _check_korea_scope_matches(
    matches: pd.DataFrame,
    scope: str,
    results: list[dict[str, Any]],
) -> None:
    if not {"home_team", "away_team"}.issubset(matches.columns):
        _add_result(results, scope, "matches", "korea_scope_only", False, "home_team/away_team columns are missing.")
        return

    home = matches["home_team"].astype(str).str.strip()
    away = matches["away_team"].astype(str).str.strip()
    non_korea_count = int((~((home == KOREA_TEAM_NAME) | (away == KOREA_TEAM_NAME))).sum())
    _add_result(
        results,
        scope,
        "matches",
        "korea_scope_only",
        non_korea_count == 0,
        f"Non-Korea rows in MVP matches: {non_korea_count}",
    )


def _check_feature_score_leakage(
    features: pd.DataFrame,
    scope: str,
    results: list[dict[str, Any]],
) -> None:
    leaked_columns = sorted(SCORE_COLUMNS & set(features.columns))
    _add_result(
        results,
        scope,
        "features",
        "no_score_leakage_columns",
        not leaked_columns,
        "No final-score columns in features." if not leaked_columns else f"Leaked score columns: {leaked_columns}",
    )


def _check_feature_target_scope(
    features: pd.DataFrame,
    expected_scope: str,
    scope: str,
    results: list[dict[str, Any]],
) -> None:
    if SOURCE_TARGET_SCOPE not in features.columns:
        _add_result(results, scope, "features", "source_target_scope", False, "source_target_scope column is missing.")
        return

    observed = sorted(features[SOURCE_TARGET_SCOPE].dropna().astype(str).unique())
    passed = observed == [expected_scope]
    _add_result(
        results,
        scope,
        "features",
        "source_target_scope",
        passed,
        f"Observed source_target_scope values: {observed}; expected: {expected_scope}",
    )


def _check_feature_columns_match_model_contract(
    features: pd.DataFrame,
    scope: str,
    results: list[dict[str, Any]],
) -> None:
    required = {"date", "home_team", "away_team", TARGET_COLUMN, SOURCE_TARGET_COLUMN, SOURCE_TARGET_SCOPE}
    missing = sorted(required - set(features.columns))
    _add_result(
        results,
        scope,
        "features",
        "feature_model_contract_columns",
        not missing,
        "Feature table has model contract columns." if not missing else f"Missing feature contract columns: {missing}",
    )


def validate_scope(
    scope: str,
    matches_path: Path,
    features_path: Path,
    expected_target_scope: str,
    require_korea_only_matches: bool,
) -> list[dict[str, Any]]:
    """Validate one preprocessing scope and return detailed check rows."""
    results: list[dict[str, Any]] = []
    matches = _read_csv(matches_path)
    features = _read_csv(features_path)

    _check_non_empty(matches, scope, "matches", results)
    _check_non_empty(features, scope, "features", results)

    _check_required_columns(
        matches,
        {"date", "home_team", "away_team", "home_score", "away_score", TARGET_COLUMN},
        scope,
        "matches",
        results,
    )
    _check_required_columns(
        features,
        {"date", "home_team", "away_team", TARGET_COLUMN, SOURCE_TARGET_COLUMN, SOURCE_TARGET_SCOPE},
        scope,
        "features",
        results,
    )

    _check_no_missing(matches, ["date", "home_team", "away_team", "home_score", "away_score", TARGET_COLUMN], scope, "matches", results)
    _check_no_missing(features, ["date", "home_team", "away_team", TARGET_COLUMN, SOURCE_TARGET_COLUMN, SOURCE_TARGET_SCOPE], scope, "features", results)

    _check_duplicate_rows(matches, scope, "matches", results)
    _check_duplicate_rows(features, scope, "features", results)

    _check_target_values(matches, TARGET_COLUMN, scope, "matches", results)
    _check_target_values(features, TARGET_COLUMN, scope, "features", results)
    _check_feature_score_leakage(features, scope, results)
    _check_feature_target_scope(features, expected_target_scope, scope, results)
    _check_feature_columns_match_model_contract(features, scope, results)

    if require_korea_only_matches:
        _check_required_columns(matches, {KOREA_TARGET_COLUMN}, scope, "matches", results)
        _check_target_values(matches, KOREA_TARGET_COLUMN, scope, "matches", results)
        _check_no_missing(matches, [KOREA_TARGET_COLUMN], scope, "matches", results)
        _check_korea_scope_matches(matches, scope, results)

    return results


def write_validation_reports(results: list[dict[str, Any]]) -> None:
    """Write machine-readable and human-readable preprocessing validation reports."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    results_df = pd.DataFrame(results, columns=["scope", "artifact", "check_name", "status", "detail"])
    results_df.to_csv(VALIDATION_CSV_PATH, index=False)

    failed = results_df[results_df["status"] == "FAIL"]
    summary_rows = [
        ["Total checks", len(results_df)],
        ["Passed checks", int((results_df["status"] == "PASS").sum())],
        ["Failed checks", len(failed)],
    ]
    detail_rows = results_df.values.tolist()

    sections = [
        "# Preprocessing Validation Report",
        "",
        "This file is generated by `python src/data/validate_preprocessing.py`.",
        "It should be reviewed before model training, calibration, or tournament simulation.",
        "",
        "## Run Metadata",
        "",
        f"- Run timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "## Summary",
        "",
        _format_markdown_table(["Metric", "Value"], summary_rows),
        "",
        "## Detailed Checks",
        "",
        _format_markdown_table(["Scope", "Artifact", "Check", "Status", "Detail"], detail_rows),
        "",
    ]
    if not failed.empty:
        sections.extend(
            [
                "## Required Action",
                "",
                "One or more preprocessing checks failed. Fix the failing rows before continuing to model training or simulation.",
                "",
            ]
        )
    else:
        sections.extend(
            [
                "## Result",
                "",
                "All preprocessing checks passed for the selected scope(s).",
                "",
            ]
        )

    VALIDATION_MD_PATH.write_text("\n".join(sections), encoding="utf-8")
    print(f"Saved preprocessing validation CSV to: {VALIDATION_CSV_PATH}")
    print(f"Saved preprocessing validation report to: {VALIDATION_MD_PATH}")


def validate_preprocessing(scope: str = "both") -> list[dict[str, Any]]:
    """Validate preprocessing outputs for korea, global, or both scopes."""
    selected_results: list[dict[str, Any]] = []
    if scope in {"korea", "both"}:
        selected_results.extend(
            validate_scope(
                scope="korea_mvp",
                matches_path=KOREA_MATCHES_PATH,
                features_path=KOREA_FEATURES_PATH,
                expected_target_scope="korea",
                require_korea_only_matches=True,
            )
        )
    if scope in {"global", "both"}:
        selected_results.extend(
            validate_scope(
                scope="global_expansion",
                matches_path=GLOBAL_MATCHES_PATH,
                features_path=GLOBAL_FEATURES_PATH,
                expected_target_scope="home",
                require_korea_only_matches=False,
            )
        )

    write_validation_reports(selected_results)
    failed = [result for result in selected_results if result["status"] == "FAIL"]
    if failed:
        print(f"Preprocessing validation failed with {len(failed)} failed check(s).")
        raise SystemExit(1)

    print("Preprocessing validation passed.")
    return selected_results


def parse_args() -> argparse.Namespace:
    """Parse command-line options for preprocessing validation."""
    parser = argparse.ArgumentParser(description="Validate preprocessing outputs before modeling.")
    parser.add_argument(
        "--scope",
        choices=("korea", "global", "both"),
        default="both",
        help="Choose which preprocessing output scope to validate. Default: both.",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entry point for preprocessing validation."""
    args = parse_args()
    validate_preprocessing(scope=args.scope)


if __name__ == "__main__":
    main()
