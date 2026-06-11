"""Build the match dataset used by feature engineering.

Data flow for beginners:
1. Prefer real raw CSV files in ``data/raw`` when they use common football
   results columns such as ``date``, ``home_team``, and ``away_team``.
2. If raw data is not available yet, create a small but trainable demo dataset.
3. Save the standardized match table to ``data/processed/matches.csv``.

Default behavior preserves the Korea Republic MVP scope. Expansion work can call
``build_dataset(filter_korea=False)`` or run this script with ``--global-scope``
to keep all compatible international rows.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MATCHES_PATH = PROCESSED_DIR / "matches.csv"
REPORTS_DIR = PROJECT_ROOT / "reports"
DATA_QUALITY_SUMMARY_PATH = REPORTS_DIR / "data_quality_summary.md"

REQUIRED_MATCH_COLUMNS = {"date", "home_team", "away_team", "home_score", "away_score"}
KOREA_TEAM_NAME = "Korea Republic"
KOREA_TARGET_COLUMN = "target_result_korea_perspective"
TARGET_COLUMNS = ("target_result", KOREA_TARGET_COLUMN)

# Common alternative names found in public international-football datasets.
COLUMN_ALIASES = {
    "home": "home_team",
    "away": "away_team",
    "home_goals": "home_score",
    "away_goals": "away_score",
    "home_team_score": "home_score",
    "away_team_score": "away_score",
    "neutral_site": "neutral",
}


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names so later pipeline steps can be predictable."""
    standardized = df.copy()
    standardized.columns = [
        column.strip().lower().replace(" ", "_") for column in standardized.columns
    ]
    standardized = standardized.rename(columns=COLUMN_ALIASES)
    return standardized


def _add_home_perspective_target(df: pd.DataFrame) -> pd.DataFrame:
    """Create a three-class result label from the home team's perspective."""
    labeled = df.copy()
    labeled["home_score"] = pd.to_numeric(labeled["home_score"], errors="coerce")
    labeled["away_score"] = pd.to_numeric(labeled["away_score"], errors="coerce")

    labeled["target_result"] = "Draw"
    home_wins = labeled["home_score"] > labeled["away_score"]
    home_losses = labeled["home_score"] < labeled["away_score"]
    labeled.loc[home_wins, "target_result"] = "Win"
    labeled.loc[home_losses, "target_result"] = "Loss"
    return labeled


def _add_korea_perspective_target(df: pd.DataFrame, require_all_rows: bool) -> pd.DataFrame:
    """Add Korea Republic perspective labels where Korea is in the match.

    The MVP uses this as its business target. In global expansion mode, non-Korea
    rows are allowed and keep this audit column empty.
    """
    labeled = df.copy()
    home_team = labeled["home_team"].astype(str).str.strip()
    away_team = labeled["away_team"].astype(str).str.strip()
    korea_home = home_team == KOREA_TEAM_NAME
    korea_away = away_team == KOREA_TEAM_NAME
    korea_match = korea_home | korea_away

    if require_all_rows and (~korea_match).any():
        invalid_rows = labeled.loc[~korea_match, ["date", "home_team", "away_team"]]
        raise ValueError(
            "Korea perspective target requires every row to include "
            f"{KOREA_TEAM_NAME!r} as home_team or away_team. Invalid rows: "
            f"{invalid_rows.to_dict(orient='records')}"
        )

    reverse_home_result = {"Win": "Loss", "Loss": "Win", "Draw": "Draw"}
    labeled[KOREA_TARGET_COLUMN] = pd.NA
    labeled.loc[korea_home, KOREA_TARGET_COLUMN] = labeled.loc[korea_home, "target_result"]
    labeled.loc[korea_away, KOREA_TARGET_COLUMN] = labeled.loc[
        korea_away, "target_result"
    ].map(reverse_home_result)

    if require_all_rows and labeled[KOREA_TARGET_COLUMN].isna().any():
        raise ValueError(
            f"Failed to create {KOREA_TARGET_COLUMN}; check score and team values."
        )
    return labeled


def _add_target_result(df: pd.DataFrame, require_korea_perspective: bool = True) -> pd.DataFrame:
    """Create result labels required by MVP and expansion pipelines.

    ``target_result`` remains the traditional home-team perspective label. The
    MVP additionally requires ``target_result_korea_perspective`` for every row.
    Global expansion mode keeps Korea perspective values only where available.
    """
    labeled = _add_home_perspective_target(df)
    labeled = _add_korea_perspective_target(
        labeled,
        require_all_rows=require_korea_perspective,
    )
    return labeled


def _filter_to_korea_matches(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only rows where Korea Republic is either home or away."""
    home_team = df["home_team"].astype(str).str.strip()
    away_team = df["away_team"].astype(str).str.strip()
    korea_matches = df.loc[
        (home_team == KOREA_TEAM_NAME) | (away_team == KOREA_TEAM_NAME)
    ].copy()

    if korea_matches.empty:
        raise ValueError(
            f"No {KOREA_TEAM_NAME!r} matches found. The MVP dataset must include "
            "Korea Republic as home_team or away_team in at least one row."
        )

    return korea_matches


def _load_first_compatible_raw_csv(raw_dir: Path = RAW_DIR) -> pd.DataFrame | None:
    """Return the first raw CSV that has enough match-result columns."""
    if not raw_dir.exists():
        return None

    for csv_path in sorted(raw_dir.glob("*.csv")):
        candidate = _standardize_columns(pd.read_csv(csv_path))
        if REQUIRED_MATCH_COLUMNS.issubset(candidate.columns):
            print(f"Loaded raw match data from: {csv_path}")
            return candidate
    return None


def _format_markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    """Return a small dependency-free Markdown table."""
    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join("---" for _ in headers) + " |"
    data_rows = ["| " + " | ".join(str(value) for value in row) + " |" for row in rows]
    return "\n".join([header_row, separator_row, *data_rows])


def _write_data_quality_summary(matches: pd.DataFrame, scope_name: str) -> None:
    """Write a minimal data-quality report for the processed match dataset."""
    if matches.empty:
        raise ValueError("Cannot write a data quality summary for an empty dataset.")

    missing_rows = [
        [column, int(missing_count)]
        for column, missing_count in matches.isna().sum().sort_index().items()
    ]

    sections = [
        "# Data Quality Summary",
        "",
        "This file is generated by `python src/data/build_dataset.py`.",
        "",
        "## Scope",
        "",
        f"- Dataset scope: {scope_name}",
        "",
        "## Row Count",
        "",
        f"- Rows: {len(matches)}",
        f"- Columns: {len(matches.columns)}",
        "",
        "## Missing Values",
        "",
        _format_markdown_table(["Column", "Missing Count"], missing_rows),
        "",
        "## Target Distribution",
        "",
    ]

    for target_column in TARGET_COLUMNS:
        sections.extend([f"### `{target_column}`", ""])
        if target_column not in matches.columns:
            sections.extend([f"- Column `{target_column}` is not present.", ""])
            continue

        distribution_rows = [
            [target_value, int(count)]
            for target_value, count in matches[target_column]
            .value_counts(dropna=False)
            .sort_index()
            .items()
        ]
        sections.extend(
            [
                _format_markdown_table(["Target Value", "Count"], distribution_rows),
                "",
            ]
        )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_QUALITY_SUMMARY_PATH.write_text("\n".join(sections), encoding="utf-8")
    print(f"Saved data quality summary to: {DATA_QUALITY_SUMMARY_PATH}")


def _build_demo_matches() -> pd.DataFrame:
    """Create a compact fallback dataset for local MVP development."""
    rows = [
        ("2024-01-10", "Korea Republic", "Japan", 2, 1, False, 23, 18),
        ("2024-01-20", "Korea Republic", "Iran", 1, 1, True, 23, 20),
        ("2024-02-05", "Korea Republic", "Australia", 0, 1, False, 22, 25),
        ("2024-02-18", "Japan", "Korea Republic", 1, 2, False, 17, 22),
        ("2024-03-02", "Iran", "Korea Republic", 0, 0, False, 19, 22),
        ("2024-03-19", "Australia", "Korea Republic", 3, 1, True, 24, 22),
        ("2024-04-04", "Korea Republic", "Saudi Arabia", 3, 0, False, 21, 55),
        ("2024-04-22", "Saudi Arabia", "Korea Republic", 2, 2, False, 54, 21),
        ("2024-05-11", "Korea Republic", "Qatar", 1, 2, True, 21, 58),
        ("2024-05-30", "Qatar", "Korea Republic", 0, 1, False, 57, 21),
        ("2024-06-14", "Korea Republic", "Iraq", 1, 1, False, 20, 63),
        ("2024-06-29", "Iraq", "Korea Republic", 2, 0, False, 62, 20),
        ("2024-07-13", "Korea Republic", "Uzbekistan", 2, 0, True, 20, 74),
        ("2024-07-27", "Uzbekistan", "Korea Republic", 1, 1, False, 73, 20),
        ("2024-08-09", "Korea Republic", "United States", 0, 2, False, 20, 13),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "date",
            "home_team",
            "away_team",
            "home_score",
            "away_score",
            "neutral",
            "home_rank",
            "away_rank",
        ],
    )


def build_dataset(filter_korea: bool = True) -> pd.DataFrame:
    """Build and persist the standardized match dataset.

    Args:
        filter_korea: When True, preserve the Korea Republic MVP scope. When
            False, keep all compatible international rows for expansion work.
    """
    matches = _load_first_compatible_raw_csv()
    if matches is None:
        print("No compatible raw CSV found. Using built-in MVP demo data.")
        matches = _build_demo_matches()

    matches = _standardize_columns(matches)
    if filter_korea:
        matches = _filter_to_korea_matches(matches)

    matches = _add_target_result(matches, require_korea_perspective=filter_korea)

    required_subset = [
        "date",
        "home_team",
        "away_team",
        "home_score",
        "away_score",
        "target_result",
    ]
    if filter_korea:
        required_subset.append(KOREA_TARGET_COLUMN)

    matches["date"] = pd.to_datetime(matches["date"], errors="coerce")
    matches = matches.dropna(subset=required_subset)
    matches = matches.sort_values("date").drop_duplicates().reset_index(drop=True)
    matches["date"] = matches["date"].dt.strftime("%Y-%m-%d")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    matches.to_csv(MATCHES_PATH, index=False)

    scope_name = "korea_mvp" if filter_korea else "global_expansion"
    print(f"Saved {scope_name} match dataset with {len(matches)} rows to: {MATCHES_PATH}")
    _write_data_quality_summary(matches, scope_name=scope_name)
    return matches


def _parse_args() -> argparse.Namespace:
    """Parse command-line options for MVP and expansion data builds."""
    parser = argparse.ArgumentParser(description="Build processed match dataset.")
    parser.add_argument(
        "--global-scope",
        action="store_true",
        help="Keep all compatible international rows instead of Korea-only MVP rows.",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entry point for the data-building step."""
    args = _parse_args()
    build_dataset(filter_korea=not args.global_scope)


if __name__ == "__main__":
    main()
