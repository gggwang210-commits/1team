"""Build the model-ready match dataset.

This script loads raw match and ranking CSV files, cleans them, merges ranking
features onto each match, and saves the processed dataset for later modeling.
"""

from pathlib import Path
import sys

import pandas as pd

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from clean_data import clean_matches, clean_rankings
from load_data import load_matches, load_rankings

PROCESSED_DATA_DIR = Path("data/processed")
PROCESSED_MATCHES_PATH = PROCESSED_DATA_DIR / "matches.csv"
OUTPUT_COLUMNS = [
    "date",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
    "target_result",
    "home_rank",
    "away_rank",
    "rank_diff",
]


def _latest_rankings_by_team(rankings: pd.DataFrame) -> pd.DataFrame:
    """Keep one ranking row per team so each match merges to one row.

    If a ranking date exists, we keep the latest available ranking for each team.
    Otherwise, we simply keep the last row for each team in the cleaned file.
    """

    required_columns = {"team", "rank"}
    missing_columns = required_columns - set(rankings.columns)
    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise ValueError(f"Rankings data is missing required column(s): {missing_text}")

    ranking_columns = ["team", "rank"]
    if "ranking_date" in rankings.columns:
        ranking_columns.append("ranking_date")
        ordered_rankings = rankings.sort_values(["team", "ranking_date"])
    else:
        ordered_rankings = rankings.copy()

    # Drop rows without team because they cannot be joined to match teams.
    latest_rankings = ordered_rankings.dropna(subset=["team"])
    latest_rankings = latest_rankings.drop_duplicates(subset=["team"], keep="last")
    return latest_rankings[ranking_columns]


def _validate_matches_for_merge(matches: pd.DataFrame) -> None:
    """Fail early with a clear message if match data lacks key columns."""

    required_columns = {"home_team", "away_team"}
    missing_columns = required_columns - set(matches.columns)
    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise ValueError(f"Matches data is missing required column(s): {missing_text}")


def build_dataset() -> pd.DataFrame:
    """Create and save the processed match-level modeling dataset."""

    matches = clean_matches(load_matches())
    rankings = clean_rankings(load_rankings())

    _validate_matches_for_merge(matches)
    latest_rankings = _latest_rankings_by_team(rankings)

    # Merge rankings twice: once from the home-team point of view and once from
    # the away-team point of view. Renaming keeps the final columns easy to read.
    home_rankings = latest_rankings.rename(columns={"team": "home_team", "rank": "home_rank"})
    away_rankings = latest_rankings.rename(columns={"team": "away_team", "rank": "away_rank"})

    dataset = matches.merge(home_rankings[["home_team", "home_rank"]], on="home_team", how="left")
    dataset = dataset.merge(away_rankings[["away_team", "away_rank"]], on="away_team", how="left")
    dataset["rank_diff"] = dataset["home_rank"] - dataset["away_rank"]

    # Keep the requested columns when present. This makes the output stable but
    # still tolerant if an optional input such as score or date is unavailable.
    available_output_columns = [column for column in OUTPUT_COLUMNS if column in dataset.columns]
    dataset = dataset[available_output_columns]

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(PROCESSED_MATCHES_PATH, index=False)

    return dataset


if __name__ == "__main__":
    build_dataset()
