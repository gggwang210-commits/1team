"""Build the MVP match dataset used by feature engineering.

Data flow for beginners:
1. Prefer real raw CSV files in ``data/raw`` when they use common football
   results columns such as ``date``, ``home_team``, and ``away_team``.
2. If raw data is not available yet, create a small but trainable demo dataset.
3. Save the standardized match table to ``data/processed/matches.csv``.

The demo dataset is intentionally simple, but it is large enough to support a
stratified train/test split for the baseline classifier.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MATCHES_PATH = PROCESSED_DIR / "matches.csv"

REQUIRED_MATCH_COLUMNS = {"date", "home_team", "away_team", "home_score", "away_score"}

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


def _add_target_result(df: pd.DataFrame) -> pd.DataFrame:
    """Create a three-class match result label from final scores."""
    labeled = df.copy()
    labeled["home_score"] = pd.to_numeric(labeled["home_score"], errors="coerce")
    labeled["away_score"] = pd.to_numeric(labeled["away_score"], errors="coerce")

    labeled["target_result"] = "DRAW"
    labeled.loc[labeled["home_score"] > labeled["away_score"], "target_result"] = (
        "HOME_WIN"
    )
    labeled.loc[labeled["home_score"] < labeled["away_score"], "target_result"] = (
        "AWAY_WIN"
    )
    return labeled


def _load_first_compatible_raw_csv(raw_dir: Path = RAW_DIR) -> pd.DataFrame | None:
    """Return the first raw CSV that has enough match-result columns.

    The project may use different Kaggle/public datasets during MVP discovery,
    so this loader accepts common column variants instead of depending on one
    exact filename.
    """
    if not raw_dir.exists():
        return None

    for csv_path in sorted(raw_dir.glob("*.csv")):
        candidate = _standardize_columns(pd.read_csv(csv_path))
        if REQUIRED_MATCH_COLUMNS.issubset(candidate.columns):
            print(f"Loaded raw match data from: {csv_path}")
            return candidate
    return None


def _build_demo_matches() -> pd.DataFrame:
    """Create a compact fallback dataset for local MVP development.

    The fallback has 15 rows and three classes. With the default 20% test split,
    this gives three test rows, which is the minimum needed for a stratified
    three-class split.
    """
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


def build_dataset() -> pd.DataFrame:
    """Build and persist the standardized MVP match dataset."""
    matches = _load_first_compatible_raw_csv()
    if matches is None:
        print("No compatible raw CSV found. Using built-in MVP demo data.")
        matches = _build_demo_matches()
    matches = _standardize_columns(matches)
    matches = _add_target_result(matches)

    # Keep only rows that can support supervised training.
    matches["date"] = pd.to_datetime(matches["date"], errors="coerce")
    matches = matches.dropna(
        subset=[
            "date",
            "home_team",
            "away_team",
            "home_score",
            "away_score",
            "target_result",
        ]
    )
    matches = matches.sort_values("date").drop_duplicates().reset_index(drop=True)
    matches["date"] = matches["date"].dt.strftime("%Y-%m-%d")

    # ``processed`` is the stable hand-off directory for downstream pipeline
    # steps such as feature engineering and smoke tests.
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    matches.to_csv(MATCHES_PATH, index=False)
    print(f"Saved MVP match dataset with {len(matches)} rows to: {MATCHES_PATH}")
    return matches


def main() -> None:
    """CLI entry point for the data-building step."""
    build_dataset()


if __name__ == "__main__":
    main()
