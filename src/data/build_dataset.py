"""Build the model-ready match dataset.

This script loads raw match and ranking CSV files, cleans them, joins the latest
FIFA ranking available before each match date, and saves the processed dataset
for later modeling.
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
    "rank_difference",
]


def _validate_required_columns(
    data: pd.DataFrame, required_columns: set[str], data_name: str
) -> None:
    """Fail early with a clear message if a cleaned dataset lacks key columns."""

    missing_columns = required_columns - set(data.columns)
    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise ValueError(f"{data_name} data is missing required column(s): {missing_text}")


def _add_latest_rank_before_match(
    matches: pd.DataFrame,
    rankings: pd.DataFrame,
    *,
    team_column: str,
    rank_column: str,
) -> pd.DataFrame:
    """Add the latest FIFA rank available on or before each match date.

    We do not use rankings published after a match because that would leak future
    information into the model. Each row is matched by team name and date.
    """

    _validate_required_columns(matches, {"date", team_column}, "Matches")
    _validate_required_columns(rankings, {"team", "rank", "ranking_date"}, "Rankings")

    # _match_id lets us sort and merge safely, then put each rank back on the
    # original match row without losing the input order.
    match_keys = matches[["_match_id", "date", team_column]].copy()
    rank_lookup = rankings[["team", "rank", "ranking_date"]].dropna(
        subset=["team", "rank", "ranking_date"]
    )

    # Rows without a match date cannot be safely matched to a historical
    # ranking, so they stay in the output with a blank rank value.
    valid_match_keys = match_keys.dropna(subset=[team_column, "date"])

    joined_parts: list[pd.DataFrame] = []
    for team_name, team_matches in valid_match_keys.groupby(team_column):
        team_rankings = rank_lookup[rank_lookup["team"] == team_name]

        # If the team has no FIFA ranking rows, keep the match rows and leave the
        # rank blank so data quality issues are visible in the processed CSV.
        if team_rankings.empty:
            empty_result = team_matches[["_match_id"]].copy()
            empty_result[rank_column] = pd.NA
            joined_parts.append(empty_result)
            continue

        latest_rank = pd.merge_asof(
            team_matches.sort_values("date"),
            team_rankings.sort_values("ranking_date"),
            left_on="date",
            right_on="ranking_date",
            direction="backward",
        )
        rank_result = latest_rank[["_match_id", "rank"]].rename(
            columns={"rank": rank_column}
        )
        joined_parts.append(rank_result)

    if joined_parts:
        joined_ranks = pd.concat(joined_parts, ignore_index=True)
    else:
        joined_ranks = pd.DataFrame(columns=["_match_id", rank_column])

    # A left merge preserves every match, even when a ranking is unavailable.
    output = matches.merge(joined_ranks, on="_match_id", how="left")
    return output


def build_dataset() -> pd.DataFrame:
    """Create and save the processed match-level modeling dataset."""

    matches = clean_matches(load_matches())
    rankings = clean_rankings(load_rankings())

    _validate_required_columns(matches, {"date", "home_team", "away_team"}, "Matches")
    _validate_required_columns(rankings, {"team", "rank", "ranking_date"}, "Rankings")

    # Add a stable row id before joining rankings. This makes the later merge
    # steps safe even when the same teams play more than once.
    dataset = matches.copy().reset_index(drop=True)
    dataset["_match_id"] = dataset.index

    # Join rankings separately for home and away teams, always using the latest
    # ranking published before the match date.
    dataset = _add_latest_rank_before_match(
        dataset,
        rankings,
        team_column="home_team",
        rank_column="home_rank",
    )
    dataset = _add_latest_rank_before_match(
        dataset,
        rankings,
        team_column="away_team",
        rank_column="away_rank",
    )

    # Lower FIFA rank numbers are stronger, so a negative value means the home
    # team was ranked better than the away team at match time.
    dataset["rank_difference"] = dataset["home_rank"] - dataset["away_rank"]

    # Keep the requested columns when present. This makes the output stable but
    # still tolerant if an optional input such as score is unavailable.
    available_output_columns = [
        column for column in OUTPUT_COLUMNS if column in dataset.columns
    ]
    dataset = dataset[available_output_columns]

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(PROCESSED_MATCHES_PATH, index=False)

    return dataset


if __name__ == "__main__":
    build_dataset()
