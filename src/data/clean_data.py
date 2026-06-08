"""Clean raw football match and FIFA ranking data.

This module standardizes column names and team names so later feature-building
code can work with predictable columns such as ``home_team`` and ``rank`` even
when the original CSV files use slightly different headers.
"""

import re
from collections.abc import Iterable

import pandas as pd

# A small starter mapping for team-name aliases. Add more aliases here when the
# team discovers naming differences in new raw data sources.
TEAM_NAME_MAP = {
    "Korea Republic": "Korea Republic",
    "South Korea": "Korea Republic",
    "USA": "United States",
    "United States": "United States",
    "IR Iran": "Iran",
    "Iran": "Iran",
}

MATCH_DATE_CANDIDATES = ("date", "match_date")
HOME_TEAM_CANDIDATES = ("home_team", "home", "home_country", "home_team_name")
AWAY_TEAM_CANDIDATES = ("away_team", "away", "away_country", "away_team_name")
HOME_SCORE_CANDIDATES = ("home_score", "home_goals", "home_team_score", "score_home")
AWAY_SCORE_CANDIDATES = ("away_score", "away_goals", "away_team_score", "score_away")
TEAM_CANDIDATES = ("team", "country", "country_full", "team_name", "nation")
RANK_CANDIDATES = ("rank", "ranking", "fifa_rank", "current_rank")
RANKING_DATE_CANDIDATES = ("ranking_date", "rank_date", "date")


def _to_snake_case(column_name: object) -> str:
    """Convert a raw column name into lowercase snake_case."""

    text = str(column_name).strip().lower()
    text = re.sub(r"[^0-9a-zA-Z]+", "_", text)
    return text.strip("_")


def _standardize_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with beginner-friendly, predictable column names."""

    cleaned = data.copy()
    cleaned.columns = [_to_snake_case(column) for column in cleaned.columns]
    return cleaned


def _find_column(columns: Iterable[str], candidates: Iterable[str]) -> str | None:
    """Find the first available column from a list of candidate names.

    Raw CSV files often use different names for the same concept. For example,
    one match file may use ``home_team`` while another uses ``home``. This helper
    lets the cleaning functions support those common variations.
    """

    available_columns = set(columns)
    for candidate in candidates:
        normalized_candidate = _to_snake_case(candidate)
        if normalized_candidate in available_columns:
            return normalized_candidate
    return None


def _rename_first_available(
    data: pd.DataFrame, candidates: Iterable[str], target_column: str
) -> pd.DataFrame:
    """Rename the first matching candidate column to a canonical name."""

    source_column = _find_column(data.columns, candidates)
    if source_column is None or source_column == target_column:
        return data
    return data.rename(columns={source_column: target_column})


def standardize_team_name(name: str) -> str:
    """Normalize common team-name aliases to one shared spelling."""

    if pd.isna(name):
        return name

    # Convert to string and collapse repeated spaces so mapping keys match even
    # when raw data has accidental leading/trailing spaces.
    cleaned_name = " ".join(str(name).strip().split())
    return TEAM_NAME_MAP.get(cleaned_name, cleaned_name)


def clean_matches(matches: pd.DataFrame) -> pd.DataFrame:
    """Clean match results and create the Win/Draw/Loss target column."""

    cleaned = _standardize_columns(matches)

    # Rename the important input columns to one project-wide spelling. This
    # keeps the rest of the pipeline simple and easier for beginners to follow.
    cleaned = _rename_first_available(cleaned, MATCH_DATE_CANDIDATES, "date")
    cleaned = _rename_first_available(cleaned, HOME_TEAM_CANDIDATES, "home_team")
    cleaned = _rename_first_available(cleaned, AWAY_TEAM_CANDIDATES, "away_team")
    cleaned = _rename_first_available(cleaned, HOME_SCORE_CANDIDATES, "home_score")
    cleaned = _rename_first_available(cleaned, AWAY_SCORE_CANDIDATES, "away_score")

    if "date" in cleaned.columns:
        cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")

    for team_column in ("home_team", "away_team"):
        if team_column in cleaned.columns:
            cleaned[team_column] = cleaned[team_column].apply(standardize_team_name)

    for score_column in ("home_score", "away_score"):
        if score_column in cleaned.columns:
            cleaned[score_column] = pd.to_numeric(cleaned[score_column], errors="coerce")

    if {"home_score", "away_score"}.issubset(cleaned.columns):
        # target_result is from the home team's point of view:
        # Win = home_score > away_score, Draw = equal, Loss = home_score < away_score.
        cleaned["target_result"] = pd.NA
        cleaned.loc[cleaned["home_score"] > cleaned["away_score"], "target_result"] = "Win"
        cleaned.loc[cleaned["home_score"] == cleaned["away_score"], "target_result"] = "Draw"
        cleaned.loc[cleaned["home_score"] < cleaned["away_score"], "target_result"] = "Loss"

    return cleaned


def clean_rankings(rankings: pd.DataFrame) -> pd.DataFrame:
    """Clean FIFA ranking data for date-aware merging with match rows."""

    cleaned = _standardize_columns(rankings)

    cleaned = _rename_first_available(cleaned, TEAM_CANDIDATES, "team")
    cleaned = _rename_first_available(cleaned, RANK_CANDIDATES, "rank")
    cleaned = _rename_first_available(cleaned, RANKING_DATE_CANDIDATES, "ranking_date")

    if "team" in cleaned.columns:
        cleaned["team"] = cleaned["team"].apply(standardize_team_name)

    if "rank" in cleaned.columns:
        cleaned["rank"] = pd.to_numeric(cleaned["rank"], errors="coerce")

    if "ranking_date" in cleaned.columns:
        cleaned["ranking_date"] = pd.to_datetime(cleaned["ranking_date"], errors="coerce")

    return cleaned
