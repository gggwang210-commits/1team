"""Create model-ready match features from processed match data.

This script reads ``data/processed/matches.csv`` and writes
``data/processed/features.csv``.  The code is intentionally defensive because
team projects often receive data from multiple sources with slightly different
column names.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "matches.csv"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "features.csv"

# Common column-name candidates.  If your CSV uses a different name, add it here
# instead of changing the feature logic below.
COLUMN_ALIASES = {
    "date": ["date", "match_date", "game_date", "fixture_date", "datetime"],
    "team": ["team", "team_name", "country", "nation"],
    "opponent": ["opponent", "opponent_name", "opposing_team", "rival"],
    "goals_for": ["goals_for", "team_goals", "goals_scored", "score_for"],
    "goals_against": [
        "goals_against",
        "opponent_goals",
        "goals_conceded",
        "score_against",
    ],
    "team_rank": ["team_rank", "rank", "fifa_rank", "ranking", "team_fifa_rank"],
    "opponent_rank": [
        "opponent_rank",
        "opponent_fifa_rank",
        "opponent_ranking",
        "rival_rank",
    ],
    "neutral": ["neutral", "neutral_flag", "neutral_venue", "is_neutral"],
    "home_team": ["home_team", "home", "home_name", "home_country"],
    "away_team": ["away_team", "away", "away_name", "away_country"],
    "home_goals": ["home_goals", "home_score", "home_team_goals", "score_home"],
    "away_goals": ["away_goals", "away_score", "away_team_goals", "score_away"],
    "home_rank": ["home_rank", "home_fifa_rank", "home_ranking"],
    "away_rank": ["away_rank", "away_fifa_rank", "away_ranking"],
}

FEATURE_COLUMNS = [
    "win_rate_last_5",
    "win_rate_last_10",
    "avg_goals_for_last_5",
    "avg_goals_against_last_5",
    "goal_difference_last_5",
    "rank_difference",
    "neutral_flag",
]


def load_matches(input_path: str | Path = DEFAULT_INPUT_PATH) -> pd.DataFrame:
    """Load the processed match CSV.

    Parameters
    ----------
    input_path:
        Location of the match-level CSV.  Defaults to
        ``data/processed/matches.csv``.
    """

    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_path}. "
            "Create data/processed/matches.csv first, then rerun this script."
        )

    # pandas reads CSV files into a table-like DataFrame that is easy to clean
    # and transform for machine learning.
    return pd.read_csv(input_path)


def _find_column(columns: Iterable[str], aliases: list[str]) -> str | None:
    """Return the actual column name matching one of the accepted aliases."""

    normalized_columns = {column.lower().strip(): column for column in columns}
    for alias in aliases:
        match = normalized_columns.get(alias.lower())
        if match is not None:
            return match
    return None


def _column_map(matches: pd.DataFrame) -> dict[str, str | None]:
    """Build a mapping from standard names to the CSV's real column names."""

    return {
        standard_name: _find_column(matches.columns, aliases)
        for standard_name, aliases in COLUMN_ALIASES.items()
    }


def _require_columns(column_map: dict[str, str | None], required: list[str]) -> None:
    """Raise a beginner-friendly error when required source columns are missing."""

    missing = [name for name in required if column_map.get(name) is None]
    if missing:
        raise ValueError(
            "Missing required column(s): "
            f"{', '.join(missing)}. "
            "Please rename your CSV columns or add their names to COLUMN_ALIASES."
        )


def _to_numeric(series: pd.Series) -> pd.Series:
    """Convert a column to numbers while keeping invalid or blank values as NaN."""

    return pd.to_numeric(series, errors="coerce")


def _to_neutral_flag(series: pd.Series) -> pd.Series:
    """Convert common boolean/text neutral-venue values into 0/1 integers."""

    true_values = {"1", "true", "t", "yes", "y", "neutral"}
    false_values = {"0", "false", "f", "no", "n", "home", "away"}

    def convert(value: object) -> int:
        if pd.isna(value):
            return 0
        if isinstance(value, bool):
            return int(value)
        value_text = str(value).strip().lower()
        if value_text in true_values:
            return 1
        if value_text in false_values:
            return 0
        numeric_value = pd.to_numeric(value_text, errors="coerce")
        if pd.isna(numeric_value):
            return 0
        return int(numeric_value != 0)

    return series.map(convert).astype(int)


def _normalize_long_form(matches: pd.DataFrame) -> pd.DataFrame:
    """Normalize team/opponent rows regardless of source CSV shape.

    Some football datasets already have one row per team, with columns like
    ``team`` and ``opponent``.  Others have one row per match, with columns like
    ``home_team`` and ``away_team``.  Rolling features are easier and safer when
    every row is from one team's perspective, so home/away data is expanded into
    two rows.
    """

    column_map = _column_map(matches)

    if column_map["team"] and column_map["opponent"]:
        _require_columns(
            column_map, ["date", "team", "opponent", "goals_for", "goals_against"]
        )

        normalized = pd.DataFrame(
            {
                "date": matches[column_map["date"]],
                "team": matches[column_map["team"]],
                "opponent": matches[column_map["opponent"]],
                "goals_for": _to_numeric(matches[column_map["goals_for"]]),
                "goals_against": _to_numeric(matches[column_map["goals_against"]]),
                "team_rank": _to_numeric(matches[column_map["team_rank"]])
                if column_map["team_rank"]
                else pd.NA,
                "opponent_rank": _to_numeric(matches[column_map["opponent_rank"]])
                if column_map["opponent_rank"]
                else pd.NA,
                "neutral_flag": _to_neutral_flag(matches[column_map["neutral"]])
                if column_map["neutral"]
                else 0,
                "source_row": matches.index,
            }
        )
        return normalized

    _require_columns(
        column_map, ["date", "home_team", "away_team", "home_goals", "away_goals"]
    )

    # Create a home-team view: goals_for means the home team's score.
    home_view = pd.DataFrame(
        {
            "date": matches[column_map["date"]],
            "team": matches[column_map["home_team"]],
            "opponent": matches[column_map["away_team"]],
            "goals_for": _to_numeric(matches[column_map["home_goals"]]),
            "goals_against": _to_numeric(matches[column_map["away_goals"]]),
            "team_rank": _to_numeric(matches[column_map["home_rank"]])
            if column_map["home_rank"]
            else pd.NA,
            "opponent_rank": _to_numeric(matches[column_map["away_rank"]])
            if column_map["away_rank"]
            else pd.NA,
            "neutral_flag": _to_neutral_flag(matches[column_map["neutral"]])
            if column_map["neutral"]
            else 0,
            "source_row": matches.index,
            "venue_side": "home",
        }
    )

    # Create an away-team view: the same match, but flipped to the away team's
    # perspective so each team gets its own historical features.
    away_view = pd.DataFrame(
        {
            "date": matches[column_map["date"]],
            "team": matches[column_map["away_team"]],
            "opponent": matches[column_map["home_team"]],
            "goals_for": _to_numeric(matches[column_map["away_goals"]]),
            "goals_against": _to_numeric(matches[column_map["home_goals"]]),
            "team_rank": _to_numeric(matches[column_map["away_rank"]])
            if column_map["away_rank"]
            else pd.NA,
            "opponent_rank": _to_numeric(matches[column_map["home_rank"]])
            if column_map["home_rank"]
            else pd.NA,
            "neutral_flag": _to_neutral_flag(matches[column_map["neutral"]])
            if column_map["neutral"]
            else 0,
            "source_row": matches.index,
            "venue_side": "away",
        }
    )

    return pd.concat([home_view, away_view], ignore_index=True)


def add_recent_form_features(matches: pd.DataFrame) -> pd.DataFrame:
    """Add leakage-safe rolling features for each team."""

    features = _normalize_long_form(matches).copy()

    # Convert dates to pandas datetime values so sorting is chronological, not
    # alphabetical.  Invalid dates become NaT and are placed at the end.
    features["date"] = pd.to_datetime(features["date"], errors="coerce")

    # Sorting before rolling is critical: each row should only look backward at
    # matches that happened earlier for the same team.
    sort_columns = ["date", "source_row", "team"]
    if "venue_side" in features.columns:
        sort_columns.append("venue_side")
    features = features.sort_values(sort_columns).reset_index(drop=True)

    # A win is 1, a draw/loss is 0.  This is the raw result of the current match;
    # the shift below prevents the current match from influencing its own feature.
    features["win"] = (features["goals_for"] > features["goals_against"]).astype(int)

    grouped = features.groupby("team", group_keys=False)

    # shift(1) means "start from the previous match".  This avoids data leakage
    # because today's match result is never used to create today's input feature.
    features["win_rate_last_5"] = grouped["win"].transform(
        lambda values: values.shift(1).rolling(window=5, min_periods=1).mean()
    )
    features["win_rate_last_10"] = grouped["win"].transform(
        lambda values: values.shift(1).rolling(window=10, min_periods=1).mean()
    )
    features["avg_goals_for_last_5"] = grouped["goals_for"].transform(
        lambda values: values.shift(1).rolling(window=5, min_periods=1).mean()
    )
    features["avg_goals_against_last_5"] = grouped["goals_against"].transform(
        lambda values: values.shift(1).rolling(window=5, min_periods=1).mean()
    )

    # Goal difference is goals scored minus goals conceded.  Positive values mean
    # the team has recently scored more than it allowed.
    features["goal_difference_last_5"] = (
        features["avg_goals_for_last_5"] - features["avg_goals_against_last_5"]
    )

    # Lower FIFA rank numbers usually mean stronger teams, so this subtraction is
    # intentionally team_rank - opponent_rank as requested.
    features["rank_difference"] = features["team_rank"] - features["opponent_rank"]

    # Keep useful identifiers plus the requested feature columns.  The optional
    # target-like result columns can help later modeling scripts create labels.
    output_columns = [
        "date",
        "team",
        "opponent",
        "source_row",
        "goals_for",
        "goals_against",
        "win",
        *FEATURE_COLUMNS,
    ]
    if "venue_side" in features.columns:
        output_columns.insert(4, "venue_side")

    return features[output_columns]


def save_features(features: pd.DataFrame, output_path: str | Path = DEFAULT_OUTPUT_PATH) -> None:
    """Save the feature table to CSV, creating the folder if needed."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # index=False keeps the CSV clean by not writing pandas' internal row number.
    features.to_csv(output_path, index=False)


def main(
    input_path: str | Path = DEFAULT_INPUT_PATH,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> pd.DataFrame:
    """Run the full feature-engineering pipeline."""

    matches = load_matches(input_path)
    features = add_recent_form_features(matches)
    save_features(features, output_path)
    print(f"Saved {len(features):,} feature rows to {Path(output_path)}")
    return features


if __name__ == "__main__":
    main()
